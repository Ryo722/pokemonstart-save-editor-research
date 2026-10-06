# Fast Lab two-lane canonical adoption — 2026-10-06

Status: **CANONICAL PROJECT STRATEGY** once this record is on `main`.

GitHub `main` remains the durable canonical authority. This record adopts the Human-authorized two-lane project architecture while preserving the evidentiary and safety boundaries of the existing Stable lane.

## Human authorization

Controlling authorization:

> `AUTHORIZE CANONICAL FAST-LAB TWO-LANE ADOPTION`
>
> Adopt the Human-authorized Stable Lane + Fast Lab Lane strategy into the durable canonical project records.
>
> Preserve all existing Stable-lane evidence and milestones, but update the North Star, milestone architecture, success criteria, current position, and authorization wording so that Stable capabilities continue to require stronger lifecycle/provenance/recovery/delivery evidence before adoption; Fast Lab capabilities may be developed and used experimentally on immutable-source / separate-output private saves under exact capability profiles; Fast Lab success does not require normal in-game SAVE proof for every field when verifier + bounded live confirmation is sufficient; experimental Fast Lab capability does not imply Stable support; Inventory and Party work may proceed by practical value and evidence rather than a mandatory M5B-before-M5C sequence; exact PokemonStart build support is tracked per ROM SHA/profile rather than generalized across versions; and public/generic support claims remain prohibited without later review.

The authorization also directs that current v0.22 Fast Lab evidence be recorded canonically without promoting it to Stable support, and that protected-artifact, immutable-original, separate-output, and public-release boundaries remain unchanged.

## Revised North Star

Build a practical local save editor for the owner's PokemonStart saves that advances useful editing capability quickly while preserving a separate Stable lane for stronger adoption.

The project now intentionally has two lanes:

- **Stable Lane:** capabilities are adopted only after the stronger evidence, lifecycle/provenance, recovery, delivery, and fail-closed review appropriate to durable supported behavior.
- **Fast Lab Lane:** exact-build experimental capabilities may be developed rapidly against private, recoverable, disposable save copies when the original ROM/save remains immutable, output is separate, diffs are explainable, the repository verifier accepts the output, and cheap exact-build live confirmation is obtained where practical.

Fast Lab is not a weaker form of Stable. It is a separate evidence class and delivery posture. A Fast Lab result never becomes Stable merely because it worked once or because it was canonically recorded.

## Shared non-negotiable safeguards

Both lanes retain these boundaries:

- original/private source ROMs and source saves remain immutable;
- writers create a new output and do not overwrite the source;
- malformed, ambiguous, or unsupported inputs fail closed;
- protected/private artifacts such as ROMs, saves, `.pks`, BPS/IPS, extracted proprietary executables/payloads, and copyrighted assets are not committed or publicly distributed;
- no public generic-save or generic-version support claim follows from private Fast Lab evidence;
- no arbitrary version generalization: compatibility is tracked per exact ROM/build capability profile;
- no automatic replacement of emulator live-save state;
- no security-control weakening as a prerequisite;
- capability labels must distinguish Stable evidence from Fast Lab experimental evidence.

## Lane-specific success criteria

### Stable Lane

Stable adoption continues to require the evidence appropriate to the capability, including as applicable:

- supported-save/build gates;
- lifecycle or round-trip evidence;
- provenance/continuity handling;
- independent verification;
- recovery path;
- delivery and platform boundary review;
- explicit Human adoption decision.

The existing M1-M5A Stable records are preserved. Nothing in this adoption marks M5A COMPLETE, implements P-direct/P-reanchor, broadens M4 provenance, or promotes Fast Lab v0.22 capabilities into Stable support.

### Fast Lab Lane

A bounded Fast Lab capability may be treated as experimentally usable when, for the exact capability profile:

1. the private ROM/build identity is explicit;
2. the input save passes the existing structural verifier or an equally bounded compatibility gate;
3. the original input remains immutable;
4. the edit is written to a separate output;
5. the editor diff is explainable and bounded;
6. required checksums/invariants are updated and the output re-verifies;
7. exact-build live confirmation is obtained where cheap and materially informative;
8. limitations and untested couplings are recorded honestly.

A normal in-game SAVE round trip is **not required for every Fast Lab field** when the above evidence is sufficient for the bounded experimental claim. It may still be required later for Stable adoption.

