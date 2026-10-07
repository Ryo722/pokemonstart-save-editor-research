# E1 Human native transitions: verified results

Disposition: **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE**. E1 qualification remains incomplete; E2 has not started.

Canonical base and fresh remote main at preparation: `785e113fa1885ac17e19da842a74740f62a8e789`.
Read-only verification used candidate `98173a4dc0a2cd84710ea1110d6138f4899f80c3`, tree `75f503e67dcc2a3ac302cfae2b138158c95ff97a`, without code changes.
This publication adds documentation only. Final packet identity is recorded in draft PR #21 after push.

## Evidence separation

The Human performed the requested game actions, normal in-game SAVE and full mGBA close/flush, retaining four separate read-only private snapshots. They reported no unexpected actions to the best of their recollection (not an absolute assertion). Snapshot verification does not independently attest button presses or onscreen observations.

The implementation agent subsequently read the actual private files and compared the existing primary decoder with the separate auditor. This is an implementation-context audit, not the independent review required before adoption.

## Snapshot results

All files are 131,088 bytes with owner-read-only permissions. SHA values match the Human's shell output. Both reconstruction paths agree on every pocket record, holes and first-free position. Structure/checksums pass and supported research state is reported for all four snapshots.

| Snapshot | Counter / saved statistic | Regular pocket in slot order |
| --- | --- | --- |
| E1_T1_PRE | 11 / 11 | Potion x2, Venusaurite (#533) x1, Antidote x1 |
| E1_T1_POST_DELETE | 12 / 12 | Venusaurite x1, Antidote x1 |
| E1_T2_POST_ACQUIRE | 13 / 13 | Venusaurite x1, Antidote x1, Potion x1 |
| E1_T3_POST_STACK | 14 / 14 | Venusaurite x1, Antidote x3, Potion x1 |

The exact snapshot hashes and bounded diff offsets are in [the sanitized JSON](e1-native-transition-results.json). No ROM/save bytes, private paths or raw proprietary tables are included.

## What these transitions establish

- T1: removal of a leading Potion stack with later occupied records results in compaction by the returned normal-SAVE state. The remaining two items preserve their relative order; no persistent hole remains in this case.
- T2: acquiring an absent Potion puts it in slot 2, the first empty slot after the compacted entries. It does not restore Potion's original leading position.
- T3: adding two Antidotes changes the existing slot's quantity from 1 to 3 without changing item order or creating a second stack.
- Each transition increments the save counter and saved-game statistic by one, rotates every logical section by one physical position, and retains the previous active save slot byte-for-byte.
- Complete occupied Party records and all other decoded pocket records remain unchanged across T1/T2/T3. Money deltas are 0, -200 and -400 respectively; this is consistent with the reported purchases, not a new Money capability proof.
- Sector 31 remains byte-identical. In sector 30, T1 and T2 each change only offset `0x716`; T3 changes no sector-30 bytes.

The offset `0x716` is in the established non-pocket gap `0x708..0x727` between Key Items and Balls. It must not be mislabeled as an item record or copied into a writer envelope without qualification. Cursor/count/UI linkage is a hypothesis only. Native game diffs include game-save effects; they do not alone prescribe an editor's required byte writes.

## E1 matrix update

This supplements the initial matrix in [the candidate record](e1-inventory-candidate.md); it does not adopt broader writer capability.

| Criterion / question | Updated result |
| --- | --- |
| Exact build, scatter map, catalog, independent read-only reconstruction | Existing findings retained; both production decoders accept the new snapshots |
| Leading deletion with later occupied records | PASS for the observed three-entry state: compacted by post-SAVE, remaining order preserved |
| Absent-item insertion after that deletion | PASS for observed Potion reacquisition: first-empty slot 2 |
| Different existing item's quantity transition | PASS for observed Antidote x1 to x3 |
| General compaction algorithm and runtime timing | NOT ESTABLISHED in full; snapshots do not identify when compaction occurs or every sort/configuration case |
| Non-pocket state at sector 30 0x716 | NOT ESTABLISHED: T1/T2 change it; semantic meaning and necessary writer coupling unresolved |
| Full proposed ordinary-item quantity range | NOT ESTABLISHED: source-backed existing-stack 999 bound, small native Potion/Antidote quantities only |
| Relevant custom/anti-cheat effects for the intended capability | NOT ESTABLISHED in full; broad absence not claimed |
| Nonzero keys / alternate runtime bag | Still explicitly unsupported |
| Give All | Still disabled |

## Verification and preservation

Before/after complete byte comparisons show the ROM, original frozen starting save, and all four snapshots unchanged by read-only verification. Original ROM/source SHA values reproduce the previously recorded identity. The file-name typo during T1 retention was corrected by the Human; the resulting snapshot hash was unchanged.

No tests or implementation were added or changed in this follow-up. Earlier candidate test results (9 focused passed; 238 full-suite run, 223 passed and 15 skipped) are historical results for unchanged code, not newly rerun tests. No further static disassembly was performed during this snapshot-verification step.

## Human workflow preference

For future native-game verification, the Human explicitly prefers this procedure: preserve original private inputs, use a dedicated working ROM/save copy, give one complete stage command block at a time, perform ordinary game actions and normal SAVE, fully quit/flush mGBA, retain a separately named read-only snapshot, and calculate its SHA and file size. Avoid savestate persistence evidence and unnecessary repetitive gameplay. Private artifacts and absolute paths remain outside Git/publication.

## Current stop

The Human requested a broader planning discussion in ChatGPT before further E1 analysis or E2 implementation. The discussion packet is [e1-chatgpt-handoff.md](e1-chatgpt-handoff.md). No main merge, canonical adoption, independent review or E2 implementation is part of this publication.
