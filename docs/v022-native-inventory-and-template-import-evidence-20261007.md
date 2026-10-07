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
save. The repository verifier and independent complete-byte construction
accepted the output. The 47 changed bytes are confined to the count, 100-byte
destination record and two checksum bytes; every byte outside that envelope is
identical to the pre-acquisition save.

### Disposition: GAME-ACCEPTED / NORMAL-SAVE-ACCEPTED

### Human game proof and returned-save verification

The Human loaded the exact candidate in exact v0.22. Party slot 5 displayed
the expected Lv3 Rattata; its summary and moves opened normally. The Rattata was
healed at a Pokémon Center, entered a safe battle, performed an action, and the
battle completed. A normal in-game SAVE succeeded and mGBA was closed/flushed.
These observations are Human gameplay attestation, separate from machine
verification.

Returned snapshot SHA-256 is
`256bf24dd9d3c2d6601d5203f56ff8b2f9ef4d59c5d8114f684e81be69dccdbe`.
The repository verifier accepted it at active counter 10 with Party count 5.
Party[4] remained species 19, level 3, EXP 27, friendship 50, moves 33/39,
IVs 30/30/9/18/31/27 and zero EVs. PP and HP reflect ordinary healing/battle
activity. This is machine verification of the returned save, separate from
Human observation of the battle and normal SAVE.

Supported conclusion: a complete valid game-generated 100-byte Pokémon Party
record can be imported into an empty Party slot with the count change and
required checksum update, without copying unrelated native capture/Pokédex/
battle/event state, and exact v0.22 can load, display, heal, battle with and
normally save that imported Pokémon.

This remains one exact-record template-import proof. It does not establish
arbitrary Pokémon synthesis, arbitrary species construction, automatic
Pokédex consistency, Box creation, legality generation or generic Pokémon
constructors. The operation remains experimental evidence and is not exposed
as a general GUI feature.

A local exact-ROM method to force a wild encounter species has not been
derived. No known FireRed cheat address or downloaded code is evidence for
this patched ROM. The practical next specimen after this import check should
be a second ordinary game-native capture of a different species. Static
ROM-backed encounter-table/runtime analysis can follow from a disposable ROM
copy if a higher-diversity specimen is still needed.

## R4 disposition

The R4 sequence used the actual product GUI twice. Cycle 1 began from a
previously unseen save SHA, was loaded in exact v0.22 and normally saved. The
returned save passed the acceptance harness, retained requested semantics,
advanced counter 6→7 and remained eligible. Human gameplay then removed the
last Antidote through the normal Inventory UI, normally saved, purchased one
Antidote, normally saved again and closed/flushed the emulator. The resulting
new SHA advanced the counter 7→9, qualified under the candidate predicates and
produced the Cycle 2 GUI transaction.

Cycle 2's exact GUI output loaded in exact v0.22. The Human observed Money
7,654,321, Potion x2 and a normal Party, then completed a normal SAVE and
closed/flushed mGBA. The returned snapshot SHA is
`606af61f976b0634d6eaf11e58bf3b9693345120e34b6d998631e068ca77d9ea`.
Independent harness execution confirmed counter 9→10, preserved the previous
active slot, retained Money/Friendship/Potion semantics and qualified the
returned save for another edit. The live disposable save and frozen snapshot
had identical SHA after mGBA fully exited.

The harness deliberately continues to report
`STRUCTURAL_ROUNDTRIP_PASS_HUMAN_GAMEPLAY_ATTESTATION_REQUIRED` and
`r4_complete: false`: it cannot attest Human interaction. Combined machine,
private-input and separately recorded Human evidence closes R4. The exact
Rattata template-import experiment is a separate branch from the Cycle 2 source
and does not contribute to the two-cycle acceptance sequence.
