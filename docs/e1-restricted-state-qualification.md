# E1 restricted-state qualification for the E2 candidate

Disposition: **E1_MODEL_QUALIFIED_FOR_E2_CANDIDATE**.
Canonical base freshly fetched: `785e113fa1885ac17e19da842a74740f62a8e789`.
Input PR #21 HEAD: `e8ec73ae547f6860a20f6adbab4f0a4dd87b830f`, tree
`63f944be20da099782e7539be0cf9fa2a99ce40b`.
This is candidate qualification in the implementation context, not adoption
or independent review. The preceding stop records remain historical evidence.

## Restricted contract

Actual exact ROM bytes must pass the profile hash, descriptor and catalog
checks. Both independently implemented read-only gates require normal
consecutive save epochs, key0, ordinary bag marker, selector flag clear,
all occupied regular entries classification zero, valid unique IDs,
quantities 1..999, compact occupied prefix and zero records afterward.
The persisted three menu counts must match occupied regular/Key/Ball counts;
Key/Ball lists must be compact and retain a free slot. Every other state is
unsupported. Empty regular pockets are eligible only with selector clear
and regular count zero. Eligibility uses save + ROM, never transient RAM.

## Exact relevant topology and conclusions

The installed classifier at `0x090B81F0` is a binary integer-ID classifier.
It is neither a pocket classification nor a catalog safety classification.
Its nonzero branches are independently transcribed in both read-only gates.
Isolated execution of the actual Thumb function for all IDs 0..838 agreed
with the production predicate. This caught and corrected a transcription
omission for ID 836 before any writer implementation.

The regular helper `0x090B8274` visits exactly 700 records, partitions matching
records then nonmatching records, copies complete records and zeros the tail.
Its selected count is stored by `0x090D3D74` at `0x0203C6C2` (sector30+0x716).
With selector zero and all occupied classifications zero, the first traversal
copies every occupied record in order and the second copies none. Thus both
order and complete records are preserved. Empty input returns zero. Allocation
failure instead counts the prefix without partitioning; a compact input gives
the same count/order in either branch. These results also hold for one item.

The exact classifier/partition was additionally executed in isolation for
occupied counts 0/1/3/324/325/326/699/700 with allocation success and failure.
All 16 cases returned occupied count and preserved the complete regular image.
Allocator, FlagGet, memcpy and free were intercepted with their ordinary
contracts. This is isolated function evidence, not emulator gameplay or proof
of arbitrary runtime frames. The diagnostic JIT required host execution;
no game was launched or private save changed.

Relevant selector literals lead to functions `0x090B8164`, `0x090B8198`,
`0x090B8260`, `0x090B8274` and `0x090B83F4`. The first two set flag 0x12EB
from category-selection callbacks; `0x090B8260` and the partition read it;
`0x090B83F4` clears it and resets regular cursor positions. Bag-entry support
at `0x090B8440` first clears it, then scans for nonzero-classification records
before offering its separate category path. With all classifications zero
(or an empty pocket), that scan cannot enable the category branch. Explicit
selection in another game state may set it; any returned save with it set is
rejected. The writer never changes the flag.

Exact FlagGet address-resolution hooks reach `0x090EB4F0`. Flag 0x12EB maps
to RAM `0x0203B225`, bit3, hence active section4+0xE09. The relevant writes
are through FlagSet/FlagClear; raw selector state is serialized in the
parasite. SaveParasite `0x090EAD2C` copies section tails, load `0x090EAD8C`
restores them and extra-sector payloads, and the save path `0x090EB168`
serializes them. No transform or automatic selected-count recomputation occurs
inside those serialization copies. A stale cache therefore is not accepted
on the assumption that future menu opening will repair it.

The count hook `0x081098C0` -> `0x09036518` -> `0x090D3D74` recomputes on menu
rebuild. Readers `0x090D3E28`/`0x090D3E40`, cursor adjustment `0x090D3A30`,
and list builder `0x090D43A8` consume halfword counts. For regular items the
list builder starts at the installed regular pointer, advances four bytes
per entry and associates list index i with physical record i. Cancel is a
separate terminal entry, including when count is zero. ID and quantity
accessors `0x0809A1A0`/`0x0809A1BC` use the same pointer plus index*4.
There is no selected-to-unselected offset translation on this neutral prefix.

Removal primitive `0x08099BE0` decrements and zeros an exhausted record.
The compact hook `0x08099F8C` -> `0x090D40D4` uses comparator `0x090D2524`
and the installed stable merge routine. Equal occupied records choose the
left merge input, preserving relative order; zero records move to the end.
Native T1 corroborates the stable persisted result. Addition `0x08099A8C`
uses first free for an absent regular item; T2 corroborates append to the
compact prefix. T3 corroborates existing-stack update without reorder.
Exact section13/sector30 serialization continues at slot325; no contiguous
file-array assumption is made.

