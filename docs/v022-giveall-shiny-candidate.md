# Exact-v0.22 Give All (recovery subset) and PID-only shiny — candidate

Status: **GUI-integrated sprint candidate; not game-accepted, not reviewed, not adopted.**
Integration branch: `codex/v022-editor-sprint-20261008` = E5 candidate (with the
requested-field persistence correction `08d2151`) + this candidate + GUI wiring.
Launch: `./start-editor.command` (see README Quick start).

## Scope

- **Give All Supported Items:** the 32 regular-pocket items whose complete
  behavior metadata (pocket 1, importance 0, type 1, classifier 0, field-use
  `0x080A29B5`, battle usage 1, battle-use `0x080A327D`) equals the adopted
  E2 medicines. Pinned IDs: 13–33, 38–41, 44, 52–56, 82. Each is raised to 99;
  larger stacks are not lowered. Enabled only while the result stays within
  section 13 (≤325 regular entries). This is not all-item support.
- Individual add/set/remove uses the same 32-item set.
- **Shiny:** PID-only transition for eligible ordinary Party records and E4
  creation. OT name/TID/SID, nature (PID mod 25), native gender, stored
  ability bits and bytes 4..99 are unchanged. Species change in the same edit,
  unchanged state, and PID collisions within the Party are rejected.

## Evidence

- Both independent auditors reconstruct complete outputs (Inventory: own
  Give All expansion; Party/creator: own shiny derivation and predicates).
- Synthetic suite: 310 tests, 287 pass, 15 Windows skips; 8 NiceGUI tests
  could not run in the agent sandbox (not counted as passing).
- Exact-ROM in-memory derivations on retained E4 saves: Give All and shiny
  edits/creation pass complete independent audits. No files written.
- Native isolated execution (owner host, 2026-10-08,
  `pokemonstart_v022_shiny_native_probe.py`, retained E4 return save):
  `NATIVE_SHINY_PID_ONLY_QUALIFIED_NOT_GAME_ACCEPTED`; 48 threshold cases
  (24 shiny) agree with score < 8; 12 record transitions (to and back) keep
  `IsMonShiny`-expected state, nature, `GetMonGender`, `GetMonAbility` and
  bytes 4..99.

## GUI integration (2026-10-08 sprint)

- Items tab: `Give All Supported Items` checkbox (single-operation, disabled with
  the reason when unavailable); refuses combination with other Items edits.
- Party: `Shiny（色違い）` checkbox for E3-eligible members, ★ in headers;
  creation: optional `Create Shiny`. Request schema unchanged when unused, so
  E5 Cycle 1/2 requests derive byte-identical outputs to the Human-accepted
  E5 artifacts (checked on the retained private inputs).
- `PC Box` tab: read-only table (species, level, held item, moves, IV/EV,
  friendship, ★, native-observed flag); fails closed off the exact ROM.
- Item identities of all 32 Give All targets were listed from the exact ROM:
  recovery medicines, status cures, revives, drinks/food, Berry Juice and the
  three flutes; all share the adopted medicine field/battle routines.

## Pending before review

- Human gameplay: Bag display after Give All and use of one newly qualified
  item; shiny appearance in summary/battle; normal SAVE and return checks.

## Additional evidence (2026-10-08)

- Human observation: the Party Zigzagoon that the formula and the native
  `IsMonShiny` classify as already shiny was seen as shiny in game.

## Box read-only qualification (viewer only; no writer)

- Exact ROM box pointer table (25 entries) equals the pinned CFRU-JP layout:
  boxes 1–19 in the original storage block, 20–22 in global extra sectors
  30/31 (not slot-rotated, not checksummed), 23–24 in SaveBlock1, 25 in
  SaveBlock2. Records are the 58-byte CompressedPokemon (packed 10-bit
  moves, no stored PP/stats); records may straddle section boundaries.
- Native observation (owner, disposable non-E5 pair): one normal SAVE after
  depositing Zigzagoon to Box 1/1 and Bulbasaur to Box 25/30. The read-only
  decoder found exactly those two records; species, EXP-derived level,
  friendship, EVs, IVs, held item, moves and ability selector all equal the
  source Party records.
- `pokemonstart_v022_box_model.py` is read-only. Boxes 2–24 are ROM/source
  mapped but not natively observed. Box writing remains unauthorized.

## Box writer — authorization decision (prepared, not requested as a blocker)

Evidence is sufficient for the read-only viewer only. A Box writer would need,
at minimum: (1) native observation of one deposit in each storage class not yet
observed (boxes 2–19 storage block, 20–22 unchecksummed extra sectors, 23–24
SaveBlock1); (2) a qualified Party(100)↔CompressedPokemon(58) mapping proven
by round-trip on natively deposited records; (3) a first writer limited to
editing existing records in boxes 1–19 (checksummed, slot-rotated) with
independent reconstruction; (4) one grouped Human SAVE/withdraw check.
Decision requested from the owner when convenient: **authorize step (1)–(3)
as a bounded Box-edit candidate (boxes 1–19, existing records only)?**
Box creation and boxes 20–25 writes stay out of scope until separately evidenced.
