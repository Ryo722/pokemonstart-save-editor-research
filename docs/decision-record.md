# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — exact-v0.22 composed Party append + Inventory insertion GUI transaction proof active

The project retains the adopted Stable Lane + Fast Lab Lane architecture and refined terminal goal.

Controlling Human authorizations include:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

> `AUTHORIZE FL2-G0 MERGE 44c90e8217061cc8ac294a392984dfe73e622d80`

> `AUTHORIZE FL2 MERGE e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

> `AUTHORIZE EXACT-V0.22 KEY0 FIXED-TARGET MONEY REUSABLE-ENVELOPE QUALIFICATION`

> `AUTHORIZE EXACT-V0.22 FAST-LAB PARTY-APPEND + INVENTORY-INSERTION PROOFS AND LOCALHOST GUI PROTOTYPE`

> `AUTHORIZE EXACT-V0.22 CREATION + LOCALHOST GUI FAST-LAB ADOPTION 310a982cc41a6d254eb542e4a985545c4ee7960a`

> `AUTHORIZE EXACT-V0.22 PARTY-APPEND + INVENTORY-INSERTION COMPOSED GUI TRANSACTION PROOF`

The adopted exact-v0.22 creation + localhost GUI Fast Lab slice remains canonical history. The active next-work contract is now:

- `docs/v022-composed-gui-transaction-proof.md`

Where older roadmap/status wording conflicts with this record, this later record controls.

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can inspect supported saves, preview supported edits, preserve original inputs, write only separate outputs, explain semantic/byte changes, verify outputs, and reject unsupported builds/fields/saves rather than guess.

Exact-build capability profiles define the supported envelope. The terminal goal does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, GUI specifically, or Stable promotion of every Fast Lab capability.

## Current terminal-state assessment

Status:

> **TERMINAL GOAL PARTIALLY SATISFIED — USER-OPERABLE EXACT-INPUT GUI EXISTS; COMPOSED TRANSACTION PROOF ACTIVE; PRACTICAL REUSE REMAINS INCOMPLETE**

The project has a localhost-only v0.22 GUI slice that can inspect an exact supported input, preview bounded operations, and return verified separate outputs. Party append and Inventory insertion are each experimentally proven on the exact fresh proof root and survive exact-v0.22 load, normal SAVE and cold reload.

The active gap is whether those two already-adopted primitives can be composed safely into one exact-root output and one GUI transaction without broadening writer eligibility. Reusable editing of naturally progressed outputs remains a later, separately gated problem.

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

Exact-v0.22 Fast Lab evidence covers bounded Money editing, practical/composed Party editing on existing party[0], and one bounded existing-item Inventory quantity edit.

### FL2-G0 — durable Fast Lab baseline — COMPLETE / MERGED

Human-authorized candidate `44c90e8217061cc8ac294a392984dfe73e622d80` is canonical history.

### FL2 — unified practical local CLI — COMPLETE / MERGED

Human-authorized candidate `e44e85358be9a1e72e0cd84c65d446eec5bd81c2` is canonical history. The merged workflow provides exact ROM/profile gating, inspect, semantic + byte-diff preview, bounded Money/Party/Inventory operations, separate-output creation, persisted-output equality checks, verifier revalidation, and explicit unsupported rejection.

### Post-FL2 private acceptance — COMPLETE

Reviewed evidence branch `93c070215181bb9e1a83c1b1b0bc82110a726793` reported `PASS_POST_FL2_PRIVATE_ACCEPTANCE`. That acceptance did not itself broaden canonical writer eligibility.

### Money reusable-envelope qualification — PAUSED / INCOMPLETE

Preserved branch `909e3e50d4cb6a173188d6c97538f03aed464417` contains partial implementation/evidence. It is not canonical writer capability and remains frozen unless separately resumed.

### Exact-v0.22 Party append + Inventory insertion + localhost GUI — COMPLETE EXPERIMENTALLY / ADOPTED

Canonical adopted candidate:

`310a982cc41a6d254eb542e4a985545c4ee7960a`

Adopted experimental capability boundary:

- exact v0.22 ROM/profile only;
- exact fresh proof-root save SHA only for the two creation operations;
- Party append: party count `3 -> 4`, copy the complete existing slot0 100-byte record into slot3, no internal record synthesis;
- Inventory insertion: insert Antidote ID14 quantity1 into the game-observed regular-items slot2 under key0, preserve Money and existing item order;
- both creation operations passed independent complete-candidate audit, exact-v0.22 load, normal SAVE and cold reload;
- localhost-only NiceGUI (`127.0.0.1`) exposes inspection, existing canonical FL2 operations under their unchanged gates, and the two exact creation operations;
- GUI delivery is upload/in-memory preview/verified separate download only; no live-save overwrite path;
- GUI output for the two creation operations was byte-identical to the game-confirmed non-GUI core candidates;
- Fast Lab experimental only; not Stable and not public release support.

### Exact-v0.22 composed Party append + Inventory insertion GUI transaction proof — ACTIVE

Controlling scope:

- `docs/v022-composed-gui-transaction-proof.md`

Authorized work is bounded to one exact composed transaction from the same adopted proof-root input:

- Party append using the already-adopted exact-copy shape;
- Inventory insertion using the already-adopted Antidote slot2 shape;
- exact union-of-envelopes byte proof and independent order-independence proof;
- one exact-v0.22 load -> normal SAVE -> cold reload persistence proof;
- one explicit combined localhost GUI choice whose downloaded bytes equal the game-confirmed core candidate.

This authorization does not create reusable writer eligibility and does not authorize a generic transaction engine.

## Current authorization boundary

Current work may:

- fresh-read canonical `main` and reconstruct the two adopted creation primitives;
- create a fresh work branch from canonical `main`;
- implement exactly one composed Party-append + Inventory-insertion operation from the exact adopted proof root;
- add an independent composed-candidate auditor and order-independence proof;
- run exactly one private exact-v0.22 load/normal-save/cold-reload persistence proof for that composed candidate;
- extend the localhost GUI with exactly one explicit combined operation;
- run focused/regression/full/static/security validation;
- push only sanitized source/tests/docs/evidence to a review branch.

Current work does **not** authorize:

- applying either creation operation to its own output or another naturally progressed save;
- reusable semantic eligibility for either creation operation;
- arbitrary Pokémon synthesis/templates;
- arbitrary item IDs, quantities, slots, pockets, deletion or reordering;
- composition with Money or other FL2 Party/Inventory edits;
- nonzero-key support;
- broader PokemonStart builds/versions;
- Stable promotion;
- public/LAN GUI exposure;
- paused Money reusable candidate adoption;
- protected-data publication;
- canonical `main` merge/adoption of the composed candidate without separate Human authorization.

If the exact adopted envelopes cannot be composed without speculative coupling or predicate relaxation, stop with `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`.

## Current next step

**Delegate the bounded exact-v0.22 Party-append + Inventory-insertion composed GUI transaction proof to local Codex. Require exact union-of-envelopes proof, independent candidate/order-independence audit, one game SAVE/cold-reload proof, GUI byte-equality proof, full validation and push-safe review-branch publication; then stop for independent review before any canonical merge/adoption.**
