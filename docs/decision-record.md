# Canonical re-evaluation — 2026-10-05

## PR #13 bounded implementation adoption — controlling current state

Human authorization

> `AUTHORIZE PR #13 BOUNDED M4 IMPLEMENTATION MERGE AS IN-PROGRESS: merge exact candidate 2612df5de7bac7a1ebce6650eb9ed69b440fbc4d into main; retain Windows write/download disabled and unproven, retain M4 IN PROGRESS, and do not broaden save/build/capability scope or declare M4 COMPLETE.`

adopts the exact PR #13 candidate `2612df5de7bac7a1ebce6650eb9ed69b440fbc4d` as a bounded **M4 IN PROGRESS** implementation. PR #13 was merged as `4685edd4fa61d7e02a29d1cb6279e0e8858bdaa7`.

The adopted implementation includes the retained-lineage S0/P/C core, one bounded repeated-use `party[0]` markings `0 <-> 1` FAMILY, hash/metadata-only private lineage journal, independent output auditing, macOS new-file/no-clobber filesystem publication, CLI/audit delivery, and localhost-only NiceGUI browser delivery. The exact adoption record is `docs/m4-pr13-adoption.md`.

Windows write/download remains **disabled and unproven**. Windows may perform read-only S0/P inspection, but C actions and preview/commit/download fail closed until separate Windows validation is completed and later human adoption explicitly enables that platform. M4 is **not COMPLETE**.

This adoption does not broaden arbitrary/non-lineage save support, PokemonStart build/version support, editable fields, party indices, values, boxes/bags, emulator-live-save behavior, network exposure, or protected-data publication.

## M4 delivery correction — controlling delivery decision

Human authorization

> `AUTHORIZE M4 DELIVERY CORRECTION: replace the Tkinter adapter with a localhost-only NiceGUI browser UI using the existing S0/P/C core and verified download-output flow; retain CLI, fail-closed capability gates, private-data boundaries, and the existing no-merge boundary.`

superseded only the earlier Tkinter adapter choice. The current bounded M4 delivery is **CLI/audit + localhost-only NiceGUI browser UI** over the same evidence-gated S0/P/C core. The browser service must remain loopback-only; remote/LAN/public exposure and external upload of private save/ROM data are not authorized. The preferred UI flow is local select/upload -> inspect/preview -> core-gated mutation -> independent verification -> verified browser download/save action. See `docs/m4-delivery-correction.md`.

The original no-merge boundary in that delivery correction was satisfied only for exact PR #13 by the later explicit adoption above. It does not authorize any broader or future implementation merge.

## M4 bounded implementation authorization — historical implementation authority retained

PR #12 adopted `docs/m4-entry-decision.md` as the evidence-gated M4 entry design. Human authorization

> `AUTHORIZE PR #12 DESIGN MERGE AND BOUNDED M4 IMPLEMENTATION: retained-lineage S0/P/C qualification, one bounded repeated-use party[0] markings family, new-file transaction hardening, thin Tkinter/CLI delivery, and required private canaries; no arbitrary-save support and no implementation PR merge without separate authorization.`

moved the project from the M4 design boundary into a bounded M4 implementation phase. The later delivery correction superseded the Tkinter choice while retaining the rest of this authorization, and the later PR #13 authorization separately satisfied the exact implementation-merge gate for that candidate only.

## M3C closure decision after derived-stat canary

Canonical `main` before M3C closure was `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3`, containing the human-passed low-coupling friendship/markings/ball batch. The exact derived-state group on PR #11 then proved nature mint, Attack IV, HP EV, and the required cached stats/HP update as one coupled transformation on the retained private v0.15 lineage.

The supplied combined-canary return save independently re-verifies at SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`, active slot 0/counter 6. All 28 ordinary section checksums validate; the old active slot, returned active party record, and sectors 28–31 are preserved as required; the external footer changed only under the established game-resave rule. The exact derived-state group is therefore PROVEN for the named retained-lineage transformation. Future private save outputs go outside the repository.

Human authorization `AUTHORIZE PR #11 MERGE AND M3C CLOSURE` adopted the M3C exit assessment and closed M3C. That historical authorization did not itself authorize M4; the later bounded M4 authorities above control the current slice.

## Authority and evidence discipline

GitHub `main` is the durable canonical authority. Protected binaries remain outside Git. Conclusions must distinguish repository/canonical evidence, independently checked public upstream source, local private-input verification, human observation, prior observations/command logs, and hypotheses.

Do not generalize from one successful edit or one successful batch. Unsupported, malformed, ambiguous, or unqualified saves must fail closed.

