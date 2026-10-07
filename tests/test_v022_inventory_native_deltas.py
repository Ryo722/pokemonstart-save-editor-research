import struct
import unittest
import pokemonstart_save_verifier as v
import pokemonstart_v022_product_inventory as items
from test_v022_inventory_insertion import inventory_fixture

ROM = items.profile.EXPECTED_ROM_SHA256


class NativeInventoryDeltaTests(unittest.TestCase):
    def source(self):
        raw = bytearray(inventory_fixture())
        active = v.verify_bytes(raw).slots[v.verify_bytes(raw).active_slot]
        base = active.section(13).physical_sector * v.SECTOR_SIZE
        raw[base + items.OFFSET:base + 0xFF4] = bytes(0xFF4 - items.OFFSET)
        struct.pack_into('<HHHHHH', raw, base + items.OFFSET, 13, 3, 533, 1, 14, 1)
        return bytes(raw)

    def test_remove_zeroes_slot_and_insert_restores_exact_bytes(self):
        source = self.source()
        deleted, receipt = items.remove_observed_antidote(source, ROM)
        active = v.verify_bytes(source).slots[v.verify_bytes(source).active_slot]
        base = active.section(13).physical_sector * v.SECTOR_SIZE + items.OFFSET
        self.assertEqual(deleted[base:base + 12], source[base:base + 8] + bytes(4))
        self.assertFalse(receipt['compacted'])
        restored, inserted = items.insert_observed_antidote(deleted, ROM)
        self.assertEqual(restored, source)
        self.assertTrue(inserted['restored_observed_position'])

    def test_rejects_changed_prefix_and_tail(self):
        source = self.source()
        active = v.verify_bytes(source).slots[v.verify_bytes(source).active_slot]
        base = active.section(13).physical_sector * v.SECTOR_SIZE + items.OFFSET
        for offset in (0, 4, 12):
            bad = bytearray(source)
            bad[base + offset] ^= 1
            with self.assertRaises(ValueError):
                items.remove_observed_antidote(bytes(bad), ROM)


if __name__ == '__main__':
    unittest.main()
