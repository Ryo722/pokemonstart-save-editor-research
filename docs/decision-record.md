# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — M5A FAMILY closure complete; provenance continuity remains design-only

Strategic Human authorization:

> `AUTHORIZE POST-M4 NORTH STAR EXPANSION AND M5A MONEY INVESTIGATION`

Exact writer authorization:

> `AUTHORIZE M5A EXACT MAX-MONEY CANARY: implement and execute the bounded exact-input 3000-to-9999999 proof writer against SHA-256 fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b; write only a new output file; require complete independent diff/checksum/invariant audit and source immutability; do not generalize this proof to reusable arbitrary money editing or any other capability.`

Repeated-use authorization:

> `AUTHORIZE M5A ROUND-TRIP ADOPTION AND REPEATED-USE CANARY: canonically record the successful exact 3000-to-9999999 game round trip and the observed early-game EventObjectTemplate/parasite transition without broadening the existing M4 provenance predicate; then implement and execute one bounded second money canary against exact return SHA-256 1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4, changing 9999999 to 1234567 into a new output only with complete independent audit. Do not yet adopt a reusable arbitrary-money FAMILY or broaden save/build/provenance scope.`

Bounded FAMILY authorization:

> `AUTHORIZE M5A SECOND ROUND-TRIP ADOPTION AND BOUNDED MONEY FAMILY CANDIDATE: canonically record the successful 9999999-to-1234567 game round trip; correct the independently reproduced M5A evidence-record discrepancies for the first EventObjectTemplate changed-byte count and opaque emulator-footer behavior; then design, implement, test, and independently audit a retained-lineage reusable money FAMILY candidate for values 0..9999999, initially fail-closed to the currently evidenced PokemonStart v0.15 build/environment and observed encryption-key boundary. Keep the existing M4 check_game_transition/provenance predicate unchanged. Any M5A-specific game-return continuation rule must be separately bounded to source-backed and independently evidenced normal-save behavior, including the observed section-4 parasite-tail evolution, and must fail closed outside that envelope. Do not expose money editing through the GUI yet, do not broaden save/build/version support, and do not begin M5B/M5C implementation.`

Current closure/design authorization:

> `AUTHORIZE M5A FAMILY CLOSURE AND PROVENANCE-CONTINUITY DESIGN: from fresh current main, close the bounded Money FAMILY candidate evidence gaps without broadening writer capability by adding and executing end-to-end synthetic lifecycle coverage for bootstrap -> preview -> commit -> Human-observed game-return enrollment -> returned-save eligibility -> next preview/commit, plus negative journal/parent/duplicate/environment cases; fresh-run the full repository suite on the exact candidate and correct canonical environment wording so macos-mgba-0.10.5 is not overstated as machine-attested where it is only human-bound. In parallel, perform a design-only, evidence-first investigation of a practical retained-lineage provenance-continuity model that separates save ancestry from ordinary gameplay payload changes, using pinned CFRU-JP save-slot/counter/write behavior and independently reproduced round-trip evidence. Do not implement a broader provenance predicate, do not expose money through GUI, do not mark M5A COMPLETE, and do not begin M5B/M5C until the resulting decision surface is reviewed and separately authorized.`

The controlling current M5A closure/design record is `docs/m5a-family-closure-and-provenance-continuity-design.md`. `docs/m5a-second-roundtrip-and-money-family.md` remains the controlling detailed record for the second round trip and current FAMILY implementation. Where older M5A prose conflicts with later independently reproduced corrections, the newer records control.

## Expanded North Star

Build an evidence-first local save editor for the owner's positively supported PokemonStart save lineage that performs the practical edits the owner actually wants while retaining fail-closed provenance/capability gates, separate-output publication, independent verification, and a reliable recovery path.

Target practical capability order:

1. money editing;
2. inventory/item editing;
3. practical party-Pokemon editing, ultimately including species transformation only where all required coupled state is proven;
4. future bounded Pokédex editing if independently justified.

General event/story/quest flag editing is an explicit non-goal. PKHeX compatibility, generic CFRU editing, arbitrary-save support, broad PokemonStart version support, and feature-count parity are not goals by themselves.

