"""Independent read-only E1 cross-check; imports neither model nor any writer.

Reconstructs the serialized RAM image instead of using per-record scatter
addresses. Structural save validation uses the existing independent parser.
"""
from __future__ import annotations

import hashlib
import struct

import pokemonstart_v022_creation_audit as structure

ROM_SHA256 = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'
NON_NEUTRAL_IDS = (frozenset(range(57, 72)) | frozenset(range(753, 774))
                   | frozenset(range(824, 829)) | {639, 640, 728, 729, 832, 836, 838})
# Independently enumerated exact-ROM recovery-signature IDs (13..33, 38..41,
# 44, 52..56, 82). Give All raises each to 99 within section 13 only.
RECOVERY_TARGETS = (frozenset(range(13, 34)) | frozenset(range(38, 42))
                    | frozenset(range(52, 57)) | {44, 82})


def expand_give_all(records: list[tuple[int, int]]) -> list[dict]:
    present = dict(records)
    expanded = []
    for target in sorted(RECOVERY_TARGETS):
        if target not in present:
            expanded.append({'op': 'add', 'item_id': target, 'quantity': 99})
        elif present[target] < 99:
            expanded.append({'op': 'set', 'item_id': target, 'quantity': 99})
    if not expanded or len(records) + sum(x['op'] == 'add' for x in expanded) > 325:
        raise ValueError('independent Give All eligibility')
    return expanded


def audit_edit(before: bytes, after: bytes, rom: bytes, operations: list[dict]) -> dict:
    """Independent full expected-output reconstruction, without writer imports."""
    old, new = restricted(before, rom), restricted(after, rom)
    records = [(row[1], row[2]) for row in old['pockets'][0]['entries']]
    if not isinstance(operations, list) or not operations:
        raise ValueError('independent empty edit')
    if operations == [{'op': 'give_all'}]:
        operations = expand_give_all(records)
    seen = set()
    for edit in operations:
        if not isinstance(edit, dict) or edit.get('op') not in ('add', 'set', 'remove'):
            raise ValueError('independent operation invalid')
        op, target = edit['op'], edit.get('item_id')
        keys = {'op', 'item_id'} | (set() if op == 'remove' else {'quantity'})
        if set(edit) != keys or type(target) is not int or target not in RECOVERY_TARGETS or target in seen:
            raise ValueError('independent unsafe/repeated target')
        seen.add(target)
        metadata = rom[0x15199C8 + target * 40:0x15199C8 + (target + 1) * 40]
        if (metadata[20] != 0 or metadata[22:24] != bytes((1, 1))
                or int.from_bytes(metadata[24:28], 'little') != 0x080A29B5
                or metadata[28] != 1 or int.from_bytes(metadata[32:36], 'little') != 0x080A327D):
            raise ValueError('independent medicine metadata')
        positions = [index for index, row in enumerate(records) if row[0] == target]
        if op != 'remove' and (type(edit.get('quantity')) is not int or not 1 <= edit['quantity'] <= 999):
            raise ValueError('independent quantity range')
        if op == 'add':
            if positions or len(records) == 700:
                raise ValueError('independent add eligibility')
            records += [(target, edit['quantity'])]
        elif not positions:
            raise ValueError('independent existing target absent')
        elif op == 'remove':
            del records[positions[0]]
        else:
            records[positions[0]] = (target, edit['quantity'])
    parsed = structure.parse(before)
    # Structural parser exposes section byte strings; independently find their
    # physical sector from section IDs, rather than importing a writer offset.
    active = parsed['active']
    section13 = next(i for i in range(active * 14, active * 14 + 14)
                     if int.from_bytes(before[i * 4096 + 0xFF4:i * 4096 + 0xFF6], 'little') == 13)
    image = b''.join(struct.pack('<HH', *row) for row in records) + bytes((700 - len(records)) * 4)
    expected = bytearray(before)
    start = section13 * 4096 + 0xADC
    expected[start:section13 * 4096 + 0xFF0] = image[:1300]
    expected[0x1E000:0x1E5DC] = image[1300:]
    expected[0x1E716:0x1E718] = len(records).to_bytes(2, 'little')
    if after != bytes(expected) or before == after:
        raise ValueError('independent complete output/envelope inequality')
    if [(row[1], row[2]) for row in new['pockets'][0]['entries']] != records:
        raise ValueError('independent semantic postcondition')
    return {'complete_output_equal': True, 'unrelated_bytes_preserved': True,
            'source_sha256': hashlib.sha256(before).hexdigest(),
            'output_sha256': hashlib.sha256(after).hexdigest(),
            'changed_offsets': [i for i, (x, y) in enumerate(zip(before, after)) if x != y]}


def restricted(raw: bytes, rom: bytes) -> dict:
    """Independent restricted predicate using assembled RAM, not scatter writes."""
    report = inspect(raw, rom)
    if not report['state_supported']:
        raise ValueError('independent malformed inventory')
    parsed = structure.parse(raw)
    sec = parsed['slots'][parsed['active']]['sections']
    image = (sec[0][0xF24:0xFF0] + sec[4][0xD98:0xFF0]
             + sec[13][0x450:0xFF0] + raw[0x1E000:0x1EFF0] + raw[0x1F000:0x1FFF0])
    if image[0x13D] & (1 << 3):
        raise ValueError('independent classification selector unsupported')
    # Independently transcribed exact classifier's accepted nonzero outcomes.
    if any(row[1] in NON_NEUTRAL_IDS for row in report['pockets'][0]['entries']):
        raise ValueError('independent non-neutral classification')
    counts = list(struct.unpack_from('<3H', image, 0x15DA))
    for count, pocket in zip(counts, report['pockets'][:3]):
        if pocket['holes'] or count != len(pocket['entries']):
            raise ValueError('independent compact/count invariant')
        if pocket['name'] != 'regular' and len(pocket['entries']) == pocket['capacity']:
            raise ValueError('independent full non-regular menu pocket')
    report['restricted_eligible'] = True
    report['menu_counts'] = counts
    return report


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
                         and record[22] == expected_pocket and record[20] in (0, 1, 2)
                         and 0xFF in record[:10] and record[0] != 0xFF)
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
