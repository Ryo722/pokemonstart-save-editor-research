"""Bounded M4 inspection and lineage diagnostics.

Private write authority stays closed until a local ROM rehash, retained
transition audit, both markings directions and game canaries qualify it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import tempfile
from dataclasses import replace
from dataclasses import dataclass
from pathlib import Path

import pokemonstart_save_verifier as v
import pokemonstart_m4_publication as publication

ROOT_SHA256 = "ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86"
# Historical seals are regression vectors only. They are never consulted by
# inspect() to grant reusable capabilities.
EXACT_VECTOR_REGISTRY = {
    "m3c-markings-0-to-1": {
        "input_sha256": "6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600",
        "output_sha256": "9baa0be361f52a6bc4b2a5cc6611bb302196d24ad9de3107600adcdd8b572ff3",
    },
}
FAMILY_REGISTRY = {"party0-markings-0-1": "PROVEN: retained PokemonStart v0.15 root/build/environment; party[0] markings 0<->1"}
FAMILY_PROVEN = True
MARKINGS_OFFSET = 27
# Source-backed state with normal game-save transitions in the retained
# counter 5 -> 6, 6 -> 7, and 7 -> 8 corpus. Only these named fields are
# masked from stable payload hashes; all other payload bytes remain exact.
SAVE_BLOCK2_PLAY_TIME = range(0x0E, 0x13)  # hours, minutes, seconds, VBlanks
SAVE_BLOCK1_EVENT_OBJECTS_OFFSET = 0x6A0
EVENT_OBJECT_SIZE = 0x24
EVENT_OBJECT_COUNT = 16
# struct EventObject fields: first runtime-flag byte, current/previous map
# coordinates, direction nybbles, movement action, and previous direction.
EVENT_OBJECT_RUNTIME_FIELDS = ((0x00, 1), (0x10, 4), (0x14, 4),
                               (0x18, 1), (0x1C, 1), (0x20, 1))
SAVE_BLOCK1_SAVED_GAME_STAT_SECTION = 2
SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET = 0x210  # SaveBlock1 0x1200 - section1 0xFF0


def _volatile_payload_offsets(section_id: int) -> set[int]:
    if section_id == 0:
        return set(SAVE_BLOCK2_PLAY_TIME)
    if section_id == 1:
        return {SAVE_BLOCK1_EVENT_OBJECTS_OFFSET + index * EVENT_OBJECT_SIZE + field_offset + byte
                for index in range(EVENT_OBJECT_COUNT)
                for field_offset, size in EVENT_OBJECT_RUNTIME_FIELDS
                for byte in range(size)}
    if section_id == SAVE_BLOCK1_SAVED_GAME_STAT_SECTION:
        return set(range(SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET,
                         SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET + 4))
    return set()


class EligibilityError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class StructuralEligibility:
    eligible: bool
    reason: str
    result: v.VerificationResult | None


@dataclass(frozen=True)
class ProfileEligibility:
    eligible: bool
    reason: str
    lineage_hash: str | None


@dataclass(frozen=True)
class Capability:
    capability_id: str
    kind: str
    party_index: int
    before: int
    after: int


@dataclass(frozen=True)
class Inspection:
    source_sha256: str
    structural: StructuralEligibility
    profile: ProfileEligibility
    capabilities: tuple[Capability, ...]


@dataclass(frozen=True)
class MutationPlan:
    source_sha256: str
    capability: Capability
    output_sha256: str
    diffs: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class VerificationReceipt:
    source_sha256: str
    output_sha256: str
    capability_id: str
    diffs: tuple[tuple[int, int, int], ...]
    independently_verified: bool


def structural(raw: bytes) -> StructuralEligibility:
    try:
        result = v.verify_bytes(raw)
        active = result.slots[result.active_slot]
        if active.counter is None or result.active_slot != active.counter % 2:
            raise EligibilityError("active slot/counter parity mismatch")
        if not result.party:
            raise EligibilityError("party[0] is absent")
        # The verifier retains the original physical sector position of each
        # logical section; require a genuine 14-sector permutation here.
        physical = {section.physical_sector for section in active.sections}
        expected = set(range(result.active_slot * 14, (result.active_slot + 1) * 14))
        if physical != expected:
            raise EligibilityError("physical section permutation invalid")
        return StructuralEligibility(True, "S0 valid", result)
    except (v.VerificationError, EligibilityError) as exc:
        return StructuralEligibility(False, str(exc), None)


def _slot_hash(raw: bytes, slot: int) -> str:
    start = slot * v.SLOT_SECTORS * v.SECTOR_SIZE
    return sha(raw[start:start + v.SLOT_SECTORS * v.SECTOR_SIZE])


def _record_hash(raw: bytes, result: v.VerificationResult) -> str:
    physical = result.slots[result.active_slot].section(1).physical_sector
    start = physical * v.SECTOR_SIZE + v.PARTY_OFFSET
    return sha(raw[start:start + v.POKEMON_SIZE])


def _identity_hash(raw: bytes, result: v.VerificationResult) -> str:
    physical = result.slots[result.active_slot].section(1).physical_sector
    start = physical * v.SECTOR_SIZE + v.PARTY_OFFSET
    record = raw[start:start + v.POKEMON_SIZE]
    return sha(record[0:15] + record[20:27] + record[32:34])


def _sector_hash(raw: bytes, number: int) -> str:
    start = number * v.SECTOR_SIZE
    return sha(raw[start:start + v.SECTOR_SIZE])


def _tail_hashes(raw: bytes, result: v.VerificationResult) -> tuple[str, ...]:
    return tuple(sha(raw[s.physical_sector * v.SECTOR_SIZE + v.SECTION_LENGTHS[s.section_id]:
                         s.physical_sector * v.SECTOR_SIZE + v.SECTION_ID_OFFSET])
                 for s in result.slots[result.active_slot].sections)


def _stable_payload_hashes(result: v.VerificationResult) -> list[str]:
    active = result.slots[result.active_slot]
    hashes = []
    for section in active.sections:
        payload = bytearray(section.data[:v.SECTION_LENGTHS[section.section_id]])
        for offset in _volatile_payload_offsets(section.section_id):
            payload[offset] = 0
        hashes.append(sha(payload))
    return hashes


def _transition_metadata(result: v.VerificationResult) -> dict[str, int]:
    active = result.slots[result.active_slot]
    save_block2 = active.section(0).data
    hours = int.from_bytes(save_block2[0x0E:0x10], "little")
    minutes, seconds = save_block2[0x10], save_block2[0x11]
    if hours > 999 or minutes > 59 or seconds > 59:
        raise EligibilityError("invalid saved play-time fields")
    saved_game_count = int.from_bytes(
        active.section(SAVE_BLOCK1_SAVED_GAME_STAT_SECTION).data[
            SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET:SAVE_BLOCK1_SAVED_GAME_STAT_OFFSET + 4], "little")
    return {"play_time_seconds": hours * 3600 + minutes * 60 + seconds,
            "saved_game_count": saved_game_count}


def journal_fingerprint(raw: bytes, result: v.VerificationResult) -> dict:
    active = result.slots[result.active_slot]
    mon = result.party[0]
    return {
        "sha256": sha(raw), "active_slot": result.active_slot,
        "counter": active.counter, "active_slot_sha256": _slot_hash(raw, result.active_slot),
        "record0_sha256": _record_hash(raw, result),
        "identity_sha256": _identity_hash(raw, result), "species": mon.species,
        "party_count": result.party_count, "markings": mon.markings,
        "permutation": [s.physical_sector % v.SLOT_SECTORS for s in active.sections],
        "sector28_31_sha256": [_sector_hash(raw, i) for i in range(28, 32)],
        "active_payload_sha256": [sha(s.data[:v.SECTION_LENGTHS[s.section_id]]) for s in active.sections],
        "stable_payload_sha256": _stable_payload_hashes(result),
        **_transition_metadata(result),
        "active_tail_sha256": list(_tail_hashes(raw, result)),
        "footer_sha256": sha(result.footer),
    }


def load_journal(path: str | Path) -> dict:
    path = Path(path)
    if path.resolve().is_relative_to(Path(__file__).resolve().parent):
        raise EligibilityError("journal must be outside repository")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EligibilityError(f"missing or broken journal: {exc}") from exc
    validate_journal(data)
    return data


def validate_journal(data: dict) -> None:
    def is_hash(value) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None

    if not isinstance(data, dict) or set(data) != {"version", "root_sha256", "build_sha256",
                                                  "environment_id", "nodes", "edges"} or \
            data.get("version") != 4 or data.get("root_sha256") != ROOT_SHA256:
        raise EligibilityError("journal root/schema mismatch")
    if not is_hash(data.get("build_sha256")):
        raise EligibilityError("journal build binding missing")
    if not isinstance(data.get("environment_id"), str) or not 1 <= len(data["environment_id"]) <= 100:
        raise EligibilityError("journal environment binding missing")
    if not isinstance(data.get("nodes"), dict) or ROOT_SHA256 not in data["nodes"]:
        raise EligibilityError("journal root node missing")
    keys = {"sha256", "active_slot", "counter", "active_slot_sha256", "record0_sha256",
            "identity_sha256", "species", "party_count", "markings", "permutation", "sector28_31_sha256",
            "active_payload_sha256", "stable_payload_sha256", "play_time_seconds", "saved_game_count",
            "active_tail_sha256", "footer_sha256"}
    for key, node in data["nodes"].items():
        if not is_hash(key):
            raise EligibilityError("journal hash malformed")
        if not isinstance(node, dict) or set(node) != keys or node.get("sha256") != key:
            raise EligibilityError("journal node mismatch")
        if not isinstance(node["active_slot"], int) or node["active_slot"] not in (0, 1) or not isinstance(node["counter"], int) or not 0 <= node["counter"] <= 0xFFFFFFFF:
            raise EligibilityError("journal slot/counter malformed")
        if not all(is_hash(node[field]) for field in ("active_slot_sha256", "record0_sha256",
                                                       "identity_sha256", "footer_sha256")):
            raise EligibilityError("journal fingerprint hash malformed")
        if not isinstance(node["permutation"], list) or len(node["permutation"]) != 14 or \
                any(type(position) is not int for position in node["permutation"]) or \
                sorted(node["permutation"]) != list(range(14)):
            raise EligibilityError("journal permutation malformed")
        if not isinstance(node["species"], int) or not 0 <= node["species"] <= 0xFFFF:
            raise EligibilityError("journal species malformed")
        if not isinstance(node["party_count"], int) or not 1 <= node["party_count"] <= v.PARTY_SIZE or \
                not isinstance(node["markings"], int) or not 0 <= node["markings"] <= 0xFF:
            raise EligibilityError("journal party metadata malformed")
        if type(node["play_time_seconds"]) is not int or not 0 <= node["play_time_seconds"] <= 999 * 3600 + 59 * 60 + 59 or \
                type(node["saved_game_count"]) is not int or not 0 <= node["saved_game_count"] <= 0xFFFFFFFF:
            raise EligibilityError("journal game-transition metadata malformed")
        for field, length in (("sector28_31_sha256", 4), ("active_payload_sha256", 14),
                              ("stable_payload_sha256", 14),
                              ("active_tail_sha256", 14)):
            if not isinstance(node[field], list) or len(node[field]) != length or \
                    any(not is_hash(value) for value in node[field]):
                raise EligibilityError(f"journal {field} malformed")
    edges = data.get("edges")
    if not isinstance(edges, list):
        raise EligibilityError("journal edges missing")
    children = set()
    parents = {}
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("kind") not in ("editor", "game"):
            raise EligibilityError("journal edge malformed")
        expected = {"kind", "parent", "child", "capability"} if edge["kind"] == "editor" else {"kind", "parent", "child"}
        if set(edge) != expected or (edge["kind"] == "editor" and edge["capability"] not in ("markings-0-to-1", "markings-1-to-0")):
            raise EligibilityError("journal edge metadata malformed")
        parent, child = edge.get("parent"), edge.get("child")
        if parent not in data["nodes"] or child not in data["nodes"] or child == ROOT_SHA256 or child in children:
            raise EligibilityError("journal parent/child missing or duplicated")
        children.add(child)
        parents[child] = parent
    if children != set(data["nodes"]) - {ROOT_SHA256}:
        raise EligibilityError("journal node lacks parent edge")
    for node in children:
        seen = set()
        current = node
        while current != ROOT_SHA256:
            if current in seen or current not in parents:
                raise EligibilityError("journal lineage is not root-anchored")
            seen.add(current)
            current = parents[current]


def check_game_transition(parent: dict, candidate_raw: bytes,
                          candidate: v.VerificationResult) -> str | None:
    """Check a proposed B -> C normal save without enrolling its hash."""
    old_slot = parent["active_slot"]
    new_slot = candidate.active_slot
    if new_slot != 1 - old_slot:
        return "normal save did not switch to opposite slot"
    expected_counter = (parent["counter"] + 1) & 0xFFFFFFFF
    if candidate.slots[new_slot].counter != expected_counter:
        return "normal save counter is not next counter"
    if candidate.slots[old_slot].counter != parent["counter"]:
        return "previous slot counter changed"
    if _slot_hash(candidate_raw, old_slot) != parent["active_slot_sha256"]:
        return "previous slot bytes changed"
    try:
        current = journal_fingerprint(candidate_raw, candidate)
    except EligibilityError as exc:
        return str(exc)
    if current["identity_sha256"] != parent["identity_sha256"] or current["species"] != parent["species"] or current["party_count"] != parent["party_count"]:
        return "party identity/count changed"
    if current["record0_sha256"] != parent["record0_sha256"]:
        return "party[0] record changed outside editor edit"
    if current["stable_payload_sha256"] != parent["stable_payload_sha256"]:
        return "game-save payload changed outside qualified envelope"
    if current["play_time_seconds"] < parent["play_time_seconds"]:
        return "saved play time moved backwards"
    if current["saved_game_count"] != ((parent["saved_game_count"] + 1) & 0xFFFFFFFF):
        return "saved-game statistic did not increment once"
    if current["sector28_31_sha256"] != parent["sector28_31_sha256"]:
        return "sectors 28-31 changed"
    if current["active_tail_sha256"] != parent["active_tail_sha256"]:
        return "checksum-excluded tails changed"
    expected_permutation = [(position + 1) % v.SLOT_SECTORS for position in parent["permutation"]]
    if current["permutation"] != expected_permutation:
        return "unexpected section rotation"
    return None


def profile(raw: bytes, result: v.VerificationResult, journal: dict | None,
            build_sha256: str | None, environment_id: str | None) -> ProfileEligibility:
    if journal is None:
        return ProfileEligibility(False, "local private lineage journal missing", None)
    try:
        validate_journal(journal)
    except EligibilityError as exc:
        return ProfileEligibility(False, str(exc), None)
    if build_sha256 != journal["build_sha256"]:
        return ProfileEligibility(False, "selected ROM/build hash mismatch", None)
    if environment_id != journal["environment_id"]:
        return ProfileEligibility(False, "selected emulator environment mismatch", None)
    digest = result.file_sha256
    node = journal["nodes"].get(digest)
    if node is None:
        return ProfileEligibility(False, "unknown root or unobserved lineage descendant", None)
    if node != journal_fingerprint(raw, result):
        return ProfileEligibility(False, "journal fingerprint mismatch", None)
    if digest != ROOT_SHA256 and not any(edge.get("child") == digest for edge in journal.get("edges", [])):
        return ProfileEligibility(False, "missing parent edge", None)
    return ProfileEligibility(True, "journaled retained lineage", digest)


def inspect(raw: bytes, journal: dict | None = None,
            build_sha256: str | None = None, environment_id: str | None = None) -> Inspection:
    s0 = structural(raw)
    p = profile(raw, s0.result, journal, build_sha256, environment_id) if s0.eligible and s0.result else ProfileEligibility(False, "S0 failed", None)
    capabilities: tuple[Capability, ...] = ()
    if s0.eligible and p.eligible and FAMILY_PROVEN:
        marking = s0.result.party[0].markings
        if marking in (0, 1):
            capabilities = (Capability(f"markings-{marking}-to-{1-marking}", "FAMILY", 0, marking, 1-marking),)
    return Inspection(sha(raw), s0, p, capabilities)


def _derive_markings(raw: bytes, capability: Capability) -> tuple[bytes, MutationPlan]:
    if capability.kind != "FAMILY" or capability.party_index != 0 or (capability.before, capability.after) not in ((0, 1), (1, 0)):
        raise EligibilityError("unsupported capability request")
    before = structural(raw)
    if not before.eligible or before.result is None:
        raise EligibilityError(f"S0 failed: {before.reason}")
    result = before.result
    if result.party[0].markings != capability.before:
        raise EligibilityError("markings starting value mismatch")
    physical = result.slots[result.active_slot].section(1).physical_sector
    base = physical * v.SECTOR_SIZE
    mark_offset = base + v.PARTY_OFFSET + MARKINGS_OFFSET
    checksum_offset = base + v.SECTION_CHECKSUM_OFFSET
    out = bytearray(raw)
    if out[mark_offset] != capability.before:
        raise EligibilityError("raw markings byte mismatch")
    out[mark_offset] = capability.after
    checksum = v.calculate_save_checksum(bytes(out[base:base + v.SECTION_LENGTHS[1]]))
    struct.pack_into("<H", out, checksum_offset, checksum)
    output = bytes(out)
    diffs = tuple((i, old, new) for i, (old, new) in enumerate(zip(raw, output)) if old != new)
    plan = MutationPlan(sha(raw), capability, sha(output), diffs)
    audit_output(raw, output, plan)
    return output, plan


def audit_output(source: bytes, output: bytes, plan: MutationPlan) -> VerificationReceipt:
    """Independent byte/semantic audit; never trusts the writer's diff alone."""
    if len(source) != len(output) or sha(source) != plan.source_sha256 or sha(output) != plan.output_sha256:
        raise EligibilityError("source/output hash or length mismatch")
    before, after = v.verify_bytes(source), v.verify_bytes(output)
    if before.active_slot != after.active_slot or tuple(s.counter for s in before.slots) != tuple(s.counter for s in after.slots):
        raise EligibilityError("slot or counter changed")
    old_sections = tuple(tuple((s.section_id, s.physical_sector, s.signature) for s in slot.sections) for slot in before.slots)
    new_sections = tuple(tuple((s.section_id, s.physical_sector, s.signature) for s in slot.sections) for slot in after.slots)
    if old_sections != new_sections:
        raise EligibilityError("section permutation/metadata changed")
    if before.party_count != after.party_count or after.party[0] != replace(before.party[0], markings=plan.capability.after):
        raise EligibilityError("party semantics changed outside markings")
    if before.party[0].markings != plan.capability.before:
        raise EligibilityError("markings starting value mismatch")
    if before.footer != after.footer:
        raise EligibilityError("footer changed")
    physical = before.slots[before.active_slot].section(1).physical_sector
    base = physical * v.SECTOR_SIZE
    allowed = {base + v.PARTY_OFFSET + MARKINGS_OFFSET, base + v.SECTION_CHECKSUM_OFFSET,
               base + v.SECTION_CHECKSUM_OFFSET + 1}
    diffs = tuple((i, old, new) for i, (old, new) in enumerate(zip(source, output)) if old != new)
    if diffs != plan.diffs or not diffs or any(i not in allowed for i, _, _ in diffs):
        raise EligibilityError("unexplained byte diff")
    if output[base + v.PARTY_OFFSET + MARKINGS_OFFSET] != plan.capability.after:
        raise EligibilityError("markings byte mismatch")
    return VerificationReceipt(plan.source_sha256, plan.output_sha256,
                               plan.capability.capability_id, diffs, True)


