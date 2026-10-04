"""Fail-closed transaction envelope for exact, profile-bound party-record proofs.

This module has no field authority of its own. A caller must supply an exact
lineage profile, byte patches, a semantic validator, and an output seal.
"""
from __future__ import annotations

import hashlib
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import pokemonstart_save_verifier as v


class TransactionError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Profile:
    input_sha256: str
    active_slot: int
    active_counter: int
    inactive_counter: int
    section1_sector: int
    party_count: int
    record0_sha256: str
    sector30_sha256: str
    sector31_sha256: str
    footer_sha256: str


@dataclass(frozen=True)
class RecordPatch:
    offset: int
    before: bytes
    after: bytes


@dataclass(frozen=True)
class Fingerprint:
    input_sha256: str
    output_sha256: str
    active_slot: int
    active_counter: int
    section1_sector: int
    checksum_before: int
    checksum_after: int
    diffs: tuple[tuple[int, int, int], ...]


def _section_map(slot: v.SlotInfo) -> tuple[tuple[int, int, int, int], ...]:
    return tuple((s.section_id, s.physical_sector, s.counter, s.signature) for s in slot.sections)


def _check_profile(raw: bytes, result: v.VerificationResult, profile: Profile) -> int:
    if result.file_sha256 != profile.input_sha256:
        raise TransactionError("unrecognized input hash")
    if result.active_slot != profile.active_slot:
        raise TransactionError("active slot profile mismatch")
    active = result.slots[result.active_slot]
    inactive = result.slots[1 - result.active_slot]
    if active.state != "valid" or inactive.state != "valid":
        raise TransactionError("both slots must be valid")
    if (active.counter, inactive.counter) != (profile.active_counter, profile.inactive_counter):
        raise TransactionError("slot counter profile mismatch")
    if active.counter is None or result.active_slot != active.counter % 2:
        raise TransactionError("active slot/counter parity mismatch")
    sector = active.section(1).physical_sector
    if sector != profile.section1_sector:
        raise TransactionError("section 1 physical sector profile mismatch")
    if result.party_count != profile.party_count or not result.party:
        raise TransactionError("party profile mismatch")
    record_base = sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    if sha(raw[record_base:record_base + v.POKEMON_SIZE]) != profile.record0_sha256:
        raise TransactionError("party[0] record profile mismatch")
    if sha(result.sector30) != profile.sector30_sha256 or sha(result.sector31) != profile.sector31_sha256:
        raise TransactionError("extra-sector profile mismatch")
    if len(result.footer) != v.RTC_FOOTER_SIZE or sha(result.footer) != profile.footer_sha256:
        raise TransactionError("footer profile mismatch")
    return sector


def derive(
    raw: bytes,
    profile: Profile,
    patches: Iterable[RecordPatch],
    validate_before: Callable[[v.VerificationResult], None],
    validate_after: Callable[[v.VerificationResult, v.VerificationResult], None],
) -> tuple[bytes, Fingerprint]:
    before = v.verify_bytes(raw)
    sector = _check_profile(raw, before, profile)
    validate_before(before)
    base = sector * v.SECTOR_SIZE
    record_base = base + v.PARTY_OFFSET
    checksum_offset = base + v.SECTION_CHECKSUM_OFFSET
    out = bytearray(raw)
    allowed = {checksum_offset, checksum_offset + 1}
    patches = tuple(patches)
    if not patches:
        raise TransactionError("empty transaction")
    for patch in patches:
        if len(patch.before) != len(patch.after) or not patch.before:
            raise TransactionError("invalid record patch length")
        if patch.offset < 0 or patch.offset + len(patch.before) > v.POKEMON_SIZE:
            raise TransactionError("record patch outside party[0]")
        absolute = record_base + patch.offset
        positions = set(range(absolute, absolute + len(patch.before)))
        if positions & allowed:
            raise TransactionError("overlapping record patches")
        if bytes(out[absolute:absolute + len(patch.before)]) != patch.before:
            raise TransactionError("record patch starting value mismatch")
        out[absolute:absolute + len(patch.after)] = patch.after
        allowed.update(positions)
    old_checksum = before.slots[before.active_slot].section(1).checksum_stored
    new_checksum = v.calculate_save_checksum(bytes(out[base:base + v.SECTION_LENGTHS[1]]))
    struct.pack_into("<H", out, checksum_offset, new_checksum)
    output = bytes(out)
    diffs = tuple((i, a, b) for i, (a, b) in enumerate(zip(raw, output)) if a != b)
    if not diffs or any(i not in allowed for i, _, _ in diffs):
        raise TransactionError("output diff escaped record/checksum envelope")
    after = v.verify_bytes(output)
    if after.active_slot != before.active_slot or tuple(s.counter for s in after.slots) != tuple(s.counter for s in before.slots):
        raise TransactionError("slot selection/counters changed")
    if tuple(_section_map(s) for s in after.slots) != tuple(_section_map(s) for s in before.slots):
        raise TransactionError("section metadata/permutation changed")
    if after.party_count != before.party_count:
        raise TransactionError("party count changed")
    validate_after(before, after)
    return output, Fingerprint(
        before.file_sha256, sha(output), before.active_slot, profile.active_counter,
        sector, old_checksum, new_checksum, diffs,
    )


def write_new(
    input_path: str | Path,
    output_path: str | Path,
    build: Callable[[bytes], tuple[bytes, Fingerprint]],
) -> Fingerprint:
    source, dest = Path(input_path), Path(output_path)
    repository = Path(__file__).resolve().parent
    if dest.resolve().is_relative_to(repository):
        raise TransactionError("private output must be outside the repository")
    if source.resolve() == dest.resolve():
        raise TransactionError("refusing to overwrite input")
    if dest.exists():
        raise TransactionError("refusing to overwrite existing output")
    raw = source.read_bytes()
    output, fp = build(raw)
    created = False
    try:
        with dest.open("xb") as handle:
            created = True
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        if dest.read_bytes() != output:
            raise TransactionError("written output differs from verified candidate")
        if sha(source.read_bytes()) != fp.input_sha256:
            raise TransactionError("input changed during output write")
    except Exception:
        if created:
            try:
                dest.unlink()
            except OSError:
                pass
        raise
    return fp
