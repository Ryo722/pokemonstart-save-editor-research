from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_fastlab_v022_inventory_editor as editor
import pokemonstart_save_verifier as v
from test_m3c_derived_stats_writer import synthetic


def inventory_synthetic(quantity: int = 2) -> bytes:
    raw, _ = synthetic()
    parsed = v.verify_bytes(raw)
    active = parsed.slots[parsed.active_slot]
    section = active.section(editor.ITEM_SECTION)
    base = section.physical_sector * v.SECTOR_SIZE + editor.ITEM_OFFSET
    mutable = bytearray(raw)
    struct.pack_into("<HH", mutable, base, editor.ITEM_ID_POTION, quantity)
    return bytes(mutable)


class FastLabV022InventoryEditorTests(unittest.TestCase):
    def setUp(self):
        self.raw = inventory_synthetic()
        patcher = mock.patch.object(editor, "SUPPORTED_INPUT_SHA256", editor._sha(self.raw))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_inspect_decodes_only_the_correlated_existing_slot(self):
        result = editor.inspect_bytes(self.raw)
        self.assertEqual(result["entries"], [{"slot": 0, "item_id": 13,
                                               "item_name": "Potion", "quantity": 2}])
        self.assertEqual(result["section_id"], 13)
        self.assertEqual(result["section_relative_offset"], 0xADC)
        self.assertFalse(result["checksum_covered"])

    def test_quantity_edit_changes_only_the_quantity_byte_and_verifies(self):
        output, report = editor.derive_bytes(self.raw, 0, 13, 3)
        before = v.verify_bytes(self.raw)
        after = v.verify_bytes(output)
        section = before.slots[before.active_slot].section(13)
        expected_offset = section.physical_sector * v.SECTOR_SIZE + 0xADC + 2
        diffs = [(i, a, b) for i, (a, b) in enumerate(zip(self.raw, output)) if a != b]
        self.assertEqual(diffs, [(expected_offset, 2, 3)])
        self.assertEqual(section.checksum_stored,
                         after.slots[after.active_slot].section(13).checksum_stored)
        self.assertEqual(editor.inspect_bytes(output)["entries"][0]["quantity"], 3)
        self.assertTrue(report["verifier_accepted"])
        self.assertTrue(report["unchanged_outside_quantity"])
        self.assertEqual(editor.derive_bytes(self.raw, 0, 13, 2)[0], self.raw)

    def test_rejects_other_slots_items_quantities_and_unmapped_records(self):
        for args in ((1, 13, 3), (0, 1, 3), (0, 13, 4), (0, 13, 0), (0, 13, 1)):
            with self.subTest(args=args), self.assertRaises(editor.InventoryEditorError):
                editor.derive_bytes(self.raw, *args)
        extra = bytearray(self.raw)
        parsed = v.verify_bytes(self.raw)
        section = parsed.slots[parsed.active_slot].section(13)
        extra[section.physical_sector * v.SECTOR_SIZE + 0xAE0] = 1
        with self.assertRaisesRegex(editor.InventoryEditorError, "additional"):
            editor.inspect_bytes(bytes(extra))

    def test_new_output_helper_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.sav"
            path.write_bytes(b"keep")
            with mock.patch.object(editor, "PRIVATE_ROOT", Path(directory)):
                with self.assertRaisesRegex(editor.InventoryEditorError, "overwrite"):
                    editor.write_new_file(path, b"replace")
            self.assertEqual(path.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
