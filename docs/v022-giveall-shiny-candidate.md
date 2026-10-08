# Exact-v0.22 Give All (recovery subset) and PID-only shiny — candidate

Status: **core candidate; not GUI-integrated, not game-accepted, not reviewed.**
Base: canonical `main` `5864e7a`. E5 is not incorporated.

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

## Pending before review

- GUI controls (after E5 adoption, on top of the E5 GUI).
- Human gameplay: Bag display after Give All and use of one newly qualified
  item; shiny appearance in summary/battle; normal SAVE and return checks.
