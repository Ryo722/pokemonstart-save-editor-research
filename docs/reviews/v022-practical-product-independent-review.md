# Fresh-context independent review packet: exact-v0.22 product candidate

## Review target

- Canonical base: `main` at `7e7435c5507abfec183c3b370dcb1fa381b22186`.
- Candidate branch: `codex/v022-practical-product-sprint`.
- Exact implementation candidate HEAD to review: `7b84f7f940ea110f9839baa6fe14550a4f08e0bb`.
- Candidate tree at that HEAD: `62ec5ccd7fe7000d25055833a3e17a92251d0e62`.
- The review packet is committed immediately after that implementation HEAD as documentation. Review the branch HEAD supplied with the review-start prompt, and confirm it descends from this target. The packet commit adds no product code.

The implementation has **not** been independently reviewed in the maker context.
This packet is a claim/evidence index, not a review conclusion or merge request.

## Scope and authority

Review the bounded local experimental editor for the exact PokemonStart v0.22
profile: reusable Money, existing Party editing, observed regular-item editing,
localhost GUI, fail-closed eligibility, and the two-cycle owner workflow.

The controlling authorization is:

`AUTHORIZE V0.22 PRACTICAL PRODUCT SPRINT REALIGNMENT AND BOUNDED R1-R4 IMPLEMENTATION`

It authorizes candidate implementation, testing, private local verification,
sanitized evidence, commits and candidate-branch push. It does not authorize
merge to `main`, public release, Stable-Lane promotion, another PokemonStart
version, generic CFRU editing, Box/Pokédex/story/quest/event/RTC editing,
arbitrary Pokémon synthesis, unproven item behavior, or public/LAN GUI access.
The review may recommend only within that boundary. It must not merge, publish,
or treat review as Human adoption approval.

## Start from fresh state

Fetch GitHub `main` and the candidate branch, verify the SHAs above, and read
the canonical `docs/decision-record.md` and
`docs/v022-practical-product-sprint.md` from the exact base. Review the full
candidate diff against `7e7435c5507abfec183c3b370dcb1fa381b22186`.

Primary candidate evidence:

- `docs/v022-product-candidate.md`
- `docs/v022-product-candidate-evidence.json`
- `docs/v022-product-sprint-completion-evidence.json`
- `docs/v022-native-inventory-and-template-import-evidence-20261007.md`
- `docs/evidence.md` candidate refresh section

Relevant implementation:

- `pokemonstart_v022_product_core.py` — immutable composed transaction and semantic receipt.
- `pokemonstart_v022_product_money.py` — exact-profile, key0, two-slot reusable Money predicate/writer.
- `pokemonstart_v022_product_party.py` — existing-member capability predicates, bounded field writers and coupled state checks.
- `pokemonstart_v022_product_stats.py` — candidate `+5` non-HP stat calculator.
- `pokemonstart_v022_product_inventory.py` — observed regular-item prefix, Potion quantity and shape-gated Antidote insertion/removal.
- `pokemonstart_v022_product_template_import.py` — one exact game-generated Rattata record import proof.
- `pokemonstart_v022_product_acceptance.py` — structural return/progress harness; deliberately cannot attest Human gameplay.
- `pokemonstart_v022_product_web.py` — local GUI workflow and verified separate download.
- `pokemonstart_v022_product_audit.py`, `pokemonstart_v022_creation_audit.py` — independent byte-envelope audits.

Relevant tests:

- `tests/test_v022_product_money.py`
- `tests/test_v022_product_party.py`
- `tests/test_v022_product_inventory.py`
- `tests/test_v022_inventory_native_deltas.py`
- `tests/test_v022_product_core.py`
- `tests/test_v022_product_web.py`
- `tests/test_v022_product_acceptance.py`
- `tests/test_v022_template_import.py`
- `tests/v022_product_browser_smoke.py`

## Evidence summary and classifications

Keep these classes distinct in the review:

