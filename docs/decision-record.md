# Canonical decision record — 2026-10-06

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or explicitly adopted here.

## Controlling current decision — M5A bounded money FAMILY candidate

Strategic Human authorization:

> `AUTHORIZE POST-M4 NORTH STAR EXPANSION AND M5A MONEY INVESTIGATION`

First exact writer authorization:

> `AUTHORIZE M5A EXACT MAX-MONEY CANARY: implement and execute the bounded exact-input 3000-to-9999999 proof writer against SHA-256 fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b; write only a new output file; require complete independent diff/checksum/invariant audit and source immutability; do not generalize this proof to reusable arbitrary money editing or any other capability.`

Repeated-use authorization:

> `AUTHORIZE M5A ROUND-TRIP ADOPTION AND REPEATED-USE CANARY: canonically record the successful exact 3000-to-9999999 game round trip and the observed early-game EventObjectTemplate/parasite transition without broadening the existing M4 provenance predicate; then implement and execute one bounded second money canary against exact return SHA-256 1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4, changing 9999999 to 1234567 into a new output only with complete independent audit. Do not yet adopt a reusable arbitrary-money FAMILY or broaden save/build/provenance scope.`

Current bounded FAMILY authorization:

> `AUTHORIZE M5A SECOND ROUND-TRIP ADOPTION AND BOUNDED MONEY FAMILY CANDIDATE: canonically record the successful 9999999-to-1234567 game round trip; correct the independently reproduced M5A evidence-record discrepancies for the first EventObjectTemplate changed-byte count and opaque emulator-footer behavior; then design, implement, test, and independently audit a retained-lineage reusable money FAMILY candidate for values 0..9999999, initially fail-closed to the currently evidenced PokemonStart v0.15 build/environment and observed encryption-key boundary. Keep the existing M4 check_game_transition/provenance predicate unchanged. Any M5A-specific game-return continuation rule must be separately bounded to source-backed and independently evidenced normal-save behavior, including the observed section-4 parasite-tail evolution, and must fail closed outside that envelope. Do not expose money editing through the GUI yet, do not broaden save/build/version support, and do not begin M5B/M5C implementation.`

The controlling detailed M5A evidence/candidate record is `docs/m5a-second-roundtrip-and-money-family.md`. Where older M5A prose conflicts with its independently reproduced corrections, that newer record controls.

## Expanded North Star

Build an evidence-first local save editor for the owner's positively supported PokemonStart save lineage that performs the common practical edits the owner actually wants while retaining fail-closed provenance/capability gates, separate-output publication, independent verification, and a reliable recovery path.

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
8. **M5A — Money capability — FAMILY CANDIDATE IMPLEMENTED / TESTED / INDEPENDENTLY AUDITED.** Two consecutive exact money transformations are game-proven: `3000 -> 9,999,999`, then `9,999,999 -> 1,234,567`. The reusable candidate supports integer targets `0..9,999,999` only within the retained root-anchored private money lineage, exact evidenced PokemonStart v0.15 build, explicit macOS+mGBA 0.10.5 environment binding, and observed encryption key `0`. It is not exposed through GUI yet and M5A is not declared broadly complete beyond this bounded candidate.
9. **M5B — Inventory capability — PLANNED, NOT AUTHORIZED.**
10. **M5C — Practical Pokemon editing — PLANNED, NOT AUTHORIZED.**
11. **Future — Pokédex — NOT AUTHORIZED.**

## M5A independently reproduced game evidence

Source-derived representation remains:

`money = LE32(active logical section 1 @ 0x0290) XOR LE32(active logical section 0 @ 0x0F20)`

Pinned CFRU-JP source places `SaveBlock1.money` at `0x0290`, `SaveBlock2.encryptionKey` at `0x0F20`, and records the 9,999,999 maximum-money patch. Public FireRed decomp source corroborates XOR decode/encode semantics.

Exact first round trip:

- initial retained input SHA: `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`
- first editor candidate SHA: `e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69`
- first normal-save return SHA: `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`
- semantic result: `3000 -> 9,999,999`, displayed in game and retained after normal save

Exact second round trip:

- second editor candidate SHA: `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`
- second normal-save return SHA: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- semantic result: `9,999,999 -> 1,234,567`, displayed in game and retained after normal save
- slot/counter: `0/2 -> 1/3`
- saved-game statistic: `2 -> 3`
- play time: `151 -> 159` seconds
- party[0] unchanged
- sectors 28–31 unchanged
- stable checksum-covered payload unchanged under the existing M4 volatile-field mask

## Corrections controlling older M5A prose

Pinned CFRU-JP `SaveBlock1.eventObjectTemplates[64]` begins at **`0x08E0`**. On the first very-early-game return, observed additional changes occurred only in subrange **`0x09E0..0x0ED9`**, totaling **85 bytes** after excluding already-qualified M4 EventObject runtime fields. These changes did not recur on the second return. Older M5A prose stating 89 bytes or placing the array start at `0x09E0` is superseded.

