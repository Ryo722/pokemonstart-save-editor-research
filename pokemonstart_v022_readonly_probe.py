#!/usr/bin/env python3
"""Read-only mGBA compatibility probe for the exact Fast Lab v0.22 ROM."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile

import pokemonstart_mgba_harness as bridge
import pokemonstart_save_verifier as verifier

PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
V022_ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
V015_LINEAGE_SAVE_SHA256 = "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf"
V022_EXPERIMENTAL_MONEY_SAVE_SHA256 = "15bdac0d6635c6237549565c49e3752c167e85a33643b89ff722ed3c7d17d569"
V022_EXPERIMENTAL_PARTY_FRIENDSHIP_SAVE_SHA256 = "cb817b561c1eb29813b5e58524d8536dbdf42cb13065b90b5603a47a73f2a37d"
V022_EXPERIMENTAL_PARTY_ATTACK_IV_SAVE_SHA256 = "5a688c2c3f2e3f2ba4e9f73788ead12da715adaae861880aa0ef5f7faeb620de"
V022_EXPERIMENTAL_PARTY_POUND_MOVE_SAVE_SHA256 = "ded29c2b307343b662ebcdf0889f7b2e24f0952a453e7622049b655e40891efb"
V022_EXPERIMENTAL_PARTY_LEVEL_6_SAVE_SHA256 = "09e58a8cda8277ea107991cbf01ea99fa0d0724ce476330be45ef1d5456ed6dc"
V022_EXPERIMENTAL_PARTY_IVYSAUR_SAVE_SHA256 = "fb0d649fe39e286a7bbe5c8bbd8e62e373b3dc8e6048b2405d8f1f647dc54f4f"
USER_POTION_SAVE_SHA256 = "a85fed049378e81f373446a720af0867d7b7f4d3fc9e0a7d54c39632fc04561f"
COMPOSED_PARTY_SAVE_SHA256 = "29380e12b8c43df9dfd12f3070e2bbe2925e300e9b4a1f3fcafda9fef56ef0d5"
USER_POTION_QUANTITY_2_SAVE_SHA256 = "b32abee33dc951c61068b4a83f4bc06215db8a86d880f07620a1aece82ccca50"
FASTLAB_POTION_QUANTITY_3_SAVE_SHA256 = "51129cdd5168f2f9f3d28966085bfdd4ae094c2a705052253001cc3d189c987b"
ALLOWED_SAVE_HASHES = {V015_LINEAGE_SAVE_SHA256, V022_EXPERIMENTAL_MONEY_SAVE_SHA256,
                       V022_EXPERIMENTAL_PARTY_FRIENDSHIP_SAVE_SHA256,
                       V022_EXPERIMENTAL_PARTY_ATTACK_IV_SAVE_SHA256,
                       V022_EXPERIMENTAL_PARTY_POUND_MOVE_SAVE_SHA256,
                       V022_EXPERIMENTAL_PARTY_LEVEL_6_SAVE_SHA256,
                       V022_EXPERIMENTAL_PARTY_IVYSAUR_SAVE_SHA256,
                       USER_POTION_SAVE_SHA256, COMPOSED_PARTY_SAVE_SHA256,
                       USER_POTION_QUANTITY_2_SAVE_SHA256,
                       FASTLAB_POTION_QUANTITY_3_SAVE_SHA256}


def decode_offline(raw: bytes) -> dict[str, object]:
    result = verifier.verify_bytes(raw)
    money, party_count, saved, party0_from_block = bridge.save_money(raw)
    active = result.slots[result.active_slot]
    party0 = active.section(1).data[0x38:0x38 + 100]
    key = int.from_bytes(active.section(0).data[0xF20:0xF24], "little")
    record = result.party[0] if result.party else None
    return {
        "file_sha256": result.file_sha256,
        "active_slot": result.active_slot,
        "counter": result.slots[result.active_slot].counter,
        "encryption_key": key,
        "money": money,
        "party_count": party_count,
        "party0_bytes": party0,
        "party0": None if record is None else {
            "species": record.species, "backup_species": record.backup_species,
            "level": record.level, "experience": record.experience,
            "friendship": record.friendship, "markings": record.markings,
            "ball": record.ball, "nature_mint": record.nature_mint,
            "held_item": record.held_item, "moves": list(record.moves),
            "ability_num": record.ability_num,
            "ivs": list(record.ivs), "evs": list(record.evs), "pp": list(record.pp),
            "stats": [record.hp, record.max_hp, record.attack, record.defense,
                      record.speed, record.sp_attack, record.sp_defense],
        },
        "saved_statistic": saved,
    }


def observe_ewram(ewram: bytes, offline: dict[str, object]) -> dict[str, object]:
    address = bridge.discover_money(
        ewram, int(offline["money"]), int(offline["party_count"]),
        int(offline["saved_statistic"]), offline["party0_bytes"],
    )
    money_offset = address - 0x02000000
    block_offset = money_offset - 0x290
    if block_offset < 0 or block_offset + 0x38 + 100 > len(ewram):
        raise bridge.HarnessError("discovered SaveBlock does not fit EWRAM")
    party_count = ewram[block_offset + 0x34]
    party0 = ewram[block_offset + 0x38:block_offset + 0x38 + 100]
    live_party = verifier._decode_party_record(party0, 0) if party_count else None
    items_base = 0x0203BA98 - 0x02000000
    item_entries = []
    item_pocket = bytearray()
    for slot in range(450):
        offset = items_base + slot * 4
        item_id = int.from_bytes(ewram[offset:offset + 2], "little")
        quantity = int.from_bytes(ewram[offset + 2:offset + 4], "little")
        item_pocket.extend(ewram[offset:offset + 4])
        if item_id or quantity:
            item_entries.append({"pocket": "regular_items", "slot": slot,
                                 "item_id": item_id, "live_quantity": quantity})
    pocket_ram_matches = []
    if item_entries:
        search_at = 0
        while len(pocket_ram_matches) < 8:
            found = ewram.find(item_pocket, search_at)
            if found < 0:
                break
            if found % 4 == 0:
                pocket_address = 0x02000000 + found
                pocket_ram_matches.append({"address": f"0x{pocket_address:08x}",
                                           "exact_450_slot_match": True})
            search_at = found + 4
    live_money = int.from_bytes(ewram[money_offset:money_offset + 4], "little")
    if party_count != offline["party_count"] or party0 != offline["party0_bytes"]:
        raise bridge.HarnessError("live party structure differs from offline save")
    if live_money != offline["money"]:
        raise bridge.HarnessError("live Money differs from offline save")
    return {"money_address": f"0x{address:08x}", "money": live_money,
            "party_count": party_count,
            "party0": None if live_party is None else {
                "species": live_party.species, "experience": live_party.experience,
                "level": live_party.level, "ability_num": live_party.ability_num,
                "stats": [live_party.hp, live_party.max_hp, live_party.attack,
                          live_party.defense, live_party.speed,
                          live_party.sp_attack, live_party.sp_defense]},
            "party0_sha256": hashlib.sha256(party0).hexdigest(),
            "party0_matches_offline": True,
            "regular_items": {"base": "0x0203BA98", "slots_scanned": 450,
                              "populated": item_entries,
                              "full_pocket_ram_matches": pocket_ram_matches}}


def _private_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file() or not resolved.is_relative_to(PRIVATE_ROOT):
        raise bridge.HarnessError(f"{label} must be an existing file in PokemonStart-private")
    return resolved


def run(rom: Path, save: Path, mgba: Path) -> dict[str, object]:
    rom = _private_file(rom, "ROM")
    save = _private_file(save, "save")
    rom_sha = bridge.sha(rom)
    save_sha = bridge.sha(save)
    if rom_sha != V022_ROM_SHA256:
        raise bridge.HarnessError("ROM is not the verified v0.22 patched build")
    if save_sha not in ALLOWED_SAVE_HASHES:
        raise bridge.HarnessError("save is not an exact allowlisted disposable Fast Lab input")
    offline = decode_offline(save.read_bytes())
    root = Path(tempfile.gettempdir()) / "pokemonstart-fast-lab-v022-compat"
    bridge.outside_repo(root)
    root.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix="session-", dir=root))
    working_rom = session / "research.gba"
    working_save = session / "research.sav"
    shutil.copyfile(rom, working_rom)
    shutil.copyfile(save, working_save)
    if bridge.sha(working_rom) != rom_sha or bridge.sha(working_save) != save_sha:
        raise bridge.HarnessError("private ROM/save clone hash mismatch")
    artifacts = session / "artifacts"
    artifacts.mkdir()
    audit = session / "audit.jsonl"
    version = subprocess.check_output([str(mgba), "--version"], text=True).strip()
    if "mGBA 0.10.5" not in version:
        raise bridge.HarnessError("read-only probe requires dedicated mGBA 0.10.5")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(180)
    token = secrets.token_hex(32)
    script = bridge.write_stable_bridge(
        "127.0.0.1", server.getsockname()[1], token, working_save, artifacts)
    pid = None
    conn = None
    source_before = {"rom": bridge.sha(rom), "save": bridge.sha(save)}
    working_save_before = bridge.sha(working_save)
    result: dict[str, object] = {
        "status": "started", "rom_sha256": rom_sha,
        "source_save_sha256": save_sha, "working_save_sha256_before": working_save_before,
        "mGBA": version, "offline": {k: v for k, v in offline.items() if k != "party0_bytes"},
        "session": str(session), "script_path": str(script),
        "bootstrap_load_method": None,
    }
    audit.write_text(json.dumps({"event": "readonly_compat_start", **result},
                                ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    try:
        pid = bridge.launch_owned_mgba(mgba, working_rom)
        ui = bridge.attach_cold_bridge_ui(pid, script)
        peer, address = server.accept()
        if address[0] != "127.0.0.1":
            peer.close()
            raise bridge.HarnessError("bridge peer is not IPv4 loopback")
        conn = peer
        client = bridge.Bridge(conn, token, audit, artifacts)
        meta = client.command("meta")
        client.command("health")
        if len(meta) != 3 or meta[0] != "0" or not meta[1] or not meta[2]:
            raise bridge.HarnessError(f"unexpected GBA/game metadata: {meta}")
        client.command("load_save")
        client.command("reset")
        client.command("frames", 120)
        client.command("screenshot", 1)
        observed = observe_ewram(client.read_ewram(), offline)
        result.update({"status": "read-compatible", "game_metadata": list(meta),
                       "bootstrap_load_method": ui["load_method"], "live": observed,
                       "screenshot": str(artifacts / "screen-1.png"), "pid": pid})
        client.log("readonly_compat_pass", **observed, metadata=meta,
                   load_method=ui["load_method"])
    finally:
        if pid is not None and pid in bridge.mgba_pids():
            bridge.stop_owned_mgba(pid)
        if conn is not None:
            conn.close()
        server.close()
    source_after = {"rom": bridge.sha(rom), "save": bridge.sha(save)}
    working_after = bridge.sha(working_save)
    result["source_sha256_after"] = source_after
    result["source_immutable"] = source_after == source_before
    result["working_save_sha256_after"] = working_after
    result["working_save_unchanged"] = working_after == working_save_before
    if not result["source_immutable"]:
        raise bridge.HarnessError("a protected source artifact changed")
    if not result.get("live"):
        result["status"] = "probe did not reach live compatibility confirmation"
    with audit.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"event": "readonly_compat_final", **result},
                                ensure_ascii=False, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("save", type=Path)
    parser.add_argument("--mgba", type=Path,
                        default=Path("/Applications/mGBA.app/Contents/MacOS/mGBA"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.rom, args.save, args.mgba), ensure_ascii=False, indent=2))
    except (bridge.HarnessError, OSError, verifier.VerificationError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
