#!/usr/bin/env python3
"""Sealed M3C Bulbasaur nature-mint / HP-EV / Attack-IV canary group.

Only the exact retained v0.15 post-low-coupling lineage input is writable.
The three changes are one derived-stat family: cached party stats and HP are
recomputed with the field changes rather than edited independently.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import replace
from pathlib import Path

import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx


PRIVATE_PROFILE = tx.Profile(
    input_sha256="baf0b88fd357c54e17743601bbfa26b436db467a2fd78cd1d2c598fb714c50fa",
    active_slot=1,
    active_counter=5,
    inactive_counter=4,
    section1_sector=20,
    party_count=1,
    record0_sha256="a9eabd308b5cfb11e8a09db88e139a30fa3391db7fc0b6b78f2f30560bcb5840",
    sector30_sha256="335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525",
    sector31_sha256="ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7",
    footer_sha256="f1f4a7b20f12225b63887afa855735504f25db397acedb1c2aab6e000b0833e4",
)

CAPABILITIES = {
    "nature_mint": (0, 4),       # 0 = original Modest; 4 = Adamant + 1.
    "hp_ev": (0, 80),           # bounded to an ordinary 0..252 EV value.
    "attack_iv": (29, 0),       # in 5-bit Attack-IV field.
}
ALLOWED_GROUPS = {
    ("nature_mint",),
    ("hp_ev",),
    ("attack_iv",),
    ("attack_iv", "hp_ev", "nature_mint"),
}

SEALS: dict[tuple[str, ...], dict[str, object]] = {
    ("nature_mint",): {
        "output_sha256": "b9d9096fd990ad80c48bbe9c83b3291adc32aea55cd4e2ed8de9a431bfdd0845",
        "diffs": ((81991, 0, 4), (82066, 9, 12), (82072, 13, 10), (86007, 31, 35)),
    },
    ("hp_ev",): {
        "output_sha256": "73dc915f119ab433185d4232d4b52b429d350aa8563a1813992234365265c2ce",
        "diffs": ((82032, 0, 80), (82062, 21, 22), (82064, 21, 22), (86006, 23, 105)),
    },
    ("attack_iv",): {
        "output_sha256": "a661223e95b6fa0236bedf64d04c29ee8ad90302e53f24552529be756dac4b73",
        "diffs": ((82048, 191, 31), (82049, 235, 232), (82066, 9, 8),
                  (86006, 23, 118), (86007, 31, 27)),
    },
    ("attack_iv", "hp_ev", "nature_mint"): {
        "output_sha256": "aaac81a2ef0ade68e87eef4a64809434c3519c278b3ecb14a760ff9dadb1bab0",
        "diffs": ((81991, 0, 4), (82032, 0, 80), (82048, 191, 31),
                  (82049, 235, 232), (82062, 21, 22), (82064, 21, 22),
                  (82072, 13, 10), (86006, 23, 198)),
    },
}


def _group(fields) -> tuple[str, ...]:
    requested = tuple(fields)
    if len(requested) != len(set(requested)):
        raise tx.TransactionError("duplicate derived-stat field")
    names = tuple(sorted(requested))
    if names not in ALLOWED_GROUPS:
        raise tx.TransactionError(f"unsupported derived-stat field group: {names!r}")
    return names


def _stats(mon: v.PartyRecord, nature: int) -> tuple[int, int, int, int, int, int, int]:
    """CFRU-JP CalculateMonStatsNew ordinary Bulbasaur profile, level 5.

    Return HP, max HP, Attack, Defense, Speed, Sp. Attack, Sp. Defense.
    This proof handles ordinary saved party stats outside battle. Only
    source-backed Modest and Adamant are accepted.
    """
    if mon.species != 1 or mon.level != 5 or mon.hyper_training != 0:
        raise tx.TransactionError("unsupported derived-stat species/level/hyper-training profile")
    if nature not in (3, 15):
        raise tx.TransactionError("unsupported effective nature")
    if any(iv < 0 or iv > 31 for iv in mon.ivs):
        raise tx.TransactionError("IV out of range")
    if any(ev < 0 or ev > 252 for ev in mon.evs) or sum(mon.evs) > 510:
        raise tx.TransactionError("EV allocation out of range")
    hp_max = ((2 * 45 + mon.ivs[0] + mon.evs[0] // 4) * 5) // 100 + 5 + 10
    bases = (49, 49, 45, 65, 65)
    values = []
    for i, base in enumerate(bases, 1):
        n = ((2 * base + mon.ivs[i] + mon.evs[i] // 4) * 5) // 100 + 5
        if (nature == 3 and i == 1) or (nature == 15 and i == 4):
            n = n * 110 // 100
        elif (nature == 3 and i == 4) or (nature == 15 and i == 1):
            n = n * 90 // 100
        values.append(n)
    if hp_max < mon.max_hp:
        raise tx.TransactionError("HP-decreasing transformation is outside this proof")
    hp = mon.hp + hp_max - mon.max_hp if mon.hp else 0
    if hp > hp_max:
        hp = hp_max
    return (hp, hp_max, *values)


def _baseline(mon: v.PartyRecord) -> None:
    if (
        mon.species, mon.level, mon.experience, mon.nature_mint,
        mon.hyper_training, mon.tera_type, mon.held_item,
        mon.friendship, mon.markings, mon.ball, mon.moves, mon.pp,
        mon.ivs, mon.evs,
    ) != (
        1, 5, 134, 0, 0, 12, 0, 52, 1, 11,
        (33, 45, 0, 0), (35, 40, 0, 0),
        (31, 29, 26, 23, 27, 29), (0, 0, 0, 0, 0, 0),
    ):
        raise tx.TransactionError("derived-stat starting party profile mismatch")
    if mon.personality % 25 != 15:  # Modest in the pinned nature enum.
        raise tx.TransactionError("original nature is not Modest")
    if (mon.hp, mon.max_hp, mon.attack, mon.defense, mon.speed, mon.sp_attack, mon.sp_defense) != _stats(mon, 15):
        raise tx.TransactionError("starting cached stats disagree with pinned formula")


def _expected(before: v.PartyRecord, names: tuple[str, ...]) -> v.PartyRecord:
    nature_mint = 4 if "nature_mint" in names else before.nature_mint
    evs = (80, *before.evs[1:]) if "hp_ev" in names else before.evs
    ivs = (before.ivs[0], 0, *before.ivs[2:]) if "attack_iv" in names else before.ivs
    interim = replace(before, nature_mint=nature_mint, evs=evs, ivs=ivs)
    nature = nature_mint - 1 if nature_mint else before.personality % 25
    hp, max_hp, atk, defense, speed, spa, spd = _stats(interim, nature)
    return replace(interim, hp=hp, max_hp=max_hp, attack=atk, defense=defense,
                   speed=speed, sp_attack=spa, sp_defense=spd)


def derive_candidate(raw: bytes, fields, profile: tx.Profile = PRIVATE_PROFILE):
    names = _group(fields)
    before = v.verify_bytes(raw)
    # The transaction module enforces the exact lineage profile and record hash.
    # This early check also guards the semantic calculation below.
    if before.file_sha256 != profile.input_sha256 or before.party_count != 1:
        raise tx.TransactionError("derived-stat input profile mismatch")
    mon = before.party[0]
    _baseline(mon)
    desired = _expected(mon, names)
    record_base = before.slots[before.active_slot].section(1).physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    patches = []
    if "nature_mint" in names:
        patches.append(tx.RecordPatch(15, bytes((0,)), bytes((4,))))
    if "hp_ev" in names:
        patches.append(tx.RecordPatch(56, bytes((0,)), bytes((80,))))
    if "attack_iv" in names:
        old_word = struct.unpack_from("<I", raw, record_base + 72)[0]
        new_word = old_word & ~(0x1F << 5)
        patches.append(tx.RecordPatch(72, struct.pack("<I", old_word), struct.pack("<I", new_word)))
    old_stats = raw[record_base + 86:record_base + 100]
    new_stats = struct.pack("<7H", desired.hp, desired.max_hp, desired.attack,
                            desired.defense, desired.speed, desired.sp_attack, desired.sp_defense)
    if old_stats != new_stats:
        patches.append(tx.RecordPatch(86, old_stats, new_stats))

    def validate_after(start: v.VerificationResult, finish: v.VerificationResult) -> None:
        if finish.party[0] != _expected(start.party[0], names):
            raise tx.TransactionError("derived-stat party invariant failed")

    output, fp = tx.derive(raw, profile, patches, lambda start: _baseline(start.party[0]), validate_after)
    return output, fp


def build_output(raw: bytes, fields, profile: tx.Profile = PRIVATE_PROFILE):
    names = _group(fields)
    output, fp = derive_candidate(raw, names, profile)
    seal = SEALS.get(names)
    if seal is None or fp.output_sha256 != seal["output_sha256"] or fp.diffs != seal["diffs"]:
        raise tx.TransactionError("derived-stat candidate does not match exact private seal")
    return output, fp


def write_output(input_path: str | Path, output_path: str | Path, fields):
    names = _group(fields)
    return tx.write_new(input_path, output_path, lambda raw: build_output(raw, names))


def manifest(fp: tx.Fingerprint, fields) -> str:
    names = _group(fields)
    return json.dumps({
        "status": "CANARY_READY",
        "fields": list(names),
        "semantic_edits": {name: {"from": CAPABILITIES[name][0], "to": CAPABILITIES[name][1]} for name in names},
        "input_sha256": fp.input_sha256,
        "output_sha256": fp.output_sha256,
        "active_slot": fp.active_slot,
        "active_counter": fp.active_counter,
        "section1_physical_sector": fp.section1_sector,
        "section1_checksum": {"from": fp.checksum_before, "to": fp.checksum_after},
        "diffs": [{"offset": i, "from": a, "to": b} for i, a, b in fp.diffs],
        "preserved": ["inactive_slot", "slot_counters", "section_ids_signatures_permutation",
                      "sectors_28_31", "checksum_excluded_tails", "opaque_footer", "unrelated_bytes"],
    }, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exact v0.15 M3C derived-stat canary writer")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--fields", required=True, help="comma-separated sealed capability names")
    args = parser.parse_args(argv)
    try:
        fields = tuple(x.strip() for x in args.fields.split(",") if x.strip())
        fp = write_output(args.input, args.output, fields)
    except (OSError, v.VerificationError, tx.TransactionError) as exc:
        print("status: REJECTED")
        print(f"reason: {exc}")
        return 2
    print(manifest(fp, fields), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
