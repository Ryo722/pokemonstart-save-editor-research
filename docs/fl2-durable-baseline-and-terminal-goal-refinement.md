# FL2 durable-baseline gate and terminal-goal refinement — 2026-10-06

Status: **CANONICAL DECISION / AUTHORIZED NEXT-WORK BOUNDARY**

GitHub `main` remains the durable canonical authority.

## Human authorization

Controlling authorization:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

This authorization adopts the milestone-boundary audit result reached after canonical two-lane adoption. It does not authorize public release, Stable promotion, broader version support, protected-data publication, or GUI exposure.

## Fresh canonical basis

The audit was performed against current `main` after the two-lane adoption. At the audit boundary:

- Stable Lane history through M4 remained complete; M5A Stable implementation/lifecycle closure evidence remained complete but adoption incomplete.
- Fast Lab FL0 and FL1 were canonically recorded as complete/complete-experimentally for exact PokemonStart v0.22.
- Exact v0.22 Fast Lab evidence covered bounded Money editing, practical/composed Party editing, and a bounded Potion quantity edit.
- The durable `main` tree did **not** yet contain the local Fast Lab implementation/test/capability-profile set that produced the FL1 evidence; canonical records explicitly stated that strategy/evidence adoption did not itself merge those local implementation commits.

This created a concrete durability/reconstruction gap: the project could describe FL1 from `main`, but could not yet reconstruct the full FL1 implementation solely from `main`.

## Refined terminal goal

The project terminal goal is now:

> **Provide a user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves that can inspect supported saves, preview supported edits, write only separate outputs, verify those outputs, and return an explicit supported/unsupported result without guessing. Exact-build capability profiles define the supported envelope. Stable Lane remains the promotion path for selected mature capabilities, not a prerequisite for completing the practical Fast Lab editor.**

This replaces an open-ended interpretation of “maximize useful editing progress.” Adding more fields, versions, or proofs is not success by itself.

### Terminal success characteristics

A practical terminal state should provide, for at least one exact supported build/profile:

- a coherent user-operable local workflow;
- inspect/preview/edit/verify semantics;
- immutable source saves and separate outputs;
- explicit capability/profile gating;
- bounded semantic and byte-diff review;
- recovery by preserving the original input;
- honest unsupported-case rejection;
- enough practical Money/Party/Inventory functionality to be useful to the owner;
- a bounded path for adding another field/build only when real use justifies it.

The terminal goal does **not** require:

- all PokemonStart versions;
- all save fields;
- PKHeX parity;
- generic CFRU support;
- every Fast Lab capability to become Stable;
- full provenance/lifecycle proof for every experimental field;
- GUI specifically, if another local interface already satisfies the user-operable goal.

## Milestone refinement

### Stable Lane

No redesign is adopted. Existing Stable milestones and evidence remain intact. Stable provenance work such as P-direct/P-reanchor is not placed on the Fast Lab critical path.

### FL0 — exact-build preparation/harness

**COMPLETE.** No change.

### FL1 — practical core editing slice

**COMPLETE EXPERIMENTALLY.** No change to the evidence classification.

### FL2 — unified practical local CLI

**RETAINED as the next practical milestone, with a required Phase 0 durable-baseline gate.**

#### FL2-G0 — durable Fast Lab baseline reconciliation

Before implementing the unified CLI, reconcile the already-existing local Fast Lab implementation into a fresh branch based on current canonical `main`.

Required outcomes:

1. fresh-read current canonical `main` and current local Fast Lab branch/state;
2. identify the exact local implementation/test/docs/capability-profile commits needed to reproduce the canonically recorded FL1 capabilities;
3. review the full reconciliation diff rather than assuming the local branch is correct because its experiments succeeded;
4. preserve Stable semantics and avoid silently broadening Stable support;
5. keep Fast Lab modules/evidence labels explicitly experimental;
6. include no ROM, save, `.pks`, BPS/IPS, executable payload, copyrighted asset, or private protected bytes;
7. reconcile the minimum implementation, tests, capability profile, and evidence pointers needed for durable reconstruction;
8. run focused and full repository tests plus static/syntax/JSON/diff/protected-artifact checks as applicable;
9. produce an exact candidate commit suitable for later canonical merge/adoption;
10. do not merge or mutate canonical `main` beyond separately authorized recording work unless the Human explicitly authorizes that candidate.

The purpose of FL2-G0 is **durability and reproducibility**, not new capability discovery.

#### FL2 implementation after G0

After the durable baseline is established, consolidate already-evidenced operations into one local CLI with at least:

- inspect save/profile;
- semantic preview;
- supported Money editing;
- supported Party editing;
- currently bounded Inventory quantity editing;
- semantic and byte-diff preview;
- separate-output write;
- output verification;
- explicit unsupported-build/field rejection.

FL2 must reuse/reconcile existing bounded logic rather than rediscover known fields or broaden ranges merely to make the CLI look complete.

## Post-FL2 work is usage-driven, not a fixed FL3 -> FL4 chain

The previous roadmap listed profile broadening before GUI/delivery. That fixed order is no longer controlling.

After FL2, choose the next milestone from actual owner use:

- **Capability expansion path:** broaden species, levels, moves, abilities, items/pockets, encryption-key handling, or later PokemonStart builds only when a concrete missing capability blocks useful work.
- **Delivery path:** improve the local UX/GUI when the editing contract and failure behavior are coherent enough that delivery adds more value than another field.
- **Stable promotion path:** strengthen selected Fast Lab capabilities only when durable support is worth the lifecycle/provenance/recovery cost.

These paths may occur in different orders. None is automatically required simply because it appears in a roadmap.

## Current risks / blockers

- The canonical record/implementation gap must be closed before FL2 should accumulate more local-only implementation.
- Ability resolution/write support remains unproven.
- Inventory evidence remains narrow: existing Potion slot 0, key 0, bounded quantities only.
- Party support remains exact-profile and bounded rather than generic.
- Nonzero-key Fast Lab support and other PokemonStart builds remain unsupported.
- Stable M5A provenance continuity remains unresolved but is not a Fast Lab blocker.

## Current authorization boundary

This decision authorizes:

- the terminal-goal refinement above;
- FL2-G0 as the mandatory first phase of FL2;
- fresh inspection/comparison of current `main` and the local Fast Lab branch needed to prepare a reconciliation candidate;
- bounded reconciliation design and candidate preparation under existing Fast Lab safety rules.

It does **not** by itself authorize:

- automatic merge of local Fast Lab implementation into `main`;
- Stable promotion;
- public release;
- GUI exposure;
- broader build/version/key support;
- protected-data publication;
- P-direct/P-reanchor implementation;
- arbitrary new field research unrelated to the FL2 critical path.

## New-chat handoff point

The next execution should begin in a fresh chat.

Fresh-start sequence:

1. fresh-read current remote `main`, including `README.md`, `docs/decision-record.md`, `docs/evidence.md`, `docs/fast-lab-two-lane-adoption.md`, and this record;
2. fresh-verify current issues/PRs and repository tree/tests as relevant;
3. inspect the local `codex/fast-lab-v022` branch/worktree and reconstruct its exact commit chain from current `main` ancestry;
4. perform FL2-G0 durable-baseline reconciliation first;
5. stop for Human review if the reconciliation would materially broaden capability or Stable semantics;
6. once G0 is accepted/merged under explicit authorization, proceed to the FL2 unified practical CLI.

## Current next step

**Start a new chat and execute FL2-G0 durable Fast Lab baseline reconciliation.**
