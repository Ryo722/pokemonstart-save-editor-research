# M5A second round trip and bounded money FAMILY candidate — 2026-10-06

This is the controlling M5A evidence/candidate record for the second game round trip and the reusable money FAMILY candidate. Where older M5A prose conflicts with the corrections below, this record controls.

## Human authorization

> `AUTHORIZE M5A SECOND ROUND-TRIP ADOPTION AND BOUNDED MONEY FAMILY CANDIDATE: canonically record the successful 9999999-to-1234567 game round trip; correct the independently reproduced M5A evidence-record discrepancies for the first EventObjectTemplate changed-byte count and opaque emulator-footer behavior; then design, implement, test, and independently audit a retained-lineage reusable money FAMILY candidate for values 0..9999999, initially fail-closed to the currently evidenced PokemonStart v0.15 build/environment and observed encryption-key boundary. Keep the existing M4 check_game_transition/provenance predicate unchanged. Any M5A-specific game-return continuation rule must be separately bounded to source-backed and independently evidenced normal-save behavior, including the observed section-4 parasite-tail evolution, and must fail closed outside that envelope. Do not expose money editing through the GUI yet, do not broaden save/build/version support, and do not begin M5B/M5C implementation.`

## Second game round trip — independently reproduced

Exact second editor candidate:

- source SHA-256: `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`
- generated candidate SHA-256: `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`
- semantic transformation: `9,999,999 -> 1,234,567`
- exact editor diff: `0x03290 7F->87`, `0x03291 96->D6`, `0x03292 98->12`, `0x03FF6 A7->29`, `0x03FF7 A7->E7`

The human loaded this candidate in the same retained PokemonStart v0.15 environment, observed normal loading and displayed money `1,234,567`, then performed one normal in-game save and returned the resulting private save.

Fresh read-only audit of that returned save reproduced:

- return SHA-256: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- size: `131,088` bytes (`0x20010`)
- all 28 saved sections: valid signature and section-specific checksum
- editor candidate active state: slot 0 / counter 2
- normal-save return active state: slot 1 / counter 3
- previous slot 0 in the return: byte-identical to the editor candidate's active slot
- section permutation: exact expected +1 rotation
- encryption key: `0x00000000`
- decoded money in the return: `1,234,567`
- party[0] 100-byte record: unchanged
- saved-game statistic: `2 -> 3`
- play time: `151 -> 159` seconds
- sectors 28–31: unchanged
- stable checksum-covered payload after the existing M4 volatility mask: unchanged
- opaque emulator footer: changed, as described below

Evidence label: **game-proven exact repeated-use transformation** for this retained private lineage/build/environment. Together with the prior `3000 -> 9,999,999` round trip, this establishes two consecutive editor -> game -> normal-save cycles across different active slots and section permutations.

## Corrections to older M5A evidence prose

### EventObjectTemplate changed-byte count and layout

Pinned CFRU-JP `include/global.h` places `SaveBlock1.eventObjectTemplates[64]` at SaveBlock1 offset **`0x08E0`**.

On the first money round trip, the independently reproduced bytes changed only in the subrange **`0x09E0..0x0ED9`** inside that array, for **85 changed bytes** after excluding the already-qualified M4 EventObject runtime-field changes.

Therefore older prose saying either:

- `89` EventObjectTemplate bytes changed; or
- the EventObjectTemplate array itself begins at `0x09E0`

is superseded by this correction. The bounded observation remains: this initialization occurred on the first very-early-game normal save and did **not** recur on the second normal save.

### Opaque emulator footer

Editor operations preserve the 16-byte opaque footer exactly. Normal game/emulator saves may change it. Independently reproduced footer SHA-256 values are:

- first editor candidate: `9e5dd419cf323817943c6282d4f51936fb4913fe6f0c83458aa5b4f5742ae877`
- first normal-save return: `c564b0c872dde9b8a3cf8e5b38309e1ec6a7257a747dfb083c5218c3ef280160`
- second editor candidate: same as the first return, `c564b0c872dde9b8a3cf8e5b38309e1ec6a7257a747dfb083c5218c3ef280160`
- second normal-save return: `246283651a5e2468bb6c5401a0b8215d103b80fda0855a117d5a703744045d96`

Thus older M5A prose claiming footer byte-for-byte preservation across a **normal game save** is incorrect and superseded. The retained policy is: **editor output preserves the footer; game/emulator return treats it as opaque and change-allowed.**

## Section-4 parasite-tail evidence

Both independently observed normal saves changed exactly four bytes in the checksum-excluded logical-section-4 tail:

First normal save:

- `0xEDE 46 -> E1`
- `0xEDF 24 -> 2D`
- `0xEE8 F6 -> F8`
- `0xEE9 0E -> CC`

Second normal save:

- `0xEDE E1 -> 55`
- `0xEDF 2D -> 30`
- `0xEE8 F8 -> 5C`
- `0xEE9 CC -> 98`

