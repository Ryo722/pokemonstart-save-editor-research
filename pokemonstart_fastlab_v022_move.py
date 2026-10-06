#!/usr/bin/env python3
"""Exact-input Fast Lab v0.22 one-move replacement after the IV canary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
INPUT_SHA256 = "5a688c2c3f2e3f2ba4e9f73788ead12da715adaae861880aa0ef5f7faeb620de"
MOVE_SLOT, OLD_MOVE, NEW_MOVE = 0, 33, 1
MOVE_OFFSET, PP_OFFSET, PP_BONUSES_OFFSET = 44, 52, 40
OLD_PP = NEW_PP = 35


class MoveError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _profile(raw: bytes, before: v.VerificationResult) -> tx.Profile:
    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    section = active.section(1)
    start = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return tx.Profile(
        INPUT_SHA256, before.active_slot, active.counter, inactive.counter,
        section.physical_sector, before.party_count,
        sha(raw[start:start + v.POKEMON_SIZE]), sha(before.sector30),
        sha(before.sector31), sha(before.footer),
    )


def derive(raw: bytes) -> tuple[bytes, tx.Fingerprint]:
    if sha(raw) != INPUT_SHA256:
        raise MoveError("input is not the exact derived IV experiment save")
    before = v.verify_bytes(raw)
    mon = before.party[0]
    if (before.party_count != 1 or mon.species != 1 or mon.level != 5
            or mon.experience != 134 or mon.moves != (OLD_MOVE, 45, 0, 0)
            or mon.pp != (OLD_PP, 40, 0, 0) or mon.pp_bonuses != 0
            or mon.ivs != (31, 0, 26, 23, 27, 29) or mon.attack != 8):
        raise MoveError("starting party profile mismatch")
    section = before.slots[before.active_slot].section(1)
    base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    if struct.unpack_from("<H", raw, base + MOVE_OFFSET)[0] != OLD_MOVE:
        raise MoveError("raw move[0] does not match decoded value")
    if raw[base + PP_OFFSET] != OLD_PP or raw[base + PP_BONUSES_OFFSET] != 0:
        raise MoveError("raw PP or PP-Up state mismatch")
    # Both Tackle (33) and Pound (1) have 35 base PP in the FireRed move data;
    # no PP-Up is set, so the existing 35 PP remains internally consistent.
    patches = [tx.RecordPatch(MOVE_OFFSET, struct.pack("<H", OLD_MOVE),
                              struct.pack("<H", NEW_MOVE))]

    def validate_before(start: v.VerificationResult) -> None:
        if start.party[0] != mon:
            raise tx.TransactionError("starting party changed during derivation")

    def validate_after(start: v.VerificationResult,
                       finish: v.VerificationResult) -> None:
        expected_moves = (NEW_MOVE, *start.party[0].moves[1:])
        if finish.party[0].moves != expected_moves:
            raise tx.TransactionError("move slot invariant failed")
        if (finish.party[0].pp != start.party[0].pp
                or finish.party[0].pp_bonuses != start.party[0].pp_bonuses):
            raise tx.TransactionError("move replacement changed PP coupling")

    output, fp = tx.derive(raw, _profile(raw, before), patches,
                           validate_before, validate_after)
    return output, fp


def write_new(source: Path, output: Path, rom: Path) -> dict[str, object]:
    source, rom = source.resolve(strict=True), rom.resolve(strict=True)
    output = output.resolve(strict=False)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise MoveError("source and ROM must be inside PokemonStart-private")
    if not output.is_relative_to(PRIVATE_ROOT) or output.exists() or output == source:
        raise MoveError("output must be a new path inside PokemonStart-private")
    if sha(rom.read_bytes()) != ROM_SHA256:
        raise MoveError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    candidate, fp = derive(original)
    if sha(source.read_bytes()) != INPUT_SHA256:
        raise MoveError("input changed before output creation")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
        handle.flush()
        os.fsync(handle.fileno())
    if output.read_bytes() != candidate or sha(source.read_bytes()) != INPUT_SHA256:
        raise MoveError("output persistence mismatch or source changed")
    return {
        "status": "FAST LAB EXPERIMENTAL V0.22 MOVE EDITING",
        "input_sha256": fp.input_sha256, "output_sha256": fp.output_sha256,
        "rom_sha256": ROM_SHA256, "move_slot": MOVE_SLOT,
        "move_id": {"from": OLD_MOVE, "to": NEW_MOVE},
        "pp": {"from": OLD_PP, "to": NEW_PP, "pp_bonuses": 0},
        "section1_checksum": {"from": fp.checksum_before,
                              "to": fp.checksum_after},
        "diffs": [{"offset": i, "from": a, "to": b} for i, a, b in fp.diffs],
        "source_immutable": True, "output_path": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_save", type=Path)
    parser.add_argument("output_save", type=Path)
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(write_new(args.source_save, args.output_save, args.rom), indent=2))
    except (OSError, MoveError, v.VerificationError, tx.TransactionError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
