# E1 exact-v0.22 inventory research candidate

Disposition: **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE**.

Latest exact-ROM investigation: see
[e1-count-cache-exact-results.md](e1-count-cache-exact-results.md).
Sector30 `0x716` is a regular selected-classification menu count; an exact
custom partition means it is not universally the total occupied count.
That packet supersedes the unknown-field hypothesis below. E2 remains unstarted.

Update: Human T1/T2/T3 snapshots have now been verified. See
[e1-native-transition-results.md](e1-native-transition-results.md) for the
updated evidence/matrix and [e1-chatgpt-handoff.md](e1-chatgpt-handoff.md) for
the requested broader planning discussion. Statements below about missing
T1/T2/T3 and no newly performed gameplay describe the initial checkpoint.
E1 remains incomplete; no writer qualification is implied.

Canonical starting point: GitHub `main`
`785e113fa1885ac17e19da842a74740f62a8e789`, fetched afresh for Issue #20.
Candidate branch: `codex/e1-v022-inventory-model-qualification`.
This is implementation-context research, not independent review or adoption.
The exact packet-bearing HEAD/tree is recorded in the publication receipt.

## Result and controlling difference

The exact ROM contradicts the upstream-derived **450-slot** regular pocket.
Its installed descriptor uses **700** regular records and **72** berry records,
with a **32-byte gap between Key Items and Balls**. Using the readiness packet's
450/75/50/128/75 contiguous mapping would read the wrong bytes for every later
pocket. That packet explicitly called its mapping a candidate, not authority.
No canonical file or existing product writer was changed.

Supporting upstream sources were fetched afresh at pinned CFRU-JP commit
`e24a16fe39e27ae162faf5b78596d1f3df18489d`: [save implementation](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/save.c),
[bag implementation](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/item.c),
[hook entries](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/hooks),
and [character encoding](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/charmap.tbl).
These locate useful exact-ROM investigation targets; they are not a claim
that this upstream revision is the integrated PokemonStart source.

Added files:

- `pokemonstart_v022_inventory_model.py`: exact-ROM catalog extraction and
  generalized read-only decoder; no save-writing API.
- `pokemonstart_v022_inventory_audit.py`: separate read-only reconstruction of
  the RAM image, using the existing independent structural parser; imports
  neither the model nor a writer.
- `pokemonstart_v022_inventory_qualification.py`: repeatable private probe,
  emitting sanitized counts/hashes without private filenames or ROM bytes.
- `tests/test_v022_inventory_model.py`: synthetic record-boundary, corruption,
  holes, order, capacity, rotation and rejection tests.
- this record and `docs/e1-inventory-private-evidence.json`: sanitized evidence.

## Exact-build static corroboration

Exact ROM SHA-256:
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
Size: 33,554,432 bytes. The production decoder hashes the actual ROM bytes;
passing an asserted hash string cannot bypass this gate.

The initializer hook at `0x0809984C` branches to `0x090D39A4`, which copies
the 40-byte descriptor at `0x09490E68` into `0x020397D8`.
Private Thumb disassembly identified these values and uses; raw disassembly,
ROM bytes and extracted table data are excluded from Git. Code-region hashes
and ranges are in the JSON evidence; hashes fingerprint inspected ranges and
do not themselves prove code semantics.

| Pocket | Exact RAM | Exact capacity | Saved storage |
| --- | --- | --- | --- |
| Regular 0..324 | `0x0203BA98` | 325 records in first fragment | active section 13, `0xADC..0xFEF` |
| Regular 325..699 | continuation at `0x0203BFAC` | 375 records | global sector 30, `0x000..0x5DB` |
| Key Items | `0x0203C588` | 75 | sector 30, `0x5DC..0x707` |
| Non-pocket gap | `0x0203C6B4` | 32 bytes | sector 30, `0x708..0x727` |
| Balls | `0x0203C6D4` | 50 | sector 30, `0x728..0x7EF` |
| TM/HM | `0x0203C79C` | 128 | sector 30, `0x7F0..0x9EF` |
| Berries | `0x0203C99C` | 72 | sector 30, `0x9F0..0xB0F` |

The capacity is storage extent, not proof that all slots can be filled with
safe distinct items. Slot 449 remains a boundary test because the contract
requires it, but **699** is the exact regular-pocket last slot.

Exact save/load code confirms the parasite fragments:

| RAM start | Length | Save fragment |
| --- | --- | --- |
| `0x0203B0E8` | `0xCC` | section 0, `0xF24..0xFEF` |
| `0x0203B1B4` | `0x258` | section 4, `0xD98..0xFEF` |
| `0x0203B40C` | `0xBA0` | section 13, `0x450..0xFEF` |
| `0x0203BFAC` | `0xFF0` | global sector 30 payload |
| `0x0203CF9C` | `0xFF0` | global sector 31 payload |

