"""Candidate exact-v0.22 editor for existing Pokémon in PC Boxes 1-19.

A boxed CompressedPokemon (58 bytes) is expanded into the 100-byte Party form
the game itself builds on withdrawal (CreateBoxMonFromCompressedMon: PP to
maximum; BoxMonToMon: level from EXP, recalculated stats). The adopted E3
ordinary transformation is applied, and the result is compressed back. Only
bytes the Box form stores may change; PP, level and stats are derived by the
game on withdrawal and are discarded. Boxes 20-25, empty positions, eggs,
special species/states and any record that does not round-trip are rejected.
No Box creation. An independent auditor must reconstruct the complete output.
"""
from __future__ import annotations

import struct

import pokemonstart_save_verifier as verifier
import pokemonstart_v022_box_model as box
import pokemonstart_v022_party_model as model
import pokemonstart_v022_product_party as party

WRITABLE_BOXES = range(1, 20)
FIELDS = {'species', 'level', 'experience', 'moves', 'pp_up', 'friendship', 'ivs', 'evs',
          'effective_nature', 'ability', 'held_item', 'shiny'}
# Party offsets stored by the Box form, and offsets the game derives on withdrawal.
STORED = frozenset((*range(0, 28), *range(32, 43), *range(44, 52), *range(56, 62), *range(68, 76)))
DERIVED = frozenset((*range(52, 56), *range(80, 100)))
STORAGE_SECTIONS = range(5, 14)


def expand(record: bytes, tables) -> bytes:
    if len(record) != box.RECORD_SIZE:
        raise ValueError('Box record length')
    out = bytearray(100)
    out[0:28] = record[0:28]
    out[32:43] = record[28:39]
    packed = int.from_bytes(record[39:44], 'little')
    bonuses = record[36]
    for index in range(4):
        move = (packed >> (10 * index)) & 0x3FF
        maximum = model.maximum_pp(move, (bonuses >> (2 * index)) & 3, tables)
        if maximum is None:
            raise ValueError('Box move PP metadata unresolved')
        struct.pack_into('<H', out, 44 + 2 * index, move)
        out[52 + index] = maximum
    out[56:62] = record[44:50]
    out[68:76] = record[50:58]
    species = tables.species[int.from_bytes(out[32:34], 'little')] if 0 < int.from_bytes(out[32:34], 'little') < len(tables.species) else None
    level = model.level_from_exp(int.from_bytes(out[36:40], 'little'), species.growth, tables) if species else None
    if level is None:
        raise ValueError('Box species/EXP unresolved')
    out[84] = level
    stats = model.decode_record(bytes(out), 0, tables)['ordinary_expected_stats']
    if not stats:
        raise ValueError('Box ordinary stats unavailable')
    # Current HP 1: withdrawal heals fully, so no in-battle HP context exists.
    struct.pack_into('<7H', out, 86, 1, *stats)
    return bytes(out)


def compress(record: bytes) -> bytes:
    out = bytearray(box.RECORD_SIZE)
    out[0:28] = record[0:28]
    out[28:39] = record[32:43]
    moves = struct.unpack_from('<4H', record, 44)
    if any(move > 0x3FF for move in moves):
        raise ValueError('move ID not representable in Box form')
    out[39:44] = sum(move << (10 * i) for i, move in enumerate(moves)).to_bytes(5, 'little')
    out[44:50] = record[56:62]
    out[50:58] = record[68:76]
    return bytes(out)


