# M5A exact max-money canary — 2026-10-05

## Human authorization

> `AUTHORIZE M5A EXACT MAX-MONEY CANARY: implement and execute the bounded exact-input 3000-to-9999999 proof writer against SHA-256 fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b; write only a new output file; require complete independent diff/checksum/invariant audit and source immutability; do not generalize this proof to reusable arbitrary money editing or any other capability.`

This authorization is intentionally one-input / one-target. It does not authorize a reusable money editor, arbitrary values, other save hashes, inventory edits, Pokemon edits, broader lineage/build support, or UI exposure.

## Input and prior read proof

Private input bytes are not committed.

- exact input SHA-256: `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`
- size: `131,088` bytes (`0x20010`)
- active slot: `1`
- active counter: `1`
- logical section 0 physical sector: `15`
- logical section 1 physical sector: `16`
- encryption key: `0x00000000`
- stored/decoded money before: `3000`
- human observation: the game displays `3000` for this exact save

The read-side evidence is recorded in `docs/m5a-money-private-read-audit.md`.

## Exact proof writer

`pokemonstart_m5a_exact_max_money_writer.py` is a deliberately sealed proof writer. It requires the exact input SHA-256 above, exact active slot/counter/section placement, key `0`, and starting money `3000`. The only authorized semantic target is `9,999,999`.

It:

1. validates both save slots, section IDs, signatures, counters, and section checksums;
2. locates logical sections by section ID rather than guessing physical order;
3. confirms the exact starting state and XOR-decoded money;
4. encodes `9,999,999` with the observed key;
5. recomputes only logical-section-1 checksum;
6. requires the complete byte diff to equal the sealed five-byte diff below;
7. revalidates the complete output structure/checksums/semantic value;
8. preserves footer and sectors 28–31;
9. writes only with exclusive new-file creation;
10. rereads and re-audits the published bytes;
11. verifies source SHA-256 is unchanged before and after publication.

The writer also seals the deterministic expected output SHA-256, so an unexpected output is rejected.

## Exact generated candidate

Local private-input execution produced one new output outside Git.

- output SHA-256: `e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69`
- decoded output money: `9,999,999`
- new logical-section-1 checksum: `0x1CC1`
- source SHA-256 after execution: unchanged at `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`

Complete byte diff:

| Absolute offset | Before | After | Meaning |
| --- | ---: | ---: | --- |
| `0x10290` | `B8` | `7F` | encoded money byte 0 |
| `0x10291` | `0B` | `96` | encoded money byte 1 |
| `0x10292` | `00` | `98` | encoded money byte 2 |
| `0x10FF6` | `62` | `C1` | section-1 checksum byte 0 |
| `0x10FF7` | `91` | `1C` | section-1 checksum byte 1 |

The fourth byte of the u32 money word remains `00`, so only three money bytes actually differ.

Evidence label: **local private-input repository-writer execution / pre-game canary evidence**.

## Independent complete-byte audit

`tests/m5a_independent_max_money_audit.py` does not import the proof writer. Against the private source and generated candidate it independently reproduced:

- exact source SHA-256;
- exact output SHA-256;
- exact five changed byte offsets/values above and no other differences;
- slot 0 remains erased;
- slot 1 remains counter `1` with physical/logical order `13,0,1,...,12`;
- all section signatures/checksums pass;
- logical sections 0/1 remain physical sectors 15/16;
- key remains `0`;
- XOR-decoded money is `9,999,999`;
- 16-byte emulator footer is unchanged;
- sectors 28–31 are unchanged.

Independent audit result: **PASS**.

## Synthetic regression evidence

`tests/test_m5a_exact_max_money_writer.py` uses only synthetic save bytes. Local execution:

`python3 -m unittest discover -s tests -v` against the bounded M5A test workspace -> **5/5 PASS** for the new test file.

Covered cases:

- synthetic exact transform / complete-diff enforcement;
- nonzero encryption-key XOR semantics in the helper path;
- wrong SHA-256 rejection;
- wrong starting-money rejection;
- exclusive new-file creation plus source immutability / existing-output rejection.

This synthetic nonzero-key test is implementation evidence only. It does not prove reusable nonzero-key PokemonStart private-save support.

## Current status

**M5A exact max-money canary: GENERATED AND INDEPENDENTLY AUDITED; HUMAN GAME ROUND TRIP REQUIRED.**

This is not yet a game-proven write capability and must not be generalized to an arbitrary-money FAMILY.

Required next human step:

1. load the exact generated private output in the validated PokemonStart v0.15 environment;
2. confirm the displayed money is `9,999,999` and the save loads normally;
3. perform one normal in-game save;
4. return that new `.sav` for read-only audit.

The return audit must verify normal slot/counter rotation, all section checksums, persistence of `9,999,999`, preservation/expected evolution of unrelated state under the already established game-transition model, and absence of unexplained corruption.

## Explicit non-claims

This canary does not authorize or prove:

- arbitrary money amounts;
- another input hash or arbitrary retained descendants;
- a reusable money FAMILY;
- UI money controls;
- inventory/item edits;
- Pokemon species/stat editing;
- Pokédex or general flag editing;
- arbitrary saves/builds/versions;
- live-emulator overwrite or broader delivery/threat-model support.
