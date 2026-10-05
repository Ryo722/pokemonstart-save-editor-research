"""Stdlib-only independent A -> B markings audit; prints hashes and small diffs.

Usage: python3 tests/m4_independent_markings_audit.py A [B]
With only A, derive the expected B digest without writing a file.
"""
import hashlib
import sys
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def u16(data, offset):
    return int.from_bytes(data[offset:offset + 2], "little")


def u32(data, offset):
    return int.from_bytes(data[offset:offset + 4], "little")


def expected(source):
    if len(source) != 131088:
        raise ValueError("unexpected save length")
    slot_counters = []
    for slot in (0, 1):
        counters = {u32(source, (slot * 14 + sector) * 4096 + 0xFFC)
                    for sector in range(14)}
        if len(counters) != 1:
            raise ValueError("mixed slot counters")
        slot_counters.append(counters.pop())
    active = 0 if slot_counters[0] > slot_counters[1] else 1
    if active != slot_counters[active] % 2:
        raise ValueError("active slot parity mismatch")
    sector_ids = [u16(source, (active * 14 + sector) * 4096 + 0xFF4)
                  for sector in range(14)]
    if sorted(sector_ids) != list(range(14)):
        raise ValueError("invalid section permutation")
    physical = active * 14 + sector_ids.index(1)
    base = physical * 4096
    mark = base + 0x38 + 27
    if source[mark] != 1:
        raise ValueError("markings source is not 1")
    out = bytearray(source)
    out[mark] = 0
    # Pinned section-1 payload length is 0xFF0. Sum little-endian u32 words.
    payload = out[base:base + 0xFF0]
    total = sum(int.from_bytes(payload[i:i + 4], "little")
                for i in range(0, len(payload), 4)) & 0xFFFFFFFF
    checksum = ((total >> 16) + (total & 0xFFFF)) & 0xFFFF
    out[base + 0xFF6:base + 0xFF8] = checksum.to_bytes(2, "little")
    diffs = [(i, old, new) for i, (old, new) in enumerate(zip(source, out)) if old != new]
    if {offset for offset, _, _ in diffs} - {mark, base + 0xFF6, base + 0xFF7}:
        raise ValueError("unexpected derived difference")
    return bytes(out), diffs


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    source = Path(sys.argv[1]).read_bytes()
    output, diffs = expected(source)
    print("A SHA-256:", digest(source))
    print("expected B SHA-256:", digest(output))
    print("complete A->B diff:", [(hex(i), hex(a), hex(b)) for i, a, b in diffs])
    if len(sys.argv) == 3:
        candidate = Path(sys.argv[2]).read_bytes()
        if candidate != output:
            raise SystemExit("B does not match independent derivation")
        print("B independent audit: PASS")


if __name__ == "__main__":
    main()
