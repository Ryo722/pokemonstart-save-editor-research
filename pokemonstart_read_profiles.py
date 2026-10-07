#!/usr/bin/env python3
"""Exact-build READ profiles binding build identity, save-layout family and
ROM-semantic table verification. Read-only; no profile grants write authority.

Capability levels are kept separate on purpose:

1. ``layout_read``          -- the save structure is understood for reading;
2. ``field_read``           -- field locations/semantic reads are qualified;
3. ``write_mechanics``      -- never granted here.

The semantic model is identified by build-independent table content hashes;
each build profile only supplies its own ROM offsets, which must reproduce
those hashes before any semantic read is trusted.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import struct
import sys

import pokemonstart_save_layouts as layouts

ITEM_COUNT, ITEM_SIZE, ITEM_POINTER_FIELDS = 839, 40, (16, 24, 32)


@dataclass(frozen=True)
class SemanticTable:
    name: str
    size: int
    sha256: str
    normalization: str = "raw"


# Content identity of the exact-v0.22 E1/E3 tables (canonical evidence records
# e1-inventory-private-evidence.json and e3-existing-party-readonly-evidence.json).
SEMANTIC_MODEL_ID = "pokemonstart-cfru-jp-e1e3-tables/1"
SEMANTIC_TABLES = (
    SemanticTable("species", 1489 * 32, "f7ce80669fd5ada0b3ed2a847eea472712df7a83fda5db5e0e298de2ddae3fea"),
    SemanticTable("species_names", 1489 * 8, "527602d9a5679e2a21474d38f97bc91563029c0772f06374c9f6da2848a53a06"),
    SemanticTable("moves", 998 * 12, "d23799854048201ee34ebbb38d8a15b423badbfb574029b8f2663785cb1f1471"),
    SemanticTable("move_names", 998 * 16, "84b116b6f7a155b865b2665e108bc38f10a52eb1160e622a0145058ac67bbace"),
    SemanticTable("experience", 6 * 1024, "290cf4597a284b268b9f1f3cb6250d044d54ebbf51390a5f43e3f1c5419452c5"),
    SemanticTable("nature", 125, "1c7d07b7ce4be855b42c3dd74c42d7a2ab7acc22fac4c43837e4d0fd32afcb0c"),
    SemanticTable("pocket_descriptor", 40, "ae47094540732997b5a4dd462b4cbbbac0cfca84f1f2bdcfdc7580c14ad61e38"),
    # Item records carry build-specific ROM pointers at +16/+24/+32; identity
    # is defined with each pointer replaced by its null/non-null flag.
    SemanticTable("items", ITEM_COUNT * ITEM_SIZE,
                  "b4dbebb54aca935a9f3e54654b6b6204727f00743eb993081d10c79cc3822365", "item_pointer_flags"),
)

# Inventory pockets: (name, RAM base, capacity). Covered by pocket_descriptor.
POCKETS = (("regular", 0x0203BA98, 700), ("key", 0x0203C588, 75), ("balls", 0x0203C6D4, 50),
           ("tmhm", 0x0203C79C, 128), ("berries", 0x0203C99C, 72))
MENU_COUNTS_RAM = 0x0203C6C2
ALTERNATE_BAG_RAM = 0x0203B672


@dataclass(frozen=True)
class BuildReadProfile:
    profile_id: str
    build: str
    rom_sha256: str
    rom_size: int
    layout: str
    table_offsets: dict[str, int]
    header_pointers: dict[str, tuple[int, str]]
    capabilities: dict[str, str]
    require_slot_parity: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)


V022_EXACT = BuildReadProfile(
    profile_id="pokemonstart-v0.22-exact-read",
    build="PokemonStart v0.22 (ddd054d)",
    rom_sha256="6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0",
    rom_size=0x2000000,
    layout=layouts.LEGACY,
    table_offsets={"species": 0x19B8B40, "species_names": 0x16570A4, "moves": 0x14A3238,
                   "move_names": 0x111A74C, "experience": 0x14C5D54, "nature": 0x20F550,
                   "pocket_descriptor": 0x1490E68, "items": 0x15199C8},
    header_pointers={"species": (0x1BC, "species"), "items": (0x1C8, "items")},
    capabilities={"layout_read": "CANONICAL", "field_read": "CANONICAL (existing v0.22 modules)",
                  "write_mechanics": "CANONICAL ONLY VIA EXISTING v0.22 WRITERS; NOT GRANTED BY THIS PROFILE"},
    require_slot_parity=False,
    notes=("descriptive mirror of canonical exact-v0.22 constants; canonical modules are unchanged",),
)

V027_EXACT = BuildReadProfile(
    profile_id="pokemonstart-v0.27-exact-read",
    build="PokemonStart v0.27 (23007d4), 64 MiB",
    rom_sha256="455f5294af9cb728ea577cafea3f8a27d5efc18e8f1371e1a76492e79d3781ac",
    rom_size=0x4000000,
    layout=layouts.V023PLUS,
    table_offsets={"species": 0x17D8F74, "species_names": 0x16570D4, "moves": 0x141A840,
                   "move_names": 0x111D9A4, "experience": 0x143D35C, "nature": 0x20F550,
                   "pocket_descriptor": 0x1408400, "items": 0x1490FD0},
    header_pointers={"species": (0x1BC, "species"), "items": (0x1C8, "items")},
    capabilities={"layout_read": "PRIVATELY_RUNTIME_QUALIFIED (S0->M->R1->R2 gate)",
                  "field_read": "QUALIFIED: Party raw records, key0 Money, Inventory pocket entries/menu counts; "
                                "semantic tables content-verified (code-path equivalence not reproduced here)",
                  "write_mechanics": "NOT QUALIFIED"},
    notes=("one migrated save; empty Boxes; one copy-on-write relocation observed",
           "spare-sector selection/reuse, populated Box pages and three first-save parasite bytes unresolved"),
)

PROFILES = {"v022": V022_EXACT, "v027": V027_EXACT}


class ProfileError(ValueError):
    """Raised when a ROM or save does not satisfy an exact read profile."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize(table: SemanticTable, blob: bytes) -> bytes:
    if table.normalization == "raw":
        return blob
    data = bytearray(blob)
    for index in range(ITEM_COUNT):
        for offset in ITEM_POINTER_FIELDS:
            at = index * ITEM_SIZE + offset
            struct.pack_into("<I", data, at, 0 if struct.unpack_from("<I", data, at)[0] == 0 else 1)
    return bytes(data)


