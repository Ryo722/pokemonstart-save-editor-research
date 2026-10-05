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

**First M5A canary: GAME-PROVEN for the exact `3000 -> 9,999,999` transformation.**

## First canary return audit — 2026-10-06

The supplied return save freshly reproduced as SHA-256 `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4` and 131,088 bytes. `pokemonstart_save_verifier.py` accepted the supported layout and all 28 section signatures/checksums. The active state is slot 0/counter 2; slot 1/counter 1 remains valid and contains decoded money `9,999,999`. The return's active party[0] is byte-identical to the retained previous slot's party[0]. The transition rotated the physical section position by one, incremented the saved-game statistic once (`1 -> 2`), advanced play time from `00:02:15` to `00:02:31`, retained sectors 28–31, and retained the opaque footer byte-for-byte. Money reads from active logical section 1 offset `0x0290` XOR active logical section 0 offset `0x0F20`, with key `0`.

Human game observation plus the independently reproduced return state supports the exact first transformation as **game-proven**. The return hash proves the bytes and save transition; displayed-money confirmation remains the human-observed part of the evidence.

### Bounded early-game transition observations

Relative to the retained prior-slot state, SaveBlock1 logical section 1 has six EventObject runtime-field changes already within the M4 observation set, plus 85 changed bytes in the `EventObjectTemplate` array region at SaveBlock1 offset `0x09E0` through `0x0ED9` (the pinned CFRU-JP [`include/global.h`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/include/global.h) places `eventObjectTemplates[64]` at `0x09E0`). The logical section 4 checksum-excluded tail changed at four bytes: offsets `0xEDE`, `0xEDF`, `0xEE8`, and `0xEE9` within the tail beginning at `0xD98`. Pinned CFRU-JP [`src/save.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/save.c) uses the unchecked tails of logical sections 0, 4, and 13 for parasite save/load state.

These are **observed bounded early-game transition evidence**. The unchanged M4 `check_game_transition` reports `game-save payload changed outside qualified envelope`; both its stable-payload and tail fingerprints differ. We do not broaden the M4 predicate, volatile masks, or provenance scope from this sample.

## Second exact repeated-use canary — 2026-10-06

This proof is separately sealed and accepts only the exact return hash above. It changes decoded money `9,999,999 -> 1,234,567` and is not exposed through the M4 GUI/core FAMILY registry.

- writer: `pokemonstart_m5a_repeated_money_canary.py`
- independent auditor: `tests/m5a_independent_repeated_money_audit.py` (does not import the writer or repository verifier)
- exact source SHA-256: `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`
- exact output SHA-256: `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`
- semantic value: `9,999,999 -> 1,234,567`; active section-0 encryption key remains `0`
- allowed complete diff only: `0x03290 7F->87`, `0x03291 96->D6`, `0x03292 98->12`, `0x03FF6 A7->29`, `0x03FF7 A7->E7`
- output section-1 checksum: `0xE729`
- synthetic regressions: successful helper path, permutation independence, nonzero-key XOR semantics, wrong hash, wrong starting money, malformed checksum, existing destination, alias rejection, source immutability, and complete-diff enforcement

The writer verifies S0 before mutation, resolves logical sections by ID, reads the active key, mutates only the logical section-1 money word, recalculates only its checksum, seals the complete diff and output SHA, requires a new repo-external output path, reruns the repository verifier, rechecks decoded target money, and verifies source immutability. The independent audit checks hashes, every changed byte and no others, all signatures/checksums, active slot/counter, section order/metadata, key, decoded money, inactive slot, checksum-excluded tails, party bytes, sectors 28–31, and footer.

Status: **GENERATED / INDEPENDENTLY AUDITED; awaiting Human game round trip.** This does not adopt an arbitrary-money FAMILY and does not broaden supported saves, builds, versions, or M4 provenance.

Private execution wrote only `/Users/ryohanazaki/claude-workspace/PokemonStart-private/PokemonStart_v0.15(7)_M5A_1234567_candidate.sav`, a new repo-external file. The writer reported `source_immutable: true`; a post-run SHA-256 check independently reproduced both exact source and output hashes. The independent audit returned **PASS**. The repository verifier separately accepted the output at 131,088 bytes with all 28 section checksums/signatures valid, active slot 0/counter 2, and logical section-1 checksum `0xE729`. No private `.sav` was added to Git.

This is not yet a game-proven write capability and must not be generalized to an arbitrary-money FAMILY.

The exact first candidate's human return and independent byte audit are recorded above. The remaining Human step applies only to the second candidate: load its exact private output in the validated PokemonStart v0.15 environment, confirm the save loads and displays `1,234,567`, perform one normal in-game save, and return that `.sav` for read-only audit. Keep the generated output as recovery input.

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
