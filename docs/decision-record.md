# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — FL2 complete; post-FL2 private acceptance and reusable-envelope planning active

The project retains the adopted Stable Lane + Fast Lab Lane architecture and refined terminal goal.

Controlling Human authorizations now include:

> `AUTHORIZE FL2 DURABLE-BASELINE GATE AND TERMINAL-GOAL REFINEMENT`

> `AUTHORIZE FL2-G0 MERGE 44c90e8217061cc8ac294a392984dfe73e622d80`

> `AUTHORIZE FL2 MERGE e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

FL2-G0 and FL2 are both complete and merged into canonical `main`. The current next-work boundary is defined by:

- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`

Where older roadmap/status wording conflicts with this record, this record controls.

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can:

- inspect supported saves;
- preview supported edits;
- preserve original inputs;
- write only separate outputs;
- explain semantic and byte-level changes;
- verify generated outputs;
- reject unsupported builds/fields/saves rather than guess.

Exact-build capability profiles define the supported envelope.

The terminal goal does not require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, GUI specifically, or Stable promotion of every Fast Lab capability.

## Post-FL2 terminal-state assessment

Status:

> **TERMINAL GOAL PARTIALLY SATISFIED — PRACTICAL REUSE NOT YET PROVEN**

FL2 now durably provides the coherent local inspect/preview/write/verify workflow required by the refined goal. However, current write eligibility remains tied to exact retained input-save SHA-256 canaries in the underlying bounded Fast Lab modules.

Therefore current capability is intentionally fail-closed and is best described as:

> **profile-bounded workflow with canary-snapshot-bounded write eligibility**

A naturally changed but otherwise compatible exact-v0.22 owner save is not yet proven writable merely because its structure/semantics appear compatible.

The next useful uncertainty is therefore reuse of already-evidenced capabilities, not accumulation of additional fields.

## Canonical two-lane architecture

### Stable Lane

Durable supported capabilities require capability-appropriate evidence such as supported-save/build gates, lifecycle/game-round-trip evidence where relevant, provenance/continuity handling, independent verification, recovery, delivery review, and explicit Human adoption.

### Fast Lab Lane

Bounded exact-build experimental capabilities may progress rapidly when the exact build is identified, private source artifacts remain immutable, outputs are separate, diffs are explainable, required checksums/invariants hold, generated outputs re-verify, and unsupported coupling/coverage is recorded.

Fast Lab evidence does not imply Stable support.

## Shared safety contract

Both lanes retain these non-negotiable rules:

1. original/private ROMs and source saves remain immutable;
2. writers create new outputs and do not overwrite sources;
3. malformed, ambiguous, and unsupported inputs fail closed;
4. protected/private artifacts do not enter Git or public distribution;
5. exact-build/version support is tracked by capability profile rather than inferred across versions;
6. editor diffs remain bounded and explainable;
7. verifier/invariant checks run on generated outputs;
8. emulator live-save state is never automatically replaced;
9. public/generic support claims require later review;
10. Fast Lab and Stable evidence labels remain distinct.

## Stable Lane milestone state

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

Exact-v0.22 Fast Lab evidence covers bounded Money editing, practical/composed Party editing, and one bounded existing-item Inventory quantity edit.

### FL2-G0 — durable Fast Lab baseline reconciliation — COMPLETE / MERGED

Human-authorized candidate `44c90e8217061cc8ac294a392984dfe73e622d80` is canonical history. The reconciled Fast Lab implementation/tests/capability profile are durable.

### FL2 — unified practical local CLI — COMPLETE / MERGED

Human-authorized candidate `e44e85358be9a1e72e0cd84c65d446eec5bd81c2` is canonical history.

The merged CLI provides:

- exact ROM/profile gating;
- exact-save capability inspection;
- semantic preview;
- semantic + byte-diff reporting;
- already-evidenced bounded Money / Party / Inventory operations;
- separate-output creation with exclusive create;
- persisted-output byte equality checks;
- repository-verifier revalidation;
- explicit unsupported rejection.

FL2 did not broaden any underlying Fast Lab capability range and did not promote any capability to Stable.

## Current v0.22 Fast Lab evidence summary

Evidence class: **Fast Lab experimental**, not Stable.

### Money

A disposable output changed Money from `1,234,567` to `7,654,321`, updated the required checksum, passed the verifier, and was observed live under exact v0.22.

### Party

