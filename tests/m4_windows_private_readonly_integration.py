"""Read-only check of the prior private Windows result against production gates.

Usage: python tests/m4_windows_private_readonly_integration.py --rom PATH
       --save PATH --run-directory PATH
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import m4_independent_markings_audit as independent
import pokemonstart_m4_core as core
import pokemonstart_m4_publication as publication
import pokemonstart_m4_web as web
import pokemonstart_save_verifier as verifier


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--save", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    args = parser.parse_args()
    require(sys.platform == "win32", "actual Windows required")
    repository = Path(__file__).resolve().parent.parent
    require(not args.run_directory.resolve().is_relative_to(repository),
            "private result must stay outside repository")
    source = args.save.read_bytes()
    rom_hash = hashlib.sha256(args.rom.read_bytes()).hexdigest()
    output_path = args.run_directory / "markings-verified.sav"
    journal_path = args.run_directory / "windows-lineage.json"
    prior_report = json.loads((args.run_directory / "private-result.json").read_text())
    output = output_path.read_bytes()
    publication._local_ntfs(args.run_directory)
    require(core.sha(source) == prior_report["source_sha256"] == core.ROOT_SHA256,
            "source identity changed")
    require(rom_hash == prior_report["rom_sha256"], "ROM identity changed")
    require(core.sha(output) == prior_report["output_sha256"], "prior output changed")
    journal = core.load_journal(journal_path)
    require(journal["build_sha256"] == rom_hash, "journal build binding changed")
    require(core.write_delivery_status()[0], "integrated Windows semantic gate is closed")
    inspected = core.inspect(source, journal, rom_hash, journal["environment_id"])
    require(inspected.structural.eligible and inspected.profile.eligible,
            "integrated S0/P failed")
    require(len(inspected.capabilities) == 1 and
            inspected.capabilities[0].capability_id == prior_report["capability"],
            "integrated capability differs")
    plan = core.preview(source, journal, rom_hash, journal["environment_id"],
                        inspected.capabilities[0].capability_id)
    require(plan.output_sha256 == core.sha(output), "integrated preview differs")
    require(core.audit_output(source, output, plan).independently_verified,
            "integrated receipt audit failed")
    expected, diffs = independent.expected(source)
    require(output == expected and len(diffs) == prior_report["changed_byte_count"],
            "independent complete-byte audit differs")
    require(verifier.verify_bytes(output).party[0].markings == plan.capability.after,
            "output markings differ")
    browser = web.BrowserWorkflow(journal_path, args.rom, journal["environment_id"])
    report = browser.upload(args.save.name, source)
    require(report.s0_eligible and report.p_eligible and
            report.actions == (plan.capability.capability_id,),
            "integrated browser capability differs")
    require(browser.preview(report.actions[0]) == plan, "integrated browser preview differs")
    require(core.sha(args.save.read_bytes()) == prior_report["source_sha256"],
            "source changed during read-only check")
    require(core.sha(output_path.read_bytes()) == prior_report["output_sha256"],
            "output changed during read-only check")
    print("READ-ONLY PRODUCTION INTEGRATION CHECK PASS")


if __name__ == "__main__":
    main()
