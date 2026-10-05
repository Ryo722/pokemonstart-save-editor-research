#!/usr/bin/env python3
"""Read-only M5A probe for the source-derived PokemonStart money hypothesis.

This module grants no writer authority. It uses the existing save verifier to
select the active logical sections, then reports the candidate FireRed/CFRU-JP
money decoding rule for read-only evidence collection.
"""
from __future__ import annotations

import argparse
import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path

import pokemonstart_save_verifier as verifier

MONEY_SECTION_ID = 1
MONEY_OFFSET = 0x0290
ENCRYPTION_KEY_SECTION_ID = 0
ENCRYPTION_KEY_OFFSET = 0x0F20
SOURCE_CANDIDATE_MAX_MONEY = 9_999_999


@dataclass(frozen=True)
class MoneyProbeResult:
    source_sha256: str
    active_slot: int
    counter: int
    stored_money_word: int
    encryption_key: int
    decoded_money: int
    source_candidate_max_money: int
    source_candidate_range_ok: bool


def probe_bytes(raw: bytes) -> MoneyProbeResult:
    """Decode the source-derived candidate money representation, read-only."""
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    if active.counter is None:
        raise verifier.VerificationError("active slot has no counter")

    key_section = active.section(ENCRYPTION_KEY_SECTION_ID).data
    money_section = active.section(MONEY_SECTION_ID).data
    encryption_key = struct.unpack_from("<I", key_section, ENCRYPTION_KEY_OFFSET)[0]
    stored_money_word = struct.unpack_from("<I", money_section, MONEY_OFFSET)[0]
    decoded_money = stored_money_word ^ encryption_key

    return MoneyProbeResult(
        source_sha256=result.file_sha256,
        active_slot=result.active_slot,
        counter=active.counter,
        stored_money_word=stored_money_word,
        encryption_key=encryption_key,
        decoded_money=decoded_money,
        source_candidate_max_money=SOURCE_CANDIDATE_MAX_MONEY,
        source_candidate_range_ok=0 <= decoded_money <= SOURCE_CANDIDATE_MAX_MONEY,
    )


def probe_path(path: str | Path) -> MoneyProbeResult:
    """Probe a file and verify that the read-only operation did not alter it."""
    path = Path(path)
    before = path.read_bytes()
    report = probe_bytes(before)
    after = path.read_bytes()
    if before != after:
        raise RuntimeError("input changed during read-only money probe")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only M5A source-derived money representation probe"
    )
    parser.add_argument("save", type=Path)
    args = parser.parse_args(argv)
    try:
        report = probe_path(args.save)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        return 2

    payload = asdict(report)
    payload["status"] = "SOURCE_HYPOTHESIS_ONLY"
    payload["warning"] = (
        "Decoded value is not writer authority; private PokemonStart differential "
        "evidence is still required."
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
