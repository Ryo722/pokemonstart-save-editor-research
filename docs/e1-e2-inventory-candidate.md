# E1/E2 restricted medicine candidate — accepted Human round trip

Disposition: **READY_FOR_INDEPENDENT_REVIEW**.
E1: **E1_MODEL_QUALIFIED_FOR_E2_CANDIDATE**.
This is an implementation candidate, not independent review or canonical adoption.
PR #21 remains draft. Human E2 normal-game acceptance is **PASSED**.

## Exact identity

- Fresh canonical base: `785e113fa1885ac17e19da842a74740f62a8e789`.
- Prior candidate input: `e8ec73ae547f6860a20f6adbab4f0a4dd87b830f`.
- Tested implementation: `ca564db324b41cdb326fcdbfd582a36521c67f24`.
- Tested implementation tree: `e2570e3799045747ac8b1ffd1ba308f475d0a104`.
- Packet commit follows the tested implementation and changes documentation only.
  Its exact HEAD/tree are recorded in the draft PR body, avoiding a self-referential hash.

The [restricted E1 qualification](e1-restricted-state-qualification.md) contains
the rebuilt complete criterion matrix, exact addresses and bounded topology.
The [sanitized machine packet](e1-e2-inventory-candidate-evidence.json) records
fresh private-input qualification, exact function-region hashes, isolated
execution, GUI/core/auditor equality and the completed acceptance recipe.
Its nested read-only qualification retains `writer_authorized: false`: that
field describes the diagnostic catalog/decoder, not the implemented E2 API.

## Eligibility and writer contract

Require exact ROM/profile/catalog, structurally valid consecutive normal save
epochs, ordinary bag mode, key0, flag 0x12EB clear, every occupied regular
record classification zero, valid unique IDs, quantity 1..999, compact prefix
and zero tail. All three persisted regular/Key/Ball menu counts must match
their compact lists; Key/Ball must retain a free record. Both independent
read-only gates enforce these conditions. No malformed input is repaired.

Sector30+0x716 is a **selected-classification menu count**, not a universal
occupied count. Only under this restricted predicate does it equal regular
prefix length. Add/remove recompute its halfword; quantity changes leave its
value unchanged. Key/Ball counts and selector flag are preserved. Mixed
classification, selector mismatch, alternate ten-slot bag, nonzero key,
holes, duplicate IDs, unsupported quantities and stale caches are rejected.

Set modifies an existing supported quantity. Add appends an absent supported
medicine after the prefix. Remove shifts remaining complete four-byte records
left in original relative order and zeroes the vacated tail. Unsupported valid
records remain read-only and retain exact ID/quantity bytes even when shifted.

Every write uses the section13/sector30 scatter mapping. Permitted inventory
byte envelope is active section13 0xADC..0xFEF, sector30 0..0x5DB, and
sector30 0x716..0x717. The independent auditor constructs the entire expected
output separately and requires full-byte equality, not just envelope inclusion.
Other pockets, Party, Money, selector, inactive slot and unrelated bytes are
unchanged by inventory-only edits. These regular tails/extra sector are outside
the normal checksum envelope; no checksum changes or crash-recovery claim.

## Qualified medicine allowlist

All ten exact-ROM entries have regular pocket, importance0, classification0,
type1, the checked common recovery callbacks and ordinary quantity semantics.
The explicit editor range is **1..999**; zero uses Remove.

| ID (research only) | Exact installed name |
| --- | --- |
| 13 | キズぐすり |
| 14 | どくけし |
| 15 | やけどなおし |
| 16 | こおりなおし |
| 17 | ねむけざまし |
| 18 | まひなおし |
| 19 | かいふくのくすり |
| 20 | まんたんのくすり |
| 21 | すごいキズぐすり |
| 22 | いいキズぐすり |

Catalog existence alone grants no edit authority. Venusaurite and all other
regular items are read-only. No Give All or other-pocket edit exists.

## GUI capability matrix

| Surface | Candidate capability |
| --- | --- |
| Open | Actual private exact ROM + uploaded save, both eligibility gates |
| Items | Supported names/quantities, quantity edit, Remove, absent-name Add Item |
| Unsupported Items | Visible read-only |
| Preview | Semantic add/set/remove changes; Party/Money composition preserved |
| Verify | Core derivation plus independent full-byte inventory audit |
| Export | Separate verified output; stale source/request/ROM guards |
| Optional host export | Existing private directory only, exclusive creation, mode600 |
| Network | Existing localhost-only server |

Normal controls expose no numeric item IDs, offsets, sectors or checksums.
Default verified download remains available; `--export-directory` optionally
retains output directly in a private host directory without a Downloads step.
Existing Party/Money behavior is regression-tested and unchanged.

## Current machine verification

Against the exact tested implementation above:

- Focused inventory suite: **36 passed**.
- Full suite: **256 run, 241 passed, 15 skipped**, no failures.
- AST and compilation: **107 repository Python files passed**.
- Exact ROM classifier: both independent predicates equal all 839 installed IDs.
- Isolated exact partition: 16 cases, occupancy 0/1/3/324/325/326/699/700,
  allocator success/failure; complete record order and returned count equal.
- Exact Add/Get/Remove: all ten medicines at 1/3/99/999, 40 cases; existing
  stacks reaching 1000 rejected without mutation. Probe intercepts allocator,
  FlagGet, memcpy and free. This is isolated function evidence, not gameplay.
