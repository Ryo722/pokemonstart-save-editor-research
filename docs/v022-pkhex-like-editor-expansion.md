# Exact-v0.22 PKHeX-like practical editor expansion — canonical scope

Date: 2026-10-07

Canonical base at adoption proposal: `4011853fb7903be6dc46be3f87a3240fdc25f818`.

## Human decision

The Human explicitly adopted the vNext goal and E0-E5 milestone design after the previous exact-v0.22 practical editor reached terminal completion.

This is a substantive capability expansion beyond the completed R1-R4 terminal. It authorizes bounded exact-v0.22 investigation, candidate implementation, tests, local private-input verification, and review preparation inside E1-E5 without requiring a new approval for every internal substep.

It does **not** pre-authorize merging future writer expansions into `main`, public release, Stable promotion, another PokemonStart version, Box editing, Pokédex/story/event/quest/RTC mutation, unsafe key/event-item grants, protected-data publication, or public/LAN GUI exposure. Each material candidate remains reviewable and fail-closed.

## vNext North Star

For the exact PokemonStart v0.22 profile, provide an editor that is useful in the same way the owner reaches for PKHeX: open a naturally progressed save, perform the ordinary edits they actually want, preview the semantic result, export a separately verified save, return to normal gameplay, save again, and later reopen the progressed save.

The goal is **PKHeX-like practical operation**, not PKHeX feature parity or legality parity.

## vNext terminal goal

Deliver an **Exact-v0.22 PKHeX-like Practical Editor** in which the owner can, through ordinary GUI controls:

1. add supported ordinary items;
2. set, change, and remove supported ordinary-item quantities;
3. optionally use **Give All Supported Items** only if a safe ordinary-item catalog and pocket capacities are independently established;
4. edit existing ordinary Party Pokémon across a practical major-field set;
5. create a new ordinary Pokémon in an empty Party slot from supported parameters rather than only copying one exact captured record;
6. edit Money over the already proven range;
7. use a PKHeX-familiar Party / Items / Trainer workflow without entering hashes, offsets, JSON, or checksum details;
8. preview semantic changes and export a separately verified save;
9. load the output in exact v0.22, continue ordinary gameplay and normal saves, and later edit the progressed save again.

Unsupported states and operations must fail closed.

## Current baseline

### Money — DONE / maintenance-only

Canonical exact-v0.22 Money editing already supports `0..9,999,999` under its proven reusable predicate and has survived the adopted two-cycle GUI/game workflow.

Do not spend expansion effort on Money unless regression, a new key/state, or new evidence creates a concrete need.

### Inventory — insufficient for vNext

Current canonical support is deliberately narrow:

- Potion quantity `1..3`;
- Antidote x1 insertion/removal only in the exact observed third-slot shape;
- key0 only;
- no general pocket capacity/order/compaction claim;
- no broad ordinary-item catalog;
- no Give All.

### Party editing — insufficient for vNext

Current canonical product proves a practical but narrow subset:

- Friendship broadly under the ordinary-record predicate;
- bounded Move 1 Pound/Tackle replacement;
- level-5-only Bulbasaur/Ivysaur source-backed stat edits;
- no general level/EXP model;
- no general species/moves/nature/ability/held-item editor.

### Pokémon creation — proof exists, general creation does not

One exact complete game-generated Rattata record was imported into an empty Party slot and survived display, healing, battle, normal save and returned-save verification.

This proves that a complete valid record can be appended safely under the proven envelope. It does **not** prove arbitrary record synthesis or generic Pokémon creation.

## Milestones

### E0 — expansion contract — COMPLETE when adopted

Success:
- vNext North Star and terminal goal are canonical;
- Money is explicitly maintenance-only;
- E1-E5 sequence and boundaries are canonical;
- protected-data and fail-closed rules remain unchanged.

### E1 — Inventory model qualification — COMPLETE / ADOPTED

