"""Stdlib-only B -> C normal-save audit; reports bounded logical differences.

Usage: python3 tests/m4_independent_game_transition_audit.py B C
This does not import the product writer, verifier, or journal.
"""
import hashlib
import sys
from pathlib import Path

LENGTHS = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98, 0xFF0, 0xFF0,
           0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0x450)
VOLATILE = {0: {0x11, 0x12}, 1: {0x6DC, 0x6E4, 0x724, 0x72C}, 2: {0x210}}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def integer(data, offset, length):
    return int.from_bytes(data[offset:offset + length], "little")


def slot(raw, number):
    sections = {}
    counters = set()
    positions = {}
    for local in range(14):
        sector = raw[(number * 14 + local) * 4096:(number * 14 + local + 1) * 4096]
        section_id = integer(sector, 0xFF4, 2)
        if section_id in sections or not 0 <= section_id < 14:
            raise ValueError("invalid section IDs")
        payload = sector[:LENGTHS[section_id]]
        total = sum(integer(payload, i, 4) for i in range(0, len(payload), 4)) & 0xFFFFFFFF
        checksum = ((total >> 16) + (total & 0xFFFF)) & 0xFFFF
        if integer(sector, 0xFF6, 2) != checksum:
            raise ValueError("section checksum mismatch")
        counters.add(integer(sector, 0xFFC, 4))
        sections[section_id] = sector
        positions[section_id] = local
    if len(sections) != 14 or len(counters) != 1:
        raise ValueError("incomplete or mixed-counter slot")
    return sections, positions, counters.pop()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    before, after = (Path(name).read_bytes() for name in sys.argv[1:])
    if len(before) != 131088 or len(after) != len(before):
        raise ValueError("unexpected save length")
    b0, bp0, bc0 = slot(before, 0)
    b1, bp1, bc1 = slot(before, 1)
    c0, cp0, cc0 = slot(after, 0)
    c1, cp1, cc1 = slot(after, 1)
    old_slot = 0 if bc0 > bc1 else 1
    new_slot = 0 if cc0 > cc1 else 1
    if new_slot != 1 - old_slot:
        raise ValueError("active slot did not switch")
    old_counter = (bc0, bc1)[old_slot]
    new_counter = (cc0, cc1)[new_slot]
    if new_counter != old_counter + 1 or old_slot != old_counter % 2 or new_slot != new_counter % 2:
        raise ValueError("counter or parity mismatch")
    old_bytes = before[old_slot * 14 * 4096:(old_slot + 1) * 14 * 4096]
    preserved = after[old_slot * 14 * 4096:(old_slot + 1) * 14 * 4096]
    if old_bytes != preserved:
        raise ValueError("previous active slot changed")
    old_sections, old_positions = (b0, bp0) if old_slot == 0 else (b1, bp1)
    new_sections, new_positions = (c0, cp0) if new_slot == 0 else (c1, cp1)
    if any(new_positions[i] != (old_positions[i] + 1) % 14 for i in range(14)):
        raise ValueError("section rotation mismatch")
    if before[28 * 4096:32 * 4096] != after[28 * 4096:32 * 4096]:
        raise ValueError("sectors 28-31 changed")
    footer_changes = [(hex(i + 32 * 4096), hex(x), hex(y))
                      for i, (x, y) in enumerate(zip(before[32 * 4096:], after[32 * 4096:]))
                      if x != y]
    differences = {}
    for section_id in range(14):
        old, new = old_sections[section_id], new_sections[section_id]
        if old[LENGTHS[section_id]:0xFF4] != new[LENGTHS[section_id]:0xFF4]:
            raise ValueError("checksum-excluded tail changed")
        changes = [(i, x, y) for i, (x, y) in enumerate(zip(old[:LENGTHS[section_id]],
                                                         new[:LENGTHS[section_id]])) if x != y]
        if any(i not in VOLATILE.get(section_id, set()) for i, _, _ in changes):
            raise ValueError(f"section {section_id} changed outside observed envelope")
        if changes:
            differences[section_id] = [(hex(i), hex(x), hex(y)) for i, x, y in changes]
    if old_sections[1][0x38:0x38 + 100] != new_sections[1][0x38:0x38 + 100]:
        raise ValueError("party[0] record changed")
    print("B SHA-256:", sha(before))
    print("C SHA-256:", sha(after))
    print("slot/counter:", old_slot, old_counter, "->", new_slot, new_counter)
    print("complete logical payload differences:", differences)
    print("footer differences (reported, semantics unqualified):", footer_changes)
    print("independent game transition audit: PASS")


if __name__ == "__main__":
    main()
