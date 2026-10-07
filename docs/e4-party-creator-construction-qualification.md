# E4 exact-v0.22 Party creator candidate

Disposition: **E4_CANDIDATE_READY_FOR_HUMAN_ACCEPTANCE** after the exact pushed
candidate checks reported at handoff. This is a Maker candidate, not canonical
adoption, independent review, Human gameplay evidence, release or Stable.

## Fresh authority and position

Fresh remote main: `381bc80080919952c9a32bb7982dfcf24bc92ea5`.
Fresh candidate starting point: `69d1d5d9dcdfcdf16e4564204e61682992de205c`.
Both were fetched before work. Current remote Issues/PRs were empty. README,
decision/evidence records, expansion and creation contracts, native template
proof, E3 qualification/review, verifier, historical creation/import code and
current product/model/writer/auditors/tests were reconstructed from current
remote and source. Prior investigation conclusions were re-executed, not used
as correctness authority. E0–E3 remain adopted; E4 is the next milestone.

The [decision record](decision-record.md) and
[expansion contract](v022-pkhex-like-editor-expansion.md) authorize bounded
investigation, candidate implementation/tests/private verification, Human
acceptance and independent-review preparation. No merge/adoption, E5 expansion,
Box, Pokédex/story/event/quest/RTC mutation, arbitrary PID/shiny/OT controls,
cross-version support, release or Stable promotion is included.

Exact owned ROM hash:
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
The canonical package/source/patch profile remains controlling. All production
creation paths hash-gate the actual 32MiB ROM; there is no source-save SHA
whitelist or captured identity/record reuse. Protected binary/assets, raw
instructions/tables/private record/identity material, private absolute paths
and credentials stay outside Git. Only code, synthetic tests, hashes,
structural addresses and bounded semantic aggregates are retained.

Canonical complete-record append and native Rattata load/summary/heal/battle/
normal-SAVE/return evidence is reused from the
[native/template record](v022-native-inventory-and-template-import-evidence-20261007.md).
That is independently rechecked retained evidence and historical Human
attestation, not new gameplay evidence or authority for arbitrary templates.
E3's ordinary semantics and exceptional predicates remain controlling. No
milestone redesign was needed. E4-A's cheapest discriminator was downstream
nickname semantics; it closed and authorized E4-B continued without a pause.

## Nickname: transport is distinct from observation

The previous checkpoint correctly found stack-derived constructor tails and
fixed-width getter transport. It did not establish semantic tail observation.
The read-only `pokemonstart_v022_nickname_probe.py` now compares records differing
**only** after the first FF terminator. Species/PID/OT/language/all other bytes
and each paired runtime context are identical. Four fills00/FF/A5/5A cover all
152 ordinary IDs1–151/288, encoded name lengths3/4/5 (608 variants per path).
Full copied buffers are measured separately from final results.

