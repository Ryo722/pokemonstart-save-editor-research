#!/usr/bin/env python3
"""Diagnostic adapter for the bounded M4 core. No authority lives here."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pokemonstart_m4_core as core


def inspect_path(save: Path, journal_path: Path | None, rom_path: Path | None,
                 environment_id: str | None) -> dict:
    raw = save.read_bytes()
    journal = core.load_journal(journal_path) if journal_path else None
    build_hash = core.sha(rom_path.read_bytes()) if rom_path else None
    report = core.inspect(raw, journal, build_hash, environment_id)
    write_enabled, write_reason = core.write_delivery_status()
    values = report.structural.result.party[0] if report.structural.result else None
    return {
        "source_sha256": report.source_sha256,
        "S0": {"eligible": report.structural.eligible, "reason": report.structural.reason},
        "P": {"eligible": report.profile.eligible, "reason": report.profile.reason},
        "write_delivery": {"enabled": write_enabled, "reason": write_reason},
        "C": [{"id": cap.capability_id, "kind": cap.kind, "party_index": cap.party_index,
               "before": cap.before, "after": cap.after} for cap in report.capabilities],
        "party0": None if values is None else {"species": values.species,
                  "level": values.level, "markings": values.markings},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded M4 save eligibility and audit")
    parser.add_argument("action", choices=("inspect", "eligibility", "capabilities", "preview", "commit", "enroll-root", "record-return"))
    parser.add_argument("save", type=Path)
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--environment")
    parser.add_argument("--capability")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--parent-sha256")
    parser.add_argument("--human-observed", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "enroll-root":
            if not args.journal or not args.rom or not args.environment:
                raise core.EligibilityError("--journal, --rom, and --environment are required")
            journal = core.enroll_root(args.save.read_bytes(), args.rom.read_bytes(), args.journal,
                                       args.environment)
            print(json.dumps({"status": "ROOT_JOURNALED", "root_sha256": journal["root_sha256"],
                              "build_sha256": journal["build_sha256"]}, indent=2))
            return 0
        if args.action == "record-return":
            if not args.journal or not args.rom or not args.parent_sha256 or not args.environment:
                raise core.EligibilityError("--journal, --rom, --environment, and --parent-sha256 are required")
            node = core.record_observed_game_return(args.save, args.journal, args.rom,
                                                    args.parent_sha256, args.environment,
                                                    args.human_observed)
            print(json.dumps({"status": "JOURNALED", "source_sha256": node["sha256"],
                              "active_slot": node["active_slot"], "counter": node["counter"]}, indent=2))
            return 0
        report = inspect_path(args.save, args.journal, args.rom, args.environment)
        if args.action in ("inspect", "eligibility", "capabilities"):
            print(json.dumps(report, indent=2))
            return 0
        if not args.journal or not args.rom or not args.capability or not args.environment:
            raise core.EligibilityError("--journal, --rom, --environment, and --capability are required")
        raw = args.save.read_bytes()
        journal = core.load_journal(args.journal)
        build_hash = core.sha(args.rom.read_bytes())
        plan = core.preview(raw, journal, build_hash, args.environment, args.capability)
        if args.action == "preview":
            print(json.dumps({"source_sha256": plan.source_sha256,
                              "output_sha256": plan.output_sha256,
                              "capability": plan.capability.capability_id,
                              "before": plan.capability.before, "after": plan.capability.after,
                              "diffs": plan.diffs}, indent=2))
            return 0
        if args.output is None:
            raise core.EligibilityError("--output is required for commit")
        receipt = core.commit(args.save, args.output, args.journal, args.rom, args.environment, plan)
        print(json.dumps({"source_sha256": receipt.source_sha256,
                          "output_sha256": receipt.output_sha256,
                          "independently_verified": receipt.independently_verified,
                          "diffs": receipt.diffs}, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