Pinned CFRU-JP `src/save.c` source-backs the unchecked tails of logical sections 0, 4 and 13 as parasite save/load storage. This supports a narrowly bounded M5A continuation rule for those exact section-4 offsets only; it does not justify ignoring arbitrary tail changes.

The existing M4 `check_game_transition` remains **unchanged**. M5A implements its own stricter-purpose continuation rule rather than weakening M4 provenance.

## Bounded reusable money FAMILY candidate

Implementation: `pokemonstart_m5a_money_family.py`

Independent auditor: `tests/m5a_independent_money_family_audit.py`

Synthetic tests: `tests/test_m5a_money_family.py`

### Root and environment boundary

The candidate FAMILY starts from the second game-proven return:

- root SHA-256: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- PokemonStart v0.15 target/build SHA-256: `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`
- M5A environment identifier: `macos-mgba-0.10.5`
- observed encryption-key boundary: **only key `0x00000000` is eligible**
- supported target money range: integer `0..9,999,999`

`macos-mgba-0.10.5` is an M5A binding label for the environment actually evidenced by the two Human round trips. It is not a new cross-platform support claim.

### Eligibility and transaction model

A save is eligible only when all of the following hold:

1. S0 verifier acceptance and active-slot/counter parity;
2. exact build/environment binding;
3. membership in the root-anchored private M5A money journal;
4. complete journal fingerprint match;
5. encryption key exactly `0`;
6. current and target money both inside the adopted range.

A money edit:

- resolves logical sections by ID, not physical position;
- changes only the active logical-section-1 money word at offset `0x0290`;
- recomputes only logical-section-1 checksum;
- accepts only a fresh `MoneyPlan` bound to source SHA and deterministic output SHA/diff;
- independently re-verifies output semantics;
- uses the existing hardened M4 new-file publication layer;
- never overwrites the source;
- keeps journal/private output outside the repository;
- remains macOS-only under this candidate authorization;
- is not exposed through the M4 GUI/core capability registry.

### M5A-specific normal-save continuation rule

After a journaled money-editor output, a Human-observed normal game return may be enrolled only when all checks pass:

- opposite save slot selected;
- counter exactly +1;
- previous slot counter and bytes unchanged;
- encryption key remains `0`;
- money remains exactly the edited value;
- party count and party[0] bytes unchanged;
- checksum-covered payload equals the parent after applying exactly the existing M4 volatile payload mask (play time, qualified EventObject runtime fields, saved-game statistic);
- checksum-excluded tails equal the parent after masking **only logical-section-4 offsets `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9`**;
- play time does not move backward;
- saved-game statistic increments exactly once;
- sectors 28–31 are unchanged;
- section permutation rotates exactly as expected;
- opaque footer may change and is recorded but not used as a game-return equality requirement.

The rule rejects EventObjectTemplate initialization, any other checksum-covered drift, any other tail change, money drift, party drift, extra-sector drift, unexpected counter/slot behavior, nonzero encryption key, or unjournaled lineage.

This means the first early-game return is **not** retroactively accepted by the reusable FAMILY rule. The FAMILY root is deliberately placed after that initialization, at the second proven return.

## Verification evidence

Focused local synthetic tests for the candidate passed **15/15** during construction. Covered cases include:

- exact root bootstrap / journal membership;
- unjournaled valid-save rejection;
- wrong build/environment rejection;
- zero, mid-range and maximum target values;
- invalid-range and no-op rejection;
- nonzero encryption-key rejection;
- corrupt checksum rejection;
- stale-plan rejection;
- new-file/source-immutability behavior;
- input/output alias rejection;
- accepted M5A game return;
- rejection of tail drift outside the four allowed offsets;
- rejection of EventObjectTemplate drift;
- rejection of money drift;
- opaque footer change allowed only on the game-return side.

A separate independent auditor does not import the FAMILY implementation. Against the actual private second candidate/return pair reconstructed from canonical evidence it reproduced:

- candidate SHA-256 `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`;
- return SHA-256 `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`;
- editor five-byte diff and target `1,234,567`;
- valid slot/counter `0/2 -> 1/3` transition;
- retained money `1,234,567`;
- expected footer change;
- all bounded continuation invariants above.

Independent private transition audit: **PASS**.

## Current status / non-claims

**M5A reusable money FAMILY candidate is IMPLEMENTED / SYNTHETICALLY TESTED / INDEPENDENTLY AUDITED, but is not yet GUI-exposed and this record does not broaden save/build/version or encryption-key support.**

This does not authorize or claim:

- nonzero encryption-key private saves;
- arbitrary/unrooted PokemonStart saves;
- another PokemonStart build/version;
- Windows M5A FAMILY publication;
- changes to M4 provenance predicates;
- GUI money controls;
- inventory/item editing;
- Pokemon editing;
- Pokédex or general flag editing;
- public release/distribution guarantees.
