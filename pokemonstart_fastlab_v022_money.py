#!/usr/bin/env python3
"""One exact-input disposable v0.22 Fast Lab Money experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

import pokemonstart_save_verifier as verifier

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
INPUT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
SOURCE_MONEY = 1_234_567
TARGET_MONEY = 7_654_321


class FastLabError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive(raw: bytes) -> tuple[bytes, dict[str, object]]:
    if sha256(raw) != INPUT_SHA256:
        raise FastLabError("input is not the exact allowlisted disposable source save")
    before = verifier.verify_bytes(raw)
    active = before.slots[before.active_slot]
    if active.counter is None or before.active_slot != active.counter % 2:
        raise FastLabError("active slot/counter parity is unsupported")
    sec0, sec1 = active.section(0), active.section(1)
    key = struct.unpack_from("<I", sec0.data, 0xF20)[0]
    stored = struct.unpack_from("<I", sec1.data, 0x290)[0]
    decoded = stored ^ key
    if decoded != SOURCE_MONEY:
        raise FastLabError(f"starting Money mismatch: {decoded}")
    if not 0 <= TARGET_MONEY <= 9_999_999:
        raise FastLabError("target is outside the supported Money range")

    out = bytearray(raw)
    sec1_base = sec1.physical_sector * verifier.SECTOR_SIZE
    struct.pack_into("<I", out, sec1_base + 0x290, TARGET_MONEY ^ key)
    payload_end = sec1_base + verifier.SECTION_LENGTHS[1]
    checksum = verifier.calculate_save_checksum(bytes(out[sec1_base:payload_end]))
    struct.pack_into("<H", out, sec1_base + verifier.SECTION_CHECKSUM_OFFSET, checksum)
    candidate = bytes(out)
    after = verifier.verify_bytes(candidate)
    after_active = after.slots[after.active_slot]
    out_key = struct.unpack_from("<I", after_active.section(0).data, 0xF20)[0]
    out_money = struct.unpack_from("<I", after_active.section(1).data, 0x290)[0] ^ out_key
    if out_money != TARGET_MONEY or out_key != key:
        raise FastLabError("independent verifier did not confirm target Money/key")
    if (after.active_slot != before.active_slot or after_active.counter != active.counter
            or after.party_count != before.party_count
            or after_active.section(1).data[0x38:0x38 + 600]
            != sec1.data[0x38:0x38 + 600]):
        raise FastLabError("non-Money active-save state changed")
    allowed = {sec1_base + 0x290 + i for i in range(4)} | {
        sec1_base + verifier.SECTION_CHECKSUM_OFFSET,
        sec1_base + verifier.SECTION_CHECKSUM_OFFSET + 1,
    }
    diffs = {i for i, (old, new) in enumerate(zip(raw, candidate)) if old != new}
    if not diffs or not diffs <= allowed:
        raise FastLabError(f"unexpected output byte changes: {sorted(diffs - allowed)}")
    return candidate, {
        "input_sha256": sha256(raw), "output_sha256": sha256(candidate),
        "rom_sha256": ROM_SHA256, "active_slot": before.active_slot,
        "counter": active.counter, "encryption_key": key,
        "source_money": decoded, "target_money": out_money,
        "money_logical_section": 1, "money_section_offset": "0x0290",
        "physical_sector": sec1.physical_sector,
        "changed_byte_count": len(diffs),
    }


def write_new(input_path: Path, output_path: Path, rom_path: Path) -> dict[str, object]:
    source = input_path.resolve(strict=True)
    destination = output_path.resolve(strict=False)
    rom = rom_path.resolve(strict=True)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise FastLabError("ROM and source save must be inside PokemonStart-private")
    if source == destination or destination.exists():
        raise FastLabError("output must be a new path distinct from source")
    if not destination.is_relative_to(PRIVATE_ROOT):
        raise FastLabError("output must be inside PokemonStart-private")
    if sha256(rom.read_bytes()) != ROM_SHA256:
        raise FastLabError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    if sha256(original) != INPUT_SHA256:
        raise FastLabError("source save hash is not allowlisted")
    candidate, result = derive(original)
    if sha256(source.read_bytes()) != INPUT_SHA256:
        raise FastLabError("source save changed before output creation")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(candidate)
            handle.flush()
            os.fsync(handle.fileno())
        persisted = destination.read_bytes()
        if persisted != candidate or sha256(persisted) != result["output_sha256"]:
            raise FastLabError("published output does not match verified candidate")
        verified = verifier.verify_bytes(persisted)
        active = verified.slots[verified.active_slot]
        key = struct.unpack_from("<I", active.section(0).data, 0xF20)[0]
        money = struct.unpack_from("<I", active.section(1).data, 0x290)[0] ^ key
        if money != TARGET_MONEY:
            raise FastLabError("persisted output failed Money re-verification")
        if sha256(source.read_bytes()) != INPUT_SHA256:
            raise FastLabError("source save changed during publication")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    result["source_immutable"] = True
    result["output_path"] = str(destination)
    result["status"] = "GENERATED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_save", type=Path)
    parser.add_argument("output_save", type=Path)
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(write_new(args.source_save, args.output_save, args.rom), indent=2))
    except (OSError, FastLabError, verifier.VerificationError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
