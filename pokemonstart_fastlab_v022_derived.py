#!/usr/bin/env python3
"""Exact-input Fast Lab v0.22 IV edit using the existing M3C stat model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

import pokemonstart_fastlab_v022_stats as fastlab_stats
import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
INPUT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
FIELDS = ("attack_iv",)


class DerivedError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _profile(raw: bytes, before: v.VerificationResult) -> tx.Profile:
    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    section = active.section(1)
    base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return tx.Profile(
        input_sha256=INPUT_SHA256,
        active_slot=before.active_slot,
        active_counter=active.counter,
        inactive_counter=inactive.counter,
        section1_sector=section.physical_sector,
        party_count=before.party_count,
        record0_sha256=sha(raw[base:base + v.POKEMON_SIZE]),
        sector30_sha256=sha(before.sector30),
        sector31_sha256=sha(before.sector31),
        footer_sha256=sha(before.footer),
    )


def derive(raw: bytes) -> tuple[bytes, tx.Fingerprint, dict[str, object]]:
    if sha(raw) != INPUT_SHA256:
        raise DerivedError("input is not the exact retained Fast Lab save")
    before = v.verify_bytes(raw)
    mon = before.party[0]
    if (before.party_count != 1 or mon.species != 1 or mon.level != 5
            or mon.experience != 134 or mon.nature_mint != 0
            or mon.ivs != (31, 29, 26, 23, 27, 29)
            or mon.evs != (0, 0, 0, 0, 0, 0)):
        raise DerivedError("starting party profile mismatch")
    effective_nature = mon.personality % 25
    if effective_nature != 15:
        raise DerivedError("starting personality is not the M3C Modest profile")
    if (mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed,
            mon.sp_attack, mon.sp_defense) != fastlab_stats.stats(mon):
        raise DerivedError("starting cached stats disagree with reused M3C formula")

    desired = fastlab_stats.after_attack_iv(mon)
    section = before.slots[before.active_slot].section(1)
    record_base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    old_word = struct.unpack_from("<I", raw, record_base + 72)[0]
    new_word = old_word & ~(0x1F << 5)
    old_stats = raw[record_base + 86:record_base + 100]
    new_stats = struct.pack("<7H", desired.hp, desired.max_hp, desired.attack,
                            desired.defense, desired.speed,
                            desired.sp_attack, desired.sp_defense)
    patches = [tx.RecordPatch(72, struct.pack("<I", old_word), struct.pack("<I", new_word))]
    if old_stats != new_stats:
        patches.append(tx.RecordPatch(86, old_stats, new_stats))

    def validate_before(start: v.VerificationResult) -> None:
        if start.party[0] != mon:
            raise tx.TransactionError("starting party changed during derivation")

    def validate_after(start: v.VerificationResult,
                       finish: v.VerificationResult) -> None:
        if finish.party[0] != fastlab_stats.after_attack_iv(start.party[0]):
            raise tx.TransactionError("party record differs from reused M3C expected state")

    output, fingerprint = tx.derive(raw, _profile(raw, before), patches,
                                    validate_before, validate_after)
    after = v.verify_bytes(output)
    return output, fingerprint, {
        "field": "party[0].attack_iv",
        "from": mon.ivs[1], "to": desired.ivs[1],
        "cached_attack": {"from": mon.attack, "to": desired.attack},
        "cached_stats": {
            "from": [mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed,
                     mon.sp_attack, mon.sp_defense],
            "to": [desired.hp, desired.max_hp, desired.attack, desired.defense,
                   desired.speed, desired.sp_attack, desired.sp_defense],
        },
        "ivs_after": list(after.party[0].ivs),
        "evs_after": list(after.party[0].evs),
    }


def write_new(source: Path, output: Path, rom: Path) -> dict[str, object]:
    source, rom = source.resolve(strict=True), rom.resolve(strict=True)
    output = output.resolve(strict=False)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise DerivedError("source and ROM must be inside PokemonStart-private")
    if not output.is_relative_to(PRIVATE_ROOT) or output.exists() or output == source:
        raise DerivedError("output must be a new path inside PokemonStart-private")
    if sha(rom.read_bytes()) != ROM_SHA256:
        raise DerivedError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    output_bytes, fp, semantics = derive(original)
    if sha(source.read_bytes()) != INPUT_SHA256:
        raise DerivedError("input changed before output creation")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(output_bytes)
        handle.flush()
        os.fsync(handle.fileno())
    if output.read_bytes() != output_bytes or sha(source.read_bytes()) != INPUT_SHA256:
        raise DerivedError("output persistence mismatch or source changed")
    return {
        "status": "FAST LAB EXPERIMENTAL V0.22 IV/EV/NATURE EDITING",
        "input_sha256": fp.input_sha256,
        "output_sha256": fp.output_sha256,
        "rom_sha256": ROM_SHA256,
        "active_slot": fp.active_slot,
        "active_counter": fp.active_counter,
        "section1_physical_sector": fp.section1_sector,
        "section1_checksum": {"from": fp.checksum_before,
                              "to": fp.checksum_after},
        "semantics": semantics,
        "diffs": [{"offset": i, "from": a, "to": b} for i, a, b in fp.diffs],
        "source_immutable": True,
        "output_path": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_save", type=Path)
    parser.add_argument("output_save", type=Path)
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(write_new(args.source_save, args.output_save, args.rom), indent=2))
    except (OSError, DerivedError, v.VerificationError, tx.TransactionError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
