"""M4 new-file publication. A verified candidate is staged before it is visible.

The caller owns semantic authorization. This module owns path safety, complete
staging, no-clobber publication, and a second read of the published file.
"""
from __future__ import annotations

import hashlib
import ctypes
import os
import stat
import sys
import tempfile
from pathlib import Path

import pokemonstart_m4_host as host


class PublicationError(ValueError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _exists(path: Path) -> bool:
    return os.path.lexists(path)


def _fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _windows_volume(directory: Path) -> tuple[int, str]:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    root = ctypes.create_unicode_buffer(32768)
    if not kernel.GetVolumePathNameW(ctypes.c_wchar_p(str(directory)), root, len(root)):
        raise PublicationError("cannot identify destination volume")
    drive_type = kernel.GetDriveTypeW(ctypes.c_wchar_p(root.value))
    filesystem = ctypes.create_unicode_buffer(256)
    if not kernel.GetVolumeInformationW(ctypes.c_wchar_p(root.value), None, 0,
                                         None, None, None, filesystem, len(filesystem)):
        raise PublicationError("cannot identify destination filesystem")
    return drive_type, filesystem.value


def _local_ntfs(directory: Path) -> None:
    if sys.platform != "win32":
        raise PublicationError("Windows NTFS publication requires actual Windows")
    # Reject every existing reparse component, including junctions. This does
    # not pin parent handles against hostile replacement after the checks.
    current = directory.absolute()
    while True:
        if current.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise PublicationError("reparse-point parent is unsupported")
        if current.parent == current:
            break
        current = current.parent
    drive_type, filesystem = _windows_volume(directory)
    if drive_type != 3:  # DRIVE_FIXED; excludes network and removable volumes.
        raise PublicationError("network/removable volume is unsupported")
    if filesystem.upper() != "NTFS":
        raise PublicationError("only local NTFS is validated")


def _publish_new_windows(source: Path, destination: Path, expected_source_sha256: str,
                         candidate: bytes, independent_audit) -> str:
    repository = Path(__file__).resolve().parent
    if destination.suffix.lower() != ".sav":
        raise PublicationError("destination must end in .sav")
    _local_ntfs(destination.parent)
    if destination.resolve().is_relative_to(repository):
        raise PublicationError("private save destination is inside repository")
    if _exists(destination):
        raise PublicationError("destination already exists")
    if source.resolve() == destination.resolve():
        raise PublicationError("source and destination alias")
    if _sha(source.read_bytes()) != expected_source_sha256:
        raise PublicationError("source changed before publication")
    independent_audit(candidate)
    staged: Path | None = None
    published = False
    try:
        fd, name = tempfile.mkstemp(prefix=".pokemonstart-stage-", suffix=".tmp", dir=destination.parent)
        staged = Path(name)
        with os.fdopen(fd, "wb") as handle:
            if handle.write(candidate) != len(candidate):
                raise PublicationError("short staged write")
            handle.flush()
            os.fsync(handle.fileno())
        staged_bytes = staged.read_bytes()
        if staged_bytes != candidate:
            raise PublicationError("staged bytes differ")
        independent_audit(staged_bytes)
        if _sha(source.read_bytes()) != expected_source_sha256:
            raise PublicationError("source changed during publication")
        _local_ntfs(destination.parent)
        os.link(staged, destination)
        published = True
        final_bytes = destination.read_bytes()
        if final_bytes != candidate:
            raise PublicationError("published bytes differ")
        independent_audit(final_bytes)
        if _sha(source.read_bytes()) != expected_source_sha256:
            raise PublicationError("source changed after publication")
        return _sha(final_bytes)
    except Exception:
        if published and staged is not None and _exists(destination):
            # A reparse entry can resolve to our stage while being someone
            # else's final pathname. Never remove it in that case.
            if not (destination.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) \
                    and os.path.samefile(staged, destination):
                destination.unlink()
        raise
    finally:
        if staged is not None and _exists(staged):
            staged.unlink()


def publish_new(source: str | Path, destination: str | Path, expected_source_sha256: str,
                candidate: bytes, independent_audit) -> str:
    """Publish to a new path on validated macOS or bounded local NTFS Windows.

    Windows does not claim sudden power-loss persistence of final-name metadata.
    The untouched input is always the recovery anchor.
    """
    source, destination = Path(source), Path(destination)
    repository = Path(__file__).resolve().parent
    if sys.platform == "win32":
        if not host.validated_windows_host():
            raise PublicationError("M4 publication is unvalidated on this Windows build")
        return _publish_new_windows(source, destination, expected_source_sha256,
                                    candidate, independent_audit)
    if sys.platform != "darwin":
        raise PublicationError("M4 publication is unvalidated on this platform")
    if destination.suffix.lower() != ".sav":
        raise PublicationError("destination must end in .sav")
    if destination.resolve().is_relative_to(repository):
        raise PublicationError("private save destination is inside repository")
    if source.resolve() == destination.resolve():
        raise PublicationError("source and destination alias")
    if _exists(destination):
        raise PublicationError("destination already exists")
    if _sha(source.read_bytes()) != expected_source_sha256:
        raise PublicationError("source changed before publication")
    independent_audit(candidate)
    staged: Path | None = None
    published = False
    try:
        fd, name = tempfile.mkstemp(prefix=".pokemonstart-stage-", suffix=".tmp", dir=destination.parent)
        staged = Path(name)
        with os.fdopen(fd, "wb") as handle:
            count = handle.write(candidate)
            if count != len(candidate):
                raise PublicationError("short staged write")
            handle.flush()
            os.fsync(handle.fileno())
        if staged.read_bytes() != candidate:
            raise PublicationError("staged bytes differ")
        if _sha(source.read_bytes()) != expected_source_sha256:
            raise PublicationError("source changed during publication")
        independent_audit(staged.read_bytes())
        os.link(staged, destination)
        published = True
        _fsync_directory(destination.parent)
        if destination.read_bytes() != candidate:
            raise PublicationError("published bytes differ")
        independent_audit(destination.read_bytes())
        if _sha(source.read_bytes()) != expected_source_sha256:
            raise PublicationError("source changed after publication")
        return _sha(candidate)
    except Exception:
        if published:
            # Remove only our own link. Never remove a concurrently replaced path.
            if staged is not None and _exists(destination) and os.path.samefile(staged, destination):
                destination.unlink()
        raise
    finally:
        if staged is not None and _exists(staged):
            staged.unlink()
