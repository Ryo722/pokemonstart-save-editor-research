from __future__ import annotations

import struct
import unittest

import pokemonstart_fastlab_v022_money as money
import pokemonstart_save_verifier as verifier


def _slot(counter: int, decoded_money: int, key: int) -> bytes:
    sections = []
    for section_id in range(verifier.SLOT_SECTORS):
        sector = bytearray(verifier.SECTOR_SIZE)
        if section_id == 0:
            struct.pack_into("<I", sector, 0xF20, key)
        elif section_id == 1:
            struct.pack_into("<I", sector, 0x290, decoded_money ^ key)
        checksum = verifier.calculate_save_checksum(
            bytes(sector[:verifier.SECTION_LENGTHS[section_id]])
        )
        struct.pack_into("<H", sector, verifier.SECTION_ID_OFFSET, section_id)
        struct.pack_into("<H", sector, verifier.SECTION_CHECKSUM_OFFSET, checksum)
        struct.pack_into("<I", sector, verifier.SECTION_SIGNATURE_OFFSET, verifier.FILE_SIGNATURE)
        struct.pack_into("<I", sector, verifier.SECTION_COUNTER_OFFSET, counter)
        sections.append(bytes(sector))
    return b"".join(sections)


def _save() -> bytes:
    flash = bytearray(verifier.FLASH_SIZE)
    flash[:14 * verifier.SECTOR_SIZE] = b"\xff" * (14 * verifier.SECTOR_SIZE)
    flash[14 * verifier.SECTOR_SIZE:28 * verifier.SECTOR_SIZE] = _slot(3, money.SOURCE_MONEY, 0xA1B2C3D4)
    return bytes(flash)


class FastLabV022MoneyTests(unittest.TestCase):
    def test_only_section_money_and_checksum_change(self) -> None:
        raw = _save()
        original_expected = money.INPUT_SHA256
        money.INPUT_SHA256 = money.sha256(raw)
        try:
            result, receipt = money.derive(raw)
        finally:
            money.INPUT_SHA256 = original_expected
        before = verifier.verify_bytes(raw)
        after = verifier.verify_bytes(result)
        old_active = before.slots[before.active_slot]
        new_active = after.slots[after.active_slot]
        key = struct.unpack_from("<I", new_active.section(0).data, 0xF20)[0]
        decoded = struct.unpack_from("<I", new_active.section(1).data, 0x290)[0] ^ key
        self.assertEqual(decoded, money.TARGET_MONEY)
        self.assertEqual(receipt["encryption_key"], 0xA1B2C3D4)
        self.assertEqual(receipt["active_slot"], 1)
        self.assertEqual(new_active.counter, old_active.counter)

    def test_unrecognized_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(money.FastLabError, "exact allowlisted"):
            money.derive(b"not the retained input")


if __name__ == "__main__":
    unittest.main()