def verify_rom(profile: BuildReadProfile, rom: bytes) -> dict:
    """Bind a ROM to the profile: size, SHA-256, header pointers and every table hash."""
    if len(rom) != profile.rom_size:
        raise ProfileError("ROM size does not match the profile")
    if _sha(rom) != profile.rom_sha256:
        raise ProfileError("ROM SHA-256 does not match the profile")
    for name, (pointer, table) in profile.header_pointers.items():
        if struct.unpack_from("<I", rom, pointer)[0] != 0x08000000 + profile.table_offsets[table]:
            raise ProfileError(f"header pointer for {name} does not match the profile")
    tables = {}
    for table in SEMANTIC_TABLES:
        start = profile.table_offsets[table.name]
        digest = _sha(_normalize(table, rom[start:start + table.size]))
        if digest != table.sha256:
            raise ProfileError(f"semantic table {table.name} content differs from {SEMANTIC_MODEL_ID}")
        tables[table.name] = {"offset": f"0x{start:07X}", "size": table.size, "sha256": digest,
                              "normalization": table.normalization}
    return {"profile": profile.profile_id, "rom_sha256": profile.rom_sha256,
            "semantic_model": SEMANTIC_MODEL_ID, "tables": tables}


def _pockets(view: layouts.SaveView) -> list[dict]:
    pockets = []
    for name, base, capacity in POCKETS:
        entries, empties = [], []
        for slot in range(capacity):
            item_id, quantity = struct.unpack("<HH", view.ram(base + 4 * slot, 4))
            if (item_id, quantity) == (0, 0):
                empties.append(slot)
            else:
                entries.append((slot, item_id, quantity))
        last = max((e[0] for e in entries), default=-1)
        pockets.append({"name": name, "capacity": capacity, "entries": entries, "occupied": len(entries),
                        "holes": [s for s in empties if s < last]})
    return pockets


