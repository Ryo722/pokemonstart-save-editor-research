# Canonical re-evaluation — 2026-10-04

## Evidence hierarchy and current state

This review uses the three attached saves still accessible in this session for size and SHA-256, the user's pasted BPS application log, and the referenced conversation's analysis as distinct evidence levels. The original package, patch, source ROM, target ROM, source tree, and generated test save are not present in this workspace. Earlier conclusions are observations to reproduce, not authority. The earlier statement that sector 30 was zero was corrected by the later inspection.

The two original save attachments match at 0x20010 bytes and SHA-256. The resaved attachment has the reported new hash and same size. The prior analysis reports a valid 14-section active slot, a 100-byte party structure, a two-byte minimal edit, and in-game persistence after resave. Those deeper assertions have not been independently rerun in this repository.

## Final goal

Enable a PokemonStart player to inspect and make a small, explicitly chosen party edit to their own save, verify it, and recover the original if anything fails. A Windows GUI is a delivery option after the file format and individual field writes have evidence. The current proof justifies pursuing the goal, but does not justify treating every proposed field as safe.

## Minimal roadmap and gates

1. **Reproducible read audit.** Create an original, read-only verifier. On privately supplied originals and resaves, independently select the active slot, validate all section IDs/signatures/checksums, decode the party, and report footer and sectors 30/31 without modifying inputs. Gate: report matches known observations and handles malformed or ambiguous saves by refusing to infer.
2. **One-field writer proof.** Implement output-to-new-file only, with backup guidance and structural validation. Reproduce HP IV 31→30 on a private copy and require an allowlisted two-byte diff, checksums, RTC/footer and unrelated-sector preservation, and successful load/resave. Gate: repeatable diff and in-game round trip.
3. **Field-by-field expansion.** Test each additional field on a separate reversible fixture, including derived-stat, EXP, ID-table, and UI constraints. Gate: explicit expected diff, invariant checks, and game round trip for each field or field group.
4. **Usable editor.** Add a Windows interface only for proven fields, with read-only preview, validation, separate output path, and recovery instructions. Gate: end-to-end user test on supported save variants and clear rejection of unsupported inputs.

Current position: before gate 1 in this repository, despite a prior successful manual proof. The next bounded step is the read-only verifier. It reduces uncertainty more cheaply than building the GUI or expanding write scope.

## Adjustment to prior plan

The prior plan moved directly to a GUI exposing IV, EV, level, EXP, friendship, moves, and items. The proposed plan keeps the party-only focus and the successful HP IV proof, but moves independent read verification and one-field reproducibility ahead of a GUI. It removes unproven fields from the first release until each has evidence. The reason is concrete: only one bit-level field change has an observed game round trip, while level/EXP/stats and expanded IDs have known consistency questions. This reduces corrupted-save risk and makes failures easier to locate. It delays UI work; the change is reversible if broader field proofs arrive. Downstream GUI scope becomes an output of the gates rather than a premise.

## Authorization and risks

This repository documents research only. No permission is inferred to distribute protected inputs, run Defender-blocked executables, overwrite a save, publish a general-purpose patcher, or broaden to box editing or arbitrary fields. Public repository creation is requested here; publishing protected data is explicitly excluded. Technical risks include slot counter handling, section permutation, checksum sizing, additional sectors, RTC footer handling, field coupling, version mismatch, and IDs specific to this build. The format observations from one v0.15 save may not generalize.
