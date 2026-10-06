# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — Stable Lane + Fast Lab Lane adopted

Human authorization:

> `AUTHORIZE CANONICAL FAST-LAB TWO-LANE ADOPTION`
>
> Adopt the Human-authorized Stable Lane + Fast Lab Lane strategy into the durable canonical project records.
>
> Preserve all existing Stable-lane evidence and milestones, but update the North Star, milestone architecture, success criteria, current position, and authorization wording so that Stable capabilities continue to require stronger lifecycle/provenance/recovery/delivery evidence before adoption; Fast Lab capabilities may be developed and used experimentally on immutable-source / separate-output private saves under exact capability profiles; Fast Lab success does not require normal in-game SAVE proof for every field when verifier + bounded live confirmation is sufficient; experimental Fast Lab capability does not imply Stable support; Inventory and Party work may proceed by practical value and evidence rather than a mandatory M5B-before-M5C sequence; exact PokemonStart build support is tracked per ROM SHA/profile rather than generalized across versions; public/generic support claims remain prohibited without later review.

The exact adoption rationale, v0.22 Fast Lab evidence, capability limits, and next-milestone definition are recorded in `docs/fast-lab-two-lane-adoption.md`. That record controls where older roadmap wording conflicts with this adoption.

## North Star

Build a practical local editor for the owner's PokemonStart saves that maximizes useful editing progress while preserving a separate Stable lane for durable supported behavior.

The project intentionally separates two objectives:

- **Stable Lane:** mature capabilities under stronger lifecycle/provenance/recovery/delivery evidence and explicit adoption.
- **Fast Lab Lane:** bounded exact-build experimental capabilities for the owner's private saves, optimized for rapid practical progress under immutable-input / separate-output / verifier / capability-profile safeguards.

Fast Lab is an evidence class, not a shortcut to Stable. Canonically recording a Fast Lab capability does not make it Stable.

General event/story/quest editing remains out of scope. PKHeX parity, generic CFRU editing, arbitrary-save support, broad PokemonStart-version support, and feature-count parity are not goals by themselves.

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

## Lane-specific success criteria

### Stable Lane

Stable adoption continues to require capability-appropriate evidence such as:

- supported-save/build gates;
- lifecycle and/or game round trips where relevant;
- provenance/continuity handling;
- independent verification;
- recovery path;
- platform/delivery review;
- explicit Human adoption.

Nothing in the Fast Lab adoption weakens existing Stable evidence or marks unadopted capabilities COMPLETE.

### Fast Lab Lane

A bounded Fast Lab capability may be treated as experimentally usable when all materially relevant conditions hold:

- exact ROM/build identity is recorded;
- the save passes the structural verifier or an equivalently bounded gate;
- the source remains immutable;
- output is written separately;
- the byte/semantic diff is explainable;
- required checksums/invariants are correct;
- output re-verifies;
- exact-build live confirmation is obtained where cheap and materially informative;
- unsupported coupling/coverage is explicitly recorded.

A normal in-game SAVE round trip is **not mandatory for every Fast Lab field**. It may still be required before Stable adoption.

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

The M5A Stable implementation remains bounded to its recorded v0.15 lineage/build/key/platform/journal envelope. Practical provenance continuity remains design-only. M5A is not GUI-exposed and is not marked COMPLETE by this adoption.

The previous roadmap labels `M5B Inventory` and `M5C Practical Pokemon` are no longer a mandatory sequential execution order for Fast Lab. Stable adoption of Inventory or practical Pokemon capabilities remains future, capability-by-capability work.

## Fast Lab milestone architecture

### FL0 — exact-build private ROM preparation and harness — COMPLETE

Exact PokemonStart v0.22 package recovery, private ROM preparation, mGBA harness/bootstrap, read-path compatibility, and exact-build capability profile were established without committing protected artifacts.

Current exact private v0.22 build SHA-256:

