#!/usr/bin/env python3
"""Exact-input Fast Lab v0.22 low-coupling party write experiment."""
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
OLD_FRIENDSHIP, NEW_FRIENDSHIP = 50, 51


class PartyError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def derive(raw: bytes) -> tuple[bytes, dict[str, object]]:
    if sha(raw) != INPUT_SHA256:
        raise PartyError("input is not the exact retained Fast Lab source save")
    before = verifier.verify_bytes(raw)
    active = before.slots[before.active_slot]
    mon = before.party[0]
    if (before.party_count != 1 or mon.species != 1 or mon.level != 5
            or mon.experience != 134 or mon.friendship != OLD_FRIENDSHIP):
        raise PartyError("starting party profile mismatch")
    sec = active.section(1)
    base = sec.physical_sector * verifier.SECTOR_SIZE
    record = base + verifier.PARTY_OFFSET
    target = record + 41  # existing M3C party model: direct friendship u8
    out = bytearray(raw)
    if out[target] != OLD_FRIENDSHIP:
        raise PartyError("raw friendship byte does not match decoded value")
    out[target] = NEW_FRIENDSHIP
    check = base + verifier.SECTION_CHECKSUM_OFFSET
    payload_end = base + verifier.SECTION_LENGTHS[1]
    struct.pack_into("<H", out, check, verifier.calculate_save_checksum(bytes(out[base:payload_end])))
    candidate = bytes(out)
    after = verifier.verify_bytes(candidate)
    if after.party[0].friendship != NEW_FRIENDSHIP:
        raise PartyError("verifier did not decode target friendship")
    allowed = {target, check, check + 1}
    diffs = [i for i, (a, b) in enumerate(zip(raw, candidate)) if a != b]
    if not diffs or not set(diffs) <= allowed:
        raise PartyError("output changed bytes outside friendship/checksum")
    return candidate, {"input_sha256": sha(raw), "output_sha256": sha(candidate),
                       "rom_sha256": ROM_SHA256, "field": "party[0].friendship",
                       "from": OLD_FRIENDSHIP, "to": NEW_FRIENDSHIP,
                       "record_offset": 41, "physical_sector": sec.physical_sector,
                       "section_checksum": {"from": sec.checksum_stored,
                                            "to": after.slots[after.active_slot].section(1).checksum_stored},
                       "diffs": diffs, "status": "FAST LAB EXPERIMENTAL V0.22 PARTY WRITE"}


def write_new(source: Path, output: Path, rom: Path) -> dict[str, object]:
    source, rom = source.resolve(strict=True), rom.resolve(strict=True)
    output = output.resolve(strict=False)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise PartyError("source and ROM must be inside PokemonStart-private")
    if not output.is_relative_to(PRIVATE_ROOT) or output.exists() or output == source:
        raise PartyError("output must be a new path inside PokemonStart-private")
    if sha(rom.read_bytes()) != ROM_SHA256:
        raise PartyError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    candidate, report = derive(original)
    if sha(source.read_bytes()) != INPUT_SHA256:
        raise PartyError("source save changed during preparation")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(candidate)
        f.flush()
        os.fsync(f.fileno())
    if output.read_bytes() != candidate or sha(source.read_bytes()) != INPUT_SHA256:
        raise PartyError("published output mismatch or source changed")
    report["output_path"] = str(output)
    report["source_immutable"] = True
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_save", type=Path)
    p.add_argument("output_save", type=Path)
    p.add_argument("rom", type=Path)
    a = p.parse_args()
    try:
        print(json.dumps(write_new(a.source_save, a.output_save, a.rom), indent=2))
    except (OSError, PartyError, verifier.VerificationError) as e:
        print(f"STOP: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
