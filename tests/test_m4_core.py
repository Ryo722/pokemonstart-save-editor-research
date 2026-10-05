import tempfile
import sys
import unittest
import contextlib
import io
import os
import stat
import copy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_core as m4
import pokemonstart_m4_gui as gui
import pokemonstart_m4_cli as cli
import pokemonstart_save_verifier as v
from test_m3c_batch_writer import _make_save, _make_slot


def _advance_synthetic_game_state(raw: bytes, slot_index: int) -> bytes:
    """Model one narrow normal save: play time, event runtime, save counter."""
    result = bytearray(raw)
    for local in range(v.SLOT_SECTORS):
        base = (slot_index * v.SLOT_SECTORS + local) * v.SECTOR_SIZE
        section_id = int.from_bytes(result[base + v.SECTION_ID_OFFSET:base + v.SECTION_ID_OFFSET + 2], "little")
        if section_id == 0:
            seconds = result[base + 0x11] + 1
            if seconds > 59:
                seconds = 0
                result[base + 0x10] += 1
            result[base + 0x11] = seconds
        elif section_id == 1:
            result[base + 0x6A0 + 2 * 0x24] ^= 1  # EventObject[2] runtime flag byte
        elif section_id == 2:
            start = base + 0x210
            value = (int.from_bytes(result[start:start + 4], "little") + 1) & 0xFFFFFFFF
            result[start:start + 4] = value.to_bytes(4, "little")
        if section_id in (0, 1, 2):
            checksum = v.calculate_save_checksum(bytes(result[base:base + v.SECTION_LENGTHS[section_id]]))
            result[base + v.SECTION_CHECKSUM_OFFSET:base + v.SECTION_CHECKSUM_OFFSET + 2] = checksum.to_bytes(2, "little")
    return bytes(result)


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
        self.assertIn("PROVEN", m4.FAMILY_REGISTRY["party0-markings-0-1"])
        raw = _make_save()
        unqualified = m4.inspect(raw)
        self.assertIn("journal missing", unqualified.profile.reason)
        model = gui.display_model(unqualified)
        self.assertEqual(model["markings"], 0)
        self.assertEqual(model["actions"], ())
        result = v.verify_bytes(raw)
        node = m4.journal_fingerprint(raw, result)
        self.assertNotIn("identity", node)
        self.assertNotIn("nickname_hex", node)
        self.assertNotIn("ot_name_hex", node)
        self.assertEqual(len(node["identity_sha256"]), 64)
        root = m4.sha(raw)
        journal = {"version": 4, "root_sha256": root, "build_sha256": "a" * 64,
                   "environment_id": "synthetic",
                   "nodes": {root: node}, "edges": []}
        with patch.object(m4, "ROOT_SHA256", root):
            self.assertIn("build hash mismatch", m4.inspect(raw, journal, "b" * 64, "synthetic").profile.reason)
            self.assertIn("environment mismatch", m4.inspect(raw, journal, "a" * 64, "wrong").profile.reason)
            self.assertTrue(m4.inspect(raw, journal, "a" * 64, "synthetic").profile.eligible)
            self.assertEqual(m4.inspect(raw, journal, "a" * 64, "synthetic").capabilities[0].capability_id,
                             "markings-0-to-1")
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
        candidate = _advance_synthetic_game_state(bytes(candidate), 1)
        result = v.verify_bytes(candidate)
        self.assertEqual(m4.check_game_transition(parent, candidate, result), None)
        altered = bytearray(candidate)
        altered[0] ^= 1
        self.assertIn("previous slot", m4.check_game_transition(parent, bytes(altered), result))
        self.assertIn("counter", m4.check_game_transition({**parent, "counter": 3}, candidate, result))

        def with_payload_byte(section_id, offset):
            changed = bytearray(candidate)
            sector = result.slots[result.active_slot].section(section_id).physical_sector
            base = sector * v.SECTOR_SIZE
            changed[base + offset] ^= 1
            checksum = v.calculate_save_checksum(bytes(changed[base:base + v.SECTION_LENGTHS[section_id]]))
            changed[base + v.SECTION_CHECKSUM_OFFSET:base + v.SECTION_CHECKSUM_OFFSET + 2] = checksum.to_bytes(2, "little")
            return bytes(changed)

        for section_id, offset in ((0, 0x0E), (0, 0x10), (0, 0x11), (0, 0x12),
                                   (1, 0x6A0), (1, 0x6B0), (1, 0x6B4), (1, 0x6B8),
                                   (1, 0x6BC), (1, 0x6C0), (1, 0x6DC), (1, 0x6E4),
                                   (1, 0x724), (1, 0x72C)):
            changed = with_payload_byte(section_id, offset)
            self.assertIsNone(m4.check_game_transition(parent, changed, v.verify_bytes(changed)))
        for section_id, offset in ((0, 0x13), (1, 0x6A6), (1, 0x6DD),
                                   (2, 0x215), (3, 0x100)):
            changed = with_payload_byte(section_id, offset)
            self.assertIn("outside qualified envelope", m4.check_game_transition(parent, changed, v.verify_bytes(changed)))
        self.assertIn("play time moved backwards",
                      m4.check_game_transition({**parent, "play_time_seconds": 2}, candidate, result))
        wrong_save_count = with_payload_byte(2, 0x210)
        self.assertIn("saved-game statistic did not increment once",
                      m4.check_game_transition(parent, wrong_save_count, v.verify_bytes(wrong_save_count)))

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
        journal = {"version": 4, "root_sha256": root, "build_sha256": "c" * 64,
                   "environment_id": "synthetic",
                   "nodes": {root: node, a: {**node, "sha256": a}, b: {**node, "sha256": b}},
                   "edges": [{"kind": "game", "parent": a, "child": b},
                             {"kind": "game", "parent": b, "child": a}]}
        with patch.object(m4, "ROOT_SHA256", root):
            with self.assertRaisesRegex(m4.EligibilityError, "root-anchored"):
                m4.validate_journal(journal)

    def test_journal_rejects_unbounded_or_nonhash_data(self):
        raw = _make_save()
        root = m4.sha(raw)
        node = m4.journal_fingerprint(raw, v.verify_bytes(raw))
        journal = {"version": 4, "root_sha256": root, "build_sha256": "c" * 64,
                   "environment_id": "synthetic", "nodes": {root: node}, "edges": []}
        with patch.object(m4, "ROOT_SHA256", root):
            extra = {**journal, "private_bytes": "unwanted"}
            with self.assertRaisesRegex(m4.EligibilityError, "root/schema"):
                m4.validate_journal(extra)
            malformed = copy.deepcopy(journal)
            malformed["nodes"][root]["active_payload_sha256"][0] = "raw bytes"
            with self.assertRaisesRegex(m4.EligibilityError, "active_payload_sha256"):
                m4.validate_journal(malformed)
            malformed = copy.deepcopy(journal)
            malformed["nodes"][root]["permutation"][0] = "0"
            with self.assertRaisesRegex(m4.EligibilityError, "permutation"):
                m4.validate_journal(malformed)

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

    def test_family_constraints_and_independent_diff_audit(self):
        raw = _make_save()
        for capability in (
            m4.Capability("x", "EXACT_VECTOR", 0, 0, 1),
            m4.Capability("x", "FAMILY", 1, 0, 1),
            m4.Capability("x", "FAMILY", 0, 0, 2),
            m4.Capability("x", "FAMILY", 0, 2, 1),
        ):
            with self.assertRaisesRegex(m4.EligibilityError, "unsupported capability"):
                m4._derive_markings(raw, capability)
        permitted = m4.Capability("markings-0-to-1", "FAMILY", 0, 0, 1)
        output, plan = m4._derive_markings(raw, permitted)
        self.assertTrue(m4.audit_output(raw, output, plan).independently_verified)
        mutated = bytearray(output)
        mutated[30 * v.SECTOR_SIZE] ^= 1
        mutated = bytes(mutated)
        full_diff = tuple((i, old, new) for i, (old, new) in enumerate(zip(raw, mutated)) if old != new)
        forged_plan = replace(plan, output_sha256=m4.sha(mutated), diffs=full_diff)
        with self.assertRaisesRegex(m4.EligibilityError, "unexplained byte diff"):
            m4.audit_output(raw, mutated, forged_plan)

    @unittest.skipUnless(sys.platform == "darwin", "macOS publication proof")
    def test_proof_only_root_and_return_canaries_keep_family_closed(self):
        root, _ = m4._derive_markings(_make_save(), m4.Capability("markings-0-to-1", "FAMILY", 0, 0, 1))
        with tempfile.TemporaryDirectory() as directory, patch.object(m4, "ROOT_SHA256", m4.sha(root)):
            directory = Path(directory)
            a_path, b_path, c_path, d_path = (directory / name for name in ("A.sav", "B.sav", "C.sav", "D.sav"))
            a_path.write_bytes(root)
            rom = directory / "synthetic.gba"
            rom.write_bytes(b"synthetic build only")
            journal_path = directory / "lineage.json"
            m4.enroll_root(root, rom.read_bytes(), journal_path, "synthetic")
            receipt_b = m4.prepare_root_canary(a_path, b_path, journal_path, rom, "synthetic")
            self.assertEqual(v.verify_file(b_path).party[0].markings, 0)
            self.assertEqual(m4.inspect(b_path.read_bytes(), m4.load_journal(journal_path),
                                        m4.sha(rom.read_bytes()), "synthetic").capabilities[0].capability_id,
                             "markings-0-to-1")
            with self.assertRaisesRegex(m4.EligibilityError, "already prepared"):
                m4.prepare_root_canary(a_path, directory / "duplicate.sav", journal_path, rom, "synthetic")

            b_raw = b_path.read_bytes()
            c = bytearray(b_raw)
            for local in range(14):
                sector = bytearray(b_raw[local * v.SECTOR_SIZE:(local + 1) * v.SECTOR_SIZE])
                sector[v.SECTION_COUNTER_OFFSET:v.SECTION_COUNTER_OFFSET + 4] = (5).to_bytes(4, "little")
                new_local = (local + 1) % 14
                start = (14 + new_local) * v.SECTOR_SIZE
                c[start:start + v.SECTOR_SIZE] = sector
            c_path.write_bytes(_advance_synthetic_game_state(bytes(c), 1))
            with self.assertRaisesRegex(m4.EligibilityError, "S0/P failed"):
                m4.prepare_return_canary(c_path, d_path, journal_path, rom, "synthetic")
            m4.record_observed_game_return(c_path, journal_path, rom, receipt_b.output_sha256,
                                           "synthetic", True)
            receipt_d = m4.prepare_return_canary(c_path, d_path, journal_path, rom, "synthetic")
            self.assertTrue(receipt_d.independently_verified)
            self.assertEqual(v.verify_file(d_path).party[0].markings, 1)
            self.assertEqual(a_path.read_bytes(), root)

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
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(journal_path.stat().st_mode), 0o600)
            plan = m4.preview(raw, journal, m4.sha(rom.read_bytes()), "synthetic", "markings-0-to-1")
            b_path = directory / "B.sav"
            receipt = m4.commit(source, b_path, journal_path, rom, "synthetic", plan)
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(journal_path.stat().st_mode), 0o600)
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
            c_path.write_bytes(_advance_synthetic_game_state(bytes(c), 1))
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