Opaque emulator footer policy is also corrected: editor operations preserve it exactly; normal game/emulator saves may change it. First candidate -> first return and second candidate -> second return both changed footer hashes. Older M5A prose claiming footer equality across a normal game save is superseded.

Both normal returns independently changed exactly logical-section-4 checksum-excluded offsets `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9`. Pinned CFRU-JP source uses section 0/4/13 unchecked tails as parasite save storage.

## Bounded M5A reusable candidate

`pokemonstart_m5a_money_family.py` is a candidate reusable capability, not a general save editor.

Positive boundary:

- FAMILY root SHA: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`
- build SHA: `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`
- environment ID: `macos-mgba-0.10.5`
- encryption key: exactly `0x00000000`
- target range: integer `0..9,999,999`
- journaled root-anchored lineage only
- source immutable / separate new output / M4 hardened publication layer
- GUI exposure: none

The FAMILY root is deliberately the second game-proven return, after the one-time EventObjectTemplate initialization observed in the first return. That initialization is therefore not promoted to reusable normal-save volatility.

The M5A-specific game-return continuation rule preserves the existing M4 checksum-covered stable-payload mask and additionally allows only logical-section-4 parasite-tail offsets `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9` to vary across a normal save. It still requires opposite-slot transition, exact +1 counter, previous slot byte preservation, exact money retention, key `0`, party[0]/count preservation, saved-game +1, monotonic play time, sectors 28–31 preservation, and expected section rotation. The opaque footer may change only across the game/emulator return boundary.

**The existing M4 `check_game_transition` implementation and M4 provenance model are unchanged.**

Independent audit is implemented separately in `tests/m5a_independent_money_family_audit.py` and does not import the FAMILY implementation. Focused candidate construction tests recorded **15/15 PASS**; actual private second-candidate -> second-return transition also passed both the candidate rule and the independent auditor. This local execution evidence is not a GitHub Actions claim.

## Reusable transaction contract retained

Every adopted writer capability must continue to:

- hash/read input before mutation;
- fail closed on unsupported structure/provenance/capability state;
- reject stale plans;
- mutate only capability-authorized bytes;
- recompute only required checksums;
- explain every diff;
- preserve inactive slot, counters, section metadata/permutation, sectors 28–31, unqualified tails/footer, and every other unqualified byte;
- independently re-verify output;
- preserve source immutability;
- write only a separate new output;
- retain an original recovery anchor;
- never automatically overwrite emulator live-save state.

## M4 delivery boundary retained

M4 markings delivery remains as previously adopted: macOS bounded publication; Windows semantic/browser delivery only on exact validated Windows build `26200.9457` with filesystem publication additionally restricted to local fixed NTFS/no-reparse-parent boundary; NiceGUI localhost-only at `127.0.0.1`; no relay/LAN/public exposure; no automatic live-save replacement.

M5A money FAMILY does **not** inherit Windows delivery merely because M4 markings supports it. Current M5A FAMILY publication is fail-closed to the evidenced macOS+mGBA environment only.

## Unsupported / non-claimed surfaces

Unless later independently proven and authorized, unsupported/non-claimed includes:

- arbitrary/non-lineage saves;
- another PokemonStart build/version;
- nonzero encryption-key private saves;
- Windows M5A money FAMILY publication;
- GUI money controls;
- inventory/item writes;
- species/forms, moves, abilities, level/EXP/hyper-training and other unadopted Pokemon writes;
- Pokédex writes;
- general event/story/quest flag editing;
- public/LAN/remote browser exposure;
- automatic live-emulator save replacement;
- broader threat-model/public-release guarantees.

## Authority chain

Key durable records include:

- `docs/evidence.md`
- `docs/m3a-support-envelope-findings.md`
- `docs/m3c-exit-assessment.md`
- `docs/m4-entry-decision.md`
- `docs/m4-bounded-implementation-authorization.md`
- `docs/m4-delivery-correction.md`
- `docs/m4-pr13-adoption.md`
- `docs/m4-windows-validation.md`
- `docs/m4-completion.md`
- `docs/post-m4-strategy-and-m5a-money.md`
- `docs/m5a-money-private-read-audit.md`
- `docs/m5a-exact-max-money-canary.md`
- **`docs/m5a-second-roundtrip-and-money-family.md` — controlling current M5A correction/evidence record**

## Current authorization boundary

The Human authorization above permits the bounded M5A FAMILY candidate implementation, testing, independent audit, and canonical evidence adoption. It does **not** authorize GUI exposure, M5B/M5C implementation, broader save/build/version/key scope, Windows M5A adoption, public release, or weakening M4 provenance.

The next milestone decision must independently determine whether the bounded FAMILY candidate is sufficient to mark M5A complete and expose it through a delivery layer, or whether a narrower additional proof is required. Do not start M5B merely because the candidate implementation exists.
