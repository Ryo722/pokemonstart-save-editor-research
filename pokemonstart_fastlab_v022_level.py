#!/usr/bin/env python3
"""Exact-input Fast Lab v0.22 Bulbasaur level/EXP canary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from dataclasses import replace

import pokemonstart_fastlab_v022_stats as fastlab_stats
import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
INPUT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
TARGET_LEVEL = 6


class LevelError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def medium_slow_exp(level: int) -> int:
    """FireRed/CFRU Medium Slow table entry, using source integer order."""
    if not 1 <= level <= 100:
        raise LevelError("level outside 1..100")
    if level == 1:
        return 1
    return (6 * level * level * level) // 5 - 15 * level * level + 100 * level - 140


def level_from_medium_slow_exp(exp: int) -> int:
    level = 1
    while level < 100 and medium_slow_exp(level + 1) <= exp:
        level += 1
    return level


def _profile(raw: bytes, before: v.VerificationResult) -> tx.Profile:
    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    section = active.section(1)
    start = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return tx.Profile(INPUT_SHA256, before.active_slot, active.counter, inactive.counter,
                      section.physical_sector, before.party_count,
                      sha(raw[start:start + v.POKEMON_SIZE]), sha(before.sector30),
                      sha(before.sector31), sha(before.footer))


def _expected_party(mon: v.PartyRecord) -> v.PartyRecord:
    if mon.species != 1 or mon.nature_mint != 0 or mon.hyper_training != 0:
        raise LevelError("only the retained ordinary Bulbasaur profile is supported")
    target_exp = medium_slow_exp(TARGET_LEVEL)
    target_level = level_from_medium_slow_exp(target_exp)
    if target_level != TARGET_LEVEL or level_from_medium_slow_exp(target_exp - 1) != TARGET_LEVEL - 1:
        raise LevelError("growth threshold is not an exact adjacent-level boundary")
    nature = mon.personality % 25
    basis = replace(mon, experience=target_exp, level=target_level)
    hp, max_hp, attack, defense, speed, sp_attack, sp_defense = fastlab_stats.stats(
        basis, level=target_level)
    return replace(basis, hp=hp, max_hp=max_hp, attack=attack,
                   defense=defense, speed=speed,
                   sp_attack=sp_attack, sp_defense=sp_defense)


def derive(raw: bytes) -> tuple[bytes, tx.Fingerprint, dict[str, object]]:
    if sha(raw) != INPUT_SHA256:
        raise LevelError("input is not the exact immutable retained baseline save")
    before = v.verify_bytes(raw)
    if before.party_count != 1:
        raise LevelError("expected exactly one retained party member")
    mon = before.party[0]
    if (mon.species, mon.experience, mon.level, mon.nature_mint, mon.hyper_training,
            mon.ivs, mon.evs) != (1, 134, 5, 0, 0,
                                  (31, 29, 26, 23, 27, 29), (0, 0, 0, 0, 0, 0)):
        raise LevelError("retained baseline party profile mismatch")
    original_nature = mon.personality % 25
    if original_nature != 15:
        raise LevelError("retained personality is not the expected Modest nature")
    if (mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed,
            mon.sp_attack, mon.sp_defense) != fastlab_stats.stats(mon, level=5):
        raise LevelError("starting cached stats do not match existing M3C level-5 formula")
    if mon.hp != mon.max_hp:
        raise LevelError("current HP is not full; this experiment has no damaged-HP policy")

    desired = _expected_party(mon)
    section = before.slots[before.active_slot].section(1)
    record_base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    patches = [
        tx.RecordPatch(36, struct.pack("<I", mon.experience),
                       struct.pack("<I", desired.experience)),
        tx.RecordPatch(84, bytes((mon.level,)), bytes((desired.level,))),
    ]
    old_stats = raw[record_base + 86:record_base + 100]
    new_stats = struct.pack("<7H", desired.hp, desired.max_hp, desired.attack,
                            desired.defense, desired.speed, desired.sp_attack,
                            desired.sp_defense)
    if old_stats != new_stats:
        patches.append(tx.RecordPatch(86, old_stats, new_stats))

    def validate_before(start: v.VerificationResult) -> None:
        if start.party[0] != mon:
            raise tx.TransactionError("baseline party changed during derivation")

    def validate_after(start: v.VerificationResult,
                       finish: v.VerificationResult) -> None:
        target = _expected_party(start.party[0])
        if finish.party[0] != target:
            raise tx.TransactionError("level/EXP/stat invariant failed")
        if level_from_medium_slow_exp(finish.party[0].experience) != finish.party[0].level:
            raise tx.TransactionError("stored level disagrees with growth-table level")

    output, fp = tx.derive(raw, _profile(raw, before), patches,
                           validate_before, validate_after)
    return output, fp, {
        "species": mon.species,
        "experience": {"from": mon.experience, "to": desired.experience},
        "level": {"from": mon.level, "to": desired.level},
        "growth_rate": "Medium Slow",
        "target_threshold_calculation": "(6*n^3)//5 - 15*n^2 + 100*n - 140; n=6",
        "thresholds": {"level_5": medium_slow_exp(5), "level_6": medium_slow_exp(6)},
        "baseline_note": "Input EXP 134 is one below the source Medium Slow level-5 threshold 135 although its cached level/stats are 5; output is made coherent at level 6.",
        "hp_policy": "input HP was full; source rule adds max-HP increase, yielding full HP",
        "stats": {
            "from": [mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed,
                     mon.sp_attack, mon.sp_defense],
            "to": [desired.hp, desired.max_hp, desired.attack, desired.defense,
                   desired.speed, desired.sp_attack, desired.sp_defense],
        },
    }


def write_new(source: Path, output: Path, rom: Path) -> dict[str, object]:
    source, rom = source.resolve(strict=True), rom.resolve(strict=True)
    output = output.resolve(strict=False)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise LevelError("source and ROM must be inside PokemonStart-private")
    if not output.is_relative_to(PRIVATE_ROOT) or output.exists() or output == source:
        raise LevelError("output must be a new path inside PokemonStart-private")
    if sha(rom.read_bytes()) != ROM_SHA256:
        raise LevelError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    candidate, fp, semantics = derive(original)
    if sha(source.read_bytes()) != INPUT_SHA256:
        raise LevelError("input changed before output creation")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
        handle.flush()
        os.fsync(handle.fileno())
    if output.read_bytes() != candidate or sha(source.read_bytes()) != INPUT_SHA256:
        raise LevelError("output persistence mismatch or source changed")
    return {
        "status": "FAST LAB EXPERIMENTAL V0.22 LEVEL/EXP EDITING",
        "input_sha256": fp.input_sha256, "output_sha256": fp.output_sha256,
        "rom_sha256": ROM_SHA256, "active_slot": fp.active_slot,
        "active_counter": fp.active_counter,
        "section1_physical_sector": fp.section1_sector,
        "section1_checksum": {"from": fp.checksum_before, "to": fp.checksum_after},
        "semantics": semantics,
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
    except (OSError, LevelError, v.VerificationError, tx.TransactionError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
