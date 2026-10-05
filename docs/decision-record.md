# Canonical decision record — 2026-10-05

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or adopted here.

## Controlling current decision — post-M4 expansion and exact M5A max-money canary

Strategic Human authorization:

> `AUTHORIZE POST-M4 NORTH STAR EXPANSION AND M5A MONEY INVESTIGATION`

Exact writer/canary Human authorization:

> `AUTHORIZE M5A EXACT MAX-MONEY CANARY: implement and execute the bounded exact-input 3000-to-9999999 proof writer against SHA-256 fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b; write only a new output file; require complete independent diff/checksum/invariant audit and source immutability; do not generalize this proof to reusable arbitrary money editing or any other capability.`

The owner has identified a concrete practical unmet need: common PKHeX-like local edits such as money, inventory/items, and substantial party-Pokemon editing including species changes. General progression/event flag management is not desired; Pokédex editing is future work.

The strategic expansion is recorded in `docs/post-m4-strategy-and-m5a-money.md`. The read-side money proof is recorded in `docs/m5a-money-private-read-audit.md`. The exact writer execution and pre-game canary evidence are recorded in `docs/m5a-exact-max-money-canary.md`.

**Current position:** M1–M4 remain COMPLETE for their adopted bounded scopes. **M5A Money remains IN PROGRESS. One exact 3000 -> 9,999,999 candidate has been generated and independently audited, but the human game round trip is still required. No reusable arbitrary-money writer/FAMILY is authorized or claimed.**

## Expanded North Star

Build an evidence-first local save editor for the owner's **positively supported PokemonStart save lineage** that performs the common practical edits the owner actually wants, while retaining fail-closed provenance/capability gates, separate-output publication, independent verification, and a reliable recovery path.

The target practical capability set is:

1. money editing;
2. inventory/item editing;
3. practical party-Pokemon editing, ultimately including species changes and every coupled state that must be established for a safe transformation;
4. future bounded Pokédex editing if independently justified.

General event/story/quest flag editing is an explicit non-goal. PKHeX compatibility, generic CFRU editing, arbitrary save support, broad PokemonStart version support, and feature-count parity are not goals by themselves.

The North Star remains evidence-first: each field/capability must be proven independently, malformed/ambiguous/unsupported states fail closed, and a known offset or upstream struct does not by itself create writer authority.

The completed M4 markings editor remains a valid bounded first slice and safety foundation. This expanded goal does not retroactively broaden any M1–M4 claim.

## Milestone architecture and current position

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
4. **M3B — bounded same-field transaction proof — COMPLETE.**
5. **M3C-F1 — friendship field proof — COMPLETE.**
6. **M3C — goal-driven bounded party-field expansion — COMPLETE.** Low-coupling friendship/markings/ball and the first nontrivial derived-state nature-mint/EV/IV/stat group survived representative game-boundary proofs; remaining fields were explicitly BLOCKED/UNSUPPORTED rather than guessed.
7. **M4 — bounded usable editor / GUI first slice — COMPLETE.** PR #13 established the retained-lineage S0/P/C implementation and macOS delivery; PR #14 added the reviewed bounded Windows path under the exact host/filesystem limits below.
8. **M5A — Money capability — IN PROGRESS.** Read semantics are independently reproduced for the exact retained input. The exact `3000 -> 9,999,999` candidate has been generated with a sealed one-input writer, five-byte complete diff, synthetic tests, and an independent complete-byte audit. Human game load/resave evidence remains required before any game-proven or reusable money capability claim.
9. **M5B — Inventory capability — PLANNED, NOT AUTHORIZED.** Investigate only after M5A reaches a justified boundary; item catalog/pocket/encryption/add-remove semantics must be proven rather than inferred.
10. **M5C — Practical Pokemon editing — PLANNED, NOT AUTHORIZED.** Prefer generalizing already-proven/low-coupling attributes first; treat level/EXP/stat coupling and species transformation as separate higher-risk capabilities.
11. **Future — Pokédex — NOT AUTHORIZED.** Seen/caught editing may be evaluated as a dedicated semantic capability; this does not authorize a general flag editor.

Owner-use hardening and packaging are supporting work rather than mandatory standalone milestones. They should be performed when they materially improve safe use of the currently proven capability set, not as a substitute for the requested practical features.

## M5A controlling boundary

Pinned CFRU-JP source evidence at `e24a16fe39e27ae162faf5b78596d1f3df18489d` places:

