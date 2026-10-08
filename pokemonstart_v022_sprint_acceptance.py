"""Combined Give All / shiny / shiny-creation / Box-edit acceptance for the exact-v0.22 editor.

The recipe is derived deterministically from the source save and equals what the
GUI produces with the checklist steps (GUI defaults plus the listed changes), so
no receipt file is needed. Gameplay attestation stays with the Human.
"""
from __future__ import annotations
import argparse
import json
import struct
from pathlib import Path
import pokemonstart_v022_product_core as core
import pokemonstart_v022_party_audit as party_audit
import pokemonstart_v022_inventory_editor as items
import pokemonstart_v022_box_audit as box_audit

CREATE_SPECIES = 4  # ヒトカゲ: shiny palette is easy to recognise in game
CREATE_LEVEL = 10


def _shiny(record: bytes) -> bool:
    personality, ot_id = struct.unpack_from('<II', record, 0)
    trainer = (ot_id >> 16) ^ (ot_id & 0xFFFF)
    return (trainer ^ (personality >> 16) ^ (personality & 0xFFFF)) < 8


def recipe(raw: bytes, rom: bytes) -> dict:
    report = core.inspect(raw, core.profile.sha(rom), rom_bytes=rom)
    if not (report.get('items') or {}).get('give_all', {}).get('enabled'):
        raise ValueError('Give All is unavailable for this save')
    candidates = [m['slot'] for m in report['party'] if m['capabilities'].get('shiny') and not m['shiny']]
    if not candidates:
        raise ValueError('no eligible non-shiny Party member')
    request = {'party': [{'slot': candidates[0], 'changes': {'shiny': True}}]}
    creator = report.get('creator') or {}
    if creator.get('eligible'):
        options = creator['options']
        if CREATE_SPECIES not in options['species'] or 33 not in options['moves']:
            raise ValueError('checklist creation species/move unavailable')
        request['create'] = [{'species': CREATE_SPECIES, 'level': CREATE_LEVEL, 'nature': 0,
                              'friendship': creator['friendship_defaults'][CREATE_SPECIES],
                              'ability': options['abilities'][CREATE_SPECIES][0], 'held_item': 0,
                              'ivs': [0]*6, 'evs': [0]*6, 'moves': [33, 0, 0, 0], 'shiny': True}]
    editable = [row for row in (report.get('box') or {}).get('occupied', []) if row['editable']]
    if editable:
        row = editable[0]
        request['box'] = [{'box': row['box'], 'position': row['position'],
                           'changes': {'level': min(row['semantic']['level'] + 10, 100)}}]
    request['items'] = [{'op': 'give_all'}]
    return request


def _box_record(raw: bytes, rom: bytes, edit: dict) -> bytes:
    offsets = box_audit._record_offsets(box_audit._active_sectors(raw), rom, edit['box'], edit['position'])
    return bytes(raw[o] for o in offsets)


def audit_export(source: bytes, actual: bytes, rom: bytes) -> dict:
    request = recipe(source, rom)
    expected, transaction = core.derive(source, core.profile.sha(rom), request, rom_bytes=rom)
    if actual != expected:
        raise ValueError('GUI output differs from the independently derived checklist output')
    audit = transaction.get('independent_e4_audit') or transaction.get('independent_e3_audit')
    if not audit or not audit.get('complete_output_equal'):
        raise ValueError('independent complete-output reconstruction missing')
    if not transaction['families']['items']['independent_audit']:
        raise ValueError('independent Inventory audit missing')
    parsed = party_audit.structure.parse(actual)
    shiny_slots = [request['party'][0]['slot']] + [parsed['count'] - 1] * ('create' in request)
    if not all(_shiny(parsed['records'][slot]) for slot in shiny_slots):
        raise ValueError('independent shiny formula disagrees with the export')
    if 'box' in request:
        edit = request['box'][0]
        level = party_audit.reconstruct(box_audit._expand(_box_record(actual, rom, edit), rom), rom)['exp_derived_level']
        if level != edit['changes']['level']:
            raise ValueError('independent Box level disagrees with the export')
    return {'status': 'EXPORT_VERIFIED_READY_FOR_GAMEPLAY', 'semantic_diff': transaction['semantic_diff'],
            'shiny_slots': [s + 1 for s in shiny_slots], 'gameplay_attestation': False}


