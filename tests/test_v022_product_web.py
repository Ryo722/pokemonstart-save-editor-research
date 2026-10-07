import unittest
from unittest.mock import patch
from pathlib import Path
import pokemonstart_v022_product_web as w
from test_v022_product_core import save,ROM


class ProductWebTests(unittest.TestCase):
    def setUp(self):
        self.raw=save();self.workflow=w.ProductWorkflow(Path('unused.gba'))
        mock=patch.object(w.core.profile,'_check_rom_file',return_value=ROM)
        mock.start();self.addCleanup(mock.stop)
        self.request={'money':1234567,'party':[{'slot':0,'changes':{'friendship':200}}],
                      'items':{'potion_quantity':3}}

    def test_upload_preview_export_download_matches_core(self):
        self.workflow.upload('original.sav',self.raw)
        report=self.workflow.preview(self.request)
        self.request['money']=42 # Caller cannot mutate a retained preview.
        output,_=self.workflow.commit();download,name=self.workflow.download()
        expected,_=w.core.derive(self.raw,ROM,report['request'])
        self.assertEqual(expected,output);self.assertEqual(download,expected)
        self.assertNotEqual(name,'original.sav');self.assertTrue(name.endswith('_verified.sav'))
        self.assertEqual(self.raw,self.workflow.source_raw)
        report['request']['money']=99
        self.assertEqual(self.workflow.plan['request']['money'],1234567)

    def test_stale_source_rom_preview_output_fail_closed(self):
        self.workflow.upload('save.sav',self.raw);self.workflow.preview(self.request)
        self.workflow.commit();self.workflow.output_raw=b'bad'
        with self.assertRaises(ValueError):self.workflow.download()
        with self.assertRaises(ValueError):self.workflow.commit()
        self.workflow.preview(self.request)
        with patch.object(w.core.profile,'_check_rom_file',side_effect=ValueError('ROM changed')):
            with self.assertRaises(ValueError):self.workflow.commit()
        self.workflow.commit();self.workflow.source_raw=self.raw[:-1]+b'X'
        with self.assertRaises(ValueError):self.workflow.download()
        self.workflow.upload('save.sav',self.raw);self.workflow.preview(self.request)
        self.workflow.plan['output_sha256']='0'*64
        with self.assertRaises(ValueError):self.workflow.commit()
        with self.assertRaises(ValueError):self.workflow.upload('save.gba',self.raw)
        self.assertIsNone(self.workflow.source_raw)

    def test_invalidation_loopback_and_normal_numeric_input(self):
        self.assertEqual(w.server_options()['host'],'127.0.0.1')
        self.assertFalse(w.server_options()['on_air'])
        self.workflow.upload('save.sav',self.raw);self.workflow.preview(self.request);self.workflow.commit()
        self.workflow.invalidate()
        with self.assertRaises(ValueError):self.workflow.download()
        self.assertEqual(w.control_integer(100.0),100)
        for value in (True,1.5,'1',None):
            with self.assertRaises(ValueError):w.control_integer(value)

    def test_nicegui_controls_composed_preview_verified_download(self):
        if w.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        import asyncio,sys,os
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.number import Number
        from nicegui.elements.button import Button
        from nicegui.testing import user_simulation
        async def exercise():
            with patch.object(sys,'argv',['app','--rom','unused.gba']),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'product simulation'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    upload=next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                    await user.should_see('読み込み済み')
                    numbers=list(user.find(kind=Number).elements)
                    next(x for x in numbers if x.label=='Money').value=1234567
                    next(x for x in numbers if x.label=='Friendship — Party #1').value=200
                    next(x for x in numbers if x.label=='Quantity').value=3
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see('Money:')
                    user.find(kind=Button,content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button,content='検証済み .sav を保存').click()
                    download=await user.download.next()
                    expected,_=w.core.derive(self.raw,ROM,{'money':1234567,
                        'party':[{'slot':0,'changes':{'friendship':200}}],'items':{'potion_quantity':3}})
                    self.assertEqual(download.content,expected)
                    next(x for x in numbers if x.label=='Money').value=42
                    self.assertFalse(next(iter(user.find(kind=Button,content='検証済み .sav を保存').elements)).enabled)
        asyncio.run(exercise())
