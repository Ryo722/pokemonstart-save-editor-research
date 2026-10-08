"""Candidate medicine editing under the qualified exact-v0.22 neutral bag gate."""
from __future__ import annotations

from pathlib import Path
import os
import struct

import pokemonstart_v022_inventory_model as model
import pokemonstart_v022_inventory_audit as audit
import pokemonstart_fl2_core as profile

MEDICINES = frozenset(range(13, 23))
# Exact-v0.22 regular items sharing the adopted medicines' complete behavior
# signature (field/battle use routines). Membership is pinned by ID and the
# signature is re-checked against the ROM; neither alone grants support.
RECOVERY_ITEMS = MEDICINES | frozenset(range(23, 34)) | frozenset(range(38, 42)) | {44, 82} \
    | frozenset(range(52, 57))
GIVE_ALL_QUANTITY = 99
# Give All stays within logical section 13 (slots 0..324); slot 325 onward is
# serialized to the shared unchecksummed sector 30 without native evidence.
GIVE_ALL_OCCUPANCY_LIMIT = 325


def supported_catalog(rom: bytes) -> dict:
    catalog, _ = model.extract_catalog(rom)
    selected = {}
    for item_id in sorted(RECOVERY_ITEMS):
        item = catalog.get(item_id)
        if item is None:
            raise ValueError('qualified medicine metadata missing')
        offset = model.ITEM_TABLE - model.ROM_BASE + item_id * 40
        if (item.pocket != 1 or item.importance != 0 or item.item_type != 1
                or model.classification(item_id) != 0
                or struct.unpack_from('<I', rom, offset + 24)[0] != 0x080A29B5
                or rom[offset + 28] != 1
                or struct.unpack_from('<I', rom, offset + 32)[0] != 0x080A327D):
            raise ValueError('qualified medicine behavior metadata mismatch')
        selected[item_id] = item.name
    return selected


def inspect(raw: bytes, rom: bytes) -> dict:
    names = supported_catalog(rom)
    decoded = model.restricted(raw, rom)
    checked = audit.restricted(raw, rom)
    for first, second in zip(decoded['pockets'], checked['pockets']):
        if [(e['slot'], e['item_id'], e['quantity']) for e in first['entries']] != second['entries']:
            raise ValueError('independent inventory decode disagreement')
    if decoded['menu_counts'] != checked['menu_counts']:
        raise ValueError('independent menu-count disagreement')
    entries = [{key: entry[key] for key in ('slot', 'item_id', 'name', 'quantity')}
               | {'editable': entry['item_id'] in names, 'removable': entry['item_id'] in names}
               for entry in decoded['pockets'][0]['entries']]
    return {'e2': True, 'entries': entries, 'supported_names': names,
            'capacity': 700, 'quantity_min': 1, 'quantity_max': 999,
            'occupied': len(entries), 'give_all': give_all_status(decoded['pockets'][0]['entries'], names)}


def give_all_operations(entries: list[dict], names: dict) -> list[dict]:
    """Raise every supported item to 99 without lowering a larger stack."""
    present = {e['item_id']: e['quantity'] for e in entries}
    operations = [{'op': 'add' if item_id not in present else 'set', 'item_id': item_id,
                   'quantity': GIVE_ALL_QUANTITY}
                  for item_id in sorted(names) if present.get(item_id, 0) < GIVE_ALL_QUANTITY]
    occupied = len(entries) + sum(op['op'] == 'add' for op in operations)
    if occupied > GIVE_ALL_OCCUPANCY_LIMIT:
        raise ValueError('Give All would extend the regular pocket past slot 325')
    return operations


def give_all_status(entries: list[dict], names: dict) -> dict:
    status = {'supported_items': len(names), 'quantity': GIVE_ALL_QUANTITY,
              'scope': 'qualified recovery items only; not all items'}
    try:
        operations = give_all_operations(entries, names)
    except ValueError as exc:
        return status | {'enabled': False, 'reason': str(exc)}
    if not operations:
        return status | {'enabled': False, 'reason': 'every supported item already has 99 or more'}
    return status | {'enabled': True, 'changes': len(operations)}


