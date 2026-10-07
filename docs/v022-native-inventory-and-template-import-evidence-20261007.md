# Exact v0.22 inventory and game-generated template evidence

All source `.sav` files and the ROM remain under `PokemonStart-private`. This
document records only decoded semantics, hashes, and byte-envelope metadata.
The disposable import candidate is `/private/tmp/pokemonstart-rattata-template-import.sav`;
it is not tracked.

## Inventory deletion and reinsertion

The three snapshots verify as consecutive normal saves with active counters
7, 8, and 9. Every logical section rotated by one physical sector each time.
Across the active logical section 13, the ordinary item records at offset
`0xADC` are little-endian `u16 item_id, u16 quantity`:

| Snapshot | Ordered observed records |
| --- | --- |
| pre-delete | `(13,3), (533,1), (14,1), (0,0)` |
| post-delete | `(13,3), (533,1), (0,0), (0,0)` |
| post-insert | `(13,3), (533,1), (14,1), (0,0)` |

Potion is item 13 x3, the preserved item is ID 533 x1, and Antidote is item
14 x1. The Antidote record was zeroed in place. There was no later occupied
record in these snapshots, so compaction/order behavior for later entries is
not established. The subsequent shop purchase put Antidote back at slot 2,
the same location.

Logical section 13's checksum-covered payload ends at `0x450`; the records at
`0xADC` are outside it. The stored checksum stayed unchanged through deletion
and reinsertion, and the repository verifier accepted each save. Inventory
changes also did not change Money during deletion; the purchase changed the
Money bytes as expected for a shop transaction. Normal-save rotation, counter
metadata, saved-game statistic, play time, and other section 1/2 state changed
between snapshots. These are separate game-save effects and must not be
mistaken for inventory bytes. The purchase also changed unrelated section 1/2
bytes whose field semantics are not qualified here.

This supports bounded reusable primitives for this exact observed bag shape:
remove `(14,1)` from slot 2 by zeroing its four bytes, and insert `(14,1)` into
slot 2 only when the first two records match and the remaining observed tail
is zero. It does not qualify arbitrary item IDs, quantities, pockets,
capacity, Give All, nor behavior when later slots are occupied.

## Native Pokémon acquisition differential

The pre-acquisition save is SHA-256
`935f7bd8061f43569316239c2ab1bfcb7573fbc84601dffc823e0493bba38985`
(counter 9, Party count 4). The post-acquisition save is SHA-256
`c129892cd442fba6becd32db6dcb3061c9f8df9ea3d4550f53dff106b9abfbee`
(counter 10, Party count 5). The active save slot rotated and every logical
section moved by one physical sector.

Party[4] is a game-generated Rattata: species 19, level 3, EXP 27, friendship
50, ball 3, held item 0, personality `0xECC1032A`, OT ID `0x661C3CAC`, moves
33/39, PP 35/28, IVs 30/30/9/18/31/27, all EVs zero, and HP 3/15. Its exact
100-byte record hash is
`74d64c9dfbf4905bb0ca2abd7047d9834cb5b3bc8822cf95d538bba80da673f3`.

The capture save also changed existing Party[0] (EXP 151→172, PP for move 1
35→33, and one additional EV), along with many bytes in logical sections
0/1/2/4 and CFRU extended section 13. Regular inventory records remained
unchanged. The repository has no exact-v0.22 field map that safely attributes
those other changes to Pokédex, battle, event, or extended-state semantics;
they must be preserved from the pre-acquisition save, not copied from the
capture save. This differential does not prove no battle item or other
capture side effect exists outside the decoded ordinary-item prefix.

## Exact-record template-import candidate

The candidate writer accepts only the exact pre-acquisition save hash and the
exact Rattata record hash. It copies that record unchanged to the first
unoccupied Party slot, changes Party count 4→5, and recalculates the active
logical section 1 checksum. No other state is copied from the post-capture
save. The candidate verifier accepted it. An independent expected-byte
construction compared equal; all changed bytes were confined to the count,
100-byte destination record, and two checksum bytes (47 changed bytes in
this instance). Every byte outside that envelope is identical to the
pre-acquisition save.

This is a template-import proof only. It does not establish arbitrary record
synthesis, arbitrary species, Pokédex consistency, or that the game will
accept the output. The next Human action is to load the disposable candidate
with the exact v0.22 ROM, inspect Party[5]'s summary and moves, enter one safe
battle to confirm it can participate, then perform a normal in-game SAVE and
close/flush mGBA. Preserve the returned save separately for structural
analysis. Do not use it as a live save.

A local exact-ROM method to force a wild encounter species has not been
derived. No known FireRed cheat address or downloaded code is evidence for
this patched ROM. The practical next specimen after this import check should
be a second ordinary game-native capture of a different species. Static
ROM-backed encounter-table/runtime analysis can follow from a disposable ROM
copy if a higher-diversity specimen is still needed.

## R4 position

Human-attested Cycle 1 exact-v0.22 load and normal SAVE succeeded. The
returned save passed `check-return`, retained requested semantics, advanced
counter 6→7, and remained eligible. Normal gameplay produced a new save hash;
`check-progress` accepted it as a new reusable input, and the progressed save
produced a Cycle 2 transaction. Cycle 2 game round trip remains outstanding,
so R4 is not complete.
