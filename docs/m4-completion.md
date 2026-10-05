# M4 bounded first-slice completion — 2026-10-05

## Human authorization

> `AUTHORIZE PR #14 BOUNDED WINDOWS ADOPTION AND M4 COMPLETION: adopt and merge exact candidate a2f61ac9fa34164a531b5a884a40102de3bc52cf as bounded Windows support—semantic/browser delivery only on validated Windows build 26200.9457 and filesystem publication only to user-controlled local fixed NTFS with reparse parents rejected; retain network/removable/non-NTFS, hostile concurrent path replacement, and power-loss final-name durability as unsupported/non-claimed; retain the existing retained-lineage party[0] markings 0↔1 scope and all private-data/localhost/fail-closed boundaries; after verifying the exact merge on canonical main and reconciling canonical records, mark M4 COMPLETE for this bounded first slice. Do not broaden save/build/capability scope`

## Exact adoption

PR #14 exact candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was reviewed against canonical `main` and merged as `2547650cf898c89450a1d95b5252cf9c52e0f634`.

This completes M4 only for the approved bounded first slice:

- retained private PokemonStart v0.15 lineage/build/environment;
- S0 structural eligibility + retained-lineage P + capability C separation;
- one repeated-use `party[0]` markings `0 <-> 1` FAMILY;
- immutable input and separate verified output;
- independent semantic/byte/checksum audit;
- CLI/audit delivery;
- localhost-only NiceGUI browser delivery;
- macOS new-file/no-clobber publication;
- Windows semantic/browser delivery only on validated Windows build `26200.9457`;
- Windows filesystem publication only to user-controlled local fixed NTFS with every existing destination-parent component non-reparse.

## Completion evidence

### Shared/game evidence

The bounded markings FAMILY has representative game-boundary evidence in both directions from the retained lineage. The Windows work did not repeat that semantic game canary merely because the host OS changed; the platform-specific work instead validated Windows delivery, publication, S0/P/C, and fail-closed behavior.

### macOS

Adopted PR #13 established the bounded S0/P/C core, repeated-use markings FAMILY, independent auditing, CLI delivery, localhost-only NiceGUI delivery, and hardened new-file/no-clobber macOS publication. The recorded local regression result was 72/72 in the NiceGUI environment, with the system-Python run differing only by the optional NiceGUI simulation skip.

### Windows

PR #14 recorded actual Windows 11 build `26200.9457` execution. The Windows-local private root and selected ROM/build were independently rehashed and the fresh Windows-local journal passed S0/P. The core returned only the bounded markings action. One private local-NTFS output passed the normal receipt and a separate complete-byte audit with only the markings byte and required section checksum byte changed. The source stayed immutable. NiceGUI returned identical verified bytes without a duplicate lineage edge.

The integrated production-path Windows suite recorded 88 tests OK with 12 macOS-only skips. It covered the production core, CLI, NiceGUI browser simulation, loopback listener, NTFS publication success, no-clobber/race/fault/process-exit cases, reparse/junction rejection, unsupported-volume decisions, and unvalidated-build rejection. A later read-only production-path check matched the already audited private output without creating another save or game canary.

These are local execution results, not GitHub Actions reproduction.

## Windows supported boundary

Windows semantic/browser delivery is positively enabled only when the exact validated host gate accepts Windows build `26200.9457`.

Windows filesystem publication additionally requires:

- actual Windows;
- a local fixed volume;
- NTFS;
- a user-controlled destination directory under the adopted threat model;
- no reparse-point component in the existing destination parent chain;
- a new `.sav` destination outside the repository;
- no input/output alias and no existing destination.

Publication stages complete bytes in the destination directory, flushes the staged file, independently audits stage and final bytes, rechecks source immutability, and exposes the final name through a no-clobber same-directory hard link. The original save remains the recovery anchor.

## Explicit unsupported / non-claimed surface

M4 completion does **not** claim:

- arbitrary/non-lineage saves;
- other PokemonStart builds or versions;
- other party indices;
- unrestricted markings values;
- additional fields, boxes, or bags;
- network/removable/non-NTFS Windows filesystem publication;
- remote/LAN/public NiceGUI exposure;
- automatic emulator live-save replacement;
- resistance to hostile concurrent parent-junction/final-name replacement after path validation;
- Windows directory-metadata or final-name persistence across sudden power loss;
- general Windows support when the exact validated host gate does not pass;
- actual Windows symlink-fixture execution where the host account lacked that privilege.

These are retained limitations, not hidden completion assumptions.

## Milestone disposition

**M4 — COMPLETE for the bounded first slice above.**

This is not a declaration that the overall project is a general-purpose PokemonStart editor. Any broader save provenance, build/version support, field capability, packaging/release scope, or security/threat-model expansion requires fresh evidence and, where it materially expands scope or writer capability, a new Human authorization decision.
