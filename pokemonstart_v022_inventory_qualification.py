"""Local read-only E1 evidence generator. Prints no input paths or ROM bytes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pokemonstart_v022_inventory_model as model
import pokemonstart_v022_inventory_audit as audit


# Addresses identified from the exact ROM's hooked functions, not inferred from
# upstream function locations. Hashes fingerprint the inspected code regions;
# they are not a claim that this program disassembles or proves their semantics.
CODE_REGIONS = (
    ('bag_init', 0x090D39A4, 0x1E), ('bag_override_condition', 0x090CDFCC, 0x14),
    ('bag_override', 0x090CD770, 0x30), ('compact', 0x090D40D4, 0xE),
    ('null_compare', 0x090D2524, 0x30), ('save_parasite', 0x090EAD2C, 0x3E),
    ('load', 0x090EAD8C, 0x122), ('save', 0x090EB168, 0x16A),
    ('sanitizer', 0x090D29C0, 0x14), ('quantity_getter', 0x080997A8, 4),
    ('quantity_setter', 0x080997C4, 0x1C), ('space', 0x08099A08, 0x84),
    ('add', 0x08099A8C, 0x154), ('remove', 0x08099BE0, 0x88),
    ('classification_callbacks', 0x090B8164, 0x8C),
    ('classifier', 0x090B81F0, 0x70), ('partition_count', 0x090B8274, 0x130),
    ('selector_clear_and_open_scan', 0x090B83F4, 0xB8),
    ('store_counts', 0x090D3D74, 0xB4), ('list_builder', 0x090D43A8, 0x12E),
    ('quantity_display', 0x08109150, 0x104),
    ('medicine_use', 0x090E6818, 0x238),
)


def qualify(rom_path: Path, save_paths: list[Path]) -> dict:
    rom = rom_path.read_bytes()
    catalog, summary = model.extract_catalog(rom)
    inputs = [(path, path.read_bytes()) for path in save_paths]
    snapshots = []
    for index, (_, raw) in enumerate(inputs):
        decoded = model.inspect(raw, rom)
        checked = audit.inspect(raw, rom)
        if ((decoded['active_slot'], decoded['counter'], decoded['state_supported'])
                != (checked['active_slot'], checked['counter'], checked['state_supported'])):
            raise ValueError('independent inventory state mismatch')
        for primary, secondary in zip(decoded['pockets'], checked['pockets']):
            tuples = [(e['slot'], e['item_id'], e['quantity']) for e in primary['entries']]
            if (tuples != secondary['entries'] or primary['holes'] != secondary['holes']
                    or primary['first_empty'] != secondary['first_empty']):
                raise ValueError('independent inventory reconstruction mismatch')
        eligible, rejection = True, None
        try:
            first, second = model.restricted(raw, rom), audit.restricted(raw, rom)
            if first['menu_counts'] != second['menu_counts']:
                raise ValueError('independent restricted count mismatch')
        except ValueError as exc:
            eligible, rejection = False, str(exc)
        snapshots.append({'snapshot': index + 1, 'sha256': model.sha(raw),
                          'counter': decoded['counter'], 'active_slot': decoded['active_slot'],
                          'state_supported': decoded['state_supported'],
                          'issues': decoded['issues'], 'independent_decode_equal': True,
                          'restricted_eligible': eligible, 'restricted_rejection': rejection,
                          'pockets': [{'name': p['name'], 'capacity': p['capacity'],
                                      'occupied': p['occupied'], 'holes': p['holes']}
                                     for p in decoded['pockets']]})
    if rom_path.read_bytes() != rom or any(path.read_bytes() != raw for path, raw in inputs):
        raise ValueError('private input changed during read-only probe')
    return {'catalog': summary, 'snapshots': snapshots, 'source_immutability': True,
            'code_regions': [{'name': name, 'address': hex(address), 'length': length,
                              'sha256': model.sha(rom[address - 0x08000000:address - 0x08000000 + length])}
                             for name, address, length in CODE_REGIONS],
            'writer_authorized': False, 'give_all_enabled': False,
            'disposition': 'READ_ONLY_RESTRICTED_INPUT_QUALIFICATION',
            'semantic_contract': 'docs/e1-restricted-state-qualification.md'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--save', required=True, type=Path, action='append')
    args = parser.parse_args()
    try:
        result = qualify(args.rom, args.save)
    except OSError:
        print('REJECTED: unable to read local input')
        return 2
    except ValueError as exc:
        print('REJECTED:', exc)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(s['state_supported'] for s in result['snapshots']) else 2


if __name__ == '__main__':
    raise SystemExit(main())
