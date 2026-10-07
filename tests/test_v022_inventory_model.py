import hashlib
import struct
import unittest
from unittest.mock import patch

import pokemonstart_v022_inventory_model as model
import pokemonstart_v022_inventory_audit as audit
import pokemonstart_save_verifier as verifier
from test_v022_inventory_insertion import inventory_fixture


def synthetic_rom():
    """Original synthetic metadata, never ROM-derived bytes."""
    data = bytearray(33554432)
    struct.pack_into('<I', data, 0x1C8, model.ITEM_TABLE)
    pairs = tuple(x for _, ram, cap, _ in model.POCKETS for x in (ram, cap))
    struct.pack_into('<10I', data, model.DESCRIPTOR - model.ROM_BASE, *pairs)
    for item, pocket in ((13, 1), (14, 1), (15, 1), (533, 1), (267, 2), (4, 3), (289, 4), (142, 5)):
        base = model.ITEM_TABLE - model.ROM_BASE + item * 40
        data[base:base + 10] = bytes([0x01, 0xFF]) + bytes(8)
        struct.pack_into('<H', data, base + 10, item)
        data[base + 22] = pocket
    return bytes(data)


class InventoryModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = synthetic_rom()
        cls.rom_sha = hashlib.sha256(cls.rom).hexdigest()

    def setUp(self):
        self.gate = patch.object(model, 'ROM_SHA256', self.rom_sha)
        self.gate.start()
        self.addCleanup(self.gate.stop)
        self.other_gate = patch.object(audit, 'ROM_SHA256', self.rom_sha)
        self.other_gate.start()
        self.addCleanup(self.other_gate.stop)
        self.raw = bytearray(inventory_fixture())
        self.active = verifier.verify_bytes(self.raw).slots[verifier.verify_bytes(self.raw).active_slot]
        base = self.active.section(13).physical_sector * 4096
        self.raw[base + 0xADC:base + 0xFF0] = bytes(0xFF0 - 0xADC)
        self.raw[0x1E000:0x1EFF0] = bytes(0xFF0)

    def put_at(self, offset, item, quantity):
        struct.pack_into('<HH', self.raw, offset, item, quantity)

    def compare(self):
        before = bytes(self.raw)
        primary = model.inspect(before, self.rom)
        independent = audit.inspect(before, self.rom)
        self.assertEqual(primary['state_supported'], independent['state_supported'])
        self.assertEqual((primary['active_slot'], primary['counter']),
                         (independent['active_slot'], independent['counter']))
        for a, b in zip(primary['pockets'], independent['pockets']):
            self.assertEqual([(x['slot'], x['item_id'], x['quantity']) for x in a['entries']], b['entries'])
            for key in ('name', 'capacity', 'holes', 'first_empty'):
                self.assertEqual(a[key], b[key])
        self.assertEqual(before, bytes(self.raw))
        self.assertFalse(primary['writer_authorized'])
        self.assertFalse(primary['give_all_enabled'])
        return primary

    def test_regular_boundaries_use_independent_absolute_oracle(self):
        base = self.active.section(13).physical_sector * 4096
        # Each case independently targets its real physical location. In
        # particular slot 325 must not consume the section's 0xFF0 padding.
        for slot, offset in ((0, base + 0xADC), (324, base + 0xFEC),
                             (325, 0x1E000), (449, 0x1E1F0), (699, 0x1E5D8)):
            with self.subTest(slot=slot):
                self.put_at(offset, 13, 999)
                report = self.compare()
                entry = report['pockets'][0]['entries'][0]
                self.assertEqual((entry['slot'], entry['offset']), (slot, offset))
                self.put_at(offset, 0, 0)

    def test_each_pocket_start_end_and_gap(self):
        for index, start, end, item in ((1, 0x1E5DC, 0x1E704, 267),
                                       (2, 0x1E728, 0x1E7EC, 4),
                                       (3, 0x1E7F0, 0x1E9EC, 289),
                                       (4, 0x1E9F0, 0x1EB0C, 142)):
            for slot, offset in ((0, start), (model.POCKETS[index][2] - 1, end)):
                with self.subTest(pocket=index, slot=slot):
                    self.put_at(offset, item, 1)
                    entry = self.compare()['pockets'][index]['entries'][0]
                    self.assertEqual(entry['slot'], slot)
                    self.put_at(offset, 0, 0)
        self.raw[0x1E708:0x1E728] = bytes([0xA5]) * 32
        self.assertTrue(self.compare()['state_supported'])

    def test_malformed_id_quantity_pocket_and_duplicate(self):
        base = self.active.section(13).physical_sector * 4096 + 0xADC
        for item, qty in ((0, 1), (13, 0), (13, 1000), (13, 65535),
                          (375, 1), (839, 1), (65535, 1), (4, 1)):
            with self.subTest(item=item, qty=qty):
                self.put_at(base, item, qty)
                self.assertFalse(self.compare()['state_supported'])
        self.put_at(base, 13, 1)
        self.put_at(base + 4, 13, 2)
        self.assertFalse(self.compare()['state_supported'])

    def test_holes_order_full_capacity(self):
        base = self.active.section(13).physical_sector * 4096 + 0xADC
        self.put_at(base, 14, 2)
        self.put_at(base + 8, 13, 3)
        p = self.compare()['pockets'][0]
        self.assertEqual(p['holes'], [1])
        self.assertEqual(p['first_empty'], 1)
        self.assertEqual([x['item_id'] for x in p['entries']], [14, 13])
        # Repeated synthetic IDs are unsupported, but occupancy/full reporting
        # must still inspect the full array instead of stopping at the split.
        for slot in range(700):
            offset = base + 4 * slot if slot < 325 else 0x1E000 + 4 * (slot - 325)
            self.put_at(offset, 13, 1)
        p = self.compare()['pockets'][0]
        self.assertEqual(p['occupied'], 700)
        self.assertIsNone(p['first_empty'])

    def test_key_profile_and_corrupt_save_reject(self):
        base = self.active.section(0).physical_sector * 4096
        struct.pack_into('<I', self.raw, base + 0xF20, 1)
        struct.pack_into('<H', self.raw, base + 0xFF6,
                         verifier.calculate_save_checksum(self.raw[base:base + 0xF24]))
        for reader in (model.inspect, audit.inspect):
            with self.assertRaisesRegex(ValueError, 'key0'):
                reader(bytes(self.raw), self.rom)
            with self.assertRaises(ValueError):
                reader(bytes(self.raw), self.rom[:-1])
        self.raw[base] ^= 1
        with self.assertRaises(ValueError):
            model.inspect(bytes(self.raw), self.rom)

    def test_catalog_metadata_and_name_exclusions(self):
        catalog, summary = model.extract_catalog(self.rom)
        self.assertEqual(catalog[13].name, 'あ')
        self.assertTrue(catalog[13].proposed_ordinary)
        self.assertFalse(catalog[267].proposed_ordinary)
        self.assertIn(0, summary['excluded_ids'])
        self.assertIn(375, summary['excluded_ids'])
        for name in (bytes([0xAC, 0xFF]), bytes([0xFC, 0xFF]), bytes(10)):
            with self.assertRaises(ValueError):
                model.decode_name(name)
        self.assertEqual(model.decode_name(bytes([0xA1, 0xD2, 0xD4, 0xFF])), '0XZ')

    def test_alternate_runtime_bag_rejected(self):
        base = self.active.section(13).physical_sector * 4096
        struct.pack_into('<h', self.raw, base + 0x6B6, -1)
        # Unchecked parasite tail, so structural checksum validation still passes.
        verifier.verify_bytes(bytes(self.raw))
        for reader in (model.inspect, audit.inspect):
            with self.assertRaisesRegex(ValueError, 'alternate runtime bag'):
                reader(bytes(self.raw), self.rom)

    def test_erased_backup_rejected(self):
        inactive = 1 - self.active.slot_index
        self.raw[inactive * 14 * 4096:(inactive + 1) * 14 * 4096] = bytes([255]) * (14 * 4096)
        for reader in (model.inspect, audit.inspect):
            with self.assertRaises(ValueError):
                reader(bytes(self.raw), self.rom)

    def test_section_rotation_preserves_reconstructed_inventory(self):
        base = self.active.section(13).physical_sector * 4096
        self.put_at(base + 0xADC, 13, 999)
        self.put_at(0x1E728, 4, 5)
        expected = self.compare()
        frozen = bytes(self.raw)
        for slot in range(2):
            for physical in range(14):
                src = (slot * 14 + physical) * 4096
                dest = (slot * 14 + (physical + 5) % 14) * 4096
                self.raw[dest:dest + 4096] = frozen[src:src + 4096]
        actual = self.compare()
        for first, second in zip(expected['pockets'], actual['pockets']):
            self.assertEqual([(x['slot'], x['item_id'], x['quantity']) for x in first['entries']],
                             [(x['slot'], x['item_id'], x['quantity']) for x in second['entries']])


if __name__ == '__main__':
    unittest.main()
