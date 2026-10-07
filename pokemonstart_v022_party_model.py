"""Exact-v0.22 read-only Party semantics. No writer or creation authority.

Tables are extracted in memory from the owner's SHA-gated ROM. Special forms,
battle modes and held-item stat modifiers are explicitly outside the ordinary
calculator. Qualification is distinct from permission to write.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import struct

import pokemonstart_save_verifier as verifier
from pokemonstart_v022_inventory_model import decode_name, extract_catalog

ROM_SHA256 = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'
SPECIES_TABLE = 0x19B8B40
SPECIES_NAMES = 0x16570A4
SPECIES_COUNT = 1489
MOVE_TABLE = 0x14A3238
MOVE_NAMES = 0x111A74C
MOVE_COUNT = 998
EXP_TABLE = 0x14C5D54
NATURE_TABLE = 0x20F550
# Exact GetMonAbility's held-item/form override, not national dex numbers.
ABILITY_EXCEPTIONS = frozenset((496, 497, 498, 913, 1460))
SHEDINJA = 303
STAT_DOUBLING_ITEM = 835
# Native evidence covers these ordinary species. Other table entries remain
# inspectable, but do not acquire practical qualification by analogy.
NATIVE_SPECIES = frozenset((1, 19, 25, 288))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Species:
    species_id: int
    name: str | None
    bases: tuple[int, ...]
    growth: int
    abilities: tuple[int, int, int]


@dataclass(frozen=True)
class Move:
    move_id: int
    name: str | None
    base_pp: int


@dataclass(frozen=True)
class Tables:
    species: tuple[Species, ...]
    moves: tuple[Move, ...]
    experience: tuple[tuple[int, ...], ...]
    nature_modifiers: tuple[tuple[int, ...], ...]
    items: dict
    hashes: dict
    held_effects: dict = field(default_factory=dict)


def _name(encoded: bytes) -> str | None:
    try:
        return decode_name(encoded)
    except ValueError:
        return None


def extract_tables(rom: bytes) -> Tables:
    if len(rom) != 0x2000000 or sha(rom) != ROM_SHA256:
        raise ValueError('unsupported exact ROM identity')
    if struct.unpack_from('<I', rom, 0x1BC)[0] != 0x08000000 + SPECIES_TABLE:
        raise ValueError('exact species pointer mismatch')
    species = []
    for sid in range(SPECIES_COUNT):
        record = rom[SPECIES_TABLE + sid * 32:SPECIES_TABLE + (sid + 1) * 32]
        species.append(Species(sid, _name(rom[SPECIES_NAMES + sid*8:SPECIES_NAMES + (sid+1)*8]),
                               tuple(record[:6]), record[19],
                               (int.from_bytes(record[22:24], 'little'),
                                int.from_bytes(record[26:28], 'little'),
                                int.from_bytes(record[28:30], 'little'))))
    moves = tuple(Move(mid, _name(rom[MOVE_NAMES + mid*16:MOVE_NAMES + (mid+1)*16]),
                       rom[MOVE_TABLE + mid*12 + 4]) for mid in range(MOVE_COUNT))
    growth_count = max(s.growth for s in species) + 1
    if growth_count > 8:
        raise ValueError('unqualified growth-rate index')
    experience = tuple(struct.unpack_from('<101I', rom, EXP_TABLE + growth*1024)
                       for growth in range(growth_count))
    for thresholds in experience:
        if thresholds[1] != 1 or any(a >= b for a, b in zip(thresholds[1:], thresholds[2:])):
            raise ValueError('invalid exact EXP thresholds')
    modifiers = tuple(tuple(struct.unpack_from('<5b', rom, NATURE_TABLE + nature*5))
                      for nature in range(25))
    if any(x not in (-1, 0, 1) for row in modifiers for x in row):
        raise ValueError('invalid nature modifiers')
    items, _ = extract_catalog(rom)
    regions = {'species': (SPECIES_TABLE, SPECIES_COUNT*32),
               'species_names': (SPECIES_NAMES, SPECIES_COUNT*8),
               'moves': (MOVE_TABLE, MOVE_COUNT*12), 'move_names': (MOVE_NAMES, MOVE_COUNT*16),
               'experience': (EXP_TABLE, growth_count*1024), 'nature': (NATURE_TABLE, 125)}
    return Tables(tuple(species), moves, experience, modifiers, items,
                  {name: sha(rom[start:start+size]) for name, (start, size) in regions.items()},
                  {item_id: tuple(rom[0x15199C8 + item_id*40 + 14:0x15199C8 + item_id*40 + 16])
                   for item_id in items})


def level_from_exp(experience: int, growth: int, tables: Tables) -> int | None:
    thresholds = tables.experience[growth]
    if not thresholds[1] <= experience <= thresholds[100]:
        return None
    return max(level for level in range(1, 101) if thresholds[level] <= experience)


def maximum_pp(move: int, ups: int, tables: Tables) -> int | None:
    if not 0 <= move < len(tables.moves) or not 0 <= ups <= 3:
        return None
    if move == 0:
        return 0
    base = tables.moves[move].base_pp
    # Exact CalculatePPWithBonus skips bonuses for move 996.
    return base if move == 996 else (base + base * ups // 5) & 255


def cached_stats(species: Species, level: int, ivs: tuple, evs: tuple,
                 nature: int, tables: Tables, *, additive: str = 'five') -> tuple[int, ...]:
    if (not 1 <= level <= 100 or len(ivs) != 6 or len(evs) != 6 or not 0 <= nature < 25
            or any(not 0 <= x <= 31 for x in ivs) or any(not 0 <= x <= 252 for x in evs)
            or sum(evs) > 510 or additive not in ('five', 'level')):
        raise ValueError('ordinary stat inputs unsupported')
    hp = (2*species.bases[0] + ivs[0] + evs[0]//4)*level//100 + level + 10
    stats = []
    for i in range(1, 6):
        value = (2*species.bases[i] + ivs[i] + evs[i]//4)*level//100
        value += 5 if additive == 'five' else level
        stats.append(value*(10 + tables.nature_modifiers[nature][i-1])//10)
    return hp, *stats


def decode_record(record: bytes, slot: int, tables: Tables) -> dict:
    if len(record) != 100:
        raise ValueError('Party record must be 100 bytes')
    mon = verifier._decode_party_record(record, slot)
    hidden = bool(record[71] & 0x10)  # Exact GetMonAbility shift #27 tests bit4.
    egg = bool(record[75] & 0x40)
    nature = mon.personality % 25
    effective = mon.nature_mint - 1 if 1 <= mon.nature_mint <= 25 else nature if mon.nature_mint == 0 else None
    species = tables.species[mon.species] if 0 < mon.species < len(tables.species) else None
    derived_level = level_from_exp(mon.experience, species.growth, tables) if species else None
    reasons = []
    if mon.sanity != 2 or mon.backup_species != 0 or egg:
        reasons.append('not an ordinary non-egg/non-form record')
    if not species or not all(species.bases):
        reasons.append('species metadata unresolved')
    if not 1 <= mon.level <= 100 or not 0 <= mon.hp <= mon.max_hp or mon.max_hp == 0:
        reasons.append('stored level/current HP invalid')
    if effective is None:
        reasons.append('nature mint outside 0..25')
    if mon.hyper_training:
        reasons.append('hyper-training requires separate qualification')
    if any(x > 252 for x in mon.evs) or sum(mon.evs) > 510:
        reasons.append('EV allocation outside practical limits')
    if mon.species not in NATIVE_SPECIES:
        reasons.append('species lacks retained ordinary native corroboration')
    expected = legacy = None
    # Explicitly refuse contextual/special reconstruction instead of guessing.
    stat_reasons = list(reasons)
    if mon.held_item == STAT_DOUBLING_ITEM:
        stat_reasons.append('held item 835 modifies cached non-HP stats')
    if mon.species == SHEDINJA or mon.species in ABILITY_EXCEPTIONS:
        stat_reasons.append('exceptional species/stat/form path')
    if species and effective is not None and 1 <= mon.level <= 100 and not mon.hyper_training and all(x <= 252 for x in mon.evs) and sum(mon.evs) <= 510:
        if mon.held_item != STAT_DOUBLING_ITEM and mon.species != SHEDINJA and mon.species not in ABILITY_EXCEPTIONS:
            expected = cached_stats(species, mon.level, mon.ivs, mon.evs, effective, tables)
            legacy = cached_stats(species, mon.level, mon.ivs, mon.evs, effective, tables, additive='level')
    actual = (mon.max_hp, mon.attack, mon.defense, mon.speed, mon.sp_attack, mon.sp_defense)
    if derived_level != mon.level:
        stat_reasons.append('EXP-derived and stored level disagree')
    if expected != actual:
        stat_reasons.append('cached stats differ from ordinary +5 reconstruction')
    move_rows = []
    move_reasons = list(reasons)
    for index, (mid, pp) in enumerate(zip(mon.moves, mon.pp)):
        ups = (mon.pp_bonuses >> (2*index)) & 3
        limit = maximum_pp(mid, ups, tables)
        issues = []
        if limit is None or mid and tables.moves[mid].base_pp == 0:
            issues.append('move/base PP unresolved')
        elif pp > limit:
            issues.append('PP exceeds exact maximum' if mid else 'empty slot retains nonzero PP')
        if mid == 0 and ups:
            issues.append('empty slot retains PP-Ups')
        move_reasons.extend(f'move {index+1}: {x}' for x in issues)
        move_rows.append({'move_id': mid, 'name': tables.moves[mid].name if limit is not None else None,
                          'pp': pp, 'pp_up_count': ups, 'maximum_pp': limit, 'issues': issues})
    ability = None
    ability_reasons = list(reasons)
    if species and mon.species not in ABILITY_EXCEPTIONS:
        a1, a2, ha = species.abilities
        ability = ha if hidden and ha else a2 if mon.ability_num and a2 else a1
        if ability == 0:
            ability_reasons.append('resolved ability is NONE')
    else:
        ability_reasons.append('held-item/form ability override unresolved')
    held = tables.items.get(mon.held_item)
    held_reasons = list(reasons)
    if mon.held_item and held is None:
        held_reasons.append('held-item metadata unresolved')
    # Metadata validity is not permission to grant or change that item.
    def capability(issues):
        return {'model_qualified': not issues, 'writer_authorized': False, 'reasons': issues}
    return {'slot': slot, 'record_sha256': sha(record), 'species': mon.species,
            'species_name': species.name if species else None, 'stored_level': mon.level,
            'experience': mon.experience, 'growth_rate': species.growth if species else None,
            'exp_derived_level': derived_level, 'moves': move_rows,
            'friendship': mon.friendship, 'ivs': list(mon.ivs), 'evs': list(mon.evs),
            'native_nature': nature, 'effective_nature': effective, 'nature_mint': mon.nature_mint,
            'hyper_training': mon.hyper_training, 'ability_selector': mon.ability_num,
            'hidden_ability': hidden, 'resolved_ability': ability,
            'held_item': mon.held_item, 'held_item_name': held.name if held else None,
            'held_item_metadata': ({'pocket': held.pocket, 'importance': held.importance,
                                    'item_type': held.item_type,
                                    'hold_effect': tables.held_effects.get(mon.held_item, (None, None))[0],
                                    'hold_effect_parameter': tables.held_effects.get(mon.held_item, (None, None))[1]}
                                   if held else None),
            'cached_hp_stats': [mon.hp, *actual],
            'ordinary_expected_stats': list(expected) if expected else None,
            'legacy_expected_stats': list(legacy) if legacy else None,
            'five_matches': expected == actual, 'level_matches': legacy == actual,
            'is_egg': egg, 'backup_species': mon.backup_species, 'reasons': reasons,
            'capabilities': {'friendship': capability(reasons), 'species': capability(stat_reasons),
                             'level_exp': capability(stat_reasons), 'ivs': capability(stat_reasons),
                             'evs': capability(stat_reasons), 'effective_nature': capability(stat_reasons),
                             'cached_stats': capability(stat_reasons), 'moves_pp_pp_up': capability(move_reasons),
                             'ability': capability(ability_reasons), 'held_item': capability(held_reasons)},
            'limits': ['ordinary non-facility stat hypothesis; live battle modes not inferred',
                       'held-item metadata does not establish safe grant authority',
                       'mint/selector/PP-Up edits lack natural transition acceptance']}


def inspect(raw: bytes, rom: bytes) -> dict:
    tables = extract_tables(rom)
    verified = verifier.verify_bytes(raw)
    base = verified.slots[verified.active_slot].section(1).physical_sector*4096 + verifier.PARTY_OFFSET
    return {'rom_sha256': sha(rom), 'save_sha256': sha(raw), 'active_slot': verified.active_slot,
            'counter': verified.slots[verified.active_slot].counter, 'tables': tables.hashes,
            'writer_authorized': False,
            'party': [decode_record(raw[base+i*100:base+(i+1)*100], i, tables)
                      for i in range(verified.party_count)]}
