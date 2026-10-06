# PokemonStart save editor research

Evidence-first research and tooling for a user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

- **M1 — reproducible read-only verifier: COMPLETE.**
- **M2 — exact one-field HP-IV writer proof: COMPLETE.**
- **M3A — reusable write-envelope characterization: COMPLETE.**
- **M3B — bounded same-field transaction proof: COMPLETE.**
- **M3C — bounded party-field expansion: COMPLETE.** Friendship/markings/ball plus the first derived-state nature-mint/EV/IV/stat group survived representative retained-lineage game round trips; unsupported fields remain blocked rather than guessed.
- **M4 — bounded usable-editor first slice: COMPLETE.** Reusable `party[0] markings 0 <-> 1`, retained-lineage S0/P/C gating, macOS publication, localhost NiceGUI, and the separately bounded exact-Windows path are adopted.
- **M5A — Money: FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.** Two consecutive exact money transformations are game-proven: `3000 -> 9,999,999` and `9,999,999 -> 1,234,567`. The bounded FAMILY supports integer targets `0..9,999,999` only inside its current journal/build/key/macOS boundary. Fresh lifecycle coverage and the full suite are green, but practical provenance continuity during ordinary gameplay remains design-only, so Money is not GUI-exposed and M5A is not marked COMPLETE.
- **M5B Inventory: PLANNED, NOT AUTHORIZED.**
- **M5C Practical Pokemon editing: PLANNED, NOT AUTHORIZED.**
- **Future Pokédex editing: NOT AUTHORIZED.** General event/story/quest flag editing remains out of scope.

The expanded North Star is to build an evidence-first local editor for the owner's positively supported PokemonStart save lineage that performs the practical edits the owner actually wants while retaining fail-closed provenance/capability gates, separate outputs, independent verification, and recovery. Current target order is money -> inventory/items -> practical party-Pokemon editing; Pokédex is future work.

## M5A Money

Pinned CFRU-JP source places the stored money word at SaveBlock1 offset `0x0290` and the SaveBlock2 encryption key at offset `0x0F20`. The read/write representation is:

```text
money = LE32(active logical section 1 @ 0x0290)
        XOR LE32(active logical section 0 @ 0x0F20)
```

The retained private lineage has provided two consecutive game-proven edit/resave cycles:

1. `3000 -> 9,999,999`
2. `9,999,999 -> 1,234,567`

The second normal-save return is SHA-256 `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf` and is the current bounded FAMILY root.

### Corrected early-game evidence

Pinned CFRU-JP places `SaveBlock1.eventObjectTemplates[64]` at `0x08E0`. On the first very-early-game normal save, only subrange `0x09E0..0x0ED9` changed beyond already-qualified M4 EventObject runtime fields, totaling **85 bytes**. This initialization did not recur on the second save and is not promoted into a reusable continuation mask.

The 16-byte emulator footer is opaque: editor output preserves it exactly, while normal game/emulator saves may change it.

Both observed normal saves changed exactly four bytes in the checksum-excluded logical-section-4 parasite tail: `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9`. CFRU-JP source uses unchecked section 0/4/13 tails as parasite storage.

### Bounded reusable candidate

`pokemonstart_m5a_money_family.py` is separate from M4 and does **not** alter `pokemonstart_m4_core.check_game_transition` or the M4 markings capability registry.

Positive boundary:

- root SHA-256: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- build SHA-256: `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`
- environment ID string: `macos-mgba-0.10.5`
- encryption key: exactly `0x00000000`
- target range: integer `0..9,999,999`
- journaled root-anchored lineage only
- new verified output only; source remains immutable
- current publication boundary: macOS only
- no GUI exposure yet

`macos-mgba-0.10.5` is a **Human-attested environment binding label**, not machine attestation of the mGBA executable/version. The code machine-checks exact ROM/build SHA, exact label equality, and actual macOS at Money publication; it does not hash or query mGBA itself.

The current M5A canary-oriented game-return rule remains deliberately strict: it requires the observed money, party, stable-payload, section-4 parasite-tail, slot/counter, saved-game, sectors 28–31 and section-rotation envelope. This is useful proof infrastructure but is too strict for ordinary gameplay continuity; no broader provenance rule has been implemented yet.

Independent audit code is in `tests/m5a_independent_money_family_audit.py`. Candidate tests are in `tests/test_m5a_money_family.py`, and end-to-end closure tests are in `tests/test_m5a_money_family_lifecycle.py`.

Fresh full-suite execution on exact code/test candidate `3209f3aadb3b4dacbfab146dddbb27925895ac63`:

```text
python3 -m unittest discover -s tests -v
119 tests OK, 28 skipped
```

The run used GitHub Actions Ubuntu 24.04 / Python 3.12. A temporary branch-only workflow was used only to obtain fresh execution evidence and was removed afterward.

### Practical provenance-continuity design

Pinned CFRU-JP full-save behavior supports a strong **P-direct** model for exactly one normal save from a journaled parent: the new save uses the opposite slot with counter +1 and one-position rotation while the prior active slot remains byte-identical as an ancestry witness. This can establish ancestry without requiring ordinary gameplay payload equality.

After two or more ordinary full saves, that old editor-output slot may be overwritten. Final save bytes alone can then no longer prove exact ancestry to the older node. A practical longer-gap design therefore requires an explicit **Human-attested P-reanchor**, with S0/build/key/player-identity/counter checks used only as corroboration, never automatic ancestry proof.

This provenance design is recorded but **not implemented or authorized for adoption yet**. See `docs/m5a-family-closure-and-provenance-continuity-design.md`.

## Run the verifier

Python 3.10+ is sufficient for the core verifier:

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000` flash bytes or `0x20010` with a 16-byte opaque emulator footer and fails closed on malformed/ambiguous/inconsistent layouts.

## M4 browser delivery

The currently adopted GUI remains the M4 markings delivery layer. NiceGUI binds only to `127.0.0.1`; there is no relay/LAN/public exposure and the tool never automatically overwrites an emulator live save. Money controls are intentionally not exposed yet.

Windows M4 support remains separately bounded to validated Windows build `26200.9457`; filesystem publication additionally requires a user-controlled local fixed NTFS destination with no reparse component in the existing parent chain. M5A Money does not automatically inherit Windows delivery.

## Proof / transaction principles

Repository proof writers and transaction tooling are research infrastructure. Supported writers must reject unsupported profiles/starting states, stale plans, unexplained diffs, input/output aliasing, existing destinations, and unsupported platform/filesystem boundaries. Generated outputs are independently re-verified and inputs remain immutable.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

No private `.sav`, ROM, `.pks`, patch, proprietary executable, copyrighted game asset, or proprietary payload is committed.

## Canonical records

- `docs/decision-record.md` — controlling milestone/authority state
- `docs/evidence.md`
- `docs/m3c-exit-assessment.md`
- `docs/m4-completion.md`
- `docs/post-m4-strategy-and-m5a-money.md`
- `docs/m5a-money-private-read-audit.md`
- `docs/m5a-exact-max-money-canary.md`
- `docs/m5a-second-roundtrip-and-money-family.md`
- `docs/m5a-family-closure-and-provenance-continuity-design.md` — controlling current M5A closure/design record

## Current non-claims

The M5A candidate does not support or claim arbitrary/unrooted saves, another PokemonStart build/version, nonzero encryption-key private saves, machine-attested mGBA version identity, Windows M5A publication, GUI money editing, automatic longer-gap provenance inference, inventory/item writes, Pokemon species/stat editing, Pokédex editing, general progression flags, public release guarantees, or broader network/threat-model scope.
