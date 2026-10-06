import hashlib
import struct
import unittest

import pokemonstart_save_verifier as v


def _make_party_record(*, species=1, level=5, hp_iv=31, ability_num=0):
    record = bytearray(v.POKEMON_SIZE)
    struct.pack_into("<I", record, 0, 0x11223344)
    struct.pack_into("<I", record, 4, 0x55667788)
    record[8:15] = bytes.fromhex("01020304050607")
    record[15] = 3
    record[16] = 0x15
    record[17] = 12
    record[18] = 1
    record[19] = 2
    record[20:27] = bytes.fromhex("11121314151617")
    record[27] = 4
    struct.pack_into("<H", record, 28, species)
    struct.pack_into("<H", record, 32, species)
    struct.pack_into("<H", record, 34, 9)
    struct.pack_into("<I", record, 36, 134)
    record[40] = 0
    record[41] = 50
    record[42] = 3
    struct.pack_into("<4H", record, 44, 33, 45, 0, 0)
    record[52:56] = bytes((35, 40, 0, 0))
    record[56:62] = bytes((1, 2, 3, 4, 5, 6))
    ivs = (hp_iv, 29, 26, 23, 27, 29)
    iv_word = sum(value << (5 * i) for i, value in enumerate(ivs))
    if ability_num:
        iv_word |= 1 << 31
    struct.pack_into("<I", record, 72, iv_word)
    struct.pack_into("<I", record, 80, 0)
    record[84] = level
    record[85] = 0
    struct.pack_into("<7H", record, 86, 21, 21, 9, 11, 10, 13, 12)
    return bytes(record)


def _make_sector(section_id, counter, payload=None):
    sector = bytearray(v.SECTOR_SIZE)
    if payload is not None:
        sector[: len(payload)] = payload
    checksum = v.calculate_save_checksum(sector[: v.SECTION_LENGTHS[section_id]])
    struct.pack_into("<H", sector, v.SECTION_ID_OFFSET, section_id)
    struct.pack_into("<H", sector, v.SECTION_CHECKSUM_OFFSET, checksum)
    struct.pack_into("<I", sector, v.SECTION_SIGNATURE_OFFSET, v.FILE_SIGNATURE)
    struct.pack_into("<I", sector, v.SECTION_COUNTER_OFFSET, counter)
    return bytes(sector)


def _make_slot(counter, *, permutation=None, party_count=1, hp_iv=31):
    logical = []
    for section_id in range(v.SLOT_SECTORS):
        payload = bytearray(v.SECTION_LENGTHS[section_id])
        if section_id == 1:
            payload[v.PARTY_COUNT_OFFSET] = party_count
            if party_count:
                mon = _make_party_record(hp_iv=hp_iv)
                payload[v.PARTY_OFFSET : v.PARTY_OFFSET + len(mon)] = mon
        logical.append(_make_sector(section_id, counter, payload))
    if permutation is None:
        permutation = list(range(v.SLOT_SECTORS))
    return b"".join(logical[section_id] for section_id in permutation)


def _make_save(slot0, slot1, *, footer=b""):
    body = bytearray(b"\x00" * v.FLASH_SIZE)
    body[: 14 * v.SECTOR_SIZE] = slot0
    body[14 * v.SECTOR_SIZE : 28 * v.SECTOR_SIZE] = slot1
    body[30 * v.SECTOR_SIZE : 31 * v.SECTOR_SIZE] = b"\x01" + b"\x00" * (v.SECTOR_SIZE - 1)
    body[31 * v.SECTOR_SIZE : 32 * v.SECTOR_SIZE] = b"\x00" * v.SECTOR_SIZE
    return bytes(body) + footer


