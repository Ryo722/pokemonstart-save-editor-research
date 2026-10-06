# Exact-v0.22 key0 fixed-target Money reusable-envelope qualification — 2026-10-07

Status: **CANONICAL AUTHORIZATION / ACTIVE NEXT-WORK BOUNDARY**

GitHub `main` remains the only durable canonical authority.

## Human authorization

Controlling authorization:

> `AUTHORIZE EXACT-V0.22 KEY0 FIXED-TARGET MONEY REUSABLE-ENVELOPE QUALIFICATION`

This authorization follows the reviewed post-FL2 Phase A/B evidence branch:

- branch: `codex/post-fl2-acceptance-design-20261007`
- exact reviewed HEAD: `93c070215181bb9e1a83c1b1b0bc82110a726793`
- canonical base of that packet: `d4740a665d1a4f070a7540d8964e6838e393392b`

The packet disposition was `PASS_POST_FL2_PRIVATE_ACCEPTANCE` and selected Money as the first reusable-envelope family. The evidence packet itself remains review-branch evidence unless separately merged; this canonical record adopts the bounded authorization below, not every incidental statement in the packet.

## Current position

FL0, FL1, FL2-G0 and FL2 are complete for the exact-v0.22 Fast Lab slice. The merged unified CLI has now received private end-to-end acceptance on retained canaries. Practical reuse on naturally progressed owner saves is still unproven.

Current transition:

`FL2 complete -> post-FL2 acceptance PASS -> Money reusable-envelope qualification ACTIVE`

The objective is not a generic Money editor. It is to determine whether exact retained-save SHA membership can be replaced, for one Money-only path, by a strict independently checkable semantic/invariant predicate while keeping all other capability gates unchanged.

## Authorized capability candidate

Only the following qualification candidate is authorized:

- PokemonStart exact v0.22 profile only;
- exact profile ROM SHA-256 gate retained;
- capability-profile schema/build agreement retained;
- encryption key `0` in both valid slots;
- target Money fixed to exactly `7,654,321`;
- no-op target already present => reject/no output;
- Money-only reusable eligibility may replace exact retained-save SHA membership only when the preregistered conservative predicate passes;
- Party and Inventory write eligibility remain unchanged and exact-save gated;
- source inputs remain immutable;
- output must be a separate new private file;
- repository verifier plus independent checks must accept the generated output.

## Preregistered initial predicate

Implementation must preserve the reviewed predicate materially unchanged. If evidence shows it is wrong or insufficient, fail closed and return for Human review rather than relaxing it.

### Build / file gate

- owner-designated private save for exact v0.22 only;
- supplied ROM SHA-256 must match the exact capability profile;
- profile schema/build/module contracts must agree;
- supported file length only: `0x20000` or `0x20010`;
- source ROM/save hashes checked before and after the transaction.

### Conservative slot gate

For the first reusable proof:

- both save slots valid;
- logical section IDs 0–13 exactly once per valid slot;
- signatures and section-specific covered checksums valid;
- one counter value per slot;
- counters restricted to the preregistered ordinary non-wrap range;
- counters consecutive with expected slot/counter parity;
- verifier selects one unambiguous active slot;
- reject equal/nonconsecutive/wrap/sign-boundary/partial-erased/ambiguous states.

Physical section order must be derived from logical IDs, not assumed.

### Money semantics

For both valid slots:

- SaveBlock2 key at logical section 0 offset `0x0F20` must be exactly `0`;
- decoded Money must be within `0..9,999,999`;
- request must be a JSON object with exactly one key, `money`;
- value type must be an integer, with bool/float/string rejected;
- value must equal exactly `7,654,321`;
- active current Money must not already equal the target.

### Authorized transaction

Resolve the active logical section 1 physical base `B` from section IDs. Candidate output is a clone of the source except:

- write LE32 `7,654,321` at `B + 0x0290`;
- recompute the logical section 1 covered checksum over its canonical covered range and write it at the section checksum field;
- no other semantic writer operation is permitted.

The exact changed-byte set must be nonempty and be a subset of the four Money bytes plus the two section-checksum bytes. Checksum bytes are allowed to remain equal when recomputation yields the same value; change of the checksum field itself is not mandatory.

### Preservation / postcondition

Require:

- candidate length unchanged;
- persisted output exactly equals the previewed independently computed candidate;
- repository verifier accepts output;
- independent parser/auditor confirms signatures/checksums/section map/Money decode;
- active slot index/counter unchanged by the transaction;
- inactive slot unchanged byte-for-byte;
- party bytes unchanged;
- sectors 28–31 unchanged;
- opaque footer unchanged;
- checksum-excluded tails unchanged;
- both encryption keys unchanged and still zero;
- active decoded Money exactly `7,654,321`;
- source ROM/save remain unchanged.

## Required qualification proof

The qualification is not complete merely when code/tests pass. The private repeated-use proof is required.

At minimum:

1. Regression: retained exact Money canary still produces its existing exact output identity.
2. Non-canary qualification: use the preregistered naturally progressed private save identified by SHA only in the reviewed packet; prove the predicate independently and generate a Money-only output to a new private path.
3. Independent offline audit: do not rely solely on the writer or repository verifier; verify full transaction diff and preserved surfaces independently.
4. Exact-v0.22 game/load confirmation: confirm target Money and relevant nonchanged state; do not infer gameplay success from metadata alone.
5. Normal game resave with target Money retained, followed by independent slot/counter/rotation audit.
6. Ordinary in-game Money change and another normal resave, recording actual starting Money/change semantics.
7. Second qualification/write from the newly progressed save to the same fixed target, followed by independent audit and reload/live confirmation.
8. Another normal save proving the repeated editor -> game -> editor lifecycle.
9. No-op request after target is already present must reject without creating output.
10. Positive/negative synthetic and private checks for the preregistered malformed/ambiguous/key/request/path/race/corruption cases as practical.
11. Focused tests, Fast Lab regressions, mGBA harness where relevant, full repository suite, compile, capability JSON, diff, protected-artifact and secret checks.

A discrepancy does not authorize widening the predicate. Return `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE` when the bounded candidate cannot be proven as preregistered.

## Push / review policy

Local Codex is the default executor because private ROM/save inputs must remain local.

Codex may create and push a review branch containing only push-safe material:

- source code;
- tests;
- independent auditor code that contains no protected bytes;
- sanitized design/evidence records;
- hashes, sizes, structural summaries and non-sensitive diff metadata.

Never push ROMs, saves, `.pks`, BPS/IPS, executables, proprietary payloads, copyrighted assets, raw private memory dumps, raw private command logs, or private/protected bytes.

Before push, run diff/protected-artifact/secret checks. Branch push does not imply canonical adoption.

## Explicit non-goals

This authorization does not permit:

- arbitrary Money targets;
- nonzero encryption-key support;
- Party or Inventory reusable eligibility;
- combined reusable operations;
- other PokemonStart versions/builds;
- generic CFRU support;
- Stable promotion;
- GUI/public release;
- protected-data publication;
- canonical `main` merge/adoption.

## Completion / next Human gate

A successful result should end as a pushed exact review candidate with disposition:

`READY_FOR_INDEPENDENT_REVIEW`

Otherwise:

`BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`

After branch publication, ChatGPT independently reviews fresh canonical `main`, exact branch HEAD, complete diff, tests/evidence, capability boundary and private-evidence claims that can be corroborated remotely. ChatGPT then prepares the next Human decision and next Codex Goal.

Even after successful qualification, canonical merge/adoption requires a separate explicit Human authorization.
