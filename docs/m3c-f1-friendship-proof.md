# M3C-F1 bounded friendship proof — 2026-10-05

## Status

**BOUNDED EVIDENCE COMPLETE; MERGE AUTHORIZATION PENDING.**

This is the first M3C field-expansion proof. It is deliberately limited to one exact retained private PokemonStart v0.15 lineage input and one one-byte semantic field change: `party[0] friendship 50 -> 51`.

It does not establish arbitrary-save support, a reusable general writer, another editable field, GUI readiness, overwrite behavior, or support for another build/profile.

## Why friendship was selected first

Friendship was selected after a read-only comparison of candidate party fields against the pinned CFRU-JP source and current repository evidence. The observed in-save `Pokemon` layout stores friendship as one `u8` field; checked CFRU-JP friendship-only update paths write it directly, while EV/IV/nature-mint/hyper-training/EXP-level and other candidates introduce stronger coupling.

## Exact authorized scope

- retained private PokemonStart v0.15 lineage only;
- input SHA-256 `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282`;
- both slots valid; slot 1 active at counter 3, slot 0 inactive at counter 2;
- `party[0] friendship 50 -> 51` only;
- brand-new output file only;
- preserve counters, section metadata/permutation, inactive slot, sectors 28–31, parasite tails, optional footer, all other party bytes, and every other non-target byte;
- recompute only logical section 1 checksum.

## Sealed private fingerprint

| Item | Value |
| --- | --- |
| Input size | `131,088` bytes |
| Input SHA-256 | `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282` |
| Active slot / counter | slot `1` / counter `3` |
| Active section 1 physical sector | `18` |
| Friendship diff | `0x12061: 32 -> 33` |
| Section 1 checksum | `0x1C33 -> 0x1D33` |
| Stored checksum byte diff | `0x12FF7: 1C -> 1D` |
| Complete diff count | `2` bytes |
| Output SHA-256 | `10f13894cab59922989e2b0508b41f2eef276e8c45b2778d6e6b1a309d2f98ae` |
| Sector 30 SHA-256 | `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525` |
| Sector 31 SHA-256 | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |

The synthetic implementation preflight passed **6/6** locally. Exact private preflight and a separate parser reproduced the sealed fingerprint, checksums, section order, party invariants, sectors 28–31, footer preservation, and output SHA. No private `.sav` is committed.

## Human game round trip — PASS

The user returned a private resave after loading the exact proof output and performing one normal in-game save.

| Observation | Result |
| --- | --- |
| Resave size / SHA-256 | `131,088` bytes / `6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600` |
| Flash SHA-256 | `f3f1069f632a2bae691a949622eb1f97e9328f1cebd15f93907b926120f683e5` |
| Slot 0 | valid, counter 4 |
| Slot 1 | valid, counter 3 |
| Active slot / parity | slot 0; `0 == 4 % 2` — PASS |
| Active logical section 1 | physical sector 5 |
| Active friendship | `51` |
| Active IVs | `31/29/26/23/27/29` |
| Checked party values | species 1; level 5; EXP 134; ball 3; moves `33/45/0/0`; PP `35/40/0/0`; EVs zero; HP `21/21`; stats `9/11/10/13/12` |
| Sector 30 SHA-256 | `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525` |
| Sector 31 SHA-256 | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |
| Resave footer SHA-256 | `8ef79aef38d8658aa715ea718edef3246c6af1fc3147990a4f3b3209ae585c69` |

Byte-level checks additionally show:

- proof-output slot 1 at counter 3 is preserved byte-for-byte in the resave;
- the game wrote slot 0 at counter 4 and selected it as active;
- the returned active party record 0 is byte-for-byte identical to the proof output's active party record, so friendship 51 and all checked record-local values survived;
- sectors 28–31 are byte-for-byte identical to the proof output;
- the optional footer changed during the game/emulator save, as allowed by the preservation-only contract.

## Verdict and boundary

**M3C-F1 COMPLETE for this exact bounded private-lineage friendship proof, subject only to later merge authorization.**

The proof does not authorize or establish a second M3C field, arbitrary/non-lineage save writing, a general writer, overwrite behavior, GUI work, box editing, or protected-data publication.
