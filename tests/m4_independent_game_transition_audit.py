"""Stdlib-only B -> C normal-save audit; reports bounded logical differences.

Usage: python3 tests/m4_independent_game_transition_audit.py B C
This does not import the product writer, verifier, or journal.
"""
import hashlib
import sys
from pathlib import Path

LENGTHS = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98, 0xFF0, 0xFF0,
           0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0xFF0, 0x450)
SAVE_BLOCK2_TIME = set(range(0x0E, 0x13))
EVENT_OBJECTS_BASE, EVENT_OBJECT_SIZE, EVENT_OBJECT_COUNT = 0x6A0, 0x24, 16
EVENT_RUNTIME_FIELDS = ((0x00, 1), (0x10, 4), (0x14, 4),
                        (0x18, 1), (0x1C, 1), (0x20, 1))
EVENT_OBJECT_RUNTIME = {EVENT_OBJECTS_BASE + i * EVENT_OBJECT_SIZE + field + byte
                        for i in range(EVENT_OBJECT_COUNT)
                        for field, size in EVENT_RUNTIME_FIELDS for byte in range(size)}
SAVED_GAME_STAT_OFFSET = 0x210
VOLATILE = {0: SAVE_BLOCK2_TIME, 1: EVENT_OBJECT_RUNTIME,
            2: set(range(SAVED_GAME_STAT_OFFSET, SAVED_GAME_STAT_OFFSET + 4))}


def transition_metadata(sections):
    save2 = sections[0][:LENGTHS[0]]
    hours = integer(save2, 0x0E, 2)
    minutes, seconds = save2[0x10], save2[0x11]
    if hours > 999 or minutes > 59 or seconds > 59:
        raise ValueError("invalid saved play-time fields")
    saved_count = integer(sections[2], SAVED_GAME_STAT_OFFSET, 4)
    return hours * 3600 + minutes * 60 + seconds, saved_count


def classify(section_id, offset):
    if section_id == 0 and offset in SAVE_BLOCK2_TIME:
        if offset < 0x10:
            return "SaveBlock2.playTimeHours"
        return {0x10: "SaveBlock2.playTimeMinutes", 0x11: "SaveBlock2.playTimeSeconds",
                0x12: "SaveBlock2.playTimeVBlanks"}[offset]
    if section_id == 1 and offset in EVENT_OBJECT_RUNTIME:
        relative = offset - EVENT_OBJECTS_BASE
        index, field_offset = divmod(relative, EVENT_OBJECT_SIZE)
        if field_offset == 0:
            field = "runtimeFlags[0]"
        elif 0x10 <= field_offset < 0x14:
            field = "currentCoords." + ("x" if field_offset < 0x12 else "y")
        elif 0x14 <= field_offset < 0x18:
            field = "previousCoords." + ("x" if field_offset < 0x16 else "y")
        else:
            field = {0x18: "facingDirection/movementDirection",
                     0x1C: "movementActionId",
                     0x20: "previousMovementDirection"}[field_offset]
        return f"SaveBlock1.eventObjects[{index}].{field}"
    if section_id == 2 and offset in VOLATILE[2]:
        return "SaveBlock1.gameStats[GAME_STAT_SAVED_GAME]"
    return None


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
    old_time, old_save_count = transition_metadata(old_sections)
    new_time, new_save_count = transition_metadata(new_sections)
    if new_time < old_time:
        raise ValueError("play time moved backwards")
    if new_save_count != ((old_save_count + 1) & 0xFFFFFFFF):
        raise ValueError("saved-game statistic did not increment once")
    footer_changes = [(hex(i + 32 * 4096), hex(x), hex(y))
                      for i, (x, y) in enumerate(zip(before[32 * 4096:], after[32 * 4096:]))
                      if x != y]
    differences = {}
    for section_id in range(14):
        old, new = old_sections[section_id], new_sections[section_id]
        if old[LENGTHS[section_id]:0xFF4] != new[LENGTHS[section_id]:0xFF4]:
            raise ValueError("checksum-excluded tail changed")
        changes = [(i, x, y, classify(section_id, i))
                   for i, (x, y) in enumerate(zip(old[:LENGTHS[section_id]],
                                                  new[:LENGTHS[section_id]])) if x != y]
        if any(label is None for _, _, _, label in changes):
            raise ValueError(f"section {section_id} changed outside observed envelope")
        if changes:
            differences[section_id] = [(hex(i), hex(x), hex(y), label) for i, x, y, label in changes]
    if old_sections[1][0x38:0x38 + 100] != new_sections[1][0x38:0x38 + 100]:
        raise ValueError("party[0] record changed")
    print("B SHA-256:", sha(before))
    print("C SHA-256:", sha(after))
    print("slot/counter:", old_slot, old_counter, "->", new_slot, new_counter)
    print("complete logical payload differences classified as play time, EventObject runtime fields, or save count:", differences)
    print("play-time seconds:", old_time, "->", new_time)
    print("saved-game count:", old_save_count, "->", new_save_count)
    print("footer differences (reported, semantics unqualified):", footer_changes)
    print("independent game transition audit: PASS")


if __name__ == "__main__":
    main()