The retained party[0] 100-byte record matched offline decoding to live v0.22 memory. Successful bounded writes include friendship, Attack IV/stat recalculation, move replacement/PP handling, level/EXP editing, Bulbasaur -> Ivysaur transformation, and the recorded composed canary.

Ability-selector storage is decoded, but practical resolved-ability writing remains unproven.

### Inventory

A same-file previous/current slot differential isolated Potion item ID `13`, quantity `1 -> 2` at logical section 13 relative offset `0xADC` under encryption key `0`. A separate-output edit changed that existing Potion slot `2 -> 3`; the verifier accepted it and exact v0.22 live RAM showed Potion ID `13`, quantity `3` in the same slot.

## Important caveats

- The baseline retained party record contains stored level `5` with EXP `134`, while the source-derived Medium Slow threshold used for explicit level editing places level 5 at `135`; unrelated edits must preserve this pre-existing mismatch.
- Exact v0.22 startup/read/live-memory evidence is not broad save-migration or lifecycle proof.
- Battle behavior after species/move edits, resolved ability behavior, evolution, Pokédex effects, move legality, and normal in-game resave behavior remain unproven unless separately recorded.
- Nonzero-key Fast Lab support and other PokemonStart builds remain unsupported.
- FL2 write support remains exact-retained-save gated; reusable owner-save eligibility has not yet been proven.

## Current authorization boundary

The Human has authorized **Phase A private acceptance** and **Phase B reusable-envelope design/preregistration** as specified in `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`.

Current work may:

- fresh-read current canonical `main`;
- execute merged FL2 locally against retained private exact-v0.22 ROM/save canaries;
- run inspect/preview/write/verify on private canary copies;
- compare unified outputs against existing bounded-module derivations and existing live-confirmed identities where applicable;
- verify source immutability, no-overwrite behavior, output verification, focused/full tests and static/security checks;
- record non-sensitive hashes/results/log summaries in a candidate/evidence record;
- design and preregister field-family-specific semantic predicates for a future reusable exact-v0.22 save envelope;
- compare candidate first reusable-envelope families by cost/value/coupling.

Current work does **not** authorize:

- implementing broader reusable writer eligibility or removing exact-save SHA gates;
- Stable promotion;
- public release;
- GUI exposure;
- broader build/version support;
- nonzero-key Fast Lab support;
- arbitrary Money/Party/Inventory capability;
- ability writes;
- protected-data publication;
- unrelated new-field research.

Any proposed reusable-envelope implementation must return as a bounded decision surface and receive separate Human authorization before implementation.

## Local Codex execution policy for current work

Private acceptance work should normally be delegated to local Codex because it can operate directly in the owner's private workspace without moving ROM/save bytes into ChatGPT or GitHub.

Local Codex must still treat GitHub `main` as canonical, keep private/protected artifacts outside Git, avoid source overwrite, avoid broadening capability, and return exact command/result evidence that can be independently reviewed.

## Post-FL2 roadmap — usage driven

After current acceptance/design work, choose the next milestone from actual owner use and new evidence:

- reusable-envelope capability implementation only when separately authorized;
- additional field/build capability only when a concrete missing capability blocks useful work;
- delivery/GUI improvements when UX adds more value than capability work;
- Stable promotion when durable support justifies lifecycle/provenance/recovery cost.

No fixed FL3 -> FL4 sequence is controlling.

## Authority chain

Current key durable records:

- `docs/decision-record.md` — controlling current milestone/authority state;
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md` — current authorized next-work contract;
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md` — terminal-goal and FL2 design basis;
- `docs/fl2-g0-reconciliation.md` — merged durable-baseline reconciliation record;
- `docs/fl2-unified-cli-candidate.md` — merged FL2 implementation and validation record;
- `docs/fast-lab-two-lane-adoption.md` — two-lane adoption detail and v0.22 Fast Lab evidence;
- `docs/fast-lab-v022-capability.json` — machine-readable exact-v0.22 capability profile;
- `docs/evidence.md`;
- `docs/m4-completion.md`;
- `docs/m5a-second-roundtrip-and-money-family.md`;
- `docs/m5a-family-closure-and-provenance-continuity-design.md`.

## Current next step

**Delegate Phase A post-FL2 private acceptance to local Codex, then perform Phase B reusable-envelope design/preregistration from the resulting evidence. Stop before broader writer implementation.**