| Exact entry / downstream graph | Full intermediate buffer | Final semantic result |
| --- | --- | --- |
| GetBoxMonData0803F4B0, GetMonData0803F354 field2, GetMonNickname08120AD0 | Fixed-width tail differs, as previously reproduced | Identical visible prefix/terminator; these getters alone are **not** the equivalence proof |
| Summary081368D8 → GetMonData at081369C4 → StringCopyN_Multibyte08008E10 at081369D2; boundary081369D6 | Getter stack buffer differs | Complete20-byte destination at summary offset3034 is identical, including length/content |
| Native evolution/default-name08042C5C → getter08042C70 → StringCompare080089A4 at08042C80 → SetMonData0803FA70 at08042C94 | Getter transports tail before comparison | All variants are default names; changing a visible-prefix byte is independently nondefault and does not invoke the setter. All100 bytes normalize identically to the exact fixed7 species field |
| Party DisplayPartyPokemonNickname08121F0C → GetMonNickname08120AD0 →08121ED8 →0812ED24 → AddTextPrinter08002CF0 → RenderFont08002E4C → actual FontFuncSmall08005348 → RenderText0800575C | Name supplied to printer differs after EOS | Same terminated display name. The actual selected font interpreter at EOS returns1, reads exactly the FF byte and reads no later bytes; deterministic admitted prefixes contain no intervening extension-control sequence |
| Party Nidoran gender/default-name08122090 → StringCompare at081220CC; boundary081220D0 | Fixed-width input differs | Both species29/32 have comparison result0 for every tail. Summary's analogous check consumes an already identical normalized string |
| BattleStringExpandPlaceholders080D88A8 → patched0906D660 → actual Party GetMonData caller0906D7A6 (player-left-name tokenFD05FF) | Getter temporary differs | Complete80-byte final expansion buffer identical before rendering, not merely a generic StringLength check |
| CheckBattleTypeGhost08043EB0, normal player guard; adversarial opponent/Ghost branch → GetMonData08043EE6 → StringGet_Nickname080088A4 at08043EEC → StringCompare at08043EF4 | Opponent-control comparison buffer may transport tail | Ordinary player guard does not consume nickname. Actual normalize/compare path gives identical comparison and predicate results for all tails. The opponent control is synthetic branch evidence, not supported special-battle gameplay |
| SaveSerializedGame0804BAB8 → Party serializer0804B9A8 | Stored100-byte records differ only in tail | Exact serializer preserves each complete input record, without semantic rewriting; E3 reconstructed semantics/eligibility remain equal |

Canonical representation: **exact encoded species-name prefix, firstFF, FF
through the remainder of its7-byte field**. This is not a convention chosen for
convenience: the exact species table contains this representation throughout
the admitted class and the native evolution default-name setter intentionally
writes that complete field. It is independently constructible, E3-eligible,
and indistinguishable across the material ordinary paths traced above.

Nickname initialization is CLOSED for this default-name creation class.
Native uninitialized stack tail is never reproduced. Serializer preservation
is intentionally a storage difference, with no semantic branch or rewrite.
This does not qualify arbitrary custom nickname editing, every battle
placeholder, link/trade/facility states, rendered pixels or a whole-game proof.
RAM widgets/fonts/I/O are common synthetic execution context; native routines
are not replaced with guessed returns. Renderer execution stops at the proven
string/EOS boundary. No Human/emulator gameplay claim is inferred.

## Supported creation context and identity

The isolated harness restores disjoint SaveBlock1/2, saved native Party/count,
parasite tails **and** sectors30/31. It executes native bag initializer090D39A4;
pointer020397E4 is reconstructed, not guessed. Earlier partial bag RAM missed
both item471/833; native saved lookup08099948 now observes both present in the
primary retained save. That correction is controlling over the old result.
Production and independent creation gates both require the existing restricted
Inventory context (including key-pocket consistency and selector exclusion).

| Flag | Native-validated saved source | Effect / supported policy |
| --- | --- | --- |
| 0828 | section1:FE5 mask01 | helper090B7380 queries restored Party species and RNG; alters shiny-attempt probability. Saved false/true states are reconstructed and both qualified; no probability-mode UI |
| 0913 | section0:F26 mask08 | Direct constructor force-shiny branch rewrites supplied PID. **Reject saved true**; native false→true discriminator reproduced |
| 0930 | section0:F2A mask01 | E3 facility rejection retained, including every tier |
| 12F8 | section4:E0B mask01 | helper090B7E6C queries saved bag item833 and RNG; alters shiny-attempt probability. Reconstruct flag/bag; both states qualified, no special-mode emulation |

The constructor also checks saved bag item471. The accepted policy always
selects a non-shiny native-permitted outcome. Four0828/12F8 combinations ×
four species × eight adversarial fishing/live-battle controls give128 complete
record agreements after the qualified name/move transformations. Four saved
key-bag presence combinations for471/833 × four species give16 more agreements;
each synthetic save first passes the independent creator/Inventory predicates.
No single unchanged variant is used to infer runtime irrelevance.