def check_return(source: bytes, exported: bytes, returned: bytes, rom: bytes) -> dict:
    audit_export(source, exported, rom)
    core.v.verify_bytes(returned)
    before, after = party_audit.structure.parse(exported), party_audit.structure.parse(returned)
    old, new = before['slots'][before['active']], after['slots'][after['active']]
    if len(exported) != len(returned) or after['active'] == before['active'] or new['counter'] != old['counter'] + 1:
        raise ValueError('return requires exactly one ordinary SAVE slot/counter transition')
    prior = before['active'] * 14 * 4096
    if exported[prior:prior + 14 * 4096] != returned[prior:prior + 14 * 4096]:
        raise ValueError('prior active slot was not preserved')
    if any(new['positions'][s] % 14 != (old['positions'][s] % 14 + 1) % 14 for s in range(14)):
        raise ValueError('normal SAVE section rotation mismatch')
    request = recipe(source, rom)
    box_result = None
    if 'box' in request:
        edit = request['box'][0]
        exported_record, returned_record = _box_record(exported, rom, edit), _box_record(returned, rom, edit)
        if returned_record == exported_record:
            box_result = 'kept in Box: edited record preserved'
        elif not any(returned_record) and after['count'] == before['count'] + 1:
            withdrawn = after['records'][-1]
            if box_audit._compress(withdrawn) != exported_record:
                raise ValueError('withdrawn Box Pokémon differs from the edited record')
            if party_audit.ordinary_reasons(withdrawn, rom, party_audit.inspect(returned, rom)['saved_context']):
                raise ValueError('withdrawn Box Pokémon is not ordinary-consistent (level/stats/PP)')
            if withdrawn[84] != edit['changes']['level']:
                raise ValueError('withdrawn Box Pokémon level differs from the requested level')
            box_result = 'withdrawn to Party: stored bytes equal, level/stats/PP consistent'
        else:
            raise ValueError('edited Box record neither preserved nor cleanly withdrawn')
    if after['count'] != before['count'] + (box_result is not None and box_result.startswith('withdrawn')):
        raise ValueError('Party count changed during gameplay')
    for slot, (a, b) in enumerate(zip(before['records'], after['records'])):
        if a[:4] != b[:4] or a[32:34] != b[32:34] or _shiny(a) != _shiny(b):
            raise ValueError(f'Party #{slot+1} identity, species or shiny state changed')
    rom_names = items.supported_catalog(rom)
    quantities = {e['item_id']: e['quantity'] for e in items.inspect(returned, rom)['entries']}
    missing = [rom_names[i] for i in rom_names if i not in quantities]
    if missing:
        raise ValueError('Give All item missing after gameplay: ' + ', '.join(missing))
    used = {rom_names[i]: 99 - quantities[i] for i in rom_names if quantities[i] < 99}
    report = core.inspect(returned, core.profile.sha(rom), rom_bytes=rom)
    if not report['items'] or not report['items'].get('e2'):
        raise ValueError('returned save lost Inventory eligibility')
    return {'status': 'MACHINE_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED', 'counter': [old['counter'], new['counter']],
            'shiny_preserved': True, 'give_all_items_present': len(rom_names), 'items_used_in_game': used,
            'box_edit': box_result,
            'human_gameplay_attestation': False}


def _one_normal_save(previous: bytes, current: bytes) -> tuple[dict, dict]:
    core.v.verify_bytes(current)
    before, after = party_audit.structure.parse(previous), party_audit.structure.parse(current)
    old, new = before['slots'][before['active']], after['slots'][after['active']]
    if len(previous) != len(current) or after['active'] == before['active'] or new['counter'] != old['counter'] + 1:
        raise ValueError('requires exactly one ordinary SAVE slot/counter transition')
    prior = before['active'] * 14 * 4096
    if previous[prior:prior + 14 * 4096] != current[prior:prior + 14 * 4096]:
        raise ValueError('prior active slot was not preserved')
    if any(new['positions'][s] % 14 != (old['positions'][s] % 14 + 1) % 14 for s in range(14)):
        raise ValueError('normal SAVE section rotation mismatch')
    return before, after


