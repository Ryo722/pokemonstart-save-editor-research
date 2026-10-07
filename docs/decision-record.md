# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Detailed proof history lives in the linked evidence/scope records; this file intentionally keeps only the current decision state.

## Current Human decision

The independently reviewed exact-v0.22 practical product candidate was explicitly authorized for adoption and merged to canonical `main` through PR #16 at merge commit `ab18419108eeed91288d440a6f154cac33a1cf2e`.

The preceding sprint authorization remains historical authority for the R1–R4 implementation work:

> `AUTHORIZE V0.22 PRACTICAL PRODUCT SPRINT REALIGNMENT AND BOUNDED R1-R4 IMPLEMENTATION`

Canonical adoption does **not** imply public release, Stable promotion, support for another PokemonStart version, public/LAN GUI exposure, protected-data publication, or speculative capability expansion. Those remain separately gated.

The detailed sprint contract remains `docs/v022-practical-product-sprint.md`.

## North Star

For each currently supported PokemonStart build/profile, the owner should be able to take a save produced through ordinary gameplay, safely apply supported edits locally, return to the game, continue playing and saving, and later edit the newly progressed save again **without preregistering each individual save hash**.

Unsupported builds, malformed or ambiguous saves, unsupported save states, and unsupported operations must fail closed rather than be guessed.

The project optimizes for **continuous owner use on a supported current build**, not for maximizing the number of isolated proofs or fields.

## Terminal goal — current build

Deliver a **user-operable, recoverable local editor for the exact PokemonStart v0.22 profile** that supports repeated:

`edit -> play/save -> ordinary progress -> save -> edit`

cycles on naturally progressed owner saves using build-specific and capability-specific eligibility predicates rather than exact-save-hash allowlists.

The practical terminal surface is intentionally bounded to a useful **Party / Items / Money** product slice. It must preserve original inputs, write only separate outputs, preview semantic changes, verify generated outputs, and explicitly reject unsupported states.

The GUI should be immediately understandable to a user familiar with PKHeX, but PKHeX visual parity, legality parity, or broad feature parity is not required.

## Terminal success characteristics

For exact v0.22, terminal completion requires:

1. exact build/profile identification remains explicit;
2. structurally valid naturally progressed owner saves can be inspected without preregistering each save SHA;
3. supported edits use capability-specific semantic/invariant eligibility checks rather than exact-save membership alone;
4. Money is practically editable within the independently supported exact-v0.22 representation;
5. existing Party members have a useful editable subset covering the fields needed for practical owner use, with required coupling/derived values kept coherent;
6. Inventory has a useful regular-item editing subset, including insertion/removal only where pocket/slot/capacity semantics are independently supported;
7. normal GUI use requires no raw JSON, save hashes, sector offsets, or checksum knowledge;
8. the GUI provides inspect -> edit -> semantic preview -> verify -> separate output;
9. an editor output can be loaded and normally saved in game;
10. after ordinary gameplay progress and another normal save, the newly changed save can qualify for another editor cycle when its capability-specific predicates still pass;
11. at least one two-cycle naturally-progressed-save workflow is closed through the actual GUI;
12. malformed, ambiguous, incompatible, or unsupported states fail closed;
13. original ROM/save inputs remain immutable and recovery remains trivial by retaining them;
14. public release, Stable promotion, cross-version generalization, Box editing, Pokédex/event/story editing, and arbitrary Pokémon synthesis are not prerequisites.

`Give All Items` is a stretch goal: implement only if a safe exact-v0.22 ordinary-item set and pocket capacities can be derived without guessing. Its absence does not block terminal completion.

## Version maintenance model

Future PokemonStart versions are **not** prerequisites for completing the current-build terminal goal.

