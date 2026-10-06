#!/usr/bin/env python3
"""Bounded M5A reusable money FAMILY candidate for retained PokemonStart v0.15.

This capability is deliberately separate from the M4 markings core. It does
not change M4 provenance predicates and is not exposed through the GUI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import pokemonstart_m4_publication as publication
import pokemonstart_save_verifier as v

FAMILY_ROOT_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
EXPECTED_BUILD_SHA256 = "48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12"
SUPPORTED_ENVIRONMENT_ID = "macos-mgba-0.10.5"
OBSERVED_ENCRYPTION_KEY = 0
MIN_MONEY = 0
MAX_MONEY = 9_999_999
JOURNAL_VERSION = 1
MONEY_SECTION_ID = 1
MONEY_OFFSET = 0x0290
KEY_SECTION_ID = 0
KEY_OFFSET = 0x0F20

# Reproduce the existing M4 stable-payload mask without changing M4 code.
SAVE_BLOCK2_PLAY_TIME = range(0x0E, 0x13)
SAVE_BLOCK1_EVENT_OBJECTS_OFFSET = 0x6A0
EVENT_OBJECT_SIZE = 0x24
EVENT_OBJECT_COUNT = 16
EVENT_OBJECT_RUNTIME_FIELDS = (
    (0x00, 1), (0x10, 4), (0x14, 4), (0x18, 1), (0x1C, 1), (0x20, 1)
)
SAVE_BLOCK1_SAVED_GAME_STAT_SECTION = 2
SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET = 0x210

# Two independent normal saves changed exactly these four bytes in the
# checksum-excluded logical-section-4 parasite tail. CFRU-JP src/save.c
# source-backs section 0/4/13 unchecked tails as parasite storage.
SECTION4_ALLOWED_TAIL_OFFSETS = frozenset({0xEDE, 0xEDF, 0xEE8, 0xEE9})


class MoneyFamilyError(ValueError):
    pass


@dataclass(frozen=True)
class MoneyPlan:
    source_sha256: str
    target_money: int
    output_sha256: str
    diffs: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class MoneyReceipt:
    source_sha256: str
    output_sha256: str
    before_money: int
    after_money: int
    target_money: int
    diffs: tuple[tuple[int, int, int], ...]
    independently_verifiable: bool


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_hash(value) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _outside_repo(path: Path, label: str) -> None:
    if path.resolve(strict=False).is_relative_to(_repo_root()):
        raise MoneyFamilyError(f"{label} must be outside repository")


def _validate_target(target: int) -> None:
    if type(target) is not int or not MIN_MONEY <= target <= MAX_MONEY:
        raise MoneyFamilyError(
            f"target money outside supported range {MIN_MONEY}..{MAX_MONEY}"
        )


def _active(raw: bytes) -> tuple[v.VerificationResult, v.SlotInfo]:
    try:
        result = v.verify_bytes(raw)
    except v.VerificationError as exc:
        raise MoneyFamilyError(f"S0 rejected: {exc}") from exc
    slot = result.slots[result.active_slot]
    if slot.counter is None or result.active_slot != slot.counter % 2:
        raise MoneyFamilyError("active slot/counter parity mismatch")
    physical = {section.physical_sector for section in slot.sections}
    expected = set(
        range(
            result.active_slot * v.SLOT_SECTORS,
            (result.active_slot + 1) * v.SLOT_SECTORS,
        )
    )
    if physical != expected:
        raise MoneyFamilyError("physical section permutation invalid")
    if result.party_count < 1:
        raise MoneyFamilyError("party[0] absent")
    return result, slot


def _money(slot: v.SlotInfo) -> tuple[int, int]:
    key = struct.unpack_from("<I", slot.section(KEY_SECTION_ID).data, KEY_OFFSET)[0]
    stored = struct.unpack_from("<I", slot.section(MONEY_SECTION_ID).data, MONEY_OFFSET)[0]
    return key, stored ^ key


def _slot_hash(raw: bytes, slot: int) -> str:
    start = slot * v.SLOT_SECTORS * v.SECTOR_SIZE
    return _sha(raw[start : start + v.SLOT_SECTORS * v.SECTOR_SIZE])


def _sector_hash(raw: bytes, number: int) -> str:
    start = number * v.SECTOR_SIZE
    return _sha(raw[start : start + v.SECTOR_SIZE])


def _party0_hash(raw: bytes, result: v.VerificationResult) -> str:
    sec1 = result.slots[result.active_slot].section(1)
    base = sec1.physical_sector * v.SECTOR_SIZE + v.PARTY_OFFSET
    return _sha(raw[base : base + v.POKEMON_SIZE])


def _volatile_payload_offsets(section_id: int) -> set[int]:
    if section_id == 0:
        return set(SAVE_BLOCK2_PLAY_TIME)
    if section_id == 1:
        return {
            SAVE_BLOCK1_EVENT_OBJECTS_OFFSET
            + index * EVENT_OBJECT_SIZE
            + field_offset
            + byte
            for index in range(EVENT_OBJECT_COUNT)
            for field_offset, size in EVENT_OBJECT_RUNTIME_FIELDS
            for byte in range(size)
        }
    if section_id == SAVE_BLOCK1_SAVED_GAME_STAT_SECTION:
        return set(
            range(
                SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET,
                SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET + 4,
            )
        )
    return set()


def _stable_payload_hashes(result: v.VerificationResult) -> list[str]:
    active = result.slots[result.active_slot]
    hashes: list[str] = []
    for section in active.sections:
        payload = bytearray(section.data[: v.SECTION_LENGTHS[section.section_id]])
        for offset in _volatile_payload_offsets(section.section_id):
            payload[offset] = 0
        hashes.append(_sha(payload))
    return hashes


def _tail_hashes(
    raw: bytes, result: v.VerificationResult, *, stable: bool
) -> list[str]:
    active = result.slots[result.active_slot]
    hashes: list[str] = []
    for section in active.sections:
        base = section.physical_sector * v.SECTOR_SIZE
        start = v.SECTION_LENGTHS[section.section_id]
        tail = bytearray(raw[base + start : base + v.SECTION_ID_OFFSET])
        if stable and section.section_id == 4:
            for absolute_offset in SECTION4_ALLOWED_TAIL_OFFSETS:
                if start <= absolute_offset < v.SECTION_ID_OFFSET:
                    tail[absolute_offset - start] = 0
        hashes.append(_sha(tail))
    return hashes


def _transition_metadata(result: v.VerificationResult) -> tuple[int, int]:
    active = result.slots[result.active_slot]
    sb2 = active.section(0).data
    hours = int.from_bytes(sb2[0x0E:0x10], "little")
    minutes, seconds = sb2[0x10], sb2[0x11]
    if hours > 999 or minutes > 59 or seconds > 59:
        raise MoneyFamilyError("invalid play-time fields")
    saved = int.from_bytes(active.section(2).data[0x210:0x214], "little")
    return hours * 3600 + minutes * 60 + seconds, saved


def fingerprint(raw: bytes, result: v.VerificationResult | None = None) -> dict:
    if result is None:
        result, _ = _active(raw)
    active = result.slots[result.active_slot]
    key, money = _money(active)
    play_time, saved_count = _transition_metadata(result)
    return {
        "sha256": _sha(raw),
        "active_slot": result.active_slot,
        "counter": active.counter,
        "active_slot_sha256": _slot_hash(raw, result.active_slot),
        "key": key,
        "money": money,
        "party_count": result.party_count,
        "party0_sha256": _party0_hash(raw, result),
        "permutation": [
            section.physical_sector % v.SLOT_SECTORS for section in active.sections
        ],
        "stable_payload_sha256": _stable_payload_hashes(result),
        "tail_sha256": _tail_hashes(raw, result, stable=False),
        "stable_tail_sha256": _tail_hashes(raw, result, stable=True),
        "sector28_31_sha256": [_sector_hash(raw, i) for i in range(28, 32)],
        "play_time_seconds": play_time,
        "saved_game_count": saved_count,
        "footer_sha256": _sha(result.footer),
    }


_NODE_KEYS = {
    "sha256",
    "active_slot",
    "counter",
    "active_slot_sha256",
    "key",
    "money",
    "party_count",
    "party0_sha256",
    "permutation",
    "stable_payload_sha256",
    "tail_sha256",
    "stable_tail_sha256",
    "sector28_31_sha256",
    "play_time_seconds",
    "saved_game_count",
    "footer_sha256",
}


def validate_journal(journal: dict) -> None:
    expected_top = {
        "version",
        "root_sha256",
        "build_sha256",
        "environment_id",
        "nodes",
        "edges",
    }
    if not isinstance(journal, dict) or set(journal) != expected_top:
        raise MoneyFamilyError("journal schema mismatch")
    if (
        journal["version"] != JOURNAL_VERSION
        or journal["root_sha256"] != FAMILY_ROOT_SHA256
    ):
        raise MoneyFamilyError("journal root/version mismatch")
    if journal["build_sha256"] != EXPECTED_BUILD_SHA256:
        raise MoneyFamilyError("journal build binding mismatch")
    if journal["environment_id"] != SUPPORTED_ENVIRONMENT_ID:
        raise MoneyFamilyError("journal environment binding mismatch")
    nodes, edges = journal["nodes"], journal["edges"]
    if (
        not isinstance(nodes, dict)
        or FAMILY_ROOT_SHA256 not in nodes
        or not isinstance(edges, list)
    ):
        raise MoneyFamilyError("journal nodes/edges invalid")
    for digest, node in nodes.items():
        if (
            not _is_hash(digest)
            or not isinstance(node, dict)
            or set(node) != _NODE_KEYS
            or node.get("sha256") != digest
        ):
            raise MoneyFamilyError("journal node fingerprint malformed")
        if not all(
            _is_hash(node[field])
            for field in ("active_slot_sha256", "party0_sha256", "footer_sha256")
        ):
            raise MoneyFamilyError("journal node hash malformed")
        if node["key"] != OBSERVED_ENCRYPTION_KEY:
            raise MoneyFamilyError("journal node outside observed encryption-key boundary")
        if type(node["money"]) is not int or not MIN_MONEY <= node["money"] <= MAX_MONEY:
            raise MoneyFamilyError("journal node money malformed")
        if node["active_slot"] not in (0, 1) or type(node["counter"]) is not int:
            raise MoneyFamilyError("journal slot/counter malformed")
        if (
            not isinstance(node["permutation"], list)
            or sorted(node["permutation"]) != list(range(v.SLOT_SECTORS))
        ):
            raise MoneyFamilyError("journal permutation malformed")
        for field, length in (
            ("stable_payload_sha256", 14),
            ("tail_sha256", 14),
            ("stable_tail_sha256", 14),
            ("sector28_31_sha256", 4),
        ):
            if (
                not isinstance(node[field], list)
                or len(node[field]) != length
                or any(not _is_hash(value) for value in node[field])
            ):
                raise MoneyFamilyError(f"journal {field} malformed")
    parents: dict[str, str] = {}
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("kind") not in (
            "money-editor",
            "game",
        ):
            raise MoneyFamilyError("journal edge malformed")
        expected = (
            {"kind", "parent", "child", "target_money"}
            if edge["kind"] == "money-editor"
            else {"kind", "parent", "child"}
        )
        if set(edge) != expected:
            raise MoneyFamilyError("journal edge metadata malformed")
        parent, child = edge["parent"], edge["child"]
        if (
            parent not in nodes
            or child not in nodes
            or child == FAMILY_ROOT_SHA256
            or child in parents
        ):
            raise MoneyFamilyError("journal edge parent/child invalid")
        if edge["kind"] == "money-editor":
            _validate_target(edge["target_money"])
            if nodes[child]["money"] != edge["target_money"]:
                raise MoneyFamilyError("editor edge target mismatch")
        parents[child] = parent
    if set(parents) != set(nodes) - {FAMILY_ROOT_SHA256}:
        raise MoneyFamilyError("journal node lacks exactly one parent")
    for node in parents:
        seen: set[str] = set()
        current = node
        while current != FAMILY_ROOT_SHA256:
            if current in seen or current not in parents:
                raise MoneyFamilyError("journal lineage is not root-anchored")
            seen.add(current)
            current = parents[current]


def _read_journal(path: Path) -> dict:
    _outside_repo(path, "journal")
    try:
        journal = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MoneyFamilyError(f"journal unreadable: {exc}") from exc
    validate_journal(journal)
    return journal


def _write_journal(path: Path, journal: dict, *, create_only: bool = False) -> None:
    _outside_repo(path, "journal")
    validate_journal(journal)
    if create_only:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(journal, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(journal, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _require_build_environment(rom_path: Path, environment_id: str) -> None:
    if environment_id != SUPPORTED_ENVIRONMENT_ID:
        raise MoneyFamilyError("unsupported environment id")
    try:
        build_hash = _sha(rom_path.read_bytes())
    except OSError as exc:
        raise MoneyFamilyError(f"ROM/build unreadable: {exc}") from exc
    if build_hash != EXPECTED_BUILD_SHA256:
        raise MoneyFamilyError("selected ROM/build hash mismatch")


def bootstrap_journal(
    root_path: Path, journal_path: Path, rom_path: Path, environment_id: str
) -> dict:
    _require_build_environment(rom_path, environment_id)
    raw = root_path.read_bytes()
    if _sha(raw) != FAMILY_ROOT_SHA256:
        raise MoneyFamilyError("bootstrap source is not the adopted M5A family root")
    result, active = _active(raw)
    key, money = _money(active)
    if key != OBSERVED_ENCRYPTION_KEY or money != 1_234_567:
        raise MoneyFamilyError("family root key/money mismatch")
    journal = {
        "version": JOURNAL_VERSION,
        "root_sha256": FAMILY_ROOT_SHA256,
        "build_sha256": EXPECTED_BUILD_SHA256,
        "environment_id": SUPPORTED_ENVIRONMENT_ID,
        "nodes": {FAMILY_ROOT_SHA256: fingerprint(raw, result)},
        "edges": [],
    }
    _write_journal(journal_path, journal, create_only=True)
    return journal


def inspect(raw: bytes, journal: dict, build_sha256: str, environment_id: str) -> dict:
    validate_journal(journal)
    result, active = _active(raw)
    digest = _sha(raw)
    if build_sha256 != EXPECTED_BUILD_SHA256 or build_sha256 != journal["build_sha256"]:
        return {"eligible": False, "reason": "build mismatch", "sha256": digest}
    if (
        environment_id != SUPPORTED_ENVIRONMENT_ID
        or environment_id != journal["environment_id"]
    ):
        return {"eligible": False, "reason": "environment mismatch", "sha256": digest}
    node = journal["nodes"].get(digest)
    if node is None:
        return {
            "eligible": False,
            "reason": "save not journaled in M5A money lineage",
            "sha256": digest,
        }
    current = fingerprint(raw, result)
    if current != node:
        return {"eligible": False, "reason": "journal fingerprint mismatch", "sha256": digest}
    key, money = _money(active)
    if key != OBSERVED_ENCRYPTION_KEY:
        return {
            "eligible": False,
            "reason": "unsupported encryption key boundary",
            "sha256": digest,
        }
    if not MIN_MONEY <= money <= MAX_MONEY:
        return {"eligible": False, "reason": "money outside supported range", "sha256": digest}
    return {
        "eligible": True,
        "reason": "M5A money FAMILY candidate eligible",
        "sha256": digest,
        "money": money,
        "key": key,
        "active_slot": result.active_slot,
        "counter": active.counter,
    }


def _derive(raw: bytes, target: int) -> tuple[bytes, int, tuple[tuple[int, int, int], ...]]:
    _validate_target(target)
    result, active = _active(raw)
    key, before_money = _money(active)
    if key != OBSERVED_ENCRYPTION_KEY:
        raise MoneyFamilyError("unsupported encryption key boundary")
    if target == before_money:
        raise MoneyFamilyError("target equals current money")
    out = bytearray(raw)
    sec1 = active.section(MONEY_SECTION_ID)
    base = sec1.physical_sector * v.SECTOR_SIZE
    struct.pack_into("<I", out, base + MONEY_OFFSET, target ^ key)
    checksum = v.calculate_save_checksum(
        bytes(out[base : base + v.SECTION_LENGTHS[MONEY_SECTION_ID]])
    )
    struct.pack_into("<H", out, base + v.SECTION_CHECKSUM_OFFSET, checksum)
    candidate = bytes(out)
    allowed = set(range(base + MONEY_OFFSET, base + MONEY_OFFSET + 4)) | {
        base + v.SECTION_CHECKSUM_OFFSET,
        base + v.SECTION_CHECKSUM_OFFSET + 1,
    }
    diffs = tuple(
        (offset, before, after)
        for offset, (before, after) in enumerate(zip(raw, candidate))
        if before != after
    )
    if not diffs or any(offset not in allowed for offset, _, _ in diffs):
        raise MoneyFamilyError("unexpected byte outside money/checksum envelope")
    after_result, after_active = _active(candidate)
    out_key, out_money = _money(after_active)
    if (
        after_result.active_slot != result.active_slot
        or tuple(slot.counter for slot in after_result.slots)
        != tuple(slot.counter for slot in result.slots)
    ):
        raise MoneyFamilyError("slot/counter changed by editor")
    if out_key != key or out_money != target:
        raise MoneyFamilyError("output key/money mismatch")
    return candidate, before_money, diffs


def preview(
    raw: bytes,
    journal: dict,
    build_sha256: str,
    environment_id: str,
    target: int,
) -> MoneyPlan:
    _validate_target(target)
    found = inspect(raw, journal, build_sha256, environment_id)
    if not found["eligible"]:
        raise MoneyFamilyError(f"profile rejected: {found['reason']}")
    candidate, _, diffs = _derive(raw, target)
    return MoneyPlan(_sha(raw), target, _sha(candidate), diffs)


def audit_editor_output(source: bytes, output: bytes, plan: MoneyPlan) -> MoneyReceipt:
    if _sha(source) != plan.source_sha256 or _sha(output) != plan.output_sha256:
        raise MoneyFamilyError("source/output hash mismatch")
    expected, before_money, diffs = _derive(source, plan.target_money)
    if expected != output or diffs != plan.diffs:
        raise MoneyFamilyError("output does not match fresh bounded derivation")
    _, active = _active(output)
    _, after_money = _money(active)
    return MoneyReceipt(
        plan.source_sha256,
        plan.output_sha256,
        before_money,
        after_money,
        plan.target_money,
        diffs,
        True,
    )


def _copy_journal(journal: dict) -> dict:
    return json.loads(json.dumps(journal))


def _record_editor(journal: dict, source_sha: str, output: bytes, target: int) -> dict:
    updated = _copy_journal(journal)
    result, _ = _active(output)
    child = fingerprint(output, result)
    digest = child["sha256"]
    if digest in updated["nodes"]:
        if updated["nodes"][digest] != child:
            raise MoneyFamilyError("existing editor child fingerprint mismatch")
        return updated
    updated["nodes"][digest] = child
    updated["edges"].append(
        {
            "kind": "money-editor",
            "parent": source_sha,
            "child": digest,
            "target_money": target,
        }
    )
    validate_journal(updated)
    return updated


def commit(
    source_path: Path,
    destination_path: Path,
    journal_path: Path,
    rom_path: Path,
    environment_id: str,
    plan: MoneyPlan,
) -> MoneyReceipt:
    if sys.platform != "darwin":
        raise MoneyFamilyError(
            "M5A money FAMILY publication is enabled only on the evidenced macOS boundary"
        )
    _require_build_environment(rom_path, environment_id)
    journal = _read_journal(journal_path)
    raw = source_path.read_bytes()
    current = preview(
        raw, journal, EXPECTED_BUILD_SHA256, environment_id, plan.target_money
    )
    if current != plan:
        raise MoneyFamilyError("stale MoneyPlan")
    output, _, _ = _derive(raw, plan.target_money)
    receipt = audit_editor_output(raw, output, plan)
    updated = _record_editor(journal, plan.source_sha256, output, plan.target_money)
    try:
        published_sha = publication.publish_new(
            source_path,
            destination_path,
            plan.source_sha256,
            output,
            lambda candidate: audit_editor_output(raw, candidate, plan),
        )
    except publication.PublicationError as exc:
        raise MoneyFamilyError(str(exc)) from exc
    if published_sha != plan.output_sha256:
        raise MoneyFamilyError("published hash mismatch")
    # If journal publication fails, the verified output remains an unjournaled
    # recovery artifact and therefore is not eligible for FAMILY reuse.
    _write_journal(journal_path, updated)
    audit_editor_output(raw, destination_path.read_bytes(), plan)
    if _sha(source_path.read_bytes()) != plan.source_sha256:
        raise MoneyFamilyError("source changed after commit")
    return receipt


def check_game_return(
    parent: dict, candidate_raw: bytes, candidate: v.VerificationResult
) -> str | None:
    old_slot = parent["active_slot"]
    new_slot = candidate.active_slot
    if new_slot != 1 - old_slot:
        return "normal save did not switch slot"
    expected_counter = (parent["counter"] + 1) & 0xFFFFFFFF
    if candidate.slots[new_slot].counter != expected_counter:
        return "normal save counter is not next counter"
    if candidate.slots[old_slot].counter != parent["counter"]:
        return "previous slot counter changed"
    if _slot_hash(candidate_raw, old_slot) != parent["active_slot_sha256"]:
        return "previous slot bytes changed"
    try:
        current = fingerprint(candidate_raw, candidate)
    except MoneyFamilyError as exc:
        return str(exc)
    if current["key"] != OBSERVED_ENCRYPTION_KEY:
        return "encryption key left observed boundary"
    if current["money"] != parent["money"]:
        return "money changed across normal save"
    if (
        current["party_count"] != parent["party_count"]
        or current["party0_sha256"] != parent["party0_sha256"]
    ):
        return "party[0]/count changed outside M5A continuation envelope"
    if current["stable_payload_sha256"] != parent["stable_payload_sha256"]:
        return "game-save payload changed outside qualified M5A envelope"
    if current["stable_tail_sha256"] != parent["stable_tail_sha256"]:
        return "checksum-excluded tail changed outside qualified section-4 offsets"
    if current["play_time_seconds"] < parent["play_time_seconds"]:
        return "play time moved backwards"
    if current["saved_game_count"] != (
        (parent["saved_game_count"] + 1) & 0xFFFFFFFF
    ):
        return "saved-game statistic did not increment once"
    if current["sector28_31_sha256"] != parent["sector28_31_sha256"]:
        return "sectors 28-31 changed"
    expected_permutation = [
        (position + 1) % v.SLOT_SECTORS for position in parent["permutation"]
    ]
    if current["permutation"] != expected_permutation:
        return "unexpected section rotation"
    # Opaque emulator footer is deliberately not compared: it changed across
    # both independently observed normal game/emulator saves.
    return None


def record_game_return(
    candidate_path: Path,
    journal_path: Path,
    rom_path: Path,
    parent_sha256: str,
    environment_id: str,
    human_observed: bool,
) -> dict:
    if not human_observed:
        raise MoneyFamilyError("human game load/display/save observation required")
    _require_build_environment(rom_path, environment_id)
    journal = _read_journal(journal_path)
    parent = journal["nodes"].get(parent_sha256)
    if parent is None or not any(
        edge.get("kind") == "money-editor" and edge.get("child") == parent_sha256
        for edge in journal["edges"]
    ):
        raise MoneyFamilyError("parent is not a journaled money-editor output")
    raw = candidate_path.read_bytes()
    result, _ = _active(raw)
    reason = check_game_return(parent, raw, result)
    if reason:
        raise MoneyFamilyError(reason)
    updated = _copy_journal(journal)
    child = fingerprint(raw, result)
    if child["sha256"] in updated["nodes"]:
        raise MoneyFamilyError("game return already journaled")
    updated["nodes"][child["sha256"]] = child
    updated["edges"].append(
        {"kind": "game", "parent": parent_sha256, "child": child["sha256"]}
    )
    validate_journal(updated)
    _write_journal(journal_path, updated)
    return child


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    boot = sub.add_parser("bootstrap")
    boot.add_argument("root", type=Path)
    boot.add_argument("journal", type=Path)
    boot.add_argument("rom", type=Path)
    boot.add_argument("--environment", required=True)
    ins = sub.add_parser("inspect")
    ins.add_argument("save", type=Path)
    ins.add_argument("journal", type=Path)
    ins.add_argument("rom", type=Path)
    ins.add_argument("--environment", required=True)
    prev = sub.add_parser("preview")
    prev.add_argument("save", type=Path)
    prev.add_argument("journal", type=Path)
    prev.add_argument("rom", type=Path)
    prev.add_argument("target", type=int)
    prev.add_argument("--environment", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "bootstrap":
            value = bootstrap_journal(
                args.root, args.journal, args.rom, args.environment
            )
        else:
            _require_build_environment(args.rom, args.environment)
            journal = _read_journal(args.journal)
            raw = args.save.read_bytes()
            if args.action == "inspect":
                value = inspect(
                    raw, journal, EXPECTED_BUILD_SHA256, args.environment
                )
            else:
                value = asdict(
                    preview(
                        raw,
                        journal,
                        EXPECTED_BUILD_SHA256,
                        args.environment,
                        args.target,
                    )
                )
        print(json.dumps({"status": "OK", "result": value}, indent=2, sort_keys=True))
        return 0
    except (OSError, MoneyFamilyError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
