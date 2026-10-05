# Canonical decision record — 2026-10-05

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or adopted here.

## Controlling current decision — PR #14 adoption and bounded M4 completion

Human authorization:

> `AUTHORIZE PR #14 BOUNDED WINDOWS ADOPTION AND M4 COMPLETION: adopt and merge exact candidate a2f61ac9fa34164a531b5a884a40102de3bc52cf as bounded Windows support—semantic/browser delivery only on validated Windows build 26200.9457 and filesystem publication only to user-controlled local fixed NTFS with reparse parents rejected; retain network/removable/non-NTFS, hostile concurrent path replacement, and power-loss final-name durability as unsupported/non-claimed; retain the existing retained-lineage party[0] markings 0↔1 scope and all private-data/localhost/fail-closed boundaries; after verifying the exact merge on canonical main and reconciling canonical records, mark M4 COMPLETE for this bounded first slice. Do not broaden save/build/capability scope`

The exact PR #14 candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was merged as `2547650cf898c89450a1d95b5252cf9c52e0f634` after fresh exact-candidate review.

**M4 is COMPLETE for the bounded first slice defined below.** This does not declare general PokemonStart save-editor support.

The exact completion record is `docs/m4-completion.md`.

## Refined North Star

Enable a PokemonStart player to inspect a **positively supported** save, make a small **evidence-proven** party edit into a **separate output file**, independently verify that output, and retain a reliable recovery path.

Malformed, ambiguous, unsupported, non-lineage, or capability-ineligible saves must fail closed. The GUI is a delivery layer over proven S0/P/C authority, not a source of writer authority.

The North Star is demonstrated for the bounded M4 first slice below.

## Milestone architecture and current position

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
4. **M3B — bounded same-field transaction proof — COMPLETE.**
5. **M3C-F1 — friendship field proof — COMPLETE.**
6. **M3C — goal-driven bounded party-field expansion — COMPLETE.** Low-coupling friendship/markings/ball and the first nontrivial derived-state nature-mint/EV/IV/stat group survived representative game-boundary proofs; remaining fields were explicitly BLOCKED/UNSUPPORTED rather than guessed.
7. **M4 — bounded usable editor / GUI first slice — COMPLETE.** PR #13 established the retained-lineage S0/P/C implementation and macOS delivery; PR #14 added the reviewed bounded Windows path under the exact host/filesystem limits below.

Canonical current position is therefore:

**M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; M3B COMPLETE; M3C COMPLETE; M4 COMPLETE for the bounded first slice.**

No later milestone or general-editor expansion is automatically adopted by this completion.

## Bounded M4 support contract

Writer support remains the conjunction of three independent gates:

- **S0 — structural eligibility:** supported save size/layout, checksums, unique active slot, counter/parity, section permutation, and party structure;
- **P — provenance/profile eligibility:** the retained, root-anchored private PokemonStart v0.15 lineage bound to the independently selected ROM/build and local environment through the private hash/metadata-only journal;
- **C — capability eligibility:** only the separately proven reusable `party[0]` markings `0 <-> 1` FAMILY with exact starting-state preconditions.

Structural similarity alone does not prove PokemonStart build identity. A ROM hash alone does not prove arbitrary save provenance. Unknown or unjournaled saves remain read-only even if S0 passes.

The M4 FAMILY does not imply arbitrary markings values, party indices, save lineages, builds, versions, or other fields.

## Reusable transaction contract

Every generated candidate must:

- hash/read the input before mutation;
- reject unsupported S0/P/C state;
- reject stale plans;
- mutate only capability-authorized bytes;
- recompute only required checksum(s);
- explain every output byte difference;
- preserve section metadata/permutation, counters, inactive slot, sectors 28–31, parasite tails, footer, and every other unqualified byte;
- independently re-verify the output;
- preserve source immutability;
- retain the original input as the recovery anchor;
- never automatically overwrite an emulator live-save path.

Where filesystem publication is used, the destination must be a separate nonexistent path; input aliases, existing destinations, repository destinations, and unsupported platform/filesystem boundaries fail closed.

## Adopted delivery

### macOS

The adopted macOS path provides:

- S0/P/C inspection and preview;
- CLI/audit delivery;
- localhost-only NiceGUI browser delivery;
- independently verified in-memory browser download;
- staged/no-clobber new-file publication with the adopted macOS fault/race tests.

PR #13 exact candidate `2612df5de7bac7a1ebce6650eb9ed69b440fbc4d` was merged as `4685edd4fa61d7e02a29d1cb6279e0e8858bdaa7` under the earlier explicit M4 IN PROGRESS authorization.

### Windows

Semantic/in-memory/browser delivery is positively enabled only when the explicit host gate accepts validated Windows build `26200.9457`.

Windows filesystem publication additionally requires:

- actual Windows;
- local fixed volume;
- NTFS;
- user-controlled destination directory under the adopted threat model;
- no reparse-point component in the existing destination parent chain;
- new `.sav` destination outside the repository;
- no source/destination alias and no existing destination.

