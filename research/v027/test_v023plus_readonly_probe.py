"""Synthetic-only tests for the v0.23+ read-only probe.

No private save, ROM or upstream package content is used. Fixtures are built
in memory from the documented layouts (exact-v0.22 14-section slots; v0.23+
5-section slots plus SHEL-indexed Box pages) with pseudo-random synthetic
bytes. Run: python3 -m unittest discover -s research/v027 -v
"""
import os
import random
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pokemonstart_v023plus_readonly_probe as P  # noqa: E402

SIZES = P.SIZES
SB1_OFFSETS = (None, 0, 0xFF0, 0xFF0 * 2, 0xFF0 * 3)
STORAGE_OFFSETS = {5 + i: 0xFF0 * i for i in range(8)} | {13: 0x7F80}
PARASITE = {0: 0xCC, 4: 0x258, 13: 0xBA0}


def put16(b, o, v): struct.pack_into("<H", b, o, v)
def put32(b, o, v): struct.pack_into("<I", b, o, v)


def seal(sec, sid, counter, length):
    put16(sec, 0xFF4, sid)
    put16(sec, 0xFF6, P.checksum(bytes(sec), length))
    put32(sec, 0xFF8, P.SIG)
    put32(sec, 0xFFC, counter)
    return sec


def content(seed=7, party_count=2, money=123456, key=0):
    rnd = random.Random(seed)
    rb = lambda n: bytes(rnd.getrandbits(8) for _ in range(n))
    sb2 = bytearray(rb(0xF24)); put32(sb2, P.KEY, key)
    sb1 = bytearray(0x3D98); sb1[P.PARTY_COUNT] = party_count
    for i in range(party_count):
        rec = bytearray(rb(100)); put16(rec, 32, 1 + i); rec[84] = 5 + i
        sb1[P.PARTY + 100 * i:P.PARTY + 100 * (i + 1)] = rec
    put32(sb1, P.MONEY, money ^ key)
    storage = bytearray(0x83D0)  # 4-byte header + 19 boxes x 30 x 58 + tail
    for i in range(19 * 30):
        if rnd.random() < 0.1:
            o = 4 + i * P.MON
            storage[o:o + P.MON] = rb(P.MON); put16(storage, o + 0x1C, rnd.randrange(1, 400))
    parasite = {0: rb(0xCC), 4: rb(0x258), 13: bytearray(0xBA0)}
    struct.pack_into("<HHHH", parasite[13], 0x68C, 13, 5, 14, 2)  # regular pocket
    s30 = bytearray(P.DATA); s30[0xF00:0xF10] = bytes(range(16))
    struct.pack_into("<3H", s30, 0x716, 2, 0, 0)  # menu counts
    s31 = bytearray(P.DATA)
    return dict(sb2=bytes(sb2), sb1=bytes(sb1), storage=bytes(storage),
                parasite=parasite, s30=bytes(s30), s31=bytes(s31))


def section_payload(c, sid):
    if sid == 0:
        return c["sb2"]
    if sid < 5:
        return c["sb1"][SB1_OFFSETS[sid]:SB1_OFFSETS[sid] + SIZES[sid]]
    return c["storage"][STORAGE_OFFSETS[sid]:STORAGE_OFFSETS[sid] + SIZES[sid]]


def build_legacy(c, counters=(1, 2), footer=bytes(range(16))):
    flash = bytearray(b"\xff" * P.FLASH)
    for slot, cnt in enumerate(counters):
        for sid in range(14):
            sec = bytearray(P.SECTOR)
            payload = section_payload(c, sid); sec[:len(payload)] = payload
            if sid in PARASITE:
                sec[P.DATA - PARASITE[sid]:P.DATA] = c["parasite"][sid]
            n = slot * 14 + (sid + cnt) % 14  # rotated like vanilla slots
            flash[n * P.SECTOR:(n + 1) * P.SECTOR] = seal(sec, sid, cnt, SIZES[sid])
    flash[30 * P.SECTOR:30 * P.SECTOR + P.DATA] = c["s30"]
    flash[31 * P.SECTOR:31 * P.SECTOR + P.DATA] = c["s31"]
    return bytes(flash) + footer


