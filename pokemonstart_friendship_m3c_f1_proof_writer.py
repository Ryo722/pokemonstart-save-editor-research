#!/usr/bin/env python3
"""M3C-F1 bounded friendship proof writer for the retained v0.15 lineage."""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import pokemonstart_save_verifier as v

EXPECTED_INPUT_SHA256 = (
    "d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282"
)
EXPECTED_OUTPUT_SHA256 = (
    "10f13894cab59922989e2b0508b41f2eef276e8c45b2778d6e6b1a309d2f98ae"
)
EXPECTED_DIFFS = ((0x12061, 0x32, 0x33), (0x12FF7, 0x1C, 0x1D))
EXPECTED_ACTIVE_SLOT = 1
EXPECTED_ACTIVE_COUNTER = 3
EXPECTED_INACTIVE_COUNTER = 2
TARGET_PARTY_INDEX = 0
EXPECTED_OLD_FRIENDSHIP = 50
TARGET_FRIENDSHIP = 51
FRIENDSHIP_OFFSET_IN_RECORD = 41

EXPECTED_PARTY_SPECIES = 1
EXPECTED_PARTY_LEVEL = 5
EXPECTED_PARTY_EXP = 134
EXPECTED_PARTY_BALL = 3
EXPECTED_PARTY_MOVES = (33, 45, 0, 0)
EXPECTED_PARTY_PP = (35, 40, 0, 0)
EXPECTED_PARTY_EVS = (0, 0, 0, 0, 0, 0)
EXPECTED_PARTY_IVS = (31, 29, 26, 23, 27, 29)
EXPECTED_PARTY_HP = (21, 21)
EXPECTED_PARTY_STATS = (9, 11, 10, 13, 12)

EXPECTED_SECTOR30_SHA256 = (
    "335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525"
)
EXPECTED_SECTOR31_SHA256 = (
    "ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7"
)
EXPECTED_FOOTER_SHA256 = (
    "62cdba6ee59f22ce914c34e4007c31bead308d63393d43b18e3c774796b562cb"
)


class WriterError(ValueError):
    """Raised when the bounded M3C-F1 writer must refuse a write."""


@dataclass(frozen=True)
class CandidateFingerprint:
    input_sha256: str
    output_sha256: str
    active_slot: int
    active_counter: int
    section1_physical_sector: int
    friendship_offset: int
    checksum_offset: int
    old_friendship: int
    new_friendship: int
    diffs: tuple[tuple[int, int, int], ...]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _diffs(before: bytes, after: bytes) -> tuple[tuple[int, int, int], ...]:
    if len(before) != len(after):
        raise WriterError("output length changed")
    return tuple(
        (offset, old, new)
        for offset, (old, new) in enumerate(zip(before, after))
        if old != new
    )


def _section_map(slot: v.SlotInfo) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        (section.section_id, section.physical_sector, section.counter, section.signature)
        for section in slot.sections
    )


