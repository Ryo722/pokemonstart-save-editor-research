#!/usr/bin/env python3
"""Unified practical local CLI for the bounded PokemonStart v0.22 Fast Lab profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pokemonstart_fl2_core as core


def _changes(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise core.FL2Error("--changes-json must be valid JSON") from exc
    if not isinstance(value, dict):
        raise core.FL2Error("--changes-json must decode to a JSON object")
    return value


def _add_rom(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rom", type=Path, default=core.ROM_DEFAULT,
                        help="exact v0.22 private ROM (defaults to the private workspace path)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    inspect = sub.add_parser("inspect", help="inspect exact profile and supported operations")
    inspect.add_argument("input_save", type=Path)
    _add_rom(inspect)

    preview = sub.add_parser("preview", help="preview one bounded supported edit without writing")
    preview.add_argument("input_save", type=Path)
    preview.add_argument("--operation", choices=core.OPERATIONS, required=True)
    preview.add_argument("--changes-json", required=True)
    _add_rom(preview)

    write = sub.add_parser("write", help="write one previewed edit to a new output path")
    write.add_argument("input_save", type=Path)
    write.add_argument("output_save", type=Path)
    write.add_argument("--operation", choices=core.OPERATIONS, required=True)
    write.add_argument("--changes-json", required=True)
    _add_rom(write)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            report = core.inspect_file(args.input_save, args.rom)
        else:
            changes = _changes(args.changes_json)
            if args.action == "preview":
                report = core.preview_file(args.input_save, args.rom, args.operation, changes)
            else:
                report = core.write_file(
                    args.input_save, args.output_save, args.rom, args.operation, changes)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
