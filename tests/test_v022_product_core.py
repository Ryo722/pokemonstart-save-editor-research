import struct
import unittest
import pokemonstart_v022_product_core as c
from test_v022_composition import composed_fixture
ROM=c.profile.EXPECTED_ROM_SHA256


def save():
    raw=bytearray(composed_fixture());v=c.v.verify_bytes(raw)
    base=v.slots[v.active_slot].section(1).physical_sector*4096
    # Synthetic existing ordinary records; synthetic fixture has arbitrary copied bytes.
    for slot in range(v.party_count):
        record=base+c.v.PARTY_OFFSET+slot*100
        struct.pack_into('<H',raw,record+32,1)
        struct.pack_into('<H',raw,record+28,0)
        raw[record+19]=2;raw[record+75]&=0xBF;raw[record+84]=5
        struct.pack_into('<HH',raw,record+86,20,20)
    struct.pack_into('<H',raw,base+0xFF6,c.v.calculate_save_checksum(raw[base:base+0xFF0]))
    return bytes(raw)


class ProductCompositionTests(unittest.TestCase):
    def test_three_families_and_multiple_party_slots(self):
        raw=save()
        request={'money':9999999,'party':[{'slot':0,'changes':{'friendship':100}},
                                        {'slot':2,'changes':{'friendship':101}}],
                 'items':{'potion_quantity':3}}
        out,receipt=c.derive(raw,ROM,request)
        self.assertEqual(c.inspect(out,ROM)['money']['money'],9999999)
        self.assertEqual([c.v.verify_bytes(out).party[x].friendship for x in (0,2)],[100,101])
        self.assertEqual(c.items.inspect(out,ROM)['entries'][0]['quantity'],3)
        self.assertEqual(out,c.derive(raw,ROM,request)[0])
        active=c.v.verify_bytes(raw).active_slot
        other=(1-active)*14*4096
        self.assertEqual(raw[other:other+14*4096],out[other:other+14*4096])
        self.assertEqual(raw[28*4096:],out[28*4096:])
        self.assertEqual(receipt['request'],request)

    def test_family_rejection_does_not_disable_independent_money(self):
        raw=save()
        with self.assertRaises(ValueError):c.derive(raw,ROM,{'money':100,'items':{'remove':13}})
        self.assertEqual(c.inspect(c.derive(raw,ROM,{'money':100})[0],ROM)['money']['money'],100)
        for request in ({},{'party':[]},{'party':[{'slot':0,'changes':{'friendship':1}}]*2},
                        {'money':True},{'items':{'potion_quantity':99}}):
            with self.subTest(request=request),self.assertRaises(ValueError):c.derive(raw,ROM,request)