class VerifierTests(unittest.TestCase):
    def test_accepts_single_valid_slot_and_erased_other_slot(self):
        raw = _make_save(b"\xFF" * (14 * v.SECTOR_SIZE), _make_slot(1))
        result = v.verify_bytes(raw)
        self.assertEqual(result.active_slot, 1)
        self.assertEqual(result.party_count, 1)
        mon = result.party[0]
        self.assertEqual(mon.species, 1)
        self.assertEqual(mon.level, 5)
        self.assertEqual(mon.experience, 134)
        self.assertEqual(mon.friendship, 50)
        self.assertEqual(mon.ball, 3)
        self.assertEqual(mon.moves, (33, 45, 0, 0))
        self.assertEqual(mon.pp, (35, 40, 0, 0))
        self.assertEqual(mon.evs, (1, 2, 3, 4, 5, 6))
        self.assertEqual(mon.ivs, (31, 29, 26, 23, 27, 29))
        self.assertEqual(mon.ability_num, 0)
        self.assertEqual(mon.hp, 21)
        self.assertEqual(mon.max_hp, 21)
        self.assertEqual(sum(byte != 0 for byte in result.sector30), 1)
        self.assertEqual(sum(byte != 0 for byte in result.sector31), 0)

    def test_party_ability_selector_is_iv_word_most_significant_bit(self):
        mon = v._decode_party_record(_make_party_record(ability_num=1), 0)
        self.assertEqual(mon.ability_num, 1)
        self.assertEqual(mon.ivs, (31, 29, 26, 23, 27, 29))

    def test_section_permutation_and_newest_slot(self):
        perm0 = list(range(13, -1, -1))
        perm1 = list(range(5, 14)) + list(range(5))
        raw = _make_save(_make_slot(10, permutation=perm0), _make_slot(11, permutation=perm1))
        result = v.verify_bytes(raw)
        self.assertEqual(result.active_slot, 1)
        self.assertEqual([s.section_id for s in result.slots[0].sections], list(range(14)))

    def test_counter_wrap_selects_zero_as_newer(self):
        raw = _make_save(_make_slot(0xFFFFFFFF), _make_slot(0))
        result = v.verify_bytes(raw)
        self.assertEqual(result.active_slot, 1)

    def test_equal_counters_are_ambiguous(self):
        raw = _make_save(_make_slot(7), _make_slot(7))
        with self.assertRaisesRegex(v.VerificationError, "ambiguous save slots"):
            v.verify_bytes(raw)

    def test_checksum_corruption_is_rejected(self):
        slot = bytearray(_make_slot(1))
        slot[0] ^= 1
        raw = _make_save(bytes(slot), b"\xFF" * (14 * v.SECTOR_SIZE))
        with self.assertRaisesRegex(v.VerificationError, "checksum mismatch"):
            v.verify_bytes(raw)

    def test_duplicate_section_id_is_rejected(self):
        slot = bytearray(_make_slot(1))
        second = v.SECTOR_SIZE
        struct.pack_into("<H", slot, second + v.SECTION_ID_OFFSET, 0)
        checksum = v.calculate_save_checksum(slot[second : second + v.SECTION_LENGTHS[0]])
        struct.pack_into("<H", slot, second + v.SECTION_CHECKSUM_OFFSET, checksum)
        raw = _make_save(bytes(slot), b"\xFF" * (14 * v.SECTOR_SIZE))
        with self.assertRaisesRegex(v.VerificationError, "section id set is invalid"):
            v.verify_bytes(raw)

    def test_inconsistent_section_counters_are_rejected(self):
        slot = bytearray(_make_slot(1))
        struct.pack_into("<I", slot, v.SECTOR_SIZE + v.SECTION_COUNTER_OFFSET, 2)
        raw = _make_save(bytes(slot), b"\xFF" * (14 * v.SECTOR_SIZE))
        with self.assertRaisesRegex(v.VerificationError, "inconsistent section counters"):
            v.verify_bytes(raw)

    def test_partially_erased_slot_is_rejected(self):
        slot = bytearray(_make_slot(1))
        slot[:v.SECTOR_SIZE] = b"\xFF" * v.SECTOR_SIZE
        raw = _make_save(bytes(slot), b"\xFF" * (14 * v.SECTOR_SIZE))
        with self.assertRaisesRegex(v.VerificationError, "partially erased slot"):
            v.verify_bytes(raw)

    def test_party_count_over_six_is_rejected(self):
        raw = _make_save(b"\xFF" * (14 * v.SECTOR_SIZE), _make_slot(1, party_count=7))
        with self.assertRaisesRegex(v.VerificationError, "unsupported party count 7"):
            v.verify_bytes(raw)

    def test_opaque_16_byte_footer_is_separated_and_reported(self):
        footer = bytes(range(16))
        raw = _make_save(b"\xFF" * (14 * v.SECTOR_SIZE), _make_slot(1), footer=footer)
        result = v.verify_bytes(raw)
        self.assertEqual(result.footer, footer)
        report = v.format_report(result)
        self.assertIn("emulator_footer: present-16-byte-opaque", report)
        self.assertIn(f"emulator_footer_sha256: {hashlib.sha256(footer).hexdigest()}", report)

    def test_unsupported_size_is_rejected(self):
        with self.assertRaisesRegex(v.VerificationError, "unsupported file size"):
            v.verify_bytes(b"\x00" * 123)

    def test_report_is_deterministic_for_same_bytes(self):
        raw = _make_save(b"\xFF" * (14 * v.SECTOR_SIZE), _make_slot(1))
        self.assertEqual(v.format_report(v.verify_bytes(raw)), v.format_report(v.verify_bytes(raw)))


if __name__ == "__main__":
    unittest.main()
