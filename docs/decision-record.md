# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — FL2-G0 merged; FL2 unified practical CLI active

The project retains the previously adopted Stable Lane + Fast Lab Lane architecture and refined terminal goal.

Controlling prior authorizations:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

> `AUTHORIZE FL2-G0 MERGE 44c90e8217061cc8ac294a392984dfe73e622d80`

The FL2-G0 reconciliation candidate was independently reviewed and then fast-forwarded into canonical `main` at exact commit `44c90e8217061cc8ac294a392984dfe73e622d80`.

The durable Fast Lab implementation/test/profile gap is therefore closed. FL2-G0 is complete and no longer the next-work blocker.

The active practical milestone is now **FL2 — unified practical local CLI**. FL2 must consolidate already-evidenced exact-v0.22 operations without silently broadening their capability ranges.

Detailed controlling records remain:

- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md`
- `docs/fast-lab-two-lane-adoption.md`
- `docs/fl2-g0-reconciliation.md`

Where older roadmap wording conflicts with this record, this later record controls.

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

The terminal goal does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, GUI specifically, or Stable promotion of every Fast Lab capability.

## Canonical two-lane architecture

### Stable Lane

Durable supported capabilities require capability-appropriate evidence such as supported-save/build gates, lifecycle/game-round-trip evidence where relevant, provenance/continuity handling, independent verification, recovery, delivery review, and explicit Human adoption.

### Fast Lab Lane

Bounded exact-build experimental capabilities may progress rapidly when the exact build is identified, private source artifacts stay immutable, outputs are separate, diffs are explainable, required checksums/invariants hold, generated outputs re-verify, and unsupported coupling/coverage is recorded.

Fast Lab evidence does not imply Stable support.

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

M5A remains bounded to its recorded v0.15 lineage/build/key/platform/journal envelope. P-direct/P-reanchor remain unimplemented and are not on the Fast Lab critical path.

## Fast Lab milestone state

### FL0 — exact-build private ROM preparation and harness — COMPLETE

Exact PokemonStart v0.22 package recovery, private ROM preparation, mGBA harness/bootstrap, read-path compatibility, and exact-build capability profile are durably recorded.

Exact private v0.22 build SHA-256:

`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

### FL1 — practical core editing slice — COMPLETE EXPERIMENTALLY

Exact-v0.22 Fast Lab evidence covers:

- Money editing;
- practical/composed Party editing;
- one bounded existing-item Inventory quantity edit.

Detailed evidence and limitations remain in `docs/fast-lab-two-lane-adoption.md` and `docs/fast-lab-v022-capability.json`.

### FL2-G0 — durable Fast Lab baseline reconciliation — COMPLETE / MERGED

Human-authorized candidate `44c90e8217061cc8ac294a392984dfe73e622d80` is canonical `main` history. The reconciled implementation, tests, capability profile, and evidence pointers are now durable.

This merge did **not** promote Fast Lab capabilities to Stable and did not broaden build/version/key/field support.

### FL2 — unified practical local CLI — ACTIVE MILESTONE

FL2 must consolidate the already-evidenced operations into one local workflow with at least:

- exact profile/save inspection;
- semantic preview;
- supported Money editing;
- supported Party editing;
- currently bounded Inventory quantity editing;
- semantic and byte-diff preview;
- separate-output write;
- output verification;
- explicit unsupported-build/save/field rejection.

The implementation should delegate field derivation to the reconciled bounded Fast Lab modules rather than reimplement or generalize them.

The current implementation candidate is developed on `codex/fl2-unified-cli` and is documented in `docs/fl2-unified-cli-candidate.md`. Candidate work is not canonical adoption until separately reviewed and merged.

## Current v0.22 Fast Lab evidence summary

Evidence class: **Fast Lab experimental**, not Stable.

### Money

A disposable output changed Money from `1,234,567` to `7,654,321`, updated the required checksum, passed the verifier, and was observed live under exact v0.22.

### Party

The retained party[0] 100-byte record matched offline decoding to live v0.22 memory. Successful bounded writes include friendship, Attack IV/stat recalculation, move replacement/PP handling, level/EXP editing, Bulbasaur -> Ivysaur transformation, and the recorded composed canary.

Ability-selector storage is decoded, but practical resolved-ability writing remains unproven.

### Inventory

A same-file previous/current slot differential isolated Potion item ID `13`, quantity `1 -> 2` at logical section 13 relative offset `0xADC` under encryption key `0`.

A separate-output edit changed that existing Potion slot `2 -> 3`; the verifier accepted it and exact v0.22 live RAM showed Potion ID `13`, quantity `3` in the same slot.

This does not prove arbitrary item IDs, insertion, deletion, reordering, other pockets, nonzero-key handling, or complete pocket capacity.

## Important caveats

- The baseline retained party record contains stored level `5` with EXP `134`, while the source-derived Medium Slow threshold used for explicit level editing places level 5 at `135`; unrelated edits must preserve this pre-existing mismatch.
- Exact v0.22 startup/read/live-memory evidence is not broad save-migration or lifecycle proof.
- Battle behavior after species/move edits, resolved ability behavior, evolution, Pokédex effects, move legality, and normal in-game resave behavior remain unproven unless separately recorded.
- Nonzero-key Fast Lab support and other PokemonStart builds remain unsupported.

## Current authorization boundary

The Human has explicitly authorized and completed the FL2-G0 merge. The subsequent instruction to continue permits bounded FL2 candidate implementation consistent with the already-adopted post-G0 plan.

Current work may:

- create an FL2 implementation branch from exact canonical `main`;
- consolidate existing bounded Money / Party / Inventory logic behind one local CLI;
- add synthetic/focused tests and candidate documentation;
- inspect and preview semantic/byte diffs;
- preserve separate-output and verifier requirements.

Current work does **not** authorize:

- merge/adoption of the FL2 candidate into canonical `main` without a separate review/authorization decision;
- Stable promotion;
- public release;
- broader build/version/key support;
- arbitrary-save write support;
- ability write support or broader Inventory support;
- protected-data publication;
- unrelated new-field research.

## Post-FL2 roadmap — usage driven

After FL2, choose the next milestone from actual owner use rather than a fixed roadmap:

- capability expansion when a concrete missing capability blocks useful work;
- delivery/GUI improvements when UX adds more value than another field;
- Stable promotion when durable support justifies its extra evidence and lifecycle cost.

## Authority chain

Current key durable records:

- `docs/decision-record.md` — controlling current milestone/authority state;
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md` — terminal-goal and FL2 design basis;
- `docs/fl2-g0-reconciliation.md` — merged durable-baseline reconciliation record;
- `docs/fast-lab-two-lane-adoption.md` — two-lane adoption detail and v0.22 Fast Lab evidence;
- `docs/fast-lab-v022-capability.json` — machine-readable exact-v0.22 capability profile;
- `docs/evidence.md`;
- `docs/m4-completion.md`;
- `docs/m5a-second-roundtrip-and-money-family.md`;
- `docs/m5a-family-closure-and-provenance-continuity-design.md`.

## Current next step

**Complete focused/full validation of the bounded FL2 unified CLI candidate, independently review its exact branch HEAD, and stop for separate Human merge authorization before changing canonical `main`.**