Goal: replace one-item canaries with an independently supported exact-v0.22 regular-inventory model.

Prefer generalization evidence over serial one-item proofs.

Success requires enough independent exact-v0.22 evidence to establish, for each supported ordinary pocket:

- pocket location/boundary;
- record encoding and quantity representation;
- empty-slot semantics;
- ordering/sorting behavior where relevant;
- insertion behavior;
- removal behavior and whether compaction occurs;
- usable capacity or a safe lower bound sufficient for supported operations;
- checksum coverage;
- key/encryption behavior;
- interaction with save-slot rotation;
- a source-backed or independently derived catalog of item IDs safe for that pocket;
- explicit exclusion of unknown/key/event/story-sensitive entries;
- an independent read-only/audit implementation that can validate the model.

Use multiple native game transitions and/or exact-build source/ROM evidence to test the model. Do not infer general support from Potion/Antidote alone.

### E2 — Practical Inventory editor — COMPLETE / ADOPTED

Goal: turn E1's model into ordinary item editing.

Terminal E2 behavior:

- choose a supported ordinary item by name;
- add it when absent and capacity/order predicates permit;
- set/change quantity within the independently supported range;
- remove it safely;
- preserve unrelated records/state;
- verify complete output and capability-specific postconditions;
- expose the operations in the GUI.

At least multiple materially different supported items must independently survive editor -> game load -> normal save. One-item success is not sufficient to call the model general.

**Give All Supported Items** is allowed only if E1 establishes a safe catalog and sufficient pocket capacities/order semantics. It means supported ordinary items only; it must never blindly enumerate all item IDs or include unproven key/event/story items.

### E3 — General existing-Pokémon editor — COMPLETE / ADOPTED

Goal: make existing ordinary Party Pokémon practically editable beyond the current canary models.

Target major fields:

- species;
- level / EXP;
- moves 1-4;
- PP and PP-Up coupling where applicable;
- friendship;
- IVs;
- EVs;
- nature;
- ability / ability selector only when the exact resolution rule is established;
- held item.

Required derived/cached values must remain coherent after every edit.

Success requires:

- exact-v0.22 field/coupling model rather than species-specific hard-coded canaries;
- evidence across multiple naturally generated species and levels;
- exact-build qualification of the stat/EXP rules actually used by the patched game;
- bounded legal ranges and fail-closed unsupported combinations;
- independent byte-envelope/postcondition auditing;
- game load + normal-save evidence for representative composed edits.

Nickname, OT identity, gender, shiny/PID manipulation, ball, markings and other fields may remain later expansion unless evidence makes them cheap and safe. Do not let them block the practical major-field goal.

### E4 — Pokémon creator — NEXT / NOT STARTED

Goal: create a new ordinary Pokémon in the first empty Party slot from supported semantic parameters.

This must be true record construction/generalization, not only replay of one exact captured 100-byte record.

Initial vNext creation scope is **Party only**. Box creation is separately gated.

Success requires:

- a complete exact-v0.22 ordinary Pokémon record model sufficient for creation;
- supported selection of species and level plus the major fields needed to produce a coherent usable Pokémon;
- deterministic handling or safe generation/preservation rules for every required record field;
- required Party count/checksum updates;
- no unexplained mutation of Pokédex/story/event/Box state;
- at least two materially different created Pokémon/species or creation parameter sets surviving load, summary display, healing, battle/use, normal save, and returned-save verification;
- repeated creation on naturally progressed saves where the Party has capacity.

When Party is full, fail closed with an explicit Box-not-supported reason.

### E5 — PKHeX-like product UX and acceptance

Goal: make the supported capabilities feel like an ordinary save editor rather than a research interface.

Party:
- six visible Party slots/cards;
- select a member to edit;
- clear Main / Stats / Moves-style controls;
- dropdowns for supported species/moves/items;
- numeric level/IV/EV/friendship controls;
- explicit read-only reason for unsupported fields;
- **Create Pokémon** on an eligible empty Party slot.

