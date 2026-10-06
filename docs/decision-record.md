# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — FL2 durable-baseline gate + terminal-goal refinement adopted

Human authorization:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

This authorization follows the fresh milestone-boundary audit performed after canonical adoption of the Stable Lane + Fast Lab Lane architecture.

The detailed controlling record for this refinement is:

- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md`

The prior two-lane adoption record remains controlling for current v0.22 Fast Lab evidence and lane semantics:

- `docs/fast-lab-two-lane-adoption.md`

Where older roadmap wording conflicts with these later decisions, the later records control.

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can:

- inspect supported saves;
- preview supported edits;
- preserve the original input;
- write only a separate output;
- explain semantic and byte-level changes;
- verify the generated output;
- reject unsupported builds/fields rather than guess.

Exact-build capability profiles define the supported envelope.

The terminal goal is not to maximize feature count indefinitely. It does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, or Stable promotion of every Fast Lab capability.

Stable Lane remains the promotion path for selected mature capabilities, not a prerequisite for completing the practical Fast Lab editor.

## Canonical two-lane architecture

### Stable Lane

Durable supported capabilities require capability-appropriate evidence such as:

- supported-save/build gates;
- lifecycle/game-round-trip evidence where relevant;
- provenance/continuity handling;
- independent verification;
- recovery path;
- platform/delivery review;
- explicit Human adoption.

### Fast Lab Lane

Bounded exact-build experimental capabilities may progress rapidly when materially relevant conditions hold:

- exact ROM/build identity is recorded;
- the save passes the structural verifier or equivalent bounded gate;
- source ROM/save remains immutable;
- output is separate;
- byte/semantic diff is explainable;
- required checksums/invariants are correct;
- output re-verifies;
- exact-build live confirmation is obtained where cheap and informative;
- unsupported coupling/coverage is explicitly recorded.

A normal in-game SAVE round trip is not mandatory for every Fast Lab field. Fast Lab evidence does not imply Stable support.

## Shared safety contract

Both lanes retain these non-negotiable rules:

1. original/private ROMs and source saves remain immutable;
2. writers create new output files and do not overwrite sources;
3. malformed, ambiguous, and unsupported inputs fail closed;
4. protected/private artifacts do not enter Git or public distribution;
5. exact-build/version support is tracked by capability profile, not assumed across versions;
6. editor diffs remain bounded and explainable;
7. verifier/invariant checks run on generated outputs;
8. emulator live-save state is never automatically replaced;
9. public/generic support claims require later review;
10. Fast Lab and Stable evidence labels remain distinct.

## Stable Lane milestone state

Existing Stable history is preserved:

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
4. **M3B — bounded same-field transaction proof — COMPLETE.**
5. **M3C-F1 — friendship proof — COMPLETE.**
6. **M3C — bounded party-field expansion — COMPLETE.**
7. **M4 — bounded usable-editor first slice — COMPLETE.**
8. **M5A — Money Stable capability — FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.**

M5A remains bounded to its recorded v0.15 lineage/build/key/platform/journal envelope. Practical provenance continuity remains design-only. P-direct/P-reanchor are not implemented or adopted by the Fast Lab decisions.

Stable provenance work is not on the Fast Lab critical path.

## Fast Lab milestone state

### FL0 — exact-build private ROM preparation and harness — COMPLETE

Exact PokemonStart v0.22 package recovery, private ROM preparation, mGBA harness/bootstrap, read-path compatibility, and exact-build capability profile were established without committing protected artifacts.

Current exact private v0.22 build SHA-256:

`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

### FL1 — practical core editing slice — COMPLETE EXPERIMENTALLY

Exact-v0.22 Fast Lab evidence covers:

- Money editing;
- practical/composed Party editing;
- one bounded existing-item Inventory quantity edit.

Detailed evidence and limitations are in `docs/fast-lab-two-lane-adoption.md`.

### FL2 — unified practical local CLI — NEXT MILESTONE

FL2 is retained as the next practical milestone, but it now begins with a mandatory durable-baseline gate.

#### FL2-G0 — durable Fast Lab baseline reconciliation — NEXT EXECUTION STEP

Before additional CLI implementation accumulates, reconcile the already-existing local Fast Lab implementation into a fresh branch based on current canonical `main`.

Required outcomes:

