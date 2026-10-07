"""Semantic creation GUI/workflow, synthetic saves/ROM only."""
import asyncio
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pokemonstart_v022_product_web as web
import test_v022_creation_writer as fixture


class CreationWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.rom=fixture.inputs()
        cls.digest=web.core.profile.sha(cls.rom)
    def setUp(self):
        fixture.CreationTests.setUp(self)
        mock=patch.object(web.core.profile,'_check_rom_file',return_value=self.digest)
        mock.start();self.addCleanup(mock.stop)
        original=Path.read_bytes
        mock=patch.object(Path,'read_bytes',autospec=True,side_effect=lambda p:self.rom if p.name=='unused.gba' else original(p))
        mock.start();self.addCleanup(mock.stop)
    def test_separate_exclusive_export_stale_source_rom_and_output(self):
        workflow=web.ProductWorkflow(Path('unused.gba'))
        report=workflow.upload('source.sav',self.raw)
        self.assertEqual(report['creator']['first_slot'],3)
        workflow.preview({'create':[self.request,self.request]});output,_=workflow.commit()
        self.assertEqual(web.core.v.verify_bytes(output).party_count,5)
        self.assertEqual(workflow.source_raw,self.raw)
        with tempfile.TemporaryDirectory() as directory,patch.object(web.core.profile,'PRIVATE_ROOT',Path(directory).resolve()):
            destination=workflow.export_verified(directory)
            self.assertEqual(destination.read_bytes(),output)
            with self.assertRaises(FileExistsError):workflow.export_verified(directory)
        workflow.output_raw=output[:-1]+b'X'
        with self.assertRaises(ValueError):workflow.download()
        workflow.preview({'create':[self.request]})
        with patch.object(web.core.profile,'_check_rom_file',side_effect=ValueError('ROM changed')):
            with self.assertRaises(ValueError):workflow.commit()
        workflow.source_raw=self.raw[:-1]+b'X'
        with self.assertRaises(ValueError):workflow.commit()
    def test_nicegui_two_creations_semantic_preview_download_reopen(self):
        if web.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        import sys
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.button import Button
        from nicegui.elements.checkbox import Checkbox
        from nicegui.elements.number import Number
        from nicegui.testing import user_simulation
        async def exercise():
            with patch.object(sys,'argv',['app','--rom','unused.gba']),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'E4 creation simulation'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    upload=next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                    await user.should_see('読み込み済み')
                    boxes={c.text:c for c in user.find(kind=Checkbox).elements if c.text.startswith('Create Pokémon')}
                    self.assertFalse(boxes['Create Pokémon — Party #5'].enabled)
                    boxes['Create Pokémon — Party #4'].value=True
                    self.assertTrue(boxes['Create Pokémon — Party #5'].enabled)
                    boxes['Create Pokémon — Party #5'].value=True
                    next(x for x in user.find(kind=Number).elements if x.label=='Create Level — Party #5').value=20
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see('Create Pokémon — Party #4:')
                    await user.should_see('Create Pokémon — Party #5:')
                    user.find(kind=Button,content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button,content='検証済み .sav を保存').click()
                    download=await user.download.next()
                    base={'species':1,'level':3,'nature':0,'friendship':70,'ability':7,'held_item':0,
                          'ivs':[0]*6,'evs':[0]*6,'moves':[33,0,0,0]}
                    expected,_=web.core.derive(self.raw,self.digest,{'create':[base,{**base,'level':20}]},rom_bytes=self.rom)
                    self.assertEqual(download.content,expected)
                    boxes['Create Pokémon — Party #4'].value=False
                    self.assertFalse(boxes['Create Pokémon — Party #5'].value)
                    self.assertFalse(boxes['Create Pokémon — Party #5'].enabled)
                    self.assertFalse(next(iter(user.find(kind=Button,content='検証済み .sav を保存').elements)).enabled)
                    await upload.handle_uploads([SmallFileUpload('output.sav','application/octet-stream',expected)])
                    await user.should_see('Party #6 — Empty')
        asyncio.run(exercise())

if __name__=='__main__':unittest.main()
