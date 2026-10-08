import struct
import unittest
from unittest.mock import patch

import pokemonstart_v022_box_model as box
import pokemonstart_v022_inventory_model as inventory
import pokemonstart_v022_party_model as model
from test_v022_party_writer import synthetic_inputs


class BoxModelTests(unittest.TestCase):
    def setUp(self):
        raw, rom = synthetic_inputs()
        rom = bytearray(rom)
        struct.pack_into('<25I', rom, box.BOX_TABLE, *box.EXPECTED_POINTERS)
        self.rom = bytes(rom)
        for module in (model, inventory):
            gate = patch.object(module, 'ROM_SHA256', model.sha(self.rom))
            gate.start(); self.addCleanup(gate.stop)
        self.raw = raw
        self.party = model.verifier.verify_bytes(raw)
        self.active = self.party.slots[self.party.active_slot]

    def place(self, raw, box_index, slot, record):
        out = bytearray(raw)
        start = box.EXPECTED_POINTERS[box_index] + slot * box.RECORD_SIZE
        for i, value in enumerate(record):
            out[box._file_offset(self.active, start + i)] = value
        for section in range(14):
            base = self.active.section(section).physical_sector * 4096
            length = model.verifier.SECTION_LENGTHS[section]
            struct.pack_into('<H', out, base + 0xFF6, model.verifier.calculate_save_checksum(out[base:base + length]))
        return bytes(out)

    def compressed(self):
        base = self.active.section(1).physical_sector * 4096 + 0x38
        party = self.raw[base:base + 100]
        record = bytearray(58)
        record[0:28] = party[0:28]
        record[28:39] = party[32:43]
        packed = sum(int.from_bytes(party[44 + 2*i:46 + 2*i], 'little') << (10*i) for i in range(4))
        record[39:44] = packed.to_bytes(5, 'little')
        record[44:50] = party[56:62]
        record[50:54] = party[68:72]
        record[54:58] = party[72:76]
        return bytes(record), party

    def test_empty_and_every_region_decodes(self):
        self.assertEqual(box.inspect(self.raw, self.rom)['occupied'], [])
        record, party = self.compressed()
        for box_index, slot in ((0, 0), (18, 29), (19, 0), (21, 29), (22, 7), (23, 29), (24, 29)):
            with self.subTest(box=box_index + 1, slot=slot + 1):
                rows = box.inspect(self.place(self.raw, box_index, slot, record), self.rom)['occupied']
                self.assertEqual([(r['box'], r['position']) for r in rows], [(box_index + 1, slot + 1)])
                mon = model.decode_record(party, 0, model.extract_tables(self.rom))
                self.assertEqual((rows[0]['species'], rows[0]['experience'], rows[0]['ivs'], rows[0]['evs']),
                                 (mon['species'], mon['experience'], mon['ivs'], mon['evs']))
                self.assertEqual(rows[0]['moves'], [m['move_id'] for m in mon['moves']])

    def test_mapping_is_injective_and_rom_table_gated(self):
        seen = set()
        for start in box.EXPECTED_POINTERS:
            for i in range(box.BOX_SLOTS * box.RECORD_SIZE):
                offset = box._file_offset(self.active, start + i)
                self.assertNotIn(offset, seen); seen.add(offset)
        bad = bytearray(self.rom); bad[box.BOX_TABLE] ^= 4
        with patch.object(model, 'ROM_SHA256', model.sha(bytes(bad))), self.assertRaises(ValueError):
            box.inspect(self.raw, bytes(bad))
        self.assertFalse(box.inspect(self.raw, self.rom)['writer_authorized'])
