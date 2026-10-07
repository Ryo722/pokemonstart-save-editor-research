# v0.22 practical product candidate

Canonical base: `7e7435c5507abfec183c3b370dcb1fa381b22186` (fresh origin/main).
Candidate: `codex/v022-practical-product-sprint`. Initial working tree: clean.
Local main fast-forwarded to the canonical base; implementation occurs only on candidate.

Existing tests include Fast Lab Money/Party/Inventory, FL2, creation/composition,
NiceGUI delivery, verifier and earlier Stable tools. Existing APIs retain their
original gates. New product APIs are candidate-only and do not promote Stable support.

Protected boundary: ROM/save/package/patch/executable/game assets remain outside
Git. Private root is PokemonStart-private; only read inputs, immutable in-memory
outputs, and separate verified downloads are used. No emulator save replacement.

Frozen Money branch inspected as non-canonical reference. Reused conservative
key0/two-valid-slot/consecutive-counter ideas after reconciliation; no merge or
cherry-pick. Its fixed target is not a practical requirement. Nonzero keys remain
unsupported: existing exact-v0.22 evidence does not independently qualify them.
Open PR #3 is historical M2 work and does not affect this sprint; no open issues.

## Disposition

**BOUNDED_STOP_WITH_CONCRETE_EVIDENCE.** A usable bounded product candidate and
all automated acceptance tooling exist, but R2C terminal Inventory insertion /
removal and general pocket capacity are not qualified. R4 actual Human two-cycle
gameplay acceptance has not occurred. This is not terminal sprint completion.

Implementation head before evidence-only documentation: `53b6282` (resolve the
full immutable SHA from Git). The final review HEAD is recorded by the final
post-commit local receipt and handoff; no self-referential commit SHA is embedded
in its own committed document.

## Candidate support predicates

- All families: supplied exact v0.22 ROM hash must equal the canonical schema1
  profile; the GUI re-reads that ROM each preview/generation/download. Repository
  verifier must select a unique active slot. No output filesystem writer exists
  in the product GUI.
- Money: two valid slots, ordinary non-wrap counters `0..0x7FFFFFFE`, parity and
  consecutive counters, key0 in both slots, both decoded balances `0..9,999,999`.
  Target is an integer in that range. No-op rejected. Only four Money bytes plus
  required section1 checksum bytes can change; every other byte is preserved.
- Party: existing occupied slots 0..count-1 (up to six), sanity2, backup species0,
  non-egg packed bit, nonzero species, level1..100 and coherent HP bounds.
  Friendship0..255 is independent of the stat-model gate. Move1 permits
  Pound/Tackle with original slot1 already one of those moves, zero PP-Up word
  and PP≤35; replacement restores PP35 and preserves every other move slot.
- Derived Party fields: Bulbasaur/Ivysaur, level5/6, unminted Serious (12) or
  Modest (15), no hyper-training, ability selector0, held item0, source-calculated
  cache agreement, EXP-derived starting level agreement. Targets: species1/2,
  level5/6 or EXP135..235, IV0..31, EV0..252 with total≤510. Requested level and
  EXP must agree. Max-HP decrease is rejected; nonzero HP receives the max-HP
  delta, fainted HP stays0. No automatic learnset, evolution, ability, Pokédex or
  story changes. Other fields remain read-only.
- Items quantity: active key0; section13 observed prefix Potion ID13 x1..3,
  preserved ID533 x1, optional Antidote ID14 x1, followed by zero section13 tail.
  Only Potion quantity1..3 is reusable. ID533 and Antidote are read-only.
  This is a three-record observation window, **not** a pocket capacity claim.
- Antidote insertion remains the canonical exact proof-root operation through
  its existing independent SHA + structure gate. It is not reusable on naturally
  progressed saves. The product can compose it with independent Money/Party
  requests only when that original exact-root gate passes.
- All composed operations qualify independently against the immutable original;
  patch conflicts fail closed, shared checksums are calculated once, and all
  semantic postconditions are rechecked after composition. Preview receipts,
  source bytes, ROM identity, controls and verified downloads are checked for
  stale/corrupt state.

## Source discrepancy and evidence classes

Fresh read of pinned CFRU-JP
[`src/build_pokemon.c`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/build_pokemon.c)
shows `CALC_STAT` uses `+5` for non-HP stats. Legacy Fast Lab code uses `+level`.
The new candidate calculator uses `+5`, preserves the legacy experimental APIs,
and rejects a cache that disagrees with the source model. Serious/Modest level5
baseline checks and level6 source arithmetic are tested. A current private
Serious Bulbasaur matches the source model and qualifies for bounded derived
edits. Newly calculated target stats have **not** received new v0.22 normal-SAVE
proof; legacy exact-byte load evidence is not evidence of correct stat
recalculation. This discrepancy requires explicit fresh-context review.

Canonical evidence: exact ROM identity, save representation, old bounded live
experiments and normal-save creation proofs. Upstream source: pinned formulas
and schemas, not a claim that the complete pinned source is this exact game's
integration revision. Candidate behavior: wider numeric friendship/IV/EV/Money
requests under the listed predicates. Local private evidence: in-memory writer,
NiceGUI simulation, actual Chromium, independent basic three-family audit,
verifier acceptance and source immutability. No new game lifecycle evidence.

