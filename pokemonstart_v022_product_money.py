"""Candidate reusable exact-v0.22 key0 Money foundation (no save hash gate)."""
from __future__ import annotations
import struct
import pokemonstart_save_verifier as v
import pokemonstart_fl2_core as profile

MAX_MONEY = 9_999_999


def qualify(raw: bytes, rom_sha256: str):
    profile._require_rom_hash(rom_sha256)
    result = v.verify_bytes(raw)
    counters = []
    for slot in result.slots:
        if slot.state != 'valid' or slot.counter is None:
            raise ValueError('Money requires two valid save slots')
        if not 0 <= slot.counter <= 0x7FFFFFFE or slot.counter % 2 != slot.slot_index:
            raise ValueError('Money counter range/parity unsupported')
        counters.append(slot.counter)
        key = struct.unpack_from('<I', slot.section(0).data, 0xF20)[0]
        money = struct.unpack_from('<I', slot.section(1).data, 0x290)[0] ^ key
        if key != 0:
            raise ValueError('Money supports independently corroborated key0 only')
        if not 0 <= money <= MAX_MONEY:
            raise ValueError('decoded Money is outside 0..9,999,999')
    if abs(counters[0] - counters[1]) != 1:
        raise ValueError('Money requires consecutive counters')
    return result


def inspect(raw: bytes, rom_sha256: str):
    result = qualify(raw, rom_sha256)
    slot = result.slots[result.active_slot]
    return {'money': struct.unpack_from('<I', slot.section(1).data, 0x290)[0],
            'input_sha256': result.file_sha256, 'active_slot': result.active_slot,
            'counter': slot.counter, 'key': 0}


def derive(raw: bytes, rom_sha256: str, target: int):
    if type(target) is not int or not 0 <= target <= MAX_MONEY:
        raise ValueError('Money must be an integer in 0..9,999,999')
    before = inspect(raw, rom_sha256)
    if target == before['money']:
        raise ValueError('Money unchanged; no output')
    verified = qualify(raw, rom_sha256)
    section = verified.slots[verified.active_slot].section(1)
    base = section.physical_sector * v.SECTOR_SIZE
    output = bytearray(raw)
    struct.pack_into('<I', output, base + 0x290, target)
    struct.pack_into('<H', output, base + v.SECTION_CHECKSUM_OFFSET,
                     v.calculate_save_checksum(output[base:base+v.SECTION_LENGTHS[1]]))
    candidate = bytes(output)
    after = inspect(candidate, rom_sha256)
    offsets = [i for i,(a,b) in enumerate(zip(raw,candidate)) if a != b]
    allowed = set(range(base+0x290,base+0x294)) | {base+0xFF6,base+0xFF7}
    if not set(offsets) <= allowed or after['money'] != target:
        raise ValueError('Money postcondition/envelope failed')
    return candidate, {'input_sha256': before['input_sha256'],
                       'output_sha256': after['input_sha256'],
                       'money': {'from': before['money'], 'to': target},
                       'changed_offsets': offsets, 'verifier_accepted': True}
