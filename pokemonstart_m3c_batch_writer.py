#!/usr/bin/env python3
"""M3C goal-driven low-coupling batch writer for retained PokemonStart v0.15 lineage.

This profile-bound candidate generates three individual variants and one combined
canary from the exact M3C-F1 round-trip save: friendship 51->52, markings
0->1, and ball 3->11 (Premier Ball).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

import pokemonstart_save_verifier as v

EXPECTED_INPUT_SHA256 = "6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600"
EXPECTED_ACTIVE_SLOT = 0
EXPECTED_ACTIVE_COUNTER = 4
EXPECTED_INACTIVE_COUNTER = 3
TARGET_PARTY_INDEX = 0
EXPECTED_PARTY_SPECIES = 1
EXPECTED_PARTY_LEVEL = 5
EXPECTED_PARTY_EXP = 134
EXPECTED_PARTY_MOVES = (33, 45, 0, 0)
EXPECTED_PARTY_PP = (35, 40, 0, 0)
EXPECTED_PARTY_EVS = (0, 0, 0, 0, 0, 0)
EXPECTED_PARTY_IVS = (31, 29, 26, 23, 27, 29)
EXPECTED_PARTY_HP = (21, 21)
EXPECTED_PARTY_STATS = (9, 11, 10, 13, 12)
EXPECTED_SECTOR30_SHA256 = "335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525"
EXPECTED_SECTOR31_SHA256 = "ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7"
EXPECTED_FOOTER_SHA256 = "8ef79aef38d8658aa715ea718edef3246c6af1fc3147990a4f3b3209ae585c69"

MARKINGS_OFFSET = 27
FRIENDSHIP_OFFSET = 41
BALL_OFFSET = 42

@dataclass(frozen=True)
class FieldCapability:
    name: str
    record_offset: int
    old_value: int
    new_value: int
    risk_class: str

CAPABILITIES = {
    "friendship": FieldCapability("friendship", FRIENDSHIP_OFFSET, 51, 52, "L"),
    "markings": FieldCapability("markings", MARKINGS_OFFSET, 0, 1, "L"),
    "ball": FieldCapability("ball", BALL_OFFSET, 3, 11, "L"),
}

EXPECTED_SEALS = {
    ("friendship",): {
        "output_sha256": "75e3c7f1afcdd49d6c3678ae729e308b98563ec39ad666e43a07b7b2e85c0e07",
        "diffs": ((0x5061, 0x33, 0x34), (0x5FF7, 0x1D, 0x1E)),
    },
    ("markings",): {
        "output_sha256": "9baa0be361f52a6bc4b2a5cc6611bb302196d24ad9de3107600adcdd8b572ff3",
        "diffs": ((0x5053, 0x00, 0x01), (0x5FF7, 0x1D, 0x1E)),
    },
    ("ball",): {
        "output_sha256": "be1c4ff04c1c5ab50672b492353d3de14609a40bf898293955d9b2f036103dfb",
        "diffs": ((0x5062, 0x03, 0x0B), (0x5FF6, 0x11, 0x19)),
    },
    ("ball", "friendship", "markings"): {
        "output_sha256": "65820082d6ced2ad3081e24b27884b6f6f29b5a321b49aecc057995f24ad58bd",
        "diffs": (
            (0x5053, 0x00, 0x01),
            (0x5061, 0x33, 0x34),
            (0x5062, 0x03, 0x0B),
            (0x5FF6, 0x11, 0x19),
            (0x5FF7, 0x1D, 0x1F),
        ),
    },
}

class WriterError(ValueError):
    pass

@dataclass(frozen=True)
class CandidateFingerprint:
    input_sha256: str
    output_sha256: str
    active_slot: int
    active_counter: int
    section1_physical_sector: int
    selected_fields: tuple[str, ...]
    semantic_changes: tuple[tuple[str, int, int], ...]
    diffs: tuple[tuple[int, int, int], ...]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _diffs(a: bytes, b: bytes) -> tuple[tuple[int, int, int], ...]:
    if len(a) != len(b):
        raise WriterError("output length changed")
    return tuple((i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y)


def _section_map(slot: v.SlotInfo):
    return tuple((s.section_id, s.physical_sector, s.counter, s.signature) for s in slot.sections)


def _normalize_fields(fields: Iterable[str]) -> tuple[str, ...]:
    names = tuple(sorted(set(fields)))
    if not names:
        raise WriterError("at least one field is required")
    unknown = [name for name in names if name not in CAPABILITIES]
    if unknown:
        raise WriterError(f"unsupported batch field(s): {', '.join(unknown)}")
    if names not in EXPECTED_SEALS:
        raise WriterError(f"field combination is not sealed: {names!r}")
    return names


def _check_input_profile(before: v.VerificationResult) -> None:
    if before.active_slot != EXPECTED_ACTIVE_SLOT:
        raise WriterError(f"active slot {before.active_slot}, expected {EXPECTED_ACTIVE_SLOT}")
    s0, s1 = before.slots
    if s0.state != "valid" or s1.state != "valid":
        raise WriterError("batch input requires both save slots valid")
    active = before.slots[before.active_slot]
    inactive = before.slots[1 - before.active_slot]
    if active.counter != EXPECTED_ACTIVE_COUNTER:
        raise WriterError(f"active counter {active.counter}, expected {EXPECTED_ACTIVE_COUNTER}")
    if inactive.counter != EXPECTED_INACTIVE_COUNTER:
        raise WriterError(f"inactive counter {inactive.counter}, expected {EXPECTED_INACTIVE_COUNTER}")
    if active.counter is None or before.active_slot != active.counter % 2:
        raise WriterError("active slot/counter parity mismatch")
    if before.party_count <= TARGET_PARTY_INDEX:
        raise WriterError("party[0] is not present")
    mon = before.party[TARGET_PARTY_INDEX]
    expected = (
        EXPECTED_PARTY_SPECIES, EXPECTED_PARTY_LEVEL, EXPECTED_PARTY_EXP,
        51, 0, 3, EXPECTED_PARTY_MOVES, EXPECTED_PARTY_PP,
        EXPECTED_PARTY_EVS, EXPECTED_PARTY_IVS, EXPECTED_PARTY_HP,
        EXPECTED_PARTY_STATS,
    )
    actual = (
        mon.species, mon.level, mon.experience, mon.friendship, mon.markings,
        mon.ball, mon.moves, mon.pp, mon.evs, mon.ivs,
        (mon.hp, mon.max_hp),
        (mon.attack, mon.defense, mon.speed, mon.sp_attack, mon.sp_defense),
    )
    if actual != expected:
        raise WriterError("party[0] profile mismatch")
    if _sha(before.sector30) != EXPECTED_SECTOR30_SHA256:
        raise WriterError("sector 30 profile mismatch")
    if _sha(before.sector31) != EXPECTED_SECTOR31_SHA256:
        raise WriterError("sector 31 profile mismatch")
    if len(before.footer) != v.RTC_FOOTER_SIZE or _sha(before.footer) != EXPECTED_FOOTER_SHA256:
        raise WriterError("opaque footer profile mismatch")


def derive_candidate(raw: bytes, fields: Iterable[str]):
    names = _normalize_fields(fields)
    input_sha = _sha(raw)
    if input_sha != EXPECTED_INPUT_SHA256:
        raise WriterError(f"unsupported batch input sha256 {input_sha}")
    before = v.verify_bytes(raw)
    _check_input_profile(before)
    section1 = before.slots[before.active_slot].section(1)
    base = section1.physical_sector * v.SECTOR_SIZE
    record_base = base + v.PARTY_OFFSET + TARGET_PARTY_INDEX * v.POKEMON_SIZE
    checksum_offset = base + v.SECTION_CHECKSUM_OFFSET
    out = bytearray(raw)
    semantic_changes = []
    allowed_offsets = {checksum_offset, checksum_offset + 1}
    for name in names:
        cap = CAPABILITIES[name]
        absolute = record_base + cap.record_offset
        if out[absolute] != cap.old_value:
            raise WriterError(f"party[0] {name} raw byte is {out[absolute]}, expected {cap.old_value}")
        out[absolute] = cap.new_value
        allowed_offsets.add(absolute)
        semantic_changes.append((name, cap.old_value, cap.new_value))
    payload = bytes(out[base : base + v.SECTION_LENGTHS[1]])
    struct.pack_into("<H", out, checksum_offset, v.calculate_save_checksum(payload))
    output = bytes(out)
    diffs = _diffs(raw, output)
    if not diffs or any(i not in allowed_offsets for i, _, _ in diffs):
        raise WriterError("candidate diff escaped field/checksum envelope")
    after = v.verify_bytes(output)
    if after.active_slot != before.active_slot:
        raise WriterError("active slot changed")
    if tuple(s.counter for s in after.slots) != tuple(s.counter for s in before.slots):
        raise WriterError("slot counter changed")
    if tuple(_section_map(s) for s in after.slots) != tuple(_section_map(s) for s in before.slots):
        raise WriterError("section metadata/permutation changed")
    if after.party_count != before.party_count:
        raise WriterError("party count changed")
    changes = {name: CAPABILITIES[name].new_value for name in names}
    if after.party[0] != replace(before.party[0], **changes):
        raise WriterError("party record invariant failed")
    if after.footer != before.footer:
        raise WriterError("opaque footer changed")
    if after.sector30 != before.sector30 or after.sector31 != before.sector31:
        raise WriterError("sector 30/31 changed")
    return output, CandidateFingerprint(
        input_sha, _sha(output), before.active_slot, EXPECTED_ACTIVE_COUNTER,
        section1.physical_sector, names, tuple(semantic_changes), diffs,
    )


def require_sealed(fp: CandidateFingerprint) -> None:
    seal = EXPECTED_SEALS[fp.selected_fields]
    if fp.diffs != seal["diffs"]:
        raise WriterError(f"non-allowlisted batch diff: {fp.diffs!r}")
    if fp.output_sha256 != seal["output_sha256"]:
        raise WriterError(f"unexpected batch output sha256 {fp.output_sha256}")


def build_output(raw: bytes, fields: Iterable[str]):
    output, fp = derive_candidate(raw, fields)
    require_sealed(fp)
    return output, fp


def write_output(input_path: str | Path, output_path: str | Path, fields: Iterable[str]):
    source = Path(input_path)
    dest = Path(output_path)
    if source.resolve() == dest.resolve():
        raise WriterError("refusing to overwrite the input save")
    if dest.exists():
        raise WriterError("refusing to overwrite an existing output path")
    raw = source.read_bytes()
    output, fp = build_output(raw, fields)
    created = False
    try:
        with dest.open("xb") as h:
            created = True
            h.write(output)
            h.flush()
            os.fsync(h.fileno())
        if dest.read_bytes() != output:
            raise WriterError("written output does not match verified bytes")
        if _sha(source.read_bytes()) != fp.input_sha256:
            raise WriterError("input changed during batch write")
    except Exception:
        if created:
            try:
                dest.unlink()
            except OSError:
                pass
        raise
    return fp


def format_fingerprint(fp: CandidateFingerprint) -> str:
    lines = [
        "status: DERIVED",
        f"input_sha256: {fp.input_sha256}",
        f"output_sha256: {fp.output_sha256}",
        f"active_slot: {fp.active_slot}",
        f"active_counter: {fp.active_counter}",
        f"section1_physical_sector: {fp.section1_physical_sector}",
        f"fields: {','.join(fp.selected_fields)}",
    ]
    lines += [f"semantic: party[0].{n} {a}->{b}" for n, a, b in fp.semantic_changes]
    lines += [f"diff: 0x{i:X} {a:02X}->{b:02X}" for i, a, b in fp.diffs]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="M3C low-coupling sealed batch writer")
    p.add_argument("input")
    p.add_argument("--fields", required=True, help="comma-separated sealed field set")
    p.add_argument("--derive-only", action="store_true")
    p.add_argument("--output")
    a = p.parse_args(argv)
    fields = tuple(x.strip() for x in a.fields.split(",") if x.strip())
    try:
        raw = Path(a.input).read_bytes()
        if a.derive_only:
            _, fp = build_output(raw, fields)
            print(format_fingerprint(fp))
            return 0
        if not a.output:
            raise WriterError("--output is required unless --derive-only is used")
        fp = write_output(a.input, a.output, fields)
    except (OSError, v.VerificationError, WriterError) as e:
        print("status: REJECTED")
        print(f"reason: {e}")
        return 2
    print("status: WRITTEN")
    print(format_fingerprint(fp))
    return 0

if __name__ == "__main__":
    sys.exit(main())
