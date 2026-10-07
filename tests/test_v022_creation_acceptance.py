"""Synthetic normal-SAVE progression only, never Human gameplay acceptance."""
import copy
import struct
import unittest
import test_v022_creation_writer as fixture
from test_v022_product_acceptance import resave
import pokemonstart_v022_creation_acceptance as acceptance


class CreationAcceptanceTests(unittest.TestCase):
    setUpClass=classmethod(fixture.CreationTests.setUpClass.__func__)
    setUp=fixture.CreationTests.setUp
    def test_grouped_two_semantics_normal_save_footer_later_creation(self):
        receipt=acceptance.prepare(self.raw,self.rom)
        requests=receipt['transaction']['request']['create']
        self.assertEqual(len(requests),2);self.assertNotEqual(requests[0]['species'],requests[1]['species'])
        output,_=acceptance.core.derive(self.raw,self.digest,{'create':requests},rom_bytes=self.rom)
        returned=resave(output)
        result=acceptance.check_return(self.raw,returned,self.rom,receipt)
        self.assertFalse(result['gameplay_acceptance']);self.assertFalse(result['e4_adopted'])
        self.assertTrue(result['subsequent_creator_eligible']);self.assertEqual(result['reported_gameplay_drifts'],[])
        changed=returned[:0x20000]+bytes(x^255 for x in returned[0x20000:])
        self.assertTrue(acceptance.check_return(self.raw,changed,self.rom,receipt)['emulator_footer_changed'])
    def test_rejects_unexplained_record_receipt_money_count_and_slot_changes(self):
        receipt=acceptance.prepare(self.raw,self.rom)
        output,_=acceptance.core.derive(self.raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        returned=resave(output)
        with self.assertRaises(ValueError):acceptance.check_return(self.raw,output,self.rom,receipt)
        bad=copy.deepcopy(receipt);bad['transaction']['output_sha256']='0'*64
        with self.assertRaises(ValueError):acceptance.check_return(self.raw,returned,self.rom,bad)
        v=acceptance.core.v.verify_bytes(returned);base=v.slots[v.active_slot].section(1).physical_sector*4096
        for offset in (52,56+300,56+300+14,56+300+40,56+300+44,56+300+69,656):
            wrong=bytearray(returned);wrong[base+offset]^=1
            struct.pack_into('<H',wrong,base+0xFF6,acceptance.core.v.calculate_save_checksum(wrong[base:base+0xFF0]))
            with self.subTest(offset=offset),self.assertRaises(ValueError):acceptance.check_return(self.raw,bytes(wrong),self.rom,receipt)
    def test_report_explainable_hp_pp_friendship_and_full_party_rejection(self):
        raw,_=fixture.inputs(4)
        receipt=acceptance.prepare(raw,self.rom)
        output,_=acceptance.core.derive(raw,self.digest,receipt['transaction']['request'],rom_bytes=self.rom)
        returned=bytearray(resave(output));v=acceptance.core.v.verify_bytes(returned)
        base=v.slots[v.active_slot].section(1).physical_sector*4096;record=base+56+400
        returned[record+41]+=1;returned[record+52]-=1
        struct.pack_into('<H',returned,record+86,1)
        struct.pack_into('<H',returned,base+0xFF6,acceptance.core.v.calculate_save_checksum(returned[base:base+0xFF0]))
        result=acceptance.check_return(raw,bytes(returned),self.rom,receipt)
        self.assertTrue(result['full_party_Box_rejection_checked'])
        self.assertFalse(result['subsequent_creator_eligible'])
        self.assertEqual({x['field'] for x in result['reported_gameplay_drifts']},{'friendship','moves','cached_hp_stats'})

if __name__=='__main__':unittest.main()
