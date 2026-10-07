"""Exact-v0.22 import proof for one immutable game-generated Rattata record."""
from __future__ import annotations
import hashlib
import struct
import pokemonstart_save_verifier as v
import pokemonstart_fl2_core as profile

SOURCE_SHA256 = '935f7bd8061f43569316239c2ab1bfcb7573fbc84601dffc823e0493bba38985'
TEMPLATE_SHA256 = '74d64c9dfbf4905bb0ca2abd7047d9834cb5b3bc8822cf95d538bba80da673f3'
ROM_SHA256 = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'


def derive(raw: bytes, record: bytes, rom_sha256: str) -> tuple[bytes, dict]:
    # Qualify the exact source and complete game-generated record before the
    # only write-capable construction path below is reached.
    profile._require_rom_hash(rom_sha256)
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('template import requires the exact immutable pre-acquisition save')
    if hashlib.sha256(record).hexdigest() != TEMPLATE_SHA256:
        raise ValueError('template import requires the exact game-generated Rattata record')
    report = v.verify_bytes(raw)
    if report.party_count != 4:
        raise ValueError('pre-acquisition Party count differs')
    base = report.slots[report.active_slot].section(1).physical_sector * v.SECTOR_SIZE
    count_offset = base + v.PARTY_COUNT_OFFSET
    dest = base + v.PARTY_OFFSET + 4 * 100
    output = bytearray(raw)
    output[count_offset] = 5
    output[dest:dest + 100] = record
    struct.pack_into('<H', output, base + v.SECTION_CHECKSUM_OFFSET,
                     v.calculate_save_checksum(output[base:base + v.SECTION_LENGTHS[1]]))
    candidate = bytes(output)
    after = v.verify_bytes(candidate)
    if after.party_count != 5 or candidate[dest:dest + 100] != record:
        raise ValueError('exact template import postcondition failed')
    allowed = {count_offset, *range(dest, dest + 100),
               base + v.SECTION_CHECKSUM_OFFSET, base + v.SECTION_CHECKSUM_OFFSET + 1}
    changed = [i for i, (a, b) in enumerate(zip(raw, candidate)) if a != b]
    if not set(changed) <= allowed:
        raise ValueError('exact template import byte envelope mismatch')
    receipt = {'transition': [4, 5], 'append_slot': 4,
               'record_sha256': hashlib.sha256(record).hexdigest(),
               'changed_offsets': changed, 'verifier_accepted': True,
               'unrelated_bytes_preserved': True}
    receipt.update({'source_sha256': SOURCE_SHA256, 'template_sha256': TEMPLATE_SHA256,
                    'candidate_sha256': hashlib.sha256(candidate).hexdigest(),
                    'operation': 'exact_game_generated_template_import'})
    return candidate, receipt