Network, removable, non-NTFS, reparse-parent, or unvalidated-build cases fail closed.

The Windows publisher stages complete bytes in the destination directory, flushes the staged file, rereads and independently audits the staged bytes, rechecks source immutability, exposes the final name through a no-clobber same-directory hard link, rereads/audits the final bytes, and rechecks the source again. Post-publication cleanup removes a final entry only when it is still demonstrably the transaction-owned hard link.

### NiceGUI network boundary

NiceGUI remains localhost-only:

- host `127.0.0.1`;
- `on_air=False`;
- no relay/LAN/public listener;
- no external private-save upload;
- no automatic emulator live-save replacement.

The browser exposes only actions returned by the core. Download becomes available only after the core mutation and independent receipt audit succeed.

## M4 completion evidence

### Shared semantic/game evidence

The repeated-use markings FAMILY has representative retained-lineage game-boundary evidence in both directions. A new game canary was not required merely because the delivery host changed; Windows validation targeted platform-specific publication, delivery, S0/P/C, and fail-closed behavior.

### macOS evidence

Adopted PR #13 records the retained-lineage S0/P/C implementation, repeated-use markings FAMILY, independent auditing, CLI path, localhost browser workflow, hardened new-file publication, and local regression results. These are local execution results, not GitHub Actions reproduction.

### Windows evidence

PR #14 records actual Windows 11 build `26200.9457` execution on local NTFS. The selected ROM/build and retained root were independently rehashed locally. A fresh Windows-local journal passed S0/P and returned only the bounded markings action under the validation gate.

One private local-NTFS output was created during the validation phase. The normal receipt and a separate complete-byte audit passed; exactly the markings byte and one required section checksum byte changed, all section checksums passed, preserved regions stayed unchanged, and the source remained immutable. NiceGUI produced identical verified bytes without adding a duplicate lineage edge.

After production integration, a read-only check reproduced the same preview/output identity through the production host gate and audit path without creating another private output or game canary.

The recorded integrated Windows suite result is **88 tests OK with 12 macOS-only skips**, covering production core/CLI/NiceGUI, localhost listener, NTFS publication success, aliases/junctions, race/fault/process-exit cases, unsupported-volume decisions, and unvalidated-build rejection. These are local execution results, not GitHub Actions reproduction.

See `docs/m4-windows-candidate-evidence.md` and `docs/m4-completion.md` for the detailed evidence labels and limits.

## Explicit unsupported / non-claimed surface after M4 completion

M4 completion does **not** authorize or claim:

- arbitrary/non-lineage save support;
- broad PokemonStart build/version generalization;
- arbitrary party indices or unrestricted values;
- additional fields merely because offsets are known;
- boxes/bags;
- target-build catalogs/semantics for Tera type, held items, moves/PP/PP-Up, abilities, species/forms, or identity-related values;
- broader hyper-training or EXP/level/stat coupling beyond the exact proven historical groups;
- remote/LAN/public browser exposure;
- automatic live-emulator save replacement;
- network/removable/non-NTFS Windows filesystem publication;
- support for Windows builds that fail the exact validated-host gate;
- resistance to hostile concurrent parent-junction/final-name replacement after validation checks;
- Windows directory-metadata or final-name persistence across sudden power loss;
- general Windows filesystem safety beyond the adopted local fixed NTFS boundary;
- actual Windows symlink-fixture execution where the validation account lacked that privilege.

The application semantics of sectors 30/31 and parasite tails remain preservation-oriented rather than generally decoded. The external footer remains preservation-only for editor output and may change under a later normal game/emulator save according to the established policy.

## Authority chain

Key durable authority/evidence records are:

- `docs/evidence.md`
- `docs/m3a-support-envelope-findings.md`
- `docs/m3c-exit-assessment.md`
- `docs/m4-entry-decision.md`
- `docs/m4-bounded-implementation-authorization.md`
- `docs/m4-delivery-correction.md`
- `docs/m4-pr13-adoption.md`
- `docs/m4-windows-validation.md`
- `docs/m4-windows-candidate-evidence.md`
- `docs/m4-windows-bounded-integration-authorization.md`
- `docs/m4-completion.md`

The PR #14 completion authorization supersedes earlier statements that Windows write/download was disabled or that M4 remained IN PROGRESS, but only inside the exact bounded support contract above.

## Authorization boundary after M4

The completed first slice may be used and maintained within its adopted scope. Normal bug fixes, tests, and documentation that do not broaden writer authority remain bounded maintenance.

Any material expansion of writer capability, save provenance, supported builds/versions, party indices, editable fields, public distribution/release guarantees, network exposure, or threat model requires fresh evidence. If it exceeds existing Human authorization, present a decision surface with proposed change, evidence, benefit, risk/trade-off, and downstream impact before canonicalizing it.

No M5 or broader general-editor milestone is adopted merely because M4 is complete. The next milestone, if any, must be justified from a fresh canonical re-evaluation rather than inherited automatically from an old roadmap.
