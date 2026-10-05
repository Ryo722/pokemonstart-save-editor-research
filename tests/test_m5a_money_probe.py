import struct
import tempfile
import unittest
from pathlib import Path

import pokemonstart_m5a_money_probe as money
import pokemonstart_save_verifier as verifier


def _sector(section_id: int, counter: int, payload: bytes) -> bytes:
    raw = bytearray(verifier.SECTOR_SIZE)
    raw[: len(payload)] = payload
    checksum = verifier.calculate_save_checksum(
        raw[: verifier.SECTION_LENGTHS[section_id]]
    )
    struct.pack_into("<H", raw, verifier.SECTION_ID_OFFSET, section_id)
    struct.pack_into("<H", raw, verifier.SECTION_CHECKSUM_OFFSET, checksum)
    struct.pack_into("<I", raw, verifier.SECTION_SIGNATURE_OFFSET, verifier.FILE_SIGNATURE)
    struct.pack_into("<I", raw, verifier.SECTION_COUNTER_OFFSET, counter)
    return bytes(raw)


def _slot(counter: int, decoded_money: int, key: int, permutation=None) -> bytes:
    logical = []
    for section_id in range(verifier.SLOT_SECTORS):
        payload = bytearray(verifier.SECTION_LENGTHS[section_id])
        if section_id == money.ENCRYPTION_KEY_SECTION_ID:
            struct.pack_into("<I", payload, money.ENCRYPTION_KEY_OFFSET, key)
        if section_id == money.MONEY_SECTION_ID:
            struct.pack_into("<I", payload, money.MONEY_OFFSET, decoded_money ^ key)
            payload[verifier.PARTY_COUNT_OFFSET] = 0
        logical.append(_sector(section_id, counter, bytes(payload)))

    if permutation is None:
        permutation = list(range(verifier.SLOT_SECTORS))
    return b"".join(logical[section_id] for section_id in permutation)


def _save(valid_slot: bytes, *, slot_index=0, footer=b"") -> bytes:
    flash = bytearray(b"\x00" * verifier.FLASH_SIZE)
    erased = b"\xFF" * (verifier.SLOT_SECTORS * verifier.SECTOR_SIZE)
    if slot_index == 0:
        flash[: len(valid_slot)] = valid_slot
        flash[14 * verifier.SECTOR_SIZE : 28 * verifier.SECTOR_SIZE] = erased
    else:
        flash[: 14 * verifier.SECTOR_SIZE] = erased
        flash[14 * verifier.SECTOR_SIZE : 28 * verifier.SECTOR_SIZE] = valid_slot
    return bytes(flash) + footer


class MoneyProbeTests(unittest.TestCase):
    def test_decodes_xor_candidate_from_logical_sections(self):
        raw = _save(_slot(2, 1234567, 0xA1B2C3D4))
        result = money.probe_bytes(raw)
        self.assertEqual(result.active_slot, 0)
        self.assertEqual(result.counter, 2)
        self.assertEqual(result.encryption_key, 0xA1B2C3D4)
        self.assertEqual(result.stored_money_word, 1234567 ^ 0xA1B2C3D4)
        self.assertEqual(result.decoded_money, 1234567)
        self.assertTrue(result.source_candidate_range_ok)

    def test_physical_permutation_is_not_assumed(self):
        permutation = [13, 7, 0, 12, 1, 5, 2, 11, 3, 9, 4, 8, 6, 10]
        raw = _save(_slot(4, 7654321, 0x10203040, permutation), slot_index=1)
        result = money.probe_bytes(raw)
        self.assertEqual(result.active_slot, 1)
        self.assertEqual(result.decoded_money, 7654321)

    def test_source_candidate_range_is_advisory_not_acceptance(self):
        raw = _save(_slot(2, 10000000, 0x01020304))
        result = money.probe_bytes(raw)
        self.assertEqual(result.decoded_money, 10000000)
        self.assertFalse(result.source_candidate_range_ok)

    def test_existing_verifier_rejects_corrupt_save(self):
        raw = bytearray(_save(_slot(2, 5000, 0x55667788)))
        raw[money.MONEY_OFFSET] ^= 1
        with self.assertRaises(verifier.VerificationError):
            money.probe_bytes(bytes(raw))

    def test_path_probe_is_read_only(self):
        raw = _save(_slot(2, 5000, 0x55667788), footer=bytes(range(16)))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private.sav"
            path.write_bytes(raw)
            before = path.read_bytes()
            result = money.probe_path(path)
            after = path.read_bytes()
        self.assertEqual(result.decoded_money, 5000)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
