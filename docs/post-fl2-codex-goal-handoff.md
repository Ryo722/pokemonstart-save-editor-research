# Post-FL2 local Codex Goal handoff — 2026-10-06

Status: **CANONICAL EXECUTION HANDOFF / NO CAPABILITY EXPANSION**

GitHub `main` remains the durable canonical authority. This document does not change the milestone design or authorization boundary in `docs/decision-record.md` and `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`; it defines how the currently authorized work should be delegated as one larger local Codex work unit.

## Current position

At the time this handoff was prepared, canonical `main` was:

`dfef0558ab005e066a6cf9ef3b2d0f6f782bd17f`

If remote `main` has moved, Codex must fresh-read the new canonical state and reconcile before proceeding.

Milestone position:

- FL0 — COMPLETE
- FL1 — COMPLETE EXPERIMENTALLY
- FL2-G0 — COMPLETE / MERGED
- FL2 — COMPLETE / MERGED
- post-FL2 terminal assessment — **TERMINAL GOAL PARTIALLY SATISFIED — PRACTICAL REUSE NOT YET PROVEN**
- current authorized work — Phase A private acceptance + Phase B reusable-envelope design/preregistration

The current Human gate ends **before reusable-envelope writer implementation**.

## Human authorization

Controlling authorization:

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

This permits Phase A execution and Phase B design/preregistration only. It does not permit removing exact-save SHA gates or broadening writer eligibility.

## Recommended work-unit model

Treat the work from current state through the next Human decision surface as **one Codex Goal**.

The Goal should continue autonomously through:

1. fresh canonical-state reconstruction;
2. private exact-v0.22 artifact discovery in the owner's local workspace;
3. Phase A unified-CLI end-to-end acceptance;
4. comparison against underlying bounded derivations and existing FL1 evidence;
5. focused/full/static/security validation;
6. Phase B independent Money / Party / Inventory reusable-envelope analysis;
7. selection of exactly one cheapest meaningful first reusable-envelope family;
8. exact fail-closed predicate preregistration;
9. preparation of a final bounded decision packet.

Do not split these into repeated Human prompts merely because intermediate steps complete successfully. Continue until the Goal completion conditions are met or a concrete Human-only blocker is reached.

## Goal completion conditions

The Goal is complete only when all of the following are true:

1. the merged/current FL2 unified CLI itself has been exercised end-to-end on retained private exact-v0.22 canary inputs where available;
2. inspect / preview / write / verify behavior is evidenced;
3. source ROM/save immutability is evidenced;
4. preview no-publication and write separate-output/exclusive-create behavior are evidenced;
5. unified candidate/output bytes are compared with the corresponding underlying bounded-module derivation;
6. existing live-confirmed FL1 output identities are reused as comparison evidence when an exact matching request exists;
7. focused FL2, Fast Lab regressions, mGBA harness, full repository tests, compile, JSON, diff, protected-artifact and secret checks are completed as applicable;
8. Money / Party / Inventory are independently evaluated as reusable-envelope candidates;
9. exactly one first reusable-envelope family is selected from evidence rather than roadmap preference;
10. an exact proposed eligibility predicate and required private proof are preregistered;
11. a final decision surface is produced for Human authorization;
12. no reusable-envelope implementation or exact-save-gate broadening has occurred.

## Required canonical reads

Fresh-read at minimum:

