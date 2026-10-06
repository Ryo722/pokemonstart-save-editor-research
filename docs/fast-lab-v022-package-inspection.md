# Fast Lab v0.22 package recovery and compatibility

Frozen subject: `onikoro334274-cell/PokemonStart`, commit
`ddd054d46fc1bd0555badf738572620b1ee4670d`, file
`PokemonStart_v0.22.pks` (12,196,990 bytes; Git blob SHA-1
`95c34216bdab85a53ab39c170550f8680fcc7a00`; private SHA-256
`d22bc25d7427899e8d0b2e29e7fd6b604602781167b78cfa8a90c8a2da9e4060`).

## Private input inventory highlights

- `Pocket Monsters - FireRed (Japan).gba`: 16,777,216 bytes, SHA-256
  `1e4af44b0c75cc8649bfb8649dc4ae5850bf5358bd6b9cd0bf779c99f9db1486`, CRC32
  `3B2056E9`, GBA title `POKEMON FIRE`, game code `BPRJ`.
- `PokemonStart_v0.15.gba`: 33,554,432 bytes, SHA-256
  `48ecc0ef2df7fe9bbe389f0adbf7e277696a461ec631c65bcdf750898e4e12`, CRC32
  `C8039921`. It is the v0.15 patched target, not the source ROM.
- `PokemonStart_v0.15.pks`: 13,366,750 bytes, Git blob SHA-1
  `500cb5f7ffe5177fa11c15031dbaa4a3a31f6dc5`, SHA-256
  `a1747a37c47ae218b87f459404bdd6a6ba63ada27eff2f053d3e2a3a23f6b926`.
- `PokemonStart_v0.22_PRIVATE.gba`: exact prepared target, 33,554,432 bytes,
  SHA-256 `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`,
  CRC32 `B5D4DF5C`.

Other retained saves and helper archives were inventoried and hashed in the
private workspace; their payload bytes remain outside Git. The original source
ROM and retained v0.15 target both match their independent historical identity
expectations on fresh hashing.

## PKS1 and patcher recovery

Phase A recovered the old v0.15 extraction evidence in `PokemonStart解凍.zip`.
Its `PokemonStart解凍.html` contains an obfuscated JavaScript decoder. The
HTML's JavaScript was statically decoded and inspected; its dynamic `Function`
payload was never run. The v0.15 helper PE is 9,728 bytes, SHA-256
`81253222c2dd63619cfa46d1b4e9a62e9d36ac12e13a770d414c189af14cada7`, x86 PE32,
and imports `mscoree.dll`. The v0.15 patcher PE is 17,889,792 bytes, SHA-256
`58a04c631228e8fa1c47ad312a6e18e5f84bb0937a7c15931d479d7df934b030`, x86
PE32/.NET; static strings and embedded BPS were observed, but it was not run.
The helper HTML, rather than the patcher executable, supplied the sufficient
PKS1 decoder logic.

The observed format is deterministic: `PKS1`, 16-byte nonce, expected payload
SHA-256, then a hash-stream-XOR body. A fixed 32-byte key is present in the
helper HTML. Each 32-byte keystream block is SHA-256 over that key, the nonce,
and a little-endian block counter. XOR output is raw-DEFLATE decompressed,
SHA-256 checked, then decoded as a bounded UTF-8 member table. No external or
unavailable secret was encountered, and no key search was performed. The
minimal standard-library-only static decoder is
[`pokemonstart_pks_inspector.py`](../pokemonstart_pks_inspector.py).

v0.22 yielded three data members. The ROM patch member is `Pokemon.bps`,
17,533,956 bytes, SHA-256
`a2bb3a1bddeeb6344cd45e139edb9ff35535deb41f8c38c0dc04eb4b1a7eab27`.
Exactly one structurally valid BPS candidate was found at member offset 0;
its patch CRC validates. It declares source size/CRC `16,777,216 / 3B2056E9`,
target size/CRC `33,554,432 / B5D4DF5C`, patch CRC `6D0DEFB5`. Metadata:
`PokemonStart v0.22 デモ版（カントー・ななしま・ホウエン）・2026-10-06 14:13 作成・git 4283b3a1`.

## ROM build and save compatibility

