import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import pokemonstart_v022_inventory_model as model
import pokemonstart_v022_inventory_audit as auditor
import pokemonstart_v022_inventory_editor as editor
import pokemonstart_v022_product_core as core
import pokemonstart_v022_product_web as web
from test_v022_inventory_model import synthetic_rom
from test_v022_product_core import save


def rom_fixture():
    raw = bytearray(synthetic_rom())
    for item in range(1, 839):
        if item == 375 or item in (4, 267, 289, 142):
            continue
        start = 0x15199C8 + item * 40
        name = [0xBB] + [0xA1 + int(c) for c in str(item)] + [0xFF]
        raw[start:start + 10] = bytes(name) + bytes(10 - len(name))
        struct.pack_into('<H', raw, start + 10, item)
        raw[start + 22] = 1
    return bytes(raw)


class MedicineEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = rom_fixture()
        cls.digest = hashlib.sha256(cls.rom).hexdigest()

    def setUp(self):
        for module in (model, auditor):
            gate = patch.object(module, 'ROM_SHA256', self.digest)
            gate.start(); self.addCleanup(gate.stop)
        def test_hash(value):
            if value not in (self.digest, core.profile.EXPECTED_ROM_SHA256):
                raise ValueError('synthetic test profile mismatch')
        gate = patch.object(core.profile, '_require_rom_hash', side_effect=test_hash)
        gate.start(); self.addCleanup(gate.stop)
        def test_file(path):
            if hashlib.sha256(path.read_bytes()).hexdigest() != self.digest:
                raise ValueError('synthetic ROM changed')
            return self.digest
        gate = patch.object(core.profile, '_check_rom_file', side_effect=test_file)
        gate.start(); self.addCleanup(gate.stop)
        self.raw = self.make_save([(533, 1), (14, 3), (13, 1)])

    def make_save(self, rows):
        raw = bytearray(save())
        verified = model.verifier.verify_bytes(raw)
        active = verified.slots[verified.active_slot]
        base = active.section(13).physical_sector * 4096
        raw[base + 0xADC:base + 0xFF0] = bytes(1300)
        raw[0x1E000:0x1EFF0] = bytes(0xFF0)
        for slot, row in enumerate(rows):
            offset = base + 0xADC + slot * 4 if slot < 325 else 0x1E000 + (slot - 325) * 4
            struct.pack_into('<HH', raw, offset, *row)
        struct.pack_into('<H', raw, 0x1E716, len(rows))
        return bytes(raw)

    def rows(self, raw):
        return [(e['item_id'], e['quantity']) for e in editor.inspect(raw, self.rom)['entries']]

    def check(self, source, operations, expected):
        frozen = bytes(source)
        out, report = editor.derive(source, self.rom, operations)
        self.assertEqual(self.rows(out), expected)
        self.assertTrue(auditor.audit_edit(source, out, self.rom, operations)['complete_output_equal'])
        self.assertEqual(out, editor.derive(source, self.rom, operations)[0])
        self.assertEqual(source, frozen)
        self.assertEqual(report['after']['occupied'], struct.unpack_from('<H', out, 0x1E716)[0])
        return out, report

    def test_composed_three_operations_and_unsupported_preservation(self):
        operations = [{'op':'set', 'item_id':14, 'quantity':7},
                      {'op':'remove', 'item_id':13},
                      {'op':'add', 'item_id':15, 'quantity':11}]
        out, report = self.check(self.raw, operations, [(533,1),(14,7),(15,11)])
        request = {'items':operations}
        combined, receipt = core.derive(self.raw, self.digest, request, rom_bytes=self.rom)
        self.assertEqual(combined, out)
        self.assertEqual(len(receipt['semantic_diff']), 3)
        self.assertTrue(report['independent_audit']['unrelated_bytes_preserved'])
        self.assertFalse(editor.inspect(out,self.rom)['give_all_enabled'])
        with self.assertRaises(ValueError):editor.derive(self.raw,self.rom,[{'op':'remove','item_id':533}])

    def test_e2_composes_with_unchanged_party_money_families(self):
        request={'money':1234567,'party':[{'slot':0,'changes':{'friendship':1}}],
                 'items':[{'op':'set','item_id':13,'quantity':8}]}
        output,receipt=core.derive(self.raw,core.profile.EXPECTED_ROM_SHA256,request,rom_bytes=self.rom)
        self.assertEqual(core.money.inspect(output,core.profile.EXPECTED_ROM_SHA256)['money'],1234567)
        self.assertEqual(core.v.verify_bytes(output).party[0].friendship,1)
        self.assertEqual(self.rows(output),[(533,1),(14,3),(13,8)])
        self.assertEqual(set(receipt['families']),{'money','party_0','items'})

    def neutral_ids(self, count):
        return [i for i in range(1,839) if i not in (4,142,267,289,375,13,14,15)
                and model.classification(i)==0][:count]

    def test_scatter_add_set_remove_at_0_324_325_699(self):
        for slot in (0,324,325,699):
            with self.subTest(slot=slot):
                ids = self.neutral_ids(slot)
                raw = self.make_save([(i,1) for i in ids])
                out,_ = self.check(raw,[{'op':'add','item_id':13,'quantity':999}],[(i,1) for i in ids]+[(13,999)])
                base=model.verifier.verify_bytes(raw).slots[model.verifier.verify_bytes(raw).active_slot].section(13).physical_sector*4096
                location=base+0xADC+4*slot if slot<325 else 0x1E000+4*(slot-325)
                self.assertEqual(struct.unpack_from('<HH',out,location),(13,999))
                changed,_ = self.check(out,[{'op':'set','item_id':13,'quantity':1}],[(i,1) for i in ids]+[(13,1)])
                self.check(changed,[{'op':'remove','item_id':13}],[(i,1) for i in ids])

    def test_compaction_crosses_split_preserving_four_bytes(self):
        ids=self.neutral_ids(327)
        rows=[(item, i%999+1) for i,item in enumerate(ids)]
        rows.insert(324,(13,4))
        raw=self.make_save(rows)
        self.check(raw,[{'op':'remove','item_id':13}],rows[:324]+rows[325:])

    def test_unsupported_before_after_target_preserved(self):
        rows=[(533,77),(13,999),(30,31),(14,3)]
        raw=self.make_save(rows)
        self.check(raw,[{'op':'remove','item_id':13}],[(533,77),(30,31),(14,3)])

    def test_full_pocket_rejection(self):
        raw=self.make_save([(i,1) for i in self.neutral_ids(700)])
        self.assertEqual(len(editor.inspect(raw,self.rom)['entries']),700)
        with self.assertRaisesRegex(ValueError,'full'):
            editor.derive(raw,self.rom,[{'op':'add','item_id':13,'quantity':1}])

    def test_empty_pocket_and_last_removal(self):
        raw=self.make_save([])
        out,_=self.check(raw,[{'op':'add','item_id':13,'quantity':1}],[(13,1)])
        empty,_=self.check(out,[{'op':'remove','item_id':13}],[])
        self.assertEqual(empty,raw)

    def test_quantity_and_operation_errors(self):
        for quantity in (0,-1,1000,65535,True,1.5,'2'):
            with self.subTest(quantity=quantity),self.assertRaises(ValueError):
                editor.derive(self.raw,self.rom,[{'op':'set','item_id':13,'quantity':quantity}])
        for ops in ([],{},[{'op':'set','item_id':15,'quantity':1}],
                    [{'op':'add','item_id':13,'quantity':1}],
                    [{'op':'remove','item_id':13,'quantity':0}],
                    [{'op':'remove','item_id':13}]*2,[{'op':'set','item_id':533,'quantity':1}]):
            with self.subTest(ops=ops),self.assertRaises(ValueError):editor.derive(self.raw,self.rom,ops)

    def test_holes_duplicates_selector_count_key_alternate_invalid(self):
        active=model.verifier.verify_bytes(self.raw).slots[model.verifier.verify_bytes(self.raw).active_slot]
        base13=active.section(13).physical_sector*4096
        base4=active.section(4).physical_sector*4096
        base0=active.section(0).physical_sector*4096
        corrupt=[]
        for offset,value in ((0x1E716,b'\x02\x00'),(base13+0x6B6,b'\xff\xff'),
                             (base13+0xAE0,bytes(4)),(base13+0xADC,struct.pack('<HH',57,1)),
                             (base13+0xADC,struct.pack('<HH',13,1)),
                             (base13+0xADC,struct.pack('<HH',839,1))):
            b=bytearray(self.raw);b[offset:offset+len(value)]=value;corrupt.append(bytes(b))
        b=bytearray(self.raw);b[base4+0xE09]|=8;corrupt.append(bytes(b))
        b=bytearray(self.raw);struct.pack_into('<I',b,base0+0xF20,1)
        struct.pack_into('<H',b,base0+0xFF6,model.verifier.calculate_save_checksum(b[base0:base0+0xF24]));corrupt.append(bytes(b))
        for raw in corrupt:
            for reader in (model.restricted,auditor.restricted):
                with self.assertRaises(ValueError):reader(raw,self.rom)
            with self.assertRaises(ValueError):editor.derive(raw,self.rom,[{'op':'set','item_id':13,'quantity':5}])

    def test_auditor_detects_unrelated_byte_and_forged_semantics(self):
        operations=[{'op':'set','item_id':13,'quantity':9}]
        out,_=editor.derive(self.raw,self.rom,operations)
        b=bytearray(out);b[-1]^=1
        with self.assertRaises(ValueError):auditor.audit_edit(self.raw,bytes(b),self.rom,operations)
        with self.assertRaises(ValueError):auditor.audit_edit(self.raw,out,self.rom,[{'op':'remove','item_id':13}])

    def test_exclusive_export_and_immutable_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.sav';rom=Path(d)/'input.gba';target=Path(d)/'separate.sav'
            source.write_bytes(self.raw);rom.write_bytes(self.rom)
            ops=[{'op':'set','item_id':13,'quantity':6}]
            with self.assertRaises(ValueError):editor.export(source,target,rom,ops)
            def synthetic_private(path, label, *, must_exist):
                resolved=Path(path).resolve(strict=must_exist)
                if not resolved.is_relative_to(Path(d).resolve()):
                    raise ValueError('outside synthetic private boundary')
                return resolved
            with patch.object(editor.profile,'_private_file',side_effect=synthetic_private):
                editor.export(source,target,rom,ops)
                self.assertEqual(source.read_bytes(),self.raw);self.assertEqual(rom.read_bytes(),self.rom)
                self.assertEqual(target.stat().st_mode & 0o777,0o600)
                with self.assertRaises(FileExistsError):editor.export(source,target,rom,ops)
                with self.assertRaises(ValueError):editor.export(source,source,rom,ops)

    def test_workflow_equality_stale_source_and_rom(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.gba';p.write_bytes(self.rom)
            workflow=web.ProductWorkflow(p)
            ops={'items':[{'op':'set','item_id':13,'quantity':9}]}
            workflow.upload('source.sav',self.raw);workflow.preview(ops)
            out,_=workflow.commit();self.assertEqual(workflow.download()[0],out)
            self.assertEqual(out,core.derive(self.raw,self.digest,ops,rom_bytes=self.rom)[0])
            workflow.source_raw=self.raw[:-1]+b'X'
            with self.assertRaises(ValueError):workflow.download()
            workflow.upload('source.sav',self.raw);workflow.preview(ops)
            p.write_bytes(b'changed')
            with self.assertRaises(ValueError):workflow.commit()

    def test_nicegui_e2_composed_controls_and_download(self):
        if web.ui is None:self.skipTest('NiceGUI unavailable')
        import asyncio, os, sys
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.number import Number
        from nicegui.elements.checkbox import Checkbox
        from nicegui.elements.select import Select
        from nicegui.elements.button import Button
        from nicegui.testing import user_simulation
        with tempfile.TemporaryDirectory() as directory:
            rom_path=Path(directory)/'synthetic.gba';rom_path.write_bytes(self.rom)
            async def exercise():
                with patch.object(sys,'argv',['app','--rom',str(rom_path)]),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'E2 GUI equality'}):
                    async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                        await user.open('/')
                        upload=next(iter(user.find(kind=Upload).elements))
                        await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                        await user.should_see('読み込み済み')
                        numbers=list(user.find(kind=Number).elements)
                        next(x for x in numbers if x.label=='Quantity — A14').value=7
                        boxes=list(user.find(kind=Checkbox).elements)
                        next(x for x in boxes if x.text=='Remove — A13').value=True
                        next(x for x in boxes if x.text=='Add Item').value=True
                        next(x for x in user.find(kind=Select).elements if x.label=='Item').value=15
                        next(x for x in numbers if x.label=='Quantity — Add Item').value=11
                        self.assertFalse(any(x.label=='Quantity — A533' for x in numbers))
                        user.find(kind=Button,content='Preview').click()
                        await user.should_see('A15: x0 → x11')
                        user.find(kind=Button,content='検証して別 save を生成').click()
                        await user.should_see('検証済みの別 save を生成しました。')
                        user.find(kind=Button,content='検証済み .sav を保存').click()
                        download=await user.download.next()
                        ops=[{'op':'set','item_id':14,'quantity':7},{'op':'remove','item_id':13},
                             {'op':'add','item_id':15,'quantity':11}]
                        self.assertEqual(download.content,editor.derive(self.raw,self.rom,ops)[0])
                        next(x for x in numbers if x.label=='Quantity — A14').value=8
                        self.assertFalse(next(iter(user.find(kind=Button,content='検証済み .sav を保存').elements)).enabled)
            asyncio.run(exercise())

    def test_optional_private_gui_export_exclusive_and_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);rom=root/'synthetic.gba';rom.write_bytes(self.rom)
            workflow=web.ProductWorkflow(rom)
            workflow.upload('source.sav',self.raw)
            workflow.preview({'items':[{'op':'set','item_id':13,'quantity':9}]})
            output,_=workflow.commit()
            with self.assertRaises(ValueError):workflow.export_verified(root)
            with patch.object(web.core.profile,'PRIVATE_ROOT',root.resolve()):
                target=workflow.export_verified(root)
                self.assertEqual(target.read_bytes(),output)
                self.assertNotEqual(target.name,'source.sav')
                self.assertEqual(target.stat().st_mode&0o777,0o600)
                with self.assertRaises(FileExistsError):workflow.export_verified(root)
                workflow.invalidate()
                with self.assertRaises(ValueError):workflow.export_verified(root)
