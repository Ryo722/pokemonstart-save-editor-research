#!/usr/bin/env python3
"""One-window Tkinter adapter for the bounded M4 core."""
from __future__ import annotations

from pathlib import Path
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ModuleNotFoundError:
    tk = None
    filedialog = messagebox = ttk = None

import pokemonstart_m4_core as core


def display_model(inspection: core.Inspection) -> dict:
    result = inspection.structural.result
    party = result.party[0] if result and result.party else None
    return {
        "source": inspection.source_sha256,
        "structure": inspection.structural.reason,
        "profile": inspection.profile.reason,
        "markings": None if party is None else party.markings,
        "actions": tuple(cap.capability_id for cap in inspection.capabilities),
    }


class EditorWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("PokemonStart bounded save editor")
        root.resizable(False, False)
        self.source: Path | None = None
        self.journal: Path | None = None
        self.rom: Path | None = None
        self.inspection: core.Inspection | None = None
        self.action = tk.StringVar()
        self.environment_id = tk.StringVar()
        self.status = tk.StringVar(value="Select a save, local journal, and checked ROM.")
        self.detail = tk.StringVar(value="Original save remains the rollback copy.")
        frame = ttk.Frame(root, padding=14)
        frame.grid()
        for row, (label, callback) in enumerate((("Select .sav", self.select_save),
                                                   ("Select journal", self.select_journal),
                                                   ("Select ROM", self.select_rom))):
            ttk.Button(frame, text=label, command=callback).grid(row=row, column=0, sticky="ew", pady=3)
        ttk.Label(frame, text="Emulator environment ID used for this lineage:").grid(row=3, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.environment_id, width=40)
        entry.grid(row=4, column=0, sticky="ew")
        entry.bind("<Return>", lambda event: self.refresh())
        entry.bind("<FocusOut>", lambda event: self.refresh())
        ttk.Label(frame, textvariable=self.status, wraplength=540, justify="left").grid(row=5, column=0, sticky="w", pady=8)
        ttk.Label(frame, textvariable=self.detail, wraplength=540, justify="left").grid(row=6, column=0, sticky="w", pady=8)
        self.menu = ttk.Combobox(frame, textvariable=self.action, state="disabled", width=36)
        self.menu.grid(row=7, column=0, sticky="ew")
        self.preview_button = ttk.Button(frame, text="Preview", command=self.preview, state="disabled")
        self.preview_button.grid(row=8, column=0, sticky="ew", pady=3)
        self.commit_button = ttk.Button(frame, text="Save to new .sav", command=self.commit, state="disabled")
        self.commit_button.grid(row=9, column=0, sticky="ew", pady=3)
        ttk.Label(frame, text="Keep the original untouched. Restore it manually if the game rejects the copy.",
                  wraplength=540).grid(row=10, column=0, sticky="w", pady=8)

    def select_save(self):
        name = filedialog.askopenfilename(filetypes=[("Save files", "*.sav")])
        if name:
            self.source = Path(name)
            self.refresh()

    def select_journal(self):
        name = filedialog.askopenfilename(filetypes=[("JSON journal", "*.json")])
        if name:
            self.journal = Path(name)
            self.refresh()

    def select_rom(self):
        name = filedialog.askopenfilename(filetypes=[("GBA ROM", "*.gba")])
        if name:
            self.rom = Path(name)
            self.refresh()

    def refresh(self):
        self.inspection = None
        self.menu.configure(state="disabled", values=())
        self.preview_button.configure(state="disabled")
        self.commit_button.configure(state="disabled")
        if self.source is None:
            return
        try:
            raw = self.source.read_bytes()
            journal = core.load_journal(self.journal) if self.journal else None
            build_hash = core.sha(self.rom.read_bytes()) if self.rom else None
            self.inspection = core.inspect(raw, journal, build_hash, self.environment_id.get())
            model = display_model(self.inspection)
            self.status.set(f"SHA-256: {model['source']}\nS0: {model['structure']}\nP: {model['profile']}")
            self.detail.set(f"party[0] markings: {model['markings']}; available PROVEN actions: {', '.join(model['actions']) or 'none'}")
            if model["actions"]:
                self.menu.configure(state="readonly", values=model["actions"])
                self.action.set(model["actions"][0])
                self.preview_button.configure(state="normal")
        except (OSError, ValueError) as exc:
            self.status.set(f"REJECTED: {exc}")

    def preview(self):
        if not (self.source and self.journal and self.rom and self.action.get()):
            return
        try:
            raw = self.source.read_bytes()
            journal = core.load_journal(self.journal)
            plan = core.preview(raw, journal, core.sha(self.rom.read_bytes()),
                                self.environment_id.get(), self.action.get())
            self.detail.set(f"Preview: party[0] markings {plan.capability.before} → {plan.capability.after}; "
                            f"{len(plan.diffs)} changed bytes including checksum.\n"
                            f"Output SHA-256: {plan.output_sha256}\nOriginal is the rollback copy.")
            self.commit_button.configure(state="normal")
        except (OSError, ValueError) as exc:
            self.commit_button.configure(state="disabled")
            messagebox.showerror("Preview rejected", str(exc))

    def commit(self):
        if not (self.source and self.journal and self.rom and self.action.get()):
            return
        name = filedialog.asksaveasfilename(defaultextension=".sav", filetypes=[("Save files", "*.sav")])
        if not name:
            return
        if not messagebox.askyesno("Confirm separate output",
                                   "This destination must be a new file outside the repository and not an emulator live-save path. Continue?"):
            return
        try:
            raw = self.source.read_bytes()
            journal = core.load_journal(self.journal)
            plan = core.preview(raw, journal, core.sha(self.rom.read_bytes()),
                                self.environment_id.get(), self.action.get())
            receipt = core.commit(self.source, Path(name), self.journal, self.rom,
                                  self.environment_id.get(), plan)
            self.detail.set(f"Independently verified output: {receipt.output_sha256}\n"
                            f"Source: {receipt.source_sha256}\nKeep the original as rollback.")
            self.commit_button.configure(state="disabled")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save rejected", str(exc))


def main():
    if tk is None:
        raise SystemExit("Tkinter is unavailable in this Python; use a Python build with Tk support")
    root = tk.Tk()
    EditorWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
