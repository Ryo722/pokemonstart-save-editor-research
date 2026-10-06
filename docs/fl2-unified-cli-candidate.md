# FL2 unified practical CLI — implementation candidate

Status: **candidate implementation on `codex/fl2-unified-cli`; not adopted or merged into canonical `main`**

Base: canonical `main` `44c90e8217061cc8ac294a392984dfe73e622d80`, after the Human-authorized FL2-G0 fast-forward merge.

## Purpose

FL2 does not add save-field capability. It consolidates the already-evidenced exact-v0.22 Fast Lab operations into one local workflow that can inspect the exact profile, preview supported changes, show semantic and byte diffs, write a new output only, verify that output, and reject unsupported saves/requests without guessing.

## Bounded workflow

`pokemonstart_fl2_cli.py` exposes three actions:

- `inspect INPUT --rom ROM`
- `preview INPUT --operation {money,party,inventory} --changes-json JSON --rom ROM`
- `write INPUT OUTPUT --operation {money,party,inventory} --changes-json JSON --rom ROM`

The implementation delegates field derivation to the existing reconciled Fast Lab modules:

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
- Source ROM/save paths and output paths remain inside the existing private workspace boundary.
- `write` refuses source overwrite and pre-existing output paths and uses exclusive creation.
- The source is re-hashed before and after publication.
- The persisted output must match the previewed candidate SHA-256 and pass the repository verifier.
- On publication failure, a newly-created output is removed where possible.
- Fast Lab evidence remains experimental; no Stable promotion, nonzero-key generalization, broad-version support, ability write, or broader Inventory support is implied.

## Candidate files

Implementation/tests:

- `pokemonstart_fl2_core.py`
- `pokemonstart_fl2_cli.py`
- `tests/test_fl2_core.py`
- `tests/test_fl2_cli.py`

State/documentation synchronization on the candidate branch:

- `README.md`
- `docs/decision-record.md`
- this record

One pre-existing harness test was also made runner-independent after full-suite validation exposed a `TMPDIR`-placement assumption:

- `tests/test_mgba_harness.py`

The documentation synchronization records the already-completed FL2-G0 merge and makes FL2 the active milestone; it does not change field capability or evidence classification.

## Verification status

### Local runner verification of exact tested candidate

Exact tested candidate:

`afcfb7219603b209b1e98b930f68b3ccaa18a832`

Evidence class: **local runner verification reported by the Human/operator; not independently re-executed by ChatGPT**.

Results:

- focused FL2 tests: **10 passed**;
- existing Fast Lab regression tests: **34 passed**;
- mGBA harness tests: **11 passed**;
- full `unittest` suite: **176 tests total, 160 passed, 16 skipped, 0 failed, 0 errors**;
- `py_compile`: **70 tracked Python files passed**;
- `docs/fast-lab-v022-capability.json`: parse passed;
- `git diff --check`: passed for both canonical-base cumulative diff and correction diff;
- protected/executable tracked-artifact suffix scan: no matches;
- Gitleaks: no leaks reported.

The final correction from `6c428e293fa6ec7108cfe8fa192d0c889f38f175` to the tested `afcfb7219603b209b1e98b930f68b3ccaa18a832` changed only:

- `tests/test_fl2_core.py` — resolve the temporary root once so macOS `/var` -> `/private/var` canonicalization does not invalidate the mocked private-root boundary;
- `tests/test_mgba_harness.py` — choose an explicit path outside `HOST_SCOPE` so the host-scope rejection test does not depend on `TMPDIR` placement.

No production implementation, Stable writer, Fast Lab writer, capability profile, or capability range changed in that correction.

### Independent remote/static identity review

ChatGPT independently confirmed after the local validation that:

- canonical `main` still points to `44c90e8217061cc8ac294a392984dfe73e622d80`;
- remote `codex/fl2-unified-cli` points to exact tested candidate `afcfb7219603b209b1e98b930f68b3ccaa18a832` before this documentation-only evidence update;
- the tested candidate is a linear descendant of the canonical base with no divergence;
- the FL2 core still delegates field derivation to the existing bounded modules and preserves exact-ROM/exact-save gates, preview-only behavior, separate-output publication, and post-write verifier checks.

This record update is documentation-only and does not alter the tested implementation or tests. The branch remains a candidate until separately reviewed and Human-authorized for merge.
