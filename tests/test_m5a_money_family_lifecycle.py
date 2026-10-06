from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m5a_money_family as f
from tests.test_m5a_money_family import make_game_return, make_save


class MoneyFamilyLifecycleClosureTests(unittest.TestCase):
    def setUp(self):
        self.raw = make_save()
        self.root_hash = hashlib.sha256(self.raw).hexdigest()
        self.rom_bytes = b"synthetic-build"
        self.build_hash = hashlib.sha256(self.rom_bytes).hexdigest()
        self.patches = (
            patch.object(f, "FAMILY_ROOT_SHA256", self.root_hash),
            patch.object(f, "EXPECTED_BUILD_SHA256", self.build_hash),
        )
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

    def bootstrap(self, directory: str):
        base = Path(directory)
        root = base / "root.sav"
        root.write_bytes(self.raw)
        rom = base / "game.gba"
        rom.write_bytes(self.rom_bytes)
        journal = base / "journal.json"
        f.bootstrap_journal(root, journal, rom, f.SUPPORTED_ENVIRONMENT_ID)
        return root, rom, journal

    def test_end_to_end_reusable_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root, rom, journal_path = self.bootstrap(directory)
            journal = json.loads(journal_path.read_text())
            plan1 = f.preview(
                root.read_bytes(),
                journal,
                self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID,
                2_000_000,
            )
            editor1 = Path(directory) / "editor1.sav"
            with patch.object(f.sys, "platform", "darwin"):
                receipt1 = f.commit(
                    root,
                    editor1,
                    journal_path,
                    rom,
                    f.SUPPORTED_ENVIRONMENT_ID,
                    plan1,
                )
            self.assertEqual(receipt1.after_money, 2_000_000)

            returned_bytes = make_game_return(editor1.read_bytes())
            returned = Path(directory) / "return1.sav"
            returned.write_bytes(returned_bytes)
            child = f.record_game_return(
                returned,
                journal_path,
                rom,
                plan1.output_sha256,
                f.SUPPORTED_ENVIRONMENT_ID,
                True,
            )
            self.assertEqual(child["money"], 2_000_000)

            journal2 = json.loads(journal_path.read_text())
            inspected = f.inspect(
                returned_bytes,
                journal2,
                self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID,
            )
            self.assertTrue(inspected["eligible"])
            self.assertEqual(inspected["money"], 2_000_000)

            plan2 = f.preview(
                returned_bytes,
                journal2,
                self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID,
                3_000_000,
            )
            editor2 = Path(directory) / "editor2.sav"
            with patch.object(f.sys, "platform", "darwin"):
                receipt2 = f.commit(
                    returned,
                    editor2,
                    journal_path,
                    rom,
                    f.SUPPORTED_ENVIRONMENT_ID,
                    plan2,
                )
            self.assertEqual(receipt2.before_money, 2_000_000)
            self.assertEqual(receipt2.after_money, 3_000_000)
            self.assertEqual(hashlib.sha256(root.read_bytes()).hexdigest(), self.root_hash)

    def test_wrong_parent_and_human_observation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, rom, journal_path = self.bootstrap(directory)
            journal = json.loads(journal_path.read_text())
            plan = f.preview(
                root.read_bytes(), journal, self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID, 2_000_000,
            )
            editor = Path(directory) / "editor.sav"
            with patch.object(f.sys, "platform", "darwin"):
                f.commit(root, editor, journal_path, rom, f.SUPPORTED_ENVIRONMENT_ID, plan)
            returned = Path(directory) / "return.sav"
            returned.write_bytes(make_game_return(editor.read_bytes()))

            with self.assertRaisesRegex(f.MoneyFamilyError, "human game"):
                f.record_game_return(
                    returned, journal_path, rom, plan.output_sha256,
                    f.SUPPORTED_ENVIRONMENT_ID, False,
                )
            with self.assertRaisesRegex(f.MoneyFamilyError, "parent is not"):
                f.record_game_return(
                    returned, journal_path, rom, self.root_hash,
                    f.SUPPORTED_ENVIRONMENT_ID, True,
                )

    def test_duplicate_return_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, rom, journal_path = self.bootstrap(directory)
            journal = json.loads(journal_path.read_text())
            plan = f.preview(
                root.read_bytes(), journal, self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID, 2_000_000,
            )
            editor = Path(directory) / "editor.sav"
            with patch.object(f.sys, "platform", "darwin"):
                f.commit(root, editor, journal_path, rom, f.SUPPORTED_ENVIRONMENT_ID, plan)
            returned = Path(directory) / "return.sav"
            returned.write_bytes(make_game_return(editor.read_bytes()))
            f.record_game_return(
                returned, journal_path, rom, plan.output_sha256,
                f.SUPPORTED_ENVIRONMENT_ID, True,
            )
            with self.assertRaisesRegex(f.MoneyFamilyError, "already journaled"):
                f.record_game_return(
                    returned, journal_path, rom, plan.output_sha256,
                    f.SUPPORTED_ENVIRONMENT_ID, True,
                )

    def test_environment_and_journal_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, rom, journal_path = self.bootstrap(directory)
            journal = json.loads(journal_path.read_text())
            self.assertFalse(
                f.inspect(root.read_bytes(), journal, self.build_hash, "other-environment")[
                    "eligible"
                ]
            )
            tampered = json.loads(json.dumps(journal))
            tampered["environment_id"] = "other-environment"
            with self.assertRaisesRegex(f.MoneyFamilyError, "environment binding"):
                f.validate_journal(tampered)

            tampered = json.loads(json.dumps(journal))
            tampered["nodes"][self.root_hash]["money"] = 9_999_999
            with self.assertRaisesRegex(f.MoneyFamilyError, "journal fingerprint mismatch"):
                f.inspect(
                    root.read_bytes(), tampered, self.build_hash,
                    f.SUPPORTED_ENVIRONMENT_ID,
                )


if __name__ == "__main__":
    unittest.main()
