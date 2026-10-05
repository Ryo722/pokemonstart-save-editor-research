#!/usr/bin/env python3
"""Loopback-only NiceGUI delivery adapter for the bounded M4 core."""
from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import pokemonstart_m4_core as core
import pokemonstart_save_verifier as verifier

try:
    from nicegui import events, ui
except ImportError:  # Core and CLI remain usable without the UI dependency.
    events = None
    ui = None


LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_SAVE_SIZE = verifier.FLASH_SIZE + verifier.RTC_FOOTER_SIZE


def server_options(port: int = DEFAULT_PORT) -> dict:
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("port must be between 1024 and 65535")
    return {"host": LOOPBACK_HOST, "port": port, "on_air": False,
            "reload": False, "show": False, "title": "PokemonStart bounded save editor"}


@dataclass(frozen=True)
class BrowserInspection:
    source_sha256: str
    s0_eligible: bool
    s0_reason: str
    p_eligible: bool
    p_reason: str
    species: int | None
    level: int | None
    markings: int | None
    actions: tuple[str, ...]


class BrowserWorkflow:
    """Per-browser-session state; save bytes and candidate stay in process memory."""

    def __init__(self, journal_path: str | Path, rom_path: str | Path,
                 environment_id: str):
        self.journal_path = Path(journal_path)
        self.rom_path = Path(rom_path)
        self.environment_id = environment_id
        self.source_name: str | None = None
        self.source_raw: bytes | None = None
        self.source_hash: str | None = None
        self.inspection: core.Inspection | None = None
        self.plan: core.MutationPlan | None = None
        self.output_raw: bytes | None = None
        self.receipt: core.VerificationReceipt | None = None
        self.output_name: str | None = None

    def upload(self, filename: str, raw: bytes) -> BrowserInspection:
        self._reset()
        name = Path(filename).name
        if Path(name).suffix.lower() != ".sav":
            raise core.EligibilityError("select a local .sav file")
        if not isinstance(raw, bytes) or not verifier.FLASH_SIZE <= len(raw) <= MAX_SAVE_SIZE:
            raise core.EligibilityError("save size is outside the supported structural format")
        self.source_name, self.source_raw = name, raw
        self.source_hash = hashlib.sha256(raw).hexdigest()
        self.inspection = self._inspect(raw)
        result = self.inspection.structural.result
        party0 = result.party[0] if result else None
        return BrowserInspection(
            self.source_hash, self.inspection.structural.eligible,
            self.inspection.structural.reason, self.inspection.profile.eligible,
            self.inspection.profile.reason, party0.species if party0 else None,
            party0.level if party0 else None, party0.markings if party0 else None,
            tuple(cap.capability_id for cap in self.inspection.capabilities))

    def preview(self, capability_id: str) -> core.MutationPlan:
        if self.source_raw is None or self.inspection is None:
            raise core.EligibilityError("select a save first")
        if capability_id not in {c.capability_id for c in self.inspection.capabilities}:
            raise core.EligibilityError("requested action is not returned by the S0/P/C core")
        journal, build_hash = self._bindings()
        plan = core.preview(self.source_raw, journal, build_hash, self.environment_id, capability_id)
        self.plan = plan
        self.output_raw = None
        self.receipt = None
        self.output_name = None
        return plan

    def commit(self) -> tuple[bytes, core.VerificationReceipt]:
        if self.source_raw is None or self.source_hash is None or self.plan is None:
            raise core.EligibilityError("preview a proven action first")
        if hashlib.sha256(self.source_raw).hexdigest() != self.source_hash:
            raise core.EligibilityError("stale browser source")
        output, receipt = core.commit_download(self.source_raw, self.journal_path,
            self.rom_path, self.environment_id, self.plan)
        verified = core.audit_output(self.source_raw, output, self.plan)
        if verified != receipt or hashlib.sha256(self.source_raw).hexdigest() != self.source_hash:
            raise core.EligibilityError("independent download receipt verification failed")
        journal, build_hash = self._bindings()
        result = core.inspect(output, journal, build_hash, self.environment_id)
        if not result.structural.eligible or not result.profile.eligible:
            raise core.EligibilityError("generated download is not S0/P qualified")
        if receipt.output_sha256 != hashlib.sha256(output).hexdigest():
            raise core.EligibilityError("output hash mismatch")
        stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(self.source_name or "save").stem).strip("_")
        direction = f"markings_{self.plan.capability.before}_to_{self.plan.capability.after}"
        self.output_raw, self.receipt = output, receipt
        self.output_name = f"{stem or 'save'}_{direction}_verified.sav"
        return output, receipt

    def download(self) -> tuple[bytes, str]:
        if self.output_raw is None or self.receipt is None or self.output_name is None:
            raise core.EligibilityError("no independently verified output is available")
        return self.output_raw, self.output_name

    def _inspect(self, raw: bytes) -> core.Inspection:
        journal, build_hash = self._bindings()
        return core.inspect(raw, journal, build_hash, self.environment_id)

    def _bindings(self) -> tuple[dict, str]:
        journal = core.load_journal(self.journal_path)
        build_hash = hashlib.sha256(self.rom_path.read_bytes()).hexdigest()
        return journal, build_hash

    def _reset(self) -> None:
        self.source_name = self.source_raw = self.source_hash = None
        self.inspection = self.plan = self.output_raw = self.receipt = self.output_name = None