def build_modern(c, counter=2, table=tuple(range(10, 27)), footer=bytes(range(16))):
    """v0.23+ layout per the documented page map (see the reconnaissance doc)."""
    flash = bytearray(b"\xff" * P.FLASH)
    sb1 = bytearray(c["sb1"])
    put32(sb1, P.SHEL_SB1_OFFSET, P.SHEL_MAGIC); put32(sb1, P.SHEL_SB1_OFFSET + 4, counter)
    sb1[P.SHEL_SB1_OFFSET + 8:P.SHEL_SB1_OFFSET + 8 + P.PAGE_COUNT] = bytes(table)
    base = 5 * (counter % 2)
    for sid in range(5):
        sec = bytearray(P.SECTOR)
        payload = c["sb2"] if sid == 0 else sb1[SB1_OFFSETS[sid]:SB1_OFFSETS[sid] + SIZES[sid]]
        sec[:len(payload)] = payload
        if sid in (0, 4):
            sec[P.DATA - PARASITE[sid]:P.DATA] = c["parasite"][sid]
        flash[(base + sid) * P.SECTOR:(base + sid + 1) * P.SECTOR] = seal(sec, sid, counter, SIZES[sid])
    stream = bytearray(33 * 30 * P.MON); stream[:19 * 30 * P.MON] = c["storage"][4:4 + 19 * 30 * P.MON]
    pages = []
    p0 = bytearray(P.DATA)
    p0[0:4] = c["storage"][0:4]
    p0[4:4 + 0x98] = c["storage"][0x8128:0x81C0]
    p0[0x9C:0x9C + 0xEF] = c["storage"][0x82E1:0x83D0]
    p0[P.P0_PARASITE:P.P0_PARASITE + 0xBA0] = c["parasite"][13]
    p0[P.P0_MONS:P.P0_MONS + P.PAGE0_MONS * P.MON] = stream[:P.PAGE0_MONS * P.MON]
    pages.append(p0)
    for p in range(1, P.BOX_PAGES):
        g = P.PAGE0_MONS + (p - 1) * P.PAGE_MONS
        chunk = stream[g * P.MON:(g + P.PAGE_MONS) * P.MON]
        pg = bytearray(P.DATA); pg[:len(chunk)] = chunk; pages.append(pg)
    pages += [bytearray(c["s30"]), bytearray(c["s31"])]
    for p, n in enumerate(table):
        sec = bytearray(P.SECTOR); sec[:P.DATA] = pages[p]
        flash[n * P.SECTOR:(n + 1) * P.SECTOR] = seal(sec, P.PAGE_FIRST_ID + p, counter, P.DATA)
    return bytes(flash) + footer


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.c = content()
        self.legacy = build_legacy(self.c)
        self.modern = build_modern(self.c)

    def test_legacy_detected(self):
        r = P.probe(self.legacy)
        self.assertEqual(r["layout"], "legacy_14_section")
        self.assertEqual(r["active_counter"], 2)
        self.assertEqual(r["party"]["count"], 2)
        self.assertEqual(r["money"]["decoded"], 123456)
        self.assertEqual(r["inventory"]["pockets"]["regular"]["occupied"], 2)
        self.assertEqual(r["inventory"]["menu_counts"], [2, 0, 0])

    def test_modern_detected_and_equivalent(self):
        a, b = P.probe(self.legacy), P.probe(self.modern)
        self.assertEqual(b["layout"], "v023plus_5_section")
        self.assertTrue(b["shel"]["magic_ok"])
        self.assertTrue(b["shel"]["table_is_10_to_26"])
        self.assertTrue(b["box_pages_all_valid"])
        d = P.structural_diff(a, self.legacy, b, self.modern)
        self.assertTrue(d["party_equal"]); self.assertTrue(d["money_equal"])
        self.assertTrue(d["inventory_equal"]); self.assertTrue(all(d["fragments_equal"]))
        self.assertTrue(d["footer_equal"])
        legacy_species = sum(1 for i in range(19 * 30) if P.u16(self.c["storage"], 4 + i * P.MON + 0x1C))
        self.assertEqual(b["box_stream_observation"]["species_field_nonzero"], legacy_species)

    def test_slot_parity(self):
        self.assertEqual(P.probe(build_modern(self.c, counter=4))["candidate_layouts"]["v023plus_5_section"]["chosen"], 0)
        self.assertEqual(P.probe(build_modern(self.c, counter=3))["candidate_layouts"]["v023plus_5_section"]["chosen"], 1)

    def test_shel_table_followed_not_assumed(self):
        table = tuple(range(10, 25)) + (29, 31)  # pages relocated into spare sectors
        r = P.probe(build_modern(self.c, table=table))
        self.assertFalse(r["shel"]["table_is_10_to_26"])
        self.assertTrue(r["box_pages_all_valid"])
        self.assertEqual(r["inventory"]["menu_counts"], [2, 0, 0])

    def test_bad_page_checksum_reported(self):
        bad = bytearray(self.modern); bad[12 * P.SECTOR + 5] ^= 0xFF
        r = P.probe(bytes(bad))
        self.assertFalse(r["box_pages_all_valid"])
        self.assertFalse(r["box_pages"][2]["checksum_valid"])

    def test_missing_shel_is_unknown(self):
        r0 = P.probe(self.modern)
        slot = r0["candidate_layouts"]["v023plus_5_section"]
        n = slot["slots"][slot["chosen"]]["id_to_sector"]["0x02"]
        bad = bytearray(self.modern); o = n * P.SECTOR
        bad[o + 0x410] ^= 0xFF
        put16(bad, o + 0xFF6, P.checksum(bytes(bad[o:o + P.SECTOR]), 0xFF0))
        r = P.probe(bytes(bad))
        self.assertEqual(r["status"], "UNKNOWN_LAYOUT")

    def test_equal_counters_unknown(self):
        r = P.probe(build_legacy(self.c, counters=(5, 5)))
        self.assertEqual(r["layout"], "UNKNOWN")
        self.assertIn("equal counters", r["candidate_layouts"]["legacy_14_section"]["reason"])

    def test_legacy_rotation_zero_not_misread(self):
        r = P.probe(build_legacy(self.c, counters=(14, 13)))
        self.assertEqual(r["layout"], "legacy_14_section")

    def test_sizes_and_erased(self):
        self.assertEqual(P.probe(self.modern[:P.FLASH])["layout"], "v023plus_5_section")
        self.assertEqual(P.probe(self.modern[:-1])["status"], "UNSUPPORTED_SIZE")
        self.assertEqual(P.probe(b"\xff" * P.FLASH)["status"], "UNKNOWN_LAYOUT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
