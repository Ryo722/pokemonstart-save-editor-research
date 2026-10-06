# FL2 unified practical CLI — merged implementation and validation record

Status: **COMPLETE / MERGED into canonical `main`**

Canonical adoption commit:

`e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

Original FL2 base after the Human-authorized FL2-G0 merge:

`44c90e8217061cc8ac294a392984dfe73e622d80`

Human authorization:

> `AUTHORIZE FL2 MERGE e44e85358be9a1e72e0cd84c65d446eec5bd81c2`

## Purpose

FL2 adds no save-field capability. It consolidates the already-evidenced exact-v0.22 Fast Lab operations into one local workflow that can inspect the exact profile, preview supported changes, show semantic and byte diffs, write only a new output, verify that output, and reject unsupported saves/requests without guessing.

## Bounded workflow

`pokemonstart_fl2_cli.py` exposes:

- `inspect INPUT --rom ROM`
- `preview INPUT --operation {money,party,inventory} --changes-json JSON --rom ROM`
- `write INPUT OUTPUT --operation {money,party,inventory} --changes-json JSON --rom ROM`

Field derivation remains delegated to the existing reconciled Fast Lab modules:

- Money: `pokemonstart_fastlab_v022_money.derive`
- Party: `pokemonstart_fastlab_v022_party_editor.derive_bytes`
- Inventory: `pokemonstart_fastlab_v022_inventory_editor.derive_bytes`

FL2 therefore does not silently broaden any existing request range.

### Exact current requests

Money remains the exact retained Money canary request:

```json
{"money": 7654321}
```

Party remains limited to requests already accepted by the reconciled FL1 party editor, including its exact single-field transitions and exact composed canary. Empty/no-op requests are rejected by the unified workflow.

Inventory remains exactly:

```json
{"slot": 0, "item_id": 13, "quantity": 3}
```

for the exact retained Potion-bearing save.

## Safety and profile behavior

- The supplied ROM must hash to the exact v0.22 profile SHA-256.
- Write support is exposed only when the source save SHA-256 matches the corresponding retained FL1 canary accepted by the underlying module.
- A structurally valid but unrecognized save may be inspected only as `UNSUPPORTED_SAVE_PROFILE`; FL2 exposes no write operation for it.
- Source ROM/save paths and output paths remain inside the private workspace boundary.
- `write` refuses source overwrite and pre-existing output paths and uses exclusive creation.
- The source is re-hashed before and after publication.
- The persisted output must match the previewed candidate SHA-256 and pass the repository verifier.
- On publication failure, a newly-created output is removed where possible.
- Fast Lab evidence remains experimental; no Stable promotion, nonzero-key generalization, broad-version support, ability write, or broader Inventory support is implied.

## Implementation / test files added by FL2

- `pokemonstart_fl2_core.py`
- `pokemonstart_fl2_cli.py`
- `tests/test_fl2_core.py`
- `tests/test_fl2_cli.py`

One pre-existing harness test was made runner-independent after full-suite validation exposed a `TMPDIR`-placement assumption:

- `tests/test_mgba_harness.py`

FL2 also synchronized `README.md` and `docs/decision-record.md` to the then-current FL2 state. Post-merge status is controlled by the later canonical decision record and `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`.

## Validation evidence before merge

Exact implementation/test candidate exercised by the local runner:

`afcfb7219603b209b1e98b930f68b3ccaa18a832`

Evidence class: **local runner verification reported by the Human/operator; not independently re-executed by ChatGPT**.

Results:

- focused FL2 tests: **10 passed**;
- existing Fast Lab regression tests: **34 passed**;
- mGBA harness tests: **11 passed**;
- full `unittest` suite: **176 tests total, 160 passed, 16 skipped, 0 failed, 0 errors**;
- `py_compile`: **70 tracked Python files passed**;
- `docs/fast-lab-v022-capability.json`: parse passed;
- `git diff --check`: passed for canonical-base cumulative diff and correction diff;
- protected/executable tracked-artifact suffix scan: no matches;
- Gitleaks: no leaks reported.

The correction from `6c428e293fa6ec7108cfe8fa192d0c889f38f175` to tested `afcfb7219603b209b1e98b930f68b3ccaa18a832` changed only:

- `tests/test_fl2_core.py` — resolved the temporary root once so macOS `/var` -> `/private/var` canonicalization did not invalidate the mocked private-root boundary;
- `tests/test_mgba_harness.py` — chose an explicit path outside `HOST_SCOPE` so host-scope rejection did not depend on `TMPDIR` placement.

No production implementation, Stable writer, Fast Lab writer, capability profile, or capability range changed in that correction.

The final adoption SHA `e44e85358be9a1e72e0cd84c65d446eec5bd81c2` was one documentation-only commit after the tested implementation SHA. Independent remote review confirmed that delta changed only this FL2 evidence record and did not alter implementation/tests.

## Post-merge assessment

FL2 proves the unified workflow and delivery contract, but not reusable eligibility for naturally changed owner saves. Current write eligibility remains tied to exact retained input-save SHA-256 canaries.

Therefore FL2 is **complete**, while the refined terminal goal remains only partially satisfied until practical reuse is addressed or deliberately scoped out by a later Human decision.

Current next work is controlled by:

- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`

That plan authorizes private acceptance of the merged CLI and reusable-envelope design/preregistration only. Broader writer eligibility still requires separate Human authorization.
