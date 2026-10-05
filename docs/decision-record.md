# Canonical re-evaluation — 2026-10-05

## M4 delivery correction — controlling current decision

Later human authorization

> `AUTHORIZE M4 DELIVERY CORRECTION: replace the Tkinter adapter with a localhost-only NiceGUI browser UI using the existing S0/P/C core and verified download-output flow; retain CLI, fail-closed capability gates, private-data boundaries, and the existing no-merge boundary.`

supersedes only the earlier Tkinter adapter choice. The current bounded M4 delivery is **CLI/audit + localhost-only NiceGUI browser UI** over the same evidence-gated S0/P/C core. The browser service must remain loopback-only; remote/LAN/public exposure and external upload of private save/ROM data are not authorized. The preferred UI flow is local select/upload -> inspect/preview -> core-gated mutation -> independent verification -> verified browser download/save action. The implementation PR merge remains a separate human gate. See `docs/m4-delivery-correction.md` for the controlling delivery-layer authority.

This correction does not broaden the retained-lineage P rule, the bounded `party[0]` markings capability family, supported values, party indices, builds/versions, boxes/bags, or any writer capability.

## M4 bounded implementation authorization

PR #12 adopted `docs/m4-entry-decision.md` as the evidence-gated M4 entry design. Human authorization

> `AUTHORIZE PR #12 DESIGN MERGE AND BOUNDED M4 IMPLEMENTATION: retained-lineage S0/P/C qualification, one bounded repeated-use party[0] markings family, new-file transaction hardening, thin Tkinter/CLI delivery, and required private canaries; no arbitrary-save support and no implementation PR merge without separate authorization.`

moves the project from the M4 design boundary into a **bounded M4 implementation phase**. The later delivery correction above supersedes the Tkinter choice while retaining the rest of this authorization.

The authorized slice is limited to retained-lineage S0/P/C qualification, one bounded repeated-use `party[0]` markings family, a local/private lineage journal containing hashes and bounded metadata only, hardened new-file publication and independent verification, a reusable Python core, CLI/audit adapter, localhost-only NiceGUI browser UI, required synthetic/private/game-boundary proof work, macOS source-run validation, and preparation for later Windows validation.

This authorization does **not** permit arbitrary/non-lineage saves, broad PokemonStart build/version generalization, unrestricted values, boxes/bags, automatic live-emulator save replacement, remote/public browser exposure, protected-data publication, or merging any M4 implementation PR into `main` without a later explicit human merge authorization. See `docs/m4-bounded-implementation-authorization.md` and `docs/m4-delivery-correction.md` for the exact current scope.

## M3C closure decision after derived-stat canary

Canonical `main` before this closure merge is `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3`, which contains the human-passed low-coupling friendship/markings/ball batch. The exact derived-state group on PR #11 then proved nature mint, Attack IV, HP EV, and the required cached stats/HP update as one coupled transformation on the retained private v0.15 lineage.

The supplied combined-canary return save independently re-verifies at SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`, active slot 0/counter 6. All 28 ordinary section checksums validate; the old active slot, returned active party record, and sectors 28–31 are preserved as required; the external footer changed only under the established game-resave rule. The exact derived-state group is therefore PROVEN for the named retained-lineage transformation. Future private save outputs go outside the repository, enforced by the shared transaction writer.

Human authorization `AUTHORIZE PR #11 MERGE AND M3C CLOSURE` adopts the M3C exit assessment and closes M3C after this PR is merged. That historical authorization did not itself authorize M4; the later bounded M4 authorization recorded above supersedes that project boundary for the explicitly named slice only.

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
7. **M4 — usable editor / GUI — BOUNDED IMPLEMENTATION AUTHORIZED / IN PROGRESS.** The adopted first slice is the evidence-gated S0/P/C design from PR #12, one repeated-use `party[0]` markings family, hardened new-file transaction/publication, independent verification, CLI/audit delivery, and a localhost-only NiceGUI browser UI. Final implementation merge remains a separate human gate.

## Current position

Canonical `main` is **M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; M3B COMPLETE; M3C COMPLETE; bounded M4 implementation AUTHORIZED / IN PROGRESS.**

