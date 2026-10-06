#!/usr/bin/env python3
"""Bounded reusable experimental party editor for the exact Fast Lab v0.22 ROM."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from typing import Any, Mapping

import pokemonstart_fastlab_v022_stats as fastlab_stats
import pokemonstart_save_verifier as v
from pokemonstart_fastlab_v022_level import level_from_medium_slow_exp, medium_slow_exp

REPO = Path(__file__).resolve().parent
PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
CAPABILITY_PROFILE = REPO / "docs/fast-lab-v022-capability.json"
EXPECTED_ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
SUPPORTED_INPUT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
ROM_ARGUMENT_DEFAULT = PRIVATE_ROOT / "PokemonStart_v0.22_PRIVATE.gba"
SUPPORTED_SPECIES = {1: "Bulbasaur", 2: "Ivysaur"}
SUPPORTED_MOVE_BASE_PP = {1: 35}  # Pound; only the observed slot-0 target is writable.
WRITABLE_FIELDS = {
    "species", "level", "experience", "moves", "friendship", "ivs", "evs",
}
STAT_FIELDS = {"species", "level", "experience", "ivs", "evs"}


class EditorError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _rom_profile_hash() -> str:
    try:
        profile = json.loads(CAPABILITY_PROFILE.read_text(encoding="utf-8"))
        value = profile["profile_key"]["patched_rom_sha256"]
        schema = profile["profile_schema"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise EditorError("v0.22 capability profile is unreadable") from exc
    if schema != 1 or value != EXPECTED_ROM_SHA256:
        raise EditorError("v0.22 capability profile does not match this exact build")
    return value


def _private_path(path: str | Path, label: str, *, must_exist: bool) -> Path:
    resolved = Path(path).resolve(strict=must_exist)
    if not resolved.is_relative_to(PRIVATE_ROOT):
        raise EditorError(f"{label} must be inside PokemonStart-private")
    if must_exist and not resolved.is_file():
        raise EditorError(f"{label} is not a regular file")
    return resolved


def _check_rom(rom_path: str | Path) -> str:
    rom = _private_path(rom_path, "ROM", must_exist=True)
    expected = _rom_profile_hash()
    actual = sha(rom.read_bytes())
    if actual != expected:
        raise EditorError("ROM hash does not match the exact v0.22 capability profile")
    return actual


def _effective_nature(mon: v.PartyRecord) -> int:
    return mon.nature_mint - 1 if mon.nature_mint else mon.personality % 25


def _pp_up_count(pp_bonuses: int, slot: int) -> int:
    return (pp_bonuses >> (2 * slot)) & 3


def _maximum_pp(move_id: int, pp_bonuses: int, slot: int) -> int:
    if move_id != 1 or slot != 0 or pp_bonuses != 0:
        raise EditorError("PP calculation is bounded to slot 0 Pound with zero PP-Up bonuses")
    try:
        base = SUPPORTED_MOVE_BASE_PP[move_id]
    except KeyError as exc:
        raise EditorError(f"move {move_id} is outside the source-backed move table") from exc
    return base + base * _pp_up_count(pp_bonuses, slot) // 5


def _semantic(mon: v.PartyRecord) -> dict[str, Any]:
    return {
        "species": mon.species,
        "level": mon.level,
        "experience": mon.experience,
        "moves": list(mon.moves),
        "pp": list(mon.pp),
        "pp_bonuses": mon.pp_bonuses,
        "friendship": mon.friendship,
        "ball": mon.ball,
        "markings": mon.markings,
        "nature": mon.personality % 25,
        "nature_mint": mon.nature_mint,
        "effective_nature": _effective_nature(mon),
        "ivs": list(mon.ivs),
        "evs": list(mon.evs),
        "cached_stats": [mon.hp, mon.max_hp, mon.attack, mon.defense,
                         mon.speed, mon.sp_attack, mon.sp_defense],
        "ability_selector": mon.ability_num,
        "held_item": mon.held_item,
    }


def inspect_bytes(raw: bytes) -> dict[str, Any]:
    result = v.verify_bytes(raw)
    if not result.party:
        raise EditorError("save has no decodable party member")
    return {
        "status": "FAST LAB v0.22 read-only inspect",
        "save_sha256": result.file_sha256,
        "active_slot": result.active_slot,
        "active_counter": result.slots[result.active_slot].counter,
        "party_count": result.party_count,
        "party": [_semantic(mon) for mon in result.party],
        "evidence": ["exact-save offline"],
    }


def inspect(input_save: str | Path, rom_path: str | Path = ROM_ARGUMENT_DEFAULT) -> dict[str, Any]:
    _check_rom(rom_path)
    source = _private_path(input_save, "input save", must_exist=True)
    return inspect_bytes(source.read_bytes())


def _validate_changes(changes: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(changes, Mapping):
        raise EditorError("changes must be a JSON object / mapping")
    unknown = set(changes) - WRITABLE_FIELDS
    if unknown:
        if "ability_selector" in unknown:
            raise EditorError("ability_selector is read-only; v0.22 ability writes are unproven")
        raise EditorError(f"unsupported writable field(s): {', '.join(sorted(unknown))}")
    normalized = dict(changes)
    if "species" in normalized:
        value = normalized["species"]
        if not _is_int(value) or value not in SUPPORTED_SPECIES:
            raise EditorError("species write is bounded to Bulbasaur (1) and Ivysaur (2)")
    if "level" in normalized:
        value = normalized["level"]
        if not _is_int(value) or value != 6:
            raise EditorError("target level is bounded to the live-confirmed 5->6 transition")
    if "experience" in normalized:
        value = normalized["experience"]
        if not _is_int(value) or value != 179:
            raise EditorError("explicit EXP write is bounded to the live-confirmed 134->179 transition")
    for field, maximum in (("friendship", 53),):
        if field in normalized:
            value = normalized[field]
            if not _is_int(value) or not 0 <= value <= maximum:
                raise EditorError(f"{field} must be an integer in 0..{maximum}")
    for field, maximum in (("ivs", 31), ("evs", 8)):
        if field in normalized:
            values = normalized[field]
            if (not isinstance(values, (list, tuple)) or len(values) != 6
                    or any(not _is_int(value) or not 0 <= value <= maximum
                           for value in values)):
                raise EditorError(f"{field} must contain six integers in 0..{maximum}")
            normalized[field] = tuple(values)
    if "evs" in normalized and sum(normalized["evs"]) > 510:
        raise EditorError("EV total must not exceed 510")
    if "friendship" in normalized and normalized["friendship"] not in (51, 53):
        raise EditorError("friendship writes are bounded to live-confirmed 50->51 or composed 50->53")
    if "ivs" in normalized and normalized["ivs"] != (31, 0, 26, 23, 27, 29):
        raise EditorError("IV write is bounded to the live-confirmed Attack IV 29->0 transition")
    if "evs" in normalized and normalized["evs"] != (8, 0, 0, 0, 0, 0):
        raise EditorError("EV write is bounded to the live-confirmed composed HP EV 0->8 transition")
    if "moves" in normalized:
        moves = normalized["moves"]
        if not isinstance(moves, Mapping) or not moves:
            raise EditorError("moves must map one or more slot indices to move IDs")
        normalized_moves = {}
        for raw_slot, move_id in moves.items():
            slot = int(raw_slot) if isinstance(raw_slot, str) and raw_slot.isdecimal() else raw_slot
            if not _is_int(slot) or slot not in range(4):
                raise EditorError("move slot must be an integer in 0..3")
            if slot != 0 or not _is_int(move_id) or move_id != 1:
                raise EditorError("move write is bounded to slot 0 Tackle (33)->Pound (1)")
            normalized_moves[slot] = move_id
        normalized["moves"] = normalized_moves
    if normalized.get("friendship") == 53:
        composed = {
            "species": 2,
            "level": 6,
            "moves": {0: 1},
            "ivs": (31, 0, 26, 23, 27, 29),
            "evs": (8, 0, 0, 0, 0, 0),
            "friendship": 53,
        }
        if normalized != composed:
            raise EditorError("friendship 50->53 is supported only in the exact composed canary")
    if ("level" in normalized and "experience" in normalized
            and normalized["experience"] != medium_slow_exp(normalized["level"])):
        raise EditorError("requested level and EXP thresholds conflict")
    composed = {
        "species": 2,
        "level": 6,
        "moves": {0: 1},
        "ivs": (31, 0, 26, 23, 27, 29),
        "evs": (8, 0, 0, 0, 0, 0),
        "friendship": 53,
    }
    allowed_requests = (
        {}, {"friendship": 51}, {"level": 6}, {"experience": 179},
        {"level": 6, "experience": 179}, {"species": 2},
        {"moves": {0: 1}}, {"ivs": (31, 0, 26, 23, 27, 29)}, composed,
    )
    if normalized not in allowed_requests:
        raise EditorError("requested field combination is outside the FL1 live-confirmed transitions")
    return normalized


def _profile(result: v.VerificationResult) -> dict[str, Any]:
    active = result.slots[result.active_slot]
    return {
        "active_slot": result.active_slot,
        "counters": tuple(slot.counter for slot in result.slots),
        "sections": tuple((s.section_id, s.physical_sector, s.counter, s.signature)
                           for s in active.sections),
    }


def derive_bytes(raw: bytes, changes: Mapping[str, Any]) -> tuple[bytes, dict[str, Any]]:
    if sha(raw) != SUPPORTED_INPUT_SHA256:
        raise EditorError("writes are bounded to the exact retained v0.22 canary save")
    requested = _validate_changes(changes)
    before = v.verify_bytes(raw)
    if before.party_count != 1:
        raise EditorError("write is bounded to saves with exactly one party Pokémon")
    mon = before.party[0]
    if mon.species != 1 or mon.level != 5:
        raise EditorError("writes require the exact retained Bulbasaur level-5 canary profile")
    if (mon.hyper_training != 0 or mon.nature_mint != 0
            or mon.personality % 25 != 15):
        raise EditorError("only the live-confirmed unminted Modest stat profile is supported")
    if "ability_selector" in changes:
        raise EditorError("ability_selector is read-only; v0.22 ability writes are unproven")
    if any(name in requested for name in ("species", "level", "experience")) and mon.ability_num != 0:
        raise EditorError("species/level writes require the corroborated ability selector 0")

    target_species = requested.get("species", mon.species)
    target_level = requested.get("level", mon.level)
    target_exp = mon.experience
    if "level" in requested:
        # The currently supported species share the verified Medium Slow curve.
        target_exp = medium_slow_exp(target_level)
    elif "experience" in requested:
        target_exp = requested["experience"]
        target_level = level_from_medium_slow_exp(target_exp)
    elif (target_species != mon.species
          and level_from_medium_slow_exp(target_exp) != target_level):
        # A species transformation must be growth-coherent, but unrelated edits
        # never normalize the observed EXP/level discrepancy.
        target_exp = medium_slow_exp(target_level)

    target_ivs = requested.get("ivs", mon.ivs)
    target_evs = requested.get("evs", mon.evs)
    desired = mon
    stat_changed = any(name in requested for name in STAT_FIELDS)
    if stat_changed:
        desired = replace(
            mon, species=target_species, level=target_level, experience=target_exp,
            ivs=target_ivs, evs=target_evs)
        stats = fastlab_stats.stats(desired, level=target_level)
        desired = replace(
            desired, hp=stats[0], max_hp=stats[1], attack=stats[2],
            defense=stats[3], speed=stats[4], sp_attack=stats[5], sp_defense=stats[6])

    slot1 = before.slots[before.active_slot].section(1)
    sector_base = slot1.physical_sector * v.SECTOR_SIZE
    record_base = sector_base + v.PARTY_OFFSET
    old_record = raw[record_base:record_base + v.POKEMON_SIZE]
    edits: dict[int, bytes] = {}

    def add(offset: int, value: bytes) -> None:
        if old_record[offset:offset + len(value)] != value:
            edits[offset] = value

    if target_species != mon.species:
        add(32, struct.pack("<H", target_species))
    if target_exp != mon.experience:
        add(36, struct.pack("<I", target_exp))
    if target_level != mon.level:
        add(84, bytes((target_level,)))
    for field, offset in (("friendship", 41),):
        if field in requested:
            add(offset, bytes((requested[field],)))
    if "ivs" in requested:
        old_word = struct.unpack_from("<I", old_record, 72)[0]
        new_word = old_word & ~0x3FFFFFFF
        for i, value in enumerate(target_ivs):
            new_word |= value << (5 * i)
        add(72, struct.pack("<I", new_word))
    if "evs" in requested:
        add(56, bytes(target_evs))
    if "moves" in requested:
        bonuses = old_record[40]
        for move_slot, move_id in requested["moves"].items():
            add(44 + 2 * move_slot, struct.pack("<H", move_id))
            add(52 + move_slot, bytes((_maximum_pp(move_id, bonuses, move_slot),)))
    if stat_changed:
        add(86, struct.pack("<7H", desired.hp, desired.max_hp, desired.attack,
                            desired.defense, desired.speed, desired.sp_attack,
                            desired.sp_defense))

    output = bytearray(raw)
    allowed = set()
    for offset, value in edits.items():
        output[record_base + offset:record_base + offset + len(value)] = value
        allowed.update(range(record_base + offset, record_base + offset + len(value)))
    checksum_offset = sector_base + v.SECTION_CHECKSUM_OFFSET
    old_checksum = slot1.checksum_stored
    new_checksum = old_checksum
    if edits:
        new_checksum = v.calculate_save_checksum(
            bytes(output[sector_base:sector_base + v.SECTION_LENGTHS[1]]))
        struct.pack_into("<H", output, checksum_offset, new_checksum)
        allowed.update((checksum_offset, checksum_offset + 1))
    candidate = bytes(output)
    after = v.verify_bytes(candidate)
    if _profile(after) != _profile(before) or after.party_count != before.party_count:
        raise EditorError("edit changed save-slot or section metadata")
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(raw, candidate)) if a != b]
    if any(i not in allowed for i, _, _ in diffs):
        raise EditorError("edit changed bytes outside party[0] and its active checksum")
    if edits and not any(i in (checksum_offset, checksum_offset + 1)
                         for i, _, _ in diffs) and new_checksum != old_checksum:
        raise EditorError("section checksum update escaped diff report")
    if after.party[0].ability_num != mon.ability_num:
        raise EditorError("ability selector changed unexpectedly")
    if stat_changed:
        for field in ("hp", "max_hp", "attack", "defense", "speed", "sp_attack", "sp_defense"):
            if getattr(after.party[0], field) != getattr(desired, field):
                raise EditorError("cached party stats differ from reused M3C model")
    summary = {
        "status": "FAST LAB EXPERIMENTAL V0.22 PARTY EDIT",
        "input_sha256": before.file_sha256,
        "output_sha256": after.file_sha256,
        "active_slot": before.active_slot,
        "active_counter": before.slots[before.active_slot].counter,
        "section1_physical_sector": slot1.physical_sector,
        "section1_checksum": {"from": old_checksum, "to": new_checksum},
        "requested_changes": requested,
        "before": _semantic(mon),
        "after": _semantic(after.party[0]),
        "diffs": [{"offset": i, "from": a, "to": b} for i, a, b in diffs],
        "verifier_accepted": True,
        "unchanged_outside_party0_and_checksum": True,
    }
    return candidate, summary


def write_new_file(output_path: str | Path, data: bytes) -> None:
    """Create a new private artifact without ever replacing an existing file."""
    destination = Path(output_path).resolve(strict=False)
    if destination.exists():
        raise EditorError("refusing to overwrite existing output")
    if not destination.is_relative_to(PRIVATE_ROOT):
        raise EditorError("output must be inside PokemonStart-private")
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise EditorError("refusing to overwrite existing output") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def edit(input_save: str | Path, changes: Mapping[str, Any], output_path: str | Path,
         rom_path: str | Path = ROM_ARGUMENT_DEFAULT) -> dict[str, Any]:
    rom_hash = _check_rom(rom_path)
    source = _private_path(input_save, "input save", must_exist=True)
    destination = _private_path(output_path, "output save", must_exist=False)
    if destination == source or destination.exists():
        raise EditorError("output must be a new path; overwrite is refused")
    original = source.read_bytes()
    candidate, summary = derive_bytes(original, changes)
    write_new_file(destination, candidate)
    try:
        if sha(source.read_bytes()) != summary["input_sha256"]:
            raise EditorError("input changed during output creation")
        if sha(destination.read_bytes()) != summary["output_sha256"]:
            raise EditorError("output persistence verification failed")
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise
    summary.update({"rom_sha256": rom_hash, "source_immutable": True,
                    "output_path": str(destination),
                    "evidence": ["exact-ROM capability profile", "exact-save offline",
                                 "repository verifier", "Fast Lab experimental write"]})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    inspect_parser = sub.add_parser("inspect")
    inspect_parser.add_argument("input_save", type=Path)
    inspect_parser.add_argument("--rom", type=Path, default=ROM_ARGUMENT_DEFAULT)
    edit_parser = sub.add_parser("edit")
    edit_parser.add_argument("input_save", type=Path)
    edit_parser.add_argument("output_save", type=Path)
    edit_parser.add_argument("--changes-json", required=True)
    edit_parser.add_argument("--rom", type=Path, default=ROM_ARGUMENT_DEFAULT)
    args = parser.parse_args()
    try:
        if args.action == "inspect":
            result = inspect(args.input_save, args.rom)
        else:
            changes = json.loads(args.changes_json)
            result = edit(args.input_save, changes, args.output_save, args.rom)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, v.VerificationError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
