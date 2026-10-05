# M4 retained-lineage P transition model

## Scope

This model qualifies only normal-save descendants of retained root
`ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`, bound
to ROM/build `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`
and the matching local emulator environment journal. It separates:

- **S0:** checksums, counters/parity, section permutation, and save structure;
- **P:** root-anchored journal chain and the normal-save transition below;
- **C:** the independently bounded `party[0].markings` value change `0 ↔ 1`.

P does not grant arbitrary-save support. C does not permit any other value,
field, party slot, or build.

## Pinned primary source

All source links below pin CFRU-JP commit
[`e24a16fe39e27ae162faf5b78596d1f3df18489d`](https://github.com/kapibarasan000/CFRU-JP/tree/e24a16fe39e27ae162faf5b78596d1f3df18489d).

- [`include/global.h`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/include/global.h#L700-L773) places `SaveBlock1.eventObjects` at `0x6A0`, declares 16 map objects, places `gameStats` at SaveBlock1 offset `0x1200`, and defines SaveBlock2 play time fields: hours at `0x0E`, minutes `0x10`, seconds `0x11`, VBlanks `0x12`.
- [`include/global.fieldmap.h`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/include/global.fieldmap.h#L212-L274) defines `struct EventObject`, size `0x24`. Its first runtime flags byte is at `0x00`; `currentCoords` at `0x10`; `previousCoords` at `0x14`; facing/movement directions share byte `0x18`; `movementActionId` is `0x1C`; `previousMovementDirection` is `0x20`.
- [`src/overworld.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/overworld.c) reads map-object current coordinates and facing/direction while performing overworld movement and interactions. [`src/follow_me.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/follow_me.c) updates event-object coordinates and direction during follower movement.
- [`src/rtc.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/rtc.c#L233-L261) increments VBlanks and advances seconds, minutes, and hours with the documented rollover. Hours cap at 999.
- [`src/save.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/save.c#L444-L450) routes `SAVE_NORMAL` through `SaveSerializedGame()` and writes all save sections. This persists the SaveBlock1 and SaveBlock2 state above.
- [`include/constants/game_stat.h`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/include/constants/game_stat.h#L4-L8) identifies `GAME_STAT_SAVED_GAME` as index 0. The exact `+1` on each retained normal-save transition below is local private corpus evidence; the pinned `src/save.c` path does not itself show an increment call.

## Source-backed volatility model

For stable-payload comparisons, the core masks only these source-defined
fields:

1. SaveBlock2 `playTimeHours`, `playTimeMinutes`, `playTimeSeconds`, and
   `playTimeVBlanks` (payload section 0 offsets `0x0E..0x12`). Hours must be at
   most 999; minutes and seconds at most 59; total elapsed seconds cannot move
   backwards. VBlanks are volatile subsecond state.
2. For each of the 16 `EventObject` records at SaveBlock1 `0x6A0 + i*0x24`,
   only the source-defined runtime/movement subfields: first runtime flags byte
   `+0x00`, `currentCoords` `+0x10..+0x13`, `previousCoords` `+0x14..+0x17`,
   packed facing/movement directions `+0x18`, movement action `+0x1C`, and
   previous movement direction `+0x20`. This is a structured field mask over
   `eventObjects`, not an offset exception list. All remaining bytes in every
   record, including movement type, identity, graphics, range, and elevation,
   remain part of the exact stable-payload hash.
3. SaveBlock1 `gameStats[GAME_STAT_SAVED_GAME]`, logical section 2 offset
   `0x210` (SaveBlock1 `0x1200` follows section 1's `0xFF0` bytes). Each of the
   three retained normal saves increments this field exactly once. Its source
   identity is pinned; its repeated increment is empirical private evidence.

Every other logical payload byte must remain unchanged after checksum
recalculation. The transition also requires the opposite active slot, next
counter and parity, byte-identical previous active slot, unchanged party[0]
record and identity, unchanged sectors 28–31 and checksum-excluded tails, and
one-position section rotation. S0 verifies every active/inactive section
checksum. The emulator footer remains opaque under the adopted
preservation/change policy and is not interpreted here.

## Retained private transition results

All hashes and byte offsets below are local evidence metadata; save bytes stay
outside Git.

| Parent → child | Active slot/counter | Play time | Saved-game stat | Result |
| --- | --- | --- | --- | --- |
| retained prior slot → root A | `1/5 → 0/6` | `0:02:46 → 0:02:52` | `5 → 6` | pass |
| proof B → returned C | `0/6 → 1/7` | `0:02:52 → 0:02:58` | `6 → 7` | pass |
| proof D → returned E | `1/7 → 0/8` | `0:02:58 → 0:03:03` | `7 → 8` | pass |

The independent transition auditor classified every D→E payload difference:

- section 0 `0x10..0x12`: play-time minutes, seconds, VBlanks;
- section 1 `0x6DC/0x6E4`: `eventObjects[1]` direction and previous direction;
- section 1 `0x6E8/0x6FA/0x6FE/0x700/0x704/0x708`:
  `eventObjects[2]` runtime flags, current/previous Y coordinates, directions,
  movement action, previous direction;
- section 1 `0x724/0x72C`: `eventObjects[3]` direction and previous direction;
- section 2 `0x210`: saved-game statistic.

No unexplained payload changes remain. The retained-party record and markings
`1` remained unchanged in D→E. C's two markings directions have independent
byte/checksum audits from distinct P-qualified source hashes A and C; B→C
provides the `1→0` game boundary and D→E the `0→1` game boundary. No duplicate
game canary is required for a CLI or GUI caller because those entry points
share this core and P journal.
