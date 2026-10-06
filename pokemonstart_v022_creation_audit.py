"""Independent stdlib audit for the bounded v0.22 creation experiments.

No product writer/verifier imports. Reports hashes and offsets, never records.
"""
from __future__ import annotations

import hashlib
import struct

LENGTHS = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98, *([0xFF0] * 8), 0x450)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def checksum(payload: bytes) -> int:
    total = sum(struct.unpack('<' + 'I' * (len(payload) // 4), payload)) & 0xFFFFFFFF
    return ((total >> 16) + (total & 65535)) & 65535


def parse(raw: bytes) -> dict:
    if len(raw) not in (0x20000, 0x20010):
        raise ValueError('size')
    slots = []
    for number in range(2):
        sections, positions, counters = {}, {}, set()
        for local in range(14):
            physical = number * 14 + local
            sector = raw[physical * 4096:(physical + 1) * 4096]
            sid, stored, signature, counter = struct.unpack_from('<HHII', sector, 0xFF4)
            if sid not in range(14) or sid in sections or signature != 0x08012025:
                raise ValueError('section metadata')
            if stored != checksum(sector[:LENGTHS[sid]]):
                raise ValueError('checksum')
            sections[sid], positions[sid] = sector, physical
            counters.add(counter)
        if len(counters) != 1:
            raise ValueError('mixed counters')
        counter = counters.pop()
        if not 0 <= counter < 0x7FFFFFFF or counter % 2 != number:
            raise ValueError('ordinary counter/parity')
        slots.append(dict(sections=sections, positions=positions, counter=counter))
    if abs(slots[0]['counter'] - slots[1]['counter']) != 1:
        raise ValueError('consecutive counters')
    active = max(range(2), key=lambda n: slots[n]['counter'])
    block = slots[active]['sections'][1]
    count = block[0x34]
    if not 1 <= count <= 6:
        raise ValueError('party count')
    key = struct.unpack_from('<I', slots[active]['sections'][0], 0xF20)[0]
    return dict(slots=slots, active=active, count=count, key=key,
                money=struct.unpack_from('<I', block, 0x290)[0] ^ key,
                records=[block[0x38 + i * 100:0x38 + (i + 1) * 100] for i in range(count)])


def summary(raw: bytes) -> dict:
    p = parse(raw)
    return dict(sha256=sha(raw), size=len(raw), footer_size=len(raw) - 0x20000,
                footer_sha256=sha(raw[0x20000:]), active_slot=p['active'],
                counters=[s['counter'] for s in p['slots']],
                section_mapping=[s['positions'] for s in p['slots']],
                key=p['key'], money=p['money'], party_count=p['count'],
                party_record_sha256=[sha(r) for r in p['records']])


def independent_append(raw: bytes) -> bytes:
    p = parse(raw)
    if p['key'] != 0 or p['count'] == 6:
        raise ValueError('key/count unsupported')
    start = p['slots'][p['active']]['positions'][1] * 4096
    dest = start + 0x38 + p['count'] * 100
    # Occupancy is determined by the count. Unoccupied storage may retain
    # stale bytes; the exact input hash gates this bounded overwrite.
    output = bytearray(raw)
    output[start + 0x34] += 1
    output[dest:dest + 100] = p['records'][0]
    struct.pack_into('<H', output, start + 0xFF6, checksum(output[start:start + 0xFF0]))
    return bytes(output)


def audit_append(before: bytes, after: bytes) -> dict:
    if after != independent_append(before):
        raise ValueError('complete independent candidate inequality')
    p, q = parse(before), parse(after)
    if q['records'] != p['records'] + [p['records'][0]]:
        raise ValueError('party records')
    changes = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    start = p['slots'][p['active']]['positions'][1] * 4096
    return dict(source_sha256=sha(before), output_sha256=sha(after),
                transition=[p['count'], q['count']], template_slot=0, append_slot=p['count'],
                changed_offsets=changes, changed_byte_count=len(changes),
                count_offset=start + 0x34,
                new_record_interval=[start + 0x38 + p['count'] * 100,
                                     start + 0x38 + (p['count'] + 1) * 100],
                checksum_interval=[start + 0xFF6, start + 0xFF8],
                complete_candidate_equality=True)


def normal_save(before: bytes, after: bytes) -> dict:
    p, q = parse(before), parse(after)
    old, new = p['slots'][p['active']], q['slots'][q['active']]
    if q['active'] != 1 - p['active'] or new['counter'] != old['counter'] + 1:
        raise ValueError('normal-save slot/counter')
    start = p['active'] * 14 * 4096
    if before[start:start + 14 * 4096] != after[start:start + 14 * 4096]:
        raise ValueError('old slot modified')
    if any(new['positions'][i] % 14 != (old['positions'][i] + 1) % 14 for i in range(14)):
        raise ValueError('rotation')
    if p['records'] != q['records'] or p['count'] != q['count']:
        raise ValueError('party persistence')
    if p['money'] != q['money'] or p['key'] != q['key']:
        raise ValueError('money/key persistence')
    if old['sections'][13][0xADC:0xFF4] != new['sections'][13][0xADC:0xFF4]:
        raise ValueError('regular-items persistence')
    old_saved=struct.unpack_from('<I',old['sections'][2],0x210)[0]
    new_saved=struct.unpack_from('<I',new['sections'][2],0x210)[0]
    if new_saved != (old_saved+1)&0xFFFFFFFF:
        raise ValueError('saved-game statistic did not increment once')
    changes = {}
    for sid in range(14):
        changes[sid] = [i for i, (x, y) in enumerate(zip(old['sections'][sid][:0xFF4],
                                                       new['sections'][sid][:0xFF4])) if x != y]
    classes = {}
    for sid, offsets in changes.items():
        for offset in offsets:
            if sid == 0 and 0x0E <= offset < 0x13:
                label = 'play_time'
            elif sid == 1 and 0x6A0 <= offset < 0x8E0:
                label = 'event_objects'
            elif sid == 1 and 0x8E0 <= offset < 0xEE0:
                label = 'event_object_templates'
            elif sid == 2 and 0x210 <= offset < 0x214:
                label = 'saved_game_count'
            else:
                label = 'unclassified'
            classes.setdefault(label, []).append([sid, offset])
    if before[28 * 4096:30 * 4096] != after[28 * 4096:30 * 4096]:
        raise ValueError('sectors 28/29 changed')
    extended = {}
    for sector in (30, 31):
        left, right = before[sector*4096:(sector+1)*4096], after[sector*4096:(sector+1)*4096]
        offsets = [i for i,(x,y) in enumerate(zip(left,right)) if x!=y]
        extended[sector] = dict(before_sha256=sha(left), after_sha256=sha(right),
                                changed_offsets=offsets,
                                classification='CFRU extended save; field semantics unqualified')
    return dict(source_sha256=sha(before), returned_sha256=sha(after),
                slot_transition=[p['active'], q['active']],
                counter_transition=[old['counter'], new['counter']],
                rotation_plus_one=True, original_slot_preserved=True,
                all_party_records_persist=True, money_preserved=True,
                regular_items_preserved=True,saved_game_statistic=[old_saved,new_saved],
                logical_change_classes=classes,
                extended_sectors=extended,
                logical_changed_offsets={sid:offsets for sid,offsets in changes.items() if offsets},
                footer_changed_offsets=[i for i,(x,y) in enumerate(zip(before[0x20000:],after[0x20000:])) if x!=y])


def acquisition_diff(before: bytes, after: bytes) -> dict:
    """Independently require the one observed Antidote purchase, including cost."""
    p, q = parse(before), parse(after)
    old, new = p['slots'][p['active']], q['slots'][q['active']]
    if q['active'] != 1-p['active'] or new['counter'] != old['counter']+1:
        raise ValueError('purchase save slot/counter')
    start=p['active']*14*4096
    if before[start:start+14*4096] != after[start:start+14*4096]:
        raise ValueError('purchase old slot not retained')
    if any(new['positions'][i]%14 != (old['positions'][i]+1)%14 for i in range(14)):
        raise ValueError('purchase rotation')
    if p['key'] != 0 or q['key'] != 0 or q['money'] != p['money']-200:
        raise ValueError('purchase key/cost')
    if p['records'] != q['records']:
        raise ValueError('purchase party changed')
    left,right=old['sections'][13],new['sections'][13]
    offset=0xAE4
    if any(left[offset:offset+4]) or struct.unpack_from('<HH',right,offset)!=(14,1):
        raise ValueError('observed slot2 insertion mismatch')
    if left[0xADC:offset]!=right[0xADC:offset] or left[offset+4:0xFF4]!=right[offset+4:0xFF4]:
        raise ValueError('existing item/order or remaining tail changed')
    changes={sid:[i for i,(x,y) in enumerate(zip(old['sections'][sid][:0xFF4],
                                                new['sections'][sid][:0xFF4])) if x!=y]
             for sid in range(14)}
    return dict(pre_sha256=sha(before),post_sha256=sha(after),
                counter_transition=[old['counter'],new['counter']],
                slot_transition=[p['active'],q['active']],rotation_plus_one=True,
                money_transition=[p['money'],q['money']],purchase_cost=200,
                item_id=14,quantity=1,slot=2,section_id=13,section_offset=offset,
                key=0,checksum_covered=False,existing_items_preserved=True,
                party_records_preserved=True,
                extended_sector_changed_offsets={sector:[i for i,(x,y) in enumerate(zip(
                    before[sector*4096:(sector+1)*4096],after[sector*4096:(sector+1)*4096])) if x!=y]
                    for sector in range(28,32)},
                footer_changed_offsets=[i for i,(x,y) in enumerate(zip(before[0x20000:],after[0x20000:])) if x!=y],
                logical_changed_offsets={sid:offs for sid,offs in changes.items() if offs})


def independent_insert(raw: bytes) -> bytes:
    p=parse(raw)
    if p['key'] != 0:
        raise ValueError('insertion key')
    offset=p['slots'][p['active']]['positions'][13]*4096+0xAE4
    if any(raw[offset:offset+4]):
        raise ValueError('insertion destination occupied')
    out=bytearray(raw)
    struct.pack_into('<HH',out,offset,14,1)
    return bytes(out)


def audit_insert(before: bytes, after: bytes) -> dict:
    if independent_insert(before)!=after:
        raise ValueError('complete insertion candidate inequality')
    p,q=parse(before),parse(after)
    if p['money']!=q['money'] or p['records']!=q['records']:
        raise ValueError('insertion unrelated changes')
    return dict(source_sha256=sha(before),output_sha256=sha(after),
                item_id=14,slot=2,quantity=1,
                changed_offsets=[i for i,(x,y) in enumerate(zip(before,after)) if x!=y],
                checksum_changed=False,money_preserved=True,party_preserved=True,
                complete_candidate_equality=True)


def independent_composed(raw: bytes) -> bytes:
    """Direct construction independent of both product and primitive writers."""
    p = parse(raw)
    active = p['slots'][p['active']]
    if p['count'] != 3 or p['money'] != 3032 or any(
            struct.unpack_from('<I', slot['sections'][0], 0xF20)[0] for slot in p['slots']):
        raise ValueError('composed source count/Money/key')
    inventory = active['sections'][13]
    if struct.unpack_from('<HHHH', inventory, 0xADC) != (13, 2, 533, 1) or any(inventory[0xAE4:0xFF4]):
        raise ValueError('composed source Inventory shape')
    start = active['positions'][1] * 4096
    item = active['positions'][13] * 4096 + 0xAE4
    out = bytearray(raw)
    out[start + 0x34] = 4
    out[start + 0x164:start + 0x1C8] = p['records'][0]
    struct.pack_into('<HH', out, item, 14, 1)
    struct.pack_into('<H', out, start + 0xFF6, checksum(out[start:start + 0xFF0]))
    return bytes(out)


def audit_composed(before: bytes, after: bytes) -> dict:
    expected = independent_composed(before)
    if after != expected:
        raise ValueError('complete composed candidate inequality')
    party, items = independent_append(before), independent_insert(before)
    party_offsets = {i for i, (a, b) in enumerate(zip(before, party)) if a != b}
    item_offsets = {i for i, (a, b) in enumerate(zip(before, items)) if a != b}
    changes = {i for i, (a, b) in enumerate(zip(before, after)) if a != b}
    if changes != party_offsets | item_offsets:
        raise ValueError('composed offset union mismatch')
    if independent_insert(party) != expected or independent_append(items) != expected:
        raise ValueError('complete composed order inequality')
    p, q = parse(before), parse(after)
    if q['count'] != 4 or q['records'] != p['records'] + [p['records'][0]]:
        raise ValueError('composed Party preservation')
    old = p['slots'][p['active']]['sections'][13]
    new = q['slots'][q['active']]['sections'][13]
    if struct.unpack_from('<HHHHHH', new, 0xADC) != (13,2,533,1,14,1) or old[0xAE8:0xFF4] != new[0xAE8:0xFF4]:
        raise ValueError('composed Inventory preservation')
    if q['money'] != 3032 or q['key'] != 0:
        raise ValueError('composed Money/key preservation')
    return dict(source_sha256=sha(before),output_sha256=sha(after),
                changed_offsets=sorted(changes),changed_byte_count=len(changes),
                party_changed_offsets=sorted(party_offsets),inventory_changed_offsets=sorted(item_offsets),
                offset_union_equality=True,complete_candidate_equality=True,
                complete_byte_order_independence=True,party_count=[3,4],
                original_party_records_preserved=True,slot3_equals_complete_slot0=True,
                existing_items_order_preserved=True,remaining_inventory_tail_preserved=True,
                money=3032,key=0,footer_counters_inactive_slot_unrelated_bytes_preserved=True)


def composed_normal_save(root: bytes, candidate: bytes, returned: bytes) -> dict:
    """Audit this round trip, reporting metadata and opaque changes as well."""
    audit_composed(root, candidate)
    if len(candidate) != len(returned):
        raise ValueError('normal-save container size changed')
    receipt = normal_save(candidate, returned)
    p, q = parse(candidate), parse(returned)
    old, new = p['slots'][p['active']], q['slots'][q['active']]
    receipt.update(key_preserved=True, party_count=4, money=3032, key=0,
                   section_mapping_before=old['positions'],section_mapping_after=new['positions'],
                   logical_metadata_changed_offsets={sid:[i for i in range(0xFF4,0x1000)
                       if old['sections'][sid][i] != new['sections'][sid][i]] for sid in range(14)},
                   physical_changed_byte_count=sum(a != b for a,b in zip(candidate,returned)),
                   footer_classification='opaque emulator footer; field semantics unqualified',
                   extended_sectors_28_29_preserved=True,
                   non_claim='one observed normal SAVE; no reusable volatility predicate')
    return receipt