| Runtime input | Classification in this creator |
| --- | --- |
| 03005040 | RNG required only by native qualification; deterministic test seeds select native non-shiny/primary-type outcomes. Production identity uses the bounded policy below |
| 03005ED8 | Required native flag routing; ordinary standalone construction uses0. Alternate runtime routing is excluded, not reconstructed from numeric coincidence |
| 020397E4 | Save-derived bag runtime pointer, reconstructed by exact initializer with complete serialized bag; invalid pointers are not admitted |
| 0203DFC0 / 0203DFD0 | Fishing-dependent helper inputs; controlled ordinary baseline0, and adversarial values tested with actual helpers. They may affect branch/RNG timing; no global irrelevance claim. Accepted non-shiny/unchanged-PID/primary-type outcomes still reconstruct the full record |
| 03003569 | Live battle state in special shiny processing; accepted ordinary non-shiny path does not require it. Perturbations tested; no claim to recreate in-battle construction |

Creator is a standalone ordinary initializer, not an emulator of a current
in-game event, fishing action, complete loader or random stream. Source Party
must be count1–5 and every existing member E3-ordinary; malformed/egg/form/
hyper-training/special ability/Shedinja/unsafe held/facility/Inventory contexts
fail closed. Party6 rejects explicitly: **Box creation is not supported**.

Owner OT ID is active section0[10:14]; OT name is its first7 bytes. Saved name
must have a nonempty terminated8-byte encoding; owner gender must be0/1.
Language1 is exact integrated constructor behavior. No arbitrary OT/name/PID,
shiny, gender, form, ball or extended-field controls exist.

Deterministic personality candidates use SHA256 over a fixed versioned
namespace plus owner OT ID, semantic species/level/nature and attempt0–255.
Candidate is adjusted to requested nature modulo25, checked for u32 overflow,
existing-Party PID reuse and exact native shiny XOR score<8. Reject those
candidates; bounded exhaustion fails closed. No source hash or existing PID is
a seed/template. Batch construction rebuilds saved context after each append,
so subsequent creations cannot reuse the first created PID.

Independent implementation reconstructs candidates and verifies XOR/nature
separately. Native IsShinyOtIdPersonality08043AE4, GetNatureFromPersonality080425A4,
GetGenderFromSpeciesAndPersonality0803EEF8, GetMonGender0803EE8C and
GetMonAbility0804042C agree. Exact gender uses the species ratio byte16:
0/254/255 special ratios, otherwise lowPID byte<ratio gives female254, else0.
Gender has no creator control. All admitted IDs exclude PID-dependent form
species; E3's exact native form/move and ability exclusions remain in force.
All152 species × levels1/3/20/100 × all25 natures give15,200 predicate cases.
Three synthetic OT IDs × XOR scores0–32 give99 independent shiny checks;
only scores0–7 are shiny. This is machine evidence, not natural cross-owner
Human evidence.

Byte17 is **not always primary type** for arbitrary native RNG. Exact helper
090F4D64 (called at0907526C, written at09075270) chooses an ordinary base-type
outcome. All152 species ×32 seeds (4,864 cases) produce only native base types
and reach primary. Creator deliberately chooses that native permitted primary
outcome; it is not a claim that different tera outcomes are equivalent. No
tera control is exposed. Native qualification selects matching RNG outcomes,
without changing the independently generated production PID.

## Origin: independently bounded save/ROM mapping

Native current-region08055B20 reads SaveBlock1 mapGroup/mapNum at bytes4/5.
GetMapHeader08054AF8 indexes root089A3D6C → group[mapNum] → header byte14.
The independent domain uses adjacent aligned in-ROM pointer-array extents,
with positive integral lengths1–255. E4 explicitly admits only76 qualified
groups /1,022 maps. Groups42/76/78/79 have no qualified adjacent extent and
fail closed; this is not a claim about the complete game's map count.
Every admitted map agrees with native lookup. Retained different locations
(map3/19,5/3,5/4) independently agree and remain creator-eligible.

