# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — Money reusable-envelope qualification active

The project retains the adopted Stable Lane + Fast Lab Lane architecture and refined terminal goal.

Controlling Human authorizations now include:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

> `AUTHORIZE FL2-G0 MERGE 44c90e8217061cc8ac294a392984dfe73e622d80`

> `AUTHORIZE FL2 MERGE e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

> `AUTHORIZE EXACT-V0.22 KEY0 FIXED-TARGET MONEY REUSABLE-ENVELOPE QUALIFICATION`

FL0, FL1, FL2-G0 and FL2 are complete for the current exact-v0.22 Fast Lab slice. Post-FL2 private acceptance passed and the reviewed Phase A/B packet selected Money as the cheapest meaningful first reusable-envelope family.

The controlling next-work record is now:

- `docs/money-reusable-envelope-qualification.md`

Supporting reviewed design/evidence branch:

- branch `codex/post-fl2-acceptance-design-20261007`
- exact reviewed HEAD `93c070215181bb9e1a83c1b1b0bc82110a726793`

Where older roadmap/status wording conflicts with this record, this record controls.

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can inspect supported saves, preview supported edits, preserve original inputs, write only separate outputs, explain semantic/byte changes, verify outputs, and reject unsupported builds/fields/saves rather than guess.

Exact-build capability profiles define the supported envelope. The terminal goal does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, GUI specifically, or Stable promotion of every Fast Lab capability.

## Current terminal-state assessment

Status remains:

> **TERMINAL GOAL PARTIALLY SATISFIED — PRACTICAL REUSE NOT YET PROVEN**

The merged FL2 workflow has now passed private end-to-end acceptance on retained canaries, but reusable editing of naturally progressed owner saves is not yet proven.

Current transition:

`FL2 complete -> private acceptance PASS -> exact-v0.22 key0 fixed-target Money reusable-envelope qualification ACTIVE`

## Canonical two-lane architecture

### Stable Lane

Durable supported capabilities require capability-appropriate evidence such as supported-save/build gates, lifecycle/game-round-trip evidence where relevant, provenance/continuity handling, independent verification, recovery, delivery review, and explicit Human adoption.

### Fast Lab Lane

Bounded exact-build experimental capabilities may progress rapidly when the exact build is identified, private source artifacts remain immutable, outputs are separate, diffs are explainable, checksums/invariants hold, generated outputs re-verify, and unsupported coupling/coverage is recorded.

Fast Lab evidence does not imply Stable support.

## Shared safety contract

1. Original/private ROMs and source saves remain immutable.
2. Writers create new outputs and do not overwrite sources.
3. Malformed, ambiguous and unsupported inputs fail closed.
4. Protected/private artifacts do not enter Git or public distribution.
5. Exact-build/version support is tracked by capability profile, not inferred across versions.
6. Editor diffs remain bounded and explainable.
7. Verifier/invariant checks run on generated outputs.
8. Emulator live-save state is never automatically replaced.
9. Public/generic support claims require later review.
10. Fast Lab and Stable evidence labels remain distinct.

## Stable Lane milestone state

- **M1 — reproducible read audit — COMPLETE.**
- **M2 — exact one-field writer proof — COMPLETE.**
- **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
- **M3B — bounded same-field transaction proof — COMPLETE.**
- **M3C-F1 — friendship proof — COMPLETE.**
- **M3C — bounded party-field expansion — COMPLETE.**
- **M4 — bounded usable-editor first slice — COMPLETE.**
- **M5A — Money Stable capability — FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.**

M5A remains bounded to its recorded v0.15 lineage/build/key/platform/journal envelope. Stable provenance work remains off the Fast Lab critical path.

## Fast Lab milestone state

### FL0 — exact-build preparation/harness — COMPLETE

Exact private v0.22 build SHA-256:

`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

### FL1 — practical core editing slice — COMPLETE EXPERIMENTALLY

Exact-v0.22 Fast Lab evidence covers bounded Money editing, practical/composed Party editing, and one bounded existing-item Inventory quantity edit.

