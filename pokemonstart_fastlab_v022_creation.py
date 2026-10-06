"""Exact-input Party append experiment; no synthesized record or reuse gate."""
from __future__ import annotations

import struct

import pokemonstart_fl2_core as fl2
import pokemonstart_fastlab_v022_party_editor as party
import pokemonstart_save_verifier as verifier
import pokemonstart_v022_creation_audit as audit

PARTY_SOURCE_SHA256 = '2d7ac8d6214e8b94018a3fe3f65c30270198098a9cb658318248b514242511ac'
INVENTORY_SOURCE_SHA256 = PARTY_SOURCE_SHA256
PARTY_OUTPUT_SHA256 = 'e22309a73236504d201d393f8146f113eb261d2486527c66ca0fd8e8f4bf2a5b'
INVENTORY_OUTPUT_SHA256 = '588b4cb5b96468cd2baf4d67c36f4048020f5205fa28ff57c3a094147409c596'
CREATION_OPERATIONS = ('party_append', 'inventory_insert')
OPERATIONS = fl2.OPERATIONS + CREATION_OPERATIONS


def append_party(raw: bytes, rom_sha256: str) -> tuple[bytes, dict]:
    fl2._require_rom_hash(rom_sha256)
    if fl2.sha(raw) != PARTY_SOURCE_SHA256:
        raise ValueError('Party append requires the exact fresh proof root')
    before = verifier.verify_bytes(raw)
    active = before.slots[before.active_slot]
    if before.party_count != 3 or any(
            struct.unpack_from('<I', s.section(0).data, 0xF20)[0] != 0
            for s in before.slots):
        raise ValueError('unsupported count/key')
    section = active.section(1)
    start = section.physical_sector * verifier.SECTOR_SIZE
    template = section.data[0x38:0x38 + 100]
    dest = start + verifier.PARTY_OFFSET + before.party_count * 100
    output = bytearray(raw)
    output[start + verifier.PARTY_COUNT_OFFSET] = 4
    output[dest:dest + 100] = template
    checksum = verifier.calculate_save_checksum(output[start:start + verifier.SECTION_LENGTHS[1]])
    struct.pack_into('<H', output, start + verifier.SECTION_CHECKSUM_OFFSET, checksum)
    candidate = bytes(output)
    after = verifier.verify_bytes(candidate)
    if after.party_count != 4:
        raise ValueError('count verification')
    allowed = {start + 0x34, *range(dest, dest + 100), start + 0xFF6, start + 0xFF7}
    diffs = fl2._byte_diffs(raw, candidate)
    if any(d['offset'] not in allowed for d in diffs):
        raise ValueError('append envelope violation')
    return candidate, dict(source_sha256=fl2.sha(raw), output_sha256=fl2.sha(candidate),
                          operation='party_append', party_count=[3, 4],
                          template_slot=0, append_slot=3, changed_byte_count=len(diffs),
                          changed_offsets=[d['offset'] for d in diffs],
                          repository_verifier_accepted=True)


def insert_inventory(raw: bytes, rom_sha256: str) -> tuple[bytes, dict]:
    """Only the observed root -> slot2 Antidote x1 shape; no shop charge."""
    fl2._require_rom_hash(rom_sha256)
    if fl2.sha(raw) != INVENTORY_SOURCE_SHA256:
        raise ValueError('Inventory insertion requires the exact pre-purchase proof root')
    before = verifier.verify_bytes(raw)
    active = before.slots[before.active_slot]
    if any(struct.unpack_from('<I', s.section(0).data, 0xF20)[0] != 0
           for s in before.slots):
        raise ValueError('unsupported Inventory key')
    section = active.section(13)
    if struct.unpack_from('<HHHH', section.data, 0xADC) != (13, 2, 533, 1):
        raise ValueError('existing Inventory records differ from proof')
    offset = 0xAE4
    if any(section.data[offset:]) or offset < verifier.SECTION_LENGTHS[13]:
        raise ValueError('unsupported observed empty slot/tail/checksum envelope')
    start = section.physical_sector * verifier.SECTOR_SIZE + offset
    output = bytearray(raw)
    struct.pack_into('<HH', output, start, 14, 1)
    candidate = bytes(output)
    verifier.verify_bytes(candidate)
    diffs = fl2._byte_diffs(raw, candidate)
    if [d['offset'] for d in diffs] != [start, start + 2]:
        raise ValueError('Inventory insertion envelope violation')
    return candidate, dict(source_sha256=fl2.sha(raw), output_sha256=fl2.sha(candidate),
                          operation='inventory_insert', item_id=14, slot=2, quantity=1,
                          changed_byte_count=len(diffs), changed_offsets=[start, start + 2],
                          checksum_changed=False, money_preserved=True,
                          repository_verifier_accepted=True)