`SaveParasite` is at `0x090EAD2C`; the inspected load path begins at
`0x090EAD8C` and the save path at `0x090EB168`. Logical sections use the active
slot's section IDs, not fixed physical sector numbers. Parasite tails are
outside section checksums. Extra sectors are shared across slots and have no
authenticated save counter or checksum in this model. The decoder never
combines them with the inactive slot or claims crash recovery/authentication
of their epoch. The 4 bytes at section offset `0xFF0..0xFF3` are not part of
the parasite; slot 325 starts in sector 30, not that padding.

An exact initializer call to `0x090CDFCC` tests signed halfword RAM
`0x0203B672`. If negative, `0x090CD770` substitutes a ten-slot regular bag and
zeros other pocket capacities. Its gameplay meaning is not guessed. Both
decoders reject this branch using the independently mapped saved marker
(section 13 `0x6B6`, reconstructed parasite `0x58A`). The four retained
snapshots have marker 0. This is not a claim that all other game modes are
qualified.

## Catalog derivation and policy

The exact item-name accessor at `0x090D29D4` indexes records by `item_id * 40`
and reads the pointer at ROM `0x080001C8`. It points to `0x095199C8`.
The exact sanitizer at `0x090D29C0` accepts IDs through 838; hence 839 records
including item 0. Metadata fields are name bytes 0..9, item ID at `0xA`,
importance at `0x14`, pocket at `0x16`, type at `0x17`. Stale upstream comments
about `0xE`/`0x1A` field offsets are not used as exact-build authority.

The catalog is decoded only in memory from the owned ROM. Japanese character
conversion was corroborated with pinned source `charmap.tbl`. Neither that
whole mapping file nor an extracted ROM table is distributed. The packet
records table hash/counts and necessary bounded semantics only.
The extractor excludes item 0 and invalid/placeholder entry 375. The remaining
837 entries pass its ID/name/pocket/importance checks. Metadata validity is
not a safety classification or writer authorization. Exact ID 533 decodes as
フシギバナイト, corroborating the preserved regular-pocket entry's identity.

Proposed initial ordinary selection is deliberately limited to recovery
medicine IDs 13..22, additionally requiring exact metadata pocket 1 and
importance 0. All Key Items, unknown IDs, placeholders, and items outside this
proposed set are excluded from the proposed editing surface. Existing entries
outside the set may be inspected; they confer no grant/remove authority.
This candidate supplies no writer, GUI expansion, or Give All. Safety policy
for a broader ordinary-item set and Give All remains unestablished.

## Quantity and operation findings

Exact `GetBagItemQuantity` at `0x080997A8` is a direct halfword read.
The setter at `0x080997C4` still XORs with the save key before storing. This
asymmetry is a concrete reason to exclude **every nonzero active key**, rather
than importing baseline FireRed's XOR model. Under key0, the observed record
is `u16 item_id, u16 quantity`.

Exact `CheckBagHasSpace`/`AddBagItem` contain the existing-stack bound 999.
The absent-item path takes the first item-ID-zero slot; it does not independently
enforce 999 on a new count. Therefore 1..999 is a conservative research audit
range, not a claim that all native paths enforce a universal maximum.
`RemoveBagItem` at `0x08099BE0` subtracts the count and zeroes the item ID when
the remaining count is zero, without shifting later records inside that
primitive. TM/HM/berry acquisition also has Key Item/container/flag side
effects in `AddBagItem`; no cross-pocket writer is authorized by simple record
existence.

The compaction hook at `0x08099F8C` targets `0x090D40D4`. That short function
uses the null/zero comparator at `0x090D2524`, without an auto-sort variable
lookup or anti-max-item code in those functions. Manual sorting code is also
present. Global absence of anti-cheat/custom item behavior is **not** proven.
The relation between removal, menu rebuild, possible sort state and the
persisted ordering of later occupied entries is not closed by the retained
last-slot native transitions. Merge ordering/timing and all relevant menu
callers were not fully qualified. This remaining writer semantic blocks E1
qualification and E2, even though the primitive's zeroing behavior is known.

## Private reproduction and independent audit

Re-read the three canonical native inventory snapshots plus R4 Cycle 2 return.
Their hashes and counters are in `e1-inventory-private-evidence.json`.
Counters are 7, 8, 9 and 10. Both independent reconstruction paths agree on all
decoded pocket records, holes, first-free positions and active epochs.
Occupied counts are regular 3/2/3/3, Key Items 11, Balls 1, TM/HM 0, Berries 1.
Balls decode item 4 x5; Berries decode item 142 x4. These provide fresh
non-regular-pocket corroboration without asking for repeated gameplay.
No occupied high regular slot or occupied TM/HM was present in these snapshots;
their extents are exact-ROM static findings plus synthetic boundary coverage.

