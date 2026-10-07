#!/usr/bin/env python3
"""Disposable, strictly read-only structural probe for PokemonStart saves.

Recognises the exact-v0.22 14-section layout and the v0.23+ "5 sections per
slot + SHEL-indexed Box pages" layout described by the bundled migration tool
(identical in v0.23, v0.26 and v0.27 packages) and corroborated by static ROM
constants. Scratch research tooling only: it never writes, repairs or
re-checksums anything. Unknown states are reported as unknown.

Output is sanitized: structure, hashes, counters, checksum validity, counts and
small semantic integers. No identity bytes, names, PIDs, OT IDs or raw records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

FLASH = 0x20000
FOOTER = 0x10
SECTOR = 0x1000
DATA = 0xFF0
SIG = 0x08012025
SIZES = (0xF24, 0xFF0, 0xFF0, 0xFF0, 0xD98) + (0xFF0,) * 8 + (0x450,)
PAGE_FIRST_ID, PAGE_COUNT = 0x40, 17
SHEL_SB1_OFFSET, SHEL_MAGIC = 0x1400, 0x4C454853  # "SHEL"
MON, PAGE0_MONS, PAGE_MONS, BOX_PAGES = 58, 12, 70, 15
P0_PARASITE, P0_MONS = 0x18B, 0x18B + 0xBA0      # confirmed by v0.27 ROM literals
PARTY_COUNT, PARTY, MONEY, KEY = 0x34, 0x38, 0x290, 0xF20

# RAM fragments shared by both layouts (ROM literals identical v0.22..v0.27).
# value: (ram_start, length, legacy_source, v023plus_source)
FRAGMENTS = (
    (0x0203B0E8, 0xCC, ("section", 0, 0xF24), ("section", 0, 0xF24)),
    (0x0203B1B4, 0x258, ("section", 4, 0xD98), ("section", 4, 0xD98)),
    (0x0203B40C, 0xBA0, ("section", 13, 0x450), ("page", 0, P0_PARASITE)),
    (0x0203BFAC, 0xFF0, ("sector", 30, 0), ("page", 15, 0)),
    (0x0203CF9C, 0xFF0, ("sector", 31, 0), ("page", 16, 0)),
)
# Inventory pockets (exact-v0.22 canonical RAM bases/capacities; v0.27 ROM
# literals for the same RAM bases are unchanged).
POCKETS = (("regular", 0x0203BA98, 700), ("key", 0x0203C588, 75),
           ("balls", 0x0203C6D4, 50), ("tmhm", 0x0203C79C, 128),
           ("berries", 0x0203C99C, 72))
MENU_COUNTS_RAM = 0x0203C6C2  # canonical raw 0x1E716 = sector30+0x716


def u16(b, o): return struct.unpack_from("<H", b, o)[0]
def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def sha(b): return hashlib.sha256(b).hexdigest()


def checksum(b: bytes, length: int) -> int:
    total = 0
    for o in range(0, length & ~3, 4):
        total = (total + u32(b, o)) & 0xFFFFFFFF
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def expected_length(section_id: int):
    if section_id < len(SIZES):
        return SIZES[section_id]
    if PAGE_FIRST_ID <= section_id < PAGE_FIRST_ID + PAGE_COUNT:
        return DATA
    return None


def sector_info(flash: bytes, n: int) -> dict:
    s = flash[n * SECTOR:(n + 1) * SECTOR]
    info = {"sector": n, "sha256_16": sha(s)[:16]}
    if s.count(0xFF) == SECTOR:
        info["kind"] = "erased_ff"; return info
    if s.count(0) == SECTOR:
        info["kind"] = "zero"; return info
    sid, chk, sig, cnt = u16(s, 0xFF4), u16(s, 0xFF6), u32(s, 0xFF8), u32(s, 0xFFC)
    if sig != SIG:
        info.update(kind="unsigned_data", nonzero_bytes=sum(1 for x in s if x), nonff_bytes=sum(1 for x in s if x != 0xFF))
        return info
    length = expected_length(sid)
    info.update(kind="signed", id=sid, id_hex=f"{sid:#04x}", counter=cnt, checksum_stored=f"{chk:#06x}",
                checksum_length=None if length is None else f"{length:#x}")
    if length is None:
        info["checksum_valid"] = None
    else:
        calc = checksum(s, length)
        info["checksum_calculated"] = f"{calc:#06x}"
        info["checksum_valid"] = calc == chk
    return info


def newer(a: int, b: int) -> int:
    """Vanilla-style newest-of-two with 0xFFFFFFFF->0 wrap special case."""
    if a == 0xFFFFFFFF and b == 0: return 1
    if b == 0xFFFFFFFF and a == 0: return 0
    sa = a - (1 << 32) if a & 0x80000000 else a
    sb = b - (1 << 32) if b & 0x80000000 else b
    return 0 if sa > sb else 1 if sb > sa else -1


def slot_status(sectors, first, count, ids):
    found = {}
    problems = []
    for n in range(first, first + count):
        si = sectors[n]
        if si["kind"] != "signed":
            problems.append(f"sector {n}: {si['kind']}"); continue
        if si["id"] not in ids:
            problems.append(f"sector {n}: unexpected id {si['id_hex']}"); continue
        if si["id"] in found:
            problems.append(f"sector {n}: duplicate id {si['id_hex']}"); continue
        if not si["checksum_valid"]:
            problems.append(f"sector {n}: checksum invalid"); continue
        found[si["id"]] = n
    counters = {sectors[n]["counter"] for n in found.values()}
    complete = set(found) == set(ids) and len(counters) == 1
    if len(counters) > 1:
        problems.append("mixed counters")
    return {"first_sector": first, "complete": complete, "counter": counters.pop() if complete else None,
            "id_to_sector": {f"{k:#04x}": v for k, v in sorted(found.items())}, "problems": problems}


def choose(slots):
    valid = [i for i, s in enumerate(slots) if s["complete"]]
    if not valid:
        return None, "no complete slot"
    if len(valid) == 1:
        return valid[0], "single complete slot"
    w = newer(slots[0]["counter"], slots[1]["counter"])
    if w < 0:
        return None, "UNKNOWN: equal counters (ambiguous)"
    return w, "newest by counter"


def probe(raw: bytes) -> dict:
    out = {"sha256": sha(raw), "size": len(raw)}
    if len(raw) not in (FLASH, FLASH + FOOTER):
        out["status"] = "UNSUPPORTED_SIZE"
        return out
    flash = raw[:FLASH]
    out["footer"] = None if len(raw) == FLASH else {"length": FOOTER, "sha256_16": sha(raw[FLASH:])[:16],
                                                    "treated_as": "opaque emulator trailer (not parsed)"}
    sectors = [sector_info(flash, n) for n in range(32)]
    out["sector_inventory"] = sectors
    legacy = [slot_status(sectors, 14 * k, 14, set(range(14))) for k in (0, 1)]
    modern = [slot_status(sectors, 5 * k, 5, set(range(5))) for k in (0, 1)]
    for m in modern:
        # Like the bundled tool's isNew(), a 5-section slot only counts as
        # v0.23+ when its section 2 carries the SHEL magic at SB1+0x1400.
        n2 = m["id_to_sector"].get("0x02")
        m["shel_magic"] = n2 is not None and u32(flash, n2 * SECTOR + (SHEL_SB1_OFFSET - DATA)) == SHEL_MAGIC
        if m["complete"] and not m["shel_magic"]:
            m["complete"] = False
            m["problems"].append("5-section shape without SHEL magic")
    lchoice, lwhy = choose(legacy)
    mchoice, mwhy = choose(modern)
    out["candidate_layouts"] = {
        "legacy_14_section": {"slots": legacy, "chosen": lchoice, "reason": lwhy},
        "v023plus_5_section": {"slots": modern, "chosen": mchoice, "reason": mwhy},
    }
    sections = None
    layout = "UNKNOWN"
    if mchoice is not None and lchoice is None:
        layout = "v023plus_5_section"
        idmap = modern[mchoice]["id_to_sector"]
    elif lchoice is not None and mchoice is None:
        layout = "legacy_14_section"
        idmap = legacy[lchoice]["id_to_sector"]
    elif lchoice is not None and mchoice is not None:
        # A legacy slot whose rotation puts ids 0..4 in sectors 0..4 also
        # satisfies the 5-section shape; only SHEL in section 2 (+0x410)
        # distinguishes the v0.23+ layout (the migration tool's own test).
        n2 = int(modern[mchoice]["id_to_sector"]["0x02"])
        has_shel = u32(flash, n2 * SECTOR + (SHEL_SB1_OFFSET - DATA)) == SHEL_MAGIC
        out["ambiguity_resolution"] = {"shel_magic_in_5_section_candidate": has_shel}
        if has_shel:
            layout = "UNKNOWN: both layouts parse and SHEL present"
        else:
            layout = "legacy_14_section"
            idmap = legacy[lchoice]["id_to_sector"]
            mchoice = None
    out["layout"] = layout
    if not layout.startswith(("v023plus", "legacy")):
        out["status"] = "UNKNOWN_LAYOUT"
        return out
    sec = {int(k, 16): flash[v * SECTOR:(v + 1) * SECTOR] for k, v in idmap.items()}
    sb2 = sec[0]
    sb1 = b"".join(sec[i][:SIZES[i]] for i in (1, 2, 3, 4))
    out["active_counter"] = (modern[mchoice] if layout.startswith("v023") else legacy[lchoice])["counter"]

    pages = None
    if layout.startswith("v023"):
        magic, shel_cnt = u32(sb1, SHEL_SB1_OFFSET), u32(sb1, SHEL_SB1_OFFSET + 4)
        table = list(sb1[SHEL_SB1_OFFSET + 8:SHEL_SB1_OFFSET + 8 + PAGE_COUNT])
        shel = {"magic_ok": magic == SHEL_MAGIC, "counter": shel_cnt,
                "counter_equals_slot_counter": shel_cnt == out["active_counter"],
                "page_sector_table": table,
                "table_is_10_to_26": table == list(range(10, 27)),
                "bytes_after_table_nonzero": sum(1 for x in sb1[SHEL_SB1_OFFSET + 8 + PAGE_COUNT:SHEL_SB1_OFFSET + 0x40] if x)}
        out["shel"] = shel
        page_rows = []
        pages = {}
        for p, n in enumerate(table):
            row = {"page": p, "expected_id": f"{PAGE_FIRST_ID + p:#04x}", "sector": n}
            if not 0 <= n < 32:
                row["status"] = "UNKNOWN: sector index out of range"; page_rows.append(row); continue
            si = sectors[n]
            row.update(kind=si["kind"], id=si.get("id_hex"), checksum_valid=si.get("checksum_valid"),
                       counter=si.get("counter"))
            row["id_matches"] = si.get("id") == PAGE_FIRST_ID + p
            row["counter_vs_shel"] = None if si.get("counter") is None else (
                "equal" if si["counter"] == shel_cnt else "different")
            if row["id_matches"] and si.get("checksum_valid"):
                pages[p] = flash[n * SECTOR:n * SECTOR + DATA]
            page_rows.append(row)
        out["box_pages"] = page_rows
        out["box_pages_all_valid"] = len(pages) == PAGE_COUNT
        out["page_counter_set"] = sorted({r.get("counter") for r in page_rows if r.get("counter") is not None})
        if 0 in pages:
            p0 = pages[0]
            out["page0_layout_observations"] = {
                "mons_region_offset": f"{P0_MONS:#x}", "mons_region_capacity": PAGE0_MONS,
                "occupied_box_mons_page0": sum(1 for i in range(PAGE0_MONS) if u16(p0, P0_MONS + i * MON + 0x1C)),
            }
        occ = 0; total = 0
        for p in range(BOX_PAGES):
            if p not in pages: continue
            base, n = (P0_MONS, PAGE0_MONS) if p == 0 else (0, PAGE_MONS)
            for i in range(n):
                total += 1
                if u16(pages[p], base + i * MON + 0x1C): occ += 1
        out["box_stream_observation"] = {"slots_scanned": total, "species_field_nonzero": occ,
                                         "note": "58-byte record species offset 0x1C per migration tool; semantics unqualified"}

    # Party / Money (SaveBlock1/2 offsets assumed unchanged; flagged as such)
    count = sb1[PARTY_COUNT]
    party = []
    for i in range(6):
        rec = sb1[PARTY + 100 * i:PARTY + 100 * (i + 1)]
        party.append({"slot": i, "species": u16(rec, 32), "stored_level": rec[84],
                      "all_zero": not any(rec)})
    out["party"] = {"count": count, "count_in_range": 0 <= count <= 6, "records": party,
                    "trailing_slots_all_zero": all(p["all_zero"] for p in party[count:]) if count <= 6 else None,
                    "assumption": "SaveBlock1 +0x34/+0x38 unchanged from v0.22 (migration copies SB1 verbatim)"}
    key = u32(sb2, KEY)
    out["money"] = {"decoded": u32(sb1, MONEY) ^ key, "key_is_zero": key == 0,
                    "assumption": "SB1+0x290 XOR SB2+0xF20 as in exact-v0.22"}

    # RAM-fragment reconstruction for Inventory / parasite data
    def frag_bytes(src):
        kind, ident, off = src
        if kind == "section":
            return sec[ident][off:off + 0x1000]
        if kind == "sector":
            return flash[ident * SECTOR + off:ident * SECTOR + SECTOR]
        if pages is None or ident not in pages:
            return None
        return pages[ident][off:]
    frag = []
    for ram, length, lsrc, msrc in FRAGMENTS:
        b = frag_bytes(msrc if layout.startswith("v023") else lsrc)
        frag.append((ram, length, None if b is None else b[:length]))
    out["fragments"] = [{"ram": f"{r:#010x}", "length": f"{l:#x}", "available": b is not None,
                         "sha256_16": None if b is None else sha(b)[:16]} for r, l, b in frag]

    def ram_read(addr, n):
        for r, l, b in frag:
            if r <= addr and addr + n <= r + l and b is not None:
                return b[addr - r:addr - r + n]
        return None
    inv = {}
    for name, base, cap in POCKETS:
        occupied = holes = 0; first_empty = None; unreadable = 0; qty = 0
        for i in range(cap):
            e = ram_read(base + 4 * i, 4)
            if e is None:
                unreadable += 1; continue
            item, q = struct.unpack("<HH", e)
            if (item, q) == (0, 0):
                if first_empty is None: first_empty = i
            else:
                occupied += 1; qty += q
                if first_empty is not None: holes += 1
        inv[name] = {"capacity": cap, "occupied": occupied, "holes_after_first_empty": holes,
                     "unreadable_slots": unreadable, "quantity_sum_raw": qty}
    mc = ram_read(MENU_COUNTS_RAM, 6)
    out["inventory"] = {"pockets": inv, "menu_counts": None if mc is None else list(struct.unpack("<3H", mc)),
                        "key_is_zero_required_by_v022_model": key == 0,
                        "assumption": "fragment mapping: v0.22 canonical; v0.23+ per migration tool + ROM literals"}
    if layout.startswith("v023"):
        out["extra_sectors"] = [{"sector": s["sector"], "kind": s["kind"], "id": s.get("id_hex")}
                                for s in sectors[27:32]]
    else:
        out["extra_sectors"] = [{"sector": s["sector"], "kind": s["kind"], "nonzero": s.get("nonzero_bytes")}
                                for s in sectors[28:32]]
    out["status"] = "PARSED_READ_ONLY"
    return out


def structural_diff(a: dict, araw: bytes, b: dict, braw: bytes) -> dict:
    """Region-level comparison of two probed saves (counts only, no bytes)."""
    res = {"layouts": [a.get("layout"), b.get("layout")]}
    if a.get("status") != "PARSED_READ_ONLY" or b.get("status") != "PARSED_READ_ONLY":
        res["status"] = "UNKNOWN: one side not parsed"; return res
    res["party_equal"] = a["party"] == b["party"]
    res["money_equal"] = a["money"]["decoded"] == b["money"]["decoded"]
    res["fragments_equal"] = [x["sha256_16"] == y["sha256_16"] for x, y in zip(a["fragments"], b["fragments"])]
    res["inventory_equal"] = a["inventory"]["pockets"] == b["inventory"]["pockets"]
    res["footer_equal"] = araw[FLASH:] == braw[FLASH:]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("save", type=Path)
    ap.add_argument("--against", type=Path, help="optional second save for structural diff")
    ap.add_argument("--brief", action="store_true", help="omit per-sector inventory")
    args = ap.parse_args(argv)
    paths = [args.save] + ([args.against] if args.against else [])
    raws = []
    for p in paths:
        if not p.is_file():
            print(json.dumps({"status": "STOP", "reason": "not a regular file"})); return 2
        with p.open("rb") as f:
            raws.append(f.read())
    results = [probe(r) for r in raws]
    for p, r in zip(paths, raws):  # immutability check
        with p.open("rb") as f:
            if f.read() != r:
                print(json.dumps({"status": "STOP", "reason": "input changed during probe"})); return 3
    if args.brief:
        for r in results: r.pop("sector_inventory", None)
    doc = {"probe": results[0], "read_only": True, "inputs_unchanged": True}
    if len(results) == 2:
        doc["against"] = results[1]
        doc["structural_diff"] = structural_diff(results[0], raws[0], results[1], raws[1])
    print(json.dumps(doc, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
