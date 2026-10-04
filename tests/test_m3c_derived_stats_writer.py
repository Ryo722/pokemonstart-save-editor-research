import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_m3c_derived_stats_writer as w
import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx
from test_m3c_batch_writer import _make_save


def synthetic():
    raw = bytearray(_make_save())
    base = 5 * v.SECTOR_SIZE
    mon = base + v.PARTY_OFFSET
    struct.pack_into("<I", raw, mon, 15)  # Original effective nature: Modest.
    raw[mon + 17] = 12
    raw[mon + 27] = 1
    raw[mon + 41] = 52
    raw[mon + 42] = 11
    struct.pack_into("<H", raw, base + v.SECTION_CHECKSUM_OFFSET,
                     v.calculate_save_checksum(raw[base:base + v.SECTION_LENGTHS[1]]))
    raw = bytes(raw)
    parsed = v.verify_bytes(raw)
    profile = tx.Profile(
        input_sha256=tx.sha(raw), active_slot=0, active_counter=4,
        inactive_counter=3, section1_sector=5, party_count=1,
        record0_sha256=tx.sha(raw[mon:mon + 100]),
        sector30_sha256=tx.sha(parsed.sector30),
        sector31_sha256=tx.sha(parsed.sector31),
        footer_sha256=tx.sha(parsed.footer),
    )
    return raw, profile


class DerivedStatsTests(unittest.TestCase):
    def test_exact_private_lineage_seals_are_present(self):
        self.assertEqual(w.PRIVATE_PROFILE.input_sha256,
                         "baf0b88fd357c54e17743601bbfa26b436db467a2fd78cd1d2c598fb714c50fa")
        self.assertEqual(set(w.SEALS), w.ALLOWED_GROUPS)

    def test_each_individual_and_combined_recomputes_stats_in_field_envelope(self):
        raw, profile = synthetic()
        record_base = 5 * v.SECTOR_SIZE + v.PARTY_OFFSET
        allowed = {
            "nature_mint": {15, 90, 96},
            "hp_ev": {56, 86, 88},
            "attack_iv": {72, 73, 90},
        }
        for names in w.ALLOWED_GROUPS:
            with self.subTest(names=names):
                output, fp = w.derive_candidate(raw, names, profile)
                self.assertEqual(v.verify_bytes(output).party[0],
                                 w._expected(v.verify_bytes(raw).party[0], names))
                offsets = {record_base + offset for name in names for offset in allowed[name]}
                offsets.update({5 * v.SECTOR_SIZE + v.SECTION_CHECKSUM_OFFSET,
                                5 * v.SECTOR_SIZE + v.SECTION_CHECKSUM_OFFSET + 1})
                self.assertTrue({i for i, _, _ in fp.diffs} <= offsets)
                self.assertEqual(raw[14 * v.SECTOR_SIZE:28 * v.SECTOR_SIZE],
                                 output[14 * v.SECTOR_SIZE:28 * v.SECTOR_SIZE])
                self.assertEqual(raw[28 * v.SECTOR_SIZE:], output[28 * v.SECTOR_SIZE:])

    def test_combined_selection_is_order_independent(self):
        raw, profile = synthetic()
        a, fa = w.derive_candidate(raw, ("nature_mint", "hp_ev", "attack_iv"), profile)
        b, fb = w.derive_candidate(raw, ("attack_iv", "nature_mint", "hp_ev"), profile)
        self.assertEqual((a, fa), (b, fb))

    def test_wrong_cached_stats_fail_even_with_matching_synthetic_hash(self):
        raw, profile = synthetic()
        bad = bytearray(raw)
        base = 5 * v.SECTOR_SIZE
        bad[base + v.PARTY_OFFSET + 90] += 1
        struct.pack_into("<H", bad, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(bad[base:base + v.SECTION_LENGTHS[1]]))
        bad = bytes(bad)
        profile = tx.Profile(**{**profile.__dict__, "input_sha256": tx.sha(bad),
                                "record0_sha256": tx.sha(bad[base + v.PARTY_OFFSET:
                                                              base + v.PARTY_OFFSET + 100])})
        with self.assertRaisesRegex(tx.TransactionError, "cached stats"):
            w.derive_candidate(bad, ("hp_ev",), profile)

    def test_profile_and_group_fail_closed(self):
        raw, profile = synthetic()
        with self.assertRaisesRegex(tx.TransactionError, "profile mismatch"):
            w.derive_candidate(raw, ("hp_ev",))
        with self.assertRaisesRegex(tx.TransactionError, "unsupported derived-stat"):
            w.derive_candidate(raw, ("hp_ev", "nature_mint"), profile)
        with self.assertRaisesRegex(tx.TransactionError, "duplicate"):
            w.derive_candidate(raw, ("hp_ev", "hp_ev"), profile)
        wrong = tx.Profile(**{**profile.__dict__, "active_counter": 6})
        with self.assertRaisesRegex(tx.TransactionError, "counter"):
            w.derive_candidate(raw, ("hp_ev",), wrong)

    def test_seal_and_new_file_rules(self):
        raw, profile = synthetic()
        output, fp = w.derive_candidate(raw, ("hp_ev",), profile)
        with self.assertRaisesRegex(tx.TransactionError, "exact private seal"):
            w.build_output(raw, ("hp_ev",), profile)
        with mock.patch.dict(w.SEALS, {("hp_ev",): {
            "output_sha256": fp.output_sha256, "diffs": fp.diffs,
        }}, clear=True):
            with tempfile.TemporaryDirectory() as temp:
                source, dest = Path(temp) / "in.sav", Path(temp) / "out.sav"
                source.write_bytes(raw)
                build = lambda data: w.build_output(data, ("hp_ev",), profile)
                self.assertEqual(tx.write_new(source, dest, build), fp)
                self.assertEqual(source.read_bytes(), raw)
                self.assertEqual(dest.read_bytes(), output)
                with self.assertRaisesRegex(tx.TransactionError, "overwrite input"):
                    tx.write_new(source, source, build)
                with self.assertRaisesRegex(tx.TransactionError, "existing output"):
                    tx.write_new(source, dest, build)
                repository_output = Path(__file__).resolve().parents[1] / "work" / "forbidden.sav"
                with self.assertRaisesRegex(tx.TransactionError, "outside the repository"):
                    tx.write_new(source, repository_output, build)


if __name__ == "__main__":
    unittest.main()