Private input is the prior canonical normal-SAVE return, SHA
`274dece5fd8828710d2fccf470e4e2cf47cac6998ef306f114727f5d3565ec24`,
active slot0/counter6. It is a non-canary input for the previous reusable writers,
not a newly played save acquired during this sprint. It is accepted without a
Money/Party/Potion SHA allowlist. The new composed output SHA is
`373cde959c3550d13cc01e5bace0e0446d372b589da48bde5f4b7b23caac5206`.
The independent auditor reconstructs the full output and confirms exactly seven
changed offsets and every unrelated byte preserved. NiceGUI and Chromium output
match those bytes; original ROM/save hashes remain unchanged. See the sanitized
[candidate evidence](v022-product-candidate-evidence.json).

## Inventory / Give All Items blocker

The exact pinned PokemonStart repository tree contains README and the PKS
payload, not the custom bag implementation. Canonical evidence explicitly leaves
capacity unestablished. A 450-entry RAM scan is not a proven save mapping or
capacity. The three saved rows do not establish absence of a duplicate elsewhere
in an uncharacterized pocket. Generalized insertion was consequently closed;
canonical exact-root insertion remains available. Removal/compaction/reordering
have no exact-v0.22 game differential. No removal writer or Give All feature is
exposed. New pockets/key/event items remain unsupported.

Cheapest next evidence: use only a disposable exact-v0.22 save, confirm the full
regular-items listing, preserve an immediately pre-removal SAVE, remove the last
ordinary Antidote through the game's normal menu, SAVE and preserve the return.
Independently map all relevant tail regions and compare insertion/deletion/order.
Full capacity and a safe item classification/catalog require exact-build source
or independently checked ROM layout/function evidence. Do not equate observing
three valid slots with proving 450 saved slots or every item ID.

## Validation

- Product focused tests: 19 PASS in NiceGUI environment, including actual UI
  controls -> composed preview -> verified download and stale-control rejection.
- `python3 -m unittest discover -s tests -v`: 221 run, 203 passed, 18 optional
  environment skips, no failures.
- `.venv/bin/python -m unittest discover -s tests -v`: 221 run, 206 passed,
  15 existing environment-gated skips, no failures.
- Actual private NiceGUI and Chromium (153.0.8010.12): three-family basic recipe
  PASS; complete core/download equality and source/ROM immutability.
- Independent stdlib basic-recipe auditor: complete candidate equality, seven
  changed offsets, all unrelated bytes preserved. It intentionally does not
  audit stat-changing requests or certify gameplay.
- Python compilation/imports, all tracked JSON parsing, diff whitespace,
  protected artifact/path scan and redacted Gitleaks scans are recorded in the
  evidence JSON. No protected payload is included in Git.

## Human two-cycle handoff

The exact private bundle location is in the local handoff (not published bytes).
It includes immutable `cycle1_input.sav`, immutable disposable `cycle1.gba`,
new writable `cycle1.sav` containing the GUI-verified candidate, and
`cycle1-receipt.json`. All were created at new paths, never by replacing an
emulator live save. Preserve the verified export as an immutable reference.

```bash
.venv/bin/python pokemonstart_v022_product_web.py --rom /path/inside/PokemonStart-private/acceptance/cycle1.gba
```

Open `http://127.0.0.1:8766`, upload `cycle1_input.sav`, set Money1,234,567,
Party#1 Friendship180, Potion quantity3. Preview, generate and download a separate
verified save. Expected output SHA is the one above; normal controls do not ask
for it. The prepared `cycle1.sav` already contains the same complete bytes from
the actual GUI smoke, and can be used with `cycle1.gba` in mGBA.

1. Load disposable `cycle1.gba`, confirm the three edited values and perform one
   normal in-game SAVE. Close/flush mGBA, preserve this first returned save, and
   report what was observed. The agent can preserve/audit the file locally.
2. Continue ordinary gameplay on that disposable game, SAVE again, close/flush,
   and preserve the newly changed save separately. Never overwrite the immutable
   source snapshot or export reference.
3. The agent runs `check-return` and `check-progress`, then prepares cycle2 using
   that new save. Open it in the same GUI, use Money7,654,321, Party#1 Friendship181,
   and Potion2 (the harness adjusts a no-op if necessary), preview/export, then
   load a new disposable ROM/save pair and perform normal SAVE. Preserve return.

Read-only harness commands (receipt/output redirection is sanitized JSON only):

```bash
python3 pokemonstart_v022_product_acceptance.py --rom /private/path/cycle1.gba prepare /private/path/cycle1_input.sav --cycle 1
python3 pokemonstart_v022_product_acceptance.py --rom /private/path/cycle1.gba check-return /private/path/cycle1_input.sav /private/path/first-return.sav /private/path/cycle1-receipt.json
python3 pokemonstart_v022_product_acceptance.py --rom /private/path/cycle1.gba check-progress /private/path/first-return.sav /private/path/progressed.sav
```

The actual paths must remain inside PokemonStart-private. Metadata alone is never
Human gameplay proof. Synthetic two-cycle tests always retain `r4_complete=false`.
R4 is not closed until actual observed Human actions and returned-save audits
are recorded; broader Inventory completion remains a separate outstanding gap.

## Commit / adoption boundary

Coherent implementation commits:
`d69b68e` R1 foundation; `4cfa5d4` practical Money; `6f5c851` Party;
`05d7215` bounded Inventory; `5d49646` GUI/composition;
`fa1288e` source-correct candidate stats; `c4d3109` R4 harness;
`53b6282` retain canonical insertion gate. Final documentation follows these.
No merge, push, public release or Stable promotion was performed. Local main and
origin/main remain at the initial canonical base. Fresh-context independent
review and explicit Human merge/adoption authorization remain required.
