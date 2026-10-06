#!/usr/bin/env python3
"""Bounded v0.22 experimental editor for the observed Potion regular-item slot."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from typing import Any

import pokemonstart_save_verifier as v

REPO = Path(__file__).resolve().parent
PRIVATE_ROOT = Path("/Users/ryohanazaki/claude-workspace/PokemonStart-private").resolve()
CAPABILITY_PROFILE = REPO / "docs/fast-lab-v022-capability.json"
EXPECTED_ROM_SHA256 = "6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0"
SUPPORTED_INPUT_SHA256 = "b32abee33dc951c61068b4a83f4bc06215db8a86d880f07620a1aece82ccca50"
ROM_DEFAULT = PRIVATE_ROOT / "PokemonStart_v0.22_PRIVATE.gba"
ITEM_SECTION = 13
ITEM_OFFSET = 0xADC
ITEM_ID_POTION = 13
MAX_EXPERIMENTAL_QUANTITY = 3
CHECKSUM_COVERED_LENGTH = v.SECTION_LENGTHS[ITEM_SECTION]


class InventoryEditorError(ValueError):
    """Refuse inventory writes outside the single corroborated layout."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _private_file(path: str | Path, label: str, *, must_exist: bool) -> Path:
    resolved = Path(path).resolve(strict=must_exist)
    if not resolved.is_relative_to(PRIVATE_ROOT):
        raise InventoryEditorError(f"{label} must be inside PokemonStart-private")
    if must_exist and not resolved.is_file():
        raise InventoryEditorError(f"{label} is not a regular file")
    return resolved


