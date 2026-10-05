"""Explicit Windows NTFS publication experiment; never imported by production M4.

Callers must supply an independently audited candidate. This module grants no
S0/P/C capability and is not a Windows write-delivery switch.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import stat
import sys
import tempfile
from pathlib import Path


class WindowsCandidateError(ValueError):
    pass


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _local_ntfs(directory: Path) -> None:
    if sys.platform != "win32":
        raise WindowsCandidateError("candidate requires actual Windows")
    # Reject every reparse component, including junctions and mapped aliases.
    current = directory.absolute()
    while True:
        if current.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise WindowsCandidateError("reparse-point parent is unsupported")
        if current.parent == current:
            break
        current = current.parent
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    root = ctypes.create_unicode_buffer(32768)
    if not kernel.GetVolumePathNameW(ctypes.c_wchar_p(str(directory)), root, len(root)):
        raise WindowsCandidateError("cannot identify destination volume")
    if kernel.GetDriveTypeW(ctypes.c_wchar_p(root.value)) != 3:  # DRIVE_FIXED
        raise WindowsCandidateError("network/removable volume is unsupported")
    filesystem = ctypes.create_unicode_buffer(256)
    if not kernel.GetVolumeInformationW(ctypes.c_wchar_p(root.value), None, 0,
                                         None, None, None, filesystem, len(filesystem)):
        raise WindowsCandidateError("cannot identify destination filesystem")
    if filesystem.value.upper() != "NTFS":
        raise WindowsCandidateError("only local NTFS is validated")


def publish_new(source: str | Path, destination: str | Path, expected_source_sha256: str,
                candidate: bytes, independent_audit) -> str:
    """Stage, audit, and create a no-clobber hard link on local NTFS.

    This is a synthetic validation candidate, not an adopted publication API.
    A process crash may leave a private stage; no power-loss claim is made.
    """
    source, destination = Path(source), Path(destination)
    repository = Path(__file__).resolve().parent
    if destination.suffix.lower() != ".sav":
        raise WindowsCandidateError("destination must end in .sav")
    _local_ntfs(destination.parent)
    if destination.resolve().is_relative_to(repository):
        raise WindowsCandidateError("repository destination is forbidden")
    if os.path.lexists(destination):
        raise WindowsCandidateError("destination already exists")
    if source.resolve() == destination.resolve():
        raise WindowsCandidateError("source/destination alias")
    if _hash(source) != expected_source_sha256:
        raise WindowsCandidateError("source changed before publication")
    independent_audit(candidate)
    staged = None
    published = False
    try:
        fd, name = tempfile.mkstemp(prefix=".pokemonstart-stage-", suffix=".tmp", dir=destination.parent)
        staged = Path(name)
        with os.fdopen(fd, "wb") as handle:
            if handle.write(candidate) != len(candidate):
                raise WindowsCandidateError("short staged write")
            handle.flush()
            os.fsync(handle.fileno())
        staged_bytes = staged.read_bytes()
        if staged_bytes != candidate:
            raise WindowsCandidateError("staged bytes differ")
        independent_audit(staged_bytes)
        if _hash(source) != expected_source_sha256:
            raise WindowsCandidateError("source changed during publication")
        _local_ntfs(destination.parent)
        os.link(staged, destination)
        published = True
        final_bytes = destination.read_bytes()
        if final_bytes != candidate:
            raise WindowsCandidateError("published bytes differ")
        independent_audit(final_bytes)
        if _hash(source) != expected_source_sha256:
            raise WindowsCandidateError("source changed after publication")
        return hashlib.sha256(final_bytes).hexdigest()
    except Exception:
        if published and staged is not None and os.path.lexists(destination):
            if os.path.samefile(staged, destination):
                destination.unlink()
        raise
    finally:
        if staged is not None and os.path.lexists(staged):
            staged.unlink()
