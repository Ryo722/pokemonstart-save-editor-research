#!/usr/bin/env python3
"""Bounded M2 proof writer: exact known PokemonStart v0.15 input, party[0] HP IV 31 -> 30 only."""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

import pokemonstart_save_verifier as v

EXPECTED_INPUT_SHA256 = "fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b"
EXPECTED_OUTPUT_SHA256 = "569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc"
EXPECTED_DIFFS = ((0x10080, 0xBF, 0xBE), (0x10FF6, 0x62, 0x61))
TARGET_PARTY_INDEX = 0
EXPECTED_OLD_HP_IV = 31
TARGET_HP_IV = 30
IV_WORD_OFFSET_IN_RECORD = 72


class WriterError(ValueError):
    """Raised when this proof writer must refuse the requested write."""


@dataclass(frozen=True)
class ProofResult:
    input_sha256: str
    output_sha256: str
    active_slot: int
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
    return tuple((i, a, b) for i, (a, b) in enumerate(zip(before, after)) if a != b)


def build_proof_output(raw: bytes) -> tuple[bytes, ProofResult]:
    """Build only the one exact, allowlisted M2 proof output."""
    input_sha = _sha256(raw)
    if input_sha != EXPECTED_INPUT_SHA256:
        raise WriterError(f"unsupported proof input sha256 {input_sha}")

    before = v.verify_bytes(raw)
    if before.party_count <= TARGET_PARTY_INDEX:
        raise WriterError("party[0] is not present")
    if before.party[TARGET_PARTY_INDEX].ivs[0] != EXPECTED_OLD_HP_IV:
        raise WriterError(
            f"party[0] HP IV is {before.party[TARGET_PARTY_INDEX].ivs[0]}, "
            f"expected {EXPECTED_OLD_HP_IV}"
        )

    selected = before.slots[before.active_slot]
    section1 = selected.section(1)
    sector_base = section1.physical_sector * v.SECTOR_SIZE
    iv_offset = (
        sector_base
        + v.PARTY_OFFSET
        + TARGET_PARTY_INDEX * v.POKEMON_SIZE
        + IV_WORD_OFFSET_IN_RECORD
    )
    checksum_offset = sector_base + v.SECTION_CHECKSUM_OFFSET

    out = bytearray(raw)
    old_word = struct.unpack_from("<I", out, iv_offset)[0]
    new_word = (old_word & ~0x1F) | TARGET_HP_IV
    struct.pack_into("<I", out, iv_offset, new_word)

    section_payload = bytes(out[sector_base : sector_base + v.SECTION_LENGTHS[1]])
    new_checksum = v.calculate_save_checksum(section_payload)
    struct.pack_into("<H", out, checksum_offset, new_checksum)
    output = bytes(out)

    actual_diffs = _diffs(raw, output)
    if actual_diffs != EXPECTED_DIFFS:
        rendered = ", ".join(
            f"0x{i:X}:{a:02X}->{b:02X}" for i, a, b in actual_diffs
        )
        raise WriterError(f"non-allowlisted diff: [{rendered}]")

    output_sha = _sha256(output)
    if output_sha != EXPECTED_OUTPUT_SHA256:
        raise WriterError(f"unexpected proof output sha256 {output_sha}")

    after = v.verify_bytes(output)
    if after.active_slot != before.active_slot:
        raise WriterError("active slot changed")
    if after.party_count != before.party_count:
        raise WriterError("party count changed")
    if after.party[0].ivs != (TARGET_HP_IV,) + before.party[0].ivs[1:]:
        raise WriterError("party IV invariant failed")
    if after.footer != before.footer:
        raise WriterError("opaque emulator footer changed")
    if after.sector30 != before.sector30 or after.sector31 != before.sector31:
        raise WriterError("sector 30/31 changed")

    return output, ProofResult(
        input_sha256=input_sha,
        output_sha256=output_sha,
        active_slot=before.active_slot,
        section1_physical_sector=section1.physical_sector,
        iv_offset=iv_offset,
        checksum_offset=checksum_offset,
        old_hp_iv=EXPECTED_OLD_HP_IV,
        new_hp_iv=TARGET_HP_IV,
        diffs=actual_diffs,
    )


def write_proof_file(input_path: str | Path, output_path: str | Path) -> ProofResult:
    src = Path(input_path)
    dst = Path(output_path)
    if src.resolve() == dst.resolve():
        raise WriterError("refusing to overwrite the input save")
    if dst.exists():
        raise WriterError("refusing to overwrite an existing output path")

    raw = src.read_bytes()
    output, result = build_proof_output(raw)

    created = False
    try:
        with dst.open("xb") as handle:
            created = True
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        written = dst.read_bytes()
        if written != output:
            raise WriterError("written output does not match verified bytes")
        if _sha256(src.read_bytes()) != result.input_sha256:
            raise WriterError("input changed during proof write")
    except Exception:
        if created:
            try:
                dst.unlink()
            except OSError:
                pass
        raise
    return result


def format_result(result: ProofResult) -> str:
    lines = [
        "status: WRITTEN",
        f"input_sha256: {result.input_sha256}",
        f"output_sha256: {result.output_sha256}",
        f"active_slot: {result.active_slot}",
        f"section1_physical_sector: {result.section1_physical_sector}",
        f"party[0].hp_iv: {result.old_hp_iv}->{result.new_hp_iv}",
    ]
    for offset, old, new in result.diffs:
        lines.append(f"diff: 0x{offset:X} {old:02X}->{new:02X}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "M2 bounded proof writer: exact v0.15 input, party[0] HP IV 31 -> 30 only."
        )
    )
    parser.add_argument("input", help="known before-test save; opened read-only")
    parser.add_argument("output", help="new output path; must not already exist")
    args = parser.parse_args(argv)

    try:
        result = write_proof_file(args.input, args.output)
    except (OSError, v.VerificationError, WriterError) as exc:
        print("status: REJECTED")
        print(f"reason: {exc}")
        return 2

    print(format_result(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
