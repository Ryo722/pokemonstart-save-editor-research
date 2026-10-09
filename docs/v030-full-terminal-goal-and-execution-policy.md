# Exact-v0.30 full practical editor — terminal goal and execution contract

Status: **PROPOSED FOR INDEPENDENT REVIEW AND CANONICAL ADOPTION** (2026-10-09 JST). This document is not canonical until merged into `main` following the project's Human approval and review boundaries.

## Human direction and why this change is necessary

On 2026-10-09 the owner clarified that exact-v0.30 must reach the **whole requested practical editor**, including Ability, Shiny, Held Item, Pokemon PC Boxes, PC item storage, and the other requested editor features. Partial Party/Items/Money completion is an intermediate checkpoint, not terminal completion. The previous v0.22 terminal remains a completed historical milestone and must not silently define the weaker v0.30 success criteria.

Observed cause of premature closure: prior execution prompts explicitly allowed freezing a safe subset as a 'completed practical candidate', leaving mandatory gaps to later optional expansions. Preserve the subset as a useful checkpoint, but prevent a final-completion claim while any mandatory capability remains unimplemented, unqualified, unintegrated or unaccepted.

## North Star — current exact-v0.30 profile

The owner can open an ordinary game-generated exact-v0.30 save in a locally running PKHeX-familiar editor, edit/create/move ordinary supported Pokemon across Party and PC storage, edit both bag and PC-held items, safely apply the requested core attributes (including Ability, Shiny and Held Item), preview and independently verify a **new separate output save**, load it into the actual game, normally save/progress, and reopen and edit that progressed save again. Exact build and capability-specific eligibility apply. No preregistration of individual owner-save hashes is required for an otherwise qualified state.

## Mandatory terminal capabilities

1. **Party:** inspect/edit ordinary Pokemon including species, level/EXP, moves/PP/PP Up, IV/EV, nature, friendship, **Ability, Shiny and Held Item**. Support safe ordinary semantic Pokemon creation and meaningful Party slot operations.
2. **Pokemon PC storage:** display all actual v0.30 boxes/slots, edit eligible existing stored Pokemon, create/insert Pokemon into eligible empty Box slots, and safely move/deposit/withdraw ordinary Pokemon between Party and Boxes. Confirm actual storage structure/count from exact build; never assume the v0.22 25-box layout applies unchanged.
3. **Bag:** usable name-based add/set-quantity/remove editing across appropriate ordinary pockets (regular items, balls, TM/HM and berries where independently qualified), with correct capacities, compaction, ordering, encryption and checksums. Do not manufacture a catalog by guessing ID ranges.
4. **PC item storage:** inspect the game's actual item-PC storage, safely add/set/remove items and transfer items between bag and PC when supported by exact-v0.30 evidence. Distinguish item PC storage from Pokemon Boxes.
5. **Give All Supported Items:** meaningful safe, qualified ordinary catalog with pocket-capacity handling and no unsafe Key/Event item grant. A restricted 10-item recovery-only implementation is a stepping stone, not the full requested practical experience.
6. **Trainer/Money and composed workflow:** regression-safe Money editing, multi-field edits, semantic preview, independently checked output, and useful localhost-only NiceGUI Party/Boxes/Bag/Item-PC/Trainer navigation.
7. **Continuous use:** actual-game load/display/normal SAVE, owner-returned save preservation checks, reopen and second edit for representative edited capability families, including storage movement where applicable.
8. **Existing ROM-side Moemon appearance switch:** investigate and prefer the game's native switching mechanism; do not invent a persistent save field or commit proprietary visual assets. If a save-backed control is proven, add a safe corresponding editor path. This is a tracked owner requirement, with an evidence-driven feasibility decision for whether a save editor can directly control it.

Out of scope **unless separately authorized**: generic PKHeX/legality parity, cross-version support, story/events/quests/Pokedex/RTC/Key Items manipulation, ROM distribution, public release, or public-network GUI exposure. These exclusions must not be used to waive any mandatory v0.30 capability above.

## Milestones, not alternative final goals

- **V30-A — baseline product checkpoint:** currently reported local candidate, Party basics, limited inventory, Money, GUI and safe output. It is not terminal completion.
- **V30-B — Pokemon field completion:** Ability/Shiny/Held Item plus full ordinary Party-edit/create coupling and evidence.
- **V30-C — Pokemon PC completion:** ordinary edit/create/deposit/withdraw across independently mapped boxes.
- **V30-D — item storage completion:** useful bag catalogs, add/remove/quantity, PC item storage and movement; meaningful bounded Give All.
- **V30-E — integrated owner acceptance:** usability, independently verified separate SAVE, representative game load/save/return/second edit and focused independent review of all mandatory families.

Parallel evidence-first implementation is encouraged across independent families. Milestones may advance out of order; a proof requirement for one writer must not block independent work on another. Do not replace terminal criteria with whichever partial checkpoint can be completed soonest.