## Refined North Star

Enable a PokemonStart player to inspect a **positively supported** save, make a small **evidence-proven** party edit into a **separate output file**, independently verify that output, and retain a reliable recovery path.

A GUI is a delivery layer only after save/profile eligibility and field capability are proven. The project is not trying to maximize editable fields or reproduce a generic PKHeX-style editor by default.

## Milestone architecture

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
4. **M3B — bounded same-field transaction proof — COMPLETE.**
5. **M3C-F1 — friendship field proof — COMPLETE.** `party[0] friendship 50 -> 51` survived sealed private preflight and a human game load + normal-save round trip; PR #9 merged as `ece114d0475691e34bf4c83de2f73a9e732dd34e`.
6. **M3C — goal-driven bounded party-field expansion — COMPLETE.** Low-coupling friendship/markings/ball and the first nontrivial derived-state nature-mint/EV/IV/stat group survived representative game round trips. Remaining fields are explicitly BLOCKED/UNSUPPORTED rather than guessed.
7. **M4 — usable editor / GUI — BOUNDED IMPLEMENTATION ADOPTED / IN PROGRESS.** PR #13 merged the macOS-proven retained-lineage S0/P/C implementation, repeated-use `party[0]` markings FAMILY, independent verification, CLI/audit path, hardened macOS publication, and localhost-only NiceGUI delivery. Windows write/download remains disabled and unproven; M4 completion remains outstanding.

## Current position

Canonical `main` is **M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; M3B COMPLETE; M3C COMPLETE; bounded M4 implementation ADOPTED / IN PROGRESS.**

M4 has crossed the core product-risk boundary on macOS: repeated-use retained-lineage eligibility, both markings directions, independent auditing, CLI delivery, and localhost browser delivery are implemented and backed by the documented private/game evidence. The remaining planned milestone uncertainty is primarily platform validation on Windows, not another field-expansion cycle.

## Supported-save / writer-support boundary

Writer-supported saves must pass structural eligibility, provenance/profile eligibility, and field-capability eligibility. Structural similarity alone does not prove PokemonStart build identity. Current write evidence remains limited to the retained private PokemonStart v0.15 lineage/build/environment and the bounded capability evidence documented by the M4 records.

The repeated-use markings FAMILY does not imply arbitrary values, party members, save lineages, builds, or versions. On an unvalidated host, write authority is absent even if S0/P inspection passes.

## Reusable transaction contract retained

Every generated candidate must:

- hash/read input before mutation;
- reject input/output aliasing and existing output paths where filesystem publication is used;
- reject private output paths within the repository;
- run structural + writer-support preflight;
- locate the active logical section through verified metadata;
- require active-slot/counter parity;
- preserve physical section permutation and counters/IDs/signatures;
- mutate only explicitly capability-authorized field bytes;
- recompute only required checksum(s);
- require every output byte difference to be explained by authorized field/checksum changes;
- preserve inactive slot, sectors 28–31, parasite tails, footer, and all other bytes unless separately proven otherwise;
- re-verify generated bytes;
- prove original-input immutability;
- report exact diff and output hash.

For the NiceGUI browser path, verified output may be surfaced as a local browser download/save action rather than requiring a native GUI destination picker. The browser adapter must not overwrite the input, auto-write a live emulator save, expose remote/public listeners, or bypass transaction/receipt verification.

The external 16-byte footer is preservation-only for tool output; equality is not required after a later game/emulator resave.

## M3C execution refinement — retained as historical method

M3C separated **field-level proof** from **human-level proof**:

- each field or tightly coupled group required source-backed layout/semantics, explicit validity constraints, a named capability record, synthetic/property coverage, and private differential verification;
- fields were grouped by coupling/risk rather than arbitrary one-field milestones;
- batches generated individual variants plus a combined canary and exact manifests;
- a representative human game round trip validated each defensible group at the game boundary;
- high-coupling fields were not smuggled into low-coupling batches merely to reduce interaction count.

### Risk/coupling classes

- **L — direct / low-coupling scalar or cosmetic fields:** multi-field canaries after source/range checks.
- **M — catalog/encoding-dependent fields:** target-profile catalog/encoding proof required before mutation.
- **C — derived-state coupled fields:** coupled transformation plus derived-invariant proof required.
- **H — identity/form/system fields:** separate research gate unless evidence narrows the risk.

## Proven M3C capability set for the retained v0.15 lineage

