# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Detailed proof history lives in the linked evidence/scope records; this file intentionally keeps only the current decision state.

## Controlling Human authorization

> `AUTHORIZE NORTH STAR / TERMINAL GOAL REALIGNMENT AND CANONICAL RECORD UPDATE`

This authorization realigns the project goal and milestone critical path. It does **not** itself broaden any writer eligibility, field capability, supported build, delivery exposure, or publication authority.

## North Star

For each currently supported PokemonStart build/profile, the owner should be able to take a save produced through ordinary gameplay, safely apply supported edits locally, return to the game, continue playing and saving, and later edit the newly progressed save again **without preregistering each individual save hash**.

Unsupported builds, malformed or ambiguous saves, unsupported save states, and unsupported operations must fail closed rather than be guessed.

The project optimizes for **continuous owner use on a supported current build**, not for maximizing the number of isolated proofs or fields.

## Terminal goal — current build

Deliver a **user-operable, recoverable local editor for the currently selected PokemonStart build/profile (currently exact v0.22)** that supports repeated:

`edit -> play/save -> ordinary progress -> save -> edit`

cycles on naturally progressed owner saves using **build-specific and capability-specific eligibility predicates rather than exact-save-hash allowlists**.

The editor must preserve original inputs, write only separate outputs, preview semantic and byte-level changes, verify generated outputs, and explicitly reject unsupported states.

Terminal completion for the current build requires a practical supported Money / Party / Inventory editing set sufficient for owner use, but does **not** require arbitrary values or arbitrary generation in every family.

## Terminal success characteristics

For the current exact-v0.22 build/profile, terminal completion requires:

1. exact build/profile identification remains explicit;
2. structurally valid naturally progressed owner saves can be inspected without preregistering each save SHA;
3. supported edits use capability-specific semantic/invariant eligibility checks rather than exact-save membership alone;
4. the local workflow provides inspect -> preview -> edit -> verify -> separate output;
5. an editor output can be loaded and normally saved in game;
6. after ordinary gameplay progress and another normal save, the resulting new save can be accepted again when its capability-specific predicates still pass;
7. at least one repeated editor -> game -> progress -> editor lifecycle is independently closed, and the practical supported core is extended only as needed for owner use;
8. malformed, ambiguous, incompatible, or unsupported states fail closed;
9. original ROM/save inputs remain immutable and recovery remains trivial by retaining them;
10. public release, Stable promotion, and cross-version generalization are not prerequisites for current-build terminal completion.

The key terminal distinction is therefore **repeatable editing of naturally progressed saves**, not merely successful editing of retained exact snapshots.

## Version maintenance model

Future PokemonStart versions are **not** prerequisites for completing the current-build terminal goal.

When a later version is relevant, it is onboarded separately using fresh evidence from that exact build and representative owner saves. If save layout, encoding/compression, checksums, coupling, or other relevant semantics differ, affected capabilities are requalified for that new profile rather than inferred from an older version.

A later-version onboarding cycle does not retroactively make an already completed current-build editor incomplete.

## Current position

### Stable Lane

- M1–M4: complete.
- M5A Money: implementation + lifecycle evidence complete; Stable milestone adoption still incomplete.

Stable promotion/provenance work remains available where justified, but it is not on the current practical terminal critical path.

### Fast Lab

- FL0 exact-v0.22 preparation: complete.
- FL1 practical bounded editing: complete experimentally.
- FL2 durable baseline + unified CLI: complete / merged.
- Post-FL2 private acceptance: complete for the retained exact inputs.
- Money reusable-envelope qualification: paused / incomplete; its preserved branch is evidence/partial implementation only and is not canonical writer capability.
- Exact-v0.22 Party append + Inventory insertion + localhost GUI: complete experimentally / adopted.
- Exact-v0.22 composed Party append + Antidote insertion GUI transaction: complete experimentally / adopted.

The exact-input GUI and composed creation proof mean that **absence of an editor UI or absence of a working write path is no longer the primary project gap**.

The primary practical gap is reusable eligibility on naturally progressed exact-v0.22 owner saves.

Canonical proof/scope records include:

- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`
- `docs/money-reusable-envelope-qualification.md`
- `docs/v022-creation-proofs-and-gui-prototype.md`
- `docs/v022-creation-proof-progress.md`
- `docs/v022-composed-gui-transaction-proof.md`
- `docs/v022-composed-gui-transaction-progress.md`
- `docs/v022-composed-gui-transaction-evidence.json`
- `docs/fast-lab-v022-capability.json`

## Goal-aligned milestone path

Historical M/FL milestones remain canonical evidence history. The forward practical critical path is now:

### R0 — North Star / canonical alignment — COMPLETE by this adopted record

Align the durable project definition around repeatable current-build owner use and reconcile the already-completed exact-input GUI/composition state.

### R1 — reusable-save eligibility proof — NEXT DECISION SURFACE

Prove, for the cheapest useful existing capability family on exact v0.22, that a naturally progressed save not preregistered by exact SHA can pass a strict independently checkable eligibility predicate, be edited safely, return through normal gameplay/save, progress again, and later qualify for another editor cycle.

R1 should reuse prior evidence where useful but must start from fresh canonical state and fresh immutable private inputs. The paused Money reusable branch may inform the design but is not automatically adopted or resumed.

### R2 — practical reusable core

Extend reusable eligibility only to the Money / Party / Inventory operations that materially improve owner use. Evaluate each capability family independently; one family's predicate never authorizes another by analogy.

### R3 — continuous-use GUI closure

Expose the reusable supported core through the local GUI and close an end-to-end naturally-progressed-save workflow through the actual user interface while retaining preview, verification, immutable sources, separate outputs, stale-state rejection, and fail-closed behavior.

### TERMINAL — current-build practical editor

The exact-v0.22 editor satisfies the terminal success characteristics above. Further fields, Stable promotion, public release, or another PokemonStart version become optional maintenance/expansion work rather than blockers to current-build completion.

## Shared safety contract

- source ROMs and saves remain immutable;
- writers create separate outputs only;
- malformed, ambiguous, or unsupported inputs fail closed;
- protected/private artifacts stay out of Git;
- capability support is exact-build/profile bounded;
- editor diffs remain explainable and outputs re-verify;
- emulator live-save state is never automatically overwritten;
- Fast Lab evidence does not imply Stable support;
- support for one capability or build is never inferred for another without evidence.

## Current authorization boundary

Canonical code may be used only within its already-adopted gates.

This goal realignment authorizes the documentation/current-state update only. It does **not** authorize R1 implementation or any other capability expansion.

In particular, it does not authorize:

- removal or relaxation of existing save gates;
- adoption/resumption of the paused Money reusable candidate without a new decision;
- generalized Party or Inventory reusable eligibility;
- arbitrary Pokémon synthesis/templates;
- arbitrary item IDs/quantities/slots/pockets;
- nonzero-key support;
- broader PokemonStart builds/versions;
- Stable promotion;
- public/LAN GUI exposure;
- publication of protected data.

## Next decision surface

Fresh-read current `main` again before execution and select the **cheapest uncertainty-reducing R1 proof that directly advances repeatable naturally-progressed-save editing**.

A likely candidate is a fresh bounded reusable Money proof because prior work already reached partway through the required lifecycle, but that choice must be re-evaluated from current canonical evidence rather than automatically resuming the old branch.

Any R1 implementation or broader writer eligibility requires a separate explicit Human authorization.