def preview(raw: bytes, journal: dict, build_sha256: str, environment_id: str,
            capability_id: str) -> MutationPlan:
    found = inspect(raw, journal, build_sha256, environment_id)
    for capability in found.capabilities:
        if capability.capability_id == capability_id:
            return _derive_markings(raw, capability)[1]
    raise EligibilityError("requested capability is not PROVEN and available")


def _write_journal(path: Path, journal: dict) -> None:
    validate_journal(journal)
    if path.resolve().is_relative_to(Path(__file__).resolve().parent):
        raise EligibilityError("journal must be outside repository")
    encoded = (json.dumps(journal, sort_keys=True, indent=2) + "\n").encode()
    fd, name = tempfile.mkstemp(prefix=".pokemonstart-journal-", dir=path.parent)
    staged = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staged, path)
    finally:
        if staged.exists():
            staged.unlink()


def enroll_root(raw: bytes, rom: bytes, journal_path: str | Path, environment_id: str) -> dict:
    """Enroll only the canonical observed root; this does not prove FAMILY."""
    if sha(raw) != ROOT_SHA256:
        raise EligibilityError("unknown root hash")
    s0 = structural(raw)
    if not s0.eligible or s0.result is None:
        raise EligibilityError(f"root S0 failed: {s0.reason}")
    path = Path(journal_path)
    if path.exists():
        raise EligibilityError("journal already exists")
    if not 1 <= len(environment_id) <= 100:
        raise EligibilityError("environment ID must be 1-100 characters")
    journal = {"version": 4, "root_sha256": ROOT_SHA256, "build_sha256": sha(rom),
               "environment_id": environment_id,
               "nodes": {ROOT_SHA256: journal_fingerprint(raw, s0.result)}, "edges": []}
    validate_journal(journal)
    if path.resolve().is_relative_to(Path(__file__).resolve().parent):
        raise EligibilityError("journal must be outside repository")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(journal, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return journal


def _verified_candidate(raw: bytes, journal: dict, build_hash: str,
                        environment_id: str, plan: MutationPlan) -> tuple[bytes, VerificationReceipt]:
    if sha(raw) != plan.source_sha256:
        raise EligibilityError("stale MutationPlan: source hash changed")
    current_plan = preview(raw, journal, build_hash, environment_id, plan.capability.capability_id)
    if current_plan != plan:
        raise EligibilityError("stale MutationPlan: preview changed")
    output, _ = _derive_markings(raw, plan.capability)
    receipt = audit_output(raw, output, plan)
    return output, receipt


def _record_editor_output(journal: dict, output: bytes, receipt: VerificationReceipt,
                          plan: MutationPlan) -> None:
    if receipt.output_sha256 in journal["nodes"]:
        raise EligibilityError("output candidate is already journaled")
    after = v.verify_bytes(output)
    journal["nodes"][receipt.output_sha256] = journal_fingerprint(output, after)
    journal.setdefault("edges", []).append({"kind": "editor", "parent": receipt.source_sha256,
                                             "child": receipt.output_sha256,
                                             "capability": plan.capability.capability_id})


def commit_download(source_raw: bytes, journal_path: str | Path, rom_path: str | Path,
                    environment_id: str, plan: MutationPlan) -> tuple[bytes, VerificationReceipt]:
    """Create and journal a verified in-memory candidate for browser download."""
    journal = load_journal(journal_path)
    build_hash = sha(Path(rom_path).read_bytes())
    output, receipt = _verified_candidate(source_raw, journal, build_hash, environment_id, plan)
    # Re-audit immediately before journal enrollment and returning bytes to UI.
    audit_output(source_raw, output, plan)
    _record_editor_output(journal, output, receipt, plan)
    _write_journal(Path(journal_path), journal)
    return output, receipt


def commit(source_path: str | Path, destination_path: str | Path, journal_path: str | Path,
           rom_path: str | Path, environment_id: str, plan: MutationPlan) -> VerificationReceipt:
    journal = load_journal(journal_path)
    build_hash = sha(Path(rom_path).read_bytes())
    raw = Path(source_path).read_bytes()
    output, receipt = _verified_candidate(raw, journal, build_hash, environment_id, plan)
    published_sha = publication.publish_new(source_path, destination_path, plan.source_sha256,
        output, lambda candidate: audit_output(raw, candidate, plan))
    if published_sha != receipt.output_sha256:
        raise EligibilityError("published hash mismatch")
    _record_editor_output(journal, output, receipt, plan)
    _write_journal(Path(journal_path), journal)
    return receipt


def prepare_root_canary(source_path: str | Path, destination_path: str | Path,
                        journal_path: str | Path, rom_path: str | Path,
                        environment_id: str) -> VerificationReceipt:
    """Seal one exact-root 1 -> 0 proof B; never grant reusable FAMILY access."""
    raw = Path(source_path).read_bytes()
    if sha(raw) != ROOT_SHA256:
        raise EligibilityError("canary source is not the observed root")
    journal = load_journal(journal_path)
    build_hash = sha(Path(rom_path).read_bytes())
    found = inspect(raw, journal, build_hash, environment_id)
    if not found.structural.eligible or not found.profile.eligible:
        raise EligibilityError(f"root canary S0/P failed: {found.structural.reason}; {found.profile.reason}")
    if found.structural.result.party[0].markings != 1:
        raise EligibilityError("root canary starting marking is not 1")
    if len(journal["nodes"]) != 1 or journal["edges"]:
        raise EligibilityError("root canary already prepared")
    capability = Capability("markings-1-to-0", "FAMILY", 0, 1, 0)
    output, plan = _derive_markings(raw, capability)
    receipt = audit_output(raw, output, plan)
    published_sha = publication.publish_new(source_path, destination_path, plan.source_sha256,
        output, lambda candidate: audit_output(raw, candidate, plan))
    if published_sha != receipt.output_sha256:
        raise EligibilityError("published canary hash mismatch")
    journal["nodes"][published_sha] = journal_fingerprint(output, v.verify_bytes(output))
    journal["edges"].append({"kind": "editor", "parent": plan.source_sha256,
                             "child": published_sha, "capability": capability.capability_id})
    _write_journal(Path(journal_path), journal)
    return receipt


def prepare_return_canary(source_path: str | Path, destination_path: str | Path,
                          journal_path: str | Path, rom_path: str | Path,
                          environment_id: str) -> VerificationReceipt:
    """Seal 0 -> 1 proof D only after the journaled B -> C game return."""
    raw = Path(source_path).read_bytes()
    journal = load_journal(journal_path)
    found = inspect(raw, journal, sha(Path(rom_path).read_bytes()), environment_id)
    if not found.structural.eligible or not found.profile.eligible:
        raise EligibilityError(f"return canary S0/P failed: {found.structural.reason}; {found.profile.reason}")
    if found.structural.result.party[0].markings != 0:
        raise EligibilityError("return canary starting marking is not 0")
    if len(journal["nodes"]) != 3 or len(journal["edges"]) != 2:
        raise EligibilityError("return canary lineage is incomplete or already used")
    editor, game = journal["edges"]
    if (editor.get("kind"), editor.get("parent"), editor.get("capability")) != \
            ("editor", ROOT_SHA256, "markings-1-to-0") or \
            (game.get("kind"), game.get("parent"), game.get("child")) != \
            ("game", editor.get("child"), sha(raw)):
        raise EligibilityError("return canary is not the observed B -> C descendant")
    capability = Capability("markings-0-to-1", "FAMILY", 0, 0, 1)
    output, plan = _derive_markings(raw, capability)
    receipt = audit_output(raw, output, plan)
    published_sha = publication.publish_new(source_path, destination_path, plan.source_sha256,
        output, lambda candidate: audit_output(raw, candidate, plan))
    if published_sha != receipt.output_sha256:
        raise EligibilityError("published return canary hash mismatch")
    journal["nodes"][published_sha] = journal_fingerprint(output, v.verify_bytes(output))
    journal["edges"].append({"kind": "editor", "parent": plan.source_sha256,
                             "child": published_sha, "capability": capability.capability_id})
    _write_journal(Path(journal_path), journal)
    return receipt


def record_observed_game_return(candidate_path: str | Path, journal_path: str | Path,
                                rom_path: str | Path, parent_sha256: str,
                                environment_id: str, human_observed: bool) -> dict:
    """Journal a checked B -> C return after a human reports an actual save."""
    if not human_observed:
        raise EligibilityError("actual game load and normal save observation required")
    journal = load_journal(journal_path)
    if sha(Path(rom_path).read_bytes()) != journal["build_sha256"]:
        raise EligibilityError("selected ROM/build hash mismatch")
    if environment_id != journal["environment_id"]:
        raise EligibilityError("selected emulator environment mismatch")
    parent = journal["nodes"].get(parent_sha256)
    if parent is None or not any(edge.get("kind") == "editor" and edge.get("child") == parent_sha256
                                 for edge in journal["edges"]):
        raise EligibilityError("missing journaled editor-output parent")
    raw = Path(candidate_path).read_bytes()
    s0 = structural(raw)
    if not s0.eligible or s0.result is None:
        raise EligibilityError(f"C S0 failed: {s0.reason}")
    reason = check_game_transition(parent, raw, s0.result)
    if reason:
        raise EligibilityError(reason)
    child = journal_fingerprint(raw, s0.result)
    if child["sha256"] in journal["nodes"]:
        raise EligibilityError("candidate already journaled")
    journal["nodes"][child["sha256"]] = child
    journal["edges"].append({"kind": "game", "parent": parent_sha256, "child": child["sha256"]})
    _write_journal(Path(journal_path), journal)
    return child