The uniquely matching owned source is `Pocket Monsters - FireRed (Japan).gba`.
`pokemonstart_prepare_private_build.py` applied the recovered BPS without
executing package members, refused overwrite, verified target size/CRC/SHA-256,
and rehashed the source unchanged before and after.

The repository verifier accepted the retained v0.15-lineage save
`PokemonStart_v0.15.sav` (SHA-256
`d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`). Offline
state: active slot 1/counter 3, key 0, Money 1,234,567, party count 1; party[0]
species 1, level 5, EXP 134, friendship 50, ball 3, item 0, moves 33/45/0/0,
IVs 31/29/26/23/27/29, EVs all zero.

Dedicated mGBA 0.10.5 loaded only a disposable copy of that save using the
already-enrolled bridge MRU script. At the title/reset probe, live Money was
1,234,567 at `0x0202571c`, party count was 1, and the complete 100-byte
party[0] record matched offline bytes. The original ROM and save hashes and the
working save hash were unchanged. This demonstrates read compatibility for
this exact retained save; it does not claim broad migration compatibility.

## Fast Lab Money

`pokemonstart_fastlab_v022_money.py` is a sealed one-input experiment for this
exact save, exact ROM, and target. It changes active logical section 1 offset
`0x0290` using the current key, recalculates that section checksum, writes a
new output, and reruns the verifier. Output SHA-256:
`15bdac0d6635c6237549565c49e3752c167e85a33643b89ff722ed3c7d17d569`.

The experimental output loaded in v0.22 and live Money read `7,654,321` at
`0x0202571c`; party count and party[0] bytes still matched. Input save, output
save, and ROM were unchanged during the probe. This is **FAST LAB EXPERIMENTAL
V0.22 MONEY**, not Stable support. Automated normal in-game SAVE was not
attempted.

## Party and inventory reconnaissance

Exact-save offline decode and exact-ROM mGBA reads corroborate the existing
100-byte party record model for the retained save. The listed species, level,
EXP, moves, IVs and EVs match at runtime. A bounded Fast Lab friendship writer
reused the M3C direct-field offset (`party[0] + 41`) and changed `50 -> 51` in
a new disposable copy. Only that byte and the active logical section 1
checksum changed (absolute offsets 73825 and 77815); the verifier accepted the
output. Exact v0.22 loaded it, and all 100 live party bytes matched the
offline output. Output SHA-256:
`cb817b561c1eb29813b5e58524d8536dbdf42cb13065b90b5603a47a73f2a37d`.
This is **FAST LAB EXPERIMENTAL V0.22 PARTY WRITE COMPATIBILITY**, not Stable
support. Existing M3C friendship, markings, ball, nature-mint, IV, EV and
cached-stat writer models are recorded as inherited experimental candidates.
The FL2-G0 candidate keeps inherited fields non-writable unless separately
live-proven; it does not promote inherited candidates to capabilities.

The existing M3C `_expected` and `_stats` routines were then reused for
Attack IV `29 -> 0`. Cached Attack recalculated `9 -> 8`; HP, max HP, Defense,
Speed, Sp. Attack and Sp. Defense remained `21/21/11/10/13/12`. The output
changed only the packed IV bytes, cached Attack, and active section checksum;
the verifier accepted it. v0.22 loaded the save and the full live 100-byte
party record matched offline. Output SHA-256:
`5a688c2c3f2e3f2ba4e9f73788ead12da715adaae861880aa0ef5f7faeb620de`.
This establishes **FAST LAB EXPERIMENTAL V0.22 IV/EV/NATURE EDITING** for the
tested Attack IV transform. No separate v0.22 proof was done for EV or nature
mint.

