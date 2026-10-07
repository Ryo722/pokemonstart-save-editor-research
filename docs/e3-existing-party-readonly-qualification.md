# E3 exact-v0.22 existing-Party read-only qualification candidate

Date: 2026-10-07. Fresh GitHub canonical base:
`3382de6b4be852b046cf484aee20bae6de3ae7c0`.
Candidate branch: `codex/e3-v022-existing-party-model`.
Disposition: **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE** at the read-only qualification boundary.
E3 implementation/acceptance is not complete. No expanded writer or GUI is delivered by this packet.

The remote was fetched before work; open Issues and PRs were both empty.
README, decision record, evidence ledger, expansion/readiness contracts,
native Inventory/template-import evidence, Party/verifier/product core/GUI
and their tests were freshly examined. E1/E2 is adopted for the restricted
recovery-medicine scope. Money is maintenance-only. E3 authorizes candidate
research, implementation, tests and private verification; merging, E4 creation,
Stable promotion, release and other versions remain outside this work.

## Evidence and implementation

- `pokemonstart_v022_party_model.py`: reusable production read-only model,
  exact-ROM gate, in-memory table/name extraction, complete requested major-field
  inspection and capability-specific reasons. No writer imports or output-save path.
- `pokemonstart_v022_party_audit.py`: independent record reconstruction using
  the separate section validator, direct byte reads, forward EXP threshold walk
  and arithmetic nature reconstruction. Imports neither production Party model,
  Party writer nor repository verifier.
- `pokemonstart_v022_party_qualification.py`: private read-only CLI, cross-check
  of both paths, before/after input identity checks and sanitized output.
- `pokemonstart_v022_party_static_probe.py`: isolated exact ROM execution,
  independently computed predictions, instruction-budget checks and explicit
  external-context interception. Does not modify a disk ROM/save.
- [Sanitized retained evidence](e3-existing-party-readonly-evidence.json): nine
  snapshots, 38 occupied-record observations, eight distinct record states,
  four species, counters 9–15. Repeated copies/imports are not independent
  natural specimens. Acquisition provenance is established for Rattata;
  the other materially different records were already present in retained
  game saves, not newly captured during this work.

No private paths, PID/OT/nickname data, raw records/hexdumps, copyrighted tables,
ROM/save bytes or extracted instructions are included in this packet.
Names and table contents are derived locally in memory; only table hashes are recorded.

## Cheapest discriminator: native Lv3 Rattata

The fresh post-acquisition save hash is
`c129892cd442fba6becd32db6dcb3061c9f8df9ea3d4550f53dff106b9abfbee`.
Its slot 5 record matches canonical SHA-256
`74d64c9dfbf4905bb0ca2abd7047d9834cb5b3bc8822cf95d538bba80da673f3`.

Fresh decoded state:

- species 19; stored level 3; EXP 27; ROM-derived level 3;
- moves 33/39/0/0, PP 35/28/0/0, PP-Up counts 0/0/0/0;
- friendship 50; held item 0;
- IVs HP/Atk/Def/Spe/SpA/SpD = 30/30/9/18/31/27; EVs all zero;
- native/effective nature 9 (Lax); mint 0; hyper-training 0;
- ability selector 0; hidden ability false; resolved ability ID 50;
- cached current/max HP 3/15; Atk/Def/Spe/SpA/SpD = 9/7/9/7/6.

| Candidate rule | Non-HP predictions | Comparison |
| --- | --- | --- |
| `floor((2*base+IV+floor(EV/4))*level/100)+5`, then nature | 9/7/9/7/6 | PASS, all five |
| legacy `+level`, then nature | 7/5/7/5/4 | FAIL, all five |

Lv5 records alone cannot distinguish these constants. Fresh exact-ROM
recalculation also leaves each retained 100-byte record unchanged for
Bulbasaur (1), Zigzagoon (288), Pikachu (25) and Rattata (19).
Pikachu adds nonzero EVs, a non-neutral nature and held item 202 to the comparison.

## Exact ROM corroboration

Every production extraction/probe requires SHA-256
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
All following addresses are observations of that owned exact ROM, not upstream constants promoted by assumption.

| Surface | Exact route | Qualified observation |
| --- | --- | --- |
| species/base stats/growth/abilities | pointer `0x080001BC` → `0x099B8B40`, stride 32 | local bounded extraction through ID 1488; six bases, growth byte, three u16 abilities |
| EXP | `GetLevelFromMonExp` at `0x0803DF30` → `0x094C5D54`, growth stride 1024 | direct 101-entry thresholds per growth index; no polynomial substitution |
| species names | `GetSpeciesName` → `0x096570A4`, stride 8 | decoded locally; unknown characters/placeholders stay unresolved |
| moves/base PP | exact PP routine → `0x094A3238`, stride 12 | bounded IDs 1–997; PP byte at +4 |
| move names | `0x0911A74C`, stride 16 | local decoding corroborates occupied moves; failed decoding is explicit |
| nature | `ModifyStatByNature` → `0x0820F550` | 25×5 signed modifiers; integer truncation after multiplication |
| stat routine | `0x0803DBE8` hook → `0x090756F4` | ordinary branch adds 5, derives stored level from EXP, uses mint−1 when nonzero |
| ability routine | `0x0804042C` hook → `0x09076560` | hidden bit = record byte71 bit4; selector = IV word bit31; zero HA/ability2 falls back to ability1 |
| PP-Up | `0x0804070C` → `0x090B68E8` | two bits per slot; `base+floor(base*ups/5)`; move996 ignores bonuses |
| held item | existing exact catalog at `0x095199C8`, stride40 | numeric ID/pocket/importance/type/effect/parameter; metadata validity is not safe-grant authority |

