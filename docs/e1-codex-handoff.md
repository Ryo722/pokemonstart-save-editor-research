# Codex execution handoff — E1 -> E5 exact-v0.22 expansion

Date: 2026-10-07

Repository: `Ryo722/pokemonstart-save-editor-research`

Canonical authority: current remote `main` only.

## Mission

Implement the adopted E-series path toward the Exact-v0.22 PKHeX-like Practical Editor. Start with E1 Inventory model qualification. Continue autonomously through a bounded implementation step only when the preceding evidence gate is actually satisfied.

Do not treat this prompt as evidence. Fresh-read canonical state and the research packet.

## Required fresh-read

At minimum:

1. current remote `main` HEAD;
2. `README.md`;
3. `docs/decision-record.md`;
4. `docs/evidence.md`;
5. `docs/v022-pkhex-like-editor-expansion.md`;
6. `docs/e1-e5-implementation-readiness-research.md`;
7. current Inventory / Party / GUI implementation and tests;
8. current open issues / PRs.

Reconstruct current position, completed proofs, unresolved uncertainty, protected-data boundary, and exact Human authorization before changing code.

## Recommended branch

Create a fresh candidate branch from current `main`:

`codex/e1-v022-inventory-model-qualification`

Do not base work on stale historical branches.

## E1 execution order

### A. Exact-build static corroboration

Using the private exact-v0.22 ROM only locally:

- verify the exact ROM SHA/profile;
- verify the expected CFRU bag/runtime anchors rather than assuming them;
- independently establish the serialization scatter map used by exact v0.22;
- verify pocket capacities and the actual TM/HM count;
- identify exact ROM item-table metadata and build a read-only catalog;
- determine whether relevant auto-sort / anti-cheat / quantity behavior is present in the exact build.

Do not publish ROM bytes, raw proprietary tables, or protected payloads. Sanitized decoded metadata necessary for a safe catalog may be recorded only where legally/safely appropriate; otherwise record derivation method and hashes.

### B. Read-only generalized decoder/auditor first

Before any broader writer:

- decode supported pocket records across all physical storage fragments;
- handle the regular-pocket section13 -> sector30 boundary;
- validate item IDs against exact-ROM metadata;
- decode quantities under the qualified key model;
- expose capacity, occupied slots, holes and ordering;
- report unsupported/corrupt states explicitly;
- provide an independent audit path separate from the future writer.

Add synthetic boundary tests for:
- regular slot 0;
- regular slot 324;
- regular slot 325;
- regular slot 449;
- each supported pocket start/end;
- malformed IDs/quantity/state;
- nonzero key if unsupported.

### C. Native-transition discrimination

Reuse existing canonical Potion/Antidote evidence. Do not ask the Human for repetitive gameplay unnecessarily.

Only when unresolved after static/private analysis, request the minimal targeted Human transition from the matrix in the research packet. Make the request exact: starting condition, one game action, normal SAVE, close/flush, and which snapshots to retain.

### D. E1 decision

Produce an evidence matrix showing every E1 exit criterion as PASS / FAIL / NOT ESTABLISHED.

If any required writer semantic remains ambiguous, stop with:

`BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`

and identify the cheapest discriminating next proof.

If E1 qualifies, record:

`E1_MODEL_QUALIFIED_FOR_E2_CANDIDATE`

### E. E2 bounded implementation when E1 qualifies

Only after E1 qualification, implement the E1-supported ordinary-item model:

- add absent supported item;
- set/change quantity;
- remove;
- required compaction/order;
- semantic postconditions;
- independent decoder/auditor acceptance;
- separate output only;
- GUI exposure consistent with the model.

Give All Supported Items remains disabled unless its catalog + capacity/order prerequisites all independently pass. Never implement “all IDs”.

## Later E3-E5

After an independently reviewable E1/E2 checkpoint, follow the canonical E3-E5 contract. The readiness research packet identifies the source-backed Pokémon record/table path.

Do not let optional fields block the practical major-field goal. Do not start Box support.

## Verification

At each implementation checkpoint:

- focused tests;
- full repository test suite in the applicable environment;
- Python compile/static parse checks;
- exact candidate diff review;
- protected-artifact/path scan;
- secret scan;
- source/private-input immutability checks;
- independent audit of changed byte envelope;
- exact-v0.22 game round trip where required by the milestone rather than inferred from verifier acceptance.

## Protected-data boundary

Never commit/upload:

- `.gba`, `.sav`, `.pks`;
- BPS/IPS;
- extracted EXE/proprietary package payloads;
- copyrighted game assets;
- raw private-save/ROM hexdumps;
- private absolute paths or secrets.

## GitHub / authority boundary

Authorized:
- candidate implementation;
- tests;
- local private verification;
- sanitized evidence;
- commits and push to the candidate branch;
- coherent E1/E2 implementation work that stays inside the adopted exact-v0.22 expansion contract.

Not authorized by this handoff:
- merge to `main`;
- canonical capability adoption;
- public release;
- Stable promotion;
- another PokemonStart version;
- Box/Pokédex/story/event/quest/RTC writing;
- unsafe all-items;
- public/LAN GUI;
- protected-data publication.

## Required terminal packet

Before stopping for independent review, publish a sanitized packet containing:

- canonical base SHA;
- exact candidate HEAD/tree;
- changed-file inventory;
- E1 criterion matrix;
- exact-build corroboration results;
- decoder/auditor model;
- item-catalog derivation and safety policy;
- any native-transition evidence;
- E2 writer capability matrix if implemented;
- tests/static/security results;
- explicit non-claims;
- remaining uncertainty;
- confirmation that no protected artifacts are tracked.

End with one of:

- `E1_MODEL_QUALIFIED_FOR_E2_CANDIDATE` if only model qualification is complete;
- `READY_FOR_INDEPENDENT_REVIEW` if an E1/E2 implementation candidate is ready;
- `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE` if evidence blocks safe progress.

Do not perform the independent review yourself in the implementation context.
