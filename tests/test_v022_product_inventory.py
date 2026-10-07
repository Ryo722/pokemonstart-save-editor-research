import struct
import unittest
import pokemonstart_v022_product_inventory as i
from test_v022_composition import composed_fixture
ROM=i.profile.EXPECTED_ROM_SHA256


class ProductInventoryTests(unittest.TestCase):
    def test_unseen_hash_quantity_insertion_preservation(self):
        raw=composed_fixture()
        out,receipt=i.derive(raw,ROM,{'potion_quantity':3,'insert_antidote':True})
        self.assertEqual([(x['item_id'],x['quantity']) for x in i.inspect(out,ROM)['entries']],[(13,3),(533,1),(14,1)])
        parsed=i.v.verify_bytes(raw)
        base=parsed.slots[parsed.active_slot].section(13).physical_sector*4096+i.OFFSET
        self.assertTrue(set(receipt['changed_offsets'])<=set(range(base,base+12)))
        self.assertEqual(out[:base],raw[:base]);self.assertEqual(out[base+12:],raw[base+12:])
        again,_=i.derive(out,ROM,{'potion_quantity':1})
        self.assertEqual(i.inspect(again,ROM)['entries'][0]['quantity'],1)
        with self.assertRaises(ValueError):i.derive(out,ROM,{'insert_antidote':True})

    def test_unknown_layout_key_range_removal_fail_closed(self):
        raw=composed_fixture()
        for changes in ({'potion_quantity':99},{'potion_quantity':True},{'remove':14}, {'insert_antidote':1}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):i.derive(raw,ROM,changes)
        parsed=i.v.verify_bytes(raw);base=parsed.slots[parsed.active_slot].section(13).physical_sector*4096
        for offset,value in ((i.OFFSET+12,13),(i.OFFSET+4,14),(i.OFFSET+8,15)):
            bad=bytearray(raw);bad[base+offset]=value
            with self.assertRaises(ValueError):i.inspect(bytes(bad),ROM)
        with self.assertRaises(ValueError):i.inspect(raw,'0'*64)
