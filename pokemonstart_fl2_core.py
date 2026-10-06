#!/usr/bin/env python3
"""Unified bounded Fast Lab v0.22 workflow over already-evidenced editors.

This module adds no field capability. It profiles the exact v0.22 ROM, reports
which retained save canaries are writable, previews edits in memory, and writes
only a separately verified output file.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any, Mapping

import pokemonstart_fastlab_v022_inventory_editor as inventory
import pokemonstart_fastlab_v022_money as money
import pokemonstart_fastlab_v022_party_editor as party
import pokemonstart_save_verifier as verifier

PRIVATE_ROOT = party.PRIVATE_ROOT
CAPABILITY_PROFILE = party.CAPABILITY_PROFILE
EXPECTED_ROM_SHA256 = party.EXPECTED_ROM_SHA256
ROM_DEFAULT = party.ROM_ARGUMENT_DEFAULT
OPERATIONS = ("money", "party", "inventory")


class FL2Error(ValueError):
    """Reject unsupported FL2 inputs rather than infer or broaden support."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _profile_rom_sha() -> str:
    try:
        profile = json.loads(CAPABILITY_PROFILE.read_text(encoding="utf-8"))
        schema = profile["profile_schema"]
        value = profile["profile_key"]["patched_rom_sha256"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise FL2Error("v0.22 capability profile is unreadable") from exc
    if schema != 1 or not isinstance(value, str):
        raise FL2Error("v0.22 capability profile schema is unsupported")
    return value


def _assert_module_contract() -> None:
    if not (money.ROM_SHA256 == inventory.EXPECTED_ROM_SHA256
            == party.EXPECTED_ROM_SHA256 == EXPECTED_ROM_SHA256):
        raise FL2Error("Fast Lab modules disagree on exact v0.22 ROM identity")
    if not (money.PRIVATE_ROOT == inventory.PRIVATE_ROOT == party.PRIVATE_ROOT
            == PRIVATE_ROOT):
        raise FL2Error("Fast Lab modules disagree on the private workspace boundary")


def _require_rom_hash(rom_sha256: str) -> str:
    _assert_module_contract()
    profile_hash = _profile_rom_sha()
    if profile_hash != EXPECTED_ROM_SHA256:
        raise FL2Error("capability profile and FL2 exact-build gate disagree")
    if rom_sha256 != profile_hash:
        raise FL2Error("ROM hash does not match the exact v0.22 capability profile")
    return profile_hash


def _private_file(path: str | Path, label: str, *, must_exist: bool) -> Path:
    resolved = Path(path).resolve(strict=must_exist)
    if not resolved.is_relative_to(PRIVATE_ROOT):
        raise FL2Error(f"{label} must be inside PokemonStart-private")
    if must_exist and not resolved.is_file():
        raise FL2Error(f"{label} is not a regular file")
    return resolved


def _check_rom_file(path: str | Path) -> str:
    rom = _private_file(path, "ROM", must_exist=True)
    return _require_rom_hash(sha(rom.read_bytes()))


def _money_semantic(raw: bytes) -> dict[str, Any]:
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    key = struct.unpack_from("<I", active.section(0).data, 0xF20)[0]
    stored = struct.unpack_from("<I", active.section(1).data, 0x290)[0]
    return {"value": stored ^ key, "encryption_key": key}


def _capability_status(save_sha256: str) -> dict[str, dict[str, Any]]:
    return {
        "money": {
            "write_supported": save_sha256 == money.INPUT_SHA256,
            "request": {"money": money.TARGET_MONEY},
            "scope": "exact retained Money canary only",
        },
        "party": {
            "write_supported": save_sha256 == party.SUPPORTED_INPUT_SHA256,
            "request": "one of the exact FL1 live-confirmed party transitions",
            "scope": "exact retained party canary only",
        },
        "inventory": {
            "write_supported": save_sha256 == inventory.SUPPORTED_INPUT_SHA256,
            "request": {"slot": 0, "item_id": inventory.ITEM_ID_POTION, "quantity": 3},
            "scope": "existing Potion slot 0 quantity 2->3 only",
        },
    }


def inspect_bytes(raw: bytes, rom_sha256: str) -> dict[str, Any]:
    """Inspect structure and expose only exact-save write capability labels."""
    profile_hash = _require_rom_hash(rom_sha256)
    result = verifier.verify_bytes(raw)
    save_hash = result.file_sha256
    capabilities = _capability_status(save_hash)
    supported = [name for name, item in capabilities.items() if item["write_supported"]]
    semantics: dict[str, Any] = {}
    if capabilities["money"]["write_supported"]:
        semantics["money"] = _money_semantic(raw)
    if capabilities["party"]["write_supported"]:
        semantics["party"] = party.inspect_bytes(raw)["party"]
    if capabilities["inventory"]["write_supported"]:
        semantics["inventory"] = inventory.inspect_bytes(raw)["entries"]
    return {
        "status": "SUPPORTED" if supported else "UNSUPPORTED_SAVE_PROFILE",
        "evidence_class": "Fast Lab experimental",
        "rom_sha256": profile_hash,
        "save_sha256": save_hash,
        "active_slot": result.active_slot,
        "active_counter": result.slots[result.active_slot].counter,
        "party_count": result.party_count,
        "supported_write_operations": supported,
        "capabilities": capabilities,
        "semantics": semantics,
        "non_claims": [
            "no arbitrary-save write support",
            "no nonzero-key Fast Lab generalization",
            "no broader build/version support",
        ],
    }


def _require_mapping(value: Mapping[str, Any] | dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise FL2Error("changes must be a JSON object")
    return dict(value)


def _byte_diffs(before: bytes, after: bytes) -> list[dict[str, int]]:
    if len(before) != len(after):
        raise FL2Error("editor unexpectedly changed save length")
    return [
        {"offset": offset, "from": left, "to": right}
        for offset, (left, right) in enumerate(zip(before, after))
        if left != right
    ]


def _preview_bytes(raw: bytes, rom_sha256: str, operation: str,
                   changes: Mapping[str, Any]) -> tuple[bytes, dict[str, Any]]:
    if operation not in OPERATIONS:
        raise FL2Error(f"unsupported FL2 operation: {operation}")
    inspected = inspect_bytes(raw, rom_sha256)
    capability = inspected["capabilities"][operation]
    if not capability["write_supported"]:
        raise FL2Error(f"{operation} write is unsupported for this exact save profile")
    request = _require_mapping(changes)

    legacy: dict[str, Any]
    semantic: dict[str, Any]
    if operation == "money":
        expected = {"money": money.TARGET_MONEY}
        if request != expected:
            raise FL2Error(f"Money request is bounded to {expected}")
        candidate, legacy = money.derive(raw)
        semantic = {"money": {"from": legacy["source_money"],
                              "to": legacy["target_money"]}}
    elif operation == "party":
        if not request:
            raise FL2Error("party preview requires a non-empty supported change request")
        candidate, legacy = party.derive_bytes(raw, request)
        semantic = {"party0": {"before": legacy["before"], "after": legacy["after"]},
                    "requested_changes": legacy["requested_changes"]}
    else:
        expected = {"slot": 0, "item_id": inventory.ITEM_ID_POTION, "quantity": 3}
        if request != expected:
            raise FL2Error(f"Inventory request is bounded to {expected}")
        candidate, legacy = inventory.derive_bytes(
            raw, request["slot"], request["item_id"], request["quantity"])
        semantic = {"inventory": {"slot": 0, "item_id": inventory.ITEM_ID_POTION,
                                  "quantity": legacy["quantity"]}}

    after = verifier.verify_bytes(candidate)
    diffs = _byte_diffs(raw, candidate)
    if not diffs:
        raise FL2Error("requested edit produced no byte changes")
    report = {
        "status": "PREVIEW",
        "evidence_class": "Fast Lab experimental",
        "operation": operation,
        "rom_sha256": rom_sha256,
        "source_sha256": inspected["save_sha256"],
        "output_sha256": after.file_sha256,
        "request": request,
        "semantic_diff": semantic,
        "byte_diffs": diffs,
        "changed_byte_count": len(diffs),
        "repository_verifier_accepted": True,
        "source_write_performed": False,
    }
    return candidate, report


def preview_bytes(raw: bytes, rom_sha256: str, operation: str,
                  changes: Mapping[str, Any]) -> dict[str, Any]:
    return _preview_bytes(raw, rom_sha256, operation, changes)[1]


def inspect_file(input_save: str | Path, rom_path: str | Path = ROM_DEFAULT) -> dict[str, Any]:
    rom_hash = _check_rom_file(rom_path)
    source = _private_file(input_save, "input save", must_exist=True)
    raw = source.read_bytes()
    report = inspect_bytes(raw, rom_hash)
    if sha(source.read_bytes()) != report["save_sha256"]:
        raise FL2Error("input changed during inspection")
    report["source_immutable"] = True
    return report


def preview_file(input_save: str | Path, rom_path: str | Path, operation: str,
                 changes: Mapping[str, Any]) -> dict[str, Any]:
    rom_hash = _check_rom_file(rom_path)
    source = _private_file(input_save, "input save", must_exist=True)
    raw = source.read_bytes()
    _, report = _preview_bytes(raw, rom_hash, operation, changes)
    if sha(source.read_bytes()) != report["source_sha256"]:
        raise FL2Error("input changed during preview")
    report["source_immutable"] = True
    return report


def write_file(input_save: str | Path, output_save: str | Path, rom_path: str | Path,
               operation: str, changes: Mapping[str, Any]) -> dict[str, Any]:
    rom_hash = _check_rom_file(rom_path)
    source = _private_file(input_save, "input save", must_exist=True)
    destination = _private_file(output_save, "output save", must_exist=False)
    if destination == source or destination.exists():
        raise FL2Error("output must be a new path; overwrite is refused")
    if not destination.parent.is_dir():
        raise FL2Error("output parent directory does not exist")

    raw = source.read_bytes()
    candidate, report = _preview_bytes(raw, rom_hash, operation, changes)
    if sha(source.read_bytes()) != report["source_sha256"]:
        raise FL2Error("input changed before output creation")
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise FL2Error("refusing to overwrite existing output") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(candidate)
            handle.flush()
            os.fsync(handle.fileno())
        persisted = destination.read_bytes()
        if sha(persisted) != report["output_sha256"] or persisted != candidate:
            raise FL2Error("persisted output does not match previewed candidate")
        verified = verifier.verify_bytes(persisted)
        if verified.file_sha256 != report["output_sha256"]:
            raise FL2Error("persisted output failed repository verification")
        if sha(source.read_bytes()) != report["source_sha256"]:
            raise FL2Error("input changed during output creation")
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise

    receipt = dict(report)
    receipt.update({
        "status": "GENERATED",
        "source_immutable": True,
        "output_path": str(destination),
        "repository_verifier_accepted": True,
        "source_write_performed": False,
    })
    return receipt