- `SaveBlock1.money` at SaveBlock1 offset `0x0290`;
- `SaveBlock2.encryptionKey` at SaveBlock2 offset `0xF20`;
- logical section 0 as SaveBlock2 (`0xF24` bytes);
- logical section 1 as the first SaveBlock1 chunk (`0xFF0` bytes);
- an explicit CFRU-JP byte patch increasing maximum money to `9,999,999`.

CFRU-JP also declares encrypted-data rekey helpers and links the original FireRed money routines. Public `pret/pokefirered` source corroborates that the corresponding FireRed representation is an XOR of the stored money word with the SaveBlock2 encryption key.

The candidate/read rule is:

`money = LE32(active logical section 1 @ 0x0290) XOR LE32(active logical section 0 @ 0x0F20)`

For exact retained input SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`, independent read-only analysis obtained key `0`, stored word `0x00000BB8`, and decoded money `3000`; the user independently confirmed the game displays `3000` for that exact save.

Under the later exact canary authorization, `pokemonstart_m5a_exact_max_money_writer.py` generated one new candidate only for that hash/start state/target. Output SHA-256 is `e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69`. The complete diff is exactly three changed money bytes at `0x10290`–`0x10292` plus two logical-section-1 checksum bytes at `0x10FF6`–`0x10FF7`; all other bytes are identical. An independent auditor that does not import the writer passed all structural/checksum/diff/preservation checks. The source remained immutable. See `docs/m5a-exact-max-money-canary.md`.

**This proves only a pre-game exact candidate. It does not yet prove that PokemonStart accepts/persists the write, and it grants no reusable arbitrary-money writer authority.** Human load/display/resave and return-file audit are the next required evidence.

## Bounded M4 support contract retained as safety foundation

Writer support in the completed M4 slice remains the conjunction of three independent gates:

- **S0 — structural eligibility:** supported save size/layout, checksums, unique active slot, counter/parity, section permutation, and party structure;
- **P — provenance/profile eligibility:** the retained, root-anchored private PokemonStart v0.15 lineage bound to the independently selected ROM/build and local environment through the private hash/metadata-only journal;
- **C — capability eligibility:** only the separately proven reusable `party[0]` markings `0 <-> 1` FAMILY with exact starting-state preconditions.

M5 research must reuse or deliberately extend this model with fresh evidence. Structural similarity alone does not prove PokemonStart build identity. A ROM hash alone does not prove arbitrary save provenance. Unknown or unjournaled saves remain read-only even if S0 passes.

## Reusable transaction contract

Every future generated candidate, including any eventual M5 capability, must preserve the already adopted transaction properties unless a separately authorized change proves otherwise:

- hash/read the input before mutation;
- reject unsupported S0/P/C state;
- reject stale plans;
- mutate only capability-authorized bytes;
- recompute only required checksum(s);
- explain every output byte difference;
- preserve section metadata/permutation, counters, inactive slot, sectors 28–31, parasite tails, footer, and every other unqualified byte;
- independently re-verify the output;
- preserve source immutability;
- retain the original input as the recovery anchor;
- never automatically overwrite an emulator live-save path.

Where filesystem publication is used, the destination must be a separate nonexistent path; input aliases, existing destinations, repository destinations, and unsupported platform/filesystem boundaries fail closed.

## Adopted delivery boundary retained from M4

### macOS

The adopted macOS path provides S0/P/C inspection and preview, CLI/audit delivery, localhost-only NiceGUI browser delivery, independently verified in-memory browser download, and staged/no-clobber new-file publication with adopted macOS fault/race tests.

PR #13 exact candidate `2612df5de7bac7a1ebce6650eb9ed69b440fbc4d` was merged as `4685edd4fa61d7e02a29d1cb6279e0e8858bdaa7`.

### Windows

Semantic/in-memory/browser delivery is positively enabled only when the explicit host gate accepts validated Windows build `26200.9457`.

Windows filesystem publication additionally requires actual Windows, a local fixed NTFS volume, a user-controlled destination directory under the adopted threat model, no reparse-point component in the existing destination parent chain, a new `.sav` destination outside the repository, and no input/output alias or existing destination.

Network, removable, non-NTFS, reparse-parent, or unvalidated-build cases fail closed.

### NiceGUI network boundary

NiceGUI remains localhost-only: host `127.0.0.1`, `on_air=False`, no relay/LAN/public listener, no external private-save upload, and no automatic emulator live-save replacement.

No M5 capability is automatically exposed through the UI merely because research identifies an offset. UI actions must continue to originate from adopted core capability authority.

## M4 completion authority and evidence

Human authorization that completed the prior bounded slice:

> `AUTHORIZE PR #14 BOUNDED WINDOWS ADOPTION AND M4 COMPLETION: adopt and merge exact candidate a2f61ac9fa34164a531b5a884a40102de3bc52cf as bounded Windows support—semantic/browser delivery only on validated Windows build 26200.9457 and filesystem publication only to user-controlled local fixed NTFS with reparse parents rejected; retain network/removable/non-NTFS, hostile concurrent path replacement, and power-loss final-name durability as unsupported/non-claimed; retain the existing retained-lineage party[0] markings 0↔1 scope and all private-data/localhost/fail-closed boundaries; after verifying the exact merge on canonical main and reconciling canonical records, mark M4 COMPLETE for this bounded first slice. Do not broaden save/build/capability scope`