def create_page(journal_path: str | Path, rom_path: str | Path,
                environment_id: str) -> None:
    if ui is None:
        raise RuntimeError("NiceGUI is unavailable; install requirements-m4-ui.txt")

    @ui.page("/")
    def index() -> None:
        workflow = BrowserWorkflow(journal_path, rom_path, environment_id)
        ui.label("PokemonStart bounded save editor").classes("text-h5")
        ui.label("Local-only: uploaded save data stays in this process. Keep the original as your recovery copy.")
        status = ui.label("Select a private .sav file to inspect S0/P/C.").classes("whitespace-pre-line")
        detail = ui.label("").classes("whitespace-pre-line")
        action = ui.select(options=[], label="Proven party[0] markings action").props("outlined")
        preview_button = ui.button("Preview", on_click=lambda: do_preview()).disable()
        commit_button = ui.button("Create verified download", on_click=lambda: do_commit()).disable()
        download_button = ui.button("Save verified .sav", on_click=lambda: send_download()).disable()

        async def on_upload(event: events.UploadEventArguments) -> None:
            try:
                report = workflow.upload(event.file.name, await event.file.read())
                status.text = (f"SHA-256: {report.source_sha256}\n"
                               f"S0: {report.s0_reason}\nP: {report.p_reason}")
                detail.text = (f"party[0]: species {report.species}, level {report.level}, "
                               f"markings {report.markings}\n"
                               f"PROVEN actions: {', '.join(report.actions) if report.actions else 'none'}")
                action.options = list(report.actions)
                action.value = report.actions[0] if report.actions else None
                action.update()
                preview_button.set_enabled(bool(report.actions))
                commit_button.set_enabled(False)
                download_button.set_enabled(False)
            except (OSError, ValueError) as exc:
                status.text = f"REJECTED: {exc}"
                detail.text = "No edit action is available."
                action.options, action.value = [], None
                action.update()
                preview_button.set_enabled(False)
                commit_button.set_enabled(False)
                download_button.set_enabled(False)

        def do_preview() -> None:
            try:
                plan = workflow.preview(action.value)
                detail.text = (f"Preview: party[0] markings {plan.capability.before} → "
                               f"{plan.capability.after}; {len(plan.diffs)} changed bytes including checksum.\n"
                               f"Expected output SHA-256: {plan.output_sha256}\n"
                               "The input stays unchanged; output is audited before download.")
                commit_button.set_enabled(True)
                download_button.set_enabled(False)
            except (OSError, ValueError) as exc:
                status.text = f"Preview rejected: {exc}"
                commit_button.set_enabled(False)
                download_button.set_enabled(False)

        def do_commit() -> None:
            try:
                _, receipt = workflow.commit()
                detail.text = (f"Independently verified output SHA-256: {receipt.output_sha256}\n"
                               f"Source SHA-256: {receipt.source_sha256}\n"
                               "Use Save verified .sav and choose a separate file. Never select a live emulator save.")
                commit_button.set_enabled(False)
                download_button.set_enabled(True)
            except (OSError, ValueError) as exc:
                status.text = f"Commit rejected: {exc}"
                download_button.set_enabled(False)

        def send_download() -> None:
            raw, filename = workflow.download()
            ui.download.content(raw, filename, media_type="application/octet-stream")

        def on_rejected() -> None:
            status.text = "Upload rejected."

        ui.upload(on_upload=on_upload, on_rejected=on_rejected,
                  max_file_size=MAX_SAVE_SIZE, max_files=1, multiple=False,
                  auto_upload=True, label="Select local .sav").props("accept=.sav")
        ui.separator()
        ui.label("After download, save a new copy and retain the original for recovery. "
                 "This tool never writes to an emulator live-save location.").classes("text-caption")


def run_server(journal_path: str | Path, rom_path: str | Path,
               environment_id: str, port: int = DEFAULT_PORT) -> None:
    if ui is None:
        raise RuntimeError("NiceGUI is unavailable; install requirements-m4-ui.txt")
    create_page(journal_path, rom_path, environment_id)
    ui.run(**server_options(port))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Loopback-only M4 browser editor")
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    run_server(args.journal, args.rom, args.environment, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