**Correction:** the previously suspected regionFF fallback was a neighboring
function beyond current-region's return, not this constructor path. Native
loaded-register controls0/88/89/255 return unchanged at the exact boundary
08055B3E. No admitted header hasFF; any saved map outside the independently
reconstructed domain or with regionFF rejects. No global met-location constant
or arbitrary byte-space enumeration is substituted.

Packed origin is met level bits0–6=input level, met game bits7–10=4, bits11–14
clear and bit15=owner gender. Native gender0/1 × levels1/3/20/100 controls
establish the packed rule. Naturally different owner gender is not claimed.

## Complete100-byte creator field matrix

Offsets inclusive, record-relative. Zeroed storage below is compared as part
of complete native records, not inferred from structural verification alone.
Every byte and packed bit is classified; unexplained creator-controlled bits=0.

| Bytes / bits | Field | Closed classification / creator rule |
| --- | --- | --- |
| 0–3 | personality | SEMANTIC_INPUT policy + independently qualified deterministic generator and exact-native postconditions; no raw identity input |
| 4–7 | OT ID | OWNER_SAVE_DERIVED active section0[10:14] |
| 8–14 | default nickname | CONSERVATIVE_CONSTANT representation proven consumer-equivalent: exact species encoded name/FF/tailFF, native setter corroboration |
| 15 | nature mint | EXACT_CONSTRUCTOR_DERIVED0; requested nature is native PID nature, no mint grant |
| 16 all bits | hyper-training/reserved | EXACT_CONSTRUCTOR_DERIVED0; nonzero input states UNSUPPORTED / FAIL_CLOSED |
| 17 | tera/extended type | EXACT_CONSTRUCTOR_DERIVED permitted primary-type outcome; no control |
| 18 | language | EXACT_CONSTRUCTOR_DERIVED1 |
| 19 all bits | sanity/egg metadata | EXACT_CONSTRUCTOR_DERIVED2, all other bits clear; eggs/bad eggs excluded |
| 20–26 | OT name | OWNER_SAVE_DERIVED first7 active owner bytes |
| 27 | markings | EXACT_CONSTRUCTOR_DERIVED0 |
| 28–29 | backup species | EXACT_CONSTRUCTOR_DERIVED0; nonzero existing states excluded |
| 30–31 | reserved header | EXACT_CONSTRUCTOR_DERIVED both0 |
| 32–33 | species | SEMANTIC_INPUT exact ordinary IDs1–151/288 with E3 validation |
| 34–35 | held item | EXACT_CONSTRUCTOR_DERIVED0; optional E3_DERIVED safe targets0/139/142/200 |
| 36–39 | EXP | E3_DERIVED exact species growth thresholds at requested level |
| 40 four bit pairs | PP bonuses | EXACT_CONSTRUCTOR_DERIVED0; initial PP-Up control excluded |
| 41 | friendship | EXACT_CONSTRUCTOR_DERIVED species byte18; optional SEMANTIC_INPUT0–255 via E3 |
| 42 | ball | EXACT_CONSTRUCTOR_DERIVED3 |
| 43 | reserved growth byte | EXACT_CONSTRUCTOR_DERIVED0 |
| 44–51 | moves1–4 | SEMANTIC_INPUT explicit1–4 selections, at least one occupied; qualified E3 catalog. Automatic initial learnsets remain unqualified and excluded |
| 52–55 | PP | E3_DERIVED occupied exact-table base PP; never-filled empty slots EXACT_CONSTRUCTOR_DERIVED0. E3 clear-old-slot PP35 remains unchanged for existing edits |
| 56–61 | six EVs | EXACT_CONSTRUCTOR_DERIVED zero baseline; optional E3_DERIVED0–252, total≤510 |
| 62–67 | contest/condition attributes | EXACT_CONSTRUCTOR_DERIVED all0 |
| 68 both nibbles | Pokerus strain/days | EXACT_CONSTRUCTOR_DERIVED0 |
| 69 | met location | OWNER_SAVE_DERIVED qualified saved map → exact-ROM header byte14; reject outside domain/FF |
| 70 bits0–6 | met level | EXACT_CONSTRUCTOR_DERIVED request level |
| 70 bit7 /71 bits0–2 | met game | EXACT_CONSTRUCTOR_DERIVED4 |
| 71 bit3 | Gigantamax | EXACT_CONSTRUCTOR_DERIVED clear; unsupported special states excluded |
| 71 bit4 | hidden ability | EXACT_CONSTRUCTOR_DERIVED clear; creator excludes hidden targets |
| 71 bits5–6 | reserved origin | EXACT_CONSTRUCTOR_DERIVED clear |
| 71 bit7 | OT gender | OWNER_SAVE_DERIVED owner byte8, constrained0/1 |
| 72–75 bits0–29 | six IVs | EXACT_CONSTRUCTOR_DERIVED zero baseline; optional E3_DERIVED six0–31 inputs |
| 75 bit6 | egg | EXACT_CONSTRUCTOR_DERIVED clear; eggs unsupported |
| 75 bit7 | ability selector | EXACT_CONSTRUCTOR_DERIVED PID parity when ability2 exists; optional ordinary first/second ability via E3 resolution, hidden remains clear |
| 76–79 all bits | ribbons/fateful/obedience/reserved | EXACT_CONSTRUCTOR_DERIVED all0; no controls |
| 80–83 | status | EXACT_CONSTRUCTOR_DERIVED0, ordinary standalone creation |
| 84 | stored level | E3_DERIVED requested level/EXP |
| 85 | Party Pokerus timer | EXACT_CONSTRUCTOR_DERIVED255, distinct from byte68 |
| 86–87 | current HP | E3_DERIVED full maxHP, including optional IV/EV changes |
| 88–99 | maxHP/five stats | E3_DERIVED ordinary calculator; independent E3 arithmetic/native recalculation |

