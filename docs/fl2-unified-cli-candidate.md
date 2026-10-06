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

- `pokemonstart_fl2_core.py`
- `pokemonstart_fl2_cli.py`
- `tests/test_fl2_core.py`
- `tests/test_fl2_cli.py`

## Verification status

The four new Python files compile successfully with `py_compile` in the ChatGPT execution environment. Full repository/focused test execution still requires a repository-capable local runner before merge review; this candidate must not be adopted solely from syntax/static review.

Before any FL2 merge/adoption, the stale post-G0 wording in `README.md` / `docs/decision-record.md` must also be synchronized so canonical state says FL2-G0 is complete and FL2 is the active milestone.