def _locate(raw: bytes, rom: bytes, number: int, position: int):
    if type(number) is not int or number not in WRITABLE_BOXES:
        raise ValueError('Box editing supports Boxes 1-19 only')
    if type(position) is not int or not 1 <= position <= box.BOX_SLOTS:
        raise ValueError('Box position must be 1-30')
    table = box.pointers(rom)
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    start = table[number - 1] + (position - 1) * box.RECORD_SIZE
    offsets = [box._file_offset(active, start + i) for i in range(box.RECORD_SIZE)]
    sectors = {o // 4096 for o in offsets}
    allowed = {active.section(s).physical_sector for s in STORAGE_SECTIONS}
    if not sectors <= allowed:
        raise ValueError('Box record outside checksummed storage sections')
    return result, active, offsets


def record_reasons(record: bytes, tables, context: dict) -> list:
    """Fail-closed eligibility of one boxed record for E3 editing."""
    if not any(record):
        return ['empty Box position']
    reasons = []
    try:
        expanded = expand(record, tables)
        if compress(expanded) != record:
            reasons.append('record does not round-trip through the Box form')
        reasons += model.write_eligibility(expanded, tables, context)['reasons']
        if expanded[75] & 0x40:
            reasons.append('egg')
    except ValueError as exc:
        reasons.append(str(exc))
    return list(dict.fromkeys(reasons))


def eligibility(raw: bytes, rom: bytes, number: int, position: int, tables=None) -> dict:
    tables = tables or model.extract_tables(rom)
    result, _, offsets = _locate(raw, rom, number, position)
    record = bytes(raw[o] for o in offsets)
    reasons = record_reasons(record, tables, model.saved_context(result))
    return {'eligible': not reasons, 'reasons': reasons, 'record': record}


def semantic(record: bytes, tables) -> dict:
    """E3-style view of a boxed record as the game withdraws it."""
    mon = model.decode_record(expand(record, tables), 0, tables)
    personality, ot_id = struct.unpack_from('<II', record, 0)
    return {'species': mon['species'], 'species_name': mon['species_name'], 'level': mon['stored_level'],
            'experience': mon['experience'], 'friendship': mon['friendship'], 'ivs': mon['ivs'],
            'evs': mon['evs'], 'effective_nature': mon['effective_nature'],
            'resolved_ability': mon['resolved_ability'], 'held_item': mon['held_item'],
            'moves': [m['move_id'] for m in mon['moves']],
            'pp_up': [m['pp_up_count'] for m in mon['moves']],
            'shiny': model.shiny_score(ot_id, personality) < 8}


def _all_personalities(raw: bytes, rom: bytes, skip: tuple[int, int]) -> set:
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    base = active.section(1).physical_sector * 4096 + verifier.PARTY_OFFSET
    found = {raw[base + i * 100:base + i * 100 + 4] for i in range(result.party_count)}
    for number, start in enumerate(box.pointers(rom), 1):
        for position in range(1, box.BOX_SLOTS + 1):
            if (number, position) == skip:
                continue
            record = box.read_record(raw, active, start + (position - 1) * box.RECORD_SIZE)
            if any(record):
                found.add(record[:4])
    return found


def derive(raw: bytes, rom: bytes, edits: list) -> tuple[bytes, dict]:
    """Apply E3 edits to existing Box records; returns output and receipt."""
    import pokemonstart_v022_box_audit as audit
    if not isinstance(edits, list) or not edits:
        raise ValueError('Box edits require a nonempty list')
    tables = model.extract_tables(rom)
    output = bytearray(raw)
    rows, seen = [], set()
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'box', 'position', 'changes'}:
            raise ValueError('Box edit requires box, position and changes')
        key = (edit['box'], edit['position'])
        if key in seen:
            raise ValueError('duplicate Box position')
        seen.add(key)
        changes = edit['changes']
        if not isinstance(changes, dict) or not changes or set(changes) - FIELDS:
            raise ValueError('unsupported Box changes (PP is not stored in Boxes)')
        result, active, offsets = _locate(raw, rom, *key)
        state = eligibility(raw, rom, *key, tables)
        if not state['eligible']:
            raise ValueError(f'Box {key[0]} #{key[1]} rejected: ' + '; '.join(state['reasons']))
        expanded = expand(state['record'], tables)
        transformed = party.transform_ordinary(expanded, tables, model.saved_context(result), changes)
        changed = {i for i in range(100) if expanded[i] != transformed[i]}
        if not changed <= STORED | DERIVED:
            raise ValueError('E3 transformation touched bytes the Box form cannot store')
        record = compress(transformed)
        if record == state['record']:
            raise ValueError(f'Box {key[0]} #{key[1]} unchanged')
        if record[:4] != state['record'][:4] and record[:4] in _all_personalities(raw, rom, key):
            raise ValueError('generated personality collides with another Pokémon')
        for offset, value in zip(offsets, record):
            output[offset] = value
        rows.append({'box': key[0], 'position': key[1], 'changes': changes,
                     'before': semantic(state['record'], tables), 'after': semantic(record, tables)})
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    for sid in STORAGE_SECTIONS:
        section = active.section(sid)
        base = section.physical_sector * 4096
        if output[base:base + verifier.SECTION_LENGTHS[sid]] != raw[base:base + verifier.SECTION_LENGTHS[sid]]:
            checksum = verifier.calculate_save_checksum(output[base:base + verifier.SECTION_LENGTHS[sid]])
            output[base + 0xFF6:base + 0xFF8] = checksum.to_bytes(2, 'little')
    candidate = bytes(output)
    verifier.verify_bytes(candidate)
    independent = audit.audit_box_edit(raw, candidate, rom, edits)
    return candidate, {'box': True, 'edits': rows, 'independent_audit': independent,
                       'changed_offsets': independent['changed_offsets'], 'verifier_accepted': True}
