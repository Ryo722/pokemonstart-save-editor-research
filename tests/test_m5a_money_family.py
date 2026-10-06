from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m5a_money_family as f
import pokemonstart_save_verifier as v
from tests.m5a_independent_money_family_audit import audit_editor_pair, audit_game_return


def _sector(section_id, counter, payload, tail=None):
    raw = bytearray(0x1000)
    raw[: len(payload)] = payload
    if tail:
        for offset, value in tail.items():
            raw[offset] = value
    struct.pack_into("<H", raw, 0xFF4, section_id)
    struct.pack_into(
        "<H",
        raw,
        0xFF6,
        v.calculate_save_checksum(bytes(raw[: v.SECTION_LENGTHS[section_id]])),
    )
    struct.pack_into("<I", raw, 0xFF8, v.FILE_SIGNATURE)
    struct.pack_into("<I", raw, 0xFFC, counter)
    return bytes(raw)


def _payloads(money=1_234_567, key=0, play=159, saved=3):
    result = []
    for section_id in range(14):
        payload = bytearray(v.SECTION_LENGTHS[section_id])
        if section_id == 0:
            hours, rem = divmod(play, 3600)
            minutes, seconds = divmod(rem, 60)
            struct.pack_into("<H", payload, 0x0E, hours)
            payload[0x10] = minutes
            payload[0x11] = seconds
            struct.pack_into("<I", payload, 0xF20, key)
        if section_id == 1:
            payload[v.PARTY_COUNT_OFFSET] = 1
            payload[v.PARTY_OFFSET : v.PARTY_OFFSET + v.POKEMON_SIZE] = bytes(
                range(v.POKEMON_SIZE)
            )
            struct.pack_into("<I", payload, 0x290, money ^ key)
        if section_id == 2:
            struct.pack_into("<I", payload, 0x210, saved)
        result.append(bytes(payload))
    return result


def make_save(money=1_234_567, key=0, active_slot=1, counter=3):
    permutation = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 1, 2]
    active_payloads = _payloads(money, key, 159, 3)
    inactive_payloads = _payloads(money, key, 151, 2)
    active = [
        _sector(
            section_id,
            counter,
            active_payloads[section_id],
            {0xEDE: 0x55, 0xEDF: 0x30, 0xEE8: 0x5C, 0xEE9: 0x98}
            if section_id == 4
            else None,
        )
        for section_id in range(14)
    ]
    inactive = [
        _sector(
            section_id,
            counter - 1,
            inactive_payloads[section_id],
            {0xEDE: 0xE1, 0xEDF: 0x2D, 0xEE8: 0xF8, 0xEE9: 0xCC}
            if section_id == 4
            else None,
        )
        for section_id in range(14)
    ]
    slots = []
    for slot in (0, 1):
        source = active if slot == active_slot else inactive
        if slot == active_slot:
            physical = [None] * 14
            for section_id, position in enumerate(permutation):
                physical[position] = source[section_id]
        else:
            physical = source[:]
        slots.append(b"".join(physical))
    return slots[0] + slots[1] + bytes(0x4000) + b"0123456789ABCDEF"


def make_game_return(parent: bytes, *, bad_tail=False, template_change=False, money_change=False):
    result = v.verify_bytes(parent)
    parent_active = result.slots[result.active_slot]
    new_slot = 1 - result.active_slot
    new_counter = (parent_active.counter + 1) & 0xFFFFFFFF
    logical = {
        section.section_id: bytearray(
            parent[
                section.physical_sector * 0x1000 : (section.physical_sector + 1) * 0x1000
            ]
        )
        for section in parent_active.sections
    }
    logical[0][0x11] = (logical[0][0x11] + 1) % 60
    logical[1][0x6FA] ^= 1
    logical[1][0x708] ^= 1
    saved = int.from_bytes(logical[2][0x210:0x214], "little")
    struct.pack_into("<I", logical[2], 0x210, saved + 1)
    for offset, value in ((0xEDE, 0x11), (0xEDF, 0x22), (0xEE8, 0x33), (0xEE9, 0x44)):
        logical[4][offset] ^= value
    if bad_tail:
        logical[4][0xEDA] ^= 1
    if template_change:
        logical[1][0x9E0] ^= 1
    if money_change:
        logical[1][0x290] ^= 1
    for section_id, raw in logical.items():
        struct.pack_into("<H", raw, 0xFF4, section_id)
        struct.pack_into("<I", raw, 0xFF8, v.FILE_SIGNATURE)
        struct.pack_into("<I", raw, 0xFFC, new_counter)
        struct.pack_into(
            "<H",
            raw,
            0xFF6,
            v.calculate_save_checksum(bytes(raw[: v.SECTION_LENGTHS[section_id]])),
        )
    parent_perm = [
        section.physical_sector % 14 for section in parent_active.sections
    ]
    new_perm = [(position + 1) % 14 for position in parent_perm]
    physical = [None] * 14
    for section_id, position in enumerate(new_perm):
        physical[position] = bytes(logical[section_id])
    output = bytearray(parent)
    base = new_slot * 14 * 0x1000
    output[base : base + 14 * 0x1000] = b"".join(physical)
    output[-16:] = b"FEDCBA9876543210"
    return bytes(output)


