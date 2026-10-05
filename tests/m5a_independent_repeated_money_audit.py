#!/usr/bin/env python3
"""Independent sealed audit for the exact 9,999,999 -> 1,234,567 canary.

This implementation imports neither the proof writer nor the repository verifier.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

FLASH, SECTOR, SLOT_SECTORS = 0x20000, 0x1000, 14
SIGNATURE = 0x08012025
LENGTHS = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98, 0xFF0, 0xFF0, 0xFF0,
           0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0x450)
SOURCE_SHA = "1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4"
OUTPUT_SHA = "b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7"
DIFF = {0x03290: (0x7F, 0x87), 0x03291: (0x96, 0xD6), 0x03292: (0x98, 0x12),
        0x03FF6: (0xA7, 0x29), 0x03FF7: (0xA7, 0xE7)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def checksum(data):
    total = sum(u32(data, off) for off in range(0, len(data), 4)) & 0xFFFFFFFF
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def parse_slot(raw, slot):
    base_sector = slot * SLOT_SECTORS
    sectors = [raw[(base_sector + i) * SECTOR:(base_sector + i + 1) * SECTOR]
               for i in range(SLOT_SECTORS)]
    if all(s == b"\xff" * SECTOR for s in sectors):
        return {"state": "empty", "raw": b""}
    assert not any(s == b"\xff" * SECTOR for s in sectors), "partial erased slot"
    by_id, order, counters = {}, [], set()
    for sec in sectors:
        sid = u16(sec, 0xFF4)
        assert 0 <= sid < 14 and sid not in by_id, "invalid or duplicate section ID"
        assert u32(sec, 0xFF8) == SIGNATURE, "bad section signature"
        assert u16(sec, 0xFF6) == checksum(sec[:LENGTHS[sid]]), "bad section checksum"
        by_id[sid] = sec
        order.append(sid)
        counters.add(u32(sec, 0xFFC))
    assert set(by_id) == set(range(14)) and len(counters) == 1, "invalid IDs/counters"
    start = slot * SLOT_SECTORS * SECTOR
    return {"state": "valid", "counter": counters.pop(), "by_id": by_id,
            "order": order, "raw": raw[start:start + SLOT_SECTORS * SECTOR]}


def audit(source_path, output_path):
    src, out = Path(source_path).read_bytes(), Path(output_path).read_bytes()
    assert len(src) == len(out) == 0x20010, "unsupported supported-layout size"
    assert sha(src) == SOURCE_SHA, "wrong source hash"
    assert sha(out) == OUTPUT_SHA, "wrong output hash"
    diffs = {i: (a, b) for i, (a, b) in enumerate(zip(src, out)) if a != b}
    assert diffs == DIFF, f"unexplained complete diff: {diffs!r}"

    before = [parse_slot(src, i) for i in range(2)]
    after = [parse_slot(out, i) for i in range(2)]
    active = 0
    assert before[active]["state"] == after[active]["state"] == "valid"
    assert before[active]["counter"] == after[active]["counter"] == 2
    assert before[1]["state"] == after[1]["state"] == "valid"
    assert before[1]["raw"] == after[1]["raw"], "inactive slot changed"
    assert before[active]["order"] == after[active]["order"], "section permutation changed"
    for sid in range(14):
        a, b = before[active]["by_id"][sid], after[active]["by_id"][sid]
        assert a[0xFF4:0xFF6] == b[0xFF4:0xFF6], f"section {sid} ID changed"
        assert a[0xFF8:] == b[0xFF8:], f"section {sid} signature/counter changed"
        if sid != 1:
            assert a[0xFF6:0xFF8] == b[0xFF6:0xFF8], f"section {sid} checksum changed"
        assert a[LENGTHS[sid]:0xFF4] == b[LENGTHS[sid]:0xFF4], f"section {sid} tail changed"
    sec0, sec1 = before[active]["by_id"][0], before[active]["by_id"][1]
    key = u32(sec0, 0xF20)
    assert key == u32(after[active]["by_id"][0], 0xF20), "encryption key changed"
    starting = u32(sec1, 0x290) ^ key
    ending = u32(after[active]["by_id"][1], 0x290) ^ key
    assert starting == 9_999_999 and ending == 1_234_567, "decoded money mismatch"
    party_offset, party_size = 0x38, 100
    assert sec1[party_offset:party_offset + party_size] == after[active]["by_id"][1][party_offset:party_offset + party_size], "party data changed"
    assert src[28 * SECTOR:32 * SECTOR] == out[28 * SECTOR:32 * SECTOR], "sectors 28-31 changed"
    assert src[FLASH:] == out[FLASH:], "footer changed"
    return {"status": "PASS", "source_sha256": SOURCE_SHA, "output_sha256": OUTPUT_SHA,
            "money_before": starting, "money_after": ending, "key": key,
            "active_slot": active, "counter": 2,
            "changed_offsets": [f"0x{x:05X}" for x in sorted(diffs)],
            "section_signatures_checksums": "PASS", "inactive_slot": "byte-identical",
            "section_permutation_metadata": "preserved", "checksum_excluded_tails": "byte-identical",
            "party_data": "byte-identical", "sectors_28_31": "byte-identical", "footer": "byte-identical"}


if __name__ == "__main__":
    print(json.dumps(audit(sys.argv[1], sys.argv[2]), indent=2, sort_keys=True))
