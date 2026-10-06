"""Independent M5A money FAMILY auditor.

This module does not import pokemonstart_m5a_money_family. It independently
reconstructs editor bytes and the bounded post-editor normal-save envelope.
"""
from __future__ import annotations

import hashlib
import struct

import pokemonstart_save_verifier as v

MONEY_OFFSET = 0x290
KEY_OFFSET = 0xF20
ALLOWED_SECTION4_TAIL = {0xEDE, 0xEDF, 0xEE8, 0xEE9}
SAVE_BLOCK1_EVENT_OBJECTS_OFFSET = 0x6A0
EVENT_OBJECT_SIZE = 0x24
EVENT_OBJECT_COUNT = 16
EVENT_OBJECT_RUNTIME_FIELDS = (
    (0, 1), (0x10, 4), (0x14, 4), (0x18, 1), (0x1C, 1), (0x20, 1)
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _slot_hash(raw: bytes, slot: int) -> str:
    start = slot * 14 * 0x1000
    return _sha(raw[start : start + 14 * 0x1000])


def _money(raw: bytes) -> tuple[int, int]:
    result = v.verify_bytes(raw)
    active = result.slots[result.active_slot]
    key = struct.unpack_from("<I", active.section(0).data, KEY_OFFSET)[0]
    stored = struct.unpack_from("<I", active.section(1).data, MONEY_OFFSET)[0]
    return key, stored ^ key


def audit_editor_pair(source: bytes, output: bytes, target: int) -> dict:
    before = v.verify_bytes(source)
    after = v.verify_bytes(output)
    if (
        after.active_slot != before.active_slot
        or tuple(slot.counter for slot in after.slots)
        != tuple(slot.counter for slot in before.slots)
    ):
        raise AssertionError("slot/counter changed")
    active = before.slots[before.active_slot]
    key = struct.unpack_from("<I", active.section(0).data, KEY_OFFSET)[0]
    sec1 = active.section(1)
    base = sec1.physical_sector * v.SECTOR_SIZE
    expected = bytearray(source)
    struct.pack_into("<I", expected, base + MONEY_OFFSET, target ^ key)
    checksum = v.calculate_save_checksum(
        bytes(expected[base : base + v.SECTION_LENGTHS[1]])
    )
    struct.pack_into("<H", expected, base + v.SECTION_CHECKSUM_OFFSET, checksum)
    if bytes(expected) != output:
        raise AssertionError("output differs from independent construction")
    changed = [
        offset
        for offset, (left, right) in enumerate(zip(source, output))
        if left != right
    ]
    allowed = set(range(base + MONEY_OFFSET, base + MONEY_OFFSET + 4)) | {
        base + v.SECTION_CHECKSUM_OFFSET,
        base + v.SECTION_CHECKSUM_OFFSET + 1,
    }
    if not changed or not set(changed) <= allowed:
        raise AssertionError("unexpected editor diff")
    out_key, out_money = _money(output)
    if out_key != key or out_money != target:
        raise AssertionError("semantic target mismatch")
    return {
        "source_sha256": _sha(source),
        "output_sha256": _sha(output),
        "target_money": target,
        "changed_offsets": changed,
    }


def _volatile(section_id: int) -> set[int]:
    if section_id == 0:
        return set(range(0x0E, 0x13))
    if section_id == 1:
        return {
            SAVE_BLOCK1_EVENT_OBJECTS_OFFSET
            + index * EVENT_OBJECT_SIZE
            + field_offset
            + byte
            for index in range(EVENT_OBJECT_COUNT)
            for field_offset, size in EVENT_OBJECT_RUNTIME_FIELDS
            for byte in range(size)
        }
    if section_id == 2:
        return set(range(0x210, 0x214))
    return set()


def _stable_payload(result: v.VerificationResult) -> list[str]:
    active = result.slots[result.active_slot]
    hashes = []
    for section in active.sections:
        payload = bytearray(section.data[: v.SECTION_LENGTHS[section.section_id]])
        for offset in _volatile(section.section_id):
            payload[offset] = 0
        hashes.append(_sha(payload))
    return hashes


def _stable_tails(raw: bytes, result: v.VerificationResult) -> list[str]:
    active = result.slots[result.active_slot]
    hashes = []
    for section in active.sections:
        base = section.physical_sector * v.SECTOR_SIZE
        start = v.SECTION_LENGTHS[section.section_id]
        tail = bytearray(raw[base + start : base + v.SECTION_ID_OFFSET])
        if section.section_id == 4:
            for absolute in ALLOWED_SECTION4_TAIL:
                if start <= absolute < v.SECTION_ID_OFFSET:
                    tail[absolute - start] = 0
        hashes.append(_sha(tail))
    return hashes


def _party0(raw: bytes, result: v.VerificationResult) -> bytes:
    section = result.slots[result.active_slot].section(1)
    base = section.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return raw[base : base + v.POKEMON_SIZE]


def _metadata(result: v.VerificationResult) -> tuple[int, int]:
    active = result.slots[result.active_slot]
    data = active.section(0).data
    hours = int.from_bytes(data[0x0E:0x10], "little")
    play_time = hours * 3600 + data[0x10] * 60 + data[0x11]
    saved = int.from_bytes(active.section(2).data[0x210:0x214], "little")
    return play_time, saved


def audit_game_return(parent: bytes, returned: bytes) -> dict:
    p = v.verify_bytes(parent)
    c = v.verify_bytes(returned)
    old_slot = p.active_slot
    new_slot = c.active_slot
    if new_slot != 1 - old_slot:
        raise AssertionError("slot did not flip")
    if c.slots[new_slot].counter != ((p.slots[old_slot].counter + 1) & 0xFFFFFFFF):
        raise AssertionError("counter did not increment")
    if (
        c.slots[old_slot].counter != p.slots[old_slot].counter
        or _slot_hash(returned, old_slot) != _slot_hash(parent, old_slot)
    ):
        raise AssertionError("previous slot changed")
    if _money(parent) != _money(returned):
        raise AssertionError("money/key changed across normal save")
    if p.party_count != c.party_count or _party0(parent, p) != _party0(returned, c):
        raise AssertionError("party changed")
    if _stable_payload(p) != _stable_payload(c):
        raise AssertionError("stable payload changed")
    if _stable_tails(parent, p) != _stable_tails(returned, c):
        raise AssertionError("tail changed outside allowed offsets")
    p_time, p_saved = _metadata(p)
    c_time, c_saved = _metadata(c)
    if c_time < p_time or c_saved != ((p_saved + 1) & 0xFFFFFFFF):
        raise AssertionError("transition metadata invalid")
    for sector in range(28, 32):
        start = sector * v.SECTOR_SIZE
        if parent[start : start + v.SECTOR_SIZE] != returned[start : start + v.SECTOR_SIZE]:
            raise AssertionError("sector 28-31 changed")
    p_perm = [
        section.physical_sector % v.SLOT_SECTORS
        for section in p.slots[old_slot].sections
    ]
    c_perm = [
        section.physical_sector % v.SLOT_SECTORS
        for section in c.slots[new_slot].sections
    ]
    if c_perm != [(position + 1) % v.SLOT_SECTORS for position in p_perm]:
        raise AssertionError("unexpected section rotation")
    return {
        "parent_sha256": _sha(parent),
        "return_sha256": _sha(returned),
        "money": _money(returned)[1],
        "parent_slot_counter": [old_slot, p.slots[old_slot].counter],
        "return_slot_counter": [new_slot, c.slots[new_slot].counter],
        "footer_changed": p.footer != c.footer,
    }