PR #14 exact candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was merged as `2547650cf898c89450a1d95b5252cf9c52e0f634`. See `docs/m4-completion.md` for the exact prior completion record.

Recorded M4 evidence includes representative retained-lineage game-boundary evidence for the markings FAMILY, adopted macOS S0/P/C + browser/publication evidence, and actual Windows 11 build `26200.9457` validation. The integrated Windows suite recorded **88 tests OK with 12 macOS-only skips**. These are local execution results, not GitHub Actions reproduction.

## Unsupported / non-claimed surfaces unless later milestones prove them

The post-M4 expansion is a goal and roadmap authorization, **not a blanket support claim**. Until separately proven/adopted, the following remain unsupported or non-claimed:

- arbitrary/non-lineage saves;
- broad PokemonStart build/version generalization;
- arbitrary party indices or unrestricted values;
- reusable/arbitrary money writing beyond the exact pre-game M5A canary;
- bags/items beyond a future adopted M5B capability;
- species/forms, held items, moves/PP/PP-Up, abilities, level/EXP/hyper-training and other coupled Pokemon state beyond independently adopted M5C capabilities;
- Pokédex writes;
- general event/story/quest flag editing;
- remote/LAN/public browser exposure;
- automatic live-emulator save replacement;
- network/removable/non-NTFS Windows filesystem publication;
- support for Windows builds that fail the exact validated-host gate;
- resistance to hostile concurrent parent-junction/final-name replacement after validation checks;
- Windows directory-metadata or final-name persistence across sudden power loss;
- public release/distribution guarantees.

The application semantics of sectors 30/31 and parasite tails remain preservation-oriented rather than generally decoded. The external footer remains preservation-only for editor output and may change under a later normal game/emulator save according to the established policy.

## Authority chain

Key durable authority/evidence records now include:

- `docs/evidence.md`
- `docs/m3a-support-envelope-findings.md`
- `docs/m3c-exit-assessment.md`
- `docs/m4-entry-decision.md`
- `docs/m4-bounded-implementation-authorization.md`
- `docs/m4-delivery-correction.md`
- `docs/m4-pr13-adoption.md`
- `docs/m4-windows-validation.md`
- `docs/m4-windows-candidate-evidence.md`
- `docs/m4-windows-bounded-integration-authorization.md`
- `docs/m4-completion.md`
- `docs/post-m4-strategy-and-m5a-money.md`
- `docs/m5a-money-private-read-audit.md`
- `docs/m5a-exact-max-money-canary.md`

## Authorization boundary after exact M5A canary generation

The owner has authorized the expanded North Star / milestone direction, M5A investigation, and exactly one bounded `3000 -> 9,999,999` writer execution for the named input SHA-256. That exact candidate has been generated and independently audited.

The current authorization does **not** authorize:

- generalizing the exact canary to arbitrary money values or additional save hashes;
- adopting a reusable money FAMILY before game-round-trip/repeated-use evidence;
- exposing money editing through the GUI;
- M5B inventory mutation;
- M5C Pokemon writer implementation;
- new supported save/build/version scope;
- public distribution/release guarantees;
- broader network/threat-model scope.

The next authorized activity is the Human game canary: load the exact candidate, confirm displayed `9,999,999`, perform one normal in-game save, and provide the return `.sav` for read-only audit. Any further writer-scope expansion requires a fresh evidence-based decision surface and Human authorization.