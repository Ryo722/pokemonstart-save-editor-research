"""Independent E3 reconstruction; no production Party model/writer imports.

Uses the existing independent section validator and direct byte reads. EXP is
found by a forward threshold walk; nature is reconstructed arithmetically and
cross-checked with ROM modifiers. Only decoded semantics/hashes are returned.
"""
from __future__ import annotations
import hashlib
import struct
import pokemonstart_v022_creation_audit as structure

EXACT = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'


def reconstruct(record: bytes, rom: bytes) -> dict:
    if len(record) != 100:
        raise ValueError('independent record length')
    def u16(offset):
        return int.from_bytes(record[offset:offset+2], 'little')
    species = u16(32)
    metadata = rom[0x19B8B40 + species*32:0x19B8B40 + (species+1)*32] if 0 < species < 1489 else None
    exp = int.from_bytes(record[36:40], 'little')
    level = None
    growth = metadata[19] if metadata else None
    if growth is not None and growth < 8:
        thresholds = [int.from_bytes(rom[0x14C5D54 + growth*1024 + j*4:
                                        0x14C5D54 + growth*1024 + j*4+4], 'little') for j in range(101)]
        if thresholds[1] <= exp <= thresholds[100]:
            level = 1
            while level < 100 and exp >= thresholds[level+1]:
                level += 1
    nature = int.from_bytes(record[:4], 'little') % 25
    effective = record[15]-1 if 1 <= record[15] <= 25 else nature if record[15] == 0 else None
    ivword = int.from_bytes(record[72:76], 'little')
    ivs = [(ivword // (32**j)) % 32 for j in range(6)]
    evs = list(record[56:62])
    actual = list(struct.unpack_from('<7H', record, 86))
    calculations = []
    if (metadata and effective is not None and 1 <= record[84] <= 100 and not record[16]
            and max(evs) <= 252 and sum(evs) <= 510 and u16(34) != 835
            and species not in (303, 496, 497, 498, 913, 1460)):
        # Exact nature order: Attack, Defense, Speed, SpAttack, SpDefense.
        for constant in (5, record[84]):
            values = []
            for j in range(6):
                n = ((metadata[j]*2 + ivs[j] + evs[j]//4)*record[84])//100
                if j == 0:
                    n += record[84]+10
                else:
                    n += constant
                    position = j-1
                    modifier = 0 if effective//5 == effective%5 else 1 if position == effective//5 else -1 if position == effective%5 else 0
                    # Independent arithmetic must agree with the exact table.
                    signed = rom[0x20F550 + effective*5 + j-1]
                    if (signed if signed < 128 else signed-256) != modifier:
                        raise ValueError('independent nature order disagreement')
                    n = n*(10+modifier)//10
                values.append(n)
            calculations.append(values)
    selector = ivword >> 31
    hidden = bool(record[71] & 16)
    ability = None
    if metadata and species not in (496, 497, 498, 913, 1460):
        first = int.from_bytes(metadata[22:24], 'little')
        second = int.from_bytes(metadata[26:28], 'little')
        third = int.from_bytes(metadata[28:30], 'little')
        ability = third if hidden and third else second if selector and second else first
    moves = []
    for j in range(4):
        mid = u16(44+j*2)
        ups = record[40]//(4**j) % 4
        limit = None
        if mid < 998:
            pp = rom[0x14A3238 + mid*12+4]
            limit = 0 if mid == 0 else pp if mid == 996 else (pp + pp*20*ups//100) % 256
        moves.append({'move_id': mid, 'pp': record[52+j], 'pp_up_count': ups, 'maximum_pp': limit})
    # Exact catalog already supplies public-facing names on the production
    # path; independently reconstruct numeric held-item metadata here.
    item = u16(34)
    held = None
    if 0 < item < 839:
        metadata_item = rom[0x15199C8 + item*40:0x15199C8 + (item+1)*40]
        if (int.from_bytes(metadata_item[10:12], 'little') == item
                and metadata_item[22] in range(1, 6) and metadata_item[20] in (0, 1, 2)
                and 255 in metadata_item[:10]):
            held = {'pocket': metadata_item[22], 'importance': metadata_item[20],
                    'item_type': metadata_item[23], 'hold_effect': metadata_item[14],
                    'hold_effect_parameter': metadata_item[15]}
    return {'record_sha256': hashlib.sha256(record).hexdigest(), 'species': species,
            'stored_level': record[84], 'experience': exp, 'growth_rate': growth,
            'exp_derived_level': level, 'moves': moves, 'friendship': record[41],
            'ivs': ivs, 'evs': evs, 'native_nature': nature, 'effective_nature': effective,
            'nature_mint': record[15], 'hyper_training': record[16],
            'ability_selector': selector, 'hidden_ability': hidden, 'resolved_ability': ability,
            'held_item': item, 'held_item_metadata': held, 'cached_hp_stats': actual,
            'ordinary_expected_stats': calculations[0] if calculations else None,
            'legacy_expected_stats': calculations[1] if calculations else None,
            'five_matches': bool(calculations and actual[1:] == calculations[0]),
            'level_matches': bool(calculations and actual[1:] == calculations[1]),
            'is_egg': bool(ivword & (1 << 30)), 'backup_species': u16(28)}


def inspect(raw: bytes, rom: bytes) -> dict:
    if len(rom) != 33554432 or hashlib.sha256(rom).hexdigest() != EXACT:
        raise ValueError('independent exact ROM identity')
    parsed = structure.parse(raw)
    return {'save_sha256': hashlib.sha256(raw).hexdigest(), 'active_slot': parsed['active'],
            'counter': parsed['slots'][parsed['active']]['counter'],
            'party': [reconstruct(record, rom) for record in parsed['records']]}


def compare(production: dict, independent: dict) -> None:
    for key in ('save_sha256', 'active_slot', 'counter'):
        if production[key] != independent[key]:
            raise ValueError('independent save reconstruction disagreement: ' + key)
    if len(production['party']) != len(independent['party']):
        raise ValueError('independent occupancy disagreement')
    for candidate, rebuilt in zip(production['party'], independent['party']):
        for key, value in rebuilt.items():
            actual = candidate[key]
            if key == 'moves':
                actual = [{k: row[k] for k in value[0]} for row in actual]
            if actual != value:
                raise ValueError('independent Party reconstruction disagreement: ' + key)
