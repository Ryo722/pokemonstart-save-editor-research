# M3C-F1 bounded friendship proof — 2026-10-05

## Status

**SEALED PRIVATE PREFLIGHT PASS; HUMAN GAME ROUND TRIP PENDING.**

This is the first M3C field-expansion proof. It is deliberately limited to one exact retained private PokemonStart v0.15 lineage input and one one-byte semantic field change: `party[0] friendship 50 -> 51`.

It does not establish arbitrary-save support, a reusable general writer, another editable field, GUI readiness, overwrite behavior, or support for another build/profile.

## Why friendship was selected first

Friendship was selected after a read-only comparison of candidate party fields against the pinned CFRU-JP source and current repository evidence.

- The observed in-save `Pokemon` layout stores friendship as one independent `u8` field.
- `MAX_FRIENDSHIP` is 255.
- CFRU-JP code uses `SetMonData(... MON_DATA_FRIENDSHIP ...)` to update friendship directly; the checked friendship-only update path does not itself require stat recalculation.
- By contrast, EV/IV/nature-mint/hyper-training/EXP-level candidates have direct or obvious stat coupling, and held item / moves / PP / tera-related fields introduce broader semantic dependencies.
- `50 -> 51` is intentionally minimal and avoids a large semantic jump while still proving a new useful field family.

This selection is source-backed design evidence, not a claim that friendship has no gameplay consequences. Friendship is consumed by game logic such as evolution / move-tutor conditions; the proof goal is only that the save representation can be edited safely and survives a normal game save.

## Exact authorized scope

- provenance/profile: retained private PokemonStart v0.15 lineage only;
- exact input SHA-256: `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282`;
- starting slot state: both slots valid; slot 1 active at counter 3; slot 0 inactive at counter 2;
- source-backed active-slot/counter parity: `1 == 3 % 2`;
- target: `party[0] friendship` only;
- transformation: `50 -> 51`;
- output: brand-new file only;
- preserve counters, section metadata/permutation, inactive slot, sectors 28–31, parasite tails, optional external footer, all other party-record bytes, and every other non-target byte;
- recompute only logical section 1 checksum because that covered payload changes.

## Sealed exact private fingerprint

| Item | Value |
| --- | --- |
| Input size | `131,088` bytes |
| Input SHA-256 | `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282` |
| Active slot / counter | slot `1` / counter `3` |
| Inactive counter | `2` |
| Active logical section 1 physical sector | `18` |
| Starting friendship | `50` (`0x32`) |
| Target friendship | `51` (`0x33`) |
| Friendship diff | `0x12061: 32 -> 33` |
| Section 1 checksum | `0x1C33 -> 0x1D33` |
| Stored checksum byte diff | `0x12FF7: 1C -> 1D` |
| Complete diff count | `2` bytes |
| Output SHA-256 | `10f13894cab59922989e2b0508b41f2eef276e8c45b2778d6e6b1a309d2f98ae` |
| Sector 30 SHA-256 | `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525` |
| Sector 31 SHA-256 | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |
| Input/output footer SHA-256 | `62cdba6ee59f22ce914c34e4007c31bead308d63393d43b18e3c774796b562cb` |

The exact fingerprint was independently derived from the authorized private input bytes before the repository writer was sealed. No private save bytes are committed.

## Input profile checks

The proof writer requires all of the following before mutation:

- exact input SHA-256;
- both slots valid;
- active slot 1 / counter 3 and inactive counter 2;
- active-slot/counter parity;
- `party[0] friendship = 50`;
- checked party profile: species 1, level 5, EXP 134, ball 3, moves `33/45/0/0`, PP `35/40/0/0`, EVs all zero, IVs `31/29/26/23/27/29`, HP `21/21`, stats `9/11/10/13/12`;
- expected sector 30/31 hashes;
- expected opaque 16-byte footer hash.

The writer then requires the generated party record to be byte-equivalent to the input record except for friendship, and requires all complete-file differences to remain within the friendship/checksum envelope.

## Synthetic implementation preflight

A no-private-data synthetic test harness passed **6/6** locally:

1. exact bounded sealed constants;
2. active-slot-1 / rotated-section derivation and party-record invariant;
3. private seal rejection for an unrelated synthetic candidate;
4. active-slot/counter parity mismatch rejection;
5. wrong starting friendship rejection;
6. exclusive new-file creation, input immutability, and overwrite refusal under a synthetic seal override.

The synthetic fixture uses the observed section rotations: slot 0 `12,13,0..11`; slot 1 `11,12,13,0..10`, placing active logical section 1 at physical sector 18.

Evidence level: **local synthetic implementation preflight**. No GitHub Actions result is claimed.

## Exact private preflight

The sealed writer was run against the exact authorized input and produced a brand-new private proof output.

Observed result:

- input SHA-256 before and after remains `d8f193de...f282`;
- output SHA-256 is exactly `10f13894...f98ae`;
- active slot remains 1 at counter 3;
- friendship is `50 -> 51`;
- complete output diff is exactly two bytes: `0x12061 32->33`, `0x12FF7 1C->1D`;
- both slots retain all 14 logical sections with valid signatures/checksums;
- slot counters remain `2 / 3`;
- physical section permutations remain unchanged;
- the active party record differs at exactly record offset 41 (`friendship`) and is otherwise byte-identical;
- sectors 28–31 and the optional external footer are byte-identical to the input.

A separate independent parser, not the repository candidate writer, recomputed the slot/section checksums, exact diff, section order, friendship byte, sector 30/31 hashes, footer hash, and output SHA-256 and obtained the same results.

Evidence level: **local private-input verification + independent local parser check**.

## Completion gate

M3C-F1 is **not complete** yet. The required remaining gate is:

1. load the exact generated proof output in the same PokemonStart v0.15 environment;
2. complete one normal in-game save;
3. return that resaved `.sav` privately;
4. read-only verify slot/counter transition, active parity, friendship 51 retention, checked party invariants, sectors 28–31, and the established footer preservation-only rule.

Only after that round trip passes should M3C-F1 completion / merge be considered.

## Authorization boundary

The 2026-10-05 human authorization covers this exact M3C-F1 friendship proof, including implementation, synthetic preflight, exact private candidate derivation/sealing, one new private proof output, human round-trip preparation, and read-only verification of the returned resave.

It does not authorize merge without a later explicit merge decision, a second M3C field, arbitrary/non-lineage save writing, general writer expansion, overwrite behavior, GUI work, box editing, protected-data publication, or execution/publication of protected binaries.