- Four retained native T1/T2/T3 snapshots: both decoders/counts equal and eligible.
- Actual private editor tests: 19 distinct allowlist quantity-bound cases;
  composed GUI/core output, independent audit and byte envelope equal.
- Synthetic boundary add/set/remove at 0/324/325/699, cross-fragment compaction,
  full pocket, empty pocket, unsupported before/after targets, malformed states,
  duplicate/hole/cache/selector/classification/key/alternate-mode rejection.
- GUI stale-state rejection, Party/Money composition, exclusive output creation,
  real private host export/reference equality and overwrite refusal passed.
- Source ROM and retained saves unchanged; protected-artifact/private-path scan,
  redacted secret scan and diff whitespace check passed for the candidate packet.

Skipped tests require their separate private fixtures; they are not counted as
passing. Synthetic 700-record fixtures test storage mechanics, not availability
of 700 distinct ordinary items in this ROM. Isolated probes do not establish
global absence of custom game behavior. The bounded inspected topology and
fail-closed predicate define the supported capability.

## One combined Human acceptance gate — completed

Private workspace was prepared with an immutable copy of the naturally
progressed T3 save (counter14, SHA-256
`6e2c92c4e86b9436ca0647b6852b999eb107318d1356098a3cddafba11d8c55f`).
No emulator/gameplay transition was performed during implementation.

One GUI edit: どくけし 3→7, remove キズぐすり x1, add やけどなおし x11.
Expected regular order: フシギバナイト x1, どくけし x7, やけどなおし x11.
Expected separate output: 131088 bytes, SHA-256
`633dbfbdc95e6970c66de049bf44452e80a46e75afb89e22890ba89940b801fe`.
Only source-relative byte offsets 56034, 56036, 56038 differ in this recipe;
the regular count remains three. Separate machine/native cases cover changing
the derived count. The private machine reference is comparison evidence only;
Human must export the composed GUI output and load that output in the game.

The Human reports item editing and normal SAVE succeeded. The supplied retention
command confirms mGBA fully closed before snapshot. Visual observations are
Human testimony; machine reconstruction below is separate evidence.

Returned snapshot: **131088 bytes**, mode400, SHA-256
`39904e9943f594888af49f2deee7630f784154d148f63d6a47b471f52776f29a`.
Both restricted decoder and independently reconstructed RAM auditor agree:

- Exact regular sequence: Venusaurite1, Antidote7, Burn Heal11; Potion absent.
- All five pocket record sequences and three menu counts unchanged from GUI output.
- Complete 600-byte Party storage and count unchanged; all decoded Party equal.
- Money unchanged at 7,653,721; no purchase/use effect needs explaining.
- Returned save is E2-eligible with selector clear, neutral classification and
  compact valid list; normal save epoch advances counter14→15.
- Previous active slot remains byte-identical; all sections rotate one position;
  all 28 checksums pass; checksum-excluded tails and sectors28–31 unchanged.
- Saved-game statistic14→15; play time does not decrease. Every other logical
  payload delta is classified by the existing independent normal-transition
  model (`tests/m4_independent_game_transition_audit.py`), corroborated in
  `docs/m4-p-transition-model.md`: section0 0x11/0x12 play-time fields;
  section1 0x70C/0x71C/0x724/0x728/0x72C eventObjects[3] runtime flags,
  current X, facing/movement direction, movement action, previous direction;
  section2 0x210 saved-game statistic. No unexplained payload delta remains.
- The emulator's external 16-byte footer changed; it remains opaque under the
  existing normal-resave policy. No footer semantics are claimed.
- Source ROM, original source save, editor snapshot and returned snapshot remain
  unchanged by the read-only checks. Human input hash checks separately passed.

The private verification imported the independent transition classifier and
metadata reader, independently parsed sections, checked rotation/counters,
classified every payload delta and compared all Party bytes. No proprietary
byte values, payloads or private paths are published. These are implementation
verification checks, not the separate independent review of this candidate.

## Complete changed-file inventory from canonical base

Documentation: `e1-chatgpt-handoff.md`, `e1-count-cache-exact-results.{md,json}`,
`e1-inventory-candidate.md`, `e1-inventory-private-evidence.json`,
`e1-inventory-publication.md`, `e1-native-transition-results.{md,json}`,
`e1-restricted-state-qualification.md`, `e1-e2-inventory-candidate.md`,
`e1-e2-inventory-candidate-evidence.json` (all under `docs/`).

Code: `pokemonstart_v022_inventory_audit.py`, `pokemonstart_v022_inventory_editor.py`,
`pokemonstart_v022_inventory_model.py`, `pokemonstart_v022_inventory_qualification.py`,
`pokemonstart_v022_inventory_static_probe.py`, `pokemonstart_v022_product_core.py`,
`pokemonstart_v022_product_web.py`.

Tests: `tests/test_v022_inventory_editor.py`, `tests/test_v022_inventory_model.py`,
`tests/test_v022_product_web.py`.

No raw ROM/save/disassembly, proprietary table dump, patch, .pks or private
absolute path is included. No independent-review disposition is asserted.
Human acceptance has passed. Independent review and any adoption decision remain separate later contexts.
