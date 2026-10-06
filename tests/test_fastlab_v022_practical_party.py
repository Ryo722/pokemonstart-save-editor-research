from __future__ import annotations

import unittest
from unittest import mock

import pokemonstart_fastlab_v022_derived as derived
import pokemonstart_fastlab_v022_move as move
import pokemonstart_fastlab_v022_level as level
import pokemonstart_fastlab_v022_species as species
import pokemonstart_fastlab_v022_stats as fastlab_stats
import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx
from test_m3c_derived_stats_writer import synthetic


class FastLabV022PracticalPartyTests(unittest.TestCase):
    def test_attack_iv_uses_fastlab_cached_stat_calculation(self):
        raw, _ = synthetic()
        input_hash = tx.sha(raw)
        with mock.patch.object(derived, "INPUT_SHA256", input_hash):
            output, fp, semantics = derived.derive(raw)
        before, after = v.verify_bytes(raw), v.verify_bytes(output)
        self.assertEqual(after.party[0].ivs[1], 0)
        self.assertEqual(after.party[0].attack, 8)
        self.assertEqual(after.party[0], fastlab_stats.after_attack_iv(before.party[0]))
        record = before.slots[before.active_slot].section(1).physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
        checksum = before.slots[before.active_slot].section(1).physical_sector * v.SECTOR_SIZE + v.SECTION_CHECKSUM_OFFSET
        self.assertEqual(set(i for i, _, _ in fp.diffs), {record + 72, record + 73, record + 90, checksum, checksum + 1})
        self.assertEqual(semantics["cached_attack"], {"from": 9, "to": 8})
        self.assertEqual(raw[14 * v.SECTOR_SIZE:28 * v.SECTOR_SIZE],
                         output[14 * v.SECTOR_SIZE:28 * v.SECTOR_SIZE])

    def test_move_replacement_preserves_pp_and_other_party_state(self):
        raw, _ = synthetic()
        input_hash = tx.sha(raw)
        with mock.patch.object(derived, "INPUT_SHA256", input_hash):
            iv_output, _, _ = derived.derive(raw)
        with mock.patch.object(move, "INPUT_SHA256", tx.sha(iv_output)):
            output, fp = move.derive(iv_output)
        before, after = v.verify_bytes(iv_output), v.verify_bytes(output)
        self.assertEqual(before.party[0].moves, (33, 45, 0, 0))
        self.assertEqual(after.party[0].moves, (1, 45, 0, 0))
        self.assertEqual(after.party[0].pp, (35, 40, 0, 0))
        self.assertEqual(after.party[0].pp_bonuses, 0)
        self.assertEqual(after.party[0].ivs, before.party[0].ivs)
        record = before.slots[before.active_slot].section(1).physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
        checksum = before.slots[before.active_slot].section(1).physical_sector * v.SECTOR_SIZE + v.SECTION_CHECKSUM_OFFSET
        move_diffs = {record + 44}
        allowed_diffs = {record + 44, record + 45, checksum, checksum + 1}
        changed = set(i for i, _, _ in fp.diffs)
        self.assertTrue(move_diffs <= changed)
        self.assertTrue(changed <= allowed_diffs)
        self.assertTrue(changed & {checksum, checksum + 1})

    def test_exact_input_hash_guards_fail_closed(self):
        with self.assertRaisesRegex(derived.DerivedError, "exact retained"):
            derived.derive(b"not the allowlisted save")
        with self.assertRaisesRegex(move.MoveError, "exact derived IV"):
            move.derive(b"not the allowlisted derived save")

    def test_level_thresholds_and_species_stats_use_fastlab_calculator(self):
        raw, _ = synthetic()
        mon = v.verify_bytes(raw).party[0]
        self.assertEqual(level.medium_slow_exp(5), 135)
        self.assertEqual(level.medium_slow_exp(6), 179)
        self.assertEqual(level.level_from_medium_slow_exp(134), 4)
        self.assertEqual(level.level_from_medium_slow_exp(135), 5)
        self.assertEqual(fastlab_stats.stats(mon, level=5), (21, 21, 9, 11, 10, 13, 12))
        ivysaur = __import__("dataclasses").replace(mon, species=2)
        self.assertEqual(fastlab_stats.stats(ivysaur, level=5), (22, 22, 10, 12, 12, 15, 14))
        self.assertEqual(species._target(mon).species, 2)


if __name__ == "__main__":
    unittest.main()
