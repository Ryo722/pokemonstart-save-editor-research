# Independent review packet — v0.23+ read profile candidate

Reviewer instructions: verify from source and, where you hold private inputs,
from your own copies. Do not rely on the maker's conclusions. This packet asks
for a review of a **read-only** candidate; no write authority is requested.

## Identity

- Base: `main` `381bc80080919952c9a32bb7982dfcf24bc92ea5`.
- Branch: `research/v023plus-read-profile` (HEAD/tree in the handoff message).
- Files: `pokemonstart_save_layouts.py`, `pokemonstart_read_profiles.py`,
  `tests/test_v023plus_read_profile.py`,
  `docs/v023plus-read-profile-qualification.md`,
  `docs/v023plus-read-profile-evidence.json`, this packet.
- No canonical module, README, decision record or evidence index changed.

## Claims to check

1. **No write path.** Neither module opens a file for writing; tests assert
   this by source scan. Confirm independently.
2. **Legacy non-regression.** `parse_legacy` returns the canonical
   `verify_bytes` result unchanged; `V022_EXACT` constants equal the canonical
   party/inventory model constants; the canonical verifier still rejects
   v0.23+ saves. Run the full suite and compare with base.
3. **Unique family detection.** `detect` accepts only a single matching family.
   Look for inputs both parsers might accept, and check that every rejection reason is a fail-closed one.
4. **v0.23+ invariants** (qualification record table): slot validity,
   cyclic rotation, newest-of-two counter rule reused from the canonical
   verifier, SHEL magic/counter, table range/distinctness, page id/signature/
   checksum, page counter ≤ owning slot counter, inactive-slot validation.
   In particular check that **mixed page counters are accepted** and that
   nothing rejects the observed R1/R2 copy-on-write state.
5. **Exact v0.27 profile.** ROM size/SHA binding, header pointers `0x1BC` and
   `0x1C8`, eight table offsets reproducing the semantic-model hashes
   (items with pointer normalization). Parity rule is profile-only.
6. **Capability separation.** `write_mechanics` is `NOT QUALIFIED` for
   v0.27; Money/Inventory reads are qualified only for key 0.
7. **Wording.** Only exact v0.27 is called privately runtime-qualified; the
   v0.23+ family is called structurally supported by public/static evidence.

## Suggested reproduction

```bash
python3 -m unittest tests.test_v023plus_read_profile -v
python3 -m unittest discover -s tests -v          # compare with base 381bc80
# with private inputs (outside Git):
POKEMONSTART_V027_GATE_DIR=... POKEMONSTART_V027_ROM=... POKEMONSTART_V022_ROM=... \
  python3 -m unittest tests.test_v023plus_read_profile -v
```

Expected private hashes: S0 `b153720a…26b2`, M `f4df12cc…441c`,
R1 `325e355f…99d3`, R2 `68e18ae4…67e9`; v0.27 ROM `455f5294…81ac`;
v0.22 ROM `6abce6aa…dbb0`.

## Known limits (do not treat as defects of the candidate)

Spare-sector reuse policy, populated Box pages, three first-save parasite
bytes, native new-game SHEL state, v0.23–v0.26 runtime and every write
envelope are unresolved and intentionally not encoded. The private gate is a
single migrated save with empty Boxes. Eight NiceGUI/browser tests error in the
maker's sandbox on both base and candidate (local-port binding denied).

## Requested verdict

One of: `READ_PROFILE_CANDIDATE_ACCEPTABLE`, `CHANGES_REQUIRED`
(with concrete findings), or `REJECT`. Adoption remains a separate Human decision.
