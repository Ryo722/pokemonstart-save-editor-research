from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest import mock

import pokemonstart_fl2_cli as cli


class FL2CLITests(unittest.TestCase):
    def test_inspect_dispatches_to_core_and_prints_json(self):
        with mock.patch.object(cli.core, "inspect_file", return_value={"status": "SUPPORTED"}) as call:
            stream = io.StringIO()
            with redirect_stdout(stream):
                rc = cli.main(["inspect", "/private/source.sav", "--rom", "/private/rom.gba"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(stream.getvalue())["status"], "SUPPORTED")
        call.assert_called_once()

    def test_preview_rejects_invalid_changes_json_without_calling_core(self):
        with mock.patch.object(cli.core, "preview_file") as call:
            stream = io.StringIO()
            with redirect_stdout(stream):
                rc = cli.main(["preview", "/private/source.sav", "--operation", "party",
                               "--changes-json", "not-json", "--rom", "/private/rom.gba"])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(stream.getvalue())["status"], "REJECTED")
        call.assert_not_called()

    def test_write_dispatches_operation_and_changes(self):
        receipt = {"status": "GENERATED", "output_sha256": "a" * 64}
        with mock.patch.object(cli.core, "write_file", return_value=receipt) as call:
            stream = io.StringIO()
            with redirect_stdout(stream):
                rc = cli.main(["write", "/private/source.sav", "/private/output.sav",
                               "--operation", "inventory",
                               "--changes-json", '{"slot":0,"item_id":13,"quantity":3}',
                               "--rom", "/private/rom.gba"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(stream.getvalue())["status"], "GENERATED")
        args = call.call_args.args
        self.assertEqual(args[3], "inventory")
        self.assertEqual(args[4], {"slot": 0, "item_id": 13, "quantity": 3})


if __name__ == "__main__":
    unittest.main()
