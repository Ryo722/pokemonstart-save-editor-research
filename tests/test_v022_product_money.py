import struct
import unittest
import pokemonstart_v022_product_money as m
import pokemonstart_save_verifier as v
from test_fastlab_v022_money import _slot
ROM = m.profile.EXPECTED_ROM_SHA256


def save(key=0, money=3032):
    return _slot(4, money, key) + _slot(3, 3000, key) + bytes(4*4096)


class ReusableMoneyTests(unittest.TestCase):
    def test_unseen_hash_and_rotated_sections(self):
        raw=save()
        for shift in (0,1,13):
            rotated=bytearray(raw)
            for slot in range(2):
                for i in range(14):
                    src=(slot*14+i)*4096;dst=(slot*14+(i+shift)%14)*4096
                    rotated[dst:dst+4096]=raw[src:src+4096]
            self.assertEqual(m.inspect(bytes(rotated),ROM)['money'],3032)

    def test_semantic_fail_closed(self):
        for raw, rom in ((save(1),ROM),(save(money=10000000),ROM),(save(),'0'*64),(b'bad',ROM)):
            with self.subTest(rom=rom),self.assertRaises(ValueError):m.qualify(raw,rom)
        raw=bytearray(save());raw[0]^=1
        with self.assertRaises(ValueError):m.qualify(bytes(raw),ROM)

    def test_range_targets_full_preservation_and_repeat(self):
        raw=save()
        for target in (0,1,1234567,7654321,9999999):
            out,report=m.derive(raw,ROM,target)
            self.assertEqual(m.inspect(out,ROM)['money'],target)
            self.assertEqual(raw[14*4096:],out[14*4096:])
            self.assertEqual(out,m.derive(raw,ROM,target)[0])
            self.assertTrue(report['verifier_accepted'])
            again,_=m.derive(out,ROM,42)
            self.assertEqual(m.inspect(again,ROM)['money'],42)
        for target in (True,1.0,'1',-1,10000000,3032):
            with self.assertRaises(ValueError):m.derive(raw,ROM,target)
