"""Read-only E1 research model for the exact v0.22 ROM. No writer authority.

Catalog data is derived in memory from an owned ROM, never bundled. Storage
constants below describe the exact ROM, not the pinned upstream bag layout.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct

import pokemonstart_save_verifier as verifier

ROM_SHA256 = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'
ROM_BASE = 0x08000000
DESCRIPTOR = 0x09490E68
TABLE_POINTER = 0x080001C8
ITEM_TABLE = 0x095199C8
ITEM_COUNT = 839
ITEM_SIZE = 40
# name, RAM address, capacity, metadata pocket number
POCKETS = (
    ('regular', 0x0203BA98, 700, 1),
    ('key', 0x0203C588, 75, 2),
    ('balls', 0x0203C6D4, 50, 3),
    ('tmhm', 0x0203C79C, 128, 4),
    ('berries', 0x0203C99C, 72, 5),
)
FRAGMENTS = (
    (0x0203B0E8, 0xCC, 0, 0xF24),
    (0x0203B1B4, 0x258, 4, 0xD98),
    (0x0203B40C, 0xBA0, 13, 0x450),
    (0x0203BFAC, 0xFF0, None, 30 * 4096),
    (0x0203CF9C, 0xFF0, None, 31 * 4096),
)
# A proposed E2 policy only; metadata existence never grants write permission.
# These conventional recovery medicines still need E1 semantic closure.
PROPOSED_MEDICINES = frozenset(range(13, 23))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_name(encoded: bytes) -> str:
    """Decode the bounded Japanese item-name alphabet; reject controls/unknowns.

    Encoding corroborated with pinned CFRU-JP charmap.tbl. This is character
    conversion code, not a distributed ROM name table or copyrighted asset.
    """
    if 0xFF not in encoded:
        raise ValueError('unterminated item name')
    kana = (' あいうえおかきくけこさしすせそたちつてとなにぬねの'
            'はひふへほまみむめもやゆよらりるれろわをんぁぃぅぇぉゃゅょ'
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽっ'
            'アイウエオカキクケコサシスセソタチツテトナニヌネノ'
            'ハヒフヘホマミムメモヤユヨラリルレロワヲンァィゥェォャュョ'
            'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポッ')
    chars = dict(enumerate(kana))
    chars.update({0xA1 + i: c for i, c in enumerate('0123456789')})
    chars.update({0xBB + i: c for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')})
    chars.update({0xAB: '！', 0xAC: '？', 0xAD: '。', 0xAE: 'ー',
                  0xAF: '・', 0xB0: '…', 0xB5: '♂', 0xB6: '♀', 0xF1: 'ヴ'})
    try:
        name = ''.join(chars[c] for c in encoded[:encoded.index(0xFF)])
    except KeyError as exc:
        raise ValueError('unsupported item-name character') from exc
    if not name.strip() or set(name) <= {'？', '?', ' '}:
        raise ValueError('placeholder item name')
    return name


@dataclass(frozen=True)
class Item:
    item_id: int
    name: str
    pocket: int
    importance: int
    item_type: int
    proposed_ordinary: bool


def extract_catalog(rom: bytes) -> tuple[dict[int, Item], dict]:
    """Exact-profile gate and local read-only metadata extraction.

    Invalid entries are excluded, not replaced with upstream IDs or names.
    The summary contains hashes/counts only, not the proprietary item table.
    """
    if sha(rom) != ROM_SHA256:
        raise ValueError('unsupported exact ROM identity')
    if len(rom) != 0x2000000:
        raise ValueError('unsupported ROM size')
    descriptor = struct.unpack_from('<10I', rom, DESCRIPTOR - ROM_BASE)
    expected = tuple(x for _, ram, capacity, _ in POCKETS for x in (ram, capacity))
    if descriptor != expected:
        raise ValueError('exact pocket descriptor mismatch')
    if struct.unpack_from('<I', rom, TABLE_POINTER - ROM_BASE)[0] != ITEM_TABLE:
        raise ValueError('exact item-table pointer mismatch')
    catalog, excluded = {}, []
    table = rom[ITEM_TABLE - ROM_BASE:ITEM_TABLE - ROM_BASE + ITEM_COUNT * ITEM_SIZE]
    for item_id in range(ITEM_COUNT):
        record = table[item_id * ITEM_SIZE:(item_id + 1) * ITEM_SIZE]
        stored = struct.unpack_from('<H', record, 10)[0]
        importance, pocket, item_type = record[20], record[22], record[23]
        try:
            name = decode_name(record[:10])
            if item_id == 0 or stored != item_id or pocket not in range(1, 6) or importance not in (0, 1, 2):
                raise ValueError('invalid item metadata')
        except ValueError:
            excluded.append(item_id)
            continue
        catalog[item_id] = Item(item_id, name, pocket, importance, item_type,
                                item_id in PROPOSED_MEDICINES and pocket == 1 and importance == 0)
    return catalog, {'rom_sha256': sha(rom), 'table_sha256': sha(table),
                     'descriptor_sha256': sha(rom[DESCRIPTOR - ROM_BASE:DESCRIPTOR - ROM_BASE + 40]),
                     'entries': ITEM_COUNT, 'valid_entries': len(catalog), 'excluded_ids': excluded,
                     'proposed_ordinary_ids': sorted(i for i, item in catalog.items() if item.proposed_ordinary),
                     'writer_authorized': False, 'give_all_enabled': False}


def record_offset(active, ram: int) -> int:
    for start, length, section_id, offset in FRAGMENTS:
        if start <= ram and ram + 4 <= start + length:
            base = 0 if section_id is None else active.section(section_id).physical_sector * 4096
            return base + offset + ram - start
    raise ValueError('record outside serialized fragments')


def inspect(raw: bytes, rom: bytes) -> dict:
    """Audit all five pockets; preserve holes/order and report issues explicitly.

    Quantities are read under key0 only. Issues make state_supported false;
    results never become writer eligibility, even when no issues are found.
    Extra sectors are global, have no per-slot counter and are not checksum
    protected. Inspecting the inactive slot with them would mix save epochs.
    """
    catalog, catalog_summary = extract_catalog(rom)
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    # Bound this research decoder to the ordinary two-slot lineage also accepted
    # by the independent parser. Counter wrap and erased backups are unqualified.
    if (any(s.state != 'valid' or s.counter is None or not 0 <= s.counter < 0x7FFFFFFF
            or s.counter % 2 != s.slot_index for s in result.slots)
            or abs(result.slots[0].counter - result.slots[1].counter) != 1):
        raise ValueError('unsupported inventory save epoch')
    if not 1 <= len(result.party) <= 6:
        raise ValueError('unsupported inventory Party state')
    if struct.unpack_from('<I', active.section(0).data, 0xF20)[0] != 0:
        raise ValueError('inventory supports key0 only')
    # Exact bag initialization calls 0x090CDFCC, which substitutes a ten-slot
    # bag when signed RAM halfword 0x0203B672 is negative. Its gameplay meaning
    # is not assumed. Reject the branch rather than auditing the ordinary bag
    # as if it were the runtime-selected inventory.
    if struct.unpack_from('<h', active.section(13).data, 0x6B6)[0] < 0:
        raise ValueError('alternate runtime bag state unsupported')
    pockets, issues = [], []
    for name, ram, capacity, pocket_id in POCKETS:
        entries, empties, seen = [], [], set()
        for slot in range(capacity):
            offset = record_offset(active, ram + slot * 4)
            item_id, quantity = struct.unpack_from('<HH', raw, offset)
            if (item_id, quantity) == (0, 0):
                empties.append(slot)
                continue
            item = catalog.get(item_id)
            reason = None
            if item is None:
                reason = 'invalid/excluded item ID'
            elif item.pocket != pocket_id:
                reason = 'metadata pocket mismatch'
            elif not 1 <= quantity <= 999:
                reason = 'quantity outside key0 audit range 1..999'
            elif item_id in seen:
                reason = 'duplicate item ID'
            if reason:
                issues.append({'pocket': name, 'slot': slot, 'reason': reason})
            seen.add(item_id)
            entries.append({'slot': slot, 'item_id': item_id, 'quantity': quantity,
                            'name': None if item is None else item.name, 'offset': offset})
        last = max((e['slot'] for e in entries), default=-1)
        pockets.append({'name': name, 'capacity': capacity, 'entries': entries,
                        'occupied': len(entries), 'holes': [s for s in empties if s < last],
                        'first_empty': empties[0] if empties else None,
                        'checksum_covered': False})
    return {'input_sha256': sha(raw), 'active_slot': result.active_slot, 'counter': active.counter,
            'key': 0, 'catalog': catalog_summary, 'pockets': pockets, 'issues': issues,
            'state_supported': not issues, 'writer_authorized': False, 'give_all_enabled': False,
            'model_status': 'READ_ONLY_E1_RESEARCH', 'extra_sectors_epoch_authenticated': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--save', required=True, type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.save.read_bytes(), args.rom.read_bytes())
    except OSError:
        print('REJECTED: unable to read local input')
        return 2
    except ValueError as exc:
        print('REJECTED:', exc)
        return 2
    # CLI prints sanitized counts and findings, never filenames or raw records.
    for pocket in report['pockets']:
        pocket.pop('entries')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['state_supported'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