A move replacement then changed move slot 0 from Tackle (`33`) to Pound (`1`)
while retaining PP `35`, with PP-Up bonuses zero. The selected FireRed
baseline definitions give both moves 35 base PP. Only the `u16` move ID at
record offset 44 and section 1 checksum changed. v0.22 loaded the save and
the full live record matched offline, including the new move and prior IV
change. Output SHA-256:
`ded29c2b307343b662ebcdf0889f7b2e24f0952a453e7622049b655e40891efb`.
This is **FAST LAB EXPERIMENTAL V0.22 MOVE EDITING**; no move legality or
battle execution claim is made. The source baseline for move IDs and PP is
[pret/pokefirered move constants](https://github.com/pret/pokefirered/blob/master/include/constants/moves.h)
and [FireRed move data](https://github.com/pret/pokefirered/blob/master/src/data/battle_moves.h).

Moves, level/EXP, and species transformations now have the experimental results recorded below. Ability selector representation is identified, but no ability write or battle resolution was tested.

The v0.22 package credits identify CFRU-JP/DPE-JP and a BW-style bag. The
first retained save tested had an empty regular-items pocket, so it offered no
live-to-save correlation signal. A later user-provided save with a Potion is
recorded in the checkpoint below. No neighboring pocket bases are inferred
from the original empty-pocket probe.

Capability detail is keyed by the exact target ROM SHA-256 in
[`fast-lab-v022-capability.json`](fast-lab-v022-capability.json). Money,
bounded Party writes, composed Party editing, and the Potion quantity edit
remain Fast Lab experimental; no Stable adoption is claimed.

## Level/EXP, ability selector, and species checkpoint

The exact-input level canary reused the repository's CFRU-JP stat formula,
extending its bounded helper to accept levels 5 and 6. FireRed's source
level lookup compares stored EXP against the species growth table; the
Medium Slow row formula used by this canary gives thresholds 135 at level 5
and 179 at level 6. The immutable retained Bulbasaur has EXP 134, stored
level 5, and level-5 cached stats, so its original EXP is one below that
source threshold. The new disposable output sets EXP 179 and level 6 and
recomputes cached stats, retaining full current HP. Output SHA-256:
`09e58a8cda8277ea107991cbf01ea99fa0d0724ce476330be45ef1d5456ed6dc`.
The repository verifier accepted it, and the v0.22 live complete 100-byte
party record matched the offline output. This is **FAST LAB EXPERIMENTAL
V0.22 LEVEL/EXP EDITING**.

The existing packed IV word is a `u32` at party-record offset 72. Its low
30 bits hold the six 5-bit IVs; bit 30 is the egg flag and bit 31 is the
one-bit ability selector in the FireRed party schema. The retained record's
selector is 0. Species ability slot data for the exact v0.22 build was not
established, so no selector mutation was attempted and ability editing
remains unresolved. The source schema describes ability resolution through
a species ability table, but this is not battle-execution evidence.

A fresh-baseline disposable species canary changed Bulbasaur (species 1) to
Ivysaur (species 2), preserved level 5 and selector 0, set EXP 134 to the
Medium Slow level-5 threshold 135, and recalculated cached stats with the
existing M3C formula extended to FireRed Ivysaur base stats. The verifier
accepted the output and the v0.22 live full party record matched offline.
Output SHA-256: `fb0d649fe39e286a7bbe5c8bbd8e62e373b3dc8e6048b2405d8f1f647dc54f4f`.
This is **FAST LAB EXPERIMENTAL V0.22 SPECIES TRANSFORMATION**. Battle use,
resolved ability, evolution and Pokédex effects, move legality, and normal
in-game SAVE remain untested.

The later Potion-bearing save retains both sides of one normal-save
transition in its two verified slots. That same-file differential identifies
the existing regular-items slot described below; the bounded proof does not
establish other pockets or broader item support.

Source references: [FireRed EXP-to-level lookup](https://github.com/pret/pokefirered/blob/master/src/pokemon.c), [FireRed species data](https://github.com/pret/pokefirered/blob/master/src/data/pokemon/species_info.h), [FireRed party ability selector schema](https://github.com/pret/pokefirered/blob/master/include/pokemon.h). These provide source-baseline semantics; the v0.22 ROM live probe corroborates the edited party representation, not broad title-wide compatibility.

## Reusable Party editor and composed canary

`pokemonstart_fastlab_v022_party_editor.py` provides bounded offline
`inspect` and `edit` operations gated by the exact v0.22 ROM profile and
retained canary save hash. It resolves the active slot/section from the
verifier, applies party[0]-bounded patches, recomputes only the active
section-1 checksum, re-verifies the output, reports semantic before/after
state and byte diffs, and creates outputs exclusively. Writes cover only the
recorded transitions: friendship 50->51; level 5->6 / EXP 134->179;
Bulbasaur->Ivysaur with coherent EXP 134->135; slot 0 Tackle->Pound; Attack
IV 29->0; HP EV 0->8 in the exact composed canary; and that full composed
canary. Other moves, IV/EV values, ball, markings, nature mint, held-item
writes, other inputs, and unproven combinations are rejected. Existing
EXP/level values are preserved for unrelated edits, including the retained
baseline's EXP 134 / level 5 inconsistency. Fast Lab cached stats use a
Fast Lab-only Modest Bulbasaur/Ivysaur calculation. Stable M3C calculation
scope remains unchanged. Ability selector writes are rejected. The offline
interface is `python3
pokemonstart_fastlab_v022_party_editor.py inspect <save>` and `python3
pokemonstart_fastlab_v022_party_editor.py edit <input-save> <new-output-save>
--changes-json '{"level":6,"moves":{"0":1}}'`; both ROM and save paths must
be inside the authorized private workspace.

One combined disposable edit from the immutable baseline changed species
1→2, EXP 134→179, level 5→6, move slot 0 Tackle 33→Pound 1, Attack IV
29→0, HP EV 0→8, and friendship 50→53. PP stayed 35; ability selector 0,
nature/mint, ball, markings, held item, personality, and all other moves
were preserved. Cached stats changed from `[21,21,9,11,10,13,12]` to
`[25,25,11,15,14,18,17]` in `[HP,maxHP,Atk,Def,Speed,SpA,SpD]` order.
The verifier accepted the output; v0.22 live species, EXP, level, stats,
and all 100 party-record bytes matched offline. Output SHA-256:
`29380e12b8c43df9dfd12f3070e2bbe2925e300e9b4a1f3fcafda9fef56ef0d5`.
This is **FAST LAB EXPERIMENTAL V0.22 COMPOSED PARTY EDITING**.

The user-provided `PokemonStart_v0.22_PRIVATE.sav` has SHA-256
`b32abee33dc951c61068b4a83f4bc06215db8a86d880f07620a1aece82ccca50`. Both
slots independently verify: inactive slot 1/counter 1 retains Money 3000 and
active slot 0/counter 2 has Money 3032. The counter and section rotation show
the prior slot retained through one normal-save transition. Comparing logical
sections by ID, not physical offsets, finds one inventory-shaped delta:
logical section 13 offset `0xADC`, `{u16 item 13, u16 quantity 1}` to
`{u16 item 13, u16 quantity 2}`. The following row and remaining payload tail
are zero in both slots. Encryption key is 0 in both. The offset is outside
section 13's `0x450` checksum-covered prefix; its stored checksum is unchanged.
Other normal-save changes, including Money, party/runtime bookkeeping, and
slot rotation, were kept in the differential rather than masked.

The exact-ROM live probe confirmed regular-items slot 0 at `0x0203BA98` as
Potion (ID 13), quantity 2. The verified old slot supplies the before value
quantity 1; mGBA selects the active slot, so only the after value was read
live. A bounded editor in `pokemonstart_fastlab_v022_inventory_editor.py`
supports inspecting that single observed entry and changing only the exact
retained save's existing slot-0 quantity 2→3. A new disposable output changed
it at absolute byte offset
6878; the item ID, slot, all other bytes, and all section checksums were
unchanged. The repository verifier accepted it. Exact v0.22 live RAM then
showed Potion ID 13 quantity 3 in the same slot; party and Money remained
equal to offline values. Output SHA-256:
`51129cdd5168f2f9f3d28966085bfdd4ae094c2a705052253001cc3d189c987b`.
This is **FAST LAB EXPERIMENTAL V0.22 INVENTORY QUANTITY**. Entry capacity,
other populated slots, insertion/deletion, nonzero keys, and other pockets
remain unproven. Source-baseline quantity XOR/save-copy semantics are
documented in [item.c](https://github.com/pret/pokefirered/blob/master/src/item.c)
and [load_save.c](https://github.com/pret/pokefirered/blob/master/src/load_save.c);
the exact private-save differential and live result control this bounded
location claim.

## Milestone-boundary audit — proposal only

See [`fast-lab-milestone-boundary-audit.md`](fast-lab-milestone-boundary-audit.md).
It compares canonical main `5d81e77358f95394dea62f94ba993e3ba24a4197` with
this human-authorized local Fast Lab branch. The recommendation is to adopt a
two-lane strategy canonically in a future separately authorized change; no
canonical document has been changed here.
