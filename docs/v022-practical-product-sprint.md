# v0.22 practical product sprint — canonical scope

Date: 2026-10-07

Canonical base when adopted: `d60bc654acc7d0df452c294d8beb0807c25d3539`

## Human authorization

> `AUTHORIZE V0.22 PRACTICAL PRODUCT SPRINT REALIGNMENT AND BOUNDED R1-R4 IMPLEMENTATION`

This authorization converts the forward practical path into one bounded product sprint. It authorizes implementation work inside R1–R4 on a candidate branch without requiring a new Human approval at every internal subgoal, provided the work remains within this document's capability, safety, and publication boundaries.

It does **not** authorize candidate merge into `main`, public release, support for another PokemonStart version, protected-data publication, or speculative writes outside independently supported exact-v0.22 semantics.

## Product objective

Deliver a local editor for the exact PokemonStart v0.22 profile that the owner can use repeatedly on naturally progressed saves:

`open save -> inspect -> edit -> preview -> verify -> export separate save -> play/save -> progress -> open new save again`

The practical terminal product is intentionally narrower than PKHeX parity. It must make the supported Party / Items / Money workflow obvious to a user familiar with PKHeX, while retaining evidence-first fail-closed behavior.

## Product acceptance shape

The terminal exact-v0.22 product should provide:

- a localhost-only GUI with no JSON editing required for normal use;
- visible Party, Items, and Trainer/Money editing surfaces;
- semantic preview of requested changes before output generation;
- verified separate-output save generation only;
- reusable eligibility based on exact-build and capability-specific semantic/invariant checks rather than preregistered input-save hashes;
- rejection of malformed, ambiguous, incompatible, or unsupported save states;
- at least one independently closed two-cycle naturally-progressed-save workflow through the actual GUI.

The interface should be familiar to a PKHeX-experienced user, but visual or feature parity with PKHeX is not required.

## R1 — reusable exact-v0.22 save eligibility

Goal: remove exact-input-save SHA membership as the primary write authorization mechanism for the first useful capability family, while preserving strict capability-specific eligibility.

The cheapest current candidate is Money, but implementation must fresh-read and reconcile current canonical evidence before porting or reusing anything from the frozen `codex/money-reusable-qualification-20261007` branch.

R1 success requires:

1. exact v0.22 ROM/profile identity remains mandatory;
2. the repository verifier accepts the save structure and selects a unique active slot;
3. the writer checks the actual semantic representation and all capability-specific invariants needed for a Money write;
4. input save SHA is recorded as evidence but is not itself the eligibility allowlist;
5. output changes remain bounded to the Money representation plus required checksum bytes;
6. source bytes remain immutable and output is a separate file/byte object;
7. a naturally progressed save with a previously unseen SHA can be accepted, edited, normally saved in game, progressed again, and accepted for a later editor cycle when its predicates still pass;
8. unsupported key/layout/state combinations fail closed rather than being inferred.

The existing paused Money branch may be inspected as historical implementation/evidence. It must not be merged wholesale or treated as canonical truth without reconciliation against current `main`.

## R2 — practical reusable core

Extend reusable eligibility family-by-family only where it materially improves owner use.

### Money — required

Provide normal GUI editing of the decoded current Money value to a supported target value within the exact-v0.22 representation proven by current evidence.

Do not retain fixed canary-only transitions such as a single source/target pair when the representation and invariants support a broader bounded value range.

If an observed save uses an unproven key/layout/state, fail closed unless exact-v0.22 evidence gathered during this sprint independently establishes the required semantics.

### Party — required practical subset

Provide editing of existing party members using ordinary GUI controls rather than raw JSON.

The terminal minimum is a useful subset of already evidenced or independently requalified exact-v0.22 fields, prioritizing:

- species;
- level / EXP coupling;
- moves and PP coupling;
- friendship;
- IVs and EVs;
- derived/cached party stats that must be recomputed coherently.

Held item, nature/nature-mint, markings, ball, and ability may be added when exact-v0.22 semantics are sufficiently supported. A field that is readable but not safely writable should remain visible/read-only or disabled with an explicit reason.

Arbitrary Pokémon synthesis, arbitrary templates, Box editing, legality analysis, Pokédex mutation, and PKHeX parity are not terminal requirements.

### Inventory — required practical subset

Generalize beyond the current single Potion canary only where exact-v0.22 pocket layout, slot semantics, quantity encoding, capacity, and checksum/tail behavior can be independently supported.

Terminal use should support a practical regular-item workflow, including quantity editing and item insertion/removal where those operations are proven safe for the supported pocket representation.

Key items, event/story items, unknown pockets, unknown slot semantics, or ambiguous capacity behavior must fail closed.

### Give All Items — stretch

Implement only if the sprint can derive a safe exact-v0.22 list of supported ordinary items and pocket capacities without guessing.

The intended behavior is "give all supported ordinary items" rather than indiscriminately filling every item ID. Key/event/story items are excluded unless separately proven safe.

