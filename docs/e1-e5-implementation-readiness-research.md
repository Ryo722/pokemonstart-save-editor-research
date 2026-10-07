# E1-E5 implementation-readiness research packet

Date: 2026-10-07

Canonical base: `2d9e874782337e257e392fc8ee9a98d85214bd55`.

Purpose: remove research/planning ambiguity before Codex implementation. This packet does **not** add writer capability.

## Evidence classes

- **Canonical / independently reproduced:** evidence already adopted in this repository for exact PokemonStart v0.22.
- **Local private-input verification:** exact private ROM/save observations already recorded canonically; protected bytes remain outside Git.
- **Upstream source evidence:** source from pinned CFRU-JP or baseline FireRed repositories. It is supporting evidence, not automatically the exact integrated PokemonStart revision.
- **Derived mapping:** arithmetic consequence of source constants combined with canonical exact-v0.22 observations.
- **Hypothesis / exact-build verification required:** plausible but must not be promoted until checked against the exact v0.22 ROM/save.

## 1. Current exact-v0.22 inventory facts

Canonical evidence already establishes:

- exact v0.22 ROM SHA-256 `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`;
- active save layout and verifier behavior are established;
- regular-item records observed at logical section 13 offset `0xADC`;
- each observed record is `u16 item_id, u16 quantity`;
- exact-v0.22 live RAM corroborated regular-items slot 0 at `0x0203BA98`;
- Potion is item 13; Antidote is item 14;
- normal-game snapshots demonstrated Potion quantity change and Antidote deletion/reacquisition;
- Antidote deletion zeroed its slot in the observed three-entry case;
- section 13's checksum-covered length is `0x450`; the observed regular-item bytes at `0xADC` are outside that checksum-covered prefix;
- current owner saves observed in this line use encryption key 0;
- current product support remains deliberately bounded to Potion quantity 1..3 and one shape-gated Antidote slot.

These facts control over broader upstream assumptions.

## 2. Pinned CFRU-JP source findings

Upstream source examined at CFRU-JP commit:

`e24a16fe39e27ae162faf5b78596d1f3df18489d`

This commit was already the pinned upstream source in prior canonical v0.22 work, but the repository does **not** claim it is the exact integrated PokemonStart source revision.

### 2.1 Bag record and pocket model

Pinned source defines:

- `struct ItemSlot { u16 itemId; u16 quantity; }`;
- item metadata includes `itemId`, `importance`, `pocket`, type and other fields;
- `struct BagPocket { struct ItemSlot *itemSlots; u16 capacity; }`.

The expanded bag implementation defines:

- regular items RAM: `0x0203BA98`;
- regular capacity: 450;
- key-item capacity: 75;
- Poké Ball capacity: 50;
- TM/HM capacity: `NUM_TMSHMS`;
- berry capacity: 75.

Pinned `src/config.h` defines `NUM_TMS=120` and `NUM_HMS=8`, hence upstream `NUM_TMSHMS=128`.

The exact-v0.22 live RAM address already recorded canonically for regular items is **the same `0x0203BA98` address**. This is strong compatibility evidence, but Codex must still verify the complete mapping against the exact private ROM/save before generalized writes.

### 2.2 SaveParasite serialization mapping

Pinned CFRU-JP source defines:

- `SAVE_BLOCK_PARASITE = 0x0203B0E8`;
- `PARASITE_SIZE = 0xEC4`;
- parasite pieces of `0xCC`, `0x258`, and `0xBA0`;
- those pieces are written into the unused tails of logical sections 0, 4 and 13 respectively;
- logical section 13's parasite piece begins at save-data offset `0x450`;
- RAM immediately following the parasite is serialized to extra sectors 30 and 31.

The regular-items RAM base is `0x9B0` bytes after `SAVE_BLOCK_PARASITE`.
The third parasite piece begins at parasite offset `0x324`.
Therefore regular items begin `0x68C` bytes into the third parasite piece:

`0x450 + 0x68C = 0xADC`.

That exactly predicts the independently observed exact-v0.22 regular-item save offset.

### 2.3 Derived scatter map candidate

If the exact v0.22 ROM preserves this pinned layout, the expected serialization is:

| Surface | Expected location | Capacity / extent |
| --- | --- | --- |
| regular item slots 0..324 | logical section 13, `0xADC + 4*slot` | 325 slots |
| regular item slots 325..449 | sector 30, `0x000 + 4*(slot-325)` | 125 slots |
| key items | sector 30, `0x1F4` | 75 slots |
| Poké Balls | sector 30, `0x320` | 50 slots |
| TM/HM | sector 30, `0x3E8` | 128 slots in pinned config |
| berries | sector 30, `0x5E8` | 75 slots |
| end of those five pocket arrays | sector 30, `0x714` | derived |