- `README.md`
- `docs/decision-record.md`
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`
- `docs/post-fl2-codex-goal-handoff.md`
- `docs/fl2-unified-cli-candidate.md`
- `docs/fast-lab-v022-capability.json`
- `docs/evidence.md`
- `pokemonstart_fl2_core.py`
- `pokemonstart_fl2_cli.py`
- bounded Money / Party / Inventory Fast Lab modules
- relevant tests

## Private execution policy

Private inputs may be read and used locally but must stay outside Git.

Never commit/upload:

- ROMs;
- `.sav` files;
- `.pks` files;
- BPS/IPS patches;
- executable payloads;
- proprietary package payloads;
- copyrighted game assets.

Prefer hashes, structural summaries, command/result summaries, and exact non-sensitive diff metadata in the final evidence packet.

Do not execute unrelated or unsafe binaries. Do not disable Defender or other host protections.

## Phase A execution skeleton

Use only retained inputs and already-evidenced requests.

Money request:

```json
{"money": 7654321}
```

Inventory request:

```json
{"slot": 0, "item_id": 13, "quantity": 3}
```

Party request:

Choose one or more exact requests already accepted by the canonical bounded party editor. Do not invent a transition or broaden the request range.

For each family where the retained input exists:

- hash source ROM/save before;
- unified CLI `inspect`;
- unified CLI `preview`;
- prove preview creates no output;
- derive the same request through the bounded underlying module and compare candidate bytes/diffs;
- unified CLI `write` to a new nonexistent private path;
- verify overwrite refusal;
- verify persisted bytes equal preview candidate;
- repository-verifier revalidate output;
- compare against exact prior live-confirmed FL1 output where applicable;
- hash source ROM/save after and prove immutability.

A new mGBA live run is not required when the unified output is byte-identical to an existing live-confirmed FL1 output. Use emulator execution only to resolve a concrete discrepancy that cannot be closed offline.

## Phase B design skeleton

For Money, Party, and Inventory independently evaluate:

- exact build/ROM gate;
- structural verifier gate;
- save/slot/section invariants;
- semantic preconditions;
- encryption-key assumptions;
- checksum coverage;
- coupled/cached fields;
- inactive-slot, extra-sector, footer preservation;
- allowed request range;
- allowed byte-diff or independently computable invariant envelope;
- post-write verification;
- unsupported/ambiguous rejection;
- proof needed before replacing exact input SHA gating;
- recovery/output policy;
- chained-edit / normal-resave proof requirements;
- user value;
- implementation complexity;
- failure cost;
- evidence already available;
- cheapest missing proof.

Select exactly one first reusable-envelope family and explain why the other two are not the cheapest next proof.

## Stop / escalation rules

Do not stop merely because:

- one command fails from a local path assumption;
- a retained file is not found in the first searched directory;
- a test runner needs an equivalent available invocation;
- an intermediate family is unsuitable as the first reusable target.

Investigate bounded, reversible alternatives and continue.

Stop for Human input only when a concrete blocker requires information/authority unavailable locally, for example:

- required private artifact is genuinely absent after reasonable local search;
- canonical state conflicts materially with the authorized contract;
- completing the next useful step requires broadening writer capability;
- a discrepancy would require new emulator/game interaction not justified by existing evidence;
- protected data would need to leave the private workspace;
- repository/canonical mutation beyond an explicitly authorized evidence-record candidate is necessary.

When blocked, report the exact blocker, evidence gathered, attempted alternatives, and minimum Human action needed.

## Git / canonical mutation boundary

Default execution should be read-only against canonical `main` plus repo-external private outputs.

Codex may create a local evidence/design record or local branch if useful, but must not merge, fast-forward, force-update, or otherwise mutate canonical `main` without separate Human authorization.

Do not close old PRs/issues as part of this Goal unless separately authorized.

## Final decision packet

Return:

- fresh canonical HEAD used;
- local execution environment;
- private artifact identities by hash only;
- exact commands/results or sufficiently precise command log;
- Phase A evidence by family;
- unified-vs-underlying equality results;
- source immutability evidence;
- verifier/output identities;
- test/static/security results;
- evidence labels distinguishing reproduced evidence, local private-input verification, upstream evidence, prior observation, and hypothesis;
- Phase A disposition: `PASS_POST_FL2_PRIVATE_ACCEPTANCE` or `CORRECTION_REQUIRED`;
- comparative Money / Party / Inventory reusable-envelope analysis;
- exactly one selected first family;
- exact proposed fail-closed eligibility predicate;
- required private proof;
- benefit;
- risk/trade-off;
- downstream impact;
- exact bounded implementation scope that would require the next Human authorization.

## Suggested Codex Goal

Use a Goal equivalent to:

> Complete the authorized post-FL2 acceptance and reusable-envelope design gate for `Ryo722/pokemonstart-save-editor-research`. Fresh-read current remote `main` as canonical and follow `docs/post-fl2-acceptance-and-reusable-envelope-plan.md` plus this handoff as the controlling execution contract. Continue autonomously through Phase A private acceptance, validation, Phase B family comparison, first-family selection, and exact predicate preregistration. Stop only when the completion conditions are satisfied or a concrete Human-only blocker is reached. Do not implement broader reusable writer eligibility or mutate canonical `main`.

## Current next action

**Launch local Codex in the repository/private-workspace context, establish the Goal above, and allow it to run through Phase A + Phase B to the next Human decision gate.**
