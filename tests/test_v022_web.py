import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_v022_web as web
import pokemonstart_fastlab_v022_creation as core
import pokemonstart_v022_creation_audit as audit
import pokemonstart_save_verifier as verifier
from test_v022_composition import composed_fixture


class V022WebTests(unittest.TestCase):
    def setUp(self):
        self.raw=composed_fixture()
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source=Path(self.temporary.name)/'source.sav'
        self.source.write_bytes(self.raw)
        for attr in ('PARTY_SOURCE_SHA256','INVENTORY_SOURCE_SHA256','COMPOSED_SOURCE_SHA256'):
            p=patch.object(core,attr,audit.sha(self.raw));p.start();self.addCleanup(p.stop)
        p=patch.object(core.fl2,'_check_rom_file',return_value=core.fl2.EXPECTED_ROM_SHA256)
        p.start();self.addCleanup(p.stop)
        self.workflow=web.BrowserWorkflow(Path(self.temporary.name)/'exact.gba')

    def test_loopback_only(self):
        options=web.server_options()
        self.assertEqual(options['host'],'127.0.0.1')
        self.assertFalse(options['on_air'])
        self.assertFalse(options['reload'])
        for port in (True,0,80,65536):
            with self.assertRaises(ValueError):web.server_options(port)

    def test_both_new_operations_equal_independent_and_non_gui_core(self):
        for op in core.CREATION_OPERATIONS:
            report=self.workflow.upload('source.sav',self.raw)
            self.assertEqual(report['supported_write_operations'],list(core.CREATION_OPERATIONS))
            preview=self.workflow.preview(op,{})
            output,receipt=self.workflow.commit()
            downloaded,name=self.workflow.download()
            expected,_=core.derive_bytes(self.raw,core.fl2.EXPECTED_ROM_SHA256,op,{})
            self.assertEqual(output,expected)
            self.assertEqual(downloaded,expected)
            self.assertTrue(name.endswith('_verified.sav'))
            self.assertNotEqual(name,'source.sav')
            self.assertEqual(verifier.verify_bytes(output).file_sha256,preview['output_sha256'])
            self.assertTrue(receipt['independent_audit']['complete_candidate_equality'])
            self.assertEqual(self.source.read_bytes(),self.raw)

    def test_unknown_save_read_only_and_invalid_upload_clears_state(self):
        unknown=bytearray(self.raw);unknown[-1]^=1
        report=self.workflow.upload('unknown.sav',bytes(unknown))
        self.assertEqual(report['supported_write_operations'],[])
        self.assertIn('party',report['semantics'])
        with self.assertRaises(ValueError):self.workflow.preview('party_append',{})
        with self.assertRaises(ValueError):self.workflow.download()
        self.workflow.upload('source.sav',self.raw)
        self.workflow.preview('party_append',{})
        self.workflow.commit()
        with self.assertRaises(ValueError):self.workflow.upload('source.gba',self.raw)
        self.assertIsNone(self.workflow.source_raw)
        self.assertIsNone(self.workflow.output_raw)

    def test_failed_preview_stale_source_rom_and_output_fail_closed(self):
        self.workflow.upload('source.sav',self.raw)
        self.workflow.preview('party_append',{})
        self.workflow.commit()
        with self.assertRaises(ValueError):self.workflow.preview('inventory_insert',{'quantity':2})
        with self.assertRaises(ValueError):self.workflow.download()
        self.workflow.preview('inventory_insert',{})
        with patch.object(core.fl2,'_check_rom_file',side_effect=ValueError('ROM changed')):
            with self.assertRaises(ValueError):self.workflow.commit()
        self.workflow.commit()
        self.workflow.output_raw=self.workflow.output_raw[:-1]+b'X'
        with self.assertRaises(ValueError):self.workflow.download()
        self.assertIsNone(self.workflow.output_raw)
        self.workflow.preview('party_append',{})
        self.workflow.source_raw=self.workflow.source_raw[:-1]+b'Y'
        with self.assertRaises(ValueError):self.workflow.commit()

    def test_canonical_money_gate_still_unchanged(self):
        from test_fastlab_v022_money import _save
        money=core.fl2.money
        raw=_save()
        with patch.object(money,'INPUT_SHA256',core.fl2.sha(raw)):
            report=self.workflow.upload('money.sav',raw)
            self.assertEqual(report['supported_write_operations'],['money'])
            self.workflow.preview('money',{'money':money.TARGET_MONEY})
            output,_=self.workflow.commit()
            self.assertEqual(output,money.derive(raw)[0])
            with self.assertRaises(ValueError):self.workflow.preview('money',{'money':123})

    def test_canonical_party_and_inventory_dispatch_keep_existing_gates(self):
        from test_m3c_derived_stats_writer import synthetic
        from test_fastlab_v022_inventory_editor import inventory_synthetic
        party=core.fl2.party
        raw,_=synthetic()
        with patch.object(party,'SUPPORTED_INPUT_SHA256',core.fl2.sha(raw)):
            report=self.workflow.upload('party.sav',raw)
            self.assertEqual(report['supported_write_operations'],['party'])
            self.workflow.preview('party',{'friendship':51})
            output,_=self.workflow.commit()
            self.assertEqual(output,party.derive_bytes(raw,{'friendship':51})[0])
            with self.assertRaises(ValueError):self.workflow.preview('party',{'ball':4})
        inventory=core.fl2.inventory
        raw=inventory_synthetic()
        with patch.object(inventory,'SUPPORTED_INPUT_SHA256',core.fl2.sha(raw)):
            report=self.workflow.upload('items.sav',raw)
            self.assertEqual(report['supported_write_operations'],['inventory'])
            self.assertEqual(report['semantics']['regular_items']['entries'][0]['item_id'],13)
            self.workflow.preview('inventory',{'slot':0,'item_id':13,'quantity':3})
            output,_=self.workflow.commit()
            self.assertEqual(output,inventory.derive_bytes(raw,0,13,3)[0])

    def test_nicegui_browser_upload_preview_verified_download_both_operations(self):
        if web.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.select import Select
        from nicegui.elements.button import Button
        from nicegui.testing import user_simulation

        async def exercise():
            argv=['v022_web_simulation_app.py','--rom',str(self.workflow.rom_path)]
            with patch.object(sys,'argv',argv),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'v022 browser integration'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_web_simulation_app.py')) as user:
                    await user.open('/')
                    await user.should_see('ローカル .sav を選択')
                    upload=next(iter(user.find(kind=Upload).elements))
                    for op in core.CREATION_OPERATIONS:
                        await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                        await user.should_see('SUPPORTED')
                        selection=next(iter(user.find(kind=Select).elements))
                        selection.value=op
                        user.find(kind=Button,content='プレビュー').click()
                        await user.should_see('PREVIEW')
                        user.find(kind=Button,content='検証済み出力を作成').click()
                        await user.should_see('GENERATED')
                        user.find(kind=Button,content='検証済み .sav を保存').click()
                        response=await user.download.next()
                        expected,_=core.derive_bytes(self.raw,core.fl2.EXPECTED_ROM_SHA256,op,{})
                        self.assertEqual(response.content,expected)
                        self.assertEqual(self.source.read_bytes(),self.raw)
                    unknown=bytearray(self.raw);unknown[-1]^=1
                    await upload.handle_uploads([SmallFileUpload('unknown.sav','application/octet-stream',bytes(unknown))])
                    await user.should_see('READ_ONLY_UNSUPPORTED_WRITES')
                    for label in ('プレビュー','検証済み出力を作成','検証済み .sav を保存'):
                        self.assertFalse(next(iter(user.find(kind=Button,content=label).elements)).enabled)
        asyncio.run(exercise())
