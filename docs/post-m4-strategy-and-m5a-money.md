# Post-M4 strategy and M5A money investigation — 2026-10-05

## Human authorization

> `AUTHORIZE POST-M4 NORTH STAR EXPANSION AND M5A MONEY INVESTIGATION`

This authorization adopts the post-M4 strategic expansion described below and authorizes **M5A Money investigation**. It does **not** authorize a money writer, private-save mutation by repository tooling, arbitrary save/build support, inventory writing, species editing, broader party-index support, public release, or any other later capability implementation.

GitHub `main` remains the only durable canonical authority. Fresh read at authorization start resolved `main` to `f1536450c94a5c5aa515013d51fa832a1261a7b7`, with M1–M4 complete for the bounded first slice and no later milestone previously adopted.

## Expanded North Star

Build an evidence-first local save editor for the owner's positively supported PokemonStart save lineage that can perform the **common practical edits the owner actually wants**, while retaining fail-closed provenance/capability gates, separate-output publication, independent verification, and a reliable recovery path.

The target practical capability set is, in priority order:

1. money editing;
2. inventory/item editing;
3. practical party-Pokemon editing, ultimately including species changes and the associated stat/state coupling that can be independently established;
4. future Pokédex editing if it can be given its own bounded semantics.

General event/story/quest flag editing is an explicit non-goal. PKHeX compatibility, generic CFRU support, arbitrary PokemonStart versions/builds, and feature-count parity are not goals by themselves.

The completed M4 markings editor remains a valid bounded first slice and safety foundation; the expanded North Star does not retroactively broaden M4 claims.

## Proposed milestone architecture now adopted

- **M5A — Money capability:** investigate representation, establish an exact private differential, prove one bounded money transformation, then only after separate evidence/adoption consider a reusable retained-lineage money FAMILY and UI exposure.
- **M5B — Inventory capability:** after M5A, characterize item-slot encoding, pocket/catalog semantics, encryption, quantity/add/remove behavior, and only evidence-proven safe pockets/actions. Key-item editing is not assumed safe and should be deferred unless separately justified.
- **M5C — Practical Pokemon editing:** first generalize already-proven or low-coupling attributes where possible, then coupled level/EXP/stat state, then species transformation with all required identity/stat/form/ability/move implications proven or explicitly bounded.
- **Future — Pokédex:** separately bounded seen/caught editing may be investigated later. This does not authorize a general flag editor.
- **Owner-use hardening / packaging:** perform only as needed while capabilities mature; broad polish or public distribution is not a prerequisite to each proof milestone.

Each capability remains independently gated. One successful transformation does not imply arbitrary values, other fields, other party indices, other save lineages, or other builds.

## M5A current status

**M5A MONEY — INVESTIGATION IN PROGRESS; WRITER NOT AUTHORIZED.**

### Fresh upstream/source findings

The project continues to pin the structural CFRU-JP source basis to public `kapibarasan000/CFRU-JP` commit `e24a16fe39e27ae162faf5b78596d1f3df18489d` unless a later canonical record explicitly updates that source basis.

At that commit:

- `include/global.h` places `SaveBlock1.money` at SaveBlock1 offset `0x0290` as `u32 money`.
- The same file places `SaveBlock2.encryptionKey` at SaveBlock2 offset `0xF20`.
- `src/save.c` maps logical section 0 to SaveBlock2 (`0xF24` bytes), then logical sections 1–4 to successive SaveBlock1 chunks; logical section 1 starts at SaveBlock1 offset `0` with size `0xFF0`. Therefore the source-derived candidate save location for the stored money word is logical section 1 offset `0x0290`, while the candidate key location is logical section 0 offset `0xF20`.
- CFRU-JP links the original FireRed `GetMoney`, `AddMoney`, and `RemoveMoney` routines and declares encrypted-data rekey helpers including `ApplyNewEncryptionKeyToAllEncryptedData`, `ApplyNewEncryptionKeyToBagItems`, `ApplyNewEncryptionKeyToWord`, and `ApplyNewEncryptionKeyToHword`.
- The CFRU-JP `bytereplacement` record explicitly contains `Increase Max Money to 9999999`.

For semantic corroboration only, public `pret/pokefirered` source at commit `037335f4c725d7c9aecdac87066f2002b4bd7e14` shows the corresponding FireRed logic:

- `GetMoney` returns `stored_word XOR encryptionKey`;
- `SetMoney` stores `encryptionKey XOR newValue`;
- encryption-key migration explicitly rekeys `money` with the word helper.