def _check_input_profile(before: v.VerificationResult) -> None:
    if before.active_slot != EXPECTED_ACTIVE_SLOT:
        raise WriterError(
            f"active slot {before.active_slot}, expected {EXPECTED_ACTIVE_SLOT}"
        )

    slot0, slot1 = before.slots
    if slot0.state != "valid" or slot1.state != "valid":
        raise WriterError("M3C-F1 requires both save slots valid")

    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    if active.counter != EXPECTED_ACTIVE_COUNTER:
        raise WriterError(
            f"active counter {active.counter}, expected {EXPECTED_ACTIVE_COUNTER}"
        )
    if inactive.counter != EXPECTED_INACTIVE_COUNTER:
        raise WriterError(
            f"inactive counter {inactive.counter}, expected {EXPECTED_INACTIVE_COUNTER}"
        )
    if active.counter is None or before.active_slot != active.counter % 2:
        raise WriterError("active slot/counter parity mismatch")

    if before.party_count <= TARGET_PARTY_INDEX:
        raise WriterError("party[0] is not present")

    mon = before.party[TARGET_PARTY_INDEX]
    if mon.friendship != EXPECTED_OLD_FRIENDSHIP:
        raise WriterError(
            f"party[0] friendship is {mon.friendship}, "
            f"expected {EXPECTED_OLD_FRIENDSHIP}"
        )

    expected_profile = (
        EXPECTED_PARTY_SPECIES,
        EXPECTED_PARTY_LEVEL,
        EXPECTED_PARTY_EXP,
        EXPECTED_PARTY_BALL,
        EXPECTED_PARTY_MOVES,
        EXPECTED_PARTY_PP,
        EXPECTED_PARTY_EVS,
        EXPECTED_PARTY_IVS,
        EXPECTED_PARTY_HP,
        EXPECTED_PARTY_STATS,
    )
    actual_profile = (
        mon.species,
        mon.level,
        mon.experience,
        mon.ball,
        mon.moves,
        mon.pp,
        mon.evs,
        mon.ivs,
        (mon.hp, mon.max_hp),
        (mon.attack, mon.defense, mon.speed, mon.sp_attack, mon.sp_defense),
    )
    if actual_profile != expected_profile:
        raise WriterError("party[0] profile mismatch")

    if _sha256(before.sector30) != EXPECTED_SECTOR30_SHA256:
        raise WriterError("sector 30 profile mismatch")
    if _sha256(before.sector31) != EXPECTED_SECTOR31_SHA256:
        raise WriterError("sector 31 profile mismatch")
    if (
        len(before.footer) != v.RTC_FOOTER_SIZE
        or _sha256(before.footer) != EXPECTED_FOOTER_SHA256
    ):
        raise WriterError("opaque footer profile mismatch")


def derive_candidate_fingerprint(
    raw: bytes,
) -> tuple[bytes, CandidateFingerprint]:
    """Derive the exact M3C-F1 candidate in memory without file writes."""

    input_sha = _sha256(raw)
    if input_sha != EXPECTED_INPUT_SHA256:
        raise WriterError(f"unsupported M3C-F1 input sha256 {input_sha}")

    before = v.verify_bytes(raw)
    _check_input_profile(before)

    section1 = before.slots[before.active_slot].section(1)
    sector_base = section1.physical_sector * v.SECTOR_SIZE
    friendship_offset = (
        sector_base
        + v.PARTY_OFFSET
        + TARGET_PARTY_INDEX * v.POKEMON_SIZE
        + FRIENDSHIP_OFFSET_IN_RECORD
    )
    checksum_offset = sector_base + v.SECTION_CHECKSUM_OFFSET

    output_bytes = bytearray(raw)
    if output_bytes[friendship_offset] != EXPECTED_OLD_FRIENDSHIP:
        raise WriterError("raw friendship byte/profile disagreement")
    output_bytes[friendship_offset] = TARGET_FRIENDSHIP

    section_payload = bytes(
        output_bytes[sector_base : sector_base + v.SECTION_LENGTHS[1]]
    )
    new_checksum = v.calculate_save_checksum(section_payload)
    struct.pack_into("<H", output_bytes, checksum_offset, new_checksum)
    output = bytes(output_bytes)

    actual_diffs = _diffs(raw, output)
    allowed_offsets = {friendship_offset, checksum_offset, checksum_offset + 1}
    if not actual_diffs:
        raise WriterError("candidate produced no diff")
    if any(offset not in allowed_offsets for offset, _, _ in actual_diffs):
        raise WriterError("candidate diff escaped field/checksum envelope")

    after = v.verify_bytes(output)
    if after.active_slot != before.active_slot:
        raise WriterError("active slot changed")
    if tuple(slot.counter for slot in after.slots) != tuple(
        slot.counter for slot in before.slots
    ):
        raise WriterError("slot counter changed")
    if tuple(_section_map(slot) for slot in after.slots) != tuple(
        _section_map(slot) for slot in before.slots
    ):
        raise WriterError("section metadata/permutation changed")
    if after.party_count != before.party_count:
        raise WriterError("party count changed")
    if after.party[0] != replace(before.party[0], friendship=TARGET_FRIENDSHIP):
        raise WriterError("party record invariant failed")
    if after.footer != before.footer:
        raise WriterError("opaque footer changed")
    if after.sector30 != before.sector30 or after.sector31 != before.sector31:
        raise WriterError("sector 30/31 changed")

    return output, CandidateFingerprint(
        input_sha256=input_sha,
        output_sha256=_sha256(output),
        active_slot=before.active_slot,
        active_counter=EXPECTED_ACTIVE_COUNTER,
        section1_physical_sector=section1.physical_sector,
        friendship_offset=friendship_offset,
        checksum_offset=checksum_offset,
        old_friendship=EXPECTED_OLD_FRIENDSHIP,
        new_friendship=TARGET_FRIENDSHIP,
        diffs=actual_diffs,
    )


