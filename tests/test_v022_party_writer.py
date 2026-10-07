"""E3 synthetic contracts. No private saves, ROM tables, or record fixtures."""
import ast
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

import pokemonstart_v022_party_model as model
import pokemonstart_v022_party_audit as audit
import pokemonstart_v022_product_core as core
import pokemonstart_v022_product_party as writer
import pokemonstart_v022_product_audit as composed_audit
import pokemonstart_v022_inventory_model as inventory
import pokemonstart_v022_inventory_audit as inventory_audit
from test_v022_inventory_editor import rom_fixture
from test_v022_product_core import save


def synthetic_inputs():
    rom=bytearray(rom_fixture())
    struct.pack_into('<I',rom,0x1BC,0x099B8B40)
    for sid in (*range(1,152),288,303,496,497,498,700,757,913,1460):
        entry=0x19B8B40+sid*32
        rom[entry:entry+6]=bytes((60+sid%20,50,40,30,20,10))
        rom[entry+19]=0
        struct.pack_into('<H',rom,entry+22,7)
        struct.pack_into('<2H',rom,entry+26,8,9)
        name=bytes((0xBB,0xA1+sid%10,0xFF))
        rom[0x16570A4+sid*8:0x16570A4+sid*8+8]=name+bytes(5)
    for n in range(101):
        struct.pack_into('<I',rom,0x14C5D54+4*n,0 if n==0 else 1 if n==1 else n**3)
    for n in range(25):
        struct.pack_into('<5b',rom,0x20F550+n*5,*[0 if n//5==n%5 else 1 if j==n//5 else -1 if j==n%5 else 0 for j in range(5)])
    for mid in range(998):
        rom[0x14A3238+mid*12+4]=5 if mid==996 else 35
        name=bytes((0xBC,0xA1+mid%10,0xFF))
        rom[0x111A74C+mid*16:0x111A74C+mid*16+16]=name+bytes(13)
    for iid,metadata in {**model.HELD_TARGET_METADATA,202:(1,0,4,45,0)}.items():
        pocket,importance,kind,effect,param=metadata
        entry=0x15199C8+iid*40
        rom[entry:entry+10]=bytes((0xBD,0xA1+iid%10,0xFF))+bytes(7)
        struct.pack_into('<H',rom,entry+10,iid)
        rom[entry+20]=importance;rom[entry+22]=pocket;rom[entry+23]=kind
        rom[entry+14]=effect;rom[entry+15]=param
    raw=bytearray(save())
    parsed=core.v.verify_bytes(raw); active=parsed.slots[parsed.active_slot]
    base=active.section(1).physical_sector*4096
    for slot in range(parsed.party_count):
        sid=(1,19,25,288,1,19)[slot];level=(3,6,20,50,3,6)[slot]
        record=bytearray(100);record[0]=9;record[19]=2;record[84]=level
        struct.pack_into('<H',record,32,sid);struct.pack_into('<I',record,36,level**3)
        struct.pack_into('<4H',record,44,33,39,0,0)
        record[52:56]=bytes((35,35,201,17));record[40]=192
        if slot:
            struct.pack_into('<H',record,48,98)
            record[54]=35
        stats=audit.reconstruct(record,rom)['ordinary_expected_stats']
        struct.pack_into('<7H',record,86,stats[0] if slot==0 else stats[0]//2,*stats)
        raw[base+56+slot*100:base+56+(slot+1)*100]=record
    struct.pack_into('<H',raw,base+0xFF6,core.v.calculate_save_checksum(raw[base:base+0xFF0]))
    raw[active.section(0).physical_sector*4096+0xF2A]&=254
    raw[active.section(4).physical_sector*4096+0xEFC:active.section(4).physical_sector*4096+0xEFE]=bytes(2)
    raw[active.section(4).physical_sector*4096+0xE09]&=247
    b13=active.section(13).physical_sector*4096
    raw[b13+0x6B6:b13+0x6B8]=bytes(2)
    raw[b13+0xADC:b13+0xFF0]=bytes(1300);raw[0x1E000:0x1EFF0]=bytes(0xFF0)
    for i,row in enumerate(((533,1),(14,3),(13,1))):struct.pack_into('<HH',raw,b13+0xADC+4*i,*row)
    struct.pack_into('<3H',raw,0x1E716,3,0,0)
    return bytes(raw),bytes(rom)


class OrdinaryWriterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.rom=synthetic_inputs();cls.digest=model.sha(cls.rom)

    def setUp(self):
        for module,attr in ((model,'ROM_SHA256'),(audit,'EXACT'),(inventory,'ROM_SHA256'),(inventory_audit,'ROM_SHA256')):
            gate=patch.object(module,attr,self.digest);gate.start();self.addCleanup(gate.stop)
        gate=patch.object(core.profile,'_require_rom_hash',side_effect=lambda x: None if x==self.digest else (_ for _ in ()).throw(ValueError('synthetic exact gate')))
        gate.start();self.addCleanup(gate.stop)

    def edit(self,changes,raw=None,slot=0):
        return writer.derive(self.raw if raw is None else raw,self.digest,slot,changes,rom_bytes=self.rom)

    def change_record(self,offset,value,slot=0,raw=None):
        data=bytearray(self.raw if raw is None else raw);parsed=core.v.verify_bytes(data)
        base=parsed.slots[parsed.active_slot].section(1).physical_sector*4096
        start=base+56+slot*100;data[start+offset:start+offset+len(value)]=value
        struct.pack_into('<H',data,base+0xFF6,core.v.calculate_save_checksum(data[base:base+0xFF0]))
        return bytes(data)

    def test_all_fields_composed_independent_and_repeat(self):
        changes={'species':2,'level':20,'moves':{0:996,1:1,2:33,3:0},'pp_up':{0:3,1:2,2:1},
                 'pp':{1:7},'friendship':255,'ivs':[31]*6,'evs':[4,252,0,0,252,0],
                 'effective_nature':3,'ability':9,'held_item':139}
        options=writer.ordinary_options(model.extract_tables(self.rom))['moves']
        self.assertNotEqual(options[996],options[986])
        before=bytes(self.raw);out,receipt=self.edit(changes)
        self.assertEqual(before,self.raw)
        self.assertTrue(receipt['independent_audit']['complete_output_equal'])
        row=audit.inspect(out,self.rom)['party'][0]
        self.assertEqual((row['species'],row['stored_level'],row['resolved_ability'],row['held_item']),(2,20,9,139))
        self.assertEqual([x['pp'] for x in row['moves']],[5,7,42,17])
        again,_=self.edit({'friendship':10},out)
        self.assertEqual(audit.inspect(again,self.rom)['party'][0]['friendship'],10)
        bad=bytearray(out);bad[-1]^=1
        with self.assertRaises(ValueError):audit.audit_edit(self.raw,bytes(bad),self.rom,0,changes)

    def test_untouched_empty_slots_and_all_pp_up_counts(self):
        for slot in range(4):
            for ups in range(4):
                with self.subTest(slot=slot,ups=ups):
                    out,_=self.edit({'moves':{slot:996},'pp_up':{slot:ups}})
                    old=audit.inspect(self.raw,self.rom)['party'][0]['moves']
                    new=audit.inspect(out,self.rom)['party'][0]['moves']
                    self.assertEqual(new[slot]['pp'],5)
                    for j in range(4):
                        if j!=slot:self.assertEqual(old[j],new[j])
                    source=out
                    out,_=self.edit({'moves':{slot:1},'pp_up':{slot:ups}},source)
                    self.assertEqual(audit.inspect(out,self.rom)['party'][0]['moves'][slot]['pp'],35+7*ups)
                    out,_=self.edit({'moves':{slot:0}},out)
                    final=audit.inspect(out,self.rom)['party'][0]['moves'][slot]
                    self.assertEqual((final['move_id'],final['pp'],final['pp_up_count']),(0,35,ups))
                    filled,_=self.edit({'moves':{slot:33}},out)
                    self.assertEqual(audit.inspect(filled,self.rom)['party'][0]['moves'][slot]['pp'],35+7*ups)

    def test_pp_only_and_no_global_normalization(self):
        out,receipt=self.edit({'pp':{0:2}})
        row=audit.inspect(out,self.rom)['party'][0]['moves']
        self.assertEqual([x['pp'] for x in row],[2,35,201,17])
        self.assertEqual(row[3]['pp_up_count'],3)
        self.assertEqual(len(set(receipt['changed_offsets'])-set(core.v.verify_bytes(out).slots[0].section(1).physical_sector*4096+x for x in (0xFF6,0xFF7))),1)

    def test_slot_maps_malformed_ranges_and_empty_pp_edits(self):
        for changes in ({'moves':{4:1}},{'moves':{True:1}},{'moves':{0:998}},{'moves':{0:-1}},
                        {'moves':{0:True}},{'moves':{}},{'moves':[1]}, {'pp_up':{0:4}},
                        {'pp':{0:36}},{'pp':{2:0}},{'pp_up':{2:0}}, {'moves':{0:0},'pp':{0:0}},
                        {'moves':{'0':1}}, {'level':True},{'species':303}, {'ability':65535},
                        {'ivs':[32]*6},{'evs':[252]*6},{'effective_nature':25},{'held_item':835},
                        {'nickname':'x'},{'pid':1},{'friendship':True}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.edit(changes)
        for offset,value in ((44,struct.pack('<H',998)),(52,bytes([36]))):
            with self.assertRaises(ValueError):self.edit({'friendship':1},self.change_record(offset,value))

    def test_saved_context_both_parsers_and_checksum_independence(self):
        active=core.v.verify_bytes(self.raw).slots[0]
        for flag in (0,1):
            for tier in (0,11,12,13,65535):
                data=bytearray(self.raw)
                data[active.section(0).physical_sector*4096+0xF2A]=flag
                struct.pack_into('<H',data,active.section(4).physical_sector*4096+0xEFC,tier)
                first=model.inspect(bytes(data),self.rom);second=audit.inspect(bytes(data),self.rom)
                audit.compare(first,second)
                self.assertEqual(first['saved_context']['flag_0x930'],bool(flag))
                self.assertEqual(first['saved_context']['variable_0x5018'],tier)
                if flag:
                    with self.assertRaisesRegex(ValueError,'facility'):self.edit({'friendship':1},bytes(data))
                else:self.edit({'friendship':1},bytes(data))

    def test_unsupported_record_modes_and_unknown_retained_items(self):
        for offset,value in ((16,b'\x01'),(19,b'\x00'),(28,b'\x01\x00'),(75,b'\x40'),
                             (15,b'\x1a'),(56,b'\xfd'),(34,struct.pack('<H',835)),(34,struct.pack('<H',13)),
                             (32,struct.pack('<H',303)),(32,struct.pack('<H',496)),(32,struct.pack('<H',497)),
                             (32,struct.pack('<H',498)),(32,struct.pack('<H',913)),(32,struct.pack('<H',1460)),
                             (32,struct.pack('<H',700)),(32,struct.pack('<H',757))):
            with self.subTest(offset=offset,value=value),self.assertRaises(ValueError):self.edit({'friendship':1},self.change_record(offset,value))

    def test_held_catalog_retained_and_target_are_distinct(self):
        tables=model.extract_tables(self.rom)
        self.assertTrue(model.held_eligibility(13,tables)['metadata_decodable'])
        self.assertFalse(model.held_eligibility(13,tables)['safe_new_target'])
        self.assertTrue(model.held_eligibility(202,tables)['safe_retained_value'])
        self.assertFalse(model.held_eligibility(202,tables)['safe_new_target'])
        source=self.change_record(34,struct.pack('<H',202))
        self.edit({'friendship':1},source)
        with self.assertRaises(ValueError):self.edit({'held_item':202})
        for item in (0,139,142,200):
            other=source if item==0 else self.raw
            out,_=self.edit({'held_item':item},other)
            self.assertEqual(audit.inspect(out,self.rom)['party'][0]['held_item'],item)

    def test_hp_decreases_context_independent_subset_and_fainted(self):
        # Level3 max16 (synthetic source). IVs31 increases to17; lower level2 ->14.
        old=audit.inspect(self.raw,self.rom)['party'][0]['cached_hp_stats'][1]
        for hp in (0,5,old,old-1):
            source=self.change_record(86,struct.pack('<H',hp))
            if hp>14:
                with self.assertRaisesRegex(ValueError,'in-battle'):self.edit({'level':2},source)
            else:
                out,_=self.edit({'level':2},source)
                self.assertEqual(audit.inspect(out,self.rom)['party'][0]['cached_hp_stats'][0],hp)
            out,_=self.edit({'level':20},source)
            current,newmax=audit.inspect(out,self.rom)['party'][0]['cached_hp_stats'][:2]
            self.assertEqual(current,0 if hp==0 else hp+newmax-old)

    def test_ability_resolution_and_identity_preservation(self):
        for target in (7,8,9):
            source=self.change_record(71,b'\x80')
            if target==7:source=self.change_record(75,b'\x80',raw=source)
            out,_=self.edit({'ability':target},source)
            row=audit.inspect(out,self.rom)['party'][0]
            self.assertEqual(row['resolved_ability'],target)
            record=audit.structure.parse(out)['records'][0]
            self.assertTrue(record[71]&128)
            self.assertEqual(record[:15],audit.structure.parse(source)['records'][0][:15])

    def test_exp_boundaries_species_level_conflicts_and_nature(self):
        damaged=self.change_record(86,struct.pack('<H',5))
        for exp,level in ((1,1),(7,1),(8,2),(27,3),(1000000,100)):
            out,_=self.edit({'experience':exp,'friendship':1},damaged)
            self.assertEqual(audit.inspect(out,self.rom)['party'][0]['stored_level'],level)
        for changes in ({'experience':0},{'experience':1000001},{'level':100,'experience':27}):
            with self.assertRaises(ValueError):self.edit(changes)
        for nature in range(25):
            out,_=self.edit({'effective_nature':nature,'friendship':1})
            row=audit.inspect(out,self.rom)['party'][0]
            self.assertEqual((row['native_nature'],row['effective_nature']),(9,nature))

    def test_composition_all_four_variants_and_family_conflicts(self):
        for money in (False,True):
            for items in (False,True):
                request={'party':[{'slot':0,'changes':{'friendship':1,'level':20,'ability':9,'held_item':200}}]}
                if money:request['money']=1234567
                if items:request['items']=[{'op':'set','item_id':13,'quantity':8}]
                out,receipt=core.derive(self.raw,self.digest,request,rom_bytes=self.rom)
                self.assertTrue(receipt['independent_e3_audit']['complete_output_equal'])
                self.assertTrue(any('Ability' in x or 'resolved_ability' in x for x in receipt['semantic_diff']))
                wrong=bytearray(out);wrong[-1]^=1
                with self.assertRaises(ValueError):composed_audit.audit_e3(self.raw,bytes(wrong),self.rom,request)
        with self.assertRaises(ValueError):core.derive(self.raw,self.digest,{'party':[{'slot':0,'changes':{'friendship':1}}]*2},rom_bytes=self.rom)
        original=core.money.derive
        def conflicting(*args):
            candidate,receipt=original(*args)
            byte=bytearray(candidate);parsed=core.v.verify_bytes(self.raw)
            byte[parsed.slots[parsed.active_slot].section(1).physical_sector*4096+56+41]=2
            return bytes(byte),receipt
        with patch.object(core.money,'derive',side_effect=conflicting),self.assertRaisesRegex(ValueError,'conflict'):
            core.derive(self.raw,self.digest,{'money':1234567,'party':[{'slot':0,'changes':{'friendship':1}}]},rom_bytes=self.rom)

    def test_auditor_rejects_same_section_unrequested_changes_and_context(self):
        out,_=self.edit({'friendship':1})
        for offset,value in ((27,b'\x01'),(52,b'\x01'),(75,b'\x80'),(86,b'\x00\x00')):
            bad=self.change_record(offset,value,raw=out)
            with self.subTest(offset=offset),self.assertRaises(ValueError):audit.audit_edit(self.raw,bad,self.rom,0,{'friendship':1})
        self.assertFalse(any('product_party' in alias.name or 'party_model' in alias.name for node in ast.walk(ast.parse(Path(audit.__file__).read_text())) if isinstance(node,ast.Import) for alias in node.names))




class OrdinaryWorkflowTests(unittest.TestCase):
    setUpClass=classmethod(OrdinaryWriterTests.setUpClass.__func__)
    setUp=OrdinaryWriterTests.setUp

    def test_preview_stale_download_and_exclusive_separate_export(self):
        import tempfile
        import pokemonstart_v022_product_web as web
        from pathlib import Path
        with patch.object(web.ProductWorkflow,'_read_rom',return_value=self.rom),patch.object(core.profile,'_check_rom_file',return_value=self.digest):
            flow=web.ProductWorkflow(Path('synthetic.gba'))
            inspection=flow.upload('original.sav',self.raw)
            self.assertTrue(inspection['party'][0]['ordinary_eligibility']['eligible'])
            request={'party':[{'slot':0,'changes':{'level':20,'friendship':100,'ability':9,'held_item':139}}],'money':1234567}
            receipt=flow.preview(request);output,_=flow.commit()
            request['money']=1
            self.assertEqual(flow.download()[0],output)
            self.assertEqual(flow.source_raw,self.raw)
            with tempfile.TemporaryDirectory(dir=Path.cwd()/'work') as directory,patch.object(core.profile,'PRIVATE_ROOT',Path(directory)):
                destination=flow.export_verified(directory)
                self.assertNotEqual(destination.name,'original.sav')
                self.assertEqual(destination.read_bytes(),output)
                with self.assertRaises(FileExistsError):flow.export_verified(directory)
            flow.output_raw=output[:-1]+b'x'
            with self.assertRaises(ValueError):flow.download()
            flow.preview(receipt['request']);flow.source_raw=self.raw[:-1]+b'x'
            with self.assertRaises(ValueError):flow.commit()
            flow.upload('original.sav',self.raw);flow.preview(receipt['request'])
            with patch.object(core.profile,'_check_rom_file',side_effect=ValueError('ROM stale')):
                with self.assertRaises(ValueError):flow.commit()
            self.assertEqual(web.server_options()['host'],'127.0.0.1')

    def test_gui_major_fields_composed_semantic_preview_and_download(self):
        import pokemonstart_v022_product_web as web
        if web.ui is None:self.skipTest('NiceGUI unavailable')
        import asyncio,sys,os
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.elements.number import Number
        from nicegui.elements.select import Select
        from nicegui.elements.button import Button
        from nicegui.testing import user_simulation
        async def exercise():
            with patch.object(web.ProductWorkflow,'_read_rom',return_value=self.rom),patch.object(core.profile,'_check_rom_file',return_value=self.digest),patch.object(sys,'argv',['app','--rom','synthetic.gba']),patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'E3 GUI synthetic'}):
                async with user_simulation(main_file=Path(__file__).with_name('v022_product_simulation_app.py')) as user:
                    await user.open('/')
                    upload=next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload('source.sav','application/octet-stream',self.raw)])
                    await user.should_see('読み込み済み')
                    numbers=sorted(user.find(kind=Number).elements,key=lambda x:x.id)
                    selects=sorted(user.find(kind=Select).elements,key=lambda x:x.id)
                    next(x for x in numbers if x.label=='Friendship — Party #1').value=100
                    next(x for x in numbers if x.label=='Level').value=20
                    next(x for x in numbers if x.label=='PP-Up 1').value=3
                    next(x for x in numbers if x.label=='Money').value=1234567
                    next(x for x in selects if x.label=='Move 1').value=996
                    next(x for x in selects if x.label=='Effective nature').value=3
                    next(x for x in selects if x.label=='Ability').value=9
                    next(x for x in selects if x.label=='Held item').value=139
                    item_name=inventory.extract_catalog(self.rom)[0][13].name
                    next(x for x in numbers if x.label=='Quantity — '+item_name).value=8
                    user.find(kind=Button,content='Preview').click()
                    await user.should_see('Money:')
                    await user.should_see('Party #1 Level: 3 → 20')
                    user.find(kind=Button,content='検証して別 save を生成').click()
                    await user.should_see('検証済みの別 save を生成しました。')
                    user.find(kind=Button,content='検証済み .sav を保存').click()
                    download=await user.download.next()
                    expected,_=core.derive(self.raw,self.digest,{'money':1234567,'party':[{'slot':0,'changes':{'level':20,'friendship':100,'moves':{0:996},'pp_up':{0:3},'effective_nature':3,'ability':9,'held_item':139}}],
                        'items':[{'op':'set','item_id':13,'quantity':8}]},rom_bytes=self.rom)
                    self.assertEqual(download.content,expected)
                    next(x for x in numbers if x.label=='Money').value=1
                    self.assertFalse(next(iter(user.find(kind=Button,content='検証済み .sav を保存').elements)).enabled)
        asyncio.run(exercise())