## Evidence and safety: non-negotiable

- Exact-v0.30 ROM and natural-save profile must be established independently; v0.22 implementations may be reused as architecture, never as automatic v0.30 qualification.
- Each writer has separate predicates and independent read-only verification; malformed/ambiguous/unsupported cases **fail closed**. Preserve save slots, counters, permutations, checksums, relevant footers/extra sectors and unrelated data.
- Source ROM/SAV immutable; write only new uniquely named files outside Git. Protect `.gba`, `.sav`, `.pks`, patches, binaries, game artwork and private identities. No unapproved host-security/credential mutations.
- Record `SYNTHETIC_STATIC_VERIFIED`, `PRIVATE_STATIC_VERIFIED`, `HUMAN_GAME_OBSERVED`, `RETURNED_SAVE_CORRELATED`, `GAME_ACCEPTED`, `AMBIGUOUS`, `NOT_TESTED` independently; no cross-family inflation. An agent cannot substitute its own reader for an independent verifier.
- For each capability, prove field encoding, dependencies/coupling, postconditions, integrity, reopen/second edit and applicable representative owner in-game acceptance. A valid file alone does not prove the requested change survived in game.
- New writer capability, merged canonical change, release, Stable promotion, scope exception, private publication and material authorization expansion remain subject to existing Human authorization/review boundaries. A goal declaration is not blanket writer-release authority.

## Product-focused execution policy (Outcome-first with Controlled data safety)

1. **Never label `V30 TERMINAL COMPLETE` while any mandatory feature lacks implementation, qualification, GUI integration or the necessary acceptance evidence.** Report the precise missing capability and fastest evidence-reducing next action instead.
2. Work autonomously through bounded locally authorized implementation and tests; prioritize existing maintained platform/library primitives and code reuse over custom infrastructure, without compromising exact-build safety. Do not repeatedly rebuild a proven Web mGBA environment or demand microapprovals for routine reversible edits.
3. Start from fresh `main` plus independently verified local candidate. Keep an explicit feature-gap checklist; resolve independent tasks in parallel or sequentially by expected progress/value. Fail-closed one field, continue another; never relax data-integrity gates to meet a deadline.
4. Timebox evidence gathering and expensive detours. Prefer a working implementation with focused regression to a large new governance/reporting process. Freeze local recoverable checkpoints frequently and retain all untracked/private work.
5. **Deadline discipline:** aim for the strongest fully verified result before the owner's 2026-10-09 afternoon departure, if feasible; no invented guarantee that a host agent will run unattended or that all features can be completed by that time. On interruption deliver a precise honest remaining-gap plan. No artificial early termination just because an intermediate safe subset works.
6. Independent review of current candidate `983fff78678170e87c1bfbec1cfa5325b7dc4418` proceeds unchanged. A positive review may authorize an intermediate adoption decision, but must **not** be called final v0.30 completion. Preserve candidate identity and review findings before follow-on development.
7. After each meaningful step, update capability matrix: `implemented / qualified / GUI-integrated / owner-game-evidenced / blocked`, supported states, proof, issue and next action. Progress metrics count owner-usable completed requirements, not the number of newly created documents or tests alone.

## Starting evidence (historical owner/agent reports; independently verify before promotion)

- Local unmerged v0.30 candidate `983fff78678170e87c1bfbec1cfa5325b7dc4418`, tree `cace395e5a0b9e89a614a5c792175ca9400b4017` (agent-reported).
- Owner-run returned-save audit: 4 returned files; 3 correlated (`inventory_quantity_berries`, `inventory_remove_balls`, `party_species_nature`) with second-edit status `PRIVATE_STATIC_VERIFIED`; one `AMBIGUOUS`; `game_accepted_cases=0`. These are owner-provided command observations, not fresh independent reviewer reproduction.
- Current canonical `main` locator at proposal preparation: `82e1abc265b70417ce6a76d1222b065cb91c0aad` (2026-10-09 fresh connector read). The v0.22 product is historically adopted; this proposal must not rewrite that history.

## Decision surface

**Proposed change:** make all listed v0.30 practical features mandatory terminal requirements, retain A–E as milestones, and ban early 'finished' declarations for subsets.
**Evidence:** owner's explicit v0.30 functionality clarification; incomplete capability matrix and local returned-save observations; canonical v0.22 goal was narrower.
**Benefit:** aligns autonomous agent efforts with the actual user-facing finished product and reduces repeated premature scope freezing.
**Risk/tradeoff:** deeper reverse engineering, possible unavailable native functionality, longer time and more private gameplay testing; deadline cannot outrank save safety.
**Downstream impact:** future v0.30 sprint prompts and review reports must cite this contract once adopted; current ongoing independent review remains frozen; no automatic adoption of any new writer.
**Exception process:** if evidence demonstrates a mandatory capability is impossible or unacceptably unsafe on exact v0.30, provide evidence, alternative, consequence and Human decision request. Do not silently redefine `COMPLETE`.
