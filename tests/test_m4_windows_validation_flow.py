"""Windows-only synthetic harness; production platform gates remain untouched."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_core as core
import pokemonstart_m4_web as web
import pokemonstart_m4_windows_candidate as ntfs
from test_m3c_batch_writer import _make_save


@unittest.skipUnless(sys.platform == "win32", "actual Windows validation")
class WindowsValidationFlowTests(unittest.TestCase):
    def test_bounded_core_publication_and_browser_workflow(self):
        raw = _make_save()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ntfs._local_ntfs(root)
            source, final = root / "source.sav", root / "output.sav"
            rom, journal_path = root / "build.gba", root / "lineage.json"
            source.write_bytes(raw)
            rom.write_bytes(b"synthetic build")
            with patch.object(core, "ROOT_SHA256", core.sha(raw)), \
                 patch.object(core, "write_delivery_status", return_value=(True, "Windows validation harness")), \
                 patch.object(core, "require_write_delivery", return_value=None), \
                 patch.object(core.publication, "publish_new", side_effect=ntfs.publish_new):
                journal = core.enroll_root(raw, rom.read_bytes(), journal_path, "synthetic")
                build = hashlib.sha256(rom.read_bytes()).hexdigest()
                inspected = core.inspect(raw, journal, build, "synthetic")
                self.assertEqual(tuple(c.capability_id for c in inspected.capabilities),
                                 ("markings-0-to-1",))
                plan = core.preview(raw, journal, build, "synthetic", "markings-0-to-1")
                receipt = core.commit(source, final, journal_path, rom, "synthetic", plan)
                self.assertEqual(core.audit_output(raw, final.read_bytes(), plan), receipt)
                self.assertEqual(source.read_bytes(), raw)
                self.assertEqual(list(root.glob(".pokemonstart-stage-*")), [])

                workflow = web.BrowserWorkflow(journal_path, rom, "synthetic")
                report = workflow.upload("source.sav", raw)
                self.assertEqual(report.actions, ("markings-0-to-1",))
                workflow.preview(report.actions[0])
                download, browser_receipt = workflow.commit()
                self.assertEqual(download, final.read_bytes())
                self.assertEqual(browser_receipt, receipt)
                self.assertEqual(workflow.download()[0], download)
                self.assertEqual(source.read_bytes(), raw)

                unsupported = raw[:-1] + bytes((raw[-1] ^ 1,))
                self.assertEqual(workflow.upload("unsupported.sav", unsupported).actions, ())
                with self.assertRaises(core.EligibilityError):
                    workflow.preview("markings-0-to-1")
                with self.assertRaises(core.EligibilityError):
                    workflow.download()

                stale = web.BrowserWorkflow(journal_path, rom, "synthetic")
                stale.preview(stale.upload("source.sav", raw).actions[0])
                current = core.load_journal(journal_path)
                current["environment_id"] = "changed"
                core._write_journal(journal_path, current)
                with self.assertRaisesRegex(core.EligibilityError, "not PROVEN"):
                    stale.commit()
                with self.assertRaises(core.EligibilityError):
                    stale.download()