1. **Canonical evidence:** facts already adopted on `main`; use only the exact base records for this class.
2. **Candidate implementation evidence:** source/tests on the candidate, not canonical adoption.
3. **Local private-input verification:** re-hashed private saves/ROM, repository verifier and independent byte construction; protected bytes stay outside Git.
4. **Human gameplay attestation:** actual visual game display, play actions, normal SAVE and emulator close/flush, recorded in the local session notes. Hashes/counters do not prove these actions.
5. **Upstream source evidence:** pinned CFRU-JP commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`, especially `src/build_pokemon.c`; it is not established as the exact integration revision of the patched game.
6. **Hypothesis/unverified:** explicitly listed below; do not promote into proof.

### R4: two GUI/game cycles

- Cycle 1 input SHA: `274dece5fd8828710d2fccf470e4e2cf47cac6998ef306f114727f5d3565ec24`.
- Cycle 1 verified GUI export SHA: `373cde959c3550d13cc01e5bace0e0446d372b589da48bde5f4b7b23caac5206`.
- Cycle 1 returned normal-save SHA: `6f96f92f2d9761059d2e97fccc649d8316d2784820e1d8a200d337d39fd2a492`; counter `6 -> 7`.
- Human observed exact-v0.22 load, Money 1,234,567, Friendship 180, Potion x3 and normal SAVE.
- Subsequent ordinary Inventory deletion and Antidote repurchase were normally saved. Progressed SHA `935f7bd8061f43569316239c2ab1bfcb7573fbc84601dffc823e0493bba38985`; counter `7 -> 9`; it qualified for another transaction.
- Cycle 2 verified GUI export SHA: `a1584f2f5cb783f74d5d2638725ac9ce36a7554434190f9a8a69effbe6ae2387`.
- Cycle 2 returned SHA: `606af61f976b0634d6eaf11e58bf3b9693345120e34b6d998631e068ca77d9ea`; counter `9 -> 10`.
- Human observed exact-v0.22 load, Money 7,654,321, Potion x2, normal Party and normal SAVE. After mGBA fully exited, live disposable save and frozen snapshot hashes matched.
- The structural harness reports `STRUCTURAL_ROUNDTRIP_PASS_HUMAN_GAMEPLAY_ATTESTATION_REQUIRED` and `r4_complete: false` by design. Evaluate the separate Human attestation as well; do not treat either source alone as the complete evidence.

### Inventory

Reproduced regular-item records at section13 offset `0xADC`:

- pre-delete: `(13,3),(533,1),(14,1),(0,0)`, counter 7;
- post-delete: `(13,3),(533,1),(0,0),(0,0)`, counter 8;
- post-repurchase: `(13,3),(533,1),(14,1),(0,0)`, counter 9.

The slot2 Antidote record was zeroed in place and reused; section13 checksum
does not cover this region. No later occupied slot, capacity, general
compaction/reordering, other item, other pocket or full bag mapping is proven.
Candidate UI/API reuse only allows Potion x1..3 and Antidote x1 insertion/removal
for the exact observed Potion x3 / item #533 x1 / slot2 / zero-tail shape.
Review whether the proof is sufficient for this narrow reusable predicate and
whether the absence of a GUI-created Antidote game round trip blocks terminal
acceptance.

### Rattata exact-record import

- Native pre-acquisition source SHA: `935f7bd8061f43569316239c2ab1bfcb7573fbc84601dffc823e0493bba38985`.
- Exact game-generated record SHA: `74d64c9dfbf4905bb0ca2abd7047d9834cb5b3bc8822cf95d538bba80da673f3`.
- Candidate SHA: `3b31b0e89c8907c61f81af836c117de7fc1a0cfd77662a218c492de0192ab96c`.
- Independent construction equality; Party count `4 -> 5`; 47 changed bytes limited to count, copied 100-byte record and checksum.
- Returned normal-save SHA: `256bf24dd9d3c2d6601d5203f56ff8b2f9ef4d59c5d8114f684e81be69dccdbe`, verifier accepted, counter 10, Party count 5.
- Human observed summary/moves, healing, battle action/completion and normal SAVE.
- Disposition is **GAME-ACCEPTED / NORMAL-SAVE-ACCEPTED** for this one complete game-generated record only. It is not arbitrary Pokémon synthesis and is not a general GUI feature.

The private snapshots remain under the host's `PokemonStart-private` local
acceptance evidence area (the 2026-10-07 `evidence-harvest` set and separate
template-import return). The filenames and hashes are in the sanitized
candidate evidence files above. A reviewer with the authorized host access can
re-read them; never copy them into the repository or upload them.

## Terminal acceptance matrix

The maker disposition is that all 14 exact-v0.22 terminal characteristics in
the canonical decision record pass, with bounded scope. The criterion-by-
criterion table is in `docs/v022-product-sprint-completion-evidence.json`.
Independently challenge at least:

- whether the current Party surface is actually useful to an owner, given broad Friendship, restricted Move 1, very narrow calculated stats and no generic constructor;
- whether Potion x1..3 plus the observed Antidote x1 state is a useful regular-item subset or still only a canary;
- whether exact-save SHA is fully absent from each reusable predicate that is claimed reusable;
- whether source immutability, checksum envelopes, composition conflict handling and stale GUI state rejection are sound;
- whether normal-save/counter evidence plus separately documented Human observations really closes R4;
- whether the calculator's source revision uncertainty or missing new stat-changing game round trip is terminal or post-terminal qualification only.

The source-backed stat discrepancy is explicitly bounded: legacy code used
`+level`; pinned source uses `+5`. The candidate calculator uses `+5` and
rejects source-cache disagreement. No fresh normal-save round trip of a
stat-changing candidate output exists. The R4 edit changed Friendship, so did
not exercise that calculator. Decide independently whether this is a terminal
blocker under canonical wording.

## Verification record

At this candidate implementation HEAD:

- `python3 -m unittest discover -s tests -v`: 226 run, 208 passed, 18 skipped, 0 failures.
- `.venv/bin/python -m unittest discover -s tests -v`: 226 run, 211 passed, 15 skipped, 0 failures; NiceGUI simulation exercised GUI Antidote add and remove previews/downloads.
- `python3 -m compileall -q .`: PASS.
- Candidate JSON parse and `git diff --check`: PASS.
- Gitleaks history scan: 204 commits, 0 leaks. Candidate changed-file scan: 0 leaks.
- The no-git whole-worktree scan found 3 generic-key false positives only in ignored bundled Chromium/Playwright files under `work/`; none are in candidate diff. Candidate path scan found no protected artifact suffix or absolute private-root path.
- Real Chromium smoke could not run in the current `.venv` because Playwright is not installed. Earlier actual Chromium evidence exists for the previous three-family workflow; current NiceGUI simulation covers the newly added Antidote controls.
- No `.sav`, ROM, patch, executable, raw protected bytes or copyrighted assets are in the candidate diff.

## Permitted review dispositions

- `PASS_FOR_HUMAN_ADOPTION_DECISION` — evidence and scope satisfy the canonical terminal goal; this is only a recommendation to the Human.
- `CHANGES_REQUESTED` — list exact files/criteria and the smallest bounded corrections; do not expand authorization.
- `BOUNDED_STOP_WITH_CONCRETE_TERMINAL_BLOCKER` — identify the exact unmet canonical criterion, current evidence, cheapest missing proof/work, and whether Human gameplay is required.

Do not execute another game procedure, expand item/species scope, merge, release,
promote Stable, or change canonical `main` as part of this review.