## E4-B candidate and verification

Production `pokemonstart_v022_creation_model.py` builds a new zeroed record
from owner/ROM/semantic inputs. The independent
`pokemonstart_v022_creation_baseline_audit.py` uses direct reads, its own
candidate generator/map-domain construction and adopted independent E3
arithmetic; it never imports the production constructor/writer/transforms.
`pokemonstart_v022_creation_writer.py` appends at source Party count, the first
unoccupied slot, increases count exactly once per creation and updates only
section1 checksum. The unused slot is defined by native count, not by a
zero-byte assumption; complete100 bytes are always replaced. Existing members,
unrelated bytes, counters/section metadata and editor footer are preserved.
Input never changes; verified output is separate, exclusive on export.

E3 record transformation and independent record arithmetic were extracted into
separate helpers without changing existing semantics. Creator applies optional
IV/EV/friendship/ordinary ability/held-item changes through those helpers.
Independent full-save reconstruction applies all requested families and rejects
complete output inequality. Creation count/new-record envelopes are disjoint
from Money, Inventory and existing-member edits; source-only slots and duplicate
edits reject deterministically. There is no Box/Pokédex automation.

Product core composes creation alone, +Money, +Inventory, +existing Party edit,
and all four families. GUI exposes Create Pokémon only under eligibility,
starting from the first empty slot. Later creation checkboxes require all
previous creations. Preview distinguishes new Pokémon/slot/semantic parameters
and noneditable generated identity. Explicit moves, IV/EV, nature, friendship,
ordinary ability and safe held items are practical controls. Localhost127.0.0.1,
source/ROM hash/stale controls, repeated verification and exclusive separate
export remain intact. Full Party shows the explicit Box-not-supported reason.

Machine checks include complete2,432 native constructor records (all152 ×
levels1/3/20/100 × four natures), native identity all25 natures, origin1,022,
type4,864 and32 IV/EV/ability/item override recalculations. The complete native
comparison permits only the specifically justified nickname setter and explicit
move/PP setter transformations; there are no other unexplained differences.
A second retained map/source separately executes160 complete records and1,000
all-nature identity cases. These are exact-ROM local private proofs, not
Human gameplay. Synthetic tests cover counts1–5, both active slots, physical
section permutations, batch unique identities/full-Party rejection, every
constructed-byte tamper, malformed state and all product compositions.

