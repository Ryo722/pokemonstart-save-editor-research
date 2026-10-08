"""Independent reconstruction of exact-v0.22 Box 1-19 edits.

Shares no code with the production Box writer, box decoder or save verifier:
slot/sector discovery, record placement, Box<->Party conversion and checksums
are reimplemented here; record arithmetic uses the independent E3 auditor.
"""
from __future__ import annotations

import struct

import pokemonstart_v022_party_audit as party_audit

ROM_BOX_TABLE = 0x1492538
COMPRESSED = 58
PER_BOX = 30
SECTOR = 4096
SLOT_SECTORS = 14
SIGNATURE = 0x08012025
# Storage block: logical sections 5..13; 0xFF0 payload each, 0x450 for section 13.
STORAGE_FIRST, STORAGE_PAYLOAD = 5, 0xFF0
LENGTHS = {**{sid: 0xFF0 for sid in range(5, 13)}, 13: 0x450}
PARTY_SECTION, PARTY_AT = 1, 0x38


def _active_sectors(raw: bytes) -> dict:
    best = None
    for slot in (0, 1):
        ids, counters = {}, set()
        for physical in range(slot * SLOT_SECTORS, (slot + 1) * SLOT_SECTORS):
            base = physical * SECTOR
            sid, _, signature, counter = struct.unpack_from('<HHII', raw, base + 0xFF4)
            if signature != SIGNATURE:
                break
            ids[sid] = physical
            counters.add(counter)
        if len(ids) == SLOT_SECTORS and len(counters) == 1:
            counter = counters.pop()
            if best is None or counter > best[0]:
                best = (counter, ids)
    if best is None:
        raise ValueError('independent: no complete save slot')
    return best[1]


def _checksum(data: bytes) -> int:
    total = sum(struct.unpack(f'<{len(data) // 4}I', data)) & 0xFFFFFFFF
    return ((total >> 16) + total) & 0xFFFF


def _record_offsets(ids: dict, rom: bytes, number: int, position: int) -> list:
    table = struct.unpack_from('<25I', rom, ROM_BOX_TABLE)
    storage = table[0] - 4
    if not 1 <= number <= 19 or not 1 <= position <= PER_BOX:
        raise ValueError('independent: Box location outside 1-19 / 1-30')
    pointer = table[number - 1]
    if pointer != storage + 4 + (number - 1) * PER_BOX * COMPRESSED:
        raise ValueError('independent: Box pointer outside contiguous storage')
    logical = pointer - storage + (position - 1) * COMPRESSED
    offsets = []
    for i in range(COMPRESSED):
        section, inner = divmod(logical + i, STORAGE_PAYLOAD)
        sid = STORAGE_FIRST + section
        if sid not in LENGTHS or inner >= LENGTHS[sid]:
            raise ValueError('independent: Box record outside storage payload')
        offsets.append(ids[sid] * SECTOR + inner)
    return offsets


def _expand(record: bytes, rom: bytes) -> bytes:
    party = bytearray(100)
    party[0:28], party[32:43] = record[0:28], record[28:39]
    bits = int.from_bytes(record[39:44], 'little')
    moves = [(bits >> shift) & 1023 for shift in (0, 10, 20, 30)]
    for index, move in enumerate(moves):
        party[44 + 2 * index:46 + 2 * index] = move.to_bytes(2, 'little')
    party[56:62], party[68:76] = record[44:50], record[50:58]
    first = party_audit.reconstruct(bytes(party), rom)
    party[84] = first['exp_derived_level']
    for index, move in enumerate(first['moves']):
        party[52 + index] = move['maximum_pp']
    second = party_audit.reconstruct(bytes(party), rom)
    stats = second['ordinary_expected_stats']
    if stats is None:
        raise ValueError('independent: stats unavailable')
    party[86:100] = struct.pack('<7H', 1, *stats)
    return bytes(party)


def _compress(party: bytes) -> bytes:
    moves = [int.from_bytes(party[44 + 2 * i:46 + 2 * i], 'little') for i in range(4)]
    if max(moves) >= 1024:
        raise ValueError('independent: move not representable')
    bits = moves[0] | moves[1] << 10 | moves[2] << 20 | moves[3] << 30
    return party[0:28] + party[32:43] + bits.to_bytes(5, 'little') + party[56:62] + party[68:76]


def expected_changes(before: bytes, rom: bytes, edits: list) -> tuple[dict, set, set]:
    """Independent Box record bytes and storage checksums: (offset->byte, records, checksums)."""
    ids = _active_sectors(before)
    context = party_audit.inspect(before, rom)['saved_context']
    expected = bytearray(before)
    record_bytes = set()
    for edit in edits:
        offsets = _record_offsets(ids, rom, edit['box'], edit['position'])
        if record_bytes & set(offsets):
            raise ValueError('independent: duplicate Box position')
        source = bytes(before[o] for o in offsets)
        if not any(source):
            raise ValueError('independent: empty Box position')
        party = _expand(source, rom)
        if _compress(party) != source:
            raise ValueError('independent: record does not round-trip')
        target, _ = party_audit.expected_record(party, rom, context, edit['changes'])
        for offset, value in zip(offsets, _compress(target)):
            expected[offset] = value
            record_bytes.add(offset)
    checksum_bytes = set()
    for sid, length in LENGTHS.items():
        base = ids[sid] * SECTOR
        if expected[base:base + length] != before[base:base + length]:
            expected[base + 0xFF6:base + 0xFF8] = _checksum(bytes(expected[base:base + length])).to_bytes(2, 'little')
            checksum_bytes.update((base + 0xFF6, base + 0xFF7))
    changes = {i: expected[i] for i in record_bytes | checksum_bytes}
    return changes, record_bytes, checksum_bytes


def audit_box_edit(before: bytes, after: bytes, rom: bytes, edits: list) -> dict:
    changes, record_bytes, checksum_bytes = expected_changes(before, rom, edits)
    expected = bytearray(before)
    for offset, value in changes.items():
        expected[offset] = value
    if bytes(expected) != after:
        raise ValueError('independent: Box output reconstruction differs')
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    if not set(changed) <= record_bytes | checksum_bytes:
        raise ValueError('independent: Box byte envelope exceeded')
    return {'complete_output_equal': True, 'changed_offsets': changed,
            'edited_records': len(edits), 'gameplay_acceptance': False}