def inspect_bytes(raw: bytes, rom_sha256: str) -> dict:
    """Read-only v0.22 inspection; existing FL2 gates remain authoritative."""
    report = fl2.inspect_bytes(raw, rom_sha256)
    result = verifier.verify_bytes(raw)
    report['semantics']['money'] = fl2._money_semantic(raw)
    report['semantics']['party'] = party.inspect_bytes(raw)['party'] if result.party else []
    for operation, seal in (('party_append', PARTY_SOURCE_SHA256),
                            ('inventory_insert', INVENTORY_SOURCE_SHA256)):
        report['capabilities'][operation] = dict(
            write_supported=report['save_sha256'] == seal,
            request={}, scope='Fast Lab experimental; exact creation proof root only')
    if report['capabilities']['inventory']['write_supported']:
        report['semantics']['regular_items']=dict(status='canonical bounded Potion pocket',
                                                 entries=report['semantics']['inventory'])
    elif report['save_sha256'] in {PARTY_SOURCE_SHA256, PARTY_OUTPUT_SHA256, INVENTORY_OUTPUT_SHA256}:
        section=result.slots[result.active_slot].section(13)
        entries=[]
        for slot in range(3):
            item,qty=struct.unpack_from('<HH',section.data,0xADC+slot*4)
            if item: entries.append(dict(slot=slot,item_id=item,quantity=qty))
        report['semantics']['regular_items']=dict(status='observed bounded prefix',entries=entries)
    else:
        report['semantics']['regular_items']=dict(status='unsupported pocket inspection for this input')
    report['supported_write_operations']=[op for op in OPERATIONS
                                          if report['capabilities'][op]['write_supported']]
    report['status']='SUPPORTED' if report['supported_write_operations'] else 'READ_ONLY_UNSUPPORTED_WRITES'
    return report


def derive_bytes(raw: bytes, rom_sha256: str, operation: str, changes: dict) -> tuple[bytes, dict]:
    """In-memory transaction shared by GUI and non-GUI callers."""
    request=fl2._require_mapping(changes)
    if operation in fl2.OPERATIONS:
        return fl2._preview_bytes(raw,rom_sha256,operation,request)
    if operation not in CREATION_OPERATIONS or request:
        raise ValueError('creation requires one exact operation with an empty request object')
    if operation=='party_append':
        candidate,report=append_party(raw,rom_sha256)
        receipt=audit.audit_append(raw,candidate)
        semantic=dict(party_count=[3,4],template_slot=0,append_slot=3,
                      complete_100_byte_record_copied=True)
    else:
        candidate,report=insert_inventory(raw,rom_sha256)
        receipt=audit.audit_insert(raw,candidate)
        semantic=dict(slot=2,item_id=14,item='Antidote',quantity=[0,1],money_unchanged=True)
    report.update(status='PREVIEW',evidence_class='Fast Lab experimental',request=request,
                  rom_sha256=rom_sha256,semantic_diff=semantic,
                  byte_diffs=fl2._byte_diffs(raw,candidate),
                  independent_audit=receipt,source_write_performed=False)
    return candidate,report
