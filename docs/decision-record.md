# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Detailed proof history lives in the linked evidence/scope records; this file intentionally keeps only the current decision state.

## Current Human decision

The independently reviewed exact-v0.22 practical product candidate was explicitly authorized for adoption and merged to canonical `main` through PR #16 at merge commit `ab18419108eeed91288d440a6f154cac33a1cf2e`.

The Human has additionally adopted the **Exact-v0.22 PKHeX-like Practical Editor Expansion** as the forward product goal. E1/E2 Inventory expansion is adopted on canonical `main` through PR #21 merge commit `3eb756cb1b74fc0d58637b82e93542836fa0b290`. E3 existing-Pokémon expansion is adopted on canonical `main` through PR #23 merge commit `165dda2edbb94dca559cd426ba37189e7220f18e`, from exact reviewed candidate `084f7e8089da2450521fb3069f6b0b62e85cc99b`. E4 Party-only Pokémon creation is adopted on canonical `main` through PR #24 merge commit `146492eb2951ff10c9f7f9b83d634ac819e69993`, from exact reviewed reporting head `0ffa1fe5912201f51e4450d68205fcd51dee1e80` and Human-played implementation `3fd7c9ca43b1190feb47e89d2b1684a6344617bd`. The fresh independent-review disposition `APPROVED_FOR_HUMAN_ADOPTION_DECISION` is recorded as Human-attested fresh independent-review evidence. Future expanded writer candidates remain separately review/adoption gated before merge.

The preceding sprint authorization remains historical authority for the R1–R4 implementation work:

> `AUTHORIZE V0.22 PRACTICAL PRODUCT SPRINT REALIGNMENT AND BOUNDED R1-R4 IMPLEMENTATION`

Canonical adoption does **not** imply public release, Stable promotion, support for another PokemonStart version, public/LAN GUI exposure, protected-data publication, or speculative capability expansion. Those remain separately gated.

The detailed sprint contract remains `docs/v022-practical-product-sprint.md`.

## North Star

For each currently supported PokemonStart build/profile, the owner should be able to take a save produced through ordinary gameplay, safely apply supported edits locally, return to the game, continue playing and saving, and later edit the newly progressed save again **without preregistering each individual save hash**.

Unsupported builds, malformed or ambiguous saves, unsupported save states, and unsupported operations must fail closed rather than be guessed.

The project optimizes for **continuous owner use on a supported current build**, not for maximizing the number of isolated proofs or fields.

## Terminal goals

### Previous terminal — exact-v0.22 practical editor — COMPLETE / ADOPTED

The earlier R1-R4 terminal delivered a user-operable, recoverable exact-v0.22 Party / Items / Money editor with repeated `edit -> play/save -> progress -> save -> edit` closure. That achievement remains complete and is not invalidated by the new expansion.

### Current vNext terminal — Exact-v0.22 PKHeX-like Practical Editor

Expand the canonical exact-v0.22 editor so the owner can, through ordinary GUI controls:

- add supported ordinary items, set/change quantities, and remove them;
- use Give All Supported Items only if a safe ordinary-item catalog and pocket capacities are independently established;
- practically edit existing ordinary Party Pokémon across the supported major-field set;
- create a new ordinary Pokémon in an eligible empty Party slot from supported semantic parameters;
- retain already-proven Money editing;
- use a PKHeX-familiar Party / Items / Trainer workflow with semantic preview, verification and separate output;
- return to normal gameplay/save and later reopen the progressed save.

PKHeX parity, legality parity, Box editing, Pokédex/story/event editing, public release and cross-version support are not vNext terminal prerequisites.

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

## vNext success characteristics

For exact v0.22, vNext completion requires:

1. Money remains regression-safe at the already proven `0..9,999,999` range and is not a research priority;
2. supported ordinary-item pockets have an independently supported model for record encoding, quantity, insertion/removal, ordering and safe capacity semantics;
3. supported ordinary items can be selected by name and added, quantity-edited, and removed through the GUI;
4. Give All Supported Items exists only if the safe catalog and capacities are proven; otherwise it remains disabled without blocking terminal completion;
5. existing ordinary Party Pokémon can be edited across the practical major-field set established in E3, with all required coupling/derived values coherent;
6. the editor can construct at least a bounded general class of new ordinary Pokémon in an empty Party slot rather than only replay one exact captured record;
7. representative materially different item edits, Pokémon edits, and Pokémon creations survive exact-v0.22 load, normal use/save, and returned-save verification;
8. the GUI presents Party / Items / Trainer controls in a PKHeX-familiar workflow without exposing research internals during normal use;
9. preview -> verify -> separate output and source immutability remain mandatory;
10. unsupported, malformed, ambiguous, full-Party-without-Box, unsafe item, and unsupported field states fail closed.

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

Historical M/FL/R milestones remain canonical evidence history. R1-R4 and the previous terminal are COMPLETE / ADOPTED.

The forward critical path is now the E-series expansion defined in `docs/v022-pkhex-like-editor-expansion.md`:

### E0 — expansion contract — COMPLETE / ADOPTED

The vNext goal, success characteristics, milestone sequence, Money maintenance status, safety boundaries and non-goals are canonical.

### E1 — Inventory model qualification — COMPLETE / ADOPTED

Establish a reusable exact-v0.22 model for supported ordinary-item pockets: boundaries, record encoding, quantity representation, empty-slot semantics, ordering/compaction, safe capacity, checksum/key behavior and a safe item catalog. Prefer multi-item generalization evidence and source/ROM corroboration over serial single-item canaries.

### E2 — Practical Inventory editor — COMPLETE / ADOPTED

Canonical exact-v0.22 GUI supports the independently reviewed recovery-medicine subset with add, quantity editing, and remove under fail-closed eligibility. Give All remains disabled.

### E3 — General existing-Pokémon editor — COMPLETE / ADOPTED

The independently reviewed exact-v0.22 ordinary-class existing-Party editor is canonical through PR #23. Its adopted scope covers the qualified practical subset of species, level/EXP, four move slots with PP/PP-Up coupling, friendship, IV/EV, effective nature, ordinary ability resolution/selection, conservative held items, and required cached-stat/HP coherence. Unsupported runtime/facility contexts, exceptional species/forms/states and unsafe held-item cases remain fail-closed.

### E4 — Pokémon creator — COMPLETE / ADOPTED

The independently reviewed exact-v0.22 Party-only creator is canonical through PR #24. It constructs a bounded general class of new ordinary Pokémon in the first eligible empty Party slot from supported semantic parameters, independently reconstructs the complete record/output save, preserves unrelated state, and fails closed on unsupported contexts or a full Party with an explicit Box-not-supported reason. Box creation remains outside adopted scope.

### E5 — PKHeX-like product UX and acceptance

Deliver the PKHeX-familiar Party / Items / Trainer experience with Create Pokémon, semantic preview, verified separate output, and a representative real-game acceptance cycle spanning Items, existing-Pokémon editing, creation, and Money regression.


## Historical completed R-series

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

The exact-v0.22 R1-R4 practical editor is canonical on `main`. The Human has authorized bounded E1-E5 exact-v0.22 investigation, candidate implementation, tests, local private-input verification and review preparation under `docs/v022-pkhex-like-editor-expansion.md`.

Materially expanded writer capability remains separately review/adoption gated before merge into canonical `main`.

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

Reconstruct fresh current `main` after E4 adoption and perform a milestone-boundary check before any E5 implementation. Confirm whether E5 PKHeX-like product UX / terminal acceptance remains the cheapest goal-aligned next step, restate the authorization boundary, and only then begin bounded E5 work. E4 adoption alone does not authorize E5 implementation.