Manual sort `0x090D4060` selects comparator functions at `0x090D2408`,
`0x090D2480`, `0x090D24CC`, `0x090D24F8`. Those compare name/type/quantity
and move complete records through merge; they do not set the selector or
rewrite positive quantities. Their input order is accepted as the saved
order; the editor does not request sorting. The ordinary compact hook uses
only the null comparator, with no persisted auto-sort selector lookup.
The null comparator's full body has no task-creation/wipe call: the pinned
optional ANTI_MAX_ITEM_CHEAT injection is absent from this installed hook.
Relevant add/remove/get/set and inspected menu/count/sort paths contain no
quantity-dependent regular/ball/berry wipe dispatch. This is a bounded hook
and function-topology conclusion, not global absence of custom game code.
The alternate initializer `0x090CDFCC` -> `0x090CD770` is excluded by its saved
negative signed marker at section13+0x6B6. Later gameplay that changes a
capability predicate is unsupported on reopening rather than repaired.

## Quantity and medicine policy

Exact halfword reader `0x080997A8`, key0 setter `0x080997C4`, add/space bounds
999 and unsigned remove arithmetic justify **1..999**. The bag row drawing
path `0x08109150` reads a halfword through `0x0809A1BC` and renders three
decimal digits at `0x081091E8`; toss quantity also renders three digits.
A medicine's ordinary use consumes one via the same remove primitive; its
medicine callback `0x090E6818` reaches RemoveBagItem through its installed
callback pointer after applying the medicine effect. Quantity is not
reinterpreted as a story/event parameter. Zero is explicit removal only.

Each exact catalog entry 13..22 has matching ID, regular pocket, importance0,
classification0, type1, field callback `0x080A29B5`, battle callback
`0x080A327D` and battle usage1. The common medicine flow applies recovery/status
item effects to Party and consumes a single item; these entries do not select
the TM/berry/container acquisition or special flag branches in AddBagItem.
The inspected medicine path is the same recovery/status dispatch, not a
Key/story handler. The product allowlist is these ten recovery medicines;
all other entries remain read-only, even classification-zero Venusaurite.
Names are decoded from the actual ROM at runtime, never supplied by upstream
constants. Catalog metadata and callback shape are checked before exposure.

Isolated exact Add/Get/Remove ran for all ten medicines at quantities 1,3,99,
999 (40 cases): direct quantity read agreed, removal exhausted the record,
and addition reaching 1000 on an existing stack was rejected without change.
The absent-item primitive itself does not enforce 999: the editor must enforce
that bound before either add or set. No Human 999-item experiment is required.
These probes do not replace the pending combined GUI/game normal-SAVE gate.

## Persisted writer policy

Set: change only the existing supported quantity; preserve count and order.
Add: append absent supported medicine at first free after the compact prefix.
Remove: shift all later complete records left, preserving exact bytes/order;
zero the vacated tail. Recompute only the regular selected count at sector30
0x716..0x717 after add/remove. Under this predicate it equals prefix length.
Key/Ball counts and the selector flag are preserved. Other pockets, Party,
Money, inactive slot, footer and all unrelated bytes remain unchanged.
All affected regular record addresses use the qualified scatter map.
No checksum update is needed in unchecked regular tails/sector30. These extra
sectors are shared and unauthenticated: no crash-recovery guarantee is implied.

## Rebuilt E1 gates

| Gate | Status | Bounded evidence |
| --- | --- | --- |
| Profile | PASS | Fresh actual ROM hash, descriptor and table pointer |
| Storage/scatter | PASS | Exact serialization paths, private reconstruction and boundary tests |
| Catalog | PASS | Fresh exact extraction plus bounded metadata/callback policy |
| Classification | PASS | Exact branches; all839 isolated results; neutral predicate |
| Quantity | PASS | Exact reader/display/add/remove; 40 isolated medicine cases |
| Insertion/update/removal | PASS | Exact primitives plus T1/T2/T3, constrained persisted policy |
| Compact/order | PASS | Stable merge and neutral partition, including empty and allocation failure |
| Derived/menu coupling | PASS | Serialize regular selected count explicitly; reject inconsistent input |
| Relevant custom/sort | PASS within restriction | Explicit selector paths; alternate bag rejected; bounded installed comparator topology |
| Fail-closed gates | PASS | Separate model and RAM-auditor predicates; adversarial tests |
| Independent audit | PASS | Fresh four-snapshot equality for both restricted gates |
| Boundary behavior | PASS | Exact split plus focused 0/324/325/449/699 read tests; isolated counts near split |
| Preservation model | PASS | Scatter envelope + complete-record shifts, unchecked checksum behavior |
| Give All | PASS | Disabled; no arbitrary item/pocket authority |

At this internal gate, current focused tests: **13 passed**. Exact private
snapshots all pass restricted predicates with equal count arrays. E2 output
verification, GUI equality and Human acceptance are subsequent gates, not
asserted by this E1 model decision. Complete E2 checks will be rerun after
implementation changes. No main merge, independent review or adoption.
