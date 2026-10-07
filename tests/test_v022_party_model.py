"""Synthetic-only E3 tests; no private record or proprietary table fixtures."""
import ast
import hashlib
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

import pokemonstart_v022_party_model as m
import pokemonstart_v022_party_audit as a


def fixtures():
    # Artificial species and thresholds, deliberately unlike any game table.
    species = m.Species(1, 'Synthetic', (60, 50, 40, 30, 20, 10), 0, (7, 8, 9))
    thresholds = tuple(0 if i == 0 else 1 if i == 1 else i**3 for i in range(101))
    modifiers = tuple(tuple(0 if n//5 == n%5 else 1 if j == n//5 else -1 if j == n%5 else 0
                            for j in range(5)) for n in range(25))
    moves = tuple(m.Move(i, 'Synthetic', 5 if i == 996 else 35) for i in range(998))
    tables = m.Tables((m.Species(0, None, (0,)*6, 0, (0,)*3), species), moves,
                      (thresholds,), modifiers, {}, {})
    record = bytearray(100)
    struct.pack_into('<I', record, 0, 9)
    record[19] = 2
    struct.pack_into('<H', record, 32, 1)
    struct.pack_into('<I', record, 36, 27)
    struct.pack_into('<4H', record, 44, 1, 2, 3, 996)
    record[52:56] = bytes((35, 35, 35, 5))
    record[84] = 3
    # Hand-calculated zero-IV/EV Lax stats, with the exact +5 candidate rule.
    struct.pack_into('<7H', record, 86, 4, 16, 8, 7, 6, 6, 4)
    rom = bytearray(33554432)
    rom[0x19B8B40+32:0x19B8B40+38] = bytes(species.bases)
    struct.pack_into('<H', rom, 0x19B8B40+32+22, 7)
    struct.pack_into('<2H', rom, 0x19B8B40+32+26, 8, 9)
    for i, value in enumerate(thresholds):
        struct.pack_into('<I', rom, 0x14C5D54+i*4, value)
    for i, row in enumerate(modifiers):
        struct.pack_into('<5b', rom, 0x20F550+i*5, *row)
    for move in moves:
        rom[0x14A3238+move.move_id*12+4] = move.base_pp
    return record, tables, bytes(rom)


class PartyModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record, cls.tables, cls.rom = fixtures()

    def decode(self, record=None):
        return m.decode_record(bytes(self.record if record is None else record), 0, self.tables)

    def test_low_level_discriminates_rules_and_preserves_damaged_hp(self):
        row = self.decode()
        self.assertTrue(row['five_matches'])
        self.assertFalse(row['level_matches'])
        self.assertEqual(row['cached_hp_stats'], [4, 16, 8, 7, 6, 6, 4])
        self.assertEqual(row['exp_derived_level'], 3)
        self.assertFalse(row['capabilities']['cached_stats']['writer_authorized'])

    def test_independent_reconstruction_all_fields(self):
        row = self.decode()
        rebuilt = a.reconstruct(bytes(self.record), self.rom)
        meta = {'save_sha256': 'synthetic', 'active_slot': 0, 'counter': 2}
        a.compare({**meta, 'party': [row]}, {**meta, 'party': [rebuilt]})
        row['experience'] += 1
        with self.assertRaisesRegex(ValueError, 'experience'):
            a.compare({**meta, 'party': [row]}, {**meta, 'party': [rebuilt]})

    def test_hidden_bit_is_bit4_not_ot_gender_bit7(self):
        record = bytearray(self.record)
        record[71] = 128
        self.assertFalse(self.decode(record)['hidden_ability'])
        self.assertEqual(self.decode(record)['resolved_ability'], 7)
        record[71] |= 16
        record[75] |= 128
        self.assertTrue(self.decode(record)['hidden_ability'])
        self.assertEqual(self.decode(record)['resolved_ability'], 9)
        record[71] &= ~16
        self.assertEqual(self.decode(record)['resolved_ability'], 8)

    def test_missing_alternate_and_hidden_fall_back(self):
        from dataclasses import replace
        record = bytearray(self.record); record[71] = 16; record[75] = 128
        tables = replace(self.tables, species=(self.tables.species[0], replace(self.tables.species[1], abilities=(7, 0, 0))))
        self.assertEqual(m.decode_record(bytes(record), 0, tables)['resolved_ability'], 7)

    def test_exp_boundary_is_table_driven(self):
        self.assertEqual(m.level_from_exp(26, 0, self.tables), 2)
        self.assertEqual(m.level_from_exp(27, 0, self.tables), 3)
        self.assertIsNone(m.level_from_exp(0, 0, self.tables))
        self.assertIsNone(m.level_from_exp(1000001, 0, self.tables))
        record = bytearray(self.record); struct.pack_into('<I', record, 36, 26)
        self.assertIn('EXP-derived and stored level disagree', self.decode(record)['capabilities']['level_exp']['reasons'])

    def test_all_four_pp_up_pairs_and_special_move(self):
        record = bytearray(self.record);record[40] = 0b11100100
        row = self.decode(record)
        self.assertEqual([r['pp_up_count'] for r in row['moves']], [0, 1, 2, 3])
        self.assertEqual([r['maximum_pp'] for r in row['moves']], [35, 42, 49, 5])
        record[52] = 36
        self.assertFalse(self.decode(record)['capabilities']['moves_pp_pp_up']['model_qualified'])

    def test_empty_pp_is_reported_without_mutation(self):
        record = bytearray(self.record);struct.pack_into('<H', record, 44, 0)
        original = bytes(record)
        row = self.decode(record)
        self.assertEqual(row['moves'][0]['issues'], ['empty slot retains nonzero PP'])
        self.assertEqual(bytes(record), original)

    def test_invalid_mint_level_evs_hyper_and_forms_are_classified(self):
        for offset, value in ((15, 26), (16, 1), (84, 0), (56, 253), (28, 1), (75, 64)):
            record = bytearray(self.record);record[offset] = value
            with self.subTest(offset=offset):
                row = self.decode(record)
                self.assertFalse(row['capabilities']['cached_stats']['model_qualified'])
        record = bytearray(self.record);record[56:62] = bytes((252, 252, 252, 0, 0, 0))
        self.assertIn('EV allocation outside practical limits', self.decode(record)['reasons'])

    def test_unknown_species_move_and_item_are_explicit(self):
        record = bytearray(self.record);struct.pack_into('<H', record, 32, 65535)
        row = self.decode(record)
        self.assertIsNone(row['resolved_ability'])
        self.assertIsNone(row['exp_derived_level'])
        record = bytearray(self.record);struct.pack_into('<H', record, 44, 65535)
        self.assertIsNone(self.decode(record)['moves'][0]['maximum_pp'])
        struct.pack_into('<H', record, 34, 65535)
        self.assertIn('held-item metadata unresolved', self.decode(record)['capabilities']['held_item']['reasons'])

    def test_exact_profile_gate_precedes_tables(self):
        with self.assertRaisesRegex(ValueError, 'ROM identity'):
            m.extract_tables(bytes(33554432))
        with self.assertRaisesRegex(ValueError, 'ROM identity'):
            a.inspect(b'', bytes(33554432))

    def test_auditor_does_not_import_production_or_writer(self):
        tree = ast.parse(Path(a.__file__).read_text())
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(sorted(imports), ['hashlib', 'pokemonstart_v022_creation_audit', 'struct'])

    def test_mint_controls_effective_nature_without_changing_native(self):
        record = bytearray(self.record);record[15] = 16
        row = self.decode(record)
        self.assertEqual((row['native_nature'], row['effective_nature']), (9, 15))
        self.assertFalse(row['five_matches'])
        self.assertIsNone(self.decode(bytearray(self.record[:15])+bytes([26])+self.record[16:])['effective_nature'])

    def test_modifier_item_does_not_get_ordinary_prediction(self):
        record = bytearray(self.record);struct.pack_into('<H', record, 34, 835)
        row = self.decode(record)
        self.assertIsNone(row['ordinary_expected_stats'])
        self.assertIn('held item 835 modifies cached non-HP stats', row['capabilities']['cached_stats']['reasons'])

    def test_whole_save_reconstruction_and_checksum_rejection(self):
        from test_v022_product_core import save
        raw = save()
        # Only artificial ROM identity and extraction are substituted; both
        # complete save parsers and all Party reconstruction execute normally.
        with patch.object(m, 'extract_tables', return_value=self.tables), patch.object(a, 'EXACT', hashlib.sha256(self.rom).hexdigest()):
            production, independent = m.inspect(raw, self.rom), a.inspect(raw, self.rom)
            a.compare(production, independent)
            corrupt = bytearray(raw); corrupt[0] ^= 1
            for parser in (m.inspect, a.inspect):
                with self.assertRaises(ValueError):
                    parser(bytes(corrupt), self.rom)


if __name__ == '__main__':
    unittest.main()
