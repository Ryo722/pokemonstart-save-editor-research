"""Independent exact-v0.22 key0 Money parser/auditor; no writer/verifier imports.

Only hashes, structural facts and diff offsets are returned, never private bytes.
"""
from __future__ import annotations

import hashlib
import struct

LENGTHS = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98,
           0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0x450)
TARGET = 7_654_321


def checksum(payload: bytes) -> int:
    total = sum(word[0] for word in struct.iter_unpack('<I', payload)) & 0xFFFFFFFF
    return ((total & 0xFFFF) + (total >> 16)) & 0xFFFF


def parse(raw: bytes) -> dict:
    if len(raw) not in (0x20000, 0x20010):
        raise ValueError('unsupported size')
    slots = []
    for slot in range(2):
        sections = {}
        counters = set()
        for physical in range(slot * 14, (slot + 1) * 14):
            base = physical * 0x1000
            sector = raw[base:base + 0x1000]
            logical, covered, signature, counter = struct.unpack_from('<HHII', sector, 0xFF4)
            if logical >= 14 or logical in sections:
                raise ValueError('invalid/duplicate logical section')
            if signature != 0x08012025 or checksum(sector[:LENGTHS[logical]]) != covered:
                raise ValueError('signature/checksum invalid')
            sections[logical] = base
            counters.add(counter)
        if set(sections) != set(range(14)) or len(counters) != 1:
            raise ValueError('section/counter ambiguity')
        counter = counters.pop()
        if not 0 <= counter <= 0x7FFFFFFE or counter % 2 != slot:
            raise ValueError('counter range/parity unsupported')
        key = struct.unpack_from('<I', raw, sections[0] + 0xF20)[0]
        money = struct.unpack_from('<I', raw, sections[1] + 0x290)[0] ^ key
        count = raw[sections[1] + 0x34]
        if key != 0 or not 0 <= money <= 9_999_999:
            raise ValueError('key/Money unsupported')
        if count > 6 or 0x38 + count * 100 > LENGTHS[1]:
            raise ValueError('party bounds unsupported')
        slots.append(dict(counter=counter, sections=sections, key=key,
                          money=money, party_count=count))
    if abs(slots[0]['counter'] - slots[1]['counter']) != 1:
        raise ValueError('counters must be consecutive')
    active = int(slots[1]['counter'] > slots[0]['counter'])
    return dict(sha256=hashlib.sha256(raw).hexdigest(), size=len(raw),
                active_slot=active, slots=slots)


def audit(before: bytes, after: bytes) -> dict:
    left, right = parse(before), parse(after)
    active = left['active_slot']
    base = left['slots'][active]['sections'][1]
    expected = bytearray(before)
    struct.pack_into('<I', expected, base + 0x290, TARGET)
    struct.pack_into('<H', expected, base + 0xFF6,
                     checksum(bytes(expected[base:base + 0xFF0])))
    if left['slots'][active]['money'] == TARGET:
        raise ValueError('noop rejected')
    if after != bytes(expected):
        raise ValueError('output differs from independently computed candidate')
    offsets = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    allowed = set(range(base + 0x290, base + 0x294)) | {base + 0xFF6, base + 0xFF7}
    if not offsets or not set(offsets) <= allowed or right['active_slot'] != active:
        raise ValueError('diff/active invariant failed')
    for a, b in zip(left['slots'], right['slots']):
        for field in ('counter', 'sections', 'key', 'party_count'):
            if a[field] != b[field]:
                raise ValueError('slot metadata changed')
    if right['slots'][active]['money'] != TARGET:
        raise ValueError('target not confirmed')
    return dict(input_sha256=left['sha256'], output_sha256=right['sha256'],
                active_slot=active, counter=left['slots'][active]['counter'],
                source_money=left['slots'][active]['money'], target_money=TARGET,
                changed_offsets=offsets, all_outside_envelope_preserved=True,
                signatures_checksums_sections_valid=True)


def audit_resave(before: bytes, after: bytes, expected_money: int) -> dict:
    """Audit a separately observed normal SAVE; metadata alone is not live proof."""
    left, right = parse(before), parse(after)
    old, new = left['active_slot'], right['active_slot']
    if len(before) != len(after) or new != 1 - old:
        raise ValueError('normal SAVE slot/length transition failed')
    if right['slots'][new]['counter'] != left['slots'][old]['counter'] + 1:
        raise ValueError('normal SAVE counter must advance exactly once')
    start, end = old * 14 * 4096, (old + 1) * 14 * 4096
    if before[start:end] != after[start:end]:
        raise ValueError('previous active slot was not retained')
    rotation = {}
    for logical in range(14):
        prior = left['slots'][old]['sections'][logical] // 4096 % 14
        current = right['slots'][new]['sections'][logical] // 4096 % 14
        if current != (prior + 1) % 14:
            raise ValueError('normal SAVE section rotation mismatch')
        rotation[logical] = [prior, current]
    if right['slots'][new]['money'] != expected_money:
        raise ValueError('normal SAVE Money mismatch')
    return dict(input_sha256=left['sha256'], output_sha256=right['sha256'],
                old_slot=old, new_slot=new, old_counter=left['slots'][old]['counter'],
                new_counter=right['slots'][new]['counter'], money=expected_money,
                previous_active_slot_preserved=True, section_rotation=rotation,
                extra_sectors_equal=before[28 * 4096:0x20000] == after[28 * 4096:0x20000],
                footer_equal=before[0x20000:] == after[0x20000:])
