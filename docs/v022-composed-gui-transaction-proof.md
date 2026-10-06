# Exact-v0.22 Party append + Inventory insertion composed GUI transaction proof — 2026-10-07

Status: **CANONICAL AUTHORIZATION / ACTIVE NEXT-WORK BOUNDARY**

GitHub `main` is the only durable canonical authority.

## Human authorization

Controlling authorization:

> `AUTHORIZE EXACT-V0.22 PARTY-APPEND + INVENTORY-INSERTION COMPOSED GUI TRANSACTION PROOF`

This authorization expands only the already-adopted exact-v0.22 Fast Lab creation slice by proving one composed transaction from the same exact proof root.

## Canonical base

Expected base at authorization:

`909ae1437562f32d0e64ce3cb056e3be3d310d85`

The adopted creation/GUI slice remains canonical history. The paused Money reusable-envelope branch remains excluded.

## Exact proof root and adopted primitives

Exact source save SHA-256:

`2d7ac8d6214e8b94018a3fe3f65c30270198098a9cb658318248b514242511ac`

Exact v0.22 ROM SHA-256:

`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

Already-adopted primitives:

1. **Party append**
   - party count `3 -> 4`;
   - copy the complete existing slot0 100-byte record into slot3;
   - no internal record synthesis;
   - recompute only the required logical section1 checksum.

2. **Inventory insertion**
   - regular-items slot2;
   - Antidote item ID14;
   - quantity1;
   - key0;
   - preserve Money and existing item order;
   - editor field remains outside section13 checksum-covered range.

## Goal

Prove exactly one new Fast Lab experimental capability:

> apply both adopted primitives together to the same exact proof-root input, producing one verified candidate and one GUI transaction.

This is not authorization for a generic transaction engine, applying creation operations to their own outputs, naturally progressed-save reuse, arbitrary Pokémon creation, arbitrary item insertion, Money composition, nonzero-key support, broader builds, Stable promotion, or public/LAN delivery.

## Phase 1 — composed core proof

Implement one explicit narrow operation, preferably named:

`party_append_inventory_insert`

The operation should accept no new user-controlled field values; an empty request object is preferred.

Requirements:

- exact source SHA gate remains the proof-root SHA above;
- exact ROM/profile gate remains unchanged;
- derive logical section positions from verified section IDs;
- apply only the two already-adopted semantic changes;
- preserve all bytes outside the union of the two adopted edit envelopes;
- repository verifier must accept the candidate;
- source bytes remain immutable.

Independent audit must establish:

- complete candidate equality using an implementation independent of the product writer;
- Party count exactly `3 -> 4`;
- original three complete Party records unchanged;
- fourth record equals original slot0's complete 100-byte record;
- existing regular items ID13×2 and ID533×1 remain unchanged and ordered;
- Antidote ID14×1 exists only in the observed slot2;
- Money remains exactly 3032;
- key remains zero;
- footer, inactive slot, counters and all unrelated bytes are unchanged by the editor transaction.

The composed changed-offset set must equal exactly the union of the independently reproduced adopted Party-append and Inventory-insertion changed-offset sets.

Canonical evidence suggests 54 changed bytes total. Do not hardcode that as a pass condition if fresh reproduction contradicts it. Any discrepancy must stop the proof rather than relax scope.

Also prove complete-candidate order independence with an independent derivation: Party+Inventory and Inventory+Party must resolve to exactly the same candidate bytes.

Do not weaken the product's exact-source gates merely to call the existing single-operation product functions sequentially.

## Phase 2 — exact-v0.22 composed persistence proof

Use only repo-external disposable copies.

Load the composed candidate and confirm:

- normal gameplay reached;
- Party count 4;
- all four live 100-byte Party records equal offline candidate;
- regular items show the two existing records plus Antidote ID14×1;
- Money remains 3032;
- no unexpected visible corruption.

Perform one normal in-game SAVE.

Independently audit the returned save:

- slot/counter transition;
- section rotation;
- prior active slot preservation according to the verified save model;
- Party composition persistence;
- Inventory composition persistence;
- Money persistence;
- key0 persistence;
- all ordinary save-time changes fully reported/classified without masking unknown changes.

Cold reload the returned save in a fresh emulator process and reconfirm Party / Inventory / Money.

One composed game round trip is sufficient for this Goal.

## Phase 3 — GUI composed transaction

Extend the adopted localhost-only GUI with one explicit combined choice corresponding to the exact composed operation.

Do not create a generic arbitrary multi-operation transaction editor unless strictly necessary.

Retain:

- `127.0.0.1` only;
- in-memory source handling;
- inspect before edit;
- semantic + byte-diff preview;
- stale source / stale ROM / stale preview rejection;
- repository verification;
- verified separate download only;
- no emulator live-save overwrite path.

GUI acceptance requires:

- upload exact root;
- select the combined operation;
- preview reports both semantic changes;
- generated/downloaded bytes exactly equal the game-confirmed composed core candidate;
- independent auditor accepts;
- repository verifier accepts;
- source remains unchanged;
- simulated NiceGUI workflow passes;
- actual Chromium smoke passes when the existing local environment still supports it.

No second emulator round trip is required when GUI bytes are exactly equal to the already game-confirmed composed core candidate.

## Negative and regression coverage

At minimum reject:

- wrong input SHA;
- wrong ROM/profile;
- nonzero key;
- altered Party count/template/destination shape;
- altered existing item records/order;
- occupied insertion destination;
- unexpected nonzero item tail;
- nonempty/extra composed request fields;
- attempts to combine the new composition with Money or arbitrary existing FL2 requests;
- stale source;
- stale ROM;
- stale preview;
- corrupted generated/download bytes.

Regression requirements:

- original Party append output identity unchanged;
- original Inventory insertion output identity unchanged;
- canonical FL2 Money/Party/Inventory gates unchanged;
- existing single-operation GUI behavior unchanged;
- paused Money reusable candidate remains excluded.

## Final validation / publication

Run focused composition tests, existing creation tests, GUI tests, actual-browser smoke where available, Fast Lab/FL2/M4 regressions, full repository tests, `py_compile`, capability JSON parse, `git diff --check`, protected-artifact scan and Gitleaks/secret scan.

Publish only push-safe source/tests/auditor/sanitized evidence/docs to a fresh work branch, for example:

`codex/v022-composed-gui-transaction-20261007`

Never push ROMs, saves, `.pks`, patches, executables, screenshots/raw memory, raw private logs, save hexdumps or copyrighted/private game bytes.

Do not mutate canonical `main`.

## Stop rule

Success disposition:

`READY_FOR_INDEPENDENT_REVIEW`

Stop with:

`BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`

if the exact adopted envelopes cannot be composed without speculative scope expansion or a Human-only blocker.

## Completion packet

Return at minimum:

- canonical base SHA;
- exact branch + HEAD;
- changed files;
- composed output SHA;
- exact changed-byte count and union result;
- independent complete-candidate and order-independence results;
- exact-v0.22 load/SAVE/cold-reload result;
- GUI/core byte-equality result;
- regression results;
- full test/static/security results;
- remaining non-claims;
- exact disposition.

No canonical merge/adoption is authorized by this work authorization alone.
