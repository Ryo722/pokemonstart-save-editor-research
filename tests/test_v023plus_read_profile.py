"""Synthetic tests for the read-only save-layout families and exact read profiles.

No ROM or save bytes are used. Optional private checks run only when the
POKEMONSTART_V027_GATE_DIR / POKEMONSTART_V022_ROM / POKEMONSTART_V027_ROM
environment variables point at private local inputs outside Git.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import unittest

import pokemonstart_read_profiles as profiles
import pokemonstart_save_layouts as layouts
import pokemonstart_save_verifier as verifier
import pokemonstart_v022_inventory_model as inventory_model
import pokemonstart_v022_party_model as party_model

SECTOR = 0x1000
REPO = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVE_TABLE = (27,) + tuple(range(11, 27))
DEFAULT_INACTIVE_TABLE = tuple(range(10, 27))


def _party_record(species: int, level: int) -> bytes:
    record = bytearray(100)
    struct.pack_into("<H", record, 32, species)
    record[84] = level
    return bytes(record)


def _section_payload(section_id: int, counter: int, table, *, money=1234, key=0,
                     shel_magic=layouts.SHEL_MAGIC, shel_counter=None) -> bytearray:
    data = bytearray(0xFF0)
    for i in range(0, 0xFF0, 7):  # deterministic non-uniform filler
        data[i] = (section_id * 31 + i) & 0xFF
    if section_id == 0:
        struct.pack_into("<I", data, 0xF20, key)
    if section_id == 1:
        data[verifier.PARTY_COUNT_OFFSET] = 2
        data[verifier.PARTY_OFFSET:verifier.PARTY_OFFSET + 600] = b"\0" * 600
        data[verifier.PARTY_OFFSET:verifier.PARTY_OFFSET + 100] = _party_record(1, 5)
        data[verifier.PARTY_OFFSET + 100:verifier.PARTY_OFFSET + 200] = _party_record(25, 7)
        struct.pack_into("<I", data, 0x290, money ^ key)
    if section_id == 2 and table is not None:
        o = layouts.SHEL_SECTION_OFFSET
        struct.pack_into("<II", data, o, shel_magic, counter if shel_counter is None else shel_counter)
        data[o + 8:o + 8 + len(table)] = bytes(table)
    return data


def _seal(flash: bytearray, sector: int, ident: int, counter: int, payload: bytes, length: int) -> None:
    block = bytearray(SECTOR)
    block[:len(payload)] = payload
    struct.pack_into("<H", block, 0xFF4, ident)
    struct.pack_into("<H", block, 0xFF6, verifier.calculate_save_checksum(bytes(block[:length])))
    struct.pack_into("<II", block, 0xFF8, verifier.FILE_SIGNATURE, counter)
    flash[sector * SECTOR:(sector + 1) * SECTOR] = block


def _page_payload(page: int, version: int) -> bytes:
    data = bytearray(0xFF0)
    for i in range(0, 0xFF0, 5):
        data[i] = (page * 17 + version * 3 + i) & 0xFF
    if page == 15:  # zero pockets and menu counts so Inventory reads are simple
        data[:] = b"\0" * 0xFF0
    if page == 0:
        data[0x18B:0x18B + 0xBA0] = b"\0" * 0xBA0
    return bytes(data)


def build_v023(slots=None, pages=None, *, footer=True, **section_kwargs) -> bytearray:
    """slots: {slot_index: (counter, rotation, table)}; pages: {sector: (page, counter, version)}."""
    if slots is None:
        slots = {0: (12, 1, DEFAULT_ACTIVE_TABLE), 1: (11, 0, DEFAULT_INACTIVE_TABLE)}
    if pages is None:
        pages = {n: (n - 10, 11, 0) for n in range(10, 27)}
        pages[27] = (0, 12, 1)
    flash = bytearray(b"\xFF" * verifier.FLASH_SIZE)
    for slot, (counter, rotation, table) in slots.items():
        for sid in range(5):
            payload = _section_payload(sid, counter, table, **section_kwargs)
            sector = slot * 5 + (sid + rotation) % 5
            _seal(flash, sector, sid, counter, payload, verifier.SECTION_LENGTHS[sid])
    for sector, (page, counter, version) in pages.items():
        _seal(flash, sector, 0x40 + page, counter, _page_payload(page, version), 0xFF0)
    return flash + (b"\x01" * 16 if footer else b"")


def build_legacy() -> bytes:
    flash = bytearray(b"\xFF" * verifier.FLASH_SIZE)
    for slot, counter in ((0, 10), (1, 11)):
        for sid in range(14):
            payload = _section_payload(sid, counter, None) if sid < 5 else bytearray(
                ((sid * 13 + i) & 0xFF) for i in range(0xFF0))
            sector = slot * 14 + (sid + slot * 3) % 14
            _seal(flash, sector, sid, counter, payload, verifier.SECTION_LENGTHS[sid])
    flash[30 * SECTOR:31 * SECTOR] = b"\0" * SECTOR
    flash[31 * SECTOR:32 * SECTOR] = b"\0" * SECTOR
    return bytes(flash) + b"\x02" * 16


def resign_page(raw: bytearray, sector: int) -> None:
    block = raw[sector * SECTOR:(sector + 1) * SECTOR]
    struct.pack_into("<H", raw, sector * SECTOR + 0xFF6, verifier.calculate_save_checksum(bytes(block[:0xFF0])))


class V023PlusAcceptanceTests(unittest.TestCase):
    def test_copy_on_write_state_with_mixed_page_counters(self):
        view = layouts.detect(bytes(build_v023()))
        self.assertEqual(view.layout, layouts.V023PLUS)
        self.assertEqual((view.active_slot, view.counter, view.shel_counter), (0, 12, 12))
        self.assertEqual(view.rotations, (1, 0))
        self.assertEqual(view.page_table, DEFAULT_ACTIVE_TABLE)
        self.assertEqual(sorted({p.counter for p in view.pages}), [11, 12])
        self.assertEqual(view.pages[0].physical_sector, 27)
        self.assertEqual([m.species for m in view.party()], [1, 25])
        self.assertEqual(view.money(), (0, 1234))
        self.assertTrue(all(f.epoch_authenticated for f in view.fragments))
        self.assertEqual(view.ram(0x0203BFAC, 4), b"\0\0\0\0")
        self.assertEqual(view.ram(0x0203B40C + 0xBA0 - 4, 4), b"\0\0\0\0")
        with self.assertRaises(layouts.LayoutError):
            view.ram(0x0203BFAC + 0xFF0 - 2, 4)

    def test_migrated_single_slot_state(self):
        raw = build_v023({1: (11, 0, DEFAULT_INACTIVE_TABLE)}, {n: (n - 10, 11, 0) for n in range(10, 27)})
        view = layouts.detect(bytes(raw))
        self.assertEqual((view.active_slot, view.slots[0].state, view.inactive_page_table), (1, "empty", None))
        self.assertEqual(view.rotations, (None, 0))

    def test_steady_state_shared_tables_and_second_slot(self):
        raw = build_v023({0: (12, 1, DEFAULT_ACTIVE_TABLE), 1: (13, 2, DEFAULT_ACTIVE_TABLE)})
        view = layouts.detect(bytes(raw))
        self.assertEqual((view.active_slot, view.counter, view.rotations), (1, 13, (1, 2)))
        self.assertEqual(view.inactive_page_table, view.page_table)

    def test_footer_optional_and_size_checked(self):
        self.assertEqual(layouts.detect(bytes(build_v023(footer=False))).footer, b"")
        with self.assertRaises(layouts.LayoutError):
            layouts.detect(bytes(build_v023())[:-1])


class V023PlusFailClosedTests(unittest.TestCase):
    def assertRejected(self, raw, fragment=None):
        with self.assertRaises(layouts.LayoutError) as ctx:
            layouts.detect(bytes(raw))
        if fragment:
            self.assertIn(fragment, str(ctx.exception))
        with self.assertRaises(layouts.LayoutError):
            layouts.parse_v023plus(bytes(raw))

    def test_missing_shel_magic(self):
        self.assertRejected(build_v023(shel_magic=0x12345678), "without SHEL magic")

    def test_shel_counter_differs_from_slot(self):
        self.assertRejected(build_v023(shel_counter=99), "SHEL counter differs")

    def test_duplicate_logical_section(self):
        raw = build_v023()
        sector1 = bytes(raw[1 * SECTOR:2 * SECTOR])  # slot 0 rotation 1 holds section 0 at sector 1
        raw[2 * SECTOR:3 * SECTOR] = sector1
        # Any duplicate breaks the bijective rotation before the id-set check.
        self.assertRejected(raw, "duplicate, missing or permuted")

    def test_missing_logical_section(self):
        raw = build_v023()
        payload = bytes(raw[3 * SECTOR:3 * SECTOR + 0xFF0])
        _seal(raw, 3, 7, 12, payload, verifier.SECTION_LENGTHS[2])
        self.assertRejected(raw, "unsupported section id")

    def test_mixed_slot_counters(self):
        raw = build_v023()
        struct.pack_into("<I", raw, 4 * SECTOR + 0xFFC, 13)
        self.assertRejected(raw, "mixed section counters")

    def test_equal_counter_ambiguity(self):
        raw = build_v023({0: (12, 1, DEFAULT_ACTIVE_TABLE), 1: (12, 0, DEFAULT_ACTIVE_TABLE)})
        self.assertRejected(raw, "equal counters")

    def test_non_cyclic_section_placement(self):
        raw = build_v023()
        a, b = bytes(raw[0:SECTOR]), bytes(raw[1 * SECTOR:2 * SECTOR])
        raw[0:SECTOR], raw[1 * SECTOR:2 * SECTOR] = b, a
        self.assertRejected(raw, "cyclic rotation")

    def test_partially_erased_slot(self):
        raw = build_v023()
        raw[2 * SECTOR:3 * SECTOR] = b"\xFF" * SECTOR
        self.assertRejected(raw, "partially erased")

    def test_page_sector_index_out_of_range(self):
        for bad in (5, 9, 32, 0xFF):
            table = (bad,) + DEFAULT_ACTIVE_TABLE[1:]
            self.assertRejected(build_v023({0: (12, 1, table), 1: (11, 0, DEFAULT_INACTIVE_TABLE)}), "out of range")

    def test_uninitialised_native_table_unqualified(self):
        table = (0xFF,) * 17
        self.assertRejected(build_v023({0: (12, 1, table), 1: (11, 0, DEFAULT_INACTIVE_TABLE)}))

    def test_duplicate_page_sector_mapping(self):
        table = (27, 27) + DEFAULT_ACTIVE_TABLE[2:]
        self.assertRejected(build_v023({0: (12, 1, table), 1: (11, 0, DEFAULT_INACTIVE_TABLE)}), "duplicate page-sector")

    def test_missing_page(self):
        raw = build_v023()
        raw[27 * SECTOR:28 * SECTOR] = b"\xFF" * SECTOR
        self.assertRejected(raw, "missing")

    def test_wrong_page_id(self):
        raw = build_v023()
        struct.pack_into("<H", raw, 15 * SECTOR + 0xFF4, 0x4F)
        resign_page(raw, 15)
        self.assertRejected(raw, "wrong page id")

    def test_invalid_page_checksum(self):
        raw = build_v023()
        raw[20 * SECTOR + 3] ^= 0x01
        self.assertRejected(raw, "checksum mismatch")

    def test_invalid_page_signature(self):
        raw = build_v023()
        struct.pack_into("<I", raw, 20 * SECTOR + 0xFF8, 0)
        self.assertRejected(raw, "invalid signature")

    def test_page_newer_than_owning_slot(self):
        pages = {n: (n - 10, 11, 0) for n in range(10, 27)}
        pages[27] = (0, 14, 1)
        self.assertRejected(build_v023(pages=pages), "newer than its slot")

    def test_inactive_slot_page_overwritten_after_it(self):
        # Inactive (counter 11) still references sector 10 for page 0, but the
        # sector now carries a counter-12 write: ownership is ambiguous.
        pages = {n: (n - 10, 11, 0) for n in range(11, 27)}
        pages[10] = (0, 12, 1)
        pages[27] = (0, 12, 1)
        self.assertRejected(build_v023(pages=pages), "newer than its slot")

    def test_sector_shared_by_different_pages_across_slots(self):
        inactive = (10,) + tuple(range(11, 26)) + (27,)  # page 16 -> sector 27
        pages = {n: (n - 10, 11, 0) for n in range(10, 27)}
        pages[27] = (0, 12, 1)
        raw = build_v023({0: (12, 1, DEFAULT_ACTIVE_TABLE), 1: (11, 0, inactive)}, pages)
        # A sector carries one page id, so per-slot validation catches sharing.
        self.assertRejected(raw, "wrong page id")

    def test_counter_wrap_unqualified(self):
        raw = build_v023({0: (0x7FFFFFFF, 1, DEFAULT_ACTIVE_TABLE), 1: (0x7FFFFFFE, 0, DEFAULT_INACTIVE_TABLE)},
                         {**{n: (n - 10, 11, 0) for n in range(10, 27)}, 27: (0, 12, 1)})
        self.assertRejected(raw, "counter wrap")

    def test_unknown_layout(self):
        self.assertRejected(b"\xFF" * verifier.FLASH_SIZE, "unknown layout")
        self.assertRejected(b"\0" * (verifier.FLASH_SIZE + 16), "unknown layout")


class LegacyRegressionTests(unittest.TestCase):
    def test_legacy_view_is_the_canonical_verifier_result(self):
        raw = build_legacy()
        canonical = verifier.verify_bytes(raw)
        view = layouts.detect(raw)
        self.assertEqual(view.layout, layouts.LEGACY)
        self.assertEqual(view.legacy_result, canonical)
        self.assertEqual((view.active_slot, view.counter), (canonical.active_slot, 11))
        self.assertEqual(view.party(), canonical.party)
        self.assertEqual([f.epoch_authenticated for f in view.fragments], [True, True, True, False, False])
        with self.assertRaises(layouts.LayoutError):
            layouts.parse_v023plus(raw)
        with self.assertRaises(layouts.LayoutError):
            layouts.parse_legacy(bytes(build_v023()))

    def test_legacy_fragment_mapping_matches_canonical_inventory_offsets(self):
        raw = build_legacy()
        view = layouts.detect(raw)
        active = view.active
        for _, ram, capacity, _ in inventory_model.POCKETS:
            for slot in (0, capacity - 1):
                address = ram + 4 * slot
                offset = inventory_model.record_offset(active, address)
                self.assertEqual(view.ram(address, 4), raw[offset:offset + 4])
        self.assertEqual(view.ram(profiles.MENU_COUNTS_RAM, 6), raw[0x1E716:0x1E71C])

    def test_canonical_verifier_still_rejects_v023plus(self):
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_bytes(bytes(build_v023()))


class ProfileTests(unittest.TestCase):
    def test_v022_profile_mirrors_canonical_constants(self):
        offsets = profiles.V022_EXACT.table_offsets
        self.assertEqual(profiles.V022_EXACT.rom_sha256, party_model.ROM_SHA256)
        self.assertEqual(profiles.V022_EXACT.rom_sha256, inventory_model.ROM_SHA256)
        self.assertEqual(offsets["species"], party_model.SPECIES_TABLE)
        self.assertEqual(offsets["species_names"], party_model.SPECIES_NAMES)
        self.assertEqual(offsets["moves"], party_model.MOVE_TABLE)
        self.assertEqual(offsets["move_names"], party_model.MOVE_NAMES)
        self.assertEqual(offsets["experience"], party_model.EXP_TABLE)
        self.assertEqual(offsets["nature"], party_model.NATURE_TABLE)
        self.assertEqual(offsets["items"], inventory_model.ITEM_TABLE - inventory_model.ROM_BASE)
        self.assertEqual(offsets["pocket_descriptor"], inventory_model.DESCRIPTOR - inventory_model.ROM_BASE)
        self.assertEqual(tuple((n, r, c) for n, r, c, _ in inventory_model.POCKETS), profiles.POCKETS)

    def test_semantic_hashes_are_canonical_evidence(self):
        evidence = "".join((REPO / "docs" / name).read_text(encoding="utf-8") for name in (
            "e1-inventory-private-evidence.json", "e3-existing-party-readonly-evidence.json"))
        for table in profiles.SEMANTIC_TABLES:
            if table.normalization == "raw":
                self.assertIn(table.sha256, evidence, table.name)

    def test_no_profile_grants_write_authority(self):
        self.assertEqual(profiles.V027_EXACT.capabilities["write_mechanics"], "NOT QUALIFIED")
        self.assertIn("NOT GRANTED", profiles.V022_EXACT.capabilities["write_mechanics"])
        report = profiles.read_save(profiles.V027_EXACT, bytes(build_v023()))
        self.assertFalse(report["write_authorized"])
        for module in (layouts, profiles):
            source = Path(module.__file__).read_text(encoding="utf-8")
            for token in ("write_bytes", "write_text", "'wb'", '"wb"', "'xb'", '"xb"', "'ab'", '"ab"'):
                self.assertNotIn(token, source)

    def test_v027_read_and_sanitized_output(self):
        report = profiles.read_save(profiles.V027_EXACT, bytes(build_v023()))
        self.assertEqual((report["counter"], report["party_count"]), (12, 2))
        self.assertEqual(report["money"], {"key_is_zero": True, "qualified": True, "value": 1234})
        self.assertEqual(report["inventory"]["menu_counts"], [0, 0, 0])
        clean = json.dumps(profiles.sanitized(report))
        self.assertNotIn("1234", clean)
        self.assertNotIn('"species"', clean)

    def test_nonzero_key_money_and_inventory_unqualified(self):
        report = profiles.read_save(profiles.V027_EXACT, bytes(build_v023(key=0x1234ABCD)))
        self.assertEqual(report["money"], {"key_is_zero": False, "qualified": False, "value": None})
        self.assertIsNone(report["inventory"])

    def test_profile_layout_mismatch_rejected(self):
        with self.assertRaises(profiles.ProfileError):
            profiles.read_save(profiles.V027_EXACT, build_legacy())
        with self.assertRaises(profiles.ProfileError):
            profiles.read_save(profiles.V022_EXACT, bytes(build_v023()))

    def test_v027_requires_native_slot_parity(self):
        raw = build_v023({0: (13, 1, DEFAULT_ACTIVE_TABLE), 1: (12, 0, DEFAULT_INACTIVE_TABLE)},
                         {**{n: (n - 10, 11, 0) for n in range(10, 27)}, 27: (0, 12, 1)})
        layouts.detect(bytes(raw))  # structurally valid family member
        with self.assertRaises(profiles.ProfileError):
            profiles.read_save(profiles.V027_EXACT, bytes(raw))

    def test_rom_identity_gates(self):
        with self.assertRaises(profiles.ProfileError):
            profiles.verify_rom(profiles.V027_EXACT, b"\0" * 16)
        with self.assertRaises(profiles.ProfileError):
            profiles.verify_rom(profiles.V027_EXACT, b"\0" * profiles.V027_EXACT.rom_size)


GATE = {"S0": "b153720a8180c1635bac2a86fb75460c9f34430ea8589df8f29afa46692026b2",
        "M": "f4df12ccd85df5a0325fcca9398c74a6685076704703c0e66b827cf6b10d441c",
        "R1": "325e355f1726dea64c13f454975f2b5246f70e0e59ed2b77f7b3e9e0c4d099d3",
        "R2": "68e18ae410bb63eb9c5c4de9fea51e24cf8a953ac6d858637d381893f01467e9"}


@unittest.skipUnless(os.environ.get("POKEMONSTART_V027_GATE_DIR"), "private v0.27 gate saves not provided")
class PrivateGateTests(unittest.TestCase):
    def load(self, name):
        raw = (Path(os.environ["POKEMONSTART_V027_GATE_DIR"]) / f"{name}.sav").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), GATE[name])
        return raw

    def test_gate_sequence(self):
        s0 = profiles.read_save(profiles.V022_EXACT, self.load("S0"))
        seen = [(s0["layout"], s0["active_slot"], s0["counter"])]
        expected_tables = {"M": tuple(range(10, 27)), "R1": DEFAULT_ACTIVE_TABLE, "R2": DEFAULT_ACTIVE_TABLE}
        for name in ("M", "R1", "R2"):
            report = profiles.read_save(profiles.V027_EXACT, self.load(name))
            seen.append((report["layout"], report["active_slot"], report["counter"]))
            self.assertEqual(tuple(report["shel"]["page_table"]), expected_tables[name])
            self.assertEqual(report["party"], s0["party"])
            self.assertEqual(report["money"], s0["money"])
            self.assertEqual(report["inventory"], s0["inventory"])
        self.assertEqual(seen, [(layouts.LEGACY, 1, 11), (layouts.V023PLUS, 1, 11),
                                (layouts.V023PLUS, 0, 12), (layouts.V023PLUS, 1, 13)])


@unittest.skipUnless(os.environ.get("POKEMONSTART_V027_ROM") and os.environ.get("POKEMONSTART_V022_ROM"),
                     "private ROMs not provided")
class PrivateRomTests(unittest.TestCase):
    def test_both_builds_reproduce_the_semantic_model(self):
        for profile, env in ((profiles.V022_EXACT, "POKEMONSTART_V022_ROM"), (profiles.V027_EXACT, "POKEMONSTART_V027_ROM")):
            report = profiles.verify_rom(profile, Path(os.environ[env]).read_bytes())
            self.assertEqual(len(report["tables"]), len(profiles.SEMANTIC_TABLES))


if __name__ == "__main__":
    unittest.main()
