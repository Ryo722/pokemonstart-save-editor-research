"""Candidate Box 1-19 existing-record editor; synthetic saves/ROM only."""
import struct
import unittest
from unittest.mock import patch

import pokemonstart_v022_box_audit as box_audit
import pokemonstart_v022_box_model as box
import pokemonstart_v022_box_writer as writer
import pokemonstart_v022_inventory_audit as inventory_audit
import pokemonstart_v022_inventory_model as inventory
import pokemonstart_v022_party_audit as party_audit
import pokemonstart_v022_party_model as model
import pokemonstart_v022_product_core as core
from test_v022_party_writer import synthetic_inputs


class BoxWriterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw, rom = synthetic_inputs()
        rom = bytearray(rom)
        struct.pack_into('<25I', rom, box.BOX_TABLE, *box.EXPECTED_POINTERS)
        cls.rom = bytes(rom)
        cls.digest = model.sha(cls.rom)
        cls.source = raw

    def setUp(self):
        for module, attr in ((model, 'ROM_SHA256'), (party_audit, 'EXACT'), (inventory, 'ROM_SHA256'),
                             (inventory_audit, 'ROM_SHA256')):
            gate = patch.object(module, attr, self.digest); gate.start(); self.addCleanup(gate.stop)
        gate = patch.object(core.profile, '_require_rom_hash', side_effect=lambda x: None if x == self.digest
                            else (_ for _ in ()).throw(ValueError('synthetic exact gate')))
        gate.start(); self.addCleanup(gate.stop)
        verified = model.verifier.verify_bytes(self.source)
        self.active = verified.slots[verified.active_slot]
        base = self.active.section(1).physical_sector * 4096 + 0x38
        self.party = self.source[base:base + 100]
        self.tables = model.extract_tables(self.rom)
        self.record = writer.compress(self.party)
        # Boxes 1, 3 #11 (straddles a section boundary), 19 and 24 (read-only).
        self.raw = self.place(self.source, [(0, 0), (2, 10), (18, 29), (23, 29)], self.record)

    def place(self, raw, locations, record):
        out = bytearray(raw)
        for box_index, slot in locations:
            start = box.EXPECTED_POINTERS[box_index] + slot * box.RECORD_SIZE
            for i, value in enumerate(record):
                out[box._file_offset(self.active, start + i)] = value
        for section in range(14):
            base = self.active.section(section).physical_sector * 4096
            length = model.verifier.SECTION_LENGTHS[section]
            struct.pack_into('<H', out, base + 0xFF6, model.verifier.calculate_save_checksum(out[base:base + length]))
        return bytes(out)

    def test_round_trip_matches_party_semantics(self):
        expanded = writer.expand(self.record, self.tables)
        self.assertEqual(writer.compress(expanded), self.record)
        for key in ('species', 'experience', 'ivs', 'evs', 'friendship', 'held_item', 'effective_nature',
                    'resolved_ability'):
            self.assertEqual(model.decode_record(expanded, 0, self.tables)[key],
                             model.decode_record(self.party, 0, self.tables)[key], key)
        self.assertEqual(box_audit._expand(self.record, self.rom), expanded)

    def test_edits_compose_with_independent_reconstruction(self):
        edits = [{'box': 1, 'position': 1, 'changes': {'friendship': 201, 'ivs': [1, 2, 3, 4, 5, 6]}},
                 {'box': 3, 'position': 11, 'changes': {'shiny': True, 'level': 30}},
                 {'box': 19, 'position': 30, 'changes': {'moves': {1: 33}, 'pp_up': {0: 3}}}]
        out, receipt = writer.derive(self.raw, self.rom, edits)
        self.assertTrue(receipt['independent_audit']['complete_output_equal'])
        rows = {(r['box'], r['position']): r for r in box.inspect(out, self.rom)['occupied']}
        self.assertEqual(rows[(1, 1)]['friendship'], 201)
        self.assertEqual(rows[(1, 1)]['ivs'], [1, 2, 3, 4, 5, 6])
        self.assertTrue(rows[(3, 11)]['shiny'])
        self.assertEqual(rows[(3, 11)]['level_from_exp'], 30)
        self.assertEqual(rows[(19, 30)]['moves'][1], 33)
        original = {(r['box'], r['position']): r for r in box.inspect(self.raw, self.rom)['occupied']}
        self.assertEqual(rows[(24, 30)], original[(24, 30)])
        # Only record bytes and storage checksums change.
        changed = {o // 4096 for o in receipt['changed_offsets']}
        storage = {self.active.section(s).physical_sector for s in range(5, 14)}
        self.assertTrue(changed <= storage)
        composed, report = core.derive(self.raw, self.digest, {'box': edits[:1], 'money': 1234}, rom_bytes=self.rom)
        self.assertTrue(report['independent_e3_audit']['complete_output_equal'])
        before = writer.semantic(self.record, self.tables)['friendship']
        self.assertIn(f'Box 1 #1 Friendship: {before} → 201', report['semantic_diff'])

    def test_fail_closed_cases(self):
        cases = [([{'box': 24, 'position': 30, 'changes': {'friendship': 1}}], 'Boxes 1-19'),
                 ([{'box': 1, 'position': 2, 'changes': {'friendship': 1}}], 'empty'),
                 ([{'box': 1, 'position': 1, 'changes': {'pp': {0: 1}}}], 'PP is not stored'),
                 ([{'box': 1, 'position': 1, 'changes': {'friendship': 1}}] * 2, 'duplicate'),
                 ([{'box': 1, 'position': 1, 'changes': {'species': 2, 'shiny': True}}], 'separate')]
        for edits, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                writer.derive(self.raw, self.rom, edits)
        egg = bytearray(self.record); egg[57] |= 0x40
        raw = self.place(self.raw, [(0, 1)], bytes(egg))
        with self.assertRaisesRegex(ValueError, 'rejected'):
            writer.derive(raw, self.rom, [{'box': 1, 'position': 2, 'changes': {'friendship': 1}}])
        lossy = bytearray(self.record); lossy[39:44] = (0x3FF).to_bytes(5, 'little')
        raw = self.place(self.raw, [(0, 2)], bytes(lossy))
        self.assertFalse(writer.eligibility(raw, self.rom, 1, 3)['eligible'])

    def test_independent_audit_rejects_tampering(self):
        edits = [{'box': 1, 'position': 1, 'changes': {'friendship': 9}}]
        out, _ = writer.derive(self.raw, self.rom, edits)
        tampered = bytearray(out)
        offset = box._file_offset(self.active, box.EXPECTED_POINTERS[0] + 37)
        tampered[offset] = 10
        with self.assertRaises(ValueError):
            box_audit.audit_box_edit(self.raw, bytes(tampered), self.rom, edits)
        with self.assertRaises(ValueError):
            box_audit.audit_box_edit(self.raw, out, self.rom, [{'box': 1, 'position': 1, 'changes': {'friendship': 8}}])

    def test_inspection_marks_editable_rows(self):
        report = core.inspect(self.raw, self.digest, rom_bytes=self.rom)
        rows = {(r['box'], r['position']): r for r in report['box']['occupied']}
        self.assertTrue(rows[(1, 1)]['editable'])
        self.assertFalse(rows[(24, 30)]['editable'])
        self.assertEqual(rows[(1, 1)]['semantic']['friendship'], writer.semantic(self.record, self.tables)['friendship'])

    def test_nicegui_box_grid_edit_preview_and_download(self):
        import asyncio, os, sys
        from pathlib import Path
        import pokemonstart_v022_product_web as web
        if web.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.button import Button
        from nicegui.elements.checkbox import Checkbox
        from nicegui.elements.number import Number
        from nicegui.testing import user_simulation
        name = writer.semantic(self.record, self.tables)['species_name']

        async def exercise():
            with patch.object(web.ProductWorkflow, '_read_rom', return_value=self.rom), \
                    patch.object(core.profile, '_check_rom_file', return_value=self.digest), \
                    patch.object(sys, 'argv', ['app', '--rom', 'synthetic.gba']), \
                    patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'Box GUI synthetic'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    upload = next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('source.sav', 'application/octet-stream', self.raw)])
                    await user.should_see('読み込み済み')
                    await user.should_see(f'1. {name}')
                    user.find(kind=Button, content=f'1. {name}').click()
                    await user.should_see('Friendship — Box 1 #1')
                    next(x for x in user.find(kind=Number).elements if x.label == 'Friendship — Box 1 #1').value = 77
                    next(c for c in user.find(kind=Checkbox).elements if c.text == 'Shiny（色違い） — Box 1 #1').value = True
                    user.find(kind=Button, content='Preview').click()
                    await user.should_see('Box 1 #1 Friendship:')
                    await user.should_see('Box 1 #1 Shiny: False → True')
                    user.find(kind=Button, content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button, content='検証済み .sav を保存').click()
                    download = await user.download.next()
                    expected, _ = core.derive(self.raw, self.digest, {'box': [{'box': 1, 'position': 1,
                        'changes': {'shiny': True, 'friendship': 77}}]}, rom_bytes=self.rom)
                    self.assertEqual(download.content, expected)
        asyncio.run(exercise())


if __name__ == '__main__':
    unittest.main()