Items:
- pocket-oriented list/table;
- `Item | Quantity`;
- add, quantity edit and remove controls;
- Give All Supported Items only when E2 proves it safe.

Trainer:
- Money with the already proven range.

Shared flow:
`Open save -> Edit -> Preview -> Verify -> Export separate save`.

Normal use must not require hashes, offsets, JSON, section IDs or checksum knowledge. Advanced diagnostics may expose evidence/debug details without dominating normal use.

Final acceptance requires a real owner workflow containing representative Item editing, existing-Pokémon editing, Pokémon creation, Money regression, normal game use/save, and a later re-open/edit cycle.

## Non-goals for vNext terminal

The following are not prerequisites:

- PKHeX feature parity or legality-checker parity;
- Box editing/creation;
- Pokédex automation;
- story/quest/event mutation;
- RTC editing;
- arbitrary shiny/PID/OT manipulation;
- support for every Pokémon field;
- unsafe Key Item/event-item grants;
- generic CFRU save-editor scope;
- another PokemonStart version;
- Stable promotion;
- public release.

## Working principles for expansion

1. Prefer **generalization proofs** over serial canary accumulation.
2. Use native game transitions and exact-build source/ROM evidence together when available.
3. A field/pocket gets write authority only after its own coupling/invariants are supported.
4. Do not make one successful game load stand in for a reusable semantic model.
5. Preserve originals and create separate verified outputs.
6. Private ROM/save/package artifacts remain outside Git.
7. Unsupported or ambiguous states fail closed.
8. GUI controls expose only capabilities the core currently qualifies.
9. Money is regression-protected, not a research priority.
10. Re-evaluate the milestone sequence when genuinely new evidence changes the cheapest path; do not redesign merely because a bounded task is in progress.

## Immediate next work — post-E3 boundary

E3 is complete / adopted. Before any E4 implementation, fresh-read current canonical `main` and re-evaluate the milestone boundary: confirm current position, completed proofs, unresolved creation uncertainties, authorization boundary, protected-data boundary, and whether E4 remains the cheapest uncertainty-reducing next step.

This E3 adoption action does **not** authorize E4 implementation. Any bounded E4 work must proceed only under the separately applicable project authorization boundary, with materially expanded writer adoption still independently reviewed and Human-gated.


## E1/E2 adoption record — 2026-10-07

PR #21 merged the independently reviewed exact E1/E2 Inventory candidate into canonical `main` as merge commit `3eb756cb1b74fc0d58637b82e93542836fa0b290`. Adopted scope remains the reviewed restricted exact-v0.22 recovery-medicine editor only. Give All, broader regular-item authority, other pockets as writers, cross-version support, Stable promotion, and public release remain outside this adoption.


## E3 adoption record — 2026-10-07

PR #23 merged exact independently reviewed candidate `084f7e8089da2450521fb3069f6b0b62e85cc99b` into canonical `main` as merge commit `165dda2edbb94dca559cd426ba37189e7220f18e` after explicit Human adoption authorization. Human-played writer/GUI commit was `34517a6e8664a510a8a909725ad5cf59cdaeecfb`; the follow-up candidate changed returned-save verification for the opaque 16-byte emulator trailer without changing writer/model/core/GUI semantics.

The grouped Human acceptance covered three materially different ordinary Party specimens plus Money/Inventory regression in one transaction. Returned-save verification recorded normal SAVE counter `10→11`, persistence of requested edits and regression state, Rattata recovery from `3/13` to `13/13`, explainable battle/heal drift, and continued ordinary eligibility. The fresh independent-review disposition was `APPROVED_FOR_HUMAN_ADOPTION_DECISION`, recorded as Human-attested fresh-review evidence. This adoption does not authorize E4, release, Stable promotion, cross-version expansion, Box/Pokédex/story/event scope, or protected-data publication.
