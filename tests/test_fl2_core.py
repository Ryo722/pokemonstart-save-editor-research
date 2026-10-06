from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_fastlab_v022_inventory_editor as inventory
import pokemonstart_fastlab_v022_money as money
import pokemonstart_fastlab_v022_party_editor as party
import pokemonstart_fl2_core as core
import pokemonstart_save_verifier as verifier
from test_fastlab_v022_inventory_editor import inventory_synthetic
from test_money_reusable import save as money_save
from test_m3c_derived_stats_writer import synthetic


class FL2CoreTests(unittest.TestCase):
    def profile_gate(self):
        return mock.patch.object(core, "_profile_rom_sha",
                                 return_value=core.EXPECTED_ROM_SHA256)

    def test_inspect_reports_reusable_money_and_exact_party_capabilities(self):
        raw, _ = synthetic()
        with self.profile_gate(), mock.patch.object(
                party, "SUPPORTED_INPUT_SHA256", core.sha(raw)):
            report = core.inspect_bytes(raw, core.EXPECTED_ROM_SHA256)
        self.assertEqual(report["status"], "SUPPORTED")
        self.assertEqual(report["supported_write_operations"], ["money", "party"])
        self.assertTrue(report["capabilities"]["party"]["write_supported"])
        self.assertTrue(report["capabilities"]["money"]["write_supported"])
        self.assertIn("party", report["semantics"])

    def test_unknown_sha_can_qualify_only_money(self):
        raw, _ = synthetic()
        with self.profile_gate():
            report = core.inspect_bytes(raw, core.EXPECTED_ROM_SHA256)
        self.assertEqual(report["status"], "SUPPORTED")
        self.assertEqual(report["supported_write_operations"], ["money"])
        self.assertEqual(set(report["semantics"]), {"money"})

    def test_wrong_rom_hash_fails_closed(self):
        raw, _ = synthetic()
        with self.profile_gate(), self.assertRaisesRegex(core.FL2Error, "ROM hash"):
            core.inspect_bytes(raw, "0" * 64)

    def test_money_preview_reuses_exact_bounded_money_derivation(self):
        raw = money_save()
        with self.profile_gate(), mock.patch.object(money, "INPUT_SHA256", core.sha(raw)):
            report = core.preview_bytes(raw, core.EXPECTED_ROM_SHA256, "money",
                                        {"money": money.TARGET_MONEY})
        self.assertEqual(report["status"], "PREVIEW")
        self.assertEqual(report["semantic_diff"]["money"],
                         {"from": money.SOURCE_MONEY, "to": money.TARGET_MONEY})
        self.assertTrue(report["repository_verifier_accepted"])
        self.assertGreater(report["changed_byte_count"], 0)

    def test_party_preview_reuses_existing_fail_closed_editor(self):
        raw, _ = synthetic()
        with self.profile_gate(), mock.patch.object(
                party, "SUPPORTED_INPUT_SHA256", core.sha(raw)):
            report = core.preview_bytes(raw, core.EXPECTED_ROM_SHA256, "party",
                                        {"friendship": 51})
            with self.assertRaises(party.EditorError):
                core.preview_bytes(raw, core.EXPECTED_ROM_SHA256, "party", {"ball": 4})
        self.assertEqual(report["operation"], "party")
        self.assertEqual(report["semantic_diff"]["party0"]["after"]["friendship"], 51)

    def test_inventory_preview_is_still_only_potion_slot0_2_to_3(self):
        raw = inventory_synthetic()
        with self.profile_gate(), mock.patch.object(
                inventory, "SUPPORTED_INPUT_SHA256", core.sha(raw)):
            report = core.preview_bytes(
                raw, core.EXPECTED_ROM_SHA256, "inventory",
                {"slot": 0, "item_id": 13, "quantity": 3})
            with self.assertRaises(core.FL2Error):
                core.preview_bytes(
                    raw, core.EXPECTED_ROM_SHA256, "inventory",
                    {"slot": 0, "item_id": 13, "quantity": 2})
        self.assertEqual(report["semantic_diff"]["inventory"]["quantity"],
                         {"from": 2, "to": 3})
        self.assertEqual(report["changed_byte_count"], 1)

    def test_write_creates_new_verified_output_and_keeps_source_immutable(self):
        raw = inventory_synthetic()
        with tempfile.TemporaryDirectory() as directory:
            # Resolve once so the mocked boundary matches _private_file()'s
            # resolved paths on macOS (/var/... may canonicalize to /private/var/...).
            root = Path(directory).resolve()
            source = root / "source.sav"
            output = root / "output.sav"
            source.write_bytes(raw)
            with self.profile_gate(), mock.patch.object(core, "PRIVATE_ROOT", root), \
                    mock.patch.object(money, "PRIVATE_ROOT", root), \
                    mock.patch.object(party, "PRIVATE_ROOT", root), \
                    mock.patch.object(inventory, "PRIVATE_ROOT", root), \
                    mock.patch.object(core, "_check_rom_file",
                                      return_value=core.EXPECTED_ROM_SHA256), \
                    mock.patch.object(inventory, "SUPPORTED_INPUT_SHA256", core.sha(raw)):
                report = core.write_file(
                    source, output, root / "rom.gba", "inventory",
                    {"slot": 0, "item_id": 13, "quantity": 3})
                with self.assertRaisesRegex(core.FL2Error, "new path"):
                    core.write_file(
                        source, output, root / "rom.gba", "inventory",
                        {"slot": 0, "item_id": 13, "quantity": 3})
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(core.sha(output.read_bytes()), report["output_sha256"])
            self.assertEqual(verifier.verify_bytes(output.read_bytes()).file_sha256,
                             report["output_sha256"])
            self.assertTrue(report["source_immutable"])


if __name__ == "__main__":
    unittest.main()