## Milestone architecture and current position

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
4. **M3B — bounded same-field transaction proof — COMPLETE.**
5. **M3C-F1 — friendship proof — COMPLETE.**
6. **M3C — bounded party-field expansion — COMPLETE.** Friendship/markings/ball and first derived-state nature-mint/EV/IV/stat groups survived representative retained-lineage game round trips; unproven fields remain blocked.
7. **M4 — bounded usable-editor first slice — COMPLETE.** Retained-lineage S0/P/C core, reusable `party[0] markings 0 <-> 1` FAMILY, macOS publication, localhost NiceGUI, and bounded exact-Windows support were adopted. Existing M4 provenance predicates remain unchanged by M5A.
8. **M5A — Money capability — FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.** Two consecutive exact money transformations are game-proven. The bounded FAMILY implementation supports integer targets `0..9,999,999` only inside its current journal/build/key/macOS boundary. End-to-end synthetic journal lifecycle coverage is now green and the full repository suite is freshly green. Practical provenance continuity during ordinary gameplay remains a design-only decision and therefore blocks GUI adoption / M5A COMPLETE.
9. **M5B — Inventory capability — PLANNED, NOT AUTHORIZED.**
10. **M5C — Practical Pokemon editing — PLANNED, NOT AUTHORIZED.**
11. **Future — Pokédex — NOT AUTHORIZED.**

## M5A proven money evidence

Source-derived representation:

`money = LE32(active logical section 1 @ 0x0290) XOR LE32(active logical section 0 @ 0x0F20)`

Pinned CFRU-JP source places `SaveBlock1.money` at `0x0290`, `SaveBlock2.encryptionKey` at `0x0F20`, and records the 9,999,999 maximum-money patch. Public FireRed decomp source corroborates XOR decode/encode semantics.

Game-proven retained-lineage round trips:

- original input SHA `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`
- first editor candidate SHA `e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69`
- first return SHA `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`
- semantic result `3000 -> 9,999,999`, displayed and retained after normal save
- second editor candidate SHA `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`
- second return SHA / current FAMILY root `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- semantic result `9,999,999 -> 1,234,567`, displayed and retained after normal save
- second transition slot/counter `0/2 -> 1/3`, saved-game statistic `2 -> 3`, play time `151 -> 159`, party[0] unchanged, sectors 28–31 unchanged

Corrected early-game evidence remains:

- `eventObjectTemplates[64]` begins at SaveBlock1 `0x08E0`;
- first-return additional initialization was limited to subrange `0x09E0..0x0ED9`, 85 bytes after excluding already-qualified runtime fields;
- this initialization did not recur on the second return;
- editor output preserves the opaque 16-byte footer, while normal game/emulator saves may change it;
- both normal returns changed exactly section-4 checksum-excluded offsets `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9`.

## Current bounded Money FAMILY implementation

`pokemonstart_m5a_money_family.py` remains separate from M4 and does not alter `pokemonstart_m4_core.check_game_transition` or the M4 markings registry.

Current positive boundary:

- FAMILY root SHA `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- build SHA `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`
- environment ID string `macos-mgba-0.10.5`
- encryption key exactly `0x00000000`
- target range integer `0..9,999,999`
- journaled root-anchored lineage only
- source immutable / separate new output / M4 hardened publication layer
- GUI exposure none

### Environment semantics

`macos-mgba-0.10.5` is a **Human-attested environment binding label**, not machine verification of the mGBA executable or version.

The code machine-checks exact ROM/build SHA, exact environment-label equality, and actual macOS (`sys.platform == "darwin"`) at Money FAMILY publication. It does not hash/query the mGBA executable or prove version 0.10.5. The emulator/version part of the label comes from Human-observed environment evidence from the two successful round trips.

## FAMILY closure evidence

New closure tests in `tests/test_m5a_money_family_lifecycle.py` exercise:

`bootstrap -> preview -> commit -> Human-observed game-return enrollment -> returned-save eligibility -> next preview/commit`

and negative journal/parent/duplicate/environment cases.

Fresh full-suite candidate:

- exact executable/test commit: `3209f3aadb3b4dacbfab146dddbb27925895ac63`
- GitHub Actions Ubuntu 24.04 / Python 3.12
- command: `python3 -m unittest discover -s tests -v`
- result: **119 tests OK, 28 skipped, 0 failures/errors**

