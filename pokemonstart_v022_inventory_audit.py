"""Independent read-only E1 cross-check; imports neither model nor any writer.

Reconstructs the serialized RAM image instead of using per-record scatter
addresses. Structural save validation uses the existing independent parser.
"""
from __future__ import annotations

import hashlib
import struct

import pokemonstart_v022_creation_audit as structure

ROM_SHA256 = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'


def inspect(raw: bytes, rom: bytes) -> dict:
    if hashlib.sha256(rom).hexdigest() != ROM_SHA256 or len(rom) != 33554432:
        raise ValueError('independent exact ROM gate')
    parsed = structure.parse(raw)
    if parsed['key'] != 0:
        raise ValueError('independent inventory key0 only')
    sections = parsed['slots'][parsed['active']]['sections']
    ram = (sections[0][0xF24:0xFF0] + sections[4][0xD98:0xFF0]
           + sections[13][0x450:0xFF0] + raw[0x1E000:0x1EFF0] + raw[0x1F000:0x1FFF0])
    if int.from_bytes(ram[0x58A:0x58C], 'little', signed=True) < 0:
        raise ValueError('independent alternate runtime bag unsupported')
    # Offsets relative to reconstructed 0x0203B0E8, independently enumerated.
    regions = (('regular', 0x9B0, 700, 1), ('key', 0x14A0, 75, 2),
               ('balls', 0x15EC, 50, 3), ('tmhm', 0x16B4, 128, 4),
               ('berries', 0x18B4, 72, 5))
    table_address = int.from_bytes(rom[0x1C8:0x1CC], 'little')
    if table_address != 0x095199C8:
        raise ValueError('independent item table')
    pockets, issues = [], []
    for name, start, count, expected_pocket in regions:
        entries, empty, seen = [], [], set()
        for slot in range(count):
            item, quantity = struct.unpack_from('<HH', ram, start + slot * 4)
            if item == quantity == 0:
                empty.append(slot)
                continue
            valid = 1 <= item <= 838 and item != 375
            if valid:
                record = rom[0x15199C8 + item * 40:0x15199C8 + (item + 1) * 40]
                valid = (int.from_bytes(record[10:12], 'little') == item
                         and record[22] == expected_pocket and 0xFF in record[:10])
            if not valid or not 1 <= quantity <= 999 or item in seen:
                issues.append((name, slot))
            seen.add(item)
            entries.append((slot, item, quantity))
        last = max((entry[0] for entry in entries), default=-1)
        pockets.append({'name': name, 'capacity': count, 'entries': entries,
                        'holes': [slot for slot in empty if slot < last],
                        'first_empty': empty[0] if empty else None})
    return {'active_slot': parsed['active'], 'counter': parsed['slots'][parsed['active']]['counter'],
            'pockets': pockets, 'issues': issues, 'state_supported': not issues,
            'writer_authorized': False}
