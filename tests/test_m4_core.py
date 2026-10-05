import tempfile
import sys
import unittest
import contextlib
import io
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_core as m4
import pokemonstart_m4_gui as gui
import pokemonstart_m4_cli as cli
import pokemonstart_save_verifier as v
from test_m3c_batch_writer import _make_save, _make_slot


class M4CoreTests(unittest.TestCase):
    def test_s0_accepts_permuted_valid_save_and_rejects_malformed(self):
        raw = _make_save()
        result = m4.structural(raw)
        self.assertTrue(result.eligible)
        self.assertEqual(result.result.active_slot, 0)
        self.assertFalse(m4.structural(raw[:-1]).eligible)
        corrupted = bytearray(raw)
        corrupted[0x100] ^= 1
        self.assertFalse(m4.structural(bytes(corrupted)).eligible)

    def test_s0_rejects_parity_mismatch(self):
        raw = bytearray(_make_save())
        # Both slots remain valid; make slot 1 newest with even counter.
        for local in range(14):
            offset = (14 + local) * v.SECTOR_SIZE + v.SECTION_COUNTER_OFFSET
            raw[offset:offset + 4] = (6).to_bytes(4, "little")
        self.assertIn("parity", m4.structural(bytes(raw)).reason)

    def test_unknown_root_missing_journal_and_wrong_build(self):
        self.assertIn("m3c-markings-0-to-1", m4.EXACT_VECTOR_REGISTRY)
        self.assertIn("BLOCKED", m4.FAMILY_REGISTRY["party0-markings-0-1"])
        raw = _make_save()
        unqualified = m4.inspect(raw)
        self.assertIn("journal missing", unqualified.profile.reason)
        model = gui.display_model(unqualified)
        self.assertEqual(model["markings"], 0)
        self.assertEqual(model["actions"], ())
        result = v.verify_bytes(raw)
        node = m4.journal_fingerprint(raw, result)
        root = m4.sha(raw)
        journal = {"version": 1, "root_sha256": root, "build_sha256": "a" * 64,
                   "environment_id": "synthetic",
                   "nodes": {root: node}, "edges": []}
        with patch.object(m4, "ROOT_SHA256", root):
            self.assertIn("build hash mismatch", m4.inspect(raw, journal, "b" * 64, "synthetic").profile.reason)
            self.assertIn("environment mismatch", m4.inspect(raw, journal, "a" * 64, "wrong").profile.reason)
            self.assertTrue(m4.inspect(raw, journal, "a" * 64, "synthetic").profile.eligible)
            self.assertEqual(m4.inspect(raw, journal, "a" * 64, "synthetic").capabilities, ())
            other = raw[:-1] + bytes((raw[-1] ^ 1,))
            self.assertIn("unknown root", m4.inspect(other, journal, "a" * 64, "synthetic").profile.reason)

    def test_game_transition_both_slot_direction_and_near_miss(self):
        raw = _make_save()
        before = v.verify_bytes(raw)
        parent = m4.journal_fingerprint(raw, before)
        # Move the active slot's section-zero position forward by one.
        next_permutation = [9, 10, 11, 12, 13, 0, 1, 2, 3, 4, 5, 6, 7, 8]
        candidate = bytearray(raw)
        start = 14 * v.SECTOR_SIZE
        candidate[start:start + 14 * v.SECTOR_SIZE] = _make_slot(5, next_permutation)
        candidate = bytes(candidate)
        result = v.verify_bytes(candidate)
        self.assertEqual(m4.check_game_transition(parent, candidate, result), None)
        altered = bytearray(candidate)
        altered[0] ^= 1
        self.assertIn("previous slot", m4.check_game_transition(parent, bytes(altered), result))
        self.assertIn("counter", m4.check_game_transition({**parent, "counter": 3}, candidate, result))

    def test_missing_broken_journal(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lineage.json"
            with self.assertRaisesRegex(m4.EligibilityError, "missing or broken"):
                m4.load_journal(path)
            path.write_text('{"version":1,"root_sha256":"bad"}')
            with self.assertRaisesRegex(m4.EligibilityError, "root/schema"):
                m4.load_journal(path)
            path.write_text("not json")
            with self.assertRaisesRegex(m4.EligibilityError, "missing or broken"):
                m4.load_journal(path)

    def test_journal_cycle_is_not_root_anchored(self):
        raw = _make_save()
        root = m4.sha(raw)
        node = m4.journal_fingerprint(raw, v.verify_bytes(raw))
        a, b = "a" * 64, "b" * 64
        journal = {"version": 1, "root_sha256": root, "build_sha256": "c" * 64,
                   "environment_id": "synthetic",
                   "nodes": {root: node, a: {**node, "sha256": a}, b: {**node, "sha256": b}},
                   "edges": [{"kind": "game", "parent": a, "child": b},
                             {"kind": "game", "parent": b, "child": a}]}
        with patch.object(m4, "ROOT_SHA256", root):
            with self.assertRaisesRegex(m4.EligibilityError, "root-anchored"):
                m4.validate_journal(journal)

    def test_cli_inspect_and_preview_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.sav"
            source.write_bytes(_make_save())
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(cli.main(["inspect", str(source)]), 0)
            self.assertIn('"eligible": true', stream.getvalue())
            self.assertIn('"C": []', stream.getvalue())
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(cli.main(["preview", str(source), "--capability", "markings-0-to-1"]), 2)
            self.assertIn("REJECTED", stream.getvalue())

    @unittest.skipUnless(sys.platform == "darwin", "macOS publication proof")
    def test_synthetic_repeated_use_across_both_slot_directions(self):
        raw = _make_save()
        root_hash = m4.sha(raw)
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(m4, "ROOT_SHA256", root_hash), \
             patch.object(m4, "FAMILY_PROVEN", True):
            directory = Path(directory)
            source = directory / "A.sav"
            source.write_bytes(raw)
            rom = directory / "synthetic.gba"
            rom.write_bytes(b"synthetic build only")
            journal_path = directory / "lineage.json"
            journal = m4.enroll_root(raw, rom.read_bytes(), journal_path, "synthetic")
            plan = m4.preview(raw, journal, m4.sha(rom.read_bytes()), "synthetic", "markings-0-to-1")
            b_path = directory / "B.sav"
            receipt = m4.commit(source, b_path, journal_path, rom, "synthetic", plan)
            self.assertTrue(receipt.independently_verified)
            self.assertEqual(v.verify_file(b_path).party[0].markings, 1)
            self.assertEqual(source.read_bytes(), raw)
            with self.assertRaisesRegex(m4.EligibilityError, "stale MutationPlan"):
                m4.commit(b_path, directory / "stale.sav", journal_path, rom, "synthetic", plan)

            b_raw = b_path.read_bytes()
            c = bytearray(b_raw)
            for local in range(14):
                sector = bytearray(b_raw[local * v.SECTOR_SIZE:(local + 1) * v.SECTOR_SIZE])
                sector[v.SECTION_COUNTER_OFFSET:v.SECTION_COUNTER_OFFSET + 4] = (5).to_bytes(4, "little")
                new_local = (local + 1) % 14
                start = (14 + new_local) * v.SECTOR_SIZE
                c[start:start + v.SECTOR_SIZE] = sector
            c_path = directory / "C.sav"
            c_path.write_bytes(bytes(c))
            with self.assertRaisesRegex(m4.EligibilityError, "observation required"):
                m4.record_observed_game_return(c_path, journal_path, rom, receipt.output_sha256,
                                               "synthetic", False)
            node = m4.record_observed_game_return(c_path, journal_path, rom,
                                                  receipt.output_sha256, "synthetic", True)
            self.assertEqual(node["active_slot"], 1)
            continued = m4.load_journal(journal_path)
            plan2 = m4.preview(c_path.read_bytes(), continued, m4.sha(rom.read_bytes()), "synthetic",
                               "markings-1-to-0")
            d_path = directory / "D.sav"
            receipt2 = m4.commit(c_path, d_path, journal_path, rom, "synthetic", plan2)
            self.assertTrue(receipt2.independently_verified)
            self.assertEqual(v.verify_file(d_path).party[0].markings, 0)


if __name__ == "__main__":
    unittest.main()
