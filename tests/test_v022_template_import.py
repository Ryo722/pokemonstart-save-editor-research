import hashlib
import struct
import unittest
from unittest.mock import patch
import pokemonstart_save_verifier as v
import pokemonstart_v022_creation_audit as audit
import pokemonstart_v022_product_template_import as t
from test_m3c_derived_stats_writer import synthetic


class TemplateImportTests(unittest.TestCase):
    def test_independent_audit_builder_copies_record_and_limits_envelope(self):
        raw = bytearray(synthetic()[0])
        base = 5 * v.SECTOR_SIZE
        raw[base + v.PARTY_COUNT_OFFSET] = 4
        struct.pack_into('<H', raw, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(raw[base:base + v.SECTION_LENGTHS[1]]))
        raw = bytes(raw)
        record = bytes((i * 37 + 11) & 255 for i in range(100))
        candidate = audit.independent_template_import(raw, record)
        independent = audit.audit_template_import(raw, candidate, record)
        result = v.verify_bytes(candidate)
        self.assertEqual(result.party_count, 5)
        self.assertEqual(candidate[base + v.PARTY_OFFSET + 400:base + v.PARTY_OFFSET + 500], record)
        self.assertEqual(hashlib.sha256(record).hexdigest(), audit.sha(record))
        self.assertTrue(independent['complete_candidate_equality'])
        self.assertTrue(independent['all_outside_envelope_preserved'])
        self.assertFalse(hasattr(t, 'build_candidate'))
        self.assertEqual(set(independent['changed_offsets']) <= {
            base + v.PARTY_COUNT_OFFSET,
            *range(base + v.PARTY_OFFSET + 400, base + v.PARTY_OFFSET + 500),
            base + v.SECTION_CHECKSUM_OFFSET, base + v.SECTION_CHECKSUM_OFFSET + 1}, True)

    def test_wrong_exact_template_is_rejected(self):
        raw = bytearray(synthetic()[0])
        base = 5 * v.SECTOR_SIZE
        raw[base + v.PARTY_COUNT_OFFSET] = 4
        struct.pack_into('<H', raw, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(raw[base:base + v.SECTION_LENGTHS[1]]))
        raw = bytes(raw)
        record = bytes(100)
        with patch.object(t, 'SOURCE_SHA256', hashlib.sha256(raw).hexdigest()), \
             patch.object(t, 'TEMPLATE_SHA256', hashlib.sha256(record).hexdigest()):
            candidate, receipt = t.derive(raw, record, t.ROM_SHA256)
            self.assertEqual(v.verify_bytes(candidate).party_count, 5)
            self.assertEqual(receipt['transition'], [4, 5])
        with self.assertRaisesRegex(ValueError, 'exact immutable'):
            t.derive(raw + b'X', record, t.ROM_SHA256)
        with patch.object(t, 'SOURCE_SHA256', hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, 'exact game-generated'):
                t.derive(raw, bytes([1]) + record[1:], t.ROM_SHA256)


if __name__ == '__main__':
    unittest.main()