class GroupedAcceptanceTests(unittest.TestCase):
    setUpClass=classmethod(OrdinaryWriterTests.setUpClass.__func__)
    setUp=OrdinaryWriterTests.setUp

    def test_dynamic_grouped_recipe_and_synthetic_normal_save(self):
        import pokemonstart_v022_product_acceptance as acceptance
        from test_v022_product_acceptance import resave
        packet=acceptance.prepare_e3(self.raw,self.rom)
        self.assertGreaterEqual(len({p['species'] for p in packet['selected_members']}),3)
        self.assertFalse(packet['gameplay_acceptance'])
        output,receipt=core.derive(self.raw,self.digest,packet['transaction']['request'],rom_bytes=self.rom)
        returned=resave(output)
        import json
        result=acceptance.check_e3_return(self.raw,returned,self.rom,json.loads(json.dumps(packet)))
        self.assertFalse(result['gameplay_acceptance']);self.assertFalse(result['e3_adopted'])
        self.assertTrue(result['later_edit_reconstructed'])
        self.assertEqual(result['reported_gameplay_drifts'],[])
        with self.assertRaises(ValueError):acceptance.check_e3_return(self.raw,output,self.rom,packet)
        import copy
        bad=copy.deepcopy(packet);bad['transaction']['output_sha256']='0'*64
        with self.assertRaises(ValueError):acceptance.check_e3_return(self.raw,returned,self.rom,bad)
        corrupt=bytearray(returned);parsed=core.v.verify_bytes(returned)
        base=parsed.slots[parsed.active_slot].section(1).physical_sector*4096
        corrupt[base+56+27]^=1
        struct.pack_into('<H',corrupt,base+0xFF6,core.v.calculate_save_checksum(corrupt[base:base+0xFF0]))
        with self.assertRaises(ValueError):acceptance.check_e3_return(self.raw,bytes(corrupt),self.rom,packet)


if __name__=='__main__':unittest.main()
