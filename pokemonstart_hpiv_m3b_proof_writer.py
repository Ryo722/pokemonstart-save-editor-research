#!/usr/bin/env python3
"""M3B bounded same-field proof writer for the retained v0.15 lineage.

This candidate targets exactly the fresh M2 round-trip input and changes only
party[0] HP IV 30 -> 31. The exact complete diff and output SHA-256 were
derived from the authorized private input, independently checked against the
M3A transaction envelope, and are sealed below. This remains a proof-only
writer and does not authorize support for arbitrary saves or additional fields.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

import pokemonstart_save_verifier as v

EXPECTED_INPUT_SHA256 = (
    "c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac"
)
EXPECTED_OUTPUT_SHA256 = (
    "cf2ca33a303b6409300ac4032c7c47efd9859562bc06fe18e89481bb93ea5f1f"
)
EXPECTED_DIFFS = ((0x3080, 0xBE, 0xBF), (0x3FF6, 0x20, 0x21))
EXPECTED_ACTIVE_SLOT = 0
EXPECTED_ACTIVE_COUNTER = 2
EXPECTED_INACTIVE_COUNTER = 1
TARGET_PARTY_INDEX = 0
EXPECTED_OLD_HP_IV = 30
TARGET_HP_IV = 31
IV_WORD_OFFSET_IN_RECORD = 72
EXPECTED_SECTOR30_SHA256 = (
    "335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525"
)
EXPECTED_SECTOR31_SHA256 = (
    "ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7"
)
EXPECTED_FOOTER_SHA256 = (
    "0f5e9be128e35fb5926268e15f441e442ff54ab712ba7fa50418761a4170ed0f"
)


class WriterError(ValueError):
    """Raised when the bounded M3B candidate must refuse a write."""


@dataclass(frozen=True)
class CandidateFingerprint:
    input_sha256: str
    output_sha256: str
    active_slot: int
    active_counter: int
    section1_physical_sector: int
    iv_offset: int
    checksum_offset: int
    old_hp_iv: int
    new_hp_iv: int
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
        raise WriterError("M3B requires both save slots valid")

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
    if before.party[TARGET_PARTY_INDEX].ivs[0] != EXPECTED_OLD_HP_IV:
        raise WriterError(
            "party[0] HP IV is "
            f"{before.party[TARGET_PARTY_INDEX].ivs[0]}, "
            f"expected {EXPECTED_OLD_HP_IV}"
        )

    if _sha256(before.sector30) != EXPECTED_SECTOR30_SHA256:
        raise WriterError("sector 30 profile mismatch")
    if _sha256(before.sector31) != EXPECTED_SECTOR31_SHA256:
        raise WriterError("sector 31 profile mismatch")
    if (
        len(before.footer) != v.RTC_FOOTER_SIZE
        or _sha256(before.footer) != EXPECTED_FOOTER_SHA256
    ):
        raise WriterError("opaque footer profile mismatch")


def _allowed_diff_offsets(iv_offset: int, checksum_offset: int) -> set[int]:
    return set(range(iv_offset, iv_offset + 4)) | {
        checksum_offset,
        checksum_offset + 1,
    }


def derive_candidate_fingerprint(
    raw: bytes,
) -> tuple[bytes, CandidateFingerprint]:
    """Derive the exact M3B candidate entirely in memory, without file writes."""

    input_sha = _sha256(raw)
    if input_sha != EXPECTED_INPUT_SHA256:
        raise WriterError(f"unsupported M3B input sha256 {input_sha}")

    before = v.verify_bytes(raw)
    _check_input_profile(before)

    section1 = before.slots[before.active_slot].section(1)
    sector_base = section1.physical_sector * v.SECTOR_SIZE
    iv_offset = (
        sector_base
        + v.PARTY_OFFSET
        + TARGET_PARTY_INDEX * v.POKEMON_SIZE
        + IV_WORD_OFFSET_IN_RECORD
    )
    checksum_offset = sector_base + v.SECTION_CHECKSUM_OFFSET

    output_bytes = bytearray(raw)
    old_word = struct.unpack_from("<I", output_bytes, iv_offset)[0]
    new_word = (old_word & ~0x1F) | TARGET_HP_IV
    struct.pack_into("<I", output_bytes, iv_offset, new_word)

    section_payload = bytes(
        output_bytes[sector_base : sector_base + v.SECTION_LENGTHS[1]]
    )
    new_checksum = v.calculate_save_checksum(section_payload)
    struct.pack_into("<H", output_bytes, checksum_offset, new_checksum)
    output = bytes(output_bytes)

    actual_diffs = _diffs(raw, output)
    if not actual_diffs:
        raise WriterError("candidate produced no diff")
    allowed_offsets = _allowed_diff_offsets(iv_offset, checksum_offset)
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
    if after.party[0].ivs != (TARGET_HP_IV,) + before.party[0].ivs[1:]:
        raise WriterError("party IV invariant failed")
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
        iv_offset=iv_offset,
        checksum_offset=checksum_offset,
        old_hp_iv=EXPECTED_OLD_HP_IV,
        new_hp_iv=TARGET_HP_IV,
        diffs=actual_diffs,
    )


def _require_sealed(fingerprint: CandidateFingerprint) -> None:
    if fingerprint.diffs != EXPECTED_DIFFS:
        raise WriterError(f"non-allowlisted M3B diff: {fingerprint.diffs!r}")
    if fingerprint.output_sha256 != EXPECTED_OUTPUT_SHA256:
        raise WriterError(
            f"unexpected M3B output sha256 {fingerprint.output_sha256}"
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
        f"party[0].hp_iv: {fingerprint.old_hp_iv}->{fingerprint.new_hp_iv}",
    ]
    for offset, old, new in fingerprint.diffs:
        lines.append(f"diff: 0x{offset:X} {old:02X}->{new:02X}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="M3B bounded sealed same-field proof writer."
    )
    parser.add_argument("input", help="exact retained M3B private input")
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
