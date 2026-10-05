"""macOS Tk/core smoke test with synthetic bytes only.

Run with a Python build that has Tk and a display:
    /usr/bin/python3 tests/m4_gui_smoke.py

This deliberately patches proof authority for its synthetic fixture. It does
not enable any private save action in the product.
"""
from __future__ import annotations

import sys
import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pokemonstart_m4_core as core
import pokemonstart_m4_gui as gui
import pokemonstart_save_verifier as verifier
from test_m3c_batch_writer import _make_save


def run() -> None:
    raw = _make_save()
    root_hash = core.sha(raw)
    with tempfile.TemporaryDirectory() as directory, \
            patch.object(core, "ROOT_SHA256", root_hash), \
            patch.object(core, "FAMILY_PROVEN", True):
        private_synthetic = Path(directory)
        source = private_synthetic / "A.sav"
        source.write_bytes(raw)
        rom = private_synthetic / "synthetic.gba"
        rom.write_bytes(b"synthetic build only")
        journal_path = private_synthetic / "lineage.json"
        core.enroll_root(raw, rom.read_bytes(), journal_path, "synthetic")
        output = private_synthetic / "B.sav"

        window = tk.Tk()
        window.withdraw()
        try:
            app = gui.EditorWindow(window)
            app.source, app.journal, app.rom = source, journal_path, rom
            app.environment_id.set("synthetic")
            app.refresh()
            assert "S0: S0 valid" in app.status.get()
            assert "P: journaled retained lineage" in app.status.get()
            assert str(app.menu["state"]) == "readonly"
            assert app.action.get() == "markings-0-to-1"
            with patch.object(gui.messagebox, "showerror", side_effect=AssertionError("GUI error dialog")):
                app.preview()
                assert str(app.commit_button["state"]) == "normal"
                assert "0 → 1" in app.detail.get()
                with patch.object(gui.filedialog, "asksaveasfilename", return_value=str(output)), \
                        patch.object(gui.messagebox, "askyesno", return_value=True):
                    app.commit()
            assert verifier.verify_file(output).party[0].markings == 1
            assert "Independently verified output" in app.detail.get()
            assert core.sha(source.read_bytes()) == root_hash
            window.update_idletasks()
        finally:
            window.destroy()
    print("M4 GUI/core synthetic smoke PASS")


if __name__ == "__main__":
    run()
