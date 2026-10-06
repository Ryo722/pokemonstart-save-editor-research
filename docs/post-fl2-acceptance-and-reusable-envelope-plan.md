# Post-FL2 acceptance and reusable-envelope plan — 2026-10-06

Status: **CANONICAL DECISION / AUTHORIZED NEXT-WORK BOUNDARY**

GitHub `main` is the durable canonical authority.

## Human authorization

Controlling authorization:

> `AUTHORIZE POST-FL2 ACCEPTANCE AND REUSABLE-ENVELOPE PLAN`

This authorization adopts the post-FL2 milestone-boundary audit result. It authorizes the private acceptance execution described below and the reusable-envelope design/preregistration work. It does **not** authorize reusable-envelope writer implementation, Stable promotion, public release, broader PokemonStart version support, nonzero-key support, ability writes, broader Inventory support, protected-data publication, or GUI exposure.

## Fresh canonical basis

FL2 unified practical local CLI was Human-authorized and fast-forwarded into canonical `main` at exact merge/adoption commit:

`e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

The merged FL2 implementation provides one exact-v0.22 local workflow for:

- profile/save inspection;
- semantic preview;
- byte-diff preview;
- bounded Money / Party / Inventory operations already evidenced in FL1;
- separate-output publication;
- repository-verifier revalidation;
- explicit rejection of unsupported builds/saves/requests.

The implementation preserves the Fast Lab experimental evidence class and delegates field derivation to existing bounded Fast Lab modules.

## Post-FL2 audit conclusion

The refined terminal goal is **partially satisfied, not fully closed**.

The workflow and safety contract exist durably, but current write eligibility is still tied to exact retained input-save SHA-256 values. A structurally valid owner save that has naturally changed through game progress is therefore not automatically writable even when its semantic structure remains compatible.

Current state is best described as:

> **profile-bounded workflow with canary-snapshot-bounded write eligibility**

This is an intentional fail-closed safety posture, but it does not yet prove a reusable owner-save editing envelope.

## Phase A — post-FL2 private acceptance

Purpose: prove that the merged unified CLI itself faithfully delivers the already-proven FL1 behavior. This phase adds **no capability**.

Default executor: local Codex on the owner's private workspace. Private ROM/save bytes remain outside Git.

### Required checks

Start from fresh current remote `main` and record the exact HEAD. Confirm that FL2 production code is unchanged from the Human-authorized implementation content merged at `e44e85358be9a1e72e0cd84c65d446eec5bd81c2`, apart from later documentation-only canonical-state synchronization if present.

Using only retained private exact-v0.22 canary inputs already accepted by the underlying modules:

1. verify exact private v0.22 ROM SHA-256 and capability-profile identity;
2. run unified CLI `inspect` on each relevant retained Money / Party / Inventory canary input;
3. run unified CLI `preview` for at least one already-evidenced operation in each family;
4. confirm preview performs no filesystem publication and source hashes remain unchanged;
5. compare unified preview semantic/byte results against the underlying bounded module derivation for the same request;
6. run unified CLI `write` to a new, nonexistent private output path;
7. confirm exclusive-create / no-overwrite behavior;
8. confirm persisted output bytes equal the preview candidate exactly;
9. confirm repository verifier accepts each generated output;
10. confirm source ROM and source save hashes are unchanged before/after;
11. when an existing FL1 live-confirmed output identity exists for the exact request, confirm the unified CLI produces the same bytes/hash; otherwise classify the result only as unified-wrapper acceptance, not new live gameplay evidence;
12. run focused FL2 tests and the full repository test suite after the private acceptance run;
13. perform `py_compile`, capability JSON parse, `git diff --check`, protected-artifact scan, and secret scan as applicable;
14. do not commit or upload ROMs, saves, package payloads, BPS/IPS, executables, screenshots containing protected/private data, or extracted copyrighted assets.

### Acceptance success criteria

Phase A passes only if:

- the exact merged/current FL2 code path is exercised rather than only underlying modules;
- inspect/preview/write/verify all work on retained private exact-v0.22 canary inputs;
- unified outputs are byte-identical to the bounded derivations they wrap;
- source inputs remain immutable;
- unsupported/write-boundary behavior remains fail closed;
- no new field/build/key/save support is inferred from the acceptance run;
- focused/full tests and static checks remain green.

A live mGBA replay is **not required by default** when unified output is byte-identical to an already live-confirmed FL1 output. Run new emulator interaction only if the unified path produces a concrete discrepancy that cannot be resolved statically/offline.

## Phase B — reusable exact-v0.22 save-envelope design / preregistration

Purpose: define the cheapest safe path from exact-save-SHA gating toward a reusable owner-save envelope for already-evidenced capabilities.

This phase is **design/evidence planning only** under the current authorization. Do not implement a broader writer yet.

### Design question

For an exact-v0.22 save that is not one of the retained canary hashes, what independently checkable predicates are sufficient to decide that a specific existing operation can be applied without guessing?

The design must evaluate capability families independently. A predicate adequate for Money must not automatically authorize Party or Inventory.

### Required design surfaces

For each existing family (Money, Party, Inventory), preregister:

- exact ROM/build gate;
- structural verifier requirements;
- required slot/counter/section invariants;
- field-specific semantic preconditions;
- encryption-key assumptions and rejection rules;
- checksum-covered and checksum-excluded regions touched;
- coupled/cached fields that must be recomputed or preserved;
- inactive-slot / extra-sector / footer preservation requirements;
- allowed semantic request range;
- allowed byte-diff envelope or independently computable diff predicate;
- post-write verification requirements;
- ambiguity / malformed / unsupported rejection behavior;
- evidence required before replacing exact-SHA eligibility with the new predicate;
- recovery/output naming policy;
- whether one normal gameplay resave/chained edit is necessary to prove reuse for that family.

### Cheapest proof target

Prefer the smallest family-specific reusable proof that materially improves owner use. Do not attempt a generic arbitrary-save editor.

Candidate ordering should be justified from evidence rather than assumed. Likely low-cost targets may include a repeated bounded Money edit or a narrowly recognized Party state, but the design must independently compare cost, value, and coupling before selecting one.

### Explicit non-goals

This plan does not authorize:

- removal of exact-save gates in production code;
- arbitrary Money values;
- arbitrary Party values/species/moves/levels;
- ability-selector writes;
- Inventory insertion/deletion/reordering or arbitrary item IDs/pockets;
- nonzero-key Fast Lab support;
- other PokemonStart versions/builds;
- generic CFRU support;
- GUI/public distribution;
- Stable promotion.

## Decision gate after Phase A/B

Return a bounded decision surface containing:

- Phase A exact execution identity and disposition;
- reproduced evidence vs prior observation labels;
- any discrepancy/blocker;
- proposed first reusable-envelope family;
- exact predicate proposal;
- evidence supporting it;
- benefit;
- risk/trade-off;
- required private proof;
- downstream impact;
- exact implementation scope that would require separate Human authorization.

Stop before implementing broader writer eligibility unless the Human explicitly authorizes that exact bounded implementation.

## Current next step

**Run Phase A post-FL2 private acceptance locally, then complete Phase B reusable-envelope design/preregistration from the resulting evidence. No reusable-envelope implementation yet.**
