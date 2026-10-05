"""Explicit PR #14 private Windows validation; never imported by production.

Usage: python tests/m4_windows_private_validation.py --rom PATH --save PATH
       --private-directory PATH

All generated artifacts stay under the supplied private directory. This
requires the exact retained ROM and root hash and uses current production
gates. Run only when a new private output is explicitly authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import m4_independent_markings_audit as independent
import pokemonstart_m4_core as core
import pokemonstart_m4_web as web
import pokemonstart_m4_publication as ntfs
import pokemonstart_save_verifier as verifier

ROM_SHA256 = "48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12"
ENVIRONMENT = "windows11-ntfs-private-validation"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def full_audit(source: bytes, output: bytes, before, after, capability) -> dict:
    expected, independent_diffs = independent.expected(source)
    require(output == expected, "output differs from independent byte derivation")
    require(after.active_slot == before.active_slot, "active slot changed")
    require(tuple(s.counter for s in after.slots) == tuple(s.counter for s in before.slots),
            "slot counter changed")
    for old_slot, new_slot in zip(before.slots, after.slots):
        require(tuple((s.section_id, s.physical_sector, s.signature) for s in old_slot.sections) ==
                tuple((s.section_id, s.physical_sector, s.signature) for s in new_slot.sections),
                "section metadata/permutation changed")
        for section in new_slot.sections:
            require(section.checksum_stored == section.checksum_calculated,
                    "section checksum failed")
    require(after.party_count == before.party_count, "party count changed")
    require(after.party[0] == replace(before.party[0], markings=capability.after),
            "party semantics changed outside markings")
    inactive = 1 - before.active_slot
    start = inactive * 14 * verifier.SECTOR_SIZE
    end = start + 14 * verifier.SECTOR_SIZE
    require(output[start:end] == source[start:end], "inactive slot changed")
    require(output[28 * verifier.SECTOR_SIZE:verifier.FLASH_SIZE] ==
            source[28 * verifier.SECTOR_SIZE:verifier.FLASH_SIZE], "sectors 28-31 changed")
    require(after.footer == before.footer, "opaque footer changed")
    for old_slot, new_slot in zip(before.slots, after.slots):
        for old_section, new_section in zip(old_slot.sections, new_slot.sections):
            left = old_section.physical_sector * verifier.SECTOR_SIZE + verifier.SECTION_LENGTHS[old_section.section_id]
            right = old_section.physical_sector * verifier.SECTOR_SIZE + verifier.SECTION_ID_OFFSET
            require(source[left:right] == output[left:right], "checksum-excluded tail changed")
    physical = before.slots[before.active_slot].section(1).physical_sector
    base = physical * verifier.SECTOR_SIZE
    marking = base + verifier.PARTY_OFFSET + core.MARKINGS_OFFSET
    allowed = {marking, base + verifier.SECTION_CHECKSUM_OFFSET,
               base + verifier.SECTION_CHECKSUM_OFFSET + 1}
    require(all(i in allowed for i, _, _ in independent_diffs), "unexplained diff")
    require(any(i == marking for i, _, _ in independent_diffs), "markings byte did not change")
    return {"changed_byte_count": len(independent_diffs),
            "diff_offsets_hex": [hex(i) for i, _, _ in independent_diffs],
            "section_checksums": "PASS", "inactive_slot": "UNCHANGED",
            "sectors_28_31": "UNCHANGED", "checksum_excluded_tails": "UNCHANGED",
            "opaque_footer": "UNCHANGED", "unexplained_diff": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--save", type=Path, required=True)
    parser.add_argument("--private-directory", type=Path, required=True)
    args = parser.parse_args()
    require(sys.platform == "win32", "actual Windows required")
    repository = Path(__file__).resolve().parent.parent
    require(not args.private_directory.resolve().is_relative_to(repository),
            "private directory is inside repository")
    rom_raw, source_raw = args.rom.read_bytes(), args.save.read_bytes()
    rom_hash = hashlib.sha256(rom_raw).hexdigest()
    source_hash = hashlib.sha256(source_raw).hexdigest()
    require(rom_hash == ROM_SHA256, "ROM SHA-256 differs from retained build")
    require(source_hash == core.ROOT_SHA256, "save SHA-256 differs from retained root")
    require(len(source_raw) == 131088, "retained save size differs")
    ntfs._local_ntfs(args.save.parent)
    before = verifier.verify_bytes(source_raw)
    require(core.structural(source_raw).eligible, "root S0 failed")
    args.private_directory.mkdir(parents=True, exist_ok=True)
    ntfs._local_ntfs(args.private_directory)
    run_dir = Path(tempfile.mkdtemp(prefix="run-", dir=args.private_directory))
    journal_path = run_dir / "windows-lineage.json"
    destination = run_dir / "markings-verified.sav"
    journal = core.enroll_root(source_raw, rom_raw, journal_path, ENVIRONMENT)
    read_only = core.inspect(source_raw, journal, rom_hash, ENVIRONMENT)
    require(read_only.structural.eligible and read_only.profile.eligible,
            "Windows-local S0/P enrollment failed")
    require(len(read_only.capabilities) == 1,
            "integrated Windows gate did not return the bounded capability")
    with nullcontext():
        inspected = core.inspect(source_raw, journal, rom_hash, ENVIRONMENT)
        require(len(inspected.capabilities) == 1, "core returned no unique FAMILY action")
        capability = inspected.capabilities[0]
        require(capability.kind == "FAMILY" and capability.party_index == 0 and
                (capability.before, capability.after) in ((0, 1), (1, 0)),
                "core returned out-of-scope capability")
        plan = core.preview(source_raw, journal, rom_hash, ENVIRONMENT,
                            capability.capability_id)
        receipt = core.commit(args.save, destination, journal_path, args.rom,
                              ENVIRONMENT, plan)
        output = destination.read_bytes()
        after = verifier.verify_bytes(output)
        require(core.audit_output(source_raw, output, plan) == receipt,
                "core independent receipt differs")
        independent_result = full_audit(source_raw, output, before, after, capability)
        require(hashlib.sha256(args.save.read_bytes()).hexdigest() == source_hash,
                "source changed after filesystem commit")
        after_fs_journal = core.load_journal(journal_path)
        require(len(after_fs_journal["nodes"]) == 2 and len(after_fs_journal["edges"]) == 1,
                "unexpected journal node/edge effect")
        workflow = web.BrowserWorkflow(journal_path, args.rom, ENVIRONMENT)
        browser = workflow.upload(args.save.name, source_raw)
        require(browser.s0_eligible and browser.p_eligible and
                browser.actions == (capability.capability_id,), "private browser S0/P/C mismatch")
        require(workflow.preview(browser.actions[0]) == plan, "browser preview changed plan")
        browser_output, browser_receipt = workflow.commit()
        require(browser_output == output and browser_receipt == receipt,
                "browser output/receipt differs from filesystem candidate")
        require(workflow.download()[0] == output, "download bytes differ")
        after_browser_journal = core.load_journal(journal_path)
        require(after_browser_journal["nodes"] == after_fs_journal["nodes"] and
                after_browser_journal["edges"] == after_fs_journal["edges"],
                "duplicate journal node/edge added")
        require(hashlib.sha256(args.save.read_bytes()).hexdigest() == source_hash,
                "source changed after browser workflow")
    require(core.write_delivery_status()[0] is True,
            "integrated Windows semantic gate is closed")
    require(web.server_options()["host"] == "127.0.0.1" and
            web.server_options()["on_air"] is False, "server settings broadened")
    report = {"environment": ENVIRONMENT, "rom_sha256": rom_hash,
              "source_sha256": source_hash, "output_sha256": hashlib.sha256(output).hexdigest(),
              "source_size": len(source_raw), "output_size": len(output),
              "active_slot": before.active_slot,
              "active_counter": before.slots[before.active_slot].counter,
              "markings_before": capability.before, "markings_after": capability.after,
              "capability": capability.capability_id, "s0": "PASS", "p": "PASS",
              "browser_workflow": "PASS", "source_unchanged": True,
              "journal_nodes": len(after_browser_journal["nodes"]),
              "journal_edges": len(after_browser_journal["edges"]), **independent_result}
    (run_dir / "private-result.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PRIVATE VALIDATION PASS")
    print("output SHA-256:", report["output_sha256"])
    print("capability:", report["capability"])
    print("changed bytes:", report["changed_byte_count"])
    print("journal nodes/edges:", report["journal_nodes"], report["journal_edges"])
    print("run directory:", run_dir)


if __name__ == "__main__":
    main()