### FL2-G0 — durable Fast Lab baseline — COMPLETE / MERGED

Human-authorized candidate `44c90e8217061cc8ac294a392984dfe73e622d80` is canonical history.

### FL2 — unified practical local CLI — COMPLETE / MERGED

Human-authorized candidate `e44e85358be9a1e72e0cd84c65d446eec5bd81c2` is canonical history. The merged workflow provides exact ROM/profile gating, inspect, semantic + byte-diff preview, bounded Money/Party/Inventory operations, separate-output creation, persisted-output equality checks, verifier revalidation, and explicit unsupported rejection.

### Post-FL2 Phase A/B — COMPLETE FOR CURRENT GATE

Reviewed evidence branch `93c070215181bb9e1a83c1b1b0bc82110a726793` reports `PASS_POST_FL2_PRIVATE_ACCEPTANCE`, with the unified CLI reproducing the bounded underlying derivations and the existing live-confirmed output identities where exact historical comparison exists. Money was selected as the first reusable-envelope candidate.

This acceptance/design evidence is Fast Lab/private-input evidence and does not itself broaden canonical writer eligibility.

### Money reusable-envelope qualification — ACTIVE

Authorized scope is exactly the bounded candidate in `docs/money-reusable-envelope-qualification.md`:

- exact PokemonStart v0.22 profile only;
- encryption key 0 in both valid slots;
- fixed target Money `7,654,321` only;
- conservative two-valid-slot ordinary-counter predicate;
- Money-only replacement of exact-save SHA membership when all preregistered conditions pass;
- Party and Inventory eligibility unchanged;
- separate private outputs only;
- independent audit + repeated editor -> game -> editor proof required before qualification is complete.

## Current authorization boundary

Current work may:

- implement the exact preregistered Money-only semantic/invariant predicate on a fresh local work branch;
- connect it only to the FL2 Money inspect/preview/write path;
- add positive/negative tests and push-safe independent auditor code;
- preserve the existing exact retained Money canary output as a regression identity;
- execute the authorized private non-canary qualification proof against exact v0.22;
- perform bounded load/live confirmation, normal resave, ordinary in-game Money change, second qualification/write, reload/live confirmation and repeated-use proof;
- run focused/regression/full/static/security checks;
- prepare and push a sanitized review branch containing code/tests/docs/evidence only.

Current work does **not** authorize:

- arbitrary Money values;
- nonzero-key support;
- Party or Inventory reusable eligibility;
- combined reusable operations;
- broader PokemonStart builds/versions;
- Stable promotion;
- GUI/public release;
- protected-data publication;
- canonical `main` merge/adoption.

If the preregistered predicate is insufficient, do not relax it merely to pass the proof. Stop with `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE` and return the exact discrepancy for Human review.

## Local Codex / branch publication policy

Local Codex is the default executor for private-input work. Push-safe work branches are encouraged because they permit independent remote review, provided protected/private artifacts stay outside Git.

Allowed branch material includes source code, tests, push-safe independent auditor code, sanitized evidence/design records, hashes, sizes and non-sensitive structural/diff summaries.

Do not push ROMs, saves, `.pks`, BPS/IPS, executables, proprietary payloads, copyrighted assets, raw memory dumps, raw private command logs, or private/protected bytes.

Branch push is not adoption. Canonical `main` mutation remains a separate Human decision.

## Review loop

For this and subsequent bounded work units:

1. Codex executes the Human-authorized Goal locally.
2. Codex pushes only push-safe review material to an exact work branch.
3. ChatGPT fresh-reads canonical `main` and the exact branch HEAD, independently reviews the complete diff/evidence and reconstructs current state.
4. ChatGPT returns disposition and prepares the next bounded Human decision plus the next Codex Goal.
5. No merge/adoption or material scope expansion occurs without explicit Human authorization.

## Current next step

**Delegate the exact-v0.22 key0 fixed-target Money reusable-envelope qualification to local Codex. Require implementation + private repeated-use proof + validation + push-safe review-branch publication, then stop for independent review before any canonical merge/adoption.**
