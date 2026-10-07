"""Read-only E3 qualification CLI. Prints sanitized decoded state, never bytes.

Private paths must be under PokemonStart-private. Neither ROM nor save is
modified. An optional isolated exact-ROM probe lives in party_static_probe.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as model
import pokemonstart_v022_party_audit as auditor


def qualify(raw: bytes, rom: bytes) -> dict:
    report = model.inspect(raw, rom)
    independent = auditor.inspect(raw, rom)
    auditor.compare(report, independent)
    report['independent_reconstruction_equal'] = True
    report['gameplay_acceptance'] = False
    report['writer_gate'] = 'CLOSED: unresolved exceptional/contextual and transition policies'
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--save', type=Path, required=True)
    args = parser.parse_args()
    try:
        rom_path = profile._private_file(args.rom, 'ROM', must_exist=True)
        save_path = profile._private_file(args.save, 'save', must_exist=True)
        rom, raw = rom_path.read_bytes(), save_path.read_bytes()
        report = qualify(raw, rom)
        if model.sha(rom_path.read_bytes()) != model.sha(rom) or model.sha(save_path.read_bytes()) != model.sha(raw):
            raise ValueError('private source changed during read-only qualification')
        report['sources_immutable'] = True
    except (OSError, ValueError):
        print('REJECTED: read-only qualification unavailable or unsupported')
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