def read_save(profile: BuildReadProfile, raw: bytes) -> dict:
    """Structural + field read under the profile; raises instead of guessing."""
    try:
        view = layouts.detect(raw)
    except layouts.LayoutError as exc:
        raise ProfileError(f"layout rejected: {exc}") from exc
    if view.layout != profile.layout:
        raise ProfileError(f"layout {view.layout} is not the profile layout {profile.layout}")
    if profile.require_slot_parity:
        for slot in view.slots:
            if slot.state == "valid" and slot.counter % 2 != slot.slot_index:
                raise ProfileError("slot/counter parity differs from the qualified native rule")
    key, money = view.money()
    report = {
        "profile": profile.profile_id, "layout": view.layout, "file_sha256": view.file_sha256,
        "footer_bytes": len(view.footer), "active_slot": view.active_slot, "counter": view.counter,
        "slots": [{"slot": s.slot_index, "state": s.state, "counter": s.counter,
                   "rotation": view.rotations[s.slot_index]} for s in view.slots],
        "party_count": view.party_count,
        "party": [{"slot": m.index, "species": m.species, "level": m.level} for m in view.party()],
        "money": {"key_is_zero": key == 0, "qualified": key == 0, "value": money if key == 0 else None},
        "write_authorized": False,
    }
    if view.layout == layouts.V023PLUS:
        report["shel"] = {"counter": view.shel_counter, "page_table": list(view.page_table),
                          "inactive_page_table": None if view.inactive_page_table is None
                          else list(view.inactive_page_table)}
        report["pages"] = [{"page": p.page_index, "sector": p.physical_sector, "counter": p.counter}
                           for p in view.pages]
    report["fragments"] = [{"ram": f"0x{f.ram_start:08X}", "source": f.source,
                            "epoch_authenticated": f.epoch_authenticated, "sha256": _sha(f.data)}
                           for f in view.fragments]
    if key == 0:
        report["inventory"] = {
            "pockets": _pockets(view),
            "menu_counts": list(struct.unpack("<3H", view.ram(MENU_COUNTS_RAM, 6))),
            "alternate_bag_state": struct.unpack("<h", view.ram(ALTERNATE_BAG_RAM, 2))[0] < 0,
        }
    else:
        report["inventory"] = None
    return report


def sanitized(report: dict) -> dict:
    """Drop per-record values; keep structure, counts and hashes."""
    out = {k: v for k, v in report.items() if k not in ("party", "money", "inventory")}
    out["money"] = {"key_is_zero": report["money"]["key_is_zero"]}
    if report["inventory"] is not None:
        out["inventory"] = {p["name"]: {"occupied": p["occupied"], "holes": len(p["holes"])}
                            for p in report["inventory"]["pockets"]}
        out["inventory_alternate_bag_state"] = report["inventory"]["alternate_bag_state"]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--save", type=Path)
    args = parser.parse_args(argv)
    profile = PROFILES[args.profile]
    out: dict = {"profile": profile.profile_id, "capabilities": profile.capabilities, "read_only": True}
    try:
        if args.rom:
            out["rom"] = verify_rom(profile, args.rom.read_bytes())
        if args.save:
            out["save"] = sanitized(read_save(profile, args.save.read_bytes()))
    except OSError:
        print(json.dumps({"status": "REJECTED", "reason": "unable to read local input"}))
        return 2
    except ProfileError as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    out["status"] = "ACCEPTED_READ_ONLY"
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
