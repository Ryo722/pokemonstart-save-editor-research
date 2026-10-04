# Canonical re-evaluation — 2026-10-04

## Evidence hierarchy and current state

This review uses current repository evidence, independently checked public CFRU-JP source, a retained private HP-IV-30 save for local verification, and older observations as distinct evidence levels. Protected binaries remain outside Git. Earlier conclusions are observations to reproduce, not authority.

Current `main` before this candidate was documentation-only and positioned the project before Gate 1. The M1 branch now contains an original read-only verifier, synthetic unit tests, and a private-input verification record. The exact candidate is still unmerged, so `main` remains the durable canonical source until human review/authorization changes that state.

The retained HP-IV-30 private save independently confirms the expected 14-section slot structure, section-specific checksums/signature, party layout, HP IV 30, sector 30 nonzero state, sector 31 zero state, and 16-byte trailing footer. The private original and normal-resave binaries are not currently available to this candidate, so the full Gate 1 reproduction requirement is not yet met.

## Final goal

Enable a PokemonStart player to inspect and make a small, explicitly chosen party edit to their own save, verify it, and recover the original if anything fails. A Windows GUI is a delivery option after the file format and individual field writes have evidence. The current proof justifies pursuing the goal, but does not justify treating every proposed field as safe.

## Minimal roadmap and gates

1. **Reproducible read audit.** Create an original, read-only verifier. On privately supplied originals and resaves, independently select the active slot, validate all section IDs/signatures/checksums, decode the party, and report footer and sectors 30/31 without modifying inputs. Gate: report matches known observations and handles malformed or ambiguous saves by refusing to infer.
2. **One-field writer proof.** Implement output-to-new-file only, with backup guidance and structural validation. Reproduce HP IV 31→30 on a private copy and require an allowlisted two-byte diff, checksums, RTC/footer and unrelated-sector preservation, and successful load/resave. Gate: repeatable diff and in-game round trip.
3. **Field-by-field expansion.** Test each additional field on a separate reversible fixture, including derived-stat, EXP, ID-table, and UI constraints. Gate: explicit expected diff, invariant checks, and game round trip for each field or field group.
4. **Usable editor.** Add a Windows interface only for proven fields, with read-only preview, validation, separate output path, and recovery instructions. Gate: end-to-end user test on supported save variants and clear rejection of unsupported inputs.

Current position: **inside M1 / Gate 1, candidate verification stage**. Synthetic tests pass and one retained private test save passes both the candidate and a separate throwaway checksum/party cross-check. Gate 1 remains open because the private original and normal-resave inputs have not yet been rerun with this exact implementation and the branch has not yet received bounded human/independent review.

## Fresh roadmap re-evaluation

No new canonical evidence justifies replacing the roadmap or broadening scope. M1 remains the cheapest, safest, highest-information next step because it converts prior manual observations into deterministic, fail-closed executable checks before any further write capability.

The new source evidence does change the certainty level within M1: section footer offsets, section-specific checksum lengths, counter-wrap behavior, SaveBlock1 party offsets, and the extended Pokemon field layout are now pinned to public CFRU-JP `main` commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`, rather than remaining only prior observations. The retained HP-IV-30 save also gives one local private-input reproduction. These advances reduce M1 uncertainty but do not remove the need to verify the original/resave pair.

The next cheapest uncertainty-reducing step after review of the branch is to run the exact verifier against the private original and normal-resave files, if/when they are available, and compare deterministic reports to the evidence ledger. No GUI or writer expansion is justified before that gate closes.

## Adjustment to prior plan

The prior plan moved directly to a GUI exposing IV, EV, level, EXP, friendship, moves, and items. The adopted plan keeps the party-only focus and the successful HP IV proof, but moves independent read verification and one-field reproducibility ahead of a GUI. It removes unproven fields from the first release until each has evidence. The reason is concrete: only one bit-level field change has an observed game round trip, while level/EXP/stats and expanded IDs have known consistency questions. This reduces corrupted-save risk and makes failures easier to locate. It delays UI work; the change is reversible if broader field proofs arrive. Downstream GUI scope becomes an output of the gates rather than a premise.

## Authorization and risks

The current authorization covers the bounded M1 read-only verifier implementation and synthetic/private local verification without publishing protected files. It does **not** authorize merging the candidate into canonical `main`, beginning M2 writer work, GUI work, overwriting saves, distributing protected inputs, executing Defender-blocked executables, publishing a general-purpose patcher, or broadening to box editing/arbitrary fields.

Known technical risks remain: PokemonStart version/build mismatch; inability to prove title identity from structural save layout alone; future variants with different signatures/layouts; section permutation and counter edge cases beyond observed inputs; emulator footer semantics (the verifier intentionally keeps 16 trailing bytes opaque); field coupling; expanded IDs; and the fact that a read-only parser passing one private file is not writer safety evidence.

A meaningful next human authorization gate is therefore: **review/merge the exact M1 candidate into `main`**. Merge should not be treated as Gate 1 completion unless the original/resave reproduction evidence is also available and satisfactory.
