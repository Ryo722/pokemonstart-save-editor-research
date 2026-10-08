import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import pokemonstart_v022_e5_acceptance as e5
import pokemonstart_v022_product_web as web
import test_v022_creation_writer as fixture


class E5AcceptanceTests(unittest.TestCase):
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

    def test_recipe_composes_all_adopted_families_and_audits_exact_output(self):
        receipt=e5.prepare(self.raw,self.rom)
        request=receipt['transaction']['request']
        self.assertEqual(set(request),{'money','party','items','create'})
        self.assertTrue(any(row['op']=='set' for row in request['items']))
        output,_=web.core.derive(self.raw,self.digest,request,rom_bytes=self.rom)
        report=e5.audit_export(self.raw,output,self.rom,receipt)
        self.assertTrue(report['complete_output_equal'])
        self.assertEqual(web.core.v.verify_bytes(output).party_count,4)
        wrong=output[:-1]+bytes([output[-1]^1])
        with self.assertRaisesRegex(ValueError,'differs'):
            e5.audit_export(self.raw,wrong,self.rom,receipt)

    def test_cycle2_reopens_progressed_candidate_without_hash_eligibility(self):
        receipt=e5.prepare(self.raw,self.rom)
        output,_=web.core.derive(self.raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        slot=receipt['created_slot']
        second=e5.prepare_cycle2(output,self.rom,created_slot=slot)
        self.assertEqual(second['transaction']['request']['party'][0]['slot'],slot)
        second_output,_=web.core.derive(output,self.digest,second['transaction']['request'],rom_bytes=self.rom)
        result=e5.audit_export(output,second_output,self.rom,second)
        self.assertEqual(result['status'],'GUI_OUTPUT_EQUALS_INDEPENDENT_CORE_AND_AUDIT')
        from test_v022_product_acceptance import resave
        returned=e5.check_cycle2_return(output,resave(second_output),self.rom,second)
        self.assertEqual(returned['status'],'MACHINE_CYCLE2_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED')

    def test_cycle1_return_checker_reconstructs_save_transition(self):
        from test_v022_product_acceptance import resave
        receipt=e5.prepare(self.raw,self.rom)
        output,_=web.core.derive(self.raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        result=e5.check_cycle1_return(self.raw,resave(output),self.rom,receipt)
        self.assertEqual(result['status'],'MACHINE_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED')
        self.assertTrue(result['continued_e1_e2_e3_e4_eligibility'])

    @staticmethod
    def _with_record(returned, donor, slot, offsets=range(100)):
        """Restore donor Party record bytes in the returned save, as if the edit was lost."""
        v=web.core.v
        def location(raw):
            result=v.verify_bytes(raw);section=result.slots[result.active_slot].section(1)
            return section.physical_sector*4096
        base,donor_base=location(returned),location(donor)
        out=bytearray(returned);start=v.PARTY_OFFSET+slot*100
        for offset in offsets:out[base+start+offset]=donor[donor_base+start+offset]
        checksum=v.calculate_save_checksum(out[base:base+v.SECTION_LENGTHS[1]])
        out[base+0xFF6:base+0xFF8]=checksum.to_bytes(2,'little')
        return bytes(out)

    def test_cycle1_return_rejects_lost_requested_party_field(self):
        from test_v022_product_acceptance import resave
        receipt=e5.prepare(self.raw,self.rom)
        output,_=web.core.derive(self.raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        slot=receipt['transaction']['request']['party'][0]['slot']
        self.assertIn('friendship',receipt['transaction']['request']['party'][0]['changes'])
        lost=self._with_record(resave(output),self.raw,slot,offsets=(41,))  # friendship byte
        with self.assertRaisesRegex(ValueError,'requested Party state did not persist: slot .* friendship'):
            e5.check_cycle1_return(self.raw,lost,self.rom,receipt)

    def test_cycle2_return_rejects_lost_requested_friendship(self):
        from test_v022_product_acceptance import resave
        receipt=e5.prepare(self.raw,self.rom)
        output,_=web.core.derive(self.raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        slot=receipt['created_slot']
        second=e5.prepare_cycle2(output,self.rom,created_slot=slot)
        second_output,_=web.core.derive(output,self.digest,second['transaction']['request'],rom_bytes=self.rom)
        self.assertTrue(e5.check_cycle2_return(output,resave(second_output),self.rom,second)['requested_fields_persisted'])
        lost=self._with_record(resave(second_output),output,slot)
        with self.assertRaisesRegex(ValueError,'Cycle 2 slot .* friendship'):
            e5.check_cycle2_return(output,lost,self.rom,second)

    def test_persistence_rules_allow_only_gameplay_monotone_drift(self):
        actual={'stored_level':13,'experience':900,'evs':[1,0,0,0,0,0],'held_item':0,
                'friendship':70,'resolved_ability':50,'species':19,'ivs':[1]*6,'effective_nature':3,
                'moves':[{'move_id':33,'pp':30,'pp_up_count':0,'maximum_pp':35}]+[{'move_id':0,'pp':0,'pp_up_count':0,'maximum_pp':0}]*3}
        expected={'level':12,'experience':800,'evs':[0]*6,'held_item':139,'friendship':70,
                  'ability':50,'species':19,'ivs':[1]*6,'effective_nature':3}
        e5._assert_requested_persisted({'level':12,'experience':800,'evs':[0]*6,'held_item':139,
            'friendship':70,'ability':50,'species':19,'ivs':[1]*6,'effective_nature':3,
            'moves':{0:33},'pp':{0:35},'pp_up':{0:0}},expected,actual,'test')
        for field,value in (('friendship',71),('level',14),('species',20),('held_item',1)):
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'did not persist'):
                e5._assert_requested_persisted({field:value},{**expected,field:value},actual,'test')
        with self.assertRaisesRegex(ValueError,'no rule'):
            e5._assert_requested_persisted({'unknown':1},expected,actual,'test')

    def test_actual_gui_maps_all_four_families_and_invalidates_preview(self):
        if web.ui is None:self.skipTest('NiceGUI optional dependency unavailable')
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.button import Button
        from nicegui.elements.checkbox import Checkbox
        from nicegui.elements.number import Number
        from nicegui.elements.select import Select
        from nicegui.elements.expansion import Expansion
        from nicegui.testing import user_simulation
        from nicegui.app.app_config import AppConfig
        if not hasattr(AppConfig,'reconnect_timeout'):AppConfig.reconnect_timeout=5
        async def exercise():
            receipt=e5.prepare(self.raw,self.rom)
            request=receipt['transaction']['request'];edit=request['party'][0]
            captured=[];derive=web.core.derive
            delivered=[]
            def record(raw,rom_hash,submitted,**kwargs):
                output=derive(raw,rom_hash,submitted,**kwargs)
                captured.append({'input_matches':raw==self.raw,'rom_matches':rom_hash==self.digest,
                                 'request':__import__('copy').deepcopy(submitted),
                                 'output_matches':output[0]==derive(self.raw,self.digest,request,rom_bytes=self.rom)[0]})
                return output
            from nicegui.testing.user_download import UserDownload
            original_content=UserDownload.content
            def record_download(download,content,filename=None,media_type=''):
                delivered.append(content)
                return original_content(download,content,filename,media_type)
            with patch.object(sys,'argv',['app','--rom','unused.gba']),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'E5 composed GUI'}):
              with patch.object(web.core,'derive',record),patch.object(UserDownload,'content',record_download):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    upload=next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('owner.sav','application/octet-stream',self.raw)])
                    await user.should_see('読み込み済み')
                    for index in range(1,7):await user.should_see(f'Party #{index}')
                    numbers=list(user.find(kind=Number).elements)
                    number=lambda label:next(x for x in numbers if x.label==label)
                    number('Money').value=request['money']
                    party_card=next(x for x in user.find(kind=Expansion).elements
                                    if x.text.startswith(f"Party #{edit['slot']+1} —"))
                    with user.scope(kind=Expansion,content=party_card.text):
                        party_numbers=list(user.find(kind=Number).elements)
                        pn=lambda label:next(x for x in party_numbers if x.label==label)
                        pn(f"Friendship — Party #{edit['slot']+1}").value=edit['changes']['friendship']
                        if 'ivs' in edit['changes']:pn('Attack IVS').value=edit['changes']['ivs'][1]
                        else:pn('Attack EVS').value=edit['changes']['evs'][1]
                        next(x for x in user.find(kind=Select).elements if x.label=='Move 1').value=edit['changes']['moves'][0]
                    selects=list(user.find(kind=Select).elements)
                    for operation in request['items']:
                        item_report=web.core.inspect(self.raw,self.digest,rom_bytes=self.rom)['items']
                        item=next((row for row in item_report['entries'] if row['item_id']==operation['item_id']),None)
                        row_controls={x.label:x for x in numbers}
                        if operation['op']=='set':
                            row_controls[f"Quantity — {item['name']}"].value=operation['quantity']
                        elif operation['op']=='remove':
                            next(x for x in user.find(kind=Checkbox).elements if x.text==f"Remove — {item['name']}").value=True
                        else:
                            next(x for x in user.find(kind=Checkbox).elements if x.text=='Add Item').value=True
                            next(x for x in selects if x.label=='Item').value=operation['item_id']
                            row_controls['Quantity — Add Item'].value=operation['quantity']
                    boxes={x.text:x for x in user.find(kind=Checkbox).elements}
                    boxes[f"Create Pokémon — Party #{receipt['created_slot']+1}"].value=True
                    create=request['create'][0]
                    create_slot=receipt['created_slot']+1
                    empty_card=next(x for x in user.find(kind=Expansion).elements if x.text==f'Party #{create_slot} — Empty')
                    empty_card.open()
                    with user.scope(kind=Expansion,content=empty_card.text):
                        create_numbers=list(user.find(kind=Number).elements)
                        cn=lambda label:next(x for x in create_numbers if x.label==label)
                        cn(f'Create Level — Party #{create_slot}').value=create['level']
                        cn('Create Friendship').value=create['friendship']
                        create_selects=list(user.find(kind=Select).elements)
                        cs=lambda label:next(x for x in create_selects if x.label==label)
                        cs(f'Create Species — Party #{create_slot}').value=create['species']
                        cs('Create Nature').value=create['nature']
                        cs('Create Ability').value=create['ability']
                        cs('Create Held item').value=create['held_item']
                        for move_index,value in enumerate(create['moves']):cs(f'Create Move {move_index+1}').value=value
                        for name,index in zip(('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def'),range(6)):
                            cn(f'Create {name} IVS').value=create['ivs'][index]
                            cn(f'Create {name} EVS').value=create['evs'][index]
                    await asyncio.sleep(0.1)
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see('Trainer')
                    await user.should_see('Created Pokémon')
                    user.find(kind=Button,content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button,content='検証済み .sav を保存').click()
                    download=await user.download.next()
                    expected,_=web.core.derive(self.raw,self.digest,request,rom_bytes=self.rom)
                    self.assertTrue(captured)
                    self.assertTrue(all(x['input_matches'] and x['rom_matches'] and x['request']==request
                                        and x['output_matches'] for x in captured),captured)
                    self.assertEqual(delivered[-1],expected,[(i,a,b) for i,(a,b) in enumerate(zip(delivered[-1],expected)) if a!=b][:4])
                    number('Money').value=(request['money']+1)%10000000
                    self.assertFalse(next(iter(user.find(kind=Button,content='検証済み .sav を保存').elements)).enabled)
        asyncio.run(exercise())


if __name__=='__main__':unittest.main()
