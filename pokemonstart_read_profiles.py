#!/usr/bin/env python3
"""Exact-build READ profiles binding build identity, save-layout family and
ROM-semantic table verification. Read-only; no profile grants write authority.

Capability levels are kept separate on purpose:

1. ``layout_read``          -- the save structure is understood for reading;
2. ``field_read``           -- field locations/semantic reads are qualified;
3. ``write_mechanics``      -- never granted here.

Field reads are only available through ``read_save(profile, save, rom)``,
which first binds the exact ROM (size, SHA-256, header pointers and every
semantic-table hash). A save alone never yields qualified fields. Exact-v0.22
Money and Inventory are delegated to the canonical v0.22 modules so their
eligibility boundary is the canonical one, unchanged.
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
import pokemonstart_v022_inventory_model as inventory_model
import pokemonstart_v022_product_money as product_money

ITEM_COUNT, ITEM_SIZE, ITEM_POINTER_FIELDS = 839, 40, (16, 24, 32)
MAX_MONEY = 9_999_999


@dataclass(frozen=True)
class SemanticTable:
    name: str
    size: int
    sha256: str
    normalization: str = "raw"


@dataclass(frozen=True)
class SemanticModel:
    model_id: str
    tables: tuple[SemanticTable, ...]


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
CANONICAL_SEMANTIC_MODEL = SemanticModel(SEMANTIC_MODEL_ID, SEMANTIC_TABLES)

# Inventory pockets: (name, RAM base, capacity, item-metadata pocket number).
# RAM bases/capacities are covered by the pocket_descriptor table hash.
POCKETS = (("regular", 0x0203BA98, 700, 1), ("key", 0x0203C588, 75, 2), ("balls", 0x0203C6D4, 50, 3),
           ("tmhm", 0x0203C79C, 128, 4), ("berries", 0x0203C99C, 72, 5))
MENU_COUNTS_RAM = 0x0203C6C2
ALTERNATE_BAG_RAM = 0x0203B672

V022_DELEGATE = "canonical_v022_delegate"
V023PLUS_NATIVE = "v023plus_native"


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
    field_reader: str
    semantic_model: SemanticModel = CANONICAL_SEMANTIC_MODEL
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
    capabilities={"layout_read": "CANONICAL (pokemonstart_save_verifier, unchanged)",
                  "field_read": "DELEGATED TO CANONICAL v0.22 MODULES: Party records from the canonical "
                                "verifier; Money via pokemonstart_v022_product_money.inspect; Inventory via "
                                "pokemonstart_v022_inventory_model.inspect (exact canonical eligibility)",
                  "write_mechanics": "NOT GRANTED BY THIS PROFILE (canonical v0.22 writers are separate)"},
    field_reader=V022_DELEGATE,
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
                  "field_read": "QUALIFIED ONLY AFTER EXACT v0.27 ROM VERIFICATION: Party raw records; key0 Money "
                                "0..9,999,999; Inventory pocket entries under the E1-equivalent eligibility "
                                "boundary (key0, Party 1..6, consecutive valid counters, ordinary bag only, "
                                "catalog-valid entries); semantic tables content-verified (code-path "
                                "equivalence not reproduced)",
                  "write_mechanics": "NOT QUALIFIED"},
    field_reader=V023PLUS_NATIVE,
    notes=("one migrated save; empty Boxes; one copy-on-write relocation observed",
           "spare-sector selection/reuse, populated Box pages and three first-save parasite bytes unresolved"),
)

PROFILES = {"v022": V022_EXACT, "v027": V027_EXACT}


class ProfileError(ValueError):
    """Raised when a ROM or save does not satisfy an exact read profile."""


@dataclass(frozen=True)
class VerifiedRom:
    """Proof object returned only by ``verify_rom``; carries the bound ROM."""

    profile_id: str
    rom_sha256: str
    report: dict
    rom: bytes = field(repr=False, compare=False)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize(table: SemanticTable, blob: bytes) -> bytes:
    if table.normalization == "raw":
        return blob
    if table.normalization != "item_pointer_flags" or len(blob) != ITEM_COUNT * ITEM_SIZE:
        raise ProfileError(f"unsupported normalization for {table.name}")
    data = bytearray(blob)
    for index in range(ITEM_COUNT):
        for offset in ITEM_POINTER_FIELDS:
            at = index * ITEM_SIZE + offset
            struct.pack_into("<I", data, at, 0 if struct.unpack_from("<I", data, at)[0] == 0 else 1)
    return bytes(data)


def verify_rom(profile: BuildReadProfile, rom: bytes) -> VerifiedRom:
    """Bind a ROM to the profile: size, SHA-256, header pointers and every table hash."""
    if not isinstance(rom, (bytes, bytearray)) or len(rom) != profile.rom_size:
        raise ProfileError("ROM size does not match the profile")
    rom = bytes(rom)
    if _sha(rom) != profile.rom_sha256:
        raise ProfileError("ROM SHA-256 does not match the profile")
    for name, (pointer, table) in profile.header_pointers.items():
        if struct.unpack_from("<I", rom, pointer)[0] != 0x08000000 + profile.table_offsets[table]:
            raise ProfileError(f"header pointer for {name} does not match the profile")
    tables = {}
    for table in profile.semantic_model.tables:
        start = profile.table_offsets[table.name]
        blob = rom[start:start + table.size]
        if len(blob) != table.size or _sha(_normalize(table, blob)) != table.sha256:
            raise ProfileError(f"semantic table {table.name} content differs from {profile.semantic_model.model_id}")
        tables[table.name] = {"offset": f"0x{start:07X}", "size": table.size, "sha256": table.sha256,
                              "normalization": table.normalization}
    report = {"profile": profile.profile_id, "rom_sha256": profile.rom_sha256,
              "semantic_model": profile.semantic_model.model_id, "tables": tables}
    return VerifiedRom(profile.profile_id, profile.rom_sha256, report, rom)


def _unqualified(reason: str, **extra) -> dict:
    return {"qualified": False, "reason": reason, **extra}


def _catalog(profile: BuildReadProfile, rom: bytes) -> dict[int, int]:
    """Item id -> pocket number, using the canonical E1 validity rules.

    Mirrors pokemonstart_v022_inventory_model.extract_catalog (name decoding,
    stored id, pocket 1..5, importance 0..2) at the profile's verified offset.
    """
    base = profile.table_offsets["items"]
    catalog = {}
    for item_id in range(ITEM_COUNT):
        record = rom[base + item_id * ITEM_SIZE:base + (item_id + 1) * ITEM_SIZE]
        stored = struct.unpack_from("<H", record, 10)[0]
        importance, pocket = record[20], record[22]
        try:
            inventory_model.decode_name(record[:10])
        except ValueError:
            continue
        if item_id == 0 or stored != item_id or pocket not in range(1, 6) or importance not in (0, 1, 2):
            continue
        catalog[item_id] = pocket
    return catalog


def _native_money(view: layouts.SaveView) -> dict:
    key, money = view.money()
    if key != 0:
        return _unqualified("Money supports key0 only")
    if not 0 <= money <= MAX_MONEY:
        return _unqualified("decoded Money outside 0..9,999,999")
    return {"qualified": True, "value": money}


def _native_inventory(view: layouts.SaveView, profile: BuildReadProfile, verified: VerifiedRom) -> dict:
    """E1-equivalent eligibility boundary for the v0.23+ native layout.

    Differences from the legacy E1 gate are structural only: a migrated state
    with one erased slot is allowed because every fragment is read from the
    active slot or from pages referenced by its SHEL table (no global sectors).
    """
    key, _ = view.money()
    if key != 0:
        return _unqualified("inventory supports key0 only")
    counters = [s.counter for s in view.slots if s.state == "valid"]
    if len(counters) == 2 and abs(counters[0] - counters[1]) != 1:
        return _unqualified("unsupported inventory save epoch")
    if not 1 <= view.party_count <= 6:
        return _unqualified("unsupported inventory Party state")
    if struct.unpack("<h", view.ram(ALTERNATE_BAG_RAM, 2))[0] < 0:
        return _unqualified("alternate runtime bag state unsupported")
    catalog = _catalog(profile, verified.rom)
    pockets, issues = [], []
    for name, base, capacity, pocket_id in POCKETS:
        entries, empties, seen = [], [], set()
        for slot in range(capacity):
            item_id, quantity = struct.unpack("<HH", view.ram(base + 4 * slot, 4))
            if (item_id, quantity) == (0, 0):
                empties.append(slot)
                continue
            if item_id not in catalog:
                issues.append({"pocket": name, "slot": slot, "reason": "invalid/excluded item ID"})
            elif catalog[item_id] != pocket_id:
                issues.append({"pocket": name, "slot": slot, "reason": "metadata pocket mismatch"})
            elif not 1 <= quantity <= 999:
                issues.append({"pocket": name, "slot": slot, "reason": "quantity outside key0 audit range 1..999"})
            elif item_id in seen:
                issues.append({"pocket": name, "slot": slot, "reason": "duplicate item ID"})
            seen.add(item_id)
            entries.append((slot, item_id, quantity))
        last = max((e[0] for e in entries), default=-1)
        pockets.append({"name": name, "capacity": capacity, "entries": entries, "occupied": len(entries),
                        "holes": [s for s in empties if s < last]})
    if issues:
        return _unqualified("inventory records outside the qualified state", issues=issues)
    return {"qualified": True, "pockets": pockets,
            "menu_counts": list(struct.unpack("<3H", view.ram(MENU_COUNTS_RAM, 6)))}


def _v022_money(raw: bytes, profile: BuildReadProfile) -> dict:
    try:
        return {"qualified": True, "value": product_money.inspect(raw, profile.rom_sha256)["money"]}
    except ValueError as exc:
        return _unqualified(str(exc))


def _v022_inventory(raw: bytes, verified: VerifiedRom) -> dict:
    try:
        report = inventory_model.inspect(raw, verified.rom)
    except ValueError as exc:
        return _unqualified(str(exc))
    if not report["state_supported"]:
        return _unqualified("inventory records outside the qualified state",
                            issues=[{k: i[k] for k in ("pocket", "slot", "reason")} for i in report["issues"]])
    return {"qualified": True, "pockets": [
        {"name": p["name"], "capacity": p["capacity"], "occupied": p["occupied"], "holes": p["holes"],
         "entries": [(e["slot"], e["item_id"], e["quantity"]) for e in p["entries"]]} for p in report["pockets"]]}


def read_save(profile: BuildReadProfile, raw: bytes, rom: bytes) -> dict:
    """Exact-ROM-bound structural + field read; raises ProfileError instead of guessing."""
    verified = verify_rom(profile, rom)
    try:
        view = layouts.detect(raw)
        if view.layout != profile.layout:
            raise ProfileError(f"layout {view.layout} is not the profile layout {profile.layout}")
        if profile.require_slot_parity:
            for slot in view.slots:
                if slot.state == "valid" and slot.counter % 2 != slot.slot_index:
                    raise ProfileError("slot/counter parity differs from the qualified native rule")
        party = [{"slot": m.index, "species": m.species, "level": m.level} for m in view.party()]
        if profile.field_reader == V022_DELEGATE:
            money, inventory = _v022_money(raw, profile), _v022_inventory(raw, verified)
        elif profile.field_reader == V023PLUS_NATIVE:
            money, inventory = _native_money(view), _native_inventory(view, profile, verified)
        else:
            raise ProfileError("unknown field reader")
    except layouts.LayoutError as exc:
        raise ProfileError(f"save rejected: {exc}") from exc
    report = {
        "profile": profile.profile_id, "rom": verified.report, "layout": view.layout,
        "file_sha256": view.file_sha256, "footer_bytes": len(view.footer),
        "active_slot": view.active_slot, "counter": view.counter,
        "slots": [{"slot": s.slot_index, "state": s.state, "counter": s.counter,
                   "rotation": view.rotations[s.slot_index]} for s in view.slots],
        "party_count": len(party), "party": party, "money": money, "inventory": inventory,
        "fragments": [{"ram": f"0x{f.ram_start:08X}", "source": f.source, "checksum_covered": f.checksum_covered,
                       "epoch_bound": f.epoch_bound, "sha256": _sha(f.data)} for f in view.fragments],
        "write_authorized": False,
    }
    if view.layout == layouts.V023PLUS:
        report["shel"] = {"counter": view.shel_counter, "page_table": list(view.page_table),
                          "inactive_page_table": None if view.inactive_page_table is None
                          else list(view.inactive_page_table)}
        report["pages"] = [{"page": p.page_index, "sector": p.physical_sector, "counter": p.counter}
                           for p in view.pages]
    return report


def sanitized(report: dict) -> dict:
    """Drop per-record values; keep structure, qualification flags, counts and hashes."""
    out = {k: v for k, v in report.items() if k not in ("party", "money", "inventory")}
    out["money"] = {"qualified": report["money"]["qualified"], "reason": report["money"].get("reason")}
    inventory = report["inventory"]
    out["inventory"] = {"qualified": inventory["qualified"], "reason": inventory.get("reason"),
                        "issue_count": len(inventory.get("issues", []))}
    if inventory["qualified"]:
        out["inventory"]["pockets"] = {p["name"]: {"occupied": p["occupied"], "holes": len(p["holes"])}
                                       for p in inventory["pockets"]}
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--save", type=Path, required=True)
    args = parser.parse_args(argv)
    profile = PROFILES[args.profile]
    try:
        report = read_save(profile, args.save.read_bytes(), args.rom.read_bytes())
    except OSError:
        print(json.dumps({"status": "REJECTED", "reason": "unable to read local input"}))
        return 2
    except ProfileError as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "ACCEPTED_READ_ONLY", "profile": profile.profile_id,
                      "capabilities": profile.capabilities, "save": sanitized(report)},
                     indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
