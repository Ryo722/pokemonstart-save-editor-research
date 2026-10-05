# M4 bounded implementation authorization — 2026-10-05

## Status

**AUTHORIZED / IN PROGRESS.**

Human authorization:

> `AUTHORIZE PR #12 DESIGN MERGE AND BOUNDED M4 IMPLEMENTATION: retained-lineage S0/P/C qualification, one bounded repeated-use party[0] markings family, new-file transaction hardening, thin Tkinter/CLI delivery, and required private canaries; no arbitrary-save support and no implementation PR merge without separate authorization.`

PR #12 adopted `docs/m4-entry-decision.md` as the M4 entry design. This authorization permits implementation of the bounded vertical slice defined below. It does not authorize merging an implementation PR into `main`.

## Authorized implementation scope

The bounded M4 slice may implement and privately verify:

1. retained-lineage **S0 / P / C** qualification;
2. one bounded repeated-use `party[0]` markings capability family, nominally `0 <-> 1`, only if fresh evidence continues to support that candidate;
3. a local/private retained-lineage journal containing hashes and bounded metadata only, never save bytes;
4. new-file-only transaction hardening, including independent output verification and platform-specific atomic/no-clobber publication proof work;
5. a reusable Python standard-library core;
6. a CLI/audit adapter;
7. a thin local Tkinter GUI;
8. synthetic/regression/fault tests;
9. required private preflight and representative private game/emulator canaries;
10. macOS source-run validation and preparation for later Windows validation;
11. feature branches, commits, documentation, and review-ready implementation PR preparation.

## Required trust boundaries

### S0 — structural eligibility

S0 may establish only structural/layout compatibility. It must not establish PokemonStart build identity or writer permission by itself.

### P — retained-lineage provenance/profile eligibility

P must remain rooted in positively observed private lineage evidence and independently checked environment/build evidence. Unknown or unexplained descendants fail closed. The implementation must not infer arbitrary PokemonStart v0.15 support from signature/layout similarity.

### C — capability eligibility

Historical exact proof vectors remain regression evidence. A reusable capability family requires its own bounded semantic, cross-hash, diff/checksum, negative-test, and representative game-boundary evidence before it may be exposed for private writes.

## Repeated-use requirement

The central M4 proof is continuity across a normal game save:

- start from P-qualified save A;
- apply an authorized edit into new file B;
- verify B independently;
- load B in the same qualified PokemonStart v0.15 environment and perform a normal save to produce C;
- reopen C without changing code or manually adding C's full SHA-256 to a static allowlist;
- independently re-evaluate S0, P, and C;
- expose the next bounded family action only if every gate still passes; otherwise fail closed with the unmet condition.

Success proves only the tested bounded retained-lineage continuation, not arbitrary-save or arbitrary-value support.

## Data / safety boundary

Never commit or upload ROMs, `.sav`, `.pks`, BPS/IPS patches, proprietary executables/payloads, copyrighted game assets, or private save bytes. Private outputs stay outside the repository. Inputs are never overwritten. Existing destination files are never overwritten. The tool must never auto-write into an emulator live-save location.

Do not disable Defender/Gatekeeper or create permanent security exclusions.

## Explicitly not authorized

This authorization does **not** permit:

- arbitrary/non-lineage save support;
- broad PokemonStart version/build generalization;
- unrestricted numeric/value editing;
- boxes or bags;
- new unproven fields outside the bounded first family merely because their offsets are known;
- automatic live-emulator save replacement;
- protected-data publication;
- execution of blocked/proprietary binaries;
- merging any M4 implementation PR into `main` without a later explicit human merge authorization.

## Human gates

Codex/implementation work should continue autonomously through cheap, reversible research, coding, testing, local-private preflight, documentation, and PR preparation. It should stop only for a genuinely required representative private game/emulator canary, a consequential unresolved evidence/safety decision, or final implementation-PR adoption/merge authorization.
