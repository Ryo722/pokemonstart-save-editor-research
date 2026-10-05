import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_core as core
import pokemonstart_m4_web as web
import pokemonstart_save_verifier as verifier
from test_m3c_batch_writer import _make_save


class NiceGuiAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source = _make_save()
        self.save_path = self.directory / "source.sav"
        self.save_path.write_bytes(self.source)
        self.rom_path = self.directory / "build.gba"
        self.rom_path.write_bytes(b"synthetic selected build")
        self.journal_path = self.directory / "lineage.json"
        self.root_patch = patch.object(core, "ROOT_SHA256", core.sha(self.source))
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        core.enroll_root(self.source, self.rom_path.read_bytes(), self.journal_path, "synthetic")
        self.workflow = web.BrowserWorkflow(self.journal_path, self.rom_path, "synthetic")

    def test_server_is_loopback_only_and_rejects_invalid_ports(self):
        options = web.server_options()
        self.assertEqual(options["host"], "127.0.0.1")
        self.assertIs(options["on_air"], False)
        self.assertIs(options["reload"], False)
        self.assertEqual(web.LOOPBACK_HOST, "127.0.0.1")
        for port in (0, 80, 65536, True):
            with self.assertRaises(ValueError):
                web.server_options(port)

    def test_unqualified_save_has_no_edit_action(self):
        save = bytearray(self.source)
        save[-1] ^= 1
        report = self.workflow.upload("unsupported.sav", bytes(save))
        self.assertTrue(report.s0_eligible)
        self.assertFalse(report.p_eligible)
        self.assertEqual(report.actions, ())
        with self.assertRaises(core.EligibilityError):
            self.workflow.preview("markings-0-to-1")
        with self.assertRaises(core.EligibilityError):
            self.workflow.download()

    def test_capability_preview_commit_independent_receipt_and_download(self):
        report = self.workflow.upload(self.save_path.name, self.save_path.read_bytes())
        self.assertTrue(report.s0_eligible)
        self.assertTrue(report.p_eligible)
        self.assertEqual(report.markings, 0)
        self.assertEqual(report.actions, ("markings-0-to-1",))
        plan = self.workflow.preview(report.actions[0])
        self.assertEqual((plan.capability.before, plan.capability.after), (0, 1))
        self.assertEqual(self.save_path.read_bytes(), self.source)

        output, receipt = self.workflow.commit()
        downloaded, filename = self.workflow.download()
        self.assertEqual(downloaded, output)
        self.assertTrue(filename.endswith("_markings_0_to_1_verified.sav"))
        self.assertEqual(receipt.output_sha256, core.sha(downloaded))
        self.assertTrue(receipt.independently_verified)
        self.assertEqual(core.audit_output(self.source, downloaded, plan), receipt)
        self.assertTrue(core.structural(downloaded).eligible)
        self.assertEqual(verifier.verify_bytes(downloaded).party[0].markings, 1)
        self.assertEqual(self.save_path.read_bytes(), self.source)
        if web.ui is not None:
            with patch.object(web.ui.download, "content") as deliver:
                web.deliver_verified_download(self.workflow)
            deliver.assert_called_once_with(downloaded, filename,
                                             media_type="application/octet-stream")

        before_repeat = core.load_journal(self.journal_path)
        repeated = web.BrowserWorkflow(self.journal_path, self.rom_path, "synthetic")
        repeated_report = repeated.upload(self.save_path.name, self.source)
        repeated.preview(repeated_report.actions[0])
        repeated_output, repeated_receipt = repeated.commit()
        self.assertEqual(repeated_output, downloaded)
        self.assertEqual(repeated_receipt.output_sha256, receipt.output_sha256)
        after_repeat = core.load_journal(self.journal_path)
        self.assertEqual(after_repeat["nodes"], before_repeat["nodes"])
        self.assertEqual(after_repeat["edges"], before_repeat["edges"])

    def test_stale_plan_rejected_if_lineage_binding_changes(self):
        report = self.workflow.upload(self.save_path.name, self.source)
        plan = self.workflow.preview(report.actions[0])
        journal = core.load_journal(self.journal_path)
        journal["environment_id"] = "changed"
        core._write_journal(self.journal_path, journal)
        with self.assertRaisesRegex(core.EligibilityError, "not PROVEN"):
            self.workflow.commit()
        with self.assertRaises(core.EligibilityError):
            self.workflow.download()

    def test_unsupported_filename_rejected_and_clears_prior_state(self):
        report = self.workflow.upload(self.save_path.name, self.source)
        self.assertTrue(report.actions)
        with self.assertRaisesRegex(core.EligibilityError, "local .sav"):
            self.workflow.upload("source.gba", self.source)
        self.assertIsNone(self.workflow.source_raw)

    def test_nicegui_browser_upload_preview_commit_and_download(self):
        if web.ui is None:
            self.skipTest("NiceGUI is an optional UI-only dependency")
        from nicegui.elements.button import Button
        from nicegui.elements.upload import Upload
        from nicegui.elements.upload_files import SmallFileUpload
        from nicegui.testing import user_simulation

        async def exercise_browser():
            expected, _ = core._derive_markings(
                self.source, core.Capability("markings-0-to-1", "FAMILY", 0, 0, 1))
            argv = ["m4_web_simulation_app.py", "--journal", str(self.journal_path),
                    "--rom", str(self.rom_path), "--environment", "synthetic"]
            with patch.object(sys, "argv", argv), patch.dict(
                    os.environ, {"PYTEST_CURRENT_TEST": "m4 browser integration"}):
                async with user_simulation(
                        main_file=Path(__file__).with_name("m4_web_simulation_app.py")) as user:
                    await user.open("/")
                    await user.should_see("Select local .sav")
                    upload = next(iter(user.find(kind=Upload).elements))
                    await upload.handle_uploads([SmallFileUpload(
                        "synthetic.sav", "application/octet-stream", self.source)])
                    await user.should_see("S0: S0 valid")
                    await user.should_see("P: journaled retained lineage")
                    await user.should_see("markings-0-to-1")
                    user.find(kind=Button, content="Preview").click()
                    await user.should_see("Expected output SHA-256")
                    user.find(kind=Button, content="Create verified download").click()
                    await user.should_see("Independently verified output SHA-256")
                    user.find(kind=Button, content="Save verified .sav").click()
                    response = await user.download.next()
                    self.assertEqual(response.content, expected)
                    self.assertEqual(self.save_path.read_bytes(), self.source)

                    unsupported = bytearray(self.source)
                    unsupported[-1] ^= 1  # opaque footer keeps S0 but breaks retained P
                    await upload.handle_uploads([SmallFileUpload(
                        "unsupported.sav", "application/octet-stream", bytes(unsupported))])
                    await user.should_see("PROVEN actions: none")
                    for label in ("Preview", "Create verified download", "Save verified .sav"):
                        button = next(iter(user.find(kind=Button, content=label).elements))
                        self.assertFalse(button.enabled, f"{label} must stay disabled for unsupported input")

        asyncio.run(exercise_browser())


if __name__ == "__main__":
    unittest.main()