- fresh-read current `main` and the local Fast Lab branch;
- reconstruct the exact local implementation/test/docs/capability-profile chain needed to reproduce FL1;
- review the full reconciliation diff instead of assuming experimental success proves implementation quality;
- preserve Stable semantics and Fast Lab experimental labels;
- include no protected/private artifacts;
- reconcile only the minimum implementation/tests/profile/evidence pointers needed for durable reconstruction;
- run focused/full tests and applicable syntax/JSON/diff/protected-artifact checks;
- produce an exact candidate commit for Human review;
- **do not merge the candidate into `main` without separate explicit Human authorization.**

The purpose of FL2-G0 is durability and reproducibility, not new capability discovery.

#### FL2 implementation after G0

After the durable baseline is accepted, consolidate already-evidenced operations into one local CLI with at least:

- inspect save/profile;
- semantic preview;
- supported Money editing;
- supported Party editing;
- currently bounded Inventory quantity editing;
- semantic and byte-diff preview;
- separate-output write;
- output verification;
- explicit unsupported-build/field rejection.

FL2 should reuse existing bounded logic and must not silently generalize capability ranges merely for completeness.

## Post-FL2 roadmap — usage driven

A fixed `FL3 profile broadening -> FL4 GUI` sequence is no longer controlling.

After FL2, choose the next milestone from actual owner use:

- **Capability expansion path:** broaden species, levels, moves, abilities, items/pockets, encryption-key handling, or later PokemonStart builds only when a concrete missing capability blocks useful work.
- **Delivery path:** improve local UX/GUI when delivery adds more value than another field.
- **Stable promotion path:** strengthen selected Fast Lab capabilities only when durable support is worth the lifecycle/provenance/recovery cost.

These paths may occur in different orders. None is automatically required merely because it appears in a roadmap.

## Current v0.22 Fast Lab evidence summary

Evidence class: **Fast Lab experimental**, not Stable.

### Money

A disposable output changed Money from `1,234,567` to `7,654,321`, updated the required checksum, passed the verifier, and was observed live under exact v0.22.

### Party

The retained party[0] 100-byte record matched offline decoding to live v0.22 memory. Successful bounded writes include friendship, IV/stat recalculation, move replacement/PP handling, level/EXP editing, Bulbasaur->Ivysaur transformation, and a composed multi-field edit whose full live party record matched offline output.

Ability-selector storage is decoded, but practical resolved-ability writing remains unproven.

### Inventory

A same-file previous/current slot differential isolated Potion item ID `13`, quantity `1 -> 2` at logical section 13 relative offset `0xADC` under encryption key `0`.

A separate-output edit changed the same existing Potion slot `2 -> 3`; the verifier accepted it and exact v0.22 live RAM showed Potion ID `13`, quantity `3` in the same slot.

This does not prove arbitrary item IDs, insertion, deletion, reordering, other pockets, nonzero-key handling, or complete pocket capacity.

## Important caveats

- The baseline retained party record contains stored level `5` with EXP `134`, while the source-derived Medium Slow threshold logic used for explicit level editing places level 5 at `135`; unrelated edits must preserve this pre-existing inconsistency rather than silently normalize it.
- Exact v0.22 startup/read-path/live-memory evidence is not broad save-migration or lifecycle proof.
- Battle behavior after species/move edits, ability resolution, evolution, Pokédex effects, move legality, and normal in-game resave behavior remain unproven unless separately recorded.
- The local Fast Lab implementation branch is not yet durably reconciled into canonical `main`; closing that gap is FL2-G0.

## Current authorization boundary

The current authorization permits:

- the terminal-goal refinement above;
- FL2-G0 durable-baseline reconciliation candidate preparation;
- fresh inspection/comparison of current `main` and the local Fast Lab branch under existing Fast Lab safety rules.

It does **not** by itself authorize:

- automatic merge of the FL2-G0 candidate into `main`;
- Stable promotion of Fast Lab capabilities;
- public release;
- GUI exposure;
- arbitrary-save or broad-version support;
- nonzero-key generalization;
- protected-data publication;
- P-direct/P-reanchor implementation;
- unrelated new-field research outside the FL2 critical path.

## Authority chain

Current key durable records:

- `docs/decision-record.md` — controlling milestone/authority state;
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md` — controlling FL2-G0 and terminal-goal refinement;
- `docs/fast-lab-two-lane-adoption.md` — controlling two-lane adoption detail and current v0.22 Fast Lab evidence;
- `docs/evidence.md`;
- `docs/m4-completion.md`;
- `docs/m5a-second-roundtrip-and-money-family.md`;
- `docs/m5a-family-closure-and-provenance-continuity-design.md`.

## Current next step

**Begin the next execution in a fresh chat with FL2-G0 durable Fast Lab baseline reconciliation.**
