"""Synthetic E4 construction/envelope tests; no native/gameplay claim."""
import hashlib
import struct
import unittest
from unittest.mock import patch
import pokemonstart_v022_creation_model as creator
import pokemonstart_v022_creation_writer as writer
import pokemonstart_v022_creation_baseline_audit as audit
import pokemonstart_v022_product_core as core
import pokemonstart_v022_party_model as party
import pokemonstart_v022_party_audit as party_audit
import pokemonstart_v022_inventory_model as inventory
import pokemonstart_v022_inventory_audit as inventory_audit
from test_v022_party_writer import synthetic_inputs as e3_inputs


def inputs(count=3,active=0,rotation=0):
    source,rom=e3_inputs();rom=bytearray(rom)
    for sid in (*range(1,152),288):
        pos=party.SPECIES_NAMES+sid*8
        name=rom[pos:pos+8];end=name.index(255)
        rom[pos+end:pos+8]=bytes([255])*(8-end)
        entry=party.SPECIES_TABLE+sid*32
        rom[entry+6:entry+8]=bytes((5,6));rom[entry+16]=127;rom[entry+18]=70
        if sid%2==0:rom[entry+26:entry+28]=bytes(2)
    for group in range(80):
        struct.pack_into('<I',rom,0x9A3D6C+group*4,0x08200000+group*8)
        for number in range(2):
            header=0x201000+28*(group*2+number)
            struct.pack_into('<I',rom,0x200000+group*8+number*4,header+0x08000000)
            rom[header+20]=89
    raw=bytearray(source);verified=core.v.verify_bytes(raw)
    if active:
        for section in verified.slots[0].sections:
            target=verified.slots[1].section(section.section_id).physical_sector*4096
            raw[target:target+0xFF0]=section.data[:0xFF0]
    for saved_slot in verified.slots:
        owner=saved_slot.section(0).physical_sector*4096
        raw[owner:owner+8]=bytes((0xBB,0xBC,255,255,255,255,255,255))
        raw[owner+8]=saved_slot.slot_index
        raw[owner+10:owner+14]=bytes((17,34,51,68))
        raw[owner+0xF26]&=247
        base=saved_slot.section(1).physical_sector*4096
        raw[base+4:base+6]=bytes(2)
        if saved_slot.slot_index==verified.active_slot:
            template=source[base+56:base+156]
            raw[base+52]=count
            for slot in range(verified.party_count,count):raw[base+56+100*slot:base+156+100*slot]=template
        for section in saved_slot.sections:
            pos=section.physical_sector*4096
            if active:
                struct.pack_into('<I',raw,pos+0xFFC,section.counter+2 if saved_slot.slot_index==1 else section.counter)
            struct.pack_into('<H',raw,pos+0xFF6,core.v.calculate_save_checksum(raw[pos:pos+core.v.SECTION_LENGTHS[section.section_id]]))
    # Rotate physical sectors within each slot, preserving logical metadata.
    if rotation:
        old=bytes(raw)
        for slot in range(2):
            for i in range(14):
                destination=slot*14+(i+rotation)%14
                raw[destination*4096:(destination+1)*4096]=old[(slot*14+i)*4096:(slot*14+i+1)*4096]
    if active:
        # Make the selected source slot carry the same bounded synthetic Party.
        p=core.v.verify_bytes(raw);base=p.slots[p.active_slot].section(1).physical_sector*4096
        template=verified.slots[0].section(1).data[56:156]
        raw[base+52]=count
        for i in range(count):raw[base+56+i*100:base+156+i*100]=template
        struct.pack_into('<H',raw,base+0xFF6,core.v.calculate_save_checksum(raw[base:base+0xFF0]))
    return bytes(raw),bytes(rom)


class CreationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw,cls.rom=inputs();cls.digest=hashlib.sha256(cls.rom).hexdigest()
    def setUp(self):
        for module,key in ((party,'ROM_SHA256'),(party_audit,'EXACT'),(inventory,'ROM_SHA256'),(inventory_audit,'ROM_SHA256')):
            p=patch.object(module,key,self.digest);p.start();self.addCleanup(p.stop)
        p=patch.object(core.profile,'_require_rom_hash',side_effect=lambda h:None if h==self.digest else (_ for _ in ()).throw(ValueError('exact gate')))
        p.start();self.addCleanup(p.stop)
        self.request={'species':1,'level':3,'moves':[33,39],'nature':3,'ivs':[31]*6,'evs':[4,252,0,0,252,0],
                      'friendship':123,'ability':8,'held_item':139}
    def test_full_output_independent_immutable_footer(self):
        source=bytes(self.raw);out,receipt=writer.derive(source,self.rom,[self.request])
        self.assertEqual(source,self.raw);self.assertEqual(source[-16:],out[-16:])
        parsed=party_audit.structure.parse(out);old=party_audit.structure.parse(source)
        self.assertEqual(parsed['records'][:3],old['records'])
        self.assertEqual(len(parsed['records']),4)
        self.assertEqual(parsed['records'][3],audit.expected_record(source,self.rom,self.request))
        self.assertTrue(receipt['independent_audit']['complete_output_equal'])
        final=party_audit.reconstruct(parsed['records'][3],self.rom)
        self.assertEqual(final['ivs'],[31]*6);self.assertEqual(final['resolved_ability'],8)
        self.assertEqual(final['cached_hp_stats'][0],final['cached_hp_stats'][1])
        self.assertEqual(final['native_nature'],3)
        self.assertEqual(parsed['records'][3][54:56],bytes(2))
    def test_every_constructed_byte_tamper_detected(self):
        out,_=writer.derive(self.raw,self.rom,[self.request]);v=core.v.verify_bytes(out)
        base=v.slots[v.active_slot].section(1).physical_sector*4096
        for offset in range(100):
            wrong=bytearray(out);wrong[base+56+300+offset]^=1
            struct.pack_into('<H',wrong,base+0xFF6,core.v.calculate_save_checksum(wrong[base:base+0xFF0]))
            with self.subTest(offset=offset),self.assertRaises(ValueError):audit.audit_output(self.raw,bytes(wrong),self.rom,[self.request])
        for offset in (0,-1,base+52,base+56):
            wrong=bytearray(out);wrong[offset]^=1
            with self.assertRaises(ValueError):audit.audit_output(self.raw,bytes(wrong),self.rom,[self.request])
    def test_batch_unique_identities_and_capacity(self):
        out,_=writer.derive(self.raw,self.rom,[self.request]*3)
        rows=party_audit.structure.parse(out)['records']
        self.assertEqual(len(rows),6)
        self.assertEqual(len(set(x[:4] for x in rows[3:])),3)
        self.assertNotIn(rows[3][:4],set(x[:4] for x in rows[:3]))
        with self.assertRaisesRegex(ValueError,'Box'):writer.derive(out,self.rom,[self.request])
        with self.assertRaisesRegex(ValueError,'capacity'):writer.derive(self.raw,self.rom,[self.request]*4)
    def test_counts_levels_species_natures_permutations(self):
        for count in range(1,6):
            for active in (0,1):
                raw,_=inputs(count,active,rotation=count)
                for sid,level,nature in ((1,1,0),(2,3,24),(19,20,12),(288,100,3)):
                    request={'species':sid,'level':level,'nature':nature,'moves':[1,33,0,39]}
                    out,_=writer.derive(raw,self.rom,[request])
                    row=party_audit.structure.parse(out)['records'][count]
                    self.assertEqual(row,audit.expected_record(raw,self.rom,request))
                    self.assertFalse(party_audit.ordinary_reasons(row,self.rom,party_audit.inspect(out,self.rom)['saved_context']))
    def test_invalid_requests_and_identity_controls(self):
        for changes in ({'species':303},{'species':496},{'species':700},{'species':757},{'species':913},{'species':1460},
                        {'species':True},{'level':0},{'level':101},{'nature':25},{'moves':[]},{'moves':[0]},
                        {'moves':[998]},{'moves':[True]},{'ivs':[32]*6},{'evs':[252]*6},{'ability':9},
                        {'held_item':835},{'held_item':202},{'pid':1},{'shiny':True},{'ot_id':1},
                        {'hyper_training':1},{'friendship':True},{'egg':True}):
            request={**self.request,**changes}
            with self.subTest(changes=changes),self.assertRaises(ValueError):writer.derive(self.raw,self.rom,[request])
        for requests in ([],{},[{}]):
            with self.assertRaises(ValueError):writer.derive(self.raw,self.rom,requests)
    def test_source_predicates_and_bad_context(self):
        v=core.v.verify_bytes(self.raw);active=v.slots[v.active_slot]
        owner=active.section(0).physical_sector*4096;base=active.section(1).physical_sector*4096
        for pos,value in ((owner+0xF26,8),(owner+0xF2A,1),(owner+8,2),(base+4,255),(base+5,2),
                          (base+56+16,1),(base+56+75,64),(base+52,0)):
            wrong=bytearray(self.raw);wrong[pos]=value
            for sid in (0,1):
                sector=active.section(sid).physical_sector*4096
                struct.pack_into('<H',wrong,sector+0xFF6,core.v.calculate_save_checksum(wrong[sector:sector+core.v.SECTION_LENGTHS[sid]]))
            with self.subTest(pos=pos),self.assertRaises(ValueError):writer.derive(bytes(wrong),self.rom,[self.request])
        with self.assertRaises(ValueError):writer.derive(self.raw[:-1],self.rom,[self.request])
        with self.assertRaises(ValueError):writer.derive(self.raw,self.rom[:-1],[self.request])
    def test_composition_all_families_and_conflict(self):
        combinations=({}, {'money':1234567}, {'items':[{'op':'set','item_id':13,'quantity':8}]},
                      {'party':[{'slot':0,'changes':{'friendship':1}}]},
                      {'money':1234567,'items':[{'op':'set','item_id':13,'quantity':8}],
                       'party':[{'slot':0,'changes':{'friendship':1}}]})
        for extra in combinations:
            request={'create':[self.request],**extra}
            out,report=core.derive(self.raw,self.digest,request,rom_bytes=self.rom)
            self.assertTrue(report['independent_e4_audit']['complete_output_equal'])
            self.assertEqual(core.v.verify_bytes(out).party_count,4)
        with self.assertRaises(ValueError):core.derive(self.raw,self.digest,{'create':[self.request],
             'party':[{'slot':3,'changes':{'friendship':1}}]},rom_bytes=self.rom)
        candidate,_=writer.derive(self.raw,self.rom,[self.request])
        with patch.object(core.money,'derive',return_value=(candidate,{'money':{'from':0,'to':1}})):
            with self.assertRaises(ValueError):core.derive(self.raw,self.digest,{'money':1,'create':[self.request]},rom_bytes=self.rom)
    def test_map_domain_bounds_and_regionFF_rejection(self):
        domain=audit.map_domain(self.rom)
        self.assertEqual(len(domain),79)
        for group,regions in domain.items():
            for number,region in enumerate(regions):
                self.assertEqual(creator.location(self.rom,group,number),region)
            with self.assertRaises(ValueError):creator.location(self.rom,group,len(regions))
        with self.assertRaises(ValueError):creator.location(self.rom,79,0)
        bad=bytearray(self.rom);bad[0x201000+20]=255
        with self.assertRaisesRegex(ValueError,'regionFF'):creator.location(bytes(bad),0,0)
        bad=bytearray(self.rom);struct.pack_into('<I',bad,0x9A3D70,0x08200003)
        self.assertNotIn(0,audit.map_domain(bytes(bad)))
        with self.assertRaises(ValueError):creator.location(bytes(bad),0,0)

    def test_generator_native_policy_formula_all_natures_and_no_source_hash(self):
        maker=creator.Creator(self.raw,self.rom);independent=audit.BaselineAudit(self.raw,self.rom)
        owner=int.from_bytes(maker.owner[10:14],'little')
        for sid in (1,2,19,288):
            for nature in range(25):
                pid=maker.personality(sid,20,nature)
                self.assertEqual(pid,independent.personality(sid,20,nature))
                self.assertEqual(pid%25,nature)
                self.assertGreaterEqual(audit.native_shiny_score(owner,pid),8)
                self.assertNotIn(pid,maker.used)
        modified=bytearray(self.raw);modified[-1]^=1
        other=creator.Creator(bytes(modified),self.rom)
        self.assertEqual(maker.personality(1,3,0),other.personality(1,3,0))
        class Exhausted:
            def digest(self):return bytes(32)
        # Owner's XOR halves are zero here: all generated PID0 candidates
        # violate native shiny score; exhaustion must reject, never fallback.
        maker.owner=maker.owner[:10]+bytes(4)+maker.owner[14:]
        with patch.object(creator.hashlib,'sha256',return_value=Exhausted()):
            with self.assertRaisesRegex(ValueError,'exhausted'):maker.personality(1,3,0)

    def test_independent_import_boundary(self):
        import ast
        from pathlib import Path
        tree=ast.parse(Path(audit.__file__).read_text())
        imports={n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
        self.assertFalse({'pokemonstart_v022_creation_model','pokemonstart_v022_creation_writer','pokemonstart_v022_product_party'}&imports)

if __name__=='__main__':unittest.main()
