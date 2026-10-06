from __future__ import annotations

import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_mgba_harness as h
from tests.test_m5a_money_family import make_save


class ProtocolTests(unittest.TestCase):
    def test_framing_and_rejection(self):
        self.assertEqual(h.parse_line(b"ok\t123\n"), ("ok", "123"))
        self.assertEqual(h.encode_command("read8", (0x02000000,)), b"read8\t33554432\n")
        with self.assertRaisesRegex(h.HarnessError, "request too large"):
            h.encode_command("a" * 257, ())
        h.validate_reply("read_range", ("ok", "00ff"), (0x02000000, 2))
        with self.assertRaisesRegex(h.HarnessError, "malformed memory"):
            h.validate_reply("read_range", ("ok", "00zz"), (0x02000000, 2))
        for line in (b"ok", b"ok\r\n", b"x" * 1101 + b"\n", b"\xff\n", b"\x00\n"):
            with self.assertRaises(h.HarnessError):
                h.parse_line(line)

    def test_auth_failure(self):
        client, server = socket.socketpair()
        with tempfile.TemporaryDirectory() as directory:
            client.sendall(b"hello\twrong\n")
            with self.assertRaisesRegex(h.HarnessError, "authentication"):
                h.Bridge(server, "correct-token", Path(directory) / "audit.jsonl")
        client.close()

    def test_loopback_and_generated_path(self):
        for host in ("0.0.0.0", "::", "192.168.1.2", "localhost"):
            with self.assertRaises(h.HarnessError):
                h.require_loopback(host)
        with tempfile.TemporaryDirectory() as directory:
            script = h.render_bridge("127.0.0.1", 12345, "a" * 64,
                                     Path(directory) / "working.sav", Path(directory))
            self.assertIn("127.0.0.1", script)
            self.assertNotIn("@@TOKEN@@", script)
            with self.assertRaisesRegex(h.HarnessError, "inside repository"):
                h.render_bridge("127.0.0.1", 12345, "a" * 64,
                                h.REPO / "private.sav", Path(directory))
            with self.assertRaisesRegex(h.HarnessError, "host workspace"):
                h.prepare(Path(directory) / "outside.gba", Path(directory) / "outside.sav")

    def test_command_limits_and_write_allowlist(self):
        self.assertTrue(h.ram_range(0x0203FFFC, 4))
        self.assertTrue(h.ram_range(0x03007FFF, 1))
        self.assertFalse(h.ram_range(0x03007FFF, 2))
        for op, args in (("eval", ()), ("read_range", (0x02000000, 513)),
                         ("read_range", (0x0203FFFF, 2)),
                         ("read8", (0x08000000,)), ("write32", (0x08000000, 1)),
                         ("write8", (0x04000000, 1)),
                         ("write16", (0x05000000, 1)),
                         ("write32", (0x02000290, 1))):
            with self.subTest(op=op, args=args), self.assertRaises(h.HarnessError):
                h.validate_command(op, args, frozenset())
        allowed = frozenset(range(0x02000290, 0x02000294))
        with self.assertRaisesRegex(h.HarnessError, "money arm rejected"):
            h.validate_command("arm_money", (0x02000290, 123), frozenset())
        h.validate_command("arm_money", (0x02000290, 123), frozenset(), 0x02000290)
        with self.assertRaisesRegex(h.HarnessError, "money arm rejected"):
            h.validate_command("arm_money", (0x02000290, 123), frozenset(), 0x02000390)
        h.validate_command("write32", (0x02000290, 123), allowed)
        h.validate_command("write8", (0x02000293, 1), allowed)
        with self.assertRaises(h.HarnessError):
            h.validate_command("write16", (0x02000294, 1), allowed)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.memory = bytearray(0x40000)
        self.money = 1_234_567
        self.party = bytes(range(100))

    def test_synthetic_save_semantics(self):
        money, party_count, saved, party0 = h.save_money(make_save())
        self.assertEqual((money, party_count, saved, party0),
                         (1_234_567, 1, 3, bytes(range(100))))
        independent = h.independent_save_money(make_save())
        self.assertEqual((independent["active_slot"], independent["counter"],
                          independent["key"], independent["money"], independent["saved"]),
                         (1, 3, 0, 1_234_567, 3))
        with self.assertRaisesRegex(h.HarnessError, "zero encryption key"):
            h.save_money(make_save(key=1))

    def plant(self, base: int):
        self.memory[base + 0x290:base + 0x294] = self.money.to_bytes(4, "little")
        self.memory[base + 0x34] = 1
        self.memory[base + 0x38:base + 0x38 + 100] = self.party
        self.memory[base + 0x1200:base + 0x1204] = (3).to_bytes(4, "little")

    def test_unique_candidate(self):
        self.plant(0x10000)
        self.memory[0x20000:0x20004] = self.money.to_bytes(4, "little")
        self.assertEqual(h.discover_money(bytes(self.memory), self.money, 1, 3, self.party),
                         0x02010290)

    def test_ambiguity_and_absence_fail(self):
        with self.assertRaisesRegex(h.HarnessError, "0 supported"):
            h.discover_money(bytes(self.memory), self.money, 1, 3, self.party)
        self.plant(0x10000)
        self.plant(0x20000)
        with self.assertRaisesRegex(h.HarnessError, "2 supported"):
            h.discover_money(bytes(self.memory), self.money, 1, 3, self.party)


class MGBAMenuTests(unittest.TestCase):
    def test_scripting_view_uses_source_backed_menu_predicate(self):
        # No AX window count participates in this identity predicate.
        menus = ("Apple", "mGBA", "File")
        file_items = ("Load script...", "Load recent script", "Reset")
        self.assertTrue(h.scripting_view_predicate(menus, file_items))
        self.assertFalse(h.scripting_view_predicate(menus + ("Tools",), file_items))
        self.assertFalse(h.scripting_view_predicate(menus, ("Load script...",)))
        self.assertFalse(h.scripting_view_predicate(("Apple", "mGBA", "Tools"), file_items))

    def test_normal_readiness_requires_tools_scripting_item(self):
        menus = ("Apple", "mGBA", "File", "Tools")
        self.assertTrue(h.normal_mgba_predicate(menus, ("Scripting...", "Settings...")))
        self.assertFalse(h.normal_mgba_predicate(menus, ("Settings...",)))
        self.assertFalse(h.normal_mgba_predicate(("Apple", "mGBA", "File"), ("Scripting...",)))

    def test_stable_bridge_path_is_repo_external_and_atomic_content_is_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            save = Path(directory) / "working.sav"
            save.write_bytes(b"synthetic disposable save")
            stable = Path(directory) / "bootstrap" / "bridge-current.lua"
            with patch.object(h, "stable_bridge_path", return_value=stable):
                first = h.write_stable_bridge("127.0.0.1", 12345, "a" * 64, save, Path(directory))
                first_content = first.read_text()
                second = h.write_stable_bridge("127.0.0.1", 23456, "b" * 64, save, Path(directory))
            self.assertEqual(first, second)
            self.assertNotEqual(first_content, second.read_text())
            self.assertIn("23456", second.read_text())
            self.assertFalse(first.resolve().is_relative_to(h.REPO))

    def test_recent_script_path_must_be_exact_and_unique(self):
        path = Path("/tmp/bootstrap/bridge-current.lua")
        exact = str(path.resolve())
        self.assertTrue(h.exact_recent_script((exact,), path))
        self.assertFalse(h.exact_recent_script((exact + ".old",), path))
        self.assertFalse(h.exact_recent_script((exact, exact), path))


if __name__ == "__main__":
    unittest.main()
