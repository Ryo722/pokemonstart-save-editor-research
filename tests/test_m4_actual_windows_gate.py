"""Real-host gate proof, separate from synthetic win32 monkeypatch tests."""
import hashlib
import tempfile
import unittest
from pathlib import Path

import pokemonstart_m4_core as core
import pokemonstart_m4_web as web
from test_m3c_batch_writer import _make_save


@unittest.skipUnless(core.sys.platform == "win32", "actual Windows gate")
class ActualWindowsGateTests(unittest.TestCase):
    def test_all_write_entry_points_reject_without_mutation(self):
        raw = _make_save()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, destination = root / "source.sav", root / "output.sav"
            rom, journal_path = root / "build.gba", root / "lineage.json"
            source.write_bytes(raw)
            rom.write_bytes(b"synthetic build")
            original_root = core.ROOT_SHA256
            try:
                core.ROOT_SHA256 = core.sha(raw)
                journal = core.enroll_root(raw, rom.read_bytes(), journal_path, "synthetic")
                before = journal_path.read_bytes()
                build = hashlib.sha256(rom.read_bytes()).hexdigest()
                inspected = core.inspect(raw, journal, build, "synthetic")
                self.assertTrue(inspected.structural.eligible)
                self.assertTrue(inspected.profile.eligible)
                self.assertEqual(inspected.capabilities, ())
                plan = core.MutationPlan(core.sha(raw), core.Capability(
                    "markings-0-to-1", "FAMILY", 0, 0, 1), "0" * 64, ())
                with self.assertRaisesRegex(core.EligibilityError, "disabled"):
                    core.preview(raw, journal, build, "synthetic", "markings-0-to-1")
                with self.assertRaisesRegex(core.EligibilityError, "disabled"):
                    core.commit_download(raw, journal_path, rom, "synthetic", plan)
                with self.assertRaisesRegex(core.EligibilityError, "disabled"):
                    core.commit(source, destination, journal_path, rom, "synthetic", plan)
                workflow = web.BrowserWorkflow(journal_path, rom, "synthetic")
                report = workflow.upload("source.sav", raw)
                self.assertTrue(report.s0_eligible and report.p_eligible)
                self.assertEqual(report.actions, ())
                for operation in (lambda: workflow.preview("markings-0-to-1"),
                                  workflow.commit, workflow.download):
                    with self.assertRaisesRegex(core.EligibilityError, "disabled"):
                        operation()
                self.assertEqual(journal_path.read_bytes(), before)
                self.assertEqual(source.read_bytes(), raw)
                self.assertFalse(destination.exists())
            finally:
                core.ROOT_SHA256 = original_root