This is **upstream source evidence**, not yet a PokemonStart v0.15 private-save proof. The CFRU-JP 9,999,999 patch supports a candidate semantic range but does not by itself prove the exact PokemonStart build behavior for every value.

### Current source-derived hypothesis

For the retained PokemonStart v0.15 build/lineage, a candidate read rule is:

`money = LE32(active logical section 1 data at 0x0290) XOR LE32(active logical section 0 data at 0x0F20)`

A candidate write rule would encode a new money value by XOR with the same active SaveBlock2 key, mutate only the four-byte money word in logical section 1, and recompute only the required logical-section-1 checksum while preserving every other byte under the existing transaction envelope.

**This remains a hypothesis until independently reproduced on private PokemonStart saves. No writer authority follows from this formula yet.**

## Cheapest required private proof

The next uncertainty-reducing step is a controlled **read-only before/after differential**, produced by the game itself rather than by repository writer code.

Preferred canary:

1. keep an immutable copy of a positively identified retained-lineage save A;
2. record the displayed in-game money value for A;
3. in the same validated PokemonStart v0.15 build/environment, change **only money by a known amount** through ordinary gameplay/shop/debug-free game behavior if practical;
4. immediately perform one normal in-game save to produce B;
5. retain both A and B outside Git and provide them for read-only analysis together with the two displayed money values and the exact action used;
6. independently verify S0/slot/counter behavior, decode section-0 encryption keys, test the candidate XOR formula, distinguish the normal-save transition from the actual money semantic change, and confirm there is no unexplained stable payload difference relevant to the claimed field.

A small deterministic shop purchase is preferable to a complex gameplay sequence because it reduces unrelated state changes. If a purchase necessarily changes game statistics or runtime fields, those changes must be explained rather than ignored.

The private files, ROM, journal, and derived private hashes remain outside Git except for non-sensitive hashes/metadata that are deliberately adopted as evidence.

## M5A proof ladder

M5A must not jump directly from source layout to an unrestricted editor. The intended sequence is:

1. **Source characterization — current step.** Establish layout, encryption candidate, range candidate, checksum section, and explicit uncertainty.
2. **Private read-only differential.** Independently reproduce displayed money values from save bytes and isolate the money representation from ordinary save-transition noise.
3. **Exact bounded writer candidate — requires separate authorization after the differential.** One known input, one selected target value, exact allowed byte/checksum envelope, new-file output only, complete independent audit.
4. **Human game round trip.** Load the exact candidate, confirm displayed value/normal behavior, perform a normal save, and read-only audit the return.
5. **Reverse/repeated-use proof if justified.** Demonstrate that the capability survives the retained-lineage continuation model rather than remaining a one-shot hash vector.
6. **Reusable FAMILY adoption.** Only after range semantics, cross-hash behavior, negative tests, and representative game evidence justify it.
7. **UI integration.** Delivery layer only after the core capability is adopted.

## M5A success / exit criteria

M5A can be considered complete only when canonical evidence establishes, for the retained positively supported lineage/build/environment:

- the exact money decode/encode rule;
- the supported numeric range or explicitly narrower range;
- active logical section/key locations independent of physical section permutation;
- all checksum effects and complete allowed byte-diff envelope;
- source immutability and separate verified output;
- rejection of malformed, non-lineage, wrong-build/environment, stale-plan, invalid-range, and unsupported states;
- at least one representative game load/resave proving the edited value survives a normal game boundary;
- enough repeated-use evidence to distinguish a reusable FAMILY from a one-shot exact proof vector, if FAMILY support is claimed.

If the evidence only supports an exact bounded transformation, M5A may stop with that narrower result rather than overgeneralizing.

## Explicit non-goals during M5A

M5A does not authorize:

- inventory or key-item writes;
- species/form/ability/move/level editing;
- Pokédex or general flag editing;
- arbitrary/non-lineage saves;
- another PokemonStart build/version;
- broader Windows host/filesystem support;
- remote/public browser exposure;
- emulator live-save overwrite;
- public packaging/release guarantees;
- weakening S0/P/C, lineage, transaction, independent-audit, or recovery requirements.

## Authorization boundary

The present authorization covers this strategic expansion, this canonical planning/evidence record, and **read-only M5A investigation**. It does not authorize implementing or executing a money writer.

After the private differential is available and independently audited, a new decision surface must state the exact proposed M5A writer proof, evidence, allowed transformation, risks, output/recovery contract, and human-canary burden. Stop for fresh Human authorization before any writer implementation or private save mutation by the repository tooling.