When a later version is relevant, it is onboarded separately using fresh evidence from that exact build and representative owner saves. If save layout, encoding/compression, checksums, coupling, or other relevant semantics differ, affected capabilities are requalified for that new profile rather than inferred from v0.22.

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
- Post-FL2 private acceptance: complete for retained exact inputs.
- Frozen Money reusable-envelope work exists on `codex/money-reusable-qualification-20261007`; it is reference/evidence only until reconciled against current `main`.
- Exact-v0.22 Party append + Inventory insertion + localhost GUI: complete experimentally / adopted.
- Exact-v0.22 composed Party append + Antidote insertion GUI transaction: complete experimentally / adopted.

The reusable exact-v0.22 practical product is now **canonical and adopted on `main`**. R1–R4 and the current-build terminal objective are complete. Remaining work is optional qualification, maintenance, packaging, or separately authorized capability expansion.

## Goal-aligned milestone path

Historical M/FL milestones remain canonical evidence history. The forward critical path is now one bounded product sprint:

### R0 — North Star / canonical alignment — COMPLETE

The terminal objective is repeatable exact-v0.22 owner use, not isolated proofs or broad field count.

### R1 — reusable exact-v0.22 eligibility — COMPLETE / ADOPTED

Replace exact-input-save SHA membership as the primary write gate for the first useful capability family, initially favoring Money if fresh evidence still makes it the cheapest path. Eligibility must remain exact-build and capability-specific, independently checkable, and fail closed.

The frozen Money branch may be inspected but may not be adopted wholesale without reconciliation.

### R2 — practical reusable core — COMPLETE / ADOPTED

Build the useful Party / Items / Money core:

- Money: practical current-value -> supported-target editing;
- Party: existing-party editing through a useful exact-v0.22 subset, prioritizing species, level/EXP, moves/PP, friendship, IV/EV, and required cached/derived stat coherence;
- Inventory: practical regular-item editing, with quantity/edit/insert/remove only for independently supported pocket semantics;
- Give All Items: stretch only, ordinary supported items only, no guessed key/event/story items.

Each capability family owns its own predicate; support is never inferred by analogy.

### R3 — PKHeX-familiar continuous-use GUI — COMPLETE / ADOPTED

Turn the localhost GUI from a research operation/JSON surface into an ordinary editor UI with Party, Items, Trainer/Money, semantic preview, verified export, and Advanced diagnostics. Keep the server on `127.0.0.1` and preserve stale-state rejection, source immutability, separate outputs, and verification.

### R4 — product acceptance / repeated-use closure — COMPLETE / ADOPTED

Close a real two-cycle workflow through the GUI:

`unknown-SHA natural save -> GUI edit/export -> game normal save -> ordinary progress/save -> GUI edit/export -> game normal save`

Use a composed practical edit across Money / Party / Inventory where each predicate independently passes. Human emulator/game interaction may remain the final bounded acceptance gate after the agent completes all non-human implementation/tests/audits/docs.

### TERMINAL — exact-v0.22 practical editor — COMPLETE / ADOPTED

The canonical product satisfies the terminal success characteristics above. The reviewed product candidate was merged through PR #16. Further fields, Stable promotion, public release, another PokemonStart version, Box support, or broader PKHeX parity are optional maintenance/expansion work and are not required to preserve terminal completion.

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

The exact-v0.22 practical editor is now canonical on `main`. No additional merge is pending for R1–R4.

The following still require separate justification/authorization as applicable:

- public release / release artifact publication;
- Stable promotion;
- another PokemonStart build/version;
- generic CFRU editor scope;
- Box, Pokédex, story, quest, event-flag, RTC, or unrelated save-system editing;
- arbitrary Pokémon synthesis or broad template/catalog features;
- unproven item pockets, capacities, compaction, or unsafe all-items behavior;
- public/LAN GUI exposure;
- protected/private data publication.

## Next execution step

No terminal-critical implementation remains for exact v0.22. Default next work is to use the canonical editor in ordinary owner use and only open new work when concrete evidence justifies it. High-value optional follow-ups are: packaging/run ergonomics, a fresh stat-changing normal-save proof if wider Party stat support is desired, a GUI-created Antidote round trip, broader regular-item semantics only after exact evidence, and future-version onboarding when a new PokemonStart version actually matters.
