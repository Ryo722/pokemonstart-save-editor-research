from __future__ import annotations

import tempfile
import unittest
from unittest import mock
from pathlib import Path

import pokemonstart_fastlab_v022_party_editor as editor
import pokemonstart_save_verifier as v
from test_m3c_derived_stats_writer import synthetic


class FastLabV022PartyEditorTests(unittest.TestCase):
    def setUp(self):
        self.raw, _ = synthetic()
        patcher = mock.patch.object(editor, "SUPPORTED_INPUT_SHA256", editor.sha(self.raw))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_noop_round_trip_preserves_entire_save_and_checksum(self):
        output, report = editor.derive_bytes(self.raw, {})
        self.assertEqual(output, self.raw)
        self.assertEqual(report["diffs"], [])
        self.assertEqual(report["before"], report["after"])

    def test_target_level_computes_exp_and_cached_stats(self):
        output, report = editor.derive_bytes(self.raw, {"level": 6})
        mon = v.verify_bytes(output).party[0]
        self.assertEqual((mon.level, mon.experience), (6, 179))
        self.assertEqual(report["after"]["cached_stats"], [23, 23, 11, 13, 12, 16, 15])

    def test_species_edit_preserves_level_and_coheres_exp(self):
        output, _ = editor.derive_bytes(self.raw, {"species": 2})
        mon = v.verify_bytes(output).party[0]
        self.assertEqual((mon.species, mon.level, mon.experience), (2, 5, 135))
        self.assertEqual((mon.ivs, mon.evs, mon.moves, mon.friendship),
                         ((31, 29, 26, 23, 27, 29), (0, 0, 0, 0, 0, 0),
                          (33, 45, 0, 0), 52))

    def test_move_replacement_sets_maximum_pp_and_keeps_pp_ups(self):
        output, _ = editor.derive_bytes(self.raw, {"moves": {0: 1}})
        before, after = v.verify_bytes(self.raw).party[0], v.verify_bytes(output).party[0]
        self.assertEqual(after.moves, (1, 45, 0, 0))
        self.assertEqual(after.pp[0], 35)
        self.assertEqual(after.pp[1:], before.pp[1:])
        self.assertEqual(after.pp_bonuses, before.pp_bonuses)
        self.assertEqual(editor._maximum_pp(1, 0, 0), 35)

    def test_unproven_inherited_fields_and_ranges_fail_closed(self):
        for changes in (
            {"ball": 4}, {"markings": 2}, {"nature_mint": 4},
            {"ivs": [31, 1, 26, 23, 27, 29]},
            {"evs": [80, 0, 0, 0, 0, 0]},
            {"moves": {1: 1}}, {"moves": {0: 45}},
            {"friendship": 52}, {"friendship": 53},
            {"evs": [8, 0, 0, 0, 0, 0]},
            {"species": 2, "friendship": 51},
            {"ivs": [31, 0, 26, 23, 27, 29], "friendship": 51},
        ):
            with self.subTest(changes=changes), self.assertRaises(editor.EditorError):
                editor.derive_bytes(self.raw, changes)

    def test_combined_edit_composes_fields_without_clobbering_unrelated_state(self):
        changes = {"species": 2, "level": 6, "moves": {"0": 1},
                   "ivs": [31, 0, 26, 23, 27, 29],
                   "evs": [8, 0, 0, 0, 0, 0], "friendship": 53}
        output, report = editor.derive_bytes(self.raw, changes)
        before, after = v.verify_bytes(self.raw).party[0], v.verify_bytes(output).party[0]
        self.assertEqual((after.species, after.level, after.experience), (2, 6, 179))
        self.assertEqual(after.moves[0], 1)
        self.assertEqual(after.pp[0], 35)
        self.assertEqual(after.ivs, tuple(changes["ivs"]))
        self.assertEqual(after.evs, tuple(changes["evs"]))
        self.assertEqual(after.friendship, 53)
        self.assertEqual(after.ball, before.ball)
        self.assertEqual(after.held_item, before.held_item)
        self.assertEqual(after.ability_num, before.ability_num)
        self.assertEqual(after.personality, before.personality)
        self.assertTrue(report["verifier_accepted"])
        self.assertTrue(report["unchanged_outside_party0_and_checksum"])

    def test_invalid_values_and_unproven_ability_write_fail_closed(self):
        for changes in ({"level": 5}, {"level": 7}, {"friendship": 256},
                        {"ivs": [32, 0, 0, 0, 0, 0]},
                        {"evs": [252, 252, 252, 0, 0, 0]},
                        {"moves": {4: 1}}, {"species": 3}, {"markings": 16},
                        {"ability_selector": 1}, {"mystery": 1}):
            with self.subTest(changes=changes):
                with self.assertRaises(editor.EditorError):
                    editor.derive_bytes(self.raw, changes)

    def test_unrelated_party_bytes_and_save_regions_are_preserved(self):
        output, report = editor.derive_bytes(self.raw, {"friendship": 51})
        before, after = v.verify_bytes(self.raw), v.verify_bytes(output)
        record_base = (before.slots[before.active_slot].section(1).physical_sector
                       * v.SECTOR_SIZE + v.PARTY_OFFSET)
        checksum_base = (before.slots[before.active_slot].section(1).physical_sector
                         * v.SECTOR_SIZE + v.SECTION_CHECKSUM_OFFSET)
        allowed = {record_base + 41, checksum_base, checksum_base + 1}
        self.assertTrue(set(d["offset"] for d in report["diffs"]) <= allowed)
        self.assertEqual(before.slots[before.active_slot].counter,
                         after.slots[after.active_slot].counter)
        self.assertEqual(before.sector30, after.sector30)
        self.assertEqual(before.sector31, after.sector31)

    def test_friendship_edit_preserves_observed_exp_level_and_unrelated_values(self):
        output, _ = editor.derive_bytes(self.raw, {"friendship": 51})
        before, after = v.verify_bytes(self.raw).party[0], v.verify_bytes(output).party[0]
        self.assertEqual((after.experience, after.level), (before.experience, before.level))
        self.assertEqual(after.friendship, 51)
        self.assertEqual((after.hp, after.max_hp, after.attack, after.defense,
                          after.speed, after.sp_attack, after.sp_defense),
                         (before.hp, before.max_hp, before.attack, before.defense,
                          before.speed, before.sp_attack, before.sp_defense))

    def test_unproven_species_noop_request_is_rejected(self):
        with self.assertRaisesRegex(editor.EditorError, "outside the FL1"):
            editor.derive_bytes(self.raw, {"species": 1})

    def test_new_output_helper_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.sav"
            path.write_bytes(b"keep")
            with self.assertRaisesRegex(editor.EditorError, "overwrite"):
                editor.write_new_file(path, b"replace")
            self.assertEqual(path.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
