# v0.23+ read profile: independent execution/reproduction gate and current-main reconciliation

Status: **independent execution evidence recorded; reconciliation candidate awaiting focused review.**
This record does not adopt the read profile canonically, does not authorize any
writer, Box writing, E5, version-wide v0.23–v0.26 runtime qualification,
release or Stable promotion.

## 1. Identities

| Role | Commit | Tree |
|---|---|---|
| Original exact base | `381bc80080919952c9a32bb7982dfcf24bc92ea5` | |
| Reviewed predecessor | `318ee7d97785fbb2de7eabe9ba3f5c3de2324f9d` | |
| Frozen corrected candidate | `fd338ac79c07b0782ec7e20b86338cbb27f1830e` | `0b9464187b8ec918fffef8f38486fc55cfaf9223` |
| Current canonical main at reconciliation | `5864e7ada132408d39df8cc3dc2b56a75805b24a` | |

Ancestry verified: `fd338ac -> 318ee7d -> 381bc80`, single parent each.

## 2. Execution/reproduction gate on the frozen candidate

Verdict: **`EXECUTION_REPRODUCTION_GATE_PASS`** for `fd338ac`.

Classification: fresh-context independent execution on public/synthetic inputs
only. **No private-input run** was made in this gate (the
`POKEMONSTART_V027_GATE_DIR` / `POKEMONSTART_V027_ROM` / `POKEMONSTART_V022_ROM`
variables were not set). It is not local private-input verification.

Environment: macOS, CPython 3.13.7, clean detached worktrees of each exact
commit, NiceGUI not installed, no repository dependency installed or changed.

### 2.1 Focused module at `fd338ac`

`PYTHONPATH=. python3 -m unittest tests.test_v023plus_read_profile -v`:
53 run, 49 pass, 0 fail, 0 error, 4 skip. All four skips are
`PrivateGateTests` with reason `private v0.27 gate saves / ROMs not provided`:
`test_both_builds_reproduce_the_semantic_model_and_catalog`,
`test_cross_build_binding_rejected`, `test_gate_sequence`,
`test_v022_delegation_rejects_single_slot_s0`.

### 2.2 Canonical v0.22 set, `381bc80` vs `fd338ac`

Modules (23): `test_fastlab_v022_{inventory_editor,money,party_editor,practical_party}`,
`test_v022_{composition,creation,inventory_editor,inventory_insertion,inventory_model,
inventory_native_deltas,macros,party_model,party_writer,product_acceptance,product_core,
product_inventory,product_money,product_party,product_web,readonly_probe,template_import,web}`,
`test_verifier`.

Both commits: 145 run, 138 ok, 1 error, 6 skip (NiceGUI unavailable).
Per-test outcomes identical.

### 2.3 Full suite, `381bc80` vs `fd338ac`

`PYTHONPATH=.:tests python3 -m unittest discover -s tests -p "test_*.py"`:

| | run | ok | error | fail | skip |
|---|---|---|---|---|---|
| `381bc80` | 285 | 262 | 1 | 0 | 22 |
| `fd338ac` | 338 | 311 | 1 | 0 | 26 |

All 285 base test IDs have identical outcomes at `fd338ac`; the only additions
are the 53 `test_v023plus_read_profile` tests (49 ok, 4 private skips).

The single error at both commits is the same environment-caused error:
`test_v022_party_writer.OrdinaryWorkflowTests.test_preview_stale_download_and_exclusive_separate_export`,
`FileNotFoundError` because the untracked `work/` directory does not exist in a
clean checkout.

The previously claimed "8 environment errors at both base and candidate" was
**not reproduced** in this environment; both exact base and candidate instead
had the same single environment error above. The equivalence conclusion is
unaffected.

### 2.4 Predecessor defects reproduced independently

A review-written script (not committed) ran the same scenarios against
`318ee7d` and `fd338ac`. Save images were synthesised with the predecessor's
synthetic layout fixture builders; the alternate-bag patches, erased-slot
image, synthetic ROM and synthetic semantic profile were written independently
for the review. No ROM or save bytes were used.

| Finding | `318ee7d` observed | `fd338ac` observed |
|---|---|---|
| F1 alternate bag (v0.23+ page 0 halfword `0x0203B672` = -1) | Inventory returned with 5 pockets; only flagged `alternate_bag_state: true` | `qualified: false`, `alternate runtime bag state unsupported` |
| F1 alternate bag (legacy section 13 `+0x6B6` = -1) | Inventory returned with 5 pockets | same fail-closed result via canonical `inventory_model.inspect` |
| F2 legacy save with slot 0 erased | Money `qualified: true`, Inventory returned, label `CANONICAL`; canonical `product_money.inspect` / `inventory_model.inspect` reject the same bytes | Money: `Money requires two valid save slots`; Inventory: `unsupported inventory save epoch`; label `DELEGATED TO CANONICAL v0.22 MODULES…` |
| F3 no ROM | CLI `--save` only and `--profile` only both rc 0 `ACCEPTED_READ_ONLY`; `read_save(V027_EXACT, save)` accepted | CLI exits 2 (`--rom`/`--save` required); `read_save` requires `rom`; wrong ROM raises `ProfileError` |
| m1 Party count 7 | `LayoutError` escapes `main` uncaught | `ProfileError` -> `REJECTED`, rc 2 |
| m2 fragment flags | single `epoch_authenticated` | separate `checksum_covered` / `epoch_bound` |

`ReviewFindingRegressionTests` (12 tests) pass at `fd338ac`.

### 2.5 No mutation

All exact worktrees were clean after every run; no commit, push or GitHub
change was made during the gate; no `.sav`, ROM, emulator binary or package
content is present in the `381bc80..fd338ac` diff.

## 3. Reconciliation onto current main

Branch `research/v023plus-read-profile-main-reconcile`, parent `5864e7a`.

### 3.1 Content equivalence

All six files are **byte-identical** (same blob IDs) to `fd338ac`:
`pokemonstart_read_profiles.py`, `pokemonstart_save_layouts.py`,
`tests/test_v023plus_read_profile.py`,
`docs/v023plus-read-profile-qualification.md`,
`docs/v023plus-read-profile-evidence.json`,
`docs/reviews/v023plus-read-profile-review-packet.md`.
No reconciliation edit was required. This record is the only added file.

### 3.2 Interaction with E4 / current main

`381bc80..5864e7a` (E4 creator work) touches none of the six files and none of
their imported modules: `pokemonstart_save_verifier.py`,
`pokemonstart_v022_product_money.py`, `pokemonstart_v022_inventory_model.py`,
`pokemonstart_v022_party_model.py` are byte-unchanged. The read profile does not
import any E4 module. No interaction found.

### 3.3 Current-main regression, `5864e7a` vs reconciled

Same environment and commands as section 2.

- Focused module at reconciled: 53 run, 49 ok, 4 private skips.
- Canonical v0.22 set (28 modules on current main, now including
  `test_v022_creation_{acceptance,initialization_probe,probe,web,writer}`):
  both 165 run, 157 ok, 1 error, 7 skip; per-test outcomes identical.
- Full suite: `5864e7a` 305 run (281 ok, 1 error, 23 skip); reconciled 358 run
  (330 ok, 1 error, 27 skip). All 305 main test IDs have identical outcomes,
  including all 25 E4 `test_v022_creation*` tests (24 ok, 1 skip at both); the
  additions are only the 53 focused tests. The single error is the same
  `work/`-directory environment error as in section 2.3.

No new failure or error; no canonical regression introduced.