## Build/profile model

Fast Lab support is tracked by exact capability profile rather than by version-name inference.

Current exact v0.22 private build evidence:

- upstream package source: `onikoro334274-cell/PokemonStart`
- frozen upstream commit: `ddd054d46fc1bd0555badf738572620b1ee4670d`
- package SHA-256: `d22bc25d7427899e8d0b2e29e7fd6b604602781167b78cfa8a90c8a2da9e4060`
- recovered BPS SHA-256: `a2bb3a1bddeeb6344cd45e139edb9ff35535deb41f8c38c0dc04eb4b1a7eab27`
- BPS source CRC32: `3B2056E9`
- BPS target CRC32: `B5D4DF5C`
- owned source ROM SHA-256: `1e4af44b0c75cc8649bfb8649dc4ae5850bf5358bd6b9cd0bf779c99f9db1486`
- verified private v0.22 ROM SHA-256: `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

These hashes identify private local research inputs. They do not confer redistribution rights and no protected bytes are part of this repository.

## Canonically recorded v0.22 Fast Lab evidence

Evidence class for all capabilities in this section: **Fast Lab experimental**, unless explicitly noted otherwise.

### Money

A disposable v0.15-lineage save was loaded under the exact v0.22 build. Offline Money `1,234,567` matched live Money. A separate-output edit changed Money to `7,654,321`, recomputed the required section checksum, passed the repository verifier, and was observed live as `7,654,321` under v0.22.

This does not prove broad v0.22 save migration, arbitrary saves, nonzero-key support, normal-save lifecycle, or Stable Money support on v0.22.

### Party record compatibility and practical editing

The retained party[0] 100-byte record matched byte-for-byte between offline decoding and v0.22 live RAM.

Successful bounded writes include:

- friendship `50 -> 51`, with the live 100-byte record matching the intended offline output;
- Attack IV `29 -> 0` with cached Attack recalculated `9 -> 8`, again matching live;
- move slot 0 Tackle `33 -> 1` (Pound) with PP remaining coherent at `35`;
- level/EXP edit from stored level `5`, EXP `134` to level `6`, EXP `179`, with cached HP/stats recalculated and live record matching offline;
- species transformation Bulbasaur `1 -> 2` (Ivysaur), with EXP moved to a coherent level-5 threshold, cached stats recalculated, and live record matching offline;
- a composed edit combining species, level/EXP, move, Attack IV, HP EV, friendship, and cached-stat recomputation, with the complete live party[0] record matching the offline output.

A reusable local Fast Lab party editor was created on the local research branch with inspect/edit behavior and fail-closed bounded support. The latest reported local checkpoint before this canonical adoption is commit `18d710119a814b8908fdb758652a32c78e3a94ec` on local branch `codex/fast-lab-v022`; this implementation commit itself is not thereby merged into canonical `main` by this strategy record.

Current bounded party support remains intentionally narrow. Ability-selector storage is decoded, but resolved ability editing is not proven. Species/level/move ranges outside the locally evidenced bounded editor remain unsupported unless separately demonstrated/profiled.

### Inventory

A user-provided v0.22 save retained two valid previous/current slots that supplied a same-file normal-save differential:

- previous slot: counter 1, Potion item ID `13`, quantity `1`;
- current slot: counter 2, Potion item ID `13`, quantity `2`.

Logical-section comparison isolated the Inventory difference to logical section 13, relative offset `0xADC`, where bytes changed from `0d000100` to `0d000200`. With encryption key `0`, the observed representation is little-endian `u16 item ID + u16 quantity`. The location lies beyond section 13's checksum-covered `0x450` prefix; the observed section checksum remained unchanged.

A separate-output experimental edit changed the same existing Potion slot from quantity `2 -> 3`. The reported editor diff was the single quantity byte `02 -> 03` at absolute offset `0x1ADE`; item ID, slot, and checksums remained unchanged. The repository verifier accepted the output and v0.22 live RAM showed Potion item ID `13`, quantity `3` in the same slot.

This proves only the bounded exact-profile claim: existing Potion slot 0, encryption key `0`, observed quantity range `1..3`, existing-entry quantity editing. It does **not** prove item insertion, deletion, reordering, other item IDs, other pockets, full pocket capacity, nonzero-key Inventory, or broad save compatibility.

## Important caveats retained

- The baseline party record contained stored level `5` with EXP `134`, while source-derived Medium Slow threshold logic used by the bounded level experiment placed level 5 at `135`. Fast Lab therefore preserves pre-existing EXP/level values unless the user explicitly edits level/EXP; unrelated edits must not silently normalize this inconsistency.
- Exact v0.22 startup/read-path evidence and live-memory confirmation are not a claim of broad gameplay/lifecycle compatibility.
- Ability resolution, battle behavior after species/move edits, evolution effects, Pokédex effects, move legality, and normal game re-save behavior remain unproven unless separately recorded.

## Revised milestone architecture

The old mandatory sequence `M5B Inventory -> M5C Practical Pokemon` is no longer controlling for Fast Lab work.

### Stable Lane milestones

Existing Stable history remains intact:

- M1 COMPLETE
- M2 COMPLETE
- M3A COMPLETE
- M3B COMPLETE
- M3C-F1 COMPLETE
- M3C COMPLETE
- M4 COMPLETE
- M5A Stable capability: implementation/lifecycle closure evidence complete, adoption still incomplete

Future Stable capability adoption continues capability-by-capability and does not inherit Fast Lab status automatically.

### Fast Lab milestones

- **FL0 — exact-build private ROM preparation and research harness: COMPLETE.** v0.22 package recovery, exact private ROM identity, mGBA harness/bootstrap, read-path compatibility and exact-build capability profile established.
- **FL1 — practical core editing slice: COMPLETE EXPERIMENTALLY.** Money, practical Party/composed Party, and one bounded existing-item Inventory quantity edit all have exact-v0.22 disposable-output + verifier + live evidence.
- **FL2 — unified practical local CLI: NEXT PROPOSED MILESTONE.** Consolidate existing Fast Lab inspect/edit operations behind one local command-line workflow with semantic preview, separate output, verifier, and capability-profile gates. This record identifies FL2 as the cheapest next practical milestone; it does not itself authorize additional unsupported field expansion.
- **FL3 — profile-driven capability broadening: LATER / EVIDENCE-DRIVEN.** Broaden species, levels, moves, abilities, items/pockets, keys, or later PokemonStart builds only when exact evidence justifies each expansion.
- **FL4 — practical GUI/delivery layer: LATER.** Consider only after the local editing contract, errors, preview, and recovery workflow are coherent enough that the GUI is a delivery layer rather than new proof authority.

## Current position

The project is no longer blocked on proving that practical save editing is possible. Exact v0.22 Fast Lab evidence now covers all three high-value practical areas: Money, Party, and a bounded Inventory quantity case.

The dominant uncertainty has shifted from field discovery to **usable consolidation and capability-boundary management**:

- unify already working operations without accidentally broadening claims;
- preserve per-build/profile fail-closed behavior;
- keep Stable and Fast Lab evidence visibly separate;
- broaden exact fields only when practical value justifies the cost;
- decide later which Fast Lab capabilities deserve Stable adoption.

## Current authorization boundary after adoption

This canonical adoption authorizes the **two-lane strategy and recording of the existing v0.22 Fast Lab evidence**. It does not, by itself:

- promote any v0.22 Fast Lab capability to Stable;
- mark M5A Stable COMPLETE;
- implement P-direct or P-reanchor;
- merge the local Fast Lab implementation branch;
- authorize public release;
- authorize generic arbitrary-save support;
- authorize broad PokemonStart version support;
- authorize nonzero-key support;
- authorize GUI exposure of experimental capabilities;
- authorize protected-data publication.

The next practical implementation step should be separately executed under the existing bounded Fast Lab safety model or a fresh Human authorization where scope materially expands.

## Cheapest next practical milestone

**FL2 — unified practical local CLI** is the current recommended next milestone.

The target is a small local interface that composes already evidenced capabilities rather than discovering another field first. A minimal useful surface is:

- inspect save/profile;
- preview semantic values;
- edit supported Money;
- edit supported Party fields;
- edit the bounded supported existing Inventory quantity case;
- show semantic and byte-diff preview;
- write only a new file;
- run the verifier on output;
- report unsupported fields/builds clearly.

GUI work should follow only after this local contract is coherent enough to be a delivery layer.