This table is a **derived mapping candidate**, not writer authority yet. Codex must independently verify it against exact-v0.22 ROM addresses and private save/runtime state before E1 can pass.

### 2.4 Ordering / holes

Pinned CFRU-JP source's `CompactItemsInBagPocket` sorts null/zero-quantity entries toward the back. It can optionally apply other regular-pocket sort modes when `VAR_AUTO_SORT_BAG_ITEMS` is compiled/enabled.

`StoreBagItemCount` has explicit handling for a gap in the first three pockets.

Implications:

- the observed Antidote zero-in-place snapshot does **not** prove that persistent middle holes are the general normal state;
- E1 must distinguish ordinary removal semantics from subsequent bag compaction/sort behavior;
- exact PokemonStart compile/config state for auto-sort must be checked rather than inferred.

### 2.5 Quantity and encryption baseline

Baseline FireRed source shows:

- bag quantities are XORed with the lower 16 bits of the save encryption key;
- existing stacks cap at 999 in `CheckBagHasSpace` / `AddBagItem`;
- `RemoveBagItem` zeroes item ID when quantity reaches zero;
- new items are placed in the first empty slot.

CFRU-JP continues to call/hook the corresponding BPRJ bag functions, but this baseline behavior is **not sufficient alone** to qualify exact v0.22.

For current E1:
- key0 behavior is already reproduced on exact v0.22;
- nonzero-key writes may remain fail-closed unless exact-v0.22 evidence makes support cheap;
- quantity 999 is a strong source-backed candidate maximum, but Codex must corroborate the exact ROM implementation before exposing it as product authority.

## 3. Exact-ROM item catalog route

Pinned CFRU-JP source exposes an item table pointer through the ROM and defines item metadata containing:

- encoded name;
- item ID;
- price;
- hold effect;
- importance;
- pocket;
- type;
- secondary ID.

E1 should prefer extracting the catalog from the **exact private v0.22 ROM**, not hard-coding a current upstream header.

Required catalog classification:

- exact item ID;
- decoded display name;
- pocket;
- importance;
- whether metadata is structurally valid;
- whether the entry is safe for the vNext ordinary-item surface.

Do not equate `pocket != key-items` with automatically safe. The Give-All allowlist must exclude unverified story/event/special entries even if their storage pocket is ordinary.

Upstream constants corroborate item 13 = Potion and item 14 = Antidote. Upstream ID 533 (`0x215`) is named Venusaurite, but the canonical save evidence intentionally called it “item #533”; exact-ROM decoding must establish its exact v0.22 identity before the product names it.

## 4. E1 uncertainty register

E1 is not complete until these are resolved or explicitly bounded out:

1. exact-v0.22 confirmation of the complete scatter map across section 13 and sector 30;
2. exact pocket capacities and TM/HM count actually compiled into v0.22;
3. exact item metadata table and safe ordinary-item catalog;
4. whether regular-pocket auto-sort is compiled/enabled and how normal save/UI operations affect order;
5. insertion into a nontrivial pocket with later occupied records;
6. removal from a middle occupied slot with later entries;
7. compaction timing and whether an editor should compact immediately or preserve first-empty semantics;
8. exact supported quantity maximum;
9. exact handling of key0; nonzero key may remain unsupported;
10. independent decoder/auditor coverage for all bytes an E2 writer would touch;
11. whether Give All can fit within proven capacities without including unsafe entries.

## 5. Minimal native-transition evidence matrix

Avoid serial “one item at a time” proof accumulation. Use a small set of transitions selected to distinguish the model.

Existing canonical transitions already count as evidence:

- Potion quantity 1 -> 2 under normal save history;
- editor Potion quantity 2 -> 3 live exact-v0.22 confirmation;
- Antidote native deletion/save;
- Antidote native repurchase/save;
- Antidote exact editor insert/remove byte behavior.

Only add new Human gameplay transitions when static/ROM evidence cannot distinguish a behavior.

Recommended new matrix:

| ID | Transition | What it resolves |
| --- | --- | --- |
| T1 | remove/toss/use-to-zero an ordinary item that has at least one occupied entry after it, then normal save | middle-hole vs compaction/order semantics |
| T2 | acquire an absent ordinary item while several entries already exist, then normal save | first-free/insertion/order behavior |
| T3 | increase an existing materially different ordinary item and save | confirms quantity behavior is not Potion-specific |
| T4 | if the exact build exposes a bag sort mode, perform one sort and save; otherwise prove sort mode absent/disabled statically | auto-sort behavior |
| T5 | optional only if still needed: acquire/use a Poké Ball or other different safe pocket entry | cross-pocket serialization corroboration |

Do **not** fill hundreds of slots just to prove nominal capacity. Prefer exact-ROM/source layout plus boundary-safe synthetic/read-only auditing, then use only as much native evidence as is needed to reject plausible alternate models.