Full repository suite:305 discovered,290 successful,15 Windows-only skips.
The exact pushed SHA/tree is frozen and the full suite, native probes and real
Chromium check are rerun against that candidate at handoff. Counts from an
earlier commit do not substitute. The sanitized
[evidence index](e4-party-creator-construction-evidence.json) identifies probe
hashes/aggregates; ignored logs retain exact-candidate execution details.

## Grouped acceptance prepared; not requested or completed here

The retained normally saved E1_T1_POST_DELETE source hash
`108d9e17e138375f7f0099af742eb22aaf783794abbaf66bbc50ea072b77f3bd`
(counter12, Party4, map5/3) is eligible. Its historical native-save attestation
is in [E1 transition evidence](e1-native-transition-results.json). It is not
claimed pristine before earlier adopted edits. One transaction creates:

- Party5: Bulbasaur Lv3, Hardy, explicit Tackle/Growl, IV0/EV0, ordinary ability1,
  no held item, species default friendship.
- Party6: Rattata Lv20, Adamant, explicit Tackle/Tail Whip/Quick Attack,
  IV31/17/9/25/0/13, EV0, ordinary ability2 and Leftovers, default friendship.

Growth groups, levels, nature, name lengths, moves, ability structure and held
item differ without artificial field complexity. Money/Inventory and all four
existing members remain unchanged in editor output. The batch fills Party,
allowing subsequent full-Party Box rejection to be checked in the same session.
There is no unsupported removal or Box operation and no serial canary request.

`pokemonstart_v022_creation_acceptance.py prepare` regenerates a sanitized
semantic receipt from the immutable source. `check-return` is prepared and
tested before any Human request: rederive/audit complete editor output, require
one native normal-SAVE counter/slot/section progression, preserve prior active
slot, independently reconstruct returned records, reject unexplained identity/
moves/IV/origin/opaque coupling, expose permitted EXP/EV/PP/friendship/status/
HP/battle/heal drift, check Money/Inventory, reopen editor, and test subsequent
creation or full-Party Box rejection. Emulator footer may change after game
SAVE, while editor output footer remains byte-exact. Drift needs Human action
attestation and review; synthetic normal-SAVE tests never certify gameplay.

The prepared future grouped flow is immutable normal save → GUI create/export
→ exact-v0.22 load → inspect both created summaries/moves/ability/item → heal
and normal use/battle as practical, avoiding evolution or deliberate move/item
changes → inspect existing members → normal SAVE → return save. No gameplay
has been requested/performed in this work unit. Only after returned verification
and Human acceptance should a sanitized controlling review packet freeze the
then-exact candidate and prepare a genuinely fresh independent-review prompt.
Maker does not conduct that review and no merge is authorized.

## Reproduction

Read-only native probes require Unicorn and host JIT permission. Actual browser
probe additionally requires Playwright/Chromium; neither is a production
constructor dependency. Keep all inputs/downloads private, with no traces.

```sh
.venv/bin/python pokemonstart_v022_nickname_probe.py --rom <private-ROM> --save <private-save> --broad
.venv/bin/python pokemonstart_v022_creation_context_probe.py --rom <private-ROM> --save <private-save>
.venv/bin/python pokemonstart_v022_creation_qualification.py --rom <private-ROM> --save <private-save> --broad
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python pokemonstart_v022_product_web.py --rom <private-ROM>
.venv/bin/python tests/v022_e4_browser_smoke.py --url http://127.0.0.1:8766 --source <private-grouped-source> --rom <private-ROM>
.venv/bin/python pokemonstart_v022_creation_acceptance.py --rom <private-ROM> prepare <private-grouped-source>
.venv/bin/python pokemonstart_v022_creation_acceptance.py --rom <private-ROM> check-return <private-grouped-source> --returned <private-return> --receipt <private-receipt>
```

Earlier stopped investigation remains in branch history at the fetched starting
checkpoint. Its stronger terminator claim, partial bag results and suspected
regionFF fallback are explicitly superseded by the corrected experiments here.
