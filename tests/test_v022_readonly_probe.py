from __future__ import annotations

import unittest

import pokemonstart_mgba_harness as bridge
import pokemonstart_v022_readonly_probe as probe


class V022ReadOnlyProbeTests(unittest.TestCase):
    def test_live_money_and_party_must_match_offline_record(self) -> None:
        ewram = bytearray(0x40000)
        base = 0x1000
        money, count, saved = 1234567, 1, 3
        party0 = bytes(range(100))
        ewram[base + 0x290:base + 0x294] = money.to_bytes(4, "little")
        ewram[base + 0x34] = count
        ewram[base + 0x38:base + 0x38 + 100] = party0
        ewram[base + 0x1200:base + 0x1204] = saved.to_bytes(4, "little")
        offline = {"money": money, "party_count": count, "saved_statistic": saved,
                   "party0_bytes": party0}

        result = probe.observe_ewram(bytes(ewram), offline)

        self.assertEqual(result["money"], money)
        self.assertEqual(result["party_count"], count)
        self.assertTrue(result["party0_matches_offline"])

    def test_live_money_mismatch_fails_closed(self) -> None:
        ewram = bytearray(0x40000)
        base = 0x1000
        money, count, saved = 1234567, 1, 3
        party0 = bytes(range(100))
        ewram[base + 0x290:base + 0x294] = (7654321).to_bytes(4, "little")
        ewram[base + 0x34] = count
        ewram[base + 0x38:base + 0x38 + 100] = party0
        ewram[base + 0x1200:base + 0x1204] = saved.to_bytes(4, "little")
        offline = {"money": money, "party_count": count, "saved_statistic": saved,
                   "party0_bytes": party0}

        with self.assertRaises(bridge.HarnessError):
            probe.observe_ewram(bytes(ewram), offline)


if __name__ == "__main__":
    unittest.main()