M3C is closed because it has a useful bounded party-edit capability set, a reusable fail-closed transaction envelope, successful low- and high-coupling game-boundary evidence, explicit unsupported capability handling, and a formal remaining-gap assessment. M4 now addresses reusable retained-lineage eligibility, repeated-use capability proof, safe publication/recovery, and user-facing delivery without broadening unsupported save scope.

## Supported-save / writer-support boundary

Writer-supported saves must pass structural eligibility, provenance/profile eligibility, and field-capability eligibility. Structural similarity alone does not prove PokemonStart build identity. Current write evidence remains limited to the retained private PokemonStart v0.15 lineage and the named exact transformations/hashes documented by the proof records.

M3C completion does not promote these exact proofs into arbitrary values, party members, save hashes, builds, or versions. M4 must independently qualify any reusable P rule and capability FAMILY before private writes are exposed.

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

For the NiceGUI browser path, verified output may be surfaced as a local browser download/save action rather than requiring a native GUI destination picker. The browser adapter still must not overwrite the input, auto-write a live emulator save, or bypass transaction/receipt verification.

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

`PROVEN` remains bounded to the documented exact private lineage and transformations.

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

The North Star is demonstrated as a bounded proof foundation. M4 is the authorized bounded effort to turn that foundation into a repeatable, safe player-facing workflow.

## Remaining risks / blocked capability surface

- PokemonStart build mismatch outside the retained private lineage;
- arbitrary external/non-lineage save support;
- target-build catalogs/semantics for Tera type, held items, moves/PP/PP-Up, abilities, species/forms, and identity-related values;
- hyper-training and broader EXP/level/stat coupling beyond the proven exact derived-state case;
- application semantics of sectors 30/31 and parasite tails beyond byte preservation;
- the root-anchored/journaled P rule remains bounded to its validated private-transition evidence and must fail closed outside it;
- the repeated-use markings FAMILY requires the adopted evidence status before private UI exposure;
- atomic/no-clobber filesystem publication semantics require platform-specific proof where that publication path is used, especially Windows validation;
- NiceGUI localhost-only delivery, verified download UX, and Windows browser-path validation remain implementation proof obligations.

## Authorization boundary for bounded M4 implementation

The original bounded M4 authorization permits:

- canonical adoption of PR #12's M4 entry design;
- implementation and testing of retained-lineage S0/P/C qualification;
- local/private retained-lineage journal work using hashes and bounded metadata only;
- research, implementation, and proof preparation for one bounded repeated-use `party[0]` markings family, nominally `0 <-> 1`, subject to fresh evidence;
- hardened new-file transaction/publication and independent receipt verification;
- reusable Python core and CLI/audit adapter;
- synthetic/regression/fault tests;
- local-private preflight and required representative private game/emulator canaries;
- macOS validation and preparation for later Windows validation;
- feature branches, commits, documentation, and review-ready implementation PR preparation.

The later delivery correction additionally permits and controls:

- replacing the Tkinter adapter with a localhost-only NiceGUI browser UI;
- local browser select/upload, preview, core-gated mutation, verified receipt, and verified download/save output flow;
- NiceGUI-specific adapter tests and dependency work;
- discontinuing Tkinter visible-event-loop debugging unless later evidence makes it necessary.

It does **not** authorize:

- arbitrary/non-lineage save support or broad PokemonStart-version generalization;
- unrestricted values or arbitrary party indices;
- boxes/bags;
- unrelated new field capabilities merely because offsets are known;
- input overwrite or automatic writing into emulator live-save locations;
- remote/LAN/public browser exposure or external private-save upload;
- protected-data publication;
- execution of blocked/proprietary binaries;
- merging any M4 implementation PR into `main` without a later explicit human merge authorization.

The next mandatory human gate is the smallest representative private game/emulator canary genuinely required by unresolved P/C semantics, an earlier consequential evidence/safety blocker, or final implementation-PR adoption/merge. A separate GUI-specific game canary is not required solely because the presentation layer is NiceGUI when it invokes the same already-proven core transaction path.