- HP IV bounded `31 -> 30` and `30 -> 31` proofs;
- friendship `50 -> 51` and `51 -> 52`;
- markings `0 -> 1`;
- ball `3 -> 11` (Premier Ball);
- nature mint `0 -> 4` with cached stats updated;
- HP EV `0 -> 80` with max/current HP `21/21 -> 22/22`;
- Attack IV `29 -> 0` with cached Attack updated;
- the combined nature-mint + HP-EV + Attack-IV derived-state transformation.

`PROVEN` remains bounded to the documented exact private lineage and transformations. The later M4 markings FAMILY is separately bounded by its own S0/P/C evidence and does not generalize this M3C list.

## External reference policy

Pinned CFRU-JP source remains primary upstream structural/semantic evidence. Private PokemonStart saves remain the local compatibility proof. Public CFRU-family editors may be used as supporting implementation/reference evidence only and never as PokemonStart authority.

PUSE, PKForge, PKHeX-family implementations, vanilla Gen III decompilations, and UI framework documentation may inform architecture or invariants subject to their licenses, but they do not expand PokemonStart support by themselves.

## M3C exit criteria — satisfied

M3C exit required a useful bounded party-edit capability set plus a final review of remaining gaps and whether further field expansion was more valuable than delivery work. That criterion is satisfied because:

1. both low-coupling and derived-state transformations have source-backed semantics and explicit validity/coupling rules;
2. fail-closed transaction infrastructure preserves the established save envelope and rejects in-repository private output;
3. synthetic/regression tests and private complete-diff audits cover the implemented groups;
4. representative game round trips passed for both groups;
5. every proven transformation remains explicitly bounded rather than generalized;
6. remaining candidate capabilities are marked BLOCKED/UNSUPPORTED with reasons;
7. the exit assessment finds diminishing value in additional exact-field canaries absent a specific player need.

## M4 adopted evidence and remaining risks

Adopted PR #13 evidence establishes on the validated macOS environment:

- retained-lineage S0/P/C qualification;
- the bounded `party[0]` markings `0 <-> 1` FAMILY;
- representative game-boundary evidence in both directions;
- source-backed normal-save P volatility for the qualified fields with unexplained payload changes rejected;
- local hash/metadata-only lineage journaling;
- independent output receipt/diff verification;
- CLI and localhost-only NiceGUI delivery through the same core;
- macOS new-file/no-clobber publication testing;
- local regression evidence of 72/72 tests in the NiceGUI virtual environment and 71 pass / 1 optional UI simulation skip under system Python. These are local results, not GitHub Actions reproduction.

Remaining risks / blocked surface include:

- Windows NTFS publication semantics, aliases/junctions/races and durability;
- Windows private S0/P/C validation and localhost NiceGUI interaction;
- PokemonStart build mismatch outside the retained private lineage;
- arbitrary external/non-lineage save support;
- target-build catalogs/semantics for Tera type, held items, moves/PP/PP-Up, abilities, species/forms, and identity-related values;
- hyper-training and broader EXP/level/stat coupling beyond the proven exact derived-state case;
- application semantics of sectors 30/31 and parasite tails beyond byte preservation;
- opaque footer semantics beyond the adopted preservation/game-resave policy.

## Current authorization boundary

The explicit PR #13 adoption permits the exact merged bounded implementation to remain on `main` as **M4 IN PROGRESS**. It does not authorize Windows write enablement, M4 completion, capability expansion, broad save/build support, or any unrelated implementation merge.

Permitted current continuation includes cheap/reversible work needed to execute and document the existing `docs/m4-windows-validation.md` plan, feature-branch fixes necessary to complete that bounded validation, and preparation of reviewable evidence. Any protected private inputs remain outside Git.

It does **not** authorize:

- enabling Windows write/download before evidence review and explicit adoption;
- declaring M4 COMPLETE;
- arbitrary/non-lineage save support or broad PokemonStart-version generalization;
- unrestricted values or arbitrary party indices;
- boxes/bags;
- unrelated new field capabilities merely because offsets are known;
- input overwrite or automatic writing into emulator live-save locations;
- remote/LAN/public browser exposure or external private-save upload;
- protected-data publication;
- execution of blocked/proprietary binaries.

## Next decision boundary

The cheapest remaining uncertainty-reducing next step is Windows validation under `docs/m4-windows-validation.md`: synthetic/platform checks, NTFS publication proof, private Windows S0/P/C validation, and localhost NiceGUI/browser validation while writes remain disabled until adoption.

After that evidence is available, re-evaluate from fresh canonical state whether the existing cross-platform M4 completion criteria are satisfied and whether Windows write delivery and **M4 COMPLETE** should be adopted. Do not assume the existing completion criteria are immutable if new canonical evidence materially changes the decision, but do not relax them merely to declare completion.