Private snapshots should be immutable copies outside Git. Git records hashes, counters, decoded semantics and bounded diff metadata only.

## 6. E1 exit criteria

E1 may be declared qualified when all are true:

- exact ROM/profile gate is retained;
- exact-v0.22 private evidence corroborates the pocket serialization mapping used by the decoder;
- a read-only generalized decoder/auditor can reconstruct all supported pocket entries across section 13 / sector 30 boundaries;
- exact item catalog extraction is from the exact ROM/profile, not a guessed static list;
- safe ordinary-item inclusion/exclusion policy is explicit;
- quantity representation/range is established for supported pockets;
- insertion, removal, empty-slot and order/compaction behavior are explained sufficiently for an E2 writer;
- checksums / extra-sector behavior are explicit;
- malformed/ambiguous/incompatible state fails closed;
- nonzero-key state is either qualified or explicitly unsupported;
- independent tests cover boundary slots including the section13 -> sector30 regular-pocket split;
- Give All remains disabled unless its catalog and capacity prerequisites separately pass.

## 7. E2 implementation contract preview

Once E1 passes, E2 writer/UI authority may cover only the E1-qualified set:

- inspect supported pockets;
- add supported ordinary item if absent;
- set/change quantity in the qualified range;
- remove supported ordinary item;
- compact/order exactly as the established model requires;
- preserve unrelated bytes;
- independently re-decode and verify postconditions;
- create a separate output only.

E2 must not infer Key Item/event/story authority from the existence of an item table entry.

## 8. E3/E4 Pokémon source-readiness findings

The same pinned CFRU-JP source defines a **direct 100-byte Party Pokémon struct** whose field order matches the repository's current exact-v0.22 parser model. Important source fields include:

- personality and OT ID;
- nickname / nature mint / hyper training / tera type / language / sanity;
- OT name / markings / backup species;
- species / held item / EXP / PP bonuses / friendship / Poké Ball;
- four moves and four PP values;
- six EVs;
- met/pokerus fields;
- hidden-ability bit;
- six packed IVs, egg bit and ability selector;
- condition, level, HP/max HP and five other cached battle stats.

The struct ends at 100 bytes.

Pinned source also exposes or uses:

- `CreateMon`, `CreateMonWithNature`, `CreateMonWithIVsPersonality`;
- `GetMonData` / `SetMonData`;
- `CalculateMonStats` and CFRU's newer stat path;
- species base-stat tables;
- experience tables indexed by species growth rate;
- move PP data;
- ability resolution, including hidden ability and alternate ability selector.

Canonical exact-v0.22 evidence already shows:
- complete 100-byte Party records match live RAM;
- multiple direct fields are decoded correctly;
- one exact complete game-generated Rattata record can be appended and survives normal gameplay/save.

This makes E3/E4 primarily an **exact-build table/coupling qualification problem**, not a mystery save-layout problem.

Before E3/E4 implementation, Codex should derive from the exact ROM/profile:

- species table / base stats / growth rate / abilities;
- experience thresholds;
- move table / base PP;
- species names and move names for GUI;
- exact stat formula behavior used by this build, including the previously unresolved level-6 discrepancy;
- nature/nature-mint interaction;
- ability selector + hidden-ability semantics;
- default/required values for creation fields not exposed by the user.

Creation should use a deterministic safe constructor policy. Do not generate arbitrary PID/shiny/OT complexity unless needed for a valid ordinary Pokémon. Preserving owner OT identity and selecting a deterministic non-shiny personality is preferable if source evidence supports it.

## 9. E3/E4 acceptance shape

E3 representative composed edit should include materially different species/levels and at least:
- species or level/EXP;
- IV/EV;
- a move/PP;
- friendship;
- held item or ability when qualified;
- cached stats.

E4 must create at least two materially different Pokémon/parameter sets in empty Party slots and demonstrate:
- correct GUI summary;
- healing;
- battle/use;
- normal save;
- returned-save verification;
- later re-open/edit eligibility.

Party-full state must fail closed until Box support is separately authorized.

## 10. E5 UX contract

Normal UI should be:

- Party slots 1..6 visible;
- click a member -> Main / Stats / Moves editor;
- empty eligible slot -> Create Pokémon;
- Items pocket/list view with Item + Quantity, Add, Remove;
- Trainer view with Money;
- semantic Preview;
- Verify;
- Export separate save.

Research internals (hashes, offsets, section IDs, checksums) belong under Advanced diagnostics only.

Unsupported controls should be read-only/disabled with a concrete reason rather than silently hidden.

## 11. Scope guard

This research packet does not authorize:
- Box writing;
- Pokédex/story/event/quest/RTC mutation;
- public release;
- another PokemonStart version;
- unsafe all-items behavior;
- protected-data publication.

Material writer expansion remains independently reviewable before canonical merge.
