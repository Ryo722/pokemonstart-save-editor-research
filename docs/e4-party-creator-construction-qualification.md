# E4-A exact-v0.22 Party construction checkpoint

Disposition: **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE**.
This is a read-only E4-A investigation candidate, not a qualified creator,
Human acceptance packet, independent review, or adoption decision.

## Fresh authority and milestone boundary

The freshly fetched remote `main` base is
`381bc80080919952c9a32bb7982dfcf24bc92ea5`; the remote identity was checked
again with `git ls-remote`. Open Issues and PRs were empty. Candidate branch:
`codex/e4-v022-party-creator`.

README, decision record, evidence ledger, expansion contract, historical
creation/GUI contract, native Inventory/template-import evidence, E3 writer
qualification/review packet, verifier, E3 model/writer/auditor, historical
creation/template-import code/tests and product core/GUI/tests were freshly
examined. The controlling [decision record](decision-record.md) authorizes
bounded E1–E5 investigation, candidate implementation, tests, private local
verification and review preparation. E3's historical review packet is evidence
of that candidate; its earlier scope wording does not supersede the current
decision record or the explicit E4 work authorization.

Canonical position: E0–E3 complete/adopted; E4 next; E5 follows. Money is
maintenance-only, E1/E2 Inventory remains the restricted recovery-medicine
subset, and E3 remains the qualified ordinary existing-Party editor. The
cheapest uncertainty-reducing next step remains exact record initialization,
not insertion mechanics or another capture canary. No milestone redesign is
justified by these results.

No merge/adoption, E5 expansion, Box, Pokédex/story/event/quest/RTC mutation,
arbitrary shiny/PID/OT control, other versions, Stable promotion or release is
authorized here. Original inputs remain immutable. ROM/save/package/patch/
executable/assets, private record or identity dumps, extracted ROM tables/
instructions, private absolute paths and credentials must remain outside Git.

Exact profile, freshly checked against the local ROM:

