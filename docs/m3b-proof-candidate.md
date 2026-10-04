# M3B bounded same-field proof — 2026-10-05

## Status

**BOUNDED EVIDENCE COMPLETE; MERGE AUTHORIZATION PENDING.**

The authorized M3B candidate has completed its sealed private preflight, repository test contract, one private proof-file generation, human game round trip, and read-only verification of the returned resave. This conclusion is limited to the exact retained private PokemonStart v0.15 lineage and the exact `party[0]` HP IV `30 -> 31` transformation.

No arbitrary-save support, new editable field, GUI, overwrite behavior, counter/slot rewriting, or M3C authorization is implied.

## Exact authorized scope

- provenance profile: retained private PokemonStart v0.15 M2 lineage only;
- exact input SHA-256: `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
- starting state: both slots valid; active physical slot 0 at counter 2; inactive counter 1;
- field: `party[0]` HP IV only;
- transformation: `30 -> 31`;
- output: brand-new file only;
- preserve counters, section metadata/permutation, inactive slot, sectors 28–31, parasite tails, optional footer, and every non-target byte;
- recompute only the checksum covering changed logical section 1 data.

## Sealed exact candidate fingerprint

| Item | Value |
| --- | --- |
| Input size | `131,088` bytes |
| Input SHA-256 | `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac` |
| Active slot / counter | slot `0` / counter `2` |
| Inactive counter | `1` |
| Logical section 1 physical sector | `3` |
| Starting IVs | `30/29/26/23/27/29` |
| Target IVs | `31/29/26/23/27/29` |
| Data diff | `0x3080: BE -> BF` |
| Section 1 checksum diff | `0x3FF6: 20 -> 21` |
| Complete diff count | `2` bytes |
| Output SHA-256 | `cf2ca33a303b6409300ac4032c7c47efd9859562bc06fe18e89481bb93ea5f1f` |

The repository writer seals both the exact complete diff and exact output hash. The private preflight confirmed both slots and all ordinary section checksums, source-backed active-slot/counter parity, expected sector 30/31 hashes, footer hash, physical section permutation, and starting party state before mutation. Generated output re-verifies with the expected IVs and preserves all bytes outside the two sealed changes.

Evidence level: **local private-input verification + repository candidate evidence**. No private save bytes are committed.

## Synthetic implementation preflight

The sealed-state no-private-data test contract passed **6/6** locally:

1. exact bounded sealed constants;
2. derive with two valid rotated slots while remaining in the field/checksum envelope;
3. reject an unrelated synthetic candidate against the private seal;
4. reject active-slot/counter parity mismatch;
5. reject wrong starting HP IV;
6. exercise exclusive new-file creation, input immutability, and overwrite refusal under a synthetic seal override.

No GitHub Actions run exists for this candidate head; the PASS above is a local synthetic preflight, not CI evidence.

## Human round-trip result — PASS

The user returned a new private save in direct response to the requested M3B human round-trip step. The returned file was inspected read-only and compared with the exact repository-generated M3B proof output.

| Observation | Result |
| --- | --- |
| Resave size | `131,088` bytes |
| Resave SHA-256 | `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282` |
| Flash-body SHA-256 | `ae5838c5630f56c8663f5d74aabc4a64ca90779c9e4929ecd41c4c21b11c7604` |
| Slot 0 | valid, counter 2 |
| Slot 1 | valid, counter 3 |
| Active slot | slot 1, uniquely newer |
| Active parity | `1 == 3 % 2` — PASS |
| Active logical section 1 | physical sector 18 |
| Active party count | 1 |
| Active IVs | `31/29/26/23/27/29` |
| Active IV word | `0x3BBBEBBF` |
| Checked party values | species 1; level 5; EXP 134; friendship 50; ball 3; moves 33/45; PP 35/40; EVs zero; HP 21/21; stats 9/11/10/13/12 |
| Sector 30 SHA-256 | `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525` |
| Sector 31 SHA-256 | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |
| Resave footer SHA-256 | `62cdba6ee59f22ce914c34e4007c31bead308d63393d43b18e3c774796b562cb` |

Additional byte-level checks:

- proof output slot 0 (counter 2) is preserved **byte-for-byte** in the resave;
- the game rewrote slot 1 from counter 1 to counter 3 and selected it as active;
- the returned active party record 0 is **byte-for-byte identical** to the proof output's prior active party record, so HP IV 31 and all record-local checked values survived the normal save;
- flash sectors 28–31 are **byte-for-byte identical** to the proof output;
- the optional 16-byte external footer changed across the game/emulator save, as already allowed by the M3A contract: preserve it in tool-generated output, but do not require equality across a later game round trip.

Evidence classification:

- game-round-trip occurrence: **human-relayed result**, corroborated by the independently observed counter/slot transition;
- returned save structure and byte comparisons: **local private-input verification**;
- slot/counter parity expectation: **upstream source evidence + local verification**.

## M3B verdict

**M3B COMPLETE for the exact bounded private-lineage proof, subject only to canonical merge authorization.**

This proof closes the specific uncertainty targeted by M3B: the M3A transaction envelope works on a non-M2-input hash with both slots valid and the opposite active physical slot, while keeping the semantic field family fixed. The game accepted the resulting external edit and a normal in-game save carried the HP-IV value forward into the next slot.

What remains unproven includes arbitrary PokemonStart v0.15 saves, other builds, a general build-identification mechanism, other editable fields, field coupling outside HP IV, and GUI readiness.

PR #8 must remain unmerged until explicit human merge authorization. Before merge, canonical README / decision-record milestone wording should be updated on the branch so `main` will not contain stale M3B status.
