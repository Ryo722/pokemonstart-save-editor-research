# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — exact-v0.22 Party append + Inventory insertion proofs and localhost GUI prototype active

The project retains the adopted Stable Lane + Fast Lab Lane architecture and refined terminal goal.

Controlling Human authorizations include:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

> `AUTHORIZE FL2-G0 MERGE 44c90e8217061cc8ac294a392984dfe73e622d80`

> `AUTHORIZE FL2 MERGE e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

> `AUTHORIZE EXACT-V0.22 KEY0 FIXED-TARGET MONEY REUSABLE-ENVELOPE QUALIFICATION`

> `AUTHORIZE EXACT-V0.22 FAST-LAB PARTY-APPEND + INVENTORY-INSERTION PROOFS AND LOCALHOST GUI PROTOTYPE`

The Money reusable-envelope qualification is now **PAUSED / INCOMPLETE** by Human choice and is not the active critical path. Its preserved review branch is:

- `codex/money-reusable-qualification-20261007`
- exact pushed HEAD `909e3e50d4cb6a173188d6c97538f03aed464417`

That branch is evidence/partial implementation only and is not canonical writer capability.

The active next-work contract is now:

- `docs/v022-creation-proofs-and-gui-prototype.md`

Where older roadmap/status wording conflicts with this record, this later record controls.

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can inspect supported saves, preview supported edits, preserve original inputs, write only separate outputs, explain semantic/byte changes, verify outputs, and reject unsupported builds/fields/saves rather than guess.

Exact-build capability profiles define the supported envelope. The terminal goal does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, GUI specifically, or Stable promotion of every Fast Lab capability.

## Current terminal-state assessment

Status remains:

> **TERMINAL GOAL PARTIALLY SATISFIED — PRACTICAL CREATION/REUSE COVERAGE INCOMPLETE**

FL2 provides a coherent exact-v0.22 inspect/preview/write/verify workflow for its bounded existing operations, and post-FL2 private acceptance passed. However, practical user-facing creation is still missing: current Party support mutates an existing party[0] record, and current Inventory support changes only an existing Potion quantity on one retained shape.

The current critical path therefore asks whether two creation primitives can be proven safely and then exposed through a local GUI:

1. append one party member by copying an existing valid 100-byte record into the first empty party slot and updating party count;
2. insert one newly observed item type into a proven empty regular-items slot derived from a normal game differential;
3. if both survive exact-v0.22 load + normal save, expose only those proven operations plus already-bounded supported operations through a localhost-only GUI prototype.

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

### Post-FL2 Phase A/B — COMPLETE FOR ITS GATE

Reviewed evidence branch `93c070215181bb9e1a83c1b1b0bc82110a726793` reported `PASS_POST_FL2_PRIVATE_ACCEPTANCE` and selected Money as a first reusable-envelope candidate. That did not broaden canonical writer eligibility.

### Money reusable-envelope qualification — PAUSED / INCOMPLETE

Preserved branch `909e3e50d4cb6a173188d6c97538f03aed464417` contains partial implementation/evidence. It established first non-canary qualification, independent audit, exact-v0.22 live acceptance, one normal save and extensive tests, but did not complete the ordinary-Money-change -> second qualification -> final repeated-use proof. It also documented unresolved custody/immutability of one previously used source pathname across the full work period.

Do not merge or reuse this partial candidate as canonical capability without a separate resume/review decision.

### v0.22 creation proofs + GUI prototype — ACTIVE

Controlling scope is `docs/v022-creation-proofs-and-gui-prototype.md`.

Authorized sequence:

1. fresh immutable private proof root from the current exact-v0.22 state;
2. bounded Party append proof using an exact existing 100-byte party record copied into the first empty slot, with party count increment and checksum handling only;
3. bounded Inventory insertion proof derived from a normal before/after acquisition differential for one previously absent regular item;
4. exact-v0.22 load + normal-save persistence gates for both operations;
5. only if both pass, a localhost-only NiceGUI v0.22 prototype exposing proven capabilities and fail-closing unsupported states.

## Current authorization boundary

Current work may:

- fresh-read current canonical `main` and current exact-v0.22 private state;
- create fresh repo-external immutable/disposable proof snapshots after independent verification;
- characterize the reported current three-Pokémon/shop-front starting state independently;
- implement and test exactly one Party append primitive based on copying one existing valid record into the first empty party slot;
- perform exact-v0.22 load/live/normal-save persistence proof for that append;
- perform one ordinary in-game acquisition of an item type absent from the regular-items pocket to characterize insertion by differential;
- implement and test exactly that observed Inventory insertion shape on an immutable pre-acquisition snapshot;
- perform exact-v0.22 load/live/normal-save persistence proof for that insertion;
- if both proofs pass, implement a localhost-only NiceGUI v0.22 prototype using the current v0.22/FL2/Fast Lab core and exposing only supported operations;
- run focused/regression/full/static/security checks;
- prepare and push a sanitized review branch containing code/tests/docs/evidence only.

Current work does **not** authorize:

- arbitrary Pokémon generation/synthesis;
- arbitrary species/PID/OT/nickname/met-data generation;
- box Pokémon creation;
- arbitrary item IDs, quantities, pockets, insertion slots, deletion or reorder;
- nonzero-key support;
- generic Party/Inventory reusable eligibility;
- broader PokemonStart builds/versions;
- Stable promotion;
- public/LAN GUI exposure;
- protected-data publication;
- use of paused Money reusable candidate code as canonical basis;
- canonical `main` merge/adoption.

If a proof requires speculative coupling beyond the bounded authorized primitive, stop with `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE` rather than silently broadening scope.

## Local Codex / branch publication policy

Local Codex is the default executor for private-input work. Push-safe work branches are encouraged because they permit independent remote review, provided protected/private artifacts stay outside Git.

Allowed branch material includes source code, tests, push-safe independent auditor/differential tooling, sanitized evidence/design records, hashes, sizes and non-sensitive structural/diff summaries.

Do not push ROMs, saves, `.pks`, BPS/IPS, executables, proprietary payloads, copyrighted assets, screenshots/raw memory containing protected bytes, raw private command logs, or private/protected bytes.

Branch push is not adoption. Canonical `main` mutation remains a separate Human decision.

## Review loop

1. Codex executes the Human-authorized Goal locally.
2. Codex pushes only push-safe review material to an exact work branch.
3. ChatGPT fresh-reads canonical `main` and the exact branch HEAD, independently reviews the complete diff/evidence and reconstructs current state.
4. ChatGPT returns disposition and prepares the next bounded Human decision plus the next Codex Goal.
5. No merge/adoption or material scope expansion occurs without explicit Human authorization.

## Current next step

**Delegate the exact-v0.22 Party-append + Inventory-insertion creation proofs to local Codex. Require fresh proof-root capture first. If and only if both creation proofs pass game/load/normal-save persistence gates, continue in the same Goal to the localhost-only v0.22 NiceGUI prototype, full validation and push-safe review-branch publication.**