def check_followup(previous: bytes, current: bytes, rom: bytes, *, box_number: int = 1, position: int = 1) -> dict:
    """Withdraw the edited Box Pokémon and consume one supported item, then one SAVE."""
    before, after = _one_normal_save(previous, current)
    context = party_audit.inspect(current, rom)['saved_context']
    location = {'box': box_number, 'position': position}
    boxed = _box_record(previous, rom, location)
    if not any(boxed) or any(_box_record(current, rom, location)):
        raise ValueError(f'Box {box_number} #{position} was not withdrawn')
    for number in range(1, 20):
        for slot in range(1, 31):
            if (number, slot) != (box_number, position) and _box_record(previous, rom, {'box': number, 'position': slot}) != \
                    _box_record(current, rom, {'box': number, 'position': slot}):
                raise ValueError(f'unrelated Box {number} #{slot} changed')
    import pokemonstart_v022_box_model as box
    rest = lambda raw: [r for r in box.inspect(raw, rom)['occupied'] if r['box'] > 19]
    if rest(previous) != rest(current):
        raise ValueError('Boxes 20-25 changed')
    if after['count'] != before['count'] + 1:
        raise ValueError('Party count must grow by exactly the withdrawn Pokémon')
    matches = [r for r in after['records'] if r[:4] == boxed[:4]]
    if len(matches) != 1:
        raise ValueError('withdrawn Pokémon not found exactly once in Party')
    withdrawn = matches[0]
    stored = box_audit._compress(withdrawn)
    # Walking in the Party raises friendship (byte 37 of the Box form); every other stored byte must match.
    if stored[:37] + stored[38:] != boxed[:37] + boxed[38:] or stored[37] < boxed[37]:
        raise ValueError('withdrawn Pokémon differs from its Box record (was it used in battle?)')
    row = party_audit.reconstruct(withdrawn, rom)
    if party_audit.ordinary_reasons(withdrawn, rom, context):
        raise ValueError('withdrawn Pokémon is not ordinary-consistent')
    if row['cached_hp_stats'][0] != row['cached_hp_stats'][1] or any(m['pp'] != m['maximum_pp'] for m in row['moves']):
        raise ValueError('withdrawn Pokémon lacks full HP/PP')
    for record in before['records']:
        now = [r for r in after['records'] if r[:4] == record[:4]]
        if len(now) != 1 or now[0][32:34] != record[32:34] or _shiny(now[0]) != _shiny(record):
            raise ValueError('existing Party member identity/species/shiny changed')
        if party_audit.ordinary_reasons(now[0], rom, context):
            raise ValueError('existing Party member lost ordinary eligibility')
    names = items.supported_catalog(rom)
    old_items = {e['item_id']: e['quantity'] for e in items.inspect(previous, rom)['entries']}
    new_items = {e['item_id']: e['quantity'] for e in items.inspect(current, rom)['entries']}
    unsupported = lambda q: {i: n for i, n in q.items() if i not in names}
    if unsupported(old_items) != unsupported(new_items):
        raise ValueError('non-supported Inventory entries changed')
    used = {i: old_items.get(i, 0) - new_items.get(i, 0) for i in names if old_items.get(i, 0) != new_items.get(i, 0)}
    if any(delta < 0 for delta in used.values()):
        raise ValueError('a supported item increased during gameplay')
    if not used:
        raise ValueError('no supported item was consumed')
    report = core.inspect(current, core.profile.sha(rom), rom_bytes=rom)
    if not report['items'] or not report['items'].get('e2'):
        raise ValueError('Inventory eligibility lost')
    newly = {names[i]: d for i, d in used.items() if i not in items.MEDICINES}
    money = report['money']['money'] - core.inspect(previous, core.profile.sha(rom), rom_bytes=rom)['money']['money']
    return {'status': 'MACHINE_FOLLOWUP_PASS_HUMAN_ATTESTATION_REQUIRED',
            'counter': [before['slots'][before['active']]['counter'], after['slots'][after['active']]['counter']],
            'withdrawn': {'species': row['species'], 'level': withdrawn[84], 'stats': row['cached_hp_stats'][1:],
                          'moves': [m['move_id'] for m in row['moves']], 'full_hp_pp': True,
                          'stored_bytes_equal_box_record_except_friendship': True,
                          'friendship_gameplay_increase': stored[37] - boxed[37]},
            'items_consumed': {names[i]: d for i, d in used.items()}, 'newly_qualified_item_consumed': bool(newly),
            'money_delta': money, 'unrelated_box_records_preserved': True,
            'party_identity_shiny_preserved': True, 'human_gameplay_attestation': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=core.profile.ROM_DEFAULT)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('recipe'); p.add_argument('source', type=Path)
    p = sub.add_parser('audit-export'); p.add_argument('source', type=Path); p.add_argument('exported', type=Path)
    p = sub.add_parser('check-return'); p.add_argument('source', type=Path); p.add_argument('exported', type=Path)
    p.add_argument('returned', type=Path)
    p = sub.add_parser('check-followup'); p.add_argument('previous', type=Path); p.add_argument('current', type=Path)
    args = parser.parse_args(argv)
    rom = args.rom.read_bytes()
    core.profile._require_rom_hash(core.profile.sha(rom))
    if args.action == 'recipe':
        result = recipe(args.source.read_bytes(), rom)
    elif args.action == 'check-followup':
        result = check_followup(args.previous.read_bytes(), args.current.read_bytes(), rom)
    elif args.action == 'audit-export':
        result = audit_export(args.source.read_bytes(), args.exported.read_bytes(), rom)
    else:
        result = check_return(args.source.read_bytes(), args.exported.read_bytes(), args.returned.read_bytes(), rom)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