`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

### FL1 — practical core editing slice — COMPLETE EXPERIMENTALLY

Exact-v0.22 Fast Lab experimental evidence now covers all three high-value practical areas:

- Money;
- Party/composed Party editing;
- one bounded existing-item Inventory quantity edit.

Detailed exact evidence and limitations are in `docs/fast-lab-two-lane-adoption.md`.

### FL2 — unified practical local CLI — NEXT PROPOSED MILESTONE

The cheapest next milestone is to consolidate already-working Fast Lab operations into a small local command-line workflow rather than discover another isolated field first.

Minimum target surface:

- inspect save/profile;
- preview semantic values;
- edit supported Money;
- edit supported Party fields;
- edit the currently supported bounded Inventory quantity case;
- show semantic and byte-diff preview;
- write only a new output;
- verify output;
- clearly reject unsupported builds/fields.

FL2 should reuse existing bounded implementations and must not silently generalize their capability ranges.

### FL3 — profile-driven broadening — LATER / EVIDENCE-DRIVEN

Broaden species, levels, moves, abilities, items/pockets, keys, save variants, or later PokemonStart builds only when exact evidence justifies each expansion.

### FL4 — practical GUI/delivery — LATER

GUI becomes appropriate only after the practical edit contract, failure behavior, preview, and recovery workflow are coherent enough that GUI is only a delivery layer.

## Current v0.22 Fast Lab evidence summary

Evidence class for this section: **Fast Lab experimental**, not Stable.

### Money

A disposable output changed Money from `1,234,567` to `7,654,321`, updated the required checksum, passed the repository verifier, and was observed live under exact v0.22 as `7,654,321`.

### Party

The retained party[0] 100-byte record matched offline decoding to live v0.22 memory. Successful bounded writes include:

- friendship `50 -> 51`;
- Attack IV `29 -> 0` with cached Attack `9 -> 8`;
- move slot 0 Tackle `33 -> 1` (Pound) with coherent PP;
- stored level `5`, EXP `134` -> level `6`, EXP `179` with cached-stat recomputation;
- Bulbasaur `1 -> 2` (Ivysaur), with coherent EXP/stat recomputation;
- a composed multi-field edit combining species, level/EXP, move, IV, EV, friendship, and cached stats, with the full live party record matching offline output.

Ability-selector storage is decoded, but practical resolved-ability writing is not proven.

### Inventory

A same-file previous/current save-slot differential isolated Potion item ID `13`, quantity `1 -> 2` at logical section 13 relative offset `0xADC` under encryption key `0`.

A separate-output edit changed the same existing Potion slot `2 -> 3`; only the observed quantity byte changed, the repository verifier accepted the output, and exact v0.22 live RAM showed Potion ID `13`, quantity `3` in the same slot.

This does not prove arbitrary item IDs, insertion, deletion, reordering, other pockets, nonzero-key handling, or complete pocket capacity.

## Important Fast Lab caveats

- The baseline retained party record contains stored level `5` with EXP `134`, while the source-derived Medium Slow threshold logic used for explicit level editing places level 5 at `135`. Unrelated edits must preserve the pre-existing values rather than silently normalize them.
- Exact v0.22 startup/read-path/live-memory evidence is not broad save-migration or lifecycle proof.
- Battle behavior after species/move edits, ability resolution, evolution, Pokédex effects, move legality, and normal in-game resave behavior remain unproven unless separately recorded.
- The local Fast Lab implementation branch and its commits are not automatically merged into `main` merely because the strategy/evidence record is canonicalized.

## Existing M5A Stable provenance decision remains unchanged

Pinned CFRU-JP save behavior and reproduced round-trip evidence support a possible future two-tier provenance model:

- **P-direct:** one-save structural descent using the preserved prior slot as ancestry witness;
- **P-reanchor:** explicit/manual Human-attested re-anchor for longer gaps.

Neither is implemented or adopted by this Fast Lab strategy decision. Existing M4 provenance remains unchanged.

## Authorization boundary after this adoption

This adoption authorizes the two-lane architecture and durable recording of the existing v0.22 Fast Lab evidence.

It does **not** by itself authorize or perform:

- Stable promotion of any v0.22 Fast Lab capability;
- marking M5A Stable COMPLETE;
- P-direct or P-reanchor implementation;
- merging the local Fast Lab implementation branch;
- public release;
- arbitrary-save or broad-version support;
- nonzero-key generalization;
- GUI exposure of experimental capabilities;
- protected-data publication.

The next practical implementation step should remain bounded to the existing Fast Lab safeguards unless a later task materially expands scope.

## Authority chain

Key durable records now include:

- `docs/decision-record.md` — controlling milestone/authority state;
- `docs/fast-lab-two-lane-adoption.md` — controlling two-lane adoption details and exact v0.22 Fast Lab evidence;
- `docs/evidence.md`;
- `docs/m4-completion.md`;
- `docs/m5a-second-roundtrip-and-money-family.md`;
- `docs/m5a-family-closure-and-provenance-continuity-design.md`.

Where older roadmap prose says M5B/M5C are categorically not authorized or requires a mandatory Inventory-before-Party sequence, this decision supersedes that wording for the Fast Lab lane only. Stable adoption still requires its own evidence and decision.

## Current next step

**FL2 — unified practical local CLI** is the cheapest next practical milestone.
