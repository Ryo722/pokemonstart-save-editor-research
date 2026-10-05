# Canonical decision record — 2026-10-05

GitHub `main` is the durable canonical authority for this project. Chat history, Memory, maker reasoning, local command logs, and old checkpoints are supporting context only unless reproduced or adopted here.

## Controlling current decision — post-M4 North Star expansion and M5A Money investigation

Human authorization:

> `AUTHORIZE POST-M4 NORTH STAR EXPANSION AND M5A MONEY INVESTIGATION`

This authorization supersedes the prior post-M4 assumption that the bounded markings editor might be followed only by owner-use hardening / maintenance. The owner has now identified a concrete practical unmet need: common PKHeX-like local edits such as money, inventory/items, and substantial party-Pokemon editing including species changes. General progression/event flag management is not desired; Pokédex editing is future work.

The strategic expansion and current M5A evidence/plan are recorded in `docs/post-m4-strategy-and-m5a-money.md`.

**Current position:** M1–M4 remain COMPLETE for their adopted bounded scopes. **M5A Money is IN INVESTIGATION. No money writer is authorized.**

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
8. **M5A — Money capability — IN INVESTIGATION.** Current authorization covers source/read-only characterization and the controlled private differential plan only. Writer implementation/private mutation is not authorized yet.
9. **M5B — Inventory capability — PLANNED, NOT AUTHORIZED.** Investigate only after M5A reaches a justified boundary; item catalog/pocket/encryption/add-remove semantics must be proven rather than inferred.
10. **M5C — Practical Pokemon editing — PLANNED, NOT AUTHORIZED.** Prefer generalizing already-proven/low-coupling attributes first; treat level/EXP/stat coupling and species transformation as separate higher-risk capabilities.
11. **Future — Pokédex — NOT AUTHORIZED.** Seen/caught editing may be evaluated as a dedicated semantic capability; this does not authorize a general flag editor.

Owner-use hardening and packaging are supporting work rather than mandatory standalone milestones. They should be performed when they materially improve safe use of the currently proven capability set, not as a substitute for the requested practical features.

## M5A controlling boundary

M5A currently establishes only a source-derived hypothesis and a private read-only proof plan.

Pinned CFRU-JP source evidence at `e24a16fe39e27ae162faf5b78596d1f3df18489d` places:

- `SaveBlock1.money` at SaveBlock1 offset `0x0290`;
- `SaveBlock2.encryptionKey` at SaveBlock2 offset `0xF20`;
- logical section 0 as SaveBlock2 (`0xF24` bytes);
- logical section 1 as the first SaveBlock1 chunk (`0xFF0` bytes);
- an explicit CFRU-JP byte patch increasing maximum money to `9,999,999`.

CFRU-JP also declares encrypted-data rekey helpers and links the original FireRed money routines. Public `pret/pokefirered` source corroborates that the corresponding FireRed representation is an XOR of the stored money word with the SaveBlock2 encryption key.

Therefore the current candidate read formula is:

`money = LE32(active logical section 1 @ 0x0290) XOR LE32(active logical section 0 @ 0x0F20)`

and the candidate write model would encode a target with that same key and recompute only the required logical-section-1 checksum.

**This is not yet a PokemonStart private-save proof and grants no writer authority.** The next required evidence is a controlled before/after private game save whose displayed money changes by a known amount, followed by an independent read-only differential. See `docs/post-m4-strategy-and-m5a-money.md`.

A separate Human authorization is required before implementing or executing any money writer.

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
- money writing beyond a future exact adopted M5A capability;
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

## Authorization boundary after post-M4 expansion

The owner has authorized the **expanded North Star / milestone direction** and **M5A Money investigation**. This means source review, read-only characterization, private read-only differential analysis when inputs are provided, and canonical documentation of those findings are authorized.

It does **not** authorize:

- implementation or execution of a money writer;
- M5B inventory writer/research that mutates private saves;
- M5C Pokemon writer implementation;
- new supported save/build/version scope;
- public distribution/release guarantees;
- broader network/threat-model scope.

After the M5A private differential is independently reproduced, present the exact bounded writer proof as a new decision surface with proposed transformation, evidence, benefit, risks/trade-offs, downstream impact, and human-canary burden. Stop for fresh Human authorization before writer implementation or repository-driven private save mutation.
