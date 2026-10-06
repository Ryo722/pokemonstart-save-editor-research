import struct
import unittest
from unittest.mock import patch

import pokemonstart_fastlab_v022_creation as core
import pokemonstart_v022_creation_audit as audit
import pokemonstart_save_verifier as verifier
from test_v022_inventory_insertion import inventory_fixture

OP = 'party_append_inventory_insert'


def composed_fixture():
    raw = inventory_fixture()
    out = bytearray(raw)
    p = audit.parse(raw)
    start = p['slots'][p['active']]['positions'][1] * 4096
    struct.pack_into('<I', out, start + 0x290, 3032)
    struct.pack_into('<H', out, start + 0xFF6, audit.checksum(out[start:start + 0xFF0]))
    return bytes(out)


class CompositionTests(unittest.TestCase):
    def derive(self, raw):
        return core.derive_bytes(raw, core.fl2.EXPECTED_ROM_SHA256, OP, {})

    def test_complete_candidate_union_order_and_preserved_source(self):
        raw = composed_fixture()
        with patch.object(core, 'COMPOSED_SOURCE_SHA256', audit.sha(raw)):
            output, report = self.derive(raw)
        proof = audit.audit_composed(raw, output)
        self.assertEqual(output, audit.independent_composed(raw))
        self.assertEqual(output, audit.independent_insert(audit.independent_append(raw)))
        self.assertEqual(output, audit.independent_append(audit.independent_insert(raw)))
        self.assertEqual(set(proof['changed_offsets']),
                         set(proof['party_changed_offsets']) | set(proof['inventory_changed_offsets']))
        self.assertEqual(verifier.verify_bytes(output).party_count, 4)
        self.assertEqual(raw, composed_fixture())
        self.assertEqual(report['semantic_diff']['party_append']['party_count'], [3, 4])
        self.assertEqual(report['semantic_diff']['inventory_insert']['item_id'], 14)
        self.assertTrue(report['semantic_diff']['inventory_insert']['money_unchanged'])

    def test_logical_mapping_after_rotation(self):
        raw = composed_fixture()
        for rotation in (1, 5, 13):
            moved = bytearray(raw)
            for number in range(2):
                base = number * 14 * 4096
                for local in range(14):
                    dest = base + ((local + rotation) % 14) * 4096
                    moved[dest:dest+4096] = raw[base+local*4096:base+(local+1)*4096]
            source = bytes(moved)
            with patch.object(core, 'COMPOSED_SOURCE_SHA256', audit.sha(source)):
                output, _ = self.derive(source)
            self.assertTrue(audit.audit_composed(source, output)['offset_union_equality'])

    def test_wrong_rom_profile_and_nonempty_requests(self):
        raw = composed_fixture()
        with patch.object(core, 'COMPOSED_SOURCE_SHA256', audit.sha(raw)):
            with self.assertRaises(ValueError): core.compose_creation(raw, '0'*64)
            with patch.object(core.fl2, '_profile_rom_sha', return_value='0'*64):
                with self.assertRaises(ValueError): self.derive(raw)
            for request in ({'money':3032},{'friendship':51},{'quantity':1},{'operations':[]},[],None):
                with self.subTest(request=request), self.assertRaises(ValueError):
                    core.derive_bytes(raw,core.fl2.EXPECTED_ROM_SHA256,OP,request)

    def test_exact_root_rejects_all_shape_changes_and_single_outputs(self):
        raw = composed_fixture()
        p = audit.parse(raw)
        positions = p['slots'][p['active']]['positions']
        # Each mutation keeps valid section checksums where relevant, isolating
        # the exact-root gate from general malformed-save rejection.
        mutations = [(0,0xF20),(1,0x34),(1,0x38),(1,0x38+100),(1,0x38+200),
                     (1,0x38+300),(13,0xADC),(13,0xAE0),(13,0xAE4),(13,0xAF0)]
        with patch.object(core,'COMPOSED_SOURCE_SHA256',audit.sha(raw)):
            for sid, offset in mutations:
                bad = bytearray(raw); start = positions[sid]*4096
                bad[start+offset] ^= 1
                struct.pack_into('<H',bad,start+0xFF6,
                                 audit.checksum(bad[start:start+audit.LENGTHS[sid]]))
                with self.subTest(section=sid,offset=offset), self.assertRaises(ValueError):
                    self.derive(bytes(bad))
            for source in (audit.independent_append(raw),audit.independent_insert(raw),
                           audit.independent_composed(raw),raw[:-1]+bytes([raw[-1]^1])):
                with self.assertRaises(ValueError): self.derive(source)

    def test_count_key_inventory_checks_remain_fail_closed_with_test_hash(self):
        raw = composed_fixture(); p = audit.parse(raw)
        for sid,offset in ((0,0xF20),(1,0x34),(1,0x290),(13,0xADC),(13,0xAE0),(13,0xAE4),(13,0xAF0)):
            bad=bytearray(raw);start=p['slots'][p['active']]['positions'][sid]*4096
            bad[start+offset]^=1
            struct.pack_into('<H',bad,start+0xFF6,audit.checksum(bad[start:start+audit.LENGTHS[sid]]))
            with patch.object(core,'COMPOSED_SOURCE_SHA256',audit.sha(bytes(bad))):
                with self.subTest(section=sid,offset=offset), self.assertRaises(ValueError):
                    self.derive(bytes(bad))

    def test_auditor_rejects_unrelated_changes_or_missing_primitive(self):
        raw=composed_fixture(); output=audit.independent_composed(raw)
        for bad in (output[:-1]+bytes([output[-1]^1]),audit.independent_append(raw),audit.independent_insert(raw)):
            with self.assertRaises(ValueError): audit.audit_composed(raw,bad)

    def test_combined_gui_stale_preview_source_rom_and_output(self):
        import pokemonstart_v022_web as web
        raw=composed_fixture()
        with patch.object(core,'COMPOSED_SOURCE_SHA256',audit.sha(raw)), \
             patch.object(core.fl2,'_check_rom_file',return_value=core.fl2.EXPECTED_ROM_SHA256):
            workflow=web.BrowserWorkflow('unused.gba')
            workflow.upload('source.sav',raw)
            workflow.preview(OP,{})
            workflow.plan['semantic_diff']['inventory_insert']['item_id']=13
            with self.assertRaisesRegex(ValueError,'stale preview'): workflow.commit()
            workflow.preview(OP,{})
            with patch.object(core.fl2,'_check_rom_file',side_effect=ValueError('ROM changed')):
                with self.assertRaises(ValueError): workflow.commit()
            workflow.commit(); workflow.output_raw=raw
            with self.assertRaises(ValueError): workflow.download()
            workflow.preview(OP,{}); workflow.source_raw=raw[:-1]+b'X'
            with self.assertRaises(ValueError): workflow.commit()

    def test_normal_save_audit_records_unknown_changes_and_rejects_loss(self):
        root=composed_fixture(); candidate=audit.independent_composed(root)
        p=audit.parse(candidate); old=p['slots'][p['active']]; out=bytearray(candidate)
        for sid,sector in old['sections'].items():
            data=bytearray(sector)
            struct.pack_into('<I',data,0xFFC,old['counter']+1)
            if sid==2:
                saved=struct.unpack_from('<I',data,0x210)[0]
                struct.pack_into('<I',data,0x210,saved+1)
            if sid==4: data[0xCA]^=1  # Unknown changes must remain visible.
            struct.pack_into('<H',data,0xFF6,audit.checksum(data[:audit.LENGTHS[sid]]))
            start=((1-p['active'])*14+(old['positions'][sid]+1)%14)*4096
            out[start:start+4096]=data
        out[30*4096+100]^=1; out[-1]^=1
        returned=bytes(out)
        receipt=audit.composed_normal_save(root,candidate,returned)
        self.assertIn([4,0xCA],receipt['logical_change_classes']['unclassified'])
        self.assertEqual(receipt['extended_sectors'][30]['changed_offsets'],[100])
        self.assertTrue(receipt['footer_changed_offsets'])
        self.assertTrue(receipt['key_preserved'])
        self.assertEqual(receipt['physical_changed_byte_count'],sum(a!=b for a,b in zip(candidate,returned)))
        with patch.object(core,'COMPOSED_SOURCE_SHA256',audit.sha(root)):
            with self.assertRaises(ValueError): self.derive(returned)
        q=audit.parse(returned); active=q['slots'][q['active']]
        for sid,offset in ((1,0x38),(13,0xAE4),(1,0x290)):
            bad=bytearray(returned);start=active['positions'][sid]*4096
            bad[start+offset]^=1
            struct.pack_into('<H',bad,start+0xFF6,audit.checksum(bad[start:start+audit.LENGTHS[sid]]))
            with self.subTest(section=sid,offset=offset), self.assertRaises(ValueError):
                audit.composed_normal_save(root,candidate,bytes(bad))