The exact Medium Slow table contains levels 1–7 thresholds
`1,9,57,96,134,179,236`. Therefore the old EXP134/stored-Lv5 value
happens to agree with this exact table. Its v0.15 lineage did **not** establish
that result; the new ROM read independently establishes it. The legacy
polynomial returns 135 at Lv5 and must not control an E3 generalized writer.
No existing historical writer behavior was changed in this candidate.

Isolated exact execution passed:

- all five retained records unchanged after recalculation;
- 300 parameter combinations spanning levels 3/6/20/50/100, six mint settings
  and two IV/EV allocations (includes one repeated-species record);
- selector/hidden combinations on all five records, including absent ability2 fallback;
- 15,952 move/slot/PP-Up combinations covering IDs 1–997, four slots and counts 0–3.

Only `FlagGet(0x930)` was intercepted as false to select the ordinary
non-facility branch. The actual source save's complete runtime/battle-context
reconstruction was not established. Synthetic in-memory parameter variants
are not game-native specimens or normal-SAVE acceptance. Unicorn required
host JIT permission; the sandbox attempt exited 132, and the authorized host
execution completed. No game executable or emulator was launched.

Pinned CFRU-JP `e24a16fe39e27ae162faf5b78596d1f3df18489d` was fetched only as
supporting layout/navigation evidence. Its source is not the exact integrated
revision; package metadata `git 4283b3a1` was not resolved and confers no authority.

## E3 coupling matrix

Statuses refer to read-only ordinary-model qualification at this boundary,
not broad write/gameplay acceptance. All expanded writer gates remain CLOSED.

| Adopted field | Status | Evidence / remaining boundary |
| --- | --- | --- |
| species | PASS | exact metadata and four species reconstructed; full ordinary/form inclusion policy not established |
| level / EXP | PASS | exact thresholds and isolated cross-level recalculation; historical polynomial FAIL as ROM authority |
| moves 1–4 | PASS | complete stored IDs and PP reconstructed, exact move metadata/names available locally |
| PP | FAIL | two Bulbasaur records retain PP35 in empty move slots; strict empty-slot PP=0 predicate fails; preservation/replacement policy needs explicit treatment |
| PP-Up | PASS | packed counts and all isolated maxima match, including move996 exception; no native nonzero-PP-Up transition acceptance |
| friendship | PASS | direct stored field, retained records and existing canonical separate write predicate |
| IV | PASS | six packed values and isolated arithmetic; hyper-training remains unqualified |
| EV | PASS | direct bytes, total/range validation, materially different Pikachu allocation and isolated tests |
| effective nature | PASS | native vs mint distinguished; exact modifiers/mint arithmetic cross-checked; native mint-change acceptance pending |
| ability | PASS | exact ordinary resolution and selector/hidden fallbacks; special species override path explicitly rejected |
| held item | NOT ESTABLISHED | existing metadata resolves ID202/effect45; broad safe held-item target/grant policy and form/stat coupling not qualified |
| cached stats / current HP | PASS | ordinary retained caches, damaged Rattata HP and isolated increasing-max/full-HP cases; decreasing-max HP policy/context pending |
| forms / exceptional states | NOT ESTABLISHED | exact branches identified, but complete reusable exclusion/context predicates not yet established |

## Concrete writer-gate blockers and next work

1. **Runtime context:** exact stat code includes Average Mons, 350 Cup and
   Scalemons branches guarded by flag `0x930` and variable `0x5018`.
   The current production report states its ordinary-mode hypothesis; it does
   not claim to reconstruct all persisted/runtime mode selectors.
2. **Special states:** the exact ability override checks internal species
   496/497/498/913/1460. Shedinja (303) has special HP; held item835 has an
   extra non-HP doubling path. Unknown forms, nonzero backup species,
   eggs and hyper-training remain explicitly unqualified. Broad species/held
   targets cannot receive authority solely because a table entry exists.
3. **Existing-state preservation:** native/product lineage includes empty
   moves with nonzero stored PP. A generalized writer must preserve untouched
   slots and explain any replacement/PP-Up normalization, independently audit
   the complete output and avoid imposing a guessed global PP=0 rule.
4. **HP decrease:** exact code has a separate decreasing-max path; the
   existing product rejects decreasing HP. Retain that rejection until a
   deliberate safe policy and independent reconstruction qualify it.

Continue static saved-context/exception exclusion and held-target qualification
before opening the writer gate. Then implement capability-specific edits and
independent complete-output reconstruction, preserve Money/Inventory composition,
and prepare a single grouped Human acceptance packet across materially different
ordinary specimens. Do not request serial gameplay canaries from this result.

Ability has **not** been excluded from the adopted E3 target. Ordinary resolution
is established; exceptional states are bounded out of this read-only practical
corroboration. If a later writer proposal excludes Ability altogether, it must
present a Human decision packet explaining the evidence, unresolved rule,
benefit/risk and E4/E5 consequences. This candidate makes no such scope decision.

## Verification and protection

Fourteen new synthetic tests cover independent whole-save reconstruction,
checksum corruption, low-level stat discrimination, correct hidden bit,
selector fallbacks, four PP-Up pairs, move996, stale empty PP, malformed
mint/level/EV, hyper-training, forms, unknown metadata and exact-ROM rejection.
The existing v0.22 suite passed 95 tests before the final whole-save test was
added; verifier tests passed 13 and existing Fast Lab Party tests passed 15.
Final focused rerun and push-safe checks are recorded with the candidate commit.
No full-repository/platform/gameplay test claim is made.

The nine private sources and exact ROM were read-only and rehashed unchanged.
The active/inactive slot/checksum parser remained unchanged. Product writers,
GUI binding, Money/Inventory behavior and E4 construction were not expanded.
No merge, release, Stable promotion or private-artifact publication occurred.
