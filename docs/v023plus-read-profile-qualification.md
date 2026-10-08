# v0.23+ save-layout family and exact-v0.27 read profile — qualification candidate

Status: **CORRECTED CANDIDATE FOR FOCUSED RE-REVIEW — not canonical, not adopted.**
Correction 1 addresses the fresh independent review (`CHANGES_REQUIRED` on
`318ee7d`); see [Correction 1](#correction-1-independent-review-findings).
Read-only. This record grants **no write authority** of any kind, changes no
canonical v0.22 module, and does not alter the E-series goal, terminal
definition or milestone sequence. Adoption is separately Human-gated.

Sanitized data: [v023plus-read-profile-evidence.json](v023plus-read-profile-evidence.json).
Review packet: [reviews/v023plus-read-profile-review-packet.md](reviews/v023plus-read-profile-review-packet.md).
No ROM, save, package, migration payload, emulator binary, screenshot or
copyrighted table bytes are stored in Git.

## Base and authority

- `CANONICAL_PROJECT_EVIDENCE`: candidate base is remote `main`
  `381bc80080919952c9a32bb7982dfcf24bc92ea5`; no open Issues/PRs at
  reconstruction. E0–E3 complete/adopted; E4 next, not started on `main`.
- Authorization: bounded v0.23+ read-profile qualification candidate
  (investigation, read-profile architecture, tests, sanitized evidence,
  review preparation). Not authorized: any v0.23+ writer, page allocation
  logic, Box editing, E4 writer/GUI, release, Stable promotion, merge.
- Investigation inputs reconciled, not merged: `research/v027-64mib-recon`
  (`b706444`) and `research/v027-rom64-mgba-static-verification`
  (`92986bd`). Only material facts reproduced below are relied upon.

## Evidence labels

`CANONICAL_PROJECT_EVIDENCE`, `INDEPENDENTLY_REPRODUCED`,
`LOCAL_PRIVATE_INPUT_VERIFICATION`, `UPSTREAM_SOURCE_EVIDENCE`,
`HUMAN_OBSERVATION`, `HYPOTHESIS_UNVERIFIED`.

## Wording boundary

- **v0.23+ save-layout family: structurally supported by public/static evidence.**
- **Exact v0.27 read profile: privately runtime-qualified** (one gate).
- Not claimed: "v0.23–v0.27 fully supported", "v0.23+ writer supported",
  write mechanics for any build, Box semantics.

## Architecture

Three separate concepts, each explicit data rather than version conditionals:

| Concept | Where | Meaning |
|---|---|---|
| Save-layout family | `pokemonstart_save_layouts.py` (`LEGACY`, `V023PLUS`) | structure only; strict parser per family; unique-match detection |
| Semantic model | `pokemonstart_read_profiles.SemanticModel` (`CANONICAL_SEMANTIC_MODEL`) | build-independent table identity by content hash |
| Exact build read profile | `pokemonstart_read_profiles.V022_EXACT`, `V027_EXACT` | ROM size/SHA, per-build table offsets, header pointers, layout family, semantic model, field reader, capability levels, profile-only constraints |

Capability levels are never merged:

| Level | v0.22 exact | v0.27 exact |
|---|---|---|
| 1. layout understood for reading | canonical verifier, unchanged | privately runtime-qualified |
| 2. field location / semantic read | **delegated** to canonical modules: Party records from the canonical verifier, Money via `pokemonstart_v022_product_money.inspect`, Inventory via `pokemonstart_v022_inventory_model.inspect` (exact canonical eligibility) | only after exact v0.27 ROM verification: Party raw records; key0 Money 0..9,999,999; Inventory under an E1-equivalent boundary (below); semantic tables content-verified |
| 3. write mechanics | not granted by this profile (canonical v0.22 writers are separate) | **not qualified** |

Field reads exist only as `read_save(profile, save, rom)`. It first calls
`verify_rom` (size, SHA-256, header pointers, every semantic-table hash) and
returns no field at all if that fails; there is no save-only field API. The
CLI requires `--profile`, `--rom` and `--save`; every rejection, including
malformed Party/field states, is reported as `REJECTED` with exit code 2.

v0.27 Inventory boundary (mirrors canonical E1 `inspect`): key 0; if both
slots are valid their counters are consecutive; Party count 1..6; ordinary
bag only (RAM `0x0203B672` negative => unqualified); every entry has a
catalog-valid item id (E1 validity rules applied to the verified v0.27 item
table), matching pocket metadata, quantity 1..999 and no duplicate id. Any
failure returns `{"qualified": false, "reason": ...}` with no pocket
contents. The one structural difference from the legacy gate is that a
migrated state with one erased slot may qualify, because every v0.23+
fragment is read from the active slot or from pages its SHEL table
references (there are no global extra sectors).

`detect()` runs both strict family parsers and accepts only a unique match;
two matches or none fail closed. The legacy family delegates unchanged to
`pokemonstart_save_verifier.verify_bytes`; the canonical verifier still
rejects v0.23+ saves. Both families expose one read-only `SaveView`
(active slot, sections, Party, Money, RAM-fragment reads). Fragments carry two
separate flags. `checksum_covered`: inside a stored checksum's range.
`epoch_bound`: stored in a sector of the selected epoch (active slot section
or page referenced by the active SHEL table).

| Fragment | legacy (covered, bound) | v0.23+ (covered, bound) |
|---|---|---|
| section 0 tail `+0xF24` | False, True | False, True |
| section 4 tail `+0xD98` | False, True | False, True |
| `0x0203B40C` (Inventory regular pocket) | section 13 tail: False, True | page 0 `+0x18B`: True, True |
| `0x0203BFAC`, `0x0203CF9C` | sectors 30/31: False, False | pages 15/16: True, True |

The three unidentified first-native-save bytes lie in the section 0/4 tails,
which are epoch-bound but **not** checksum-covered.

## `v023plus_shel_pages` family — read invariants encoded

| Invariant | Rule | Evidence |
|---|---|---|
| File size | `0x20000`, or `0x20010` with an opaque 16-byte emulator footer | canonical verifier rule; S0/M/R1/R2 all `0x20010` |
| Slots | sectors 0–4 and 5–9; each erased or 5 signed sections ids 0–4, section checksum lengths unchanged; partial erasure rejected | migration tool; private gate |
| Placement | sections form a cyclic rotation inside the slot; duplicates/missing/permuted rejected | private gate: rotations 0 → 1 → 2 |
| Counters | one counter per slot; vanilla/CFRU newest-of-two rule reused from the canonical verifier; equal counters ambiguous; counters above `0x7FFFFFFE` (wrap) unqualified | canonical rule; private gate 11 → 12 → 13 |
| SHEL | each valid slot carries `SHEL` at SB1+0x1400 (section 2 +0x410); its counter equals the slot counter | private gate (M, R1, R2) |
| Page table | 17 bytes at SB1+0x1408; every entry in sectors 10–31; entries distinct | private gate; an all-`0xFF` (native new game) table is rejected as unqualified |
| Pages | page *p* at its table sector: signed, id `0x40+p`, checksum over `0xFF0`, counter ≤ owning slot counter | private gate |
| Page counters | record the last write; may be older than the slot/SHEL counter and mixed | private gate R1/R2: `{11, 12}` with slot 12/13 |
| Ownership | both valid slots' tables are fully validated; a page newer than the slot that references it, or a sector claimed by different pages across slots, is rejected | fail-closed design (defence in depth) |
| Fragments | SB2 tail (section 0 +0xF24), section 4 +0xD98, page 0 +0x18B, pages 15/16 | migration tool + ROM literals (recon) + private gate Inventory equality |

The exact-v0.27 profile additionally requires each valid slot's index to equal
`counter % 2` (observed native rule; the migration tool uses the same parity).
The family parser reports rotation/parity but does not require parity.

## Exact v0.27 read profile

- `INDEPENDENTLY_REPRODUCED`: upstream `23007d4` tree blob `359a097` =
  package SHA-256 `d81b965d…fe5a90` → BPS `64cadabd…6535` → private ROM
  re-derived with an independent BPS implementation:
  SHA-256 `455f5294af9cb728ea577cafea3f8a27d5efc18e8f1371e1a76492e79d3781ac`,
  67,108,864 bytes, CRC32 `84202DAB`.
- `LOCAL_PRIVATE_INPUT_VERIFICATION`: all eight semantic tables of the exact
  v0.22 E1/E3 model are present in v0.27 at new offsets with identical content:

| Table | v0.22 offset | v0.27 offset | Anchor |
|---|---|---|---|
| species (1489×32) | `0x19B8B40` | `0x17D8F74` | header pointer `0x1BC`; unique content match |
| species names | `0x16570A4` | `0x16570D4` | unique content match |
| moves (998×12) | `0x14A3238` | `0x141A840` | unique content match |
| move names | `0x111A74C` | `0x111D9A4` | unique content match |
| experience (6 curves) | `0x14C5D54` | `0x143D35C` | unique content match |
| nature modifiers | `0x20F550` | `0x20F550` | same address, same content |
| pocket descriptor | `0x1490E68` | `0x1408400` | unique content match (RAM bases/capacities identical) |
| items (839×40) | `0x15199C8` | `0x1490FD0` | header pointer `0x1C8`; equal after replacing the three ROM pointers per record by null/non-null flags |

  The v0.22 raw hashes equal those already recorded in canonical
  `e1-inventory-private-evidence.json` and `e3-existing-party-readonly-evidence.json`
  (`CANONICAL_PROJECT_EVIDENCE`); a unit test asserts this.
- Code-path equivalence (CreateMon/GetMonData/stat calculation closures) is
  **not reproduced here**; the recon branch's static claim remains
  `HYPOTHESIS_UNVERIFIED` for this candidate. Semantic tables being identical
  does not by itself qualify derived calculations or any writer.

## Legacy profile — regression safety

- No canonical module was modified. `V022_EXACT` mirrors canonical constants
  and a test asserts equality with `pokemonstart_v022_party_model` /
  `pokemonstart_v022_inventory_model`.
- Legacy `SaveView` *is* the canonical `VerificationResult`; Party equality,
  fragment offsets and menu counts (`0x1E716`) match the canonical Inventory
  `record_offset` mapping (synthetic test).
- v0.22 Money/Inventory field reads call the canonical modules directly, so
  their eligibility boundary is the canonical one (single slot, counter wrap,
  alternate bag, non-key0 and catalog issues all stay unqualified).
- Canonical v0.22 tests (`test_verifier`, `test_v022_inventory_model`,
  `test_v022_party_model`, `test_v022_product_money`,
  `test_v022_product_inventory`, `test_v022_product_core`,
  `test_v022_readonly_probe`, `test_fl2_core`, `test_m5a_money_family`):
  64 run, OK on both base `381bc80` and the corrected candidate.
- `LOCAL_PRIVATE_INPUT_VERIFICATION` on S0: delegated reads qualify; the
  catalog derived by `_catalog` equals canonical `extract_catalog` (v0.22) and
  the v0.27 catalog is identical; v0.22 ROM reproduces every semantic hash.

## Private gate (`S0 -> M -> R1 -> R2`)

`LOCAL_PRIVATE_INPUT_VERIFICATION` unless marked otherwise. Raw files remain
private and outside Git.

| Item | S0 | M | R1 | R2 |
|---|---|---|---|---|
| SHA-256 | `b153720a…26b2` | `f4df12cc…441c` | `325e355f…99d3` | `68e18ae4…67e9` |
| Layout | legacy | v0.23+ | v0.23+ | v0.23+ |
| Active slot / counter | 1 / 11 | 1 / 11 | 0 / 12 | 1 / 13 |
| Rotation (active) | — | 0 | 1 | 2 |
| SHEL counter | — | 11 | 12 | 13 |
| Page table | — | 10..26 | 27, 11..26 | 27, 11..26 |
| Page counters | — | {11} | {11, 12} | {11, 12} |
| Raw sectors written vs previous | — | (migration) | 0–4, 27 | 5–9 |

- S0: canonical E3 Human-returned save (`CANONICAL_PROJECT_EVIDENCE`,
  `docs/reviews/e3-existing-party-independent-review.md`); original unchanged.
- M: produced by executing the upstream migration HTML's inline script
  verbatim (HTML SHA-256 `141920a2…dfc`, decoded script `2211bb99…fbe3`) in a
  zero-permission Deno runtime. Only change outside relocation: SHEL written
  over SB1+0x1400..0x1419, which was all-zero in S0. All other section data,
  parasites, former sectors 30/31 (now pages 15/16), page-0 parasite and
  footer byte-identical.
- R1/R2: Human-performed ordinary in-game saves in exact v0.27 under the
  re-hashed `rom64` mGBA (`7a3abada…`/`69afb372…`) in an isolated Windows
  kit with re-verified inputs.
- `HUMAN_OBSERVATION`: migrated save loaded normally; no unexpected dialogs;
  Pokémon pictures displayed normally (upper-half rom64 content reached).
  Presence/absence of an overwrite confirmation was not specified.
- Party, key0 Money and all Inventory pockets/menu counts equal across
  S0/M/R1/R2 (profile read and unit test with private inputs).
- First native save normalisation (R1 only): object-event template script
  pointers reloaded (stride `0x18`, SB1 `0x8E0–0xEE0`; also changes on v0.22
  map reloads); default 9-byte box names written for boxes 2–15 in the page-0
  storage tail where migration left zeros; three parasite bytes (section 0
  tail, section 4 tail) with unidentified meaning. Per-save runtime changes:
  play time, SB1+0x1200 save stat (also per-save on v0.22), object-event
  state, SHEL counter, emulator footer.

## Static family evidence (v0.23–v0.27)

`INDEPENDENTLY_REPRODUCED`: packages v0.23–v0.27 match their upstream tree
blobs; each ROM re-derived from the owned source. v0.23–v0.27 all bundle the
byte-identical migration HTML `141920a2…dfc` and contain three aligned
`SHEL` literals; v0.22 (re-derived to canonical `6abce6aa…`) has neither.
This supports the family structurally; it is **not** runtime qualification
of v0.23–v0.26, and those builds receive no profile.

## Fail-closed coverage

`tests/test_v023plus_read_profile.py` (53 tests: 49 synthetic, 4
private-input tests skipped unless all three environment variables are set):

missing SHEL magic; SHEL/slot counter mismatch; duplicate logical section;
missing logical section; mixed slot counters; equal-counter ambiguity;
non-cyclic placement; partially erased slot; page-sector index out of range
(5, 9, 32, `0xFF`); uninitialised native table; duplicate page-sector mapping;
missing (erased) page; wrong page id; invalid page checksum; invalid page
signature; page newer than its slot; inactive slot's page overwritten after
it; sector shared by different pages across slots; counter wrap; unknown
layout; wrong size. Accepted: mixed page counters after copy-on-write;
migrated single-slot state; steady state with shared tables; footer absent.
Regression: legacy view equals canonical verifier result; canonical verifier
still rejects v0.23+; profile layout mismatch; native parity rule; nonzero key
leaves Money/Inventory unqualified; non-consecutive counters, catalog issues
(invalid id, pocket mismatch, quantity, duplicate) leave Inventory
unqualified; tampered semantic table rejected; no write path in either module.
Synthetic profiles use a synthetic ROM and semantic model, so exact-ROM
binding is exercised without protected data.

## Correction 1 (independent review findings)

Predecessor `318ee7d` (tree `54499f9f`). Each finding was reproduced against
the predecessor and is covered by `ReviewFindingRegressionTests`:

| Finding | Predecessor behaviour (reproduced) | Correction |
|---|---|---|
| F1 alternate bag | v0.23+ save with `0x0203B672 < 0` returned ordinary-bag pockets with `alternate_bag_state: true` | Inventory returns `qualified: false`, reason `alternate runtime bag state unsupported`, no pockets (v0.27 native gate; v0.22 via canonical `inspect`) |
| F2 v0.22 boundary | single-slot and wrapped-counter legacy saves returned Inventory under a `CANONICAL` label | v0.22 Money/Inventory delegated to canonical `product_money.inspect` / `inventory_model.inspect`; label is `DELEGATED TO CANONICAL v0.22 MODULES` |
| F3 ROM binding | `main(["--profile","v027"])` returned rc 0; `read_save` returned qualified Money from a save alone | `read_save(profile, save, rom)` requires `verify_rom`; CLI requires `--rom` and `--save`; structurally compatible saves cannot obtain the v0.27 label without the exact v0.27 ROM |
| m1 rejection surface | CLI raised an uncaught `LayoutError` for Party count 7 | all layout/field errors become `ProfileError` -> `REJECTED`, rc 2 |
| m2 fragment claims | section 0/4 tails reported `epoch_authenticated: true` | flags split into `checksum_covered` (tails `false`) and `epoch_bound` |

## Unresolved writer blockers (not encoded, not generalized)

1. Spare-sector selection and reuse when later page writes occur (only one
   relocation, to sector 27, observed; sectors 28–31 unused).
2. Populated Box-page rewrite behaviour (gate save has zero Box Pokémon).
3. Meaning of the three first-native-save parasite bytes.
4. Native new-game SHEL state (static: table `0xFF`) — rejected for reads.
5. Runtime qualification of v0.23–v0.26.
6. Any write envelope: section/page checksum rewrite, rotation advance,
   copy-on-write placement, emulator acceptance. Inventory lives partly in
   page 0 and pages 15/16, so Inventory writes depend on (1).
7. ROM code-path equivalence for derived calculations (static recon claim not reproduced).

## E4 decision surface (assessment only)

- Profile-neutral E4-A semantic research remains valid: the semantic tables
  are content-identical v0.22 ↔ v0.27; Party record layout and SaveBlock
  offsets read identically.
- Retargeting eventual E4 implementation to exact v0.27 is technically
  supportable for Party-only creation once a v0.23+ write envelope is
  qualified (Party lives in slot sections, not pages); it remains a Human
  decision that depends on which build the owner plays.
- Exact-v0.22 E4 writer work: recommend keeping it frozen pending that
  decision. No canonical sequencing change is made here.

## Reproduction

```bash
python3 -m unittest tests.test_v023plus_read_profile -v
POKEMONSTART_V027_GATE_DIR=/private/gate POKEMONSTART_V027_ROM=/private/v027.gba \
POKEMONSTART_V022_ROM=/private/v022.gba python3 -m unittest tests.test_v023plus_read_profile -v
python3 pokemonstart_read_profiles.py --profile v027 --rom /private/v027.gba --save /private/save.sav
PYTHONPATH=.:tests python3 -m unittest discover -s tests -p "test_*.py"
```