The first temporary run exposed one incorrect expectation in the newly added test; the implementation correctly failed closed with `eligible=False`. The test was corrected, then the full suite passed. The temporary workflow was removed and is not part of the intended canonical tree.

## Provenance-continuity design result — NOT IMPLEMENTED

Pinned CFRU-JP `src/save.c` shows that a full normal save increments `gFirstSaveSector` by one, increments `gSaveCounter`, and writes all 14 logical chunks into the slot selected by counter parity. A single full save therefore leaves the prior active slot available as a byte-level ancestry witness; this behavior matches both private money round trips.

### P-direct — recommended first implementation candidate

For exactly one observed full normal save from a journaled parent, ancestry can be established independently of ordinary gameplay payload changes by requiring:

- candidate S0 valid;
- opposite active slot;
- exact counter +1 with adopted wrap handling;
- expected one-position section rotation;
- previous active slot preserved byte-for-byte as the journaled parent active slot;
- exact ROM/build binding;
- explicit Human normal-save attestation.

This would allow legitimate gameplay changes in the new active payload without pretending those bytes are editor-authorized mutations.

### P-reanchor — possible longer-gap manual continuation

After two or more full saves, the old editor-output slot may have been overwritten. Final save bytes alone can no longer prove exact ancestry to that older node.

A practical longer-gap model therefore requires an explicit **Human-attested re-anchor**, with S0/build/key checks and stable player identity (player name/gender/trainer ID) plus counter plausibility as corroboration. These fields are not cryptographic provenance and automatic enrollment from them is rejected.

### Rejected model

Do not automatically accept a save because checksums are valid, build is selected, trainer identity matches, counter looks newer, and key is 0. Those facts establish compatibility/plausibility, not ancestry.

### Recommended decision

Adopt a two-tier provenance model only under a separate authorization:

1. **P-direct** structural one-save descent first;
2. **P-reanchor** explicit/manual Human-attested continuation only for longer ordinary-play gaps.

Keep current M4 transition logic unchanged. Do not implement broader payload-volatility masks as a substitute for ancestry evidence.

## Reusable transaction contract retained

Every adopted writer capability must continue to hash/read input before mutation; fail closed on unsupported S0/P/C; reject stale plans; mutate only authorized bytes; recompute only required checksums; explain every editor diff; independently reverify output; preserve source immutability; write only a separate new output; keep a recovery anchor; and never automatically overwrite emulator live-save state.

## Delivery boundary retained

M4 markings delivery remains as previously adopted: bounded macOS publication; separately bounded Windows markings support; localhost-only NiceGUI; no relay/LAN/public exposure; no automatic live-save replacement.

M5A money currently does not inherit Windows delivery and is not GUI-exposed.

## Unsupported / non-claimed

Unless later independently proven and authorized:

- arbitrary/non-lineage saves;
- another PokemonStart build/version;
- nonzero-key private Money FAMILY saves;
- machine-attested mGBA version identity;
- Windows M5A publication;
- GUI money controls;
- automatic longer-gap provenance inference;
- inventory/item writes;
- species/forms/moves/abilities/level/EXP and other unadopted Pokemon writes;
- Pokédex writes;
- general event/story/quest flag editing;
- public/LAN/remote browser exposure;
- public release/distribution guarantees.

## Authority chain

Key current durable records:

- `docs/evidence.md`
- `docs/m4-p-transition-model.md`
- `docs/m4-completion.md`
- `docs/post-m4-strategy-and-m5a-money.md`
- `docs/m5a-money-private-read-audit.md`
- `docs/m5a-exact-max-money-canary.md`
- `docs/m5a-second-roundtrip-and-money-family.md`
- **`docs/m5a-family-closure-and-provenance-continuity-design.md` — controlling current M5A closure/design record**

## Current authorization boundary / next decision

The present authorization is exhausted by lifecycle closure testing, fresh full-suite execution, environment wording correction, and design-only provenance investigation.

It does **not** authorize:

- implementing P-direct or P-reanchor;
- changing M4 provenance;
- exposing Money through GUI;
- marking M5A COMPLETE;
- starting M5B or M5C;
- broader save/build/version/key/platform support.

The next Human decision should choose whether to implement the recommended two-tier provenance continuity, beginning with P-direct and keeping P-reanchor explicit/manual, or to retain the current canary-style strict continuation despite its ordinary-play usability cost.