class MoneyFamilyTests(unittest.TestCase):
    def setUp(self):
        self.raw = make_save()
        self.root_hash = hashlib.sha256(self.raw).hexdigest()
        self.rom = b"synthetic-build"
        self.build_hash = hashlib.sha256(self.rom).hexdigest()
        self.patches = (
            patch.object(f, "FAMILY_ROOT_SHA256", self.root_hash),
            patch.object(f, "EXPECTED_BUILD_SHA256", self.build_hash),
        )
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

    def bootstrap(self, directory):
        root = Path(directory) / "root.sav"
        root.write_bytes(self.raw)
        rom = Path(directory) / "game.gba"
        rom.write_bytes(self.rom)
        journal = Path(directory) / "journal.json"
        f.bootstrap_journal(root, journal, rom, f.SUPPORTED_ENVIRONMENT_ID)
        return root, rom, journal, json.loads(journal.read_text())

    def test_bootstrap_inspect_and_unjournaled_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, journal = self.bootstrap(directory)
            accepted = f.inspect(
                self.raw, journal, self.build_hash, f.SUPPORTED_ENVIRONMENT_ID
            )
            self.assertTrue(accepted["eligible"])
            self.assertEqual(accepted["money"], 1_234_567)
            other = make_save(money=123)
            self.assertFalse(
                f.inspect(other, journal, self.build_hash, f.SUPPORTED_ENVIRONMENT_ID)[
                    "eligible"
                ]
            )

    def test_build_environment_and_key_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, journal = self.bootstrap(directory)
            self.assertFalse(
                f.inspect(self.raw, journal, "0" * 64, f.SUPPORTED_ENVIRONMENT_ID)[
                    "eligible"
                ]
            )
            self.assertFalse(
                f.inspect(self.raw, journal, self.build_hash, "other")["eligible"]
            )
        keyed = make_save(key=0x12345678)
        with self.assertRaisesRegex(f.MoneyFamilyError, "encryption key"):
            f._derive(keyed, 100)

    def test_zero_mid_max_and_independent_editor_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, journal = self.bootstrap(directory)
            for target in (0, 7_654_321, 9_999_999):
                plan = f.preview(
                    self.raw,
                    journal,
                    self.build_hash,
                    f.SUPPORTED_ENVIRONMENT_ID,
                    target,
                )
                output, _, _ = f._derive(self.raw, target)
                receipt = f.audit_editor_output(self.raw, output, plan)
                self.assertEqual(receipt.after_money, target)
                audit_editor_pair(self.raw, output, target)

    def test_invalid_noop_and_corrupt_save_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, journal = self.bootstrap(directory)
            for target in (-1, 10_000_000, True):
                with self.assertRaises(f.MoneyFamilyError):
                    f.preview(
                        self.raw,
                        journal,
                        self.build_hash,
                        f.SUPPORTED_ENVIRONMENT_ID,
                        target,
                    )
            with self.assertRaisesRegex(f.MoneyFamilyError, "equals current"):
                f.preview(
                    self.raw,
                    journal,
                    self.build_hash,
                    f.SUPPORTED_ENVIRONMENT_ID,
                    1_234_567,
                )
        bad = bytearray(self.raw)
        result = v.verify_bytes(self.raw)
        section = result.slots[result.active_slot].section(1)
        bad[section.physical_sector * 0x1000 + 0x290] ^= 1
        with self.assertRaisesRegex(f.MoneyFamilyError, "S0 rejected"):
            f._derive(bytes(bad), 0)

    def test_stale_plan_and_publication_safety(self):
        with tempfile.TemporaryDirectory() as directory:
            root, rom, journal_path, journal = self.bootstrap(directory)
            plan = f.preview(
                self.raw,
                journal,
                self.build_hash,
                f.SUPPORTED_ENVIRONMENT_ID,
                321,
            )
            stale = f.MoneyPlan(
                plan.source_sha256, 322, plan.output_sha256, plan.diffs
            )
            with patch.object(f.sys, "platform", "darwin"):
                with self.assertRaisesRegex(f.MoneyFamilyError, "stale"):
                    f.commit(
                        root,
                        Path(directory) / "stale.sav",
                        journal_path,
                        rom,
                        f.SUPPORTED_ENVIRONMENT_ID,
                        stale,
                    )
                output = Path(directory) / "out.sav"
                before = root.read_bytes()
                f.commit(
                    root,
                    output,
                    journal_path,
                    rom,
                    f.SUPPORTED_ENVIRONMENT_ID,
                    plan,
                )
                self.assertEqual(root.read_bytes(), before)
                with self.assertRaises(f.MoneyFamilyError):
                    f.commit(
                        root,
                        output,
                        journal_path,
                        rom,
                        f.SUPPORTED_ENVIRONMENT_ID,
                        plan,
                    )

    def test_valid_game_return_and_independent_audit(self):
        output, _, _ = f._derive(self.raw, 7_654_321)
        parent = f.fingerprint(output, v.verify_bytes(output))
        returned = make_game_return(output)
        self.assertIsNone(
            f.check_game_return(parent, returned, v.verify_bytes(returned))
        )
        audit_game_return(output, returned)

    def test_game_return_negative_envelope(self):
        output, _, _ = f._derive(self.raw, 7_654_321)
        parent = f.fingerprint(output, v.verify_bytes(output))
        for returned, expected in (
            (make_game_return(output, bad_tail=True), "tail changed outside"),
            (make_game_return(output, template_change=True), "payload changed outside"),
            (make_game_return(output, money_change=True), "money changed"),
        ):
            reason = f.check_game_return(parent, returned, v.verify_bytes(returned))
            self.assertIn(expected, reason)

    def test_footer_change_allowed_only_on_game_return(self):
        output, _, _ = f._derive(self.raw, 7_654_321)
        self.assertEqual(v.verify_bytes(self.raw).footer, v.verify_bytes(output).footer)
        parent = f.fingerprint(output, v.verify_bytes(output))
        returned = make_game_return(output)
        self.assertNotEqual(v.verify_bytes(output).footer, v.verify_bytes(returned).footer)
        self.assertIsNone(
            f.check_game_return(parent, returned, v.verify_bytes(returned))
        )


if __name__ == "__main__":
    unittest.main()
