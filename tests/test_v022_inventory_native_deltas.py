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

    def test_product_operation_reuses_only_observed_empty_slot_shape(self):
        source = self.source()
        deleted, _ = items.derive(source, ROM, {'remove_antidote': True})
        self.assertEqual(items.inspect(deleted, ROM)['entries'], [
            {'slot': 0, 'item_id': 13, 'name': 'Potion', 'quantity': 3,
             'editable': True, 'removable': False},
            {'slot': 1, 'item_id': 533, 'name': 'Preserved item #533', 'quantity': 1,
             'editable': False, 'removable': False},
        ])
        restored, _ = items.derive(deleted, ROM, {'insert_antidote': True})
        self.assertEqual(restored, source)

    def test_rejects_changed_prefix_and_tail(self):
        source = self.source()
        active = v.verify_bytes(source).slots[v.verify_bytes(source).active_slot]
        base = active.section(13).physical_sector * v.SECTOR_SIZE + items.OFFSET
        for offset in (0, 4, 12):
            bad = bytearray(source)
            bad[base + offset] ^= 1
            with self.assertRaises(ValueError):
                items.remove_observed_antidote(bytes(bad), ROM)

    def test_direct_antidote_helpers_reject_nonzero_key(self):
        source = self.source()
        verified = v.verify_bytes(source)
        section = verified.slots[verified.active_slot].section(0)
        base = section.physical_sector * v.SECTOR_SIZE
        keyed = bytearray(source)
        struct.pack_into('<I', keyed, base + 0xF20, 1)
        struct.pack_into('<H', keyed, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(keyed[base:base + v.SECTION_LENGTHS[0]]))
        keyed = bytes(keyed)
        v.verify_bytes(keyed)
        with self.assertRaisesRegex(ValueError, 'key0'):
            items.remove_observed_antidote(keyed, ROM)
        empty, _ = items.remove_observed_antidote(source, ROM)
        verified = v.verify_bytes(empty)
        section = verified.slots[verified.active_slot].section(0)
        base = section.physical_sector * v.SECTOR_SIZE
        keyed_empty = bytearray(empty)
        struct.pack_into('<I', keyed_empty, base + 0xF20, 1)
        struct.pack_into('<H', keyed_empty, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(keyed_empty[base:base + v.SECTION_LENGTHS[0]]))
        with self.assertRaisesRegex(ValueError, 'key0'):
            items.insert_observed_antidote(bytes(keyed_empty), ROM)


if __name__ == '__main__':
    unittest.main()
