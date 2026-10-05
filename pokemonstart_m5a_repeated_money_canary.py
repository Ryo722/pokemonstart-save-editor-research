#!/usr/bin/env python3
"""One sealed M5A repeated-use canary: exact return hash, 9,999,999 -> 1,234,567."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path

import pokemonstart_save_verifier as verifier

EXPECTED_INPUT_SHA256 = "1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4"
EXPECTED_START_MONEY = 9_999_999
TARGET_MONEY = 1_234_567
# Sealed from independent byte derivation of the exact allowlisted input.
EXPECTED_OUTPUT_SHA256 = "b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7"
EXPECTED_DIFFS: dict[int, tuple[int, int]] = {
    0x03290: (0x7F, 0x87), 0x03291: (0x96, 0xD6), 0x03292: (0x98, 0x12),
    0x03FF6: (0xA7, 0x29), 0x03FF7: (0xA7, 0xE7),
}


class ProofError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sections(raw: bytes):
    result = verifier.verify_bytes(raw)
    if result.file_size not in (verifier.FLASH_SIZE, verifier.FLASH_SIZE + verifier.RTC_FOOTER_SIZE):
        raise ProofError("unsupported S0 layout")
    if result.active_slot not in (0, 1):
        raise ProofError("active slot invalid")
    active = result.slots[result.active_slot]
    if active.counter is None or result.active_slot != active.counter % 2:
        raise ProofError("active slot/counter parity invalid")
    # The verifier has already validated signatures, checksums, IDs and unique slot choice.
    return result, active


def _diffs(before: bytes, after: bytes) -> dict[int, tuple[int, int]]:
    if len(before) != len(after):
        raise ProofError("file length changed")
    return {i: (a, b) for i, (a, b) in enumerate(zip(before, after)) if a != b}


def derive_candidate(raw: bytes) -> tuple[bytes, dict]:
    """Semantic helper; production authorization remains bound to one exact input hash."""
    digest = _sha(raw)
    if digest != EXPECTED_INPUT_SHA256:
        raise ProofError(f"unrecognized input SHA-256 {digest}")
    try:
        before_result, active = _sections(raw)
    except verifier.VerificationError as exc:
        raise ProofError(f"S0 rejected: {exc}") from exc
    sec0 = active.section(0)
    sec1 = active.section(1)
    key = struct.unpack_from("<I", sec0.data, 0xF20)[0]
    stored = struct.unpack_from("<I", sec1.data, 0x290)[0]
    money = stored ^ key
    if money != EXPECTED_START_MONEY:
        raise ProofError(f"starting money mismatch: {money}")

    out = bytearray(raw)
    money_abs = sec1.physical_sector * verifier.SECTOR_SIZE + 0x290
    struct.pack_into("<I", out, money_abs, TARGET_MONEY ^ key)
    checksum_abs = sec1.physical_sector * verifier.SECTOR_SIZE + verifier.SECTION_CHECKSUM_OFFSET
    checksum = verifier.calculate_save_checksum(bytes(out[sec1.physical_sector * verifier.SECTOR_SIZE:
        sec1.physical_sector * verifier.SECTOR_SIZE + verifier.SECTION_LENGTHS[1]]))
    struct.pack_into("<H", out, checksum_abs, checksum)
    candidate = bytes(out)

    diffs = _diffs(raw, candidate)
    if diffs != EXPECTED_DIFFS:
        raise ProofError(f"complete diff mismatch: {diffs!r}")
    if EXPECTED_OUTPUT_SHA256 is not None and _sha(candidate) != EXPECTED_OUTPUT_SHA256:
        raise ProofError(f"output SHA-256 mismatch: {_sha(candidate)}")
    try:
        after_result, after_active = _sections(candidate)
    except verifier.VerificationError as exc:
        raise ProofError(f"writer output failed verifier: {exc}") from exc
    out_key = struct.unpack_from("<I", after_active.section(0).data, 0xF20)[0]
    out_money = struct.unpack_from("<I", after_active.section(1).data, 0x290)[0] ^ out_key
    if out_money != TARGET_MONEY:
        raise ProofError("decoded target money mismatch")
    if after_result.active_slot != before_result.active_slot or tuple(s.counter for s in after_result.slots) != tuple(s.counter for s in before_result.slots):
        raise ProofError("slot/counter changed")
    if out_key != key:
        raise ProofError("encryption key changed")
    return candidate, {
        "input_sha256": digest, "output_sha256": _sha(candidate),
        "active_slot": before_result.active_slot, "counter": active.counter,
        "key": key, "starting_money": money, "target_money": out_money,
        "section1_physical": sec1.physical_sector,
        "diffs": {f"0x{k:05X}": [f"0x{a:02X}", f"0x{b:02X}"] for k, (a, b) in sorted(diffs.items())},
    }


def write_new(input_path: Path, output_path: Path) -> dict:
    try:
        if input_path.resolve(strict=True) == output_path.resolve(strict=False):
            raise ProofError("output aliases input")
    except FileNotFoundError as exc:
        raise ProofError("input does not exist") from exc
    if output_path.exists():
        raise ProofError("output already exists")
    if output_path.resolve(strict=False).is_relative_to(Path(__file__).resolve().parent):
        raise ProofError("output must be outside repository")
    raw = input_path.read_bytes()
    source_hash = _sha(raw)
    candidate, receipt = derive_candidate(raw)
    if _sha(input_path.read_bytes()) != source_hash:
        raise ProofError("source changed before publication")
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(candidate)
            handle.flush()
            os.fsync(handle.fileno())
        persisted = output_path.read_bytes()
        if persisted != candidate or _diffs(raw, persisted) != EXPECTED_DIFFS:
            raise ProofError("published bytes/diff differ")
        # Required independent re-run of the repository verifier.
        persisted_result = verifier.verify_bytes(persisted)
        persisted_active = persisted_result.slots[persisted_result.active_slot]
        persisted_key = struct.unpack_from("<I", persisted_active.section(0).data, 0xF20)[0]
        persisted_money = struct.unpack_from("<I", persisted_active.section(1).data, 0x290)[0] ^ persisted_key
        if persisted_money != TARGET_MONEY:
            raise ProofError("persisted decoded target money mismatch")
        if _sha(input_path.read_bytes()) != source_hash:
            raise ProofError("source changed during publication")
    except Exception:
        output_path.unlink(missing_ok=True)
        raise
    receipt["source_immutable"] = True
    receipt["output_path"] = str(output_path)
    return receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps({"status": "GENERATED", **write_new(args.input, args.output)}, indent=2, sort_keys=True))
    except (OSError, ProofError, verifier.VerificationError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
