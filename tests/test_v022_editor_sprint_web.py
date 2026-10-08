"""Give All / shiny / read-only Box controls in the practical GUI; synthetic saves/ROM only."""
import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import pokemonstart_v022_product_web as web
import test_v022_creation_writer as fixture


class EditorSprintWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.rom=fixture.inputs(count=3)
        cls.digest=web.core.profile.sha(cls.rom)

    def setUp(self):
        fixture.CreationTests.setUp(self)
        check=patch.object(web.core.profile,'_check_rom_file',return_value=self.digest)
        check.start();self.addCleanup(check.stop)
        original=Path.read_bytes
        read=patch.object(Path,'read_bytes',autospec=True,
                          side_effect=lambda p:self.rom if p.name=='unused.gba' else original(p))
        read.start();self.addCleanup(read.stop)

    def test_inspection_reports_shiny_give_all_and_box_state(self):
        report=web.core.inspect(self.raw,self.digest,rom_bytes=self.rom)
        self.assertTrue(all(type(mon.get('shiny')) is bool for mon in report['party']))
        self.assertTrue(report['items']['give_all']['enabled'])
        self.assertEqual(report['items']['give_all']['quantity'],99)
        # The synthetic ROM is not the exact build: the Box viewer fails closed.
        self.assertIsNone(report['box'])
        self.assertIn('box',report['rejections'])

    def test_core_shiny_and_give_all_compose_with_semantic_preview(self):
        report=web.core.inspect(self.raw,self.digest,rom_bytes=self.rom)
        slot=next(m['slot'] for m in report['party'] if m['capabilities'].get('shiny'))
        target=not report['party'][slot]['shiny']
        output,transaction=web.core.derive(self.raw,self.digest,
            {'party':[{'slot':slot,'changes':{'shiny':target}}],'items':[{'op':'give_all'}]},rom_bytes=self.rom)
        after=web.core.inspect(output,self.digest,rom_bytes=self.rom)
        self.assertEqual(after['party'][slot]['shiny'],target)
        self.assertFalse(after['items']['give_all']['enabled'])
        self.assertIn(f'Party #{slot+1} Shiny: {not target} → {target}',transaction['semantic_diff'])
        self.assertTrue(all(e['quantity']>=99 for e in after['items']['entries']
                            if e['item_id'] in after['items']['supported_names']))
        with self.assertRaisesRegex(ValueError,'only Items operation'):
            web.core.derive(self.raw,self.digest,{'items':[{'op':'give_all'},{'op':'remove','item_id':13}]},
                            rom_bytes=self.rom)

    def test_nicegui_give_all_shiny_and_box_tab(self):
        if web.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.button import Button
        from nicegui.elements.checkbox import Checkbox
        from nicegui.elements.number import Number
        from nicegui.testing import user_simulation
        report=web.core.inspect(self.raw,self.digest,rom_bytes=self.rom)
        slot=next(m['slot'] for m in report['party'] if m['capabilities'].get('shiny'))
        target=not report['party'][slot]['shiny']

        async def exercise():
            with patch.object(sys,'argv',['app','--rom','unused.gba']),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'sprint GUI'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    await user.should_see('対応機能 / 非対応機能')
                    upload=next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                    await user.should_see('読み込み済み')
                    await user.should_see('PC Box 読み取り非対応')
                    boxes={c.text:c for c in user.find(kind=Checkbox).elements}
                    give_all=next(c for t,c in boxes.items() if t.startswith('Give All Supported Items'))
                    self.assertTrue(give_all.enabled)
                    # Give All refuses to combine with another Items change.
                    give_all.value=True
                    quantity=next(x for x in user.find(kind=Number).elements if x.label.startswith('Quantity — '))
                    original=quantity.value;quantity.value=7
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see('Give All は他の Items 変更と同時に使えません')
                    quantity.value=original
                    boxes[f'Shiny（色違い） — Party #{slot+1}'].value=target
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see(f'Party #{slot+1} Shiny: {not target} → {target}')
                    user.find(kind=Button,content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button,content='検証済み .sav を保存').click()
                    download=await user.download.next()
                    expected,_=web.core.derive(self.raw,self.digest,
                        {'party':[{'slot':slot,'changes':{'shiny':target}}],'items':[{'op':'give_all'}]},
                        rom_bytes=self.rom)
                    self.assertEqual(download.content,expected)
        asyncio.run(exercise())


if __name__=='__main__':unittest.main()
