"""Read-only exact-v0.22 PC Box decoder. No writer authority.

The exact ROM's 25-entry box pointer table (checked below) places boxes 1-19
in the original storage block, 20-22 in the global extra sectors 30/31,
23-24 in SaveBlock1 and 25 in SaveBlock2. Records are the pinned CFRU-JP
58-byte CompressedPokemon. Extra sectors are not slot-rotated or checksummed.
"""
from __future__ import annotations

import struct

import pokemonstart_save_verifier as verifier
import pokemonstart_v022_party_model as model

BOX_TABLE = 0x1492538
BOX_COUNT = 25
BOX_SLOTS = 30
RECORD_SIZE = 58
STORAGE_RAM = 0x0202924C
SAVEBLOCK1_RAM = 0x0202548C
# Derived from the table's box-25 pointer and a native deposit observed at
# logical section 0 + 0xF8 + 29*58.
SAVEBLOCK2_RAM = 0x020244E8
EXTRA_SECTORS = ((0x0203BFAC, 30), (0x0203CF9C, 31))
EXPECTED_POINTERS = tuple(STORAGE_RAM + 4 + box * BOX_SLOTS * RECORD_SIZE for box in range(19)) + (
    0x0203CABC, 0x0203D188, 0x0203D854, 0x02026D74, 0x02027440, 0x020245E0)
# Boxes with a native deposit observation; others are source/ROM mapped only.
NATIVE_OBSERVED_BOXES = frozenset((0, 24))


def pointers(rom: bytes) -> tuple[int, ...]:
    if model.sha(rom) != model.ROM_SHA256:
        raise ValueError('unsupported exact ROM identity')
    table = struct.unpack_from('<25I', rom, BOX_TABLE)
    if table != EXPECTED_POINTERS:
        raise ValueError('exact box pointer table mismatch')
    return table


def _file_offset(active, ram: int) -> int:
    """Map one RAM byte to its serialized file offset (records may straddle)."""
    for base, first, count in ((STORAGE_RAM, 5, 9), (SAVEBLOCK1_RAM, 1, 4), (SAVEBLOCK2_RAM, 0, 1)):
        relative = ram - base
        if 0 <= relative < count * 0xFF0:
            index, inner = divmod(relative, 0xFF0)
            if inner >= verifier.SECTION_LENGTHS[first + index]:
                break
            return active.section(first + index).physical_sector * 4096 + inner
    for base, sector in EXTRA_SECTORS:
        if 0 <= ram - base < 0xFF0:
            return sector * 4096 + ram - base
    raise ValueError('box record outside serialized regions')


def read_record(raw: bytes, active, ram: int) -> bytes:
    return bytes(raw[_file_offset(active, ram + i)] for i in range(RECORD_SIZE))


def decode(record: bytes, tables) -> dict:
    personality, ot_id = struct.unpack_from('<II', record, 0)
    species, held, experience = struct.unpack_from('<HHI', record, 28)
    packed = int.from_bytes(record[39:44], 'little')
    moves = [(packed >> (10 * i)) & 0x3FF for i in range(4)]
    ivs = struct.unpack_from('<I', record, 54)[0]
    info = tables.species[species] if 0 < species < len(tables.species) else None
    level = model.level_from_exp(experience, info.growth, tables) if info else None
    return {'species': species, 'species_name': info.name if info else None,
            'level_from_exp': level, 'held_item': held, 'experience': experience,
            'pp_bonuses': record[36], 'friendship': record[37], 'ball': record[38],
            'moves': moves, 'evs': list(record[44:50]),
            'ivs': [(ivs >> (5 * i)) & 31 for i in range(6)], 'ability_selector': ivs >> 31,
            'is_egg': bool(ivs >> 30 & 1), 'sanity': record[19],
            'shiny': model.shiny_score(ot_id, personality) < 8}


def inspect(raw: bytes, rom: bytes) -> dict:
    table = pointers(rom)
    tables = model.extract_tables(rom)
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    occupied, issues = [], []
    for box, start in enumerate(table):
        for slot in range(BOX_SLOTS):
            record = read_record(raw, active, start + slot * RECORD_SIZE)
            if not any(record):
                continue
            row = decode(record, tables) | {'box': box + 1, 'position': slot + 1,
                                             'native_observed_box': box in NATIVE_OBSERVED_BOXES}
            if row['species_name'] is None or row['level_from_exp'] is None:
                issues.append({'box': box + 1, 'position': slot + 1, 'reason': 'undecodable record'})
            occupied.append(row)
    return {'active_slot': result.active_slot, 'counter': active.counter, 'boxes': BOX_COUNT,
            'occupied': occupied, 'issues': issues, 'writer_authorized': False,
            'extra_sector_boxes': [20, 21, 22]}