def derive(raw: bytes, rom: bytes, operations: list[dict]) -> tuple[bytes, dict]:
    before = inspect(raw, rom)
    if not isinstance(operations, list) or not operations:
        raise ValueError('Items requires a nonempty operation list')
    rows = [(e['item_id'], e['quantity']) for e in before['entries']]
    if any(isinstance(x, dict) and x.get('op') == 'give_all' for x in operations):
        if operations != [{'op': 'give_all'}]:
            raise ValueError('Give All must be the only Items operation')
        if not before['give_all']['enabled']:
            raise ValueError('Give All unavailable: ' + before['give_all']['reason'])
        request = operations
        operations = give_all_operations(before['entries'], before['supported_names'])
    else:
        request = operations
    seen = set()
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError('invalid Items operation')
        verb = operation.get('op')
        expected = {'op', 'item_id'} if verb == 'remove' else {'op', 'item_id', 'quantity'}
        if verb not in ('add', 'set', 'remove') or set(operation) != expected:
            raise ValueError('unsupported Items operation')
        item_id = operation['item_id']
        if type(item_id) is not int or item_id not in RECOVERY_ITEMS or item_id in seen:
            raise ValueError('unsupported or repeated medicine target')
        seen.add(item_id)
        quantity = operation.get('quantity')
        if verb != 'remove' and (type(quantity) is not int or not 1 <= quantity <= 999):
            raise ValueError('medicine quantity must be an integer in 1..999')
        position = next((i for i, row in enumerate(rows) if row[0] == item_id), None)
        if verb == 'add':
            if position is not None:
                raise ValueError('Add requires an absent medicine')
            if len(rows) >= 700:
                raise ValueError('regular pocket is full')
            rows.append((item_id, quantity))
        elif position is None:
            raise ValueError('Set/Remove requires an existing medicine')
        elif verb == 'set':
            rows[position] = (item_id, quantity)
        else:
            rows.pop(position)
    verified = model.verifier.verify_bytes(raw)
    active = verified.slots[verified.active_slot]
    output = bytearray(raw)
    for slot in range(700):
        offset = model.record_offset(active, 0x0203BA98 + slot * 4)
        struct.pack_into('<HH', output, offset, *(rows[slot] if slot < len(rows) else (0, 0)))
    struct.pack_into('<H', output, 0x1E716, len(rows))
    candidate = bytes(output)
    if candidate == raw:
        raise ValueError('Items unchanged; no output')
    after = inspect(candidate, rom)
    independent = audit.audit_edit(raw, candidate, rom, request)
    return candidate, {'before': before, 'after': after,
                       'changed_offsets': independent['changed_offsets'],
                       'independent_audit': independent, 'verifier_accepted': True}


def export(source: Path, destination: Path, rom_path: Path, operations: list[dict]) -> dict:
    """Exclusive separate output; source and ROM remain immutable."""
    source = profile._private_file(source, 'source save', must_exist=True)
    rom_path = profile._private_file(rom_path, 'ROM', must_exist=True)
    destination = profile._private_file(destination, 'output save', must_exist=False)
    if source.resolve() == destination.resolve() or rom_path.resolve() == destination.resolve():
        raise ValueError('output must be separate from private inputs')
    raw, rom = source.read_bytes(), rom_path.read_bytes()
    output, report = derive(raw, rom, operations)
    if source.read_bytes() != raw or rom_path.read_bytes() != rom:
        raise ValueError('private input changed before export')
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as handle:
        handle.write(output)
    if destination.read_bytes() != output:
        raise ValueError('export equality failed')
    if source.read_bytes() != raw or rom_path.read_bytes() != rom:
        raise ValueError('private input changed during export')
    return report