Failure to establish this safely does not block terminal completion; record it as deferred with the concrete blocker.

## R3 — PKHeX-familiar local GUI

Reuse the existing localhost/in-memory/verified-download delivery model unless strong evidence shows that doing so blocks the product objective.

Normal use must not require operation names, JSON payloads, SHA hashes, sector offsets, or checksum knowledge.

The primary UI should expose approximately:

- **Party** — six party slots/cards, select a member, edit supported fields with comboboxes/numeric inputs, show unsupported fields read-only/disabled;
- **Items** — pocket-oriented item table/editor with item and quantity controls, add/remove where supported, optional Give All Items action when proven;
- **Trainer** — Money editing;
- **Preview / Export** — human-readable semantic diff followed by generation of a verified separate `.sav` output.

Examples of semantic preview:

- `Money: 1,234,567 -> 9,999,999`
- `Party #2 Level: 18 -> 30`
- `Party #1 Move 1: Tackle -> Pound`
- `Potion: x3 -> x99`

Byte-level details, hashes, sections, and verifier diagnostics should remain available in an Advanced/Details surface rather than dominate the normal workflow.

The server remains bound to `127.0.0.1` only. No LAN/public exposure is authorized.

## R4 — product acceptance and repeated-use closure

R4 closes the real product workflow through the GUI, not merely through internal library calls.

Required acceptance sequence:

1. start from a naturally progressed exact-v0.22 owner save whose SHA is not preregistered as a writer allowlist;
2. open it in the GUI;
3. perform a composed practical edit using the reusable supported core, preferably spanning Money + Party + Inventory where all three predicates pass;
4. preview and export a verified separate output;
5. load that output in exact v0.22 and perform a normal in-game save;
6. make ordinary gameplay progress and save again;
7. open the resulting newly changed save in the GUI;
8. perform another supported edit and export another verified output;
9. load and normally save again;
10. independently confirm that source saves remained immutable and outputs satisfy repository verification plus capability-specific postconditions.

If a capability family cannot participate safely in the same composed transaction, R4 may close it independently, but terminal completion still requires a practically useful Party / Items / Money product set rather than a Money-only demonstration.

Human gameplay interaction may remain a bounded acceptance gate. The coding agent must complete all non-human implementation, tests, static audits, and candidate documentation before stopping for an emulator/game round trip.

## Autonomous implementation authority inside the sprint

Within the scope above, the implementation agent is authorized to:

- create a dedicated local candidate branch from fresh `main`;
- inspect the frozen reusable-Money branch as non-canonical evidence/reference;
- refactor existing Fast Lab modules when needed to expose reusable capability predicates cleanly;
- add tests, fixtures made from synthetic/generated bytes, GUI code, documentation, and sanitized evidence records;
- use private local ROM/save artifacts as read/verification inputs without adding them to Git;
- make coherent local commits at meaningful subgoals;
- iterate through failing tests and repair the candidate without waiting for a new Human approval for each in-scope correction.

The agent should prefer the smallest implementation that reaches the product objective. Existing working paths should be reused rather than replaced merely for cleanliness.

## Required commit discipline

Use coherent subgoal commits. Exact commit count is not fixed, but a good default sequence is:

1. reusable eligibility foundation / R1 Money predicate;
2. reusable Money editing;
3. reusable Party core;
4. reusable Inventory core;
5. PKHeX-familiar GUI;
6. composed reusable tests / product acceptance harness;
7. optional supported-items Give All implementation if safely proven;
8. candidate documentation and final verification record.

Every functional commit should leave the branch in a testable state. Run focused tests during development and the full repository suite before the final candidate stop.

## Non-negotiable safety and data boundaries

- Do not overwrite source save files.
- Do not automatically replace emulator live-save state.
- Do not commit/upload ROMs, `.sav`, `.pks`, BPS/IPS patches, extracted executables, copyrighted game assets, or proprietary package payloads.
- Do not disable Defender, Gatekeeper, TCC, or other host security controls.
- Do not infer support from one capability family to another.
- Do not infer support from v0.22 to another PokemonStart version.
- Do not silently accept malformed, ambiguous, or unproven states.
- Preserve verifier acceptance, exact profile identity, semantic diff visibility, and recovery through immutable originals.

## Explicitly not authorized by this sprint

- merge of the implementation candidate into canonical `main`;
- public release or release artifact publication;
- public/LAN GUI exposure;
- Stable-Lane promotion;
- support claims for v0.15 or another PokemonStart version based on this sprint;
- generic CFRU editor scope;
- Box editing;
- Pokédex, story, quest, event flag, trainer identity, RTC, or unrelated save-system mutation;
- arbitrary Pokémon synthesis/templates as a terminal requirement;
- unsafe "all items" behavior that includes unknown/key/event/story items by guess;
- publication of protected/private artifacts.

A fresh-context review and explicit Human merge/adoption decision remain required before the candidate may become canonical implementation.
