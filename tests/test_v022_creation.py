import struct
import unittest
from unittest.mock import patch

import pokemonstart_fastlab_v022_creation as core
import pokemonstart_v022_creation_audit as audit
import pokemonstart_save_verifier as v
from test_m3c_derived_stats_writer import synthetic


def fixture():
    raw,_=synthetic(); out=bytearray(raw)
    for slot in v.verify_bytes(raw).slots:
        s=slot.section(1); base=s.physical_sector*4096
        out[base+0x34]=3
        record=bytes(out[base+0x38:base+0x38+100])
        out[base+0x38+100:base+0x38+300]=record*2
        out[base+0x38+300:base+0x38+400]=b'\xA5'*100
        struct.pack_into('<H',out,base+0xFF6,v.calculate_save_checksum(out[base:base+0xFF0]))
    return bytes(out)


class PartyAppendTests(unittest.TestCase):
    def test_logical_mapping_survives_independent_physical_rotation(self):
        raw=fixture()
        for rotation in (1, 5, 13):
            moved=bytearray(raw)
            for number in range(2):
                start=number*14*4096
                for local in range(14):
                    dest=start+((local+rotation)%14)*4096
                    moved[dest:dest+4096]=raw[start+local*4096:start+(local+1)*4096]
            source=bytes(moved)
            with patch.object(core,'PARTY_SOURCE_SHA256',audit.sha(source)):
                output,_=core.append_party(source,core.fl2.EXPECTED_ROM_SHA256)
            self.assertEqual(output,audit.independent_append(source))
            self.assertEqual(audit.parse(output)['records'],
                             audit.parse(source)['records']+[audit.parse(source)['records'][0]])

    def test_nonzero_key_and_full_party_are_rejected_even_with_test_hash_gate(self):
        for kind in ('key','full_party'):
            raw=fixture(); mutable=bytearray(raw); parsed=v.verify_bytes(raw)
            section=parsed.slots[parsed.active_slot].section(0 if kind=='key' else 1)
            start=section.physical_sector*4096
            if kind=='key':
                struct.pack_into('<I',mutable,start+0xF20,1)
            else:
                mutable[start+0x34]=6
            struct.pack_into('<H',mutable,start+0xFF6,
                             v.calculate_save_checksum(mutable[start:start+v.SECTION_LENGTHS[section.section_id]]))
            source=bytes(mutable)
            with patch.object(core,'PARTY_SOURCE_SHA256',audit.sha(source)):
                with self.assertRaises(ValueError):
                    core.append_party(source,core.fl2.EXPECTED_ROM_SHA256)

    def test_copy_into_unoccupied_stale_record_independent_equality(self):
        raw=fixture()
        with patch.object(core,'PARTY_SOURCE_SHA256',audit.sha(raw)):
            out,report=core.append_party(raw,core.fl2.EXPECTED_ROM_SHA256)
        self.assertEqual(out,audit.independent_append(raw))
        self.assertTrue(audit.audit_append(raw,out)['complete_candidate_equality'])
        a,b=audit.parse(raw),audit.parse(out)
        self.assertEqual(b['records'],a['records']+[a['records'][0]])
        self.assertEqual(raw,fixture())
        self.assertEqual(v.verify_bytes(out).party_count,4)

    def test_exact_input_and_rom_fail_closed(self):
        raw=fixture()
        with self.assertRaises(ValueError): core.append_party(raw,core.fl2.EXPECTED_ROM_SHA256)
        with patch.object(core,'PARTY_SOURCE_SHA256',audit.sha(raw)):
            with self.assertRaises(ValueError): core.append_party(raw,'0'*64)

    def test_audit_rejects_unrelated_tail_and_corrupt_checksum(self):
        raw=fixture(); out=audit.independent_append(raw)
        changed=bytearray(out); changed[-1]^=1
        with self.assertRaises(ValueError): audit.audit_append(raw,bytes(changed))
        changed=bytearray(raw); p=audit.parse(raw)
        changed[p['slots'][p['active']]['positions'][1]*4096+50]^=1
        with self.assertRaises(ValueError): audit.parse(bytes(changed))