def _require_sealed(fingerprint: CandidateFingerprint) -> None:
    if fingerprint.diffs != EXPECTED_DIFFS:
        raise WriterError(f"non-allowlisted M3C-F1 diff: {fingerprint.diffs!r}")
    if fingerprint.output_sha256 != EXPECTED_OUTPUT_SHA256:
        raise WriterError(
            f"unexpected M3C-F1 output sha256 {fingerprint.output_sha256}"
        )


def build_proof_output(raw: bytes) -> tuple[bytes, CandidateFingerprint]:
    output, fingerprint = derive_candidate_fingerprint(raw)
    _require_sealed(fingerprint)
    return output, fingerprint


def write_proof_file(
    input_path: str | Path, output_path: str | Path
) -> CandidateFingerprint:
    source = Path(input_path)
    destination = Path(output_path)

    if source.resolve() == destination.resolve():
        raise WriterError("refusing to overwrite the input save")
    if destination.exists():
        raise WriterError("refusing to overwrite an existing output path")

    raw = source.read_bytes()
    output, fingerprint = build_proof_output(raw)

    created = False
    try:
        with destination.open("xb") as handle:
            created = True
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())

        if destination.read_bytes() != output:
            raise WriterError("written output does not match verified bytes")
        if _sha256(source.read_bytes()) != fingerprint.input_sha256:
            raise WriterError("input changed during proof write")
    except Exception:
        if created:
            try:
                destination.unlink()
            except OSError:
                pass
        raise

    return fingerprint


def format_fingerprint(fingerprint: CandidateFingerprint) -> str:
    lines = [
        "status: DERIVED",
        f"input_sha256: {fingerprint.input_sha256}",
        f"output_sha256: {fingerprint.output_sha256}",
        f"active_slot: {fingerprint.active_slot}",
        f"active_counter: {fingerprint.active_counter}",
        f"section1_physical_sector: {fingerprint.section1_physical_sector}",
        f"party[0].friendship: {fingerprint.old_friendship}->{fingerprint.new_friendship}",
    ]
    for offset, old, new in fingerprint.diffs:
        lines.append(f"diff: 0x{offset:X} {old:02X}->{new:02X}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="M3C-F1 bounded sealed friendship proof writer."
    )
    parser.add_argument("input", help="exact retained M3C-F1 private input")
    parser.add_argument(
        "--derive-only",
        action="store_true",
        help="derive and verify the sealed candidate fingerprint in memory only",
    )
    parser.add_argument("--output", help="new output path")
    args = parser.parse_args(argv)

    try:
        raw = Path(args.input).read_bytes()
        if args.derive_only:
            _, fingerprint = build_proof_output(raw)
            print(format_fingerprint(fingerprint))
            return 0
        if not args.output:
            raise WriterError("--output is required unless --derive-only is used")
        fingerprint = write_proof_file(args.input, args.output)
    except (OSError, v.VerificationError, WriterError) as exc:
        print("status: REJECTED")
        print(f"reason: {exc}")
        return 2

    print("status: WRITTEN")
    print(format_fingerprint(fingerprint))
    return 0


if __name__ == "__main__":
    sys.exit(main())