- upstream package revision: `ddd054d46fc1bd0555badf738572620b1ee4670d`;
- package hash: `d22bc25d7427899e8d0b2e29e7fd6b604602781167b78cfa8a90c8a2da9e4060`;
- owned source hash: `1e4af44b0c75cc8649bfb8649dc4ae5850bf5358bd6b9cd0bf779c99f9db1486`;
- exact integrated ROM hash: `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.

The package/source hashes above are canonical profile identifiers, not a new
reproduction of the package extraction or patch chain.

## Evidence reused and newly reproduced

The canonical [native/template record](v022-native-inventory-and-template-import-evidence-20261007.md)
establishes one complete native Rattata append surviving display, healing,
battle, normal SAVE and returned verification. Those gameplay observations
remain **canonical Human attestation**; they were not replayed here.

Fresh **retained private-input verification** rediscovered the canonical
pre-acquisition, native acquisition and returned snapshots by their hashes.
The native Rattata record hash matched
`74d64c9dfbf4905bb0ca2abd7047d9834cb5b3bc8822cf95d538bba80da673f3`.
Existing production template import and the independent complete-output
builder agreed: count 4→5, 47 changed bytes, only count/new record/checksum;
unrelated bytes and footer preserved. The returned snapshot revalidated at
counter 10/count 5 with ordinary Rattata semantics. This reuses the existing
envelope; it grants no synthesis authority.

E3's semantic rules and exceptional exclusions are canonical adopted evidence.
Its synthetic full suite was freshly reproduced at the base: 285 discoveries,
270 successful, 15 skipped Windows checks. The new constructor observations
use E3's independent record arithmetic/eligibility as a **partial** check;
that auditor does not reconstruct the newly synthesized identity/metadata.

Public CFRU-JP revision `e24a16fe39e27ae162faf5b78596d1f3df18489d`
was used only for navigation. The retained `build_pokemon.c` Git blob hash
was independently calculated and matched the fresh GitHub API identity
`99f58ab79046546230e5ce6fc769dcfb7d5a0e29`. Neither that match nor the upstream
hook file establishes equality with the integrated PokemonStart binary.

## Exact-ROM investigation and limits

The [sanitized evidence index](e4-party-creator-construction-evidence.json)
contains source/probe hashes, bounded observations and the blocker comparisons.

`pokemonstart_v022_creation_probe.py` executes the SHA-gated owned binary with
Unicorn in isolated RAM. It has no save-output or product integration path.
The real `CreateMon` entry is `0x0803D1C0`; its `CreateBoxMon` route at
`0x0803D230` reaches `0x09075150`. `ZeroBoxMonData`/`ZeroMonData`, native
setters, initial moves, stats and identity postprocessing execute as part of
this path. No external routine is intercepted to return a guessed value.

RAM contains the active owner section, reconstructed SaveBlock1 payload and
serialized parasite fragments. Other runtime state starts at controlled
values. This is **exact-ROM isolated execution with partially reconstructed
RAM**, not a complete game-load reconstruction or gameplay evidence.

The broad matrix covers all 152 E3 ordinary species, levels 1/3/20/100,
two fixed synthetic personality outcomes and uniform IV0/IV31: 1,216 cases.
Another 1,216 executions vary old destination fill A5/5A. Complete records
agree for each destination-fill pair and pass E3 ordinary reconstruction.
Four growth groups occur (0/3/4/5), with ability2-present and absent species,
different native move configurations, low/high levels and full-HP extremes.
This does not qualify EV/request overrides, Party insertion permutations,
composition, creation GUI or Human use. Their E4 tests are deferred until the
complete constructor model closes, not represented as passing tests.

Tera initialization matches the species primary-type byte in every broad case;
language is 1, sanity 2, ball 3, and Party Pokerus timer 255. OT ID/name match
their owner-save sources in every case. Independent E3 arithmetic agrees with
EXP, level, ability and full HP/stats. Whole-record destination overwrite alone
does **not** establish safe field initialization.

## Complete 100-byte field classification

Offsets are record-relative, inclusive. Every byte and the packed subfields
are accounted for. `EXACT_CONSTRUCTOR_DERIVED` below means an observed native
initialization in this controlled matrix; it does not declare that the entire
independent constructor has closed. Constants are candidate policies only.

| Bytes/bits | Field | Classification / current rule |
| --- | --- | --- |
| 0–3 | personality | **UNRESOLVED / BLOCKING**: supplied synthetic PID is preserved in baseline cases but saved flag913 can rewrite it; flag913 source is section0:F26 mask08 under ordinary flag routing. Proposed creator rejects it true and retains E3 flag930 rejection. Generator/postconditions and other runtime modes remain unqualified |
| 4–7 | OT ID | OWNER_SAVE_DERIVED: active section0 bytes10–13; equal in every native case; no arbitrary control |
| 8–14 | species-default nickname | **UNRESOLVED / BLOCKING**: native species glyph prefix/terminator, followed by stack-dependent tail. Native length/compare ignore tail, but both mon getters and Party nickname copy transport it. Downstream equivalence remains blocking; no padding selected |
| 15 | nature mint | CONSERVATIVE_CONSTANT: baseline0; optional effective nature would use E3_DERIVED transformations |
| 16, all bits | hyper-training/reserved bits | UNSUPPORTED / FAIL_CLOSED for nonzero; observed baseline0 |
| 17 | tera/extended type | EXACT_CONSTRUCTOR_DERIVED: primary type in all probed ordinary species; no control |
| 18 | language | EXACT_CONSTRUCTOR_DERIVED: exact integrated build1; no control |
| 19, all bits | sanity | EXACT_CONSTRUCTOR_DERIVED:2, other bits clear; eggs/bad eggs unsupported |
| 20–26 | OT name | OWNER_SAVE_DERIVED: active section0 first seven bytes; owner encoding/terminator eligibility still needs a creator predicate |
| 27 | markings | CONSERVATIVE_CONSTANT: observed0 |
| 28–29 | backup species | UNSUPPORTED / FAIL_CLOSED for nonzero; observed0 |
| 30–31 | unnamed/reserved header | EXACT_CONSTRUCTOR_DERIVED: observed cleared; no control |
| 32–33 | species | SEMANTIC_INPUT: E3 ordinary internal IDs1–151/288 only |
| 34–35 | held item | EXACT_CONSTRUCTOR_DERIVED baseline0; optional E3_DERIVED targets0/139/142/200 only |
| 36–39 | EXP | E3_DERIVED: exact species growth table at selected level |
| 40, four bit pairs | PP bonuses | CONSERVATIVE_CONSTANT baseline0; no fresh PP-Up grant policy |
| 41 | friendship | EXACT_CONSTRUCTOR_DERIVED: species base friendship; optional E3_DERIVED byte override |
| 42 | ball | EXACT_CONSTRUCTOR_DERIVED:3; no arbitrary ball control |
| 43 | unnamed growth byte | EXACT_CONSTRUCTOR_DERIVED: observed cleared; no control |
| 44–51 | moves1–4 | EXACT_CONSTRUCTOR_DERIVED observations; independent native initial-moves algorithm unresolved. Smaller explicit-move interface may replace this default, so this alone is not a stop blocker |
| 52–55 | PP1–4 | E3_DERIVED occupied base PP; native never-filled slots observed0. Do not apply E3's clearing PP35 rule to never-filled slots |
| 56–61 | EVs | CONSERVATIVE_CONSTANT baseline six0; optional E3_DERIVED allocations/ranges |
| 62–67 | contest/condition attributes | EXACT_CONSTRUCTOR_DERIVED: observed cleared; no controls |
| 68, two nibbles | Pokerus days/strain | EXACT_CONSTRUCTOR_DERIVED: observed0; no control |
| 69 | met location | OWNER_SAVE_DERIVED via native current-region route; independent mapGroup/mapNum (section1:4/5) → exact-ROM map header+14 matches retained locations. General map-index bounds / regionFF fallback remain UNRESOLVED / BLOCKING |
| 70 bits0–6 | met level | EXACT_CONSTRUCTOR_DERIVED from requested level |
| 70 bit7 / 71 bits0–2 | met game | EXACT_CONSTRUCTOR_DERIVED: observed4; cross-owner independent reconstruction pending |
| 71 bit3 | Gigantamax | UNSUPPORTED / FAIL_CLOSED: ordinary baseline clear |
| 71 bit4 | hidden ability | EXACT_CONSTRUCTOR_DERIVED baseline clear; E4 initial optional ability policy not qualified, E3's selector/resolution remains reusable |
| 71 bits5–6 | reserved origin bits | EXACT_CONSTRUCTOR_DERIVED: observed clear; no control |
| 71 bit7 | OT gender | OWNER_SAVE_DERIVED; source section0 byte8; synthetic gender0/1 exact constructor controls reproduced; natural cross-gender owner not asserted; no control |
| 72–75 bits0–29 | six IVs | SEMANTIC_INPUT / E3_DERIVED; matrix uses uniform0/31, not a complete creation allocation policy |
| 75 bit6 | egg | UNSUPPORTED / FAIL_CLOSED: clear |
| 75 bit7 | ordinary ability selector | EXACT_CONSTRUCTOR_DERIVED: native ordinary choice; independent complete creation baseline binding to generated PID pending; E3's optional transformation remains reusable |
| 76–79, all bits | ribbons/fateful/obedience metadata | EXACT_CONSTRUCTOR_DERIVED: observed cleared; no controls |
| 80–83 | status/condition | CONSERVATIVE_CONSTANT: observed0; unsupported runtime/facility contexts require rejection |
| 84 | stored level | E3_DERIVED from EXP |
| 85 | Party Pokerus timer | EXACT_CONSTRUCTOR_DERIVED:255, distinct from byte68 |
| 86–87 | current HP | E3_DERIVED full calculated maximum for baseline creation |
| 88–99 | max HP / five cached stats | E3_DERIVED: qualified ordinary integer arithmetic |

## Concrete blockers and cheapest next evidence

**Nickname tail:** varying only the isolated pre-call stack fill changes bytes
after the native name terminator. In the eight-species targeted comparison,
species1/25/129/150/288 change byte14; species19/63/133 change bytes13–14.
The initial destination-fill comparison did not detect this because both
executions used the same initial stack. All these records still pass E3.
Copying the first seven ROM name bytes does not reproduce the observed
baseline. There is no complete independent name initializer or qualified
deterministic tail policy yet.

Guessing a tail value or recording stack garbage as a creation constant would
not qualify the complete record model. The cheapest next evidence is local
static/dataflow analysis of exact `GetSpeciesName` and nickname setters/getters
(`0x080406C4`, `0x0803FBC4`, `0x0803F4B0`), plus isolated read-consumer tests to
qualify a deliberately chosen terminated-string tail policy. No new capture
is needed for this discriminator.

**Identity postprocessing and saved/runtime eligibility:** the constructor
queries flags828/913/930/12F8. Executing native FlagSet(913) in RAM before the
same fixed-PID constructor changes bytes0–3; the native IsMonShiny query changes
false→true. Species remains unchanged. A fixed PID argument therefore does
not by itself guarantee a non-shiny output or an E3-only eligibility gate.
This is exact machine evidence, not an upstream assumption or gameplay claim.

The path also reads controlled RNG state at03005040, a flag-routing byte at
03005ED8, bag runtime state at020397E4, and bytes0203DFC0/0203DFD0. The latter
addresses have supporting upstream fishing labels; their complete exact
game-load restoration and effects are not established here. The forced-shiny
path additionally reads the live battle flag03003569. Runtime-byte variants
that produce no differences do not prove all these inputs irrelevant.

Next derive exact FlagGet/save mapping for all queried creation flags, native
bag initialization/key state and the complete PID reroll/shiny predicate.
Then qualify a bounded owner-consistent non-shiny generator against native
nature/gender/form/ability invariants. Reject unsupported creation modes;
do not copy a game's shiny-forcing effect or expose PID/OT/shiny controls.
Separately reconstruct native current-region metadata from the saved map and
exact ROM before choosing origin defaults.

There is no qualified creator writer, full-record creator auditor, composed
transaction, creation GUI, acceptance return verifier or Human request in this
checkpoint. These depend on closing the above essential initialization rules.
The explicit-move fallback can remove the independent native learnset issue;
it cannot remove nickname/identity/origin initialization requirements.

## Reproduction and verification boundary

With Unicorn2.1.4 available, run locally with private inputs:

```sh
.venv/bin/python pokemonstart_v022_creation_probe.py --rom <private-exact-ROM> --save <private-ordinary-save> --broad
.venv/bin/python -m unittest discover -s tests -p test_v022_creation_probe.py -v
.venv/bin/python -m unittest discover -s tests -v
```

Host JIT permission may be necessary. The three synthetic gate tests require
no Unicorn installation/execution: wrong ROM, corrupt save and saved facility
context reject before importing the native engine. Exact probes independently
rehash their ROM/save inputs after completion. Their stdout is sanitized
semantic/address metadata, not a protected-data export.

Final candidate validation is rerun after push; exact SHA/tree, counts, skips,
probe counts and protected-diff scan are reported with the handoff. Earlier base
tests or broader partial-constructor checks do not substitute for a qualified
E4 creator or tests of an exact later writer candidate.

All existing product behavior is preserved. Full-Party Box-not-supported
rejection, first eligible slot, count+1, separate non-overwriting output,
checksums, untouched Party/unrelated state/footer, composition conflict checks,
localhost/stale-state GUI and grouped two-Pokémon Human acceptance remain
requirements for E4-B after E4-A closes; none is claimed newly implemented.


## Continued focused investigation (2026-10-07)

Remote main and candidate were freshly fetched before continuation; main
remained `381bc80080919952c9a32bb7982dfcf24bc92ea5` and candidate began at
`a8c905b91f42e8e970d868ff6d285f945ff0d7a0`. Issues/PRs remained empty.
The controlling E4 contracts were freshly read; no authority was inferred
from the user-supplied SHA or this checkpoint's prior conclusions.

### Experimental correction

The original probe placed reconstructed SaveBlock1 at02021000. That range
intersected native gPlayerParty020241E4 and count02023F89. This does not
constitute a fully restored runtime and its helper behavior must not be
qualified from that placement. The probe now places SaveBlock1 at02010000
and SaveBlock2 at02014000, disjoint from target, output buffers, native Party,
parasite and stack, and explicitly restores the six saved Party slots/count.
The evidence index retains the original checkpoint separately and provides
fresh results under corrected placement. Bag/key/runtime state is still
partial; this correction is not a claim of complete game-load restoration.

### Nickname counterexample and stop

The new read-only `pokemonstart_v022_creation_initialization_probe.py` varies
only bytes after the first FF nickname terminator in eight ordinary species
with encoded lengths4/5. Four synthetic fills (00/FF/A5/5A) are adversarial
controls, **not** proposed padding. Exact GetBoxMonData0803F4B0 (field2),
GetMonData0803F354 (field2), and Party-facing GetMonNickname08120AD0 all
transport the changed tail into their output buffers. The copied terminated
prefix is identical; the complete copied buffers differ. Native StringLength
08008984 and StringCompare080089A4 return equal results; E3 reconstruction
and eligibility are unchanged. These facts do not establish summary/battle
consumer equivalence, default-name detection across all call sites, or normal
save serialization equivalence. The fixed-field getter is already a concrete
counterexample to “every consumer is terminator-bounded.”

Static navigation around GetSpeciesName080406C4 and SetBoxMonData0803FBC4,
and the exact executed getters, identified the stack-derived tail versus
fixed-field transport. Native garbage must not be reproduced. No zero/FF
canonical padding was selected, because full downstream equivalence has not
been proven. A complete independent baseline is therefore not added.

**Single cheapest next discriminator:** exact-ROM dataflow from the nickname
buffers produced by GetMonNickname/GetMonData into ordinary summary, default-
name detection and battle consumers, coupled with the same paired-tail RAM
execution. This determines whether transported tail is only opaque storage
or actually observed. It needs no new capture or Human movement/gameplay.

### Saved creation flags and runtime boundary

Native FlagClear0806DE9C then FlagSet0806DE74 identifies the bit even when
the retained save already has it set. Native FlagGet0806DEC4 agrees with the
independent saved bit reads in measured contexts, under controlled routing
byte03005ED8=0. These are logical section offsets, not physical sectors:

| Flag | Saved source | Construction evidence / creator status |
| --- | --- | --- |
| 0828 | section1 FE5 bit0 | queried by helper090B7380; native Party now restored; full helper/default-mode qualification unresolved |
| 0913 | section0 F26 bit3 | constructor direct branch; native set changes supplied personality and native shiny false→true; reject true is proposed ordinary creator predicate |
| 0930 | section0 F2A bit0 | E3 facility predicate remains controlling and rejects before execution |
| 12F8 | section4 E0B bit0 | helper090B7E6C also queries saved bag item833; complete construction effect unresolved |

The constructor separately calls native bag lookup for item471. Numeric
item/flag identities are observed exact call arguments; upstream labels are
not used as proof of integrated semantics. Extra-section parasite flags may
be outside their base checksum envelopes, as in the canonical E3 mapping.

Adversarial controls (1/2/all-bits-set) at each of the six requested runtime
addresses were run under native-cleared0913. No-change observations are
explicitly insufficient to claim irrelevance:

| Runtime input | Current classification |
| --- | --- |
| 03005040 | controlled RNG; fixed-PID/fixed-IV variants observed unchanged, but random-generation policy not qualified |
| 03005ED8 | required flag-routing runtime state; saved reconstruction/alternate-routing behavior unresolved |
| 020397E4 | required bag runtime pointer/state; adversarial values fail native execution; valid saved-bag reconstruction unresolved/blocking |
| 0203DFC0 | required runtime-dependent helper input; tested values unchanged, broader conditional reachability unresolved |
| 0203DFD0 | required runtime-dependent helper input; tested values unchanged, broader conditional reachability unresolved |
| 03003569 | observed in special shiny branch; false0913 variants unchanged; no global irrelevance claim |

The 0913 fail-closed predicate closes the observed saved shiny-forcing mode,
not every constructor mode. No personality generator, domain-wide native
nature/gender/form postcondition claim or arbitrary identity controls were
added. Their qualification is deferred at this concrete record-model stop.

### Origin progress and remaining generalization

Native current-region08055B20 reads SaveBlock1 bytes4/5 (saved map group/num),
then map-header lookup08054AF8: exact group pointer table089A3D6C, group table
entry[num], header byte14. The independent read-only lookup agrees with native
execution in retained contexts; their distinct map keys and results are in the
evidence index. Retained snapshots are existing private-save evidence, not
new gameplay attestation or a source-hash creator whitelist.

Synthetic owner section0 byte8 controls0/1 and levels1/3/20/100 establish met
level=input, met game4, OT gender=owner byte8 bit0 for admitted ordinary gender
values, and packed origin bits11–14 clear in this matrix. These are machine
controls, not claims about two natural owners. The regionFF alternative and
safe bounds for arbitrary map-table indices are not yet qualified; merely
checking that a ROM pointer is in range cannot qualify general map validity.
No constant met location or captured-record replay was introduced.

The full 100-byte matrix above retains explicit blockers rather than silently
promoting observations into independently qualified initialization. Explicit
moves with empty slots/PP zero and occupied exact-table PP/PP-Up zero remain
the smaller proposed surface; automatic learnsets were not allowed to delay
this stop. No complete baseline, save writer, GUI, Human request, E5 expansion,
merge, Box mutation or public protected-data payload was added.

Reproduce the additional discriminators with private exact inputs:

```sh
.venv/bin/python pokemonstart_v022_creation_initialization_probe.py --rom <private-exact-ROM> --save <private-ordinary-save>
.venv/bin/python -m unittest discover -s tests -p 'test_v022_creation*probe.py' -v
```

The added two malformed map-pointer tests use synthetic bytes and do not
establish exact-ROM semantics. Exact pushed-candidate test counts and source
immutability checks are supplied in the handoff, after freezing the candidate.
