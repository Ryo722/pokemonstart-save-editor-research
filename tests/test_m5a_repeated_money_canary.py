import hashlib
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_save_verifier as v

SPEC = importlib.util.spec_from_file_location(
    "repeated", str(Path(__file__).parents[1] / "pokemonstart_m5a_repeated_money_canary.py"))
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)


def make_sector(sid, counter, data):
    sec = bytearray(0x1000)
    sec[:len(data)] = data
    struct.pack_into("<H", sec, 0xFF4, sid)
    struct.pack_into("<H", sec, 0xFF6, v.calculate_save_checksum(bytes(sec[:v.SECTION_LENGTHS[sid]])))
    struct.pack_into("<I", sec, 0xFF8, v.FILE_SIGNATURE)
    struct.pack_into("<I", sec, 0xFFC, counter)
    return bytes(sec)


def make_save(money=9_999_999, key=0, section_order=None):
    if section_order is None:
        section_order = [7, 0, 13, 2, 1, 3, 4, 5, 6, 8, 9, 10, 11, 12]
    active = []
    for sid in range(14):
        payload = bytearray(v.SECTION_LENGTHS[sid])
        if sid == 0:
            struct.pack_into("<I", payload, 0xF20, key)
        if sid == 1:
            struct.pack_into("<I", payload, 0x290, money ^ key)
        active.append(make_sector(sid, 2, payload))
    # Counter 1 in slot 1 remains valid and byte-distinct as the inactive slot.
    inactive = [make_sector(sid, 1, bytes(v.SECTION_LENGTHS[sid])) for sid in range(14)]
    ordered_active = [active[sid] for sid in section_order]
    return (b"".join(ordered_active) + b"".join(inactive) + bytes(0x1000 * 4) + bytes(range(16)))


def independent_expected(raw, target):
    result = v.verify_bytes(raw)
    sec = result.slots[result.active_slot].section(1)
    key = struct.unpack_from("<I", result.slots[result.active_slot].section(0).data, 0xF20)[0]
    out = bytearray(raw)
    base = sec.physical_sector * v.SECTOR_SIZE
    struct.pack_into("<I", out, base + 0x290, target ^ key)
    struct.pack_into("<H", out, base + 0xFF6,
                     v.calculate_save_checksum(bytes(out[base:base + v.SECTION_LENGTHS[1]])))
    return bytes(out)


class RepeatedCanaryTests(unittest.TestCase):
    def run_derivation(self, raw, expected):
        diffs = w._diffs(raw, expected)
        with patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()), \
             patch.object(w, "EXPECTED_DIFFS", diffs), patch.object(w, "EXPECTED_OUTPUT_SHA256", None):
            return w.derive_candidate(raw)

    def test_successful_exact_semantic_helper_path(self):
        raw = make_save()
        expected = independent_expected(raw, 1_234_567)
        out, receipt = self.run_derivation(raw, expected)
        self.assertEqual(out, expected)
        self.assertEqual(receipt["starting_money"], 9_999_999)
        self.assertEqual(receipt["target_money"], 1_234_567)

    def test_section_permutation_independence(self):
        raw = make_save(section_order=[13, 4, 0, 1, 12, 2, 3, 5, 6, 7, 8, 9, 10, 11])
        expected = independent_expected(raw, 1_234_567)
        out, receipt = self.run_derivation(raw, expected)
        self.assertEqual(out, expected)
        self.assertEqual(receipt["section1_physical"], 3)  # slot 0, section 1 is physical local index 3

    def test_nonzero_key_xor_semantics(self):
        raw = make_save(key=0x12345678)
        expected = independent_expected(raw, 1_234_567)
        out, _ = self.run_derivation(raw, expected)
        self.assertEqual(out, expected)
        result = v.verify_bytes(out)
        active = result.slots[result.active_slot]
        key = struct.unpack_from("<I", active.section(0).data, 0xF20)[0]
        self.assertEqual(struct.unpack_from("<I", active.section(1).data, 0x290)[0] ^ key, 1_234_567)

    def test_wrong_hash_rejected(self):
        with self.assertRaisesRegex(w.ProofError, "unrecognized input"):
            w.derive_candidate(make_save())

    def test_wrong_starting_money_rejected(self):
        raw = make_save(money=9_999_998)
        with patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(w.ProofError, "starting money mismatch"):
                w.derive_candidate(raw)

    def test_malformed_checksum_rejected(self):
        raw = bytearray(make_save())
        raw[0x3290] ^= 1
        with patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(w.ProofError, "S0 rejected"):
                w.derive_candidate(bytes(raw))

    def test_complete_diff_enforcement(self):
        raw = make_save()
        expected = independent_expected(raw, 1_234_567)
        with patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()), \
             patch.object(w, "EXPECTED_DIFFS", {}), patch.object(w, "EXPECTED_OUTPUT_SHA256", None):
            with self.assertRaisesRegex(w.ProofError, "complete diff mismatch"):
                w.derive_candidate(raw)

    def test_existing_destination_and_source_immutability(self):
        raw = make_save()
        expected = independent_expected(raw, 1_234_567)
        diffs = w._diffs(raw, expected)
        with tempfile.TemporaryDirectory() as temp:
            src, dest = Path(temp) / "src.sav", Path(temp) / "out.sav"
            src.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            with patch.object(w, "EXPECTED_INPUT_SHA256", digest), patch.object(w, "EXPECTED_DIFFS", diffs), \
                 patch.object(w, "EXPECTED_OUTPUT_SHA256", None):
                w.write_new(src, dest)
                self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), digest)
                with self.assertRaisesRegex(w.ProofError, "output already exists"):
                    w.write_new(src, dest)

    def test_input_output_alias_rejected(self):
        raw = make_save()
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.sav"
            src.write_bytes(raw)
            with self.assertRaisesRegex(w.ProofError, "aliases input"):
                w.write_new(src, src)


if __name__ == "__main__":
    unittest.main()