def _profile_hash() -> str:
    try:
        profile = json.loads(CAPABILITY_PROFILE.read_text(encoding="utf-8"))
        value = profile["profile_key"]["patched_rom_sha256"]
        schema = profile["profile_schema"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise InventoryEditorError("v0.22 capability profile is unreadable") from exc
    if schema != 1 or value != EXPECTED_ROM_SHA256:
        raise InventoryEditorError("capability profile does not match exact v0.22 ROM")
    return value


def _check_rom(path: str | Path) -> str:
    rom = _private_file(path, "ROM", must_exist=True)
    expected = _profile_hash()
    actual = _sha(rom.read_bytes())
    if actual != expected:
        raise InventoryEditorError("ROM hash does not match exact v0.22 capability profile")
    return actual


def _active_item_area(raw: bytes) -> tuple[v.VerificationResult, v.SectionInfo, int]:
    result = v.verify_bytes(raw)
    active = result.slots[result.active_slot]
    key = int.from_bytes(active.section(0).data[0xF20:0xF24], "little")
    if key != 0:
        raise InventoryEditorError("inventory representation is only proven for key 0")
    section = active.section(ITEM_SECTION)
    if ITEM_OFFSET < CHECKSUM_COVERED_LENGTH:
        raise InventoryEditorError("observed item field unexpectedly became checksum-covered")
    if ITEM_OFFSET + 4 > len(section.data):
        raise InventoryEditorError("observed item field is outside section payload")
    if any(section.data[ITEM_OFFSET + 4:]):
        raise InventoryEditorError("additional regular-pocket records are outside this proof")
    item_id, encrypted_quantity = struct.unpack_from("<HH", section.data, ITEM_OFFSET)
    quantity = encrypted_quantity ^ (key & 0xFFFF)
    if item_id != ITEM_ID_POTION:
        raise InventoryEditorError("only the live-correlated Potion slot is supported")
    if not 1 <= quantity <= MAX_EXPERIMENTAL_QUANTITY:
        raise InventoryEditorError("Potion quantity is outside the experimental 1..3 range")
    return result, section, quantity


def inspect_bytes(raw: bytes) -> dict[str, Any]:
    result, section, quantity = _active_item_area(raw)
    active = result.slots[result.active_slot]
    return {
        "status": "FAST LAB v0.22 regular-items read-only inspect",
        "save_sha256": result.file_sha256,
        "active_slot": result.active_slot,
        "active_counter": active.counter,
        "section_id": ITEM_SECTION,
        "section_relative_offset": ITEM_OFFSET,
        "checksum_covered": False,
        "encryption_key": 0,
        "entries": [{"slot": 0, "item_id": ITEM_ID_POTION,
                     "item_name": "Potion", "quantity": quantity}],
        "limits": ["one live-correlated regular item", "quantity 1..3",
                   "key 0", "exact v0.22 ROM profile"],
        "evidence": ["exact-save offline", "same-file normal-save differential",
                     "mGBA live read"],
    }


def inspect(input_save: str | Path, rom_path: str | Path = ROM_DEFAULT) -> dict[str, Any]:
    _check_rom(rom_path)
    source = _private_file(input_save, "input save", must_exist=True)
    return inspect_bytes(source.read_bytes())


def _slot_profile(result: v.VerificationResult) -> tuple[Any, ...]:
    return tuple((slot.slot_index, slot.state, slot.counter,
                  tuple((section.section_id, section.physical_sector,
                         section.counter, section.signature)
                        for section in slot.sections))
                 for slot in result.slots)


def derive_bytes(raw: bytes, slot: int, item_id: int, quantity: int) -> tuple[bytes, dict[str, Any]]:
    if isinstance(slot, bool) or not isinstance(slot, int) or slot != 0:
        raise InventoryEditorError("only the existing regular-items slot 0 is supported")
    if isinstance(item_id, bool) or not isinstance(item_id, int) or item_id != ITEM_ID_POTION:
        raise InventoryEditorError("item ID must be the existing Potion (13)")
    if (isinstance(quantity, bool) or not isinstance(quantity, int)
            or not 1 <= quantity <= MAX_EXPERIMENTAL_QUANTITY):
        raise InventoryEditorError("target quantity must be an integer in 1..3")
    before, section, old_quantity = _active_item_area(raw)
    if quantity == old_quantity:
        return raw, {"status": "FAST LAB EXPERIMENTAL V0.22 INVENTORY EDIT",
                     "input_sha256": before.file_sha256,
                     "output_sha256": before.file_sha256,
                     "before_quantity": old_quantity, "after_quantity": quantity,
                     "diffs": [], "checksum": "unchanged; field is outside covered data",
                     "verifier_accepted": True}
    if _sha(raw) != SUPPORTED_INPUT_SHA256 or old_quantity != 2 or quantity != 3:
        raise InventoryEditorError("writes are bounded to the exact retained 2->3 Potion canary")

    absolute = section.physical_sector * v.SECTOR_SIZE + ITEM_OFFSET
    quantity_offset = absolute + 2
    output = bytearray(raw)
    struct.pack_into("<H", output, quantity_offset, quantity)
    candidate = bytes(output)
    after = v.verify_bytes(candidate)
    if _slot_profile(after) != _slot_profile(before):
        raise InventoryEditorError("edit changed slot or section metadata")
    _, after_section, decoded_quantity = _active_item_area(candidate)
    if decoded_quantity != quantity or after_section.checksum_stored != section.checksum_stored:
        raise InventoryEditorError("inventory edit did not preserve the verified checksum envelope")
    diffs = [(offset, left, right) for offset, (left, right)
             in enumerate(zip(raw, candidate)) if left != right]
    expected = quantity.to_bytes(2, "little")
    if diffs != [(quantity_offset, raw[quantity_offset], expected[0])]:
        raise InventoryEditorError("inventory edit changed bytes outside the quantity field")
    return candidate, {
        "status": "FAST LAB EXPERIMENTAL V0.22 INVENTORY EDIT",
        "input_sha256": before.file_sha256,
        "output_sha256": after.file_sha256,
        "active_slot": before.active_slot,
        "active_counter": before.slots[before.active_slot].counter,
        "section_id": ITEM_SECTION,
        "section_physical_sector": section.physical_sector,
        "section_relative_offset": ITEM_OFFSET,
        "absolute_quantity_offset": quantity_offset,
        "item_id": ITEM_ID_POTION,
        "slot": 0,
        "quantity": {"from": old_quantity, "to": quantity},
        "checksum": "unchanged; quantity field is in unchecked section-13 tail",
        "diffs": [{"offset": offset, "from": left, "to": right}
                  for offset, left, right in diffs],
        "verifier_accepted": True,
        "unchanged_outside_quantity": True,
    }


def write_new_file(path: str | Path, data: bytes) -> None:
    destination = Path(path).resolve(strict=False)
    if destination.exists():
        raise InventoryEditorError("refusing to overwrite existing output")
    if not destination.is_relative_to(PRIVATE_ROOT):
        raise InventoryEditorError("output must be inside PokemonStart-private")
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise InventoryEditorError("refusing to overwrite existing output") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def edit(input_save: str | Path, slot: int, item_id: int, quantity: int,
         output_path: str | Path, rom_path: str | Path = ROM_DEFAULT) -> dict[str, Any]:
    rom_hash = _check_rom(rom_path)
    source = _private_file(input_save, "input save", must_exist=True)
    destination = _private_file(output_path, "output save", must_exist=False)
    if destination == source or destination.exists():
        raise InventoryEditorError("output must be a new path; overwrite is refused")
    original = source.read_bytes()
    candidate, report = derive_bytes(original, slot, item_id, quantity)
    if candidate == original:
        raise InventoryEditorError("requested quantity is already present; no output created")
    write_new_file(destination, candidate)
    try:
        if _sha(source.read_bytes()) != report["input_sha256"]:
            raise InventoryEditorError("input changed during output creation")
        if _sha(destination.read_bytes()) != report["output_sha256"]:
            raise InventoryEditorError("output persistence verification failed")
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise
    report.update({"rom_sha256": rom_hash, "source_immutable": True,
                   "output_path": str(destination),
                   "evidence": ["exact-ROM capability profile", "exact-save offline",
                                "repository verifier", "Fast Lab experimental write"]})
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    view = sub.add_parser("inspect")
    view.add_argument("input_save", type=Path)
    view.add_argument("--rom", type=Path, default=ROM_DEFAULT)
    write = sub.add_parser("set-quantity")
    write.add_argument("input_save", type=Path)
    write.add_argument("output_save", type=Path)
    write.add_argument("--slot", type=int, required=True)
    write.add_argument("--item-id", type=int, required=True)
    write.add_argument("--quantity", type=int, required=True)
    write.add_argument("--rom", type=Path, default=ROM_DEFAULT)
    args = parser.parse_args()
    try:
        report = (inspect(args.input_save, args.rom) if args.action == "inspect" else
                  edit(args.input_save, args.slot, args.item_id, args.quantity,
                       args.output_save, args.rom))
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (OSError, ValueError, v.VerificationError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
