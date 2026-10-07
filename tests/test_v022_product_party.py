import struct
import unittest
import pokemonstart_v022_product_party as p
import pokemonstart_save_verifier as v
from test_m3c_derived_stats_writer import synthetic
ROM=p.profile.EXPECTED_ROM_SHA256


def save(count=1):
    raw=bytearray(synthetic()[0]);base=5*4096;record=base+v.PARTY_OFFSET
    raw[record+19]=2
    struct.pack_into('<I',raw,record+36,135)
    for slot in range(1,count):raw[record+slot*100:record+(slot+1)*100]=raw[record:record+100]
    raw[base+0x34]=count
    struct.pack_into('<H',raw,base+0xFF6,v.calculate_save_checksum(raw[base:base+0xFF0]))
    return bytes(raw)


class ProductPartyTests(unittest.TestCase):
    def test_all_present_slots_no_hash_membership(self):
        raw=save(6)
        for slot in range(6):
            out,report=p.derive(raw,ROM,slot,{'friendship':200,'moves':{0:1}})
            result=v.verify_bytes(out)
            self.assertEqual(result.party[slot].friendship,200)
            self.assertEqual(result.party[slot].moves[0],1)
            for other in range(6):
                if other!=slot:self.assertEqual(result.party[other],v.verify_bytes(raw).party[other])
            self.assertEqual(raw[14*4096:],out[14*4096:])
        with self.assertRaises(ValueError):p.derive(raw,ROM,6,{'friendship':1})

    def test_composed_stats_and_repeat(self):
        raw=save()
        changes={'species':2,'level':6,'ivs':[31,0,26,23,27,29],
                 'evs':[8,0,0,0,0,0],'friendship':53,'moves':{0:1}}
        out,_=p.derive(raw,ROM,0,changes)
        mon=v.verify_bytes(out).party[0]
        self.assertEqual((mon.species,mon.level,mon.experience),(2,6,179))
        self.assertEqual((mon.hp,mon.max_hp,mon.attack,mon.defense,mon.speed,mon.sp_attack,mon.sp_defense),
                         (25,25,11,15,14,18,17))
        self.assertTrue(p.capabilities(out,ROM,0)['stats'])
        again,_=p.derive(out,ROM,0,{'friendship':10})
        self.assertEqual(v.verify_bytes(again).party[0].friendship,10)

    def test_reject_unsupported_operations_independently(self):
        raw=save()
        for changes in ({'level':7},{'level':True},{'species':3},{'ivs':[32]*6},
                        {'evs':[252]*6},{'moves':{1:1}},{'moves':{0:45}},
                        {'ability_selector':1},{'friendship':256},{'friendship':52}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):p.derive(raw,ROM,0,changes)
        bad=bytearray(raw);bad[5*4096+v.PARTY_OFFSET]=12
        struct.pack_into('<H',bad,5*4096+0xFF6,v.calculate_save_checksum(bad[5*4096:5*4096+0xFF0]))
        bad=bytes(bad)
        with self.assertRaises(ValueError):p.derive(bad,ROM,0,{'level':6})
        self.assertEqual(v.verify_bytes(p.derive(bad,ROM,0,{'friendship':1})[0]).party[0].friendship,1)

    def test_wrong_cached_stats_and_hp_decrease_rejected(self):
        raw=save()
        with self.assertRaises(ValueError):p.derive(raw,ROM,0,{'ivs':[0]*6})
        bad=bytearray(raw);bad[5*4096+v.PARTY_OFFSET+90]+=1
        struct.pack_into('<H',bad,5*4096+0xFF6,v.calculate_save_checksum(bad[5*4096:5*4096+0xFF0]))
        with self.assertRaises(ValueError):p.derive(bytes(bad),ROM,0,{'evs':[8,0,0,0,0,0]})
