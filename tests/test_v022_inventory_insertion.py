import struct
import unittest
from unittest.mock import patch

import pokemonstart_fastlab_v022_creation as core
import pokemonstart_v022_creation_audit as audit
import pokemonstart_save_verifier as verifier
from test_v022_creation import fixture


def inventory_fixture():
    source=fixture()
    out=bytearray(source)
    slot=verifier.verify_bytes(source).slots[verifier.verify_bytes(source).active_slot]
    base=slot.section(13).physical_sector*4096
    out[base+0xADC:base+0xFF4]=bytes(0xFF4-0xADC)
    struct.pack_into('<HHHH',out,base+0xADC,13,2,533,1)
    return bytes(out)


class InventoryInsertionTests(unittest.TestCase):
    def test_normal_save_audit_requires_inventory_persistence(self):
        source=inventory_fixture();p=audit.parse(source)
        old=p['slots'][p['active']];new=1-p['active'];out=bytearray(source)
        for sid,sector in old['sections'].items():
            data=bytearray(sector)
            struct.pack_into('<I',data,0xFFC,old['counter']+1)
            if sid==2:
                saved=struct.unpack_from('<I',data,0x210)[0]
                struct.pack_into('<I',data,0x210,(saved+1)&0xFFFFFFFF)
                struct.pack_into('<H',data,0xFF6,verifier.calculate_save_checksum(data[:verifier.SECTION_LENGTHS[sid]]))
            local=(old['positions'][sid]+1)%14
            base=(new*14+local)*4096
            out[base:base+4096]=data
        after=bytes(out)
        self.assertTrue(audit.normal_save(source,after)['regular_items_preserved'])
        parsed=audit.parse(after);bad=bytearray(after)
        base=parsed['slots'][parsed['active']]['positions'][13]*4096
        bad[base+0xADC]^=1
        verifier.verify_bytes(bytes(bad))
        with self.assertRaisesRegex(ValueError,'regular-items persistence'):
            audit.normal_save(source,bytes(bad))

    def test_independent_complete_candidate_and_no_money_deduction(self):
        source=inventory_fixture()
        with patch.object(core,'INVENTORY_SOURCE_SHA256',audit.sha(source)):
            output,report=core.insert_inventory(source,core.fl2.EXPECTED_ROM_SHA256)
        self.assertEqual(output,audit.independent_insert(source))
        receipt=audit.audit_insert(source,output)
        self.assertTrue(receipt['money_preserved'])
        self.assertEqual(len(receipt['changed_offsets']),2)
        self.assertFalse(receipt['checksum_changed'])
        self.assertEqual(audit.parse(source)['records'],audit.parse(output)['records'])
        self.assertEqual(audit.parse(source)['money'],audit.parse(output)['money'])
        self.assertTrue(report['repository_verifier_accepted'])

    def test_other_input_or_rom_rejected(self):
        source=inventory_fixture()
        with self.assertRaises(ValueError):
            core.insert_inventory(source,core.fl2.EXPECTED_ROM_SHA256)
        with patch.object(core,'INVENTORY_SOURCE_SHA256',audit.sha(source)):
            with self.assertRaises(ValueError): core.insert_inventory(source,'0'*64)

    def test_occupied_slot_existing_record_and_nonzero_tail_rejected(self):
        source=inventory_fixture(); p=audit.parse(source)
        base=p['slots'][p['active']]['positions'][13]*4096
        for offset in (0xADC,0xAE4,0xAF0):
            mutable=bytearray(source);mutable[base+offset]^=1;raw=bytes(mutable)
            with patch.object(core,'INVENTORY_SOURCE_SHA256',audit.sha(raw)):
                with self.assertRaises(ValueError): core.insert_inventory(raw,core.fl2.EXPECTED_ROM_SHA256)

    def test_unrelated_byte_modification_rejected_by_independent_audit(self):
        source=inventory_fixture(); output=bytearray(audit.independent_insert(source))
        output[-1]^=1
        with self.assertRaises(ValueError): audit.audit_insert(source,bytes(output))