ROM and all four save bytes match before and after the read-only probe. No
private outputs or game-state changes were made. Read-only decoding here is
an implementation audit; the agent did **not** perform the independent review.

## E1 exit criterion matrix

| Criterion | Status | Evidence / limit |
| --- | --- | --- |
| Actual exact ROM/profile gate | PASS | Hash actual input bytes; descriptor/table pointer checked |
| Exact scatter map and pocket extents | PASS | Installed descriptor, save/load code and private pocket records; upstream candidate corrected |
| Generalized read-only decoder/auditor | PASS | Two reconstruction methods across both storage fragments |
| Exact-ROM metadata catalog | PASS | 40-byte table, IDs 0..838; 837 retained entries; table hash recorded |
| Safe ordinary selection/exclusion | PASS | Explicit proposed medicines-only policy; no writer grants |
| key0 record representation | PASS | ROM getter/setter, canonical/native private snapshots |
| Full writer quantity range for proposed set | NOT ESTABLISHED | 999 existing-stack bound; only small native quantities reproduced |
| First-free insertion primitive | PASS | Exact ROM `AddBagItem`/first-free lookup plus canonical Antidote acquisition |
| Removal primitive | PASS | Exact ROM zeroing and canonical Antidote deletion |
| Middle removal, compaction timing and persistent order | NOT ESTABLISHED | Later-occupied native case absent; UI/sort call chain not fully qualified |
| Relevant custom/anti-cheat behavior across entire item flow | NOT ESTABLISHED | Compact/comparator lack the upstream optional paths; other code not exhaustively established |
| Checksums/global extra-sector behavior | PASS | Explicit unchecked storage and epoch limitation |
| Malformed/unsupported state handling | PASS | Reject profile/key/alternate bag/save epoch; malformed records report unsupported |
| Nonzero key bounded out | PASS | Both public read-only paths reject it |
| Boundary/rotation tests | PASS | Regular 0/324/325/449/699; all other starts/ends; 32-byte gap; rotated logical sections |
| Give All disabled | PASS | No writer or GUI exposure; flags false |

Record-level problems produce `state_supported: false` with reasons; they are
not silently skipped. Holes and native order are preserved in the report.
The research decoder also bounds out erased backups, counter wrap/nonordinary
epochs and empty Party states. It does not narrow the existing product APIs.

## Cheapest discriminating next proof

Use an immutable copy of a naturally progressed exact-v0.22 owner save with
the ordinary regular list containing Potion, preserved #533, then Antidote.
Retain snapshots privately; no ROM/save uploads or publications in Git.

1. **T1, middle/leading deletion:** retain a normal-save `pre` snapshot with
   Potion followed by occupied entries. Toss all Potion through the normal
   Bag UI, return to the world, perform normal SAVE, close/flush mGBA, retain
   `post-delete`. One deletion tests behavior with later occupied records.
2. **T2, absent ordinary acquisition:** from that returned state, purchase one
   Potion, return to the world, normal SAVE, close/flush, retain `post-acquire`.
   This distinguishes first-free restoration from compacted append/order.
3. **T3, different stack:** purchase two additional Antidotes while one already
   exists, normal SAVE, close/flush, retain `post-stack`. This avoids treating
   Potion alone as quantity generalization evidence.

If the current regular list differs, select a tossable recovery medicine with
later occupied entries and record that starting order instead of manufacturing
an editor input. Do not toss the preserved #533 or a Key Item. A manual-sort
snapshot is needed only if these results leave a sort-mode ambiguity. A
larger-quantity proof should be chosen only after the small transition matrix
and remaining exact menu/source analysis identify whether it is necessary.
No request to fill hundreds of slots is needed.

## Verification and non-claims

Focused tests: **9 passed**. Full `.venv` unittest discovery: **238 run,
223 passed, 15 skipped**, no failures. AST parse: **104 Python files passed**;
all four new Python files also passed compilation. Candidate path/protected
suffix scan found no private paths or protected assets in the additions;
Gitleaks scanned candidate additions with redacted output and found no leaks.
Private probe: four snapshots, equal decodes, immutable inputs. Candidate
identity and publication status are recorded in the publication receipt. The evidence
generator is rerunnable with `--rom LOCAL_ROM --save LOCAL_SAVE` (repeat
`--save` for additional snapshots), and returns only sanitized evidence.

No E1 qualification, E2 writer, generalized GUI edits, new game round trip,
capacity-filling proof, safe Give All, global anti-cheat absence, Stable
promotion, main merge, release, or independent-review disposition is claimed.
Source/private inputs are immutable. Protected assets and private paths are
absent from this candidate's tracked additions.
