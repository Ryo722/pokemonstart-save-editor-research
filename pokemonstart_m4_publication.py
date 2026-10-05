"""M4 new-file publication. A verified candidate is staged before it is visible.

The caller owns semantic authorization. This module owns path safety, complete
staging, no-clobber publication, and a second read of the published file.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from pathlib import Path


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


def publish_new(source: str | Path, destination: str | Path, expected_source_sha256: str,
                candidate: bytes, independent_audit) -> str:
    """Publish complete verified bytes via a same-directory hard link.

    On Windows this deliberately fails closed until Windows link/durability
    behavior is validated. A crash before link leaves no final pathname; a
    crash after link leaves the complete fsynced candidate.
    """
    source, destination = Path(source), Path(destination)
    repository = Path(__file__).resolve().parent
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
