#!/usr/bin/env python3
"""Exact-input Fast Lab v0.22 Bulbasaur -> Ivysaur canary."""
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
from pokemonstart_fastlab_v022_level import level_from_medium_slow_exp, medium_slow_exp

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
INPUT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"


class SpeciesError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _profile(raw: bytes, before: v.VerificationResult) -> tx.Profile:
    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    section = active.section(1)
    start = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return tx.Profile(INPUT_SHA256, before.active_slot, active.counter, inactive.counter,
                      section.physical_sector, before.party_count,
                      sha(raw[start:start + v.POKEMON_SIZE]), sha(before.sector30),
                      sha(before.sector31), sha(before.footer))


def _target(mon: v.PartyRecord) -> v.PartyRecord:
    # FireRed species data: Ivysaur is species 2, Medium Slow, with base
    # stats HP/Atk/Def/Speed/SpA/SpD = 60/62/63/60/80/80.
    exp = medium_slow_exp(5)
    level = level_from_medium_slow_exp(exp)
    if level != 5 or level_from_medium_slow_exp(exp - 1) != 4:
        raise SpeciesError("target Medium Slow threshold is not coherent")
    basis = replace(mon, species=2, experience=exp, level=level)
    stats = fastlab_stats.stats(basis, level=level)
    return replace(basis, hp=stats[0], max_hp=stats[1], attack=stats[2],
                   defense=stats[3], speed=stats[4], sp_attack=stats[5],
                   sp_defense=stats[6])


def derive(raw: bytes) -> tuple[bytes, tx.Fingerprint, dict[str, object]]:
    if sha(raw) != INPUT_SHA256:
        raise SpeciesError("input is not the exact immutable retained baseline save")
    before = v.verify_bytes(raw)
    if before.party_count != 1:
        raise SpeciesError("expected exactly one retained party member")
    mon = before.party[0]
    if (mon.species, mon.experience, mon.level, mon.nature_mint,
            mon.hyper_training, mon.ability_num, mon.ivs, mon.evs) != (
            1, 134, 5, 0, 0, 0, (31, 29, 26, 23, 27, 29), (0, 0, 0, 0, 0, 0)):
        raise SpeciesError("retained baseline party profile mismatch")
    if mon.personality % 25 != 15:
        raise SpeciesError("expected retained Modest nature")
    expected_before = fastlab_stats.stats(mon, level=5)
    if (mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed,
            mon.sp_attack, mon.sp_defense) != expected_before or mon.hp != mon.max_hp:
        raise SpeciesError("baseline cached stats/full HP mismatch")

    desired = _target(mon)
    section = before.slots[before.active_slot].section(1)
    record_base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    old_stats = raw[record_base + 86:record_base + 100]
    new_stats = struct.pack("<7H", desired.hp, desired.max_hp, desired.attack,
                            desired.defense, desired.speed, desired.sp_attack,
                            desired.sp_defense)
    patches = [
        tx.RecordPatch(32, struct.pack("<H", mon.species), struct.pack("<H", desired.species)),
        tx.RecordPatch(36, struct.pack("<I", mon.experience), struct.pack("<I", desired.experience)),
    ]
    if old_stats != new_stats:
        patches.append(tx.RecordPatch(86, old_stats, new_stats))

    def validate_before(start: v.VerificationResult) -> None:
        if start.party[0] != mon:
            raise tx.TransactionError("baseline party changed during derivation")

    def validate_after(start: v.VerificationResult, finish: v.VerificationResult) -> None:
        target = _target(start.party[0])
        if finish.party[0] != target:
            raise tx.TransactionError("species/EXP/stat invariant failed")
        if level_from_medium_slow_exp(finish.party[0].experience) != finish.party[0].level:
            raise tx.TransactionError("stored level disagrees with growth-table level")

    output, fp = tx.derive(raw, _profile(raw, before), patches,
                           validate_before, validate_after)
    return output, fp, {
        "species": {"from": 1, "to": 2},
        "target": "Ivysaur",
        "growth_rate": "Medium Slow; shared Bulbasaur/Ivysaur source class",
        "experience": {"from": mon.experience, "to": desired.experience,
                       "threshold_formula": "(6*n^3)//5 - 15*n^2 + 100*n - 140",
                       "level5_threshold": medium_slow_exp(5)},
        "level": {"from": mon.level, "to": desired.level},
        "ability_selector": {"from": mon.ability_num, "to": desired.ability_num,
                             "policy": "preserved selector 0; no ability-table mutation"},
        "preserved": ["personality", "backup species", "IVs", "EVs", "nature/mint",
                      "held item", "friendship", "ball", "moves", "PP", "PP bonuses"],
        "stats": {"from": [mon.hp, mon.max_hp, mon.attack, mon.defense,
                            mon.speed, mon.sp_attack, mon.sp_defense],
                  "to": [desired.hp, desired.max_hp, desired.attack, desired.defense,
                         desired.speed, desired.sp_attack, desired.sp_defense]},
        "hp_policy": "baseline current HP was full; apply repository max-HP delta policy",
    }


def write_new(source: Path, output: Path, rom: Path) -> dict[str, object]:
    source, rom = source.resolve(strict=True), rom.resolve(strict=True)
    output = output.resolve(strict=False)
    if not source.is_relative_to(PRIVATE_ROOT) or not rom.is_relative_to(PRIVATE_ROOT):
        raise SpeciesError("source and ROM must be inside PokemonStart-private")
    if not output.is_relative_to(PRIVATE_ROOT) or output.exists() or output == source:
        raise SpeciesError("output must be a new path inside PokemonStart-private")
    if sha(rom.read_bytes()) != ROM_SHA256:
        raise SpeciesError("ROM is not the exact verified v0.22 build")
    original = source.read_bytes()
    candidate, fp, semantics = derive(original)
    if sha(source.read_bytes()) != INPUT_SHA256:
        raise SpeciesError("input changed before output creation")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
        handle.flush()
        os.fsync(handle.fileno())
    if output.read_bytes() != candidate or sha(source.read_bytes()) != INPUT_SHA256:
        raise SpeciesError("output persistence mismatch or source changed")
    return {"status": "FAST LAB EXPERIMENTAL V0.22 SPECIES TRANSFORMATION",
            "input_sha256": fp.input_sha256, "output_sha256": fp.output_sha256,
            "rom_sha256": ROM_SHA256, "active_slot": fp.active_slot,
            "active_counter": fp.active_counter,
            "section1_physical_sector": fp.section1_sector,
            "section1_checksum": {"from": fp.checksum_before, "to": fp.checksum_after},
            "semantics": semantics,
            "diffs": [{"offset": i, "from": a, "to": b} for i, a, b in fp.diffs],
            "source_immutable": True, "output_path": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_save", type=Path)
    parser.add_argument("output_save", type=Path)
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(write_new(args.source_save, args.output_save, args.rom), indent=2))
    except (OSError, SpeciesError, v.VerificationError, tx.TransactionError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
