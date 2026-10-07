# E1 exact count-cache investigation: concrete stop

> Historical checkpoint. The current restricted-state E1 decision is in
> [e1-restricted-state-qualification.md](e1-restricted-state-qualification.md);
> the implemented E2 candidate and completed combined Human gate are in
> [e1-e2-inventory-candidate.md](e1-e2-inventory-candidate.md).
> Earlier STOP/unknown-field statements below describe the preceding checkpoint.


Disposition: **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE**.

Fresh canonical base: `785e113fa1885ac17e19da842a74740f62a8e789`.
Input candidate: `45c709f0bd7649a6762bcb6905c21e8b5b1527ba`, tree
`688e0cafb004ae055b5288ab6b16378c0cfa9b78`.
Issue #20 is open; PR #21 remains draft. Findings are candidate evidence,
not canonical adoption or an independent-review disposition.

## Exact-build finding

The owned ROM was freshly hashed and inspected. Region fingerprints and
fresh private snapshot reproduction are in
[the sanitized evidence](e1-count-cache-exact-results.json).
No ROM bytes, disassembly, extracted proprietary tables or private paths
are published.

The supporting upstream `sBagItemAmounts` clue correctly locates an array
of three halfwords at RAM `0x0203C6C2`. The array corresponds to regular,
Key Item and Ball menu counts. The first entry is sector30 `0x716`, then
`0x718` and `0x71A`. However, the exact regular calculation is materially
different from the proposed universal occupied-record count.

Exact control flow:

1. The installed bag-count hook at `0x081098C0` redirects to bridge
   `0x09036518`; the bridge calls count computation `0x090D3D74`, before
   returning to the ordinary menu continuation.
2. `0x090D3D74` iterates the three pockets. Its regular branch calls
   `0x090B8274` with the actual regular RAM base and capacity 700, then
   stores the returned halfword at `0x0203C6C2`. Later iterations store
   Key Item and Ball counts at the next two halfwords.
3. The regular helper allocates a temporary record buffer and reads flag
   `0x12EB` through exact `FlagGet` at `0x0806DEC4`. It calls the binary
   item classifier at `0x090B81F0` for each nonzero item ID. It copies
   matching records first, then nonmatching occupied records, copies the
   assembled records back and zeros the remaining tail. Within each
   classification group the traversal preserves relative order and copies
   complete four-byte records. The returned count is the number in the
   **matching classification group**, rather than their combined count.
4. Allocation failure takes a different branch: it counts an occupied
   prefix without performing that partition. Neither allocator success
   nor failure is a save-format eligibility predicate by itself.
5. `0x090D3E28` reads array entry `pocket * 2` for pockets 0..2, returning
   zero for later pockets. `0x090D3E40` indexes it with the current pocket.
   Additional direct references in cursor adjustment (`0x090D3A30`) and
   list/menu code using literals at `0x090D42F4` and `0x090D44E0` confirm
   that the array is consumed as menu state. All consumer boundaries and
   their associated item-index translation are not yet fully qualified.

The exact extended flag-address helper at `0x090EB4F0`, reached by the
installed `FlagGet` address-resolution hook, maps flag `0x12EB` into
parasite RAM `0x0203B225`, bit 3. The existing exact scatter mapping places
that byte at active logical section4 `0xE09`. This identifies a concrete
candidate eligibility input; it does not authorize changing a game flag.

The classifier gives medicines 13..22 and preserved Venusaurite 533 the
same classification, zero. A mixed list with records of both classifications
is a structural counterexample to the proposed total-count coupling:
successful regular recomputation returns only the selected group's count
and can reorder a compact input across classification groups. No invented
private save or game transition was used as evidence for this conclusion.

## Why the four native snapshots still agree

| Snapshot | Regular occupied | Saved array: regular / Key / Ball | Flag 0x12EB |
| --- | --- | --- | --- |
| PRE | 3 | 3 / 11 / 1 | clear |
| POST_DELETE | 2 | 2 / 11 / 1 | clear |
| POST_ACQUIRE | 3 | 3 / 11 / 1 | clear |
| POST_STACK | 3 | 3 / 11 / 1 | clear |

Every retained regular item has classification zero. Thus these transitions
do not discriminate selected-group count from total occupied count. They
remain valid native deletion/insertion/stack evidence for the observed
state; they cannot independently justify the proposed cache interpretation
for other compact, unique, catalog-valid regular lists.

Both read-only reconstruction paths were freshly run against all four
snapshots and agree on every pocket record and hole. The ROM and four
snapshot bytes were unchanged by inspection. The flag and array observations
are fresh file facts, independent of the Human's qualified gameplay
attestation recorded in the native-transition packet.

## Gate and cheapest grouped discriminating proof

Work Package A explicitly requires a stop if exact-ROM investigation finds
something materially different. The actual custom partition/count path is
that finding. No E2 core, GUI or save writer was changed. Work Packages B-E
are not claimed complete and E1 is not qualified.

A promising restricted predicate is: flag clear, every regular record in
classification zero, compact valid input and cache equal to occupied count.
For the inspected regular helper, that would make its successful partition
an identity on record order and make selected count equal total count.
This is an exact local consequence of the inspected helper, **not yet a
qualified whole-flow exclusion**. The cache alone is insufficient to reject
all problematic states, especially an empty pocket.

The cheapest next proof is one grouped **static** closure, not another Human
transition:

- Trace all regular-list construction/index-translation and mode-toggle
  callers of the classifier, flag and count helpers. Establish whether the
  proposed restricted predicate remains sufficient through ordinary load,
  menu rebuild, sort and SAVE, including an initially empty pocket.
- Corroborate raw flag/cache serialization on both save and load, and the
  alternate runtime-bag exclusion. Do not write the flag to select a mode.
- Qualify a read-only predicate shared semantically by two independent
  paths; reject other classifications/modes if exclusion is defensible.
- In the same batch close medicine use/display quantity bounds and the
  bounded relevant anti-cheat/sort hook topology. Then rebuild E1 before
  considering add/set/remove. Existing low-quantity evidence and catalog
  metadata alone remain insufficient for these remaining gates.

No further Human gameplay or high-quantity canary is requested. If this
grouped static proof qualifies the restricted state, E2 can use total count
only under that predicate. Broader classified-bag editing would require its
own semantics and is not implicitly authorized by this finding.

## Current E1 criterion matrix

PASS here is bounded to the described read-only capability; it never grants
writer authority by analogy. Earlier packets retain detailed mapping and
primitive evidence. New exact findings supersede the former unknown-field
hypothesis but do not retroactively upgrade every earlier criterion.

| Criterion | Status | Limit |
| --- | --- | --- |
| Exact profile identity | PASS | Fresh actual ROM hash |
| Complete storage/scatter map | PASS, candidate evidence retained | Exact descriptor/serialization findings and existing boundary tests; no new writer |
| Exact-ROM catalog extraction | PASS | Fresh actual catalog extraction; existence is not authority |
| Independent read-only decoder/auditor | PASS | Fresh equality on all four retained native snapshots |
| Supported medicine selection | NOT ESTABLISHED for writer | IDs 13..22 have regular/importance0 metadata and common medicine callbacks; behavior qualification remains |
| Supported quantity range | NOT ESTABLISHED | Exact 999 stack bound retained; reader/display/use closure incomplete |
| Insertion primitive | PASS, bounded | First-free primitive plus observed T2; whole E2 coupling incomplete |
| Quantity update primitive | PASS, bounded | key0 halfword representation and observed T3 |
| Removal primitive | PASS, bounded | Zeroing primitive and observed T1 |
| Persisted compaction/order invariant | NOT ESTABLISHED for proposed general predicate | Native three-entry case passes; custom partition can reorder mixed classifications |
| 0x716 identity | PASS | Regular selected-group menu count, not universally total occupied count |
| E2 count/cache coupling | NOT ESTABLISHED | Whole-flow classification/mode exclusion required |
| Checksums / global extra sectors | PASS, candidate evidence retained | Unchecked tails/shared-sector limitations remain |
| Unsupported-state rejection | PASS for existing reader; incomplete for writer | Reader rejects key/alternate bag/malformed records; classification, holes and cache are not writer gates yet |
| Relevant custom/sort/anti-cheat closure | NOT ESTABLISHED | Custom partition proven present; global absence not claimed |
| Regular slots 324/325 boundary | PASS for read-only model | Existing focused synthetic tests freshly pass |
| Unrelated pockets/Party/Money preservation | PASS for retained native observations; NOT ESTABLISHED for E2 | No E2 output exists |
| Give All disabled | PASS | No expanded writer/UI exists |

## Verification

Focused inventory tests freshly pass: **9 tests**. Full repository unittest
discovery freshly runs **238 tests: 223 passed, 15 skipped**, no failures.
All **104 tracked Python files** parse; the four candidate Python files
compile. These are current runs against the unchanged implementation at
input candidate HEAD, not E2 verification or a substitute for Human acceptance.

Current `git diff --check`, evidence JSON parse, candidate private-path scan,
tracked protected-suffix scan and redacted Gitleaks scan of `docs` pass.
The original frozen normal-save source hash also reproduces unchanged.
Only the three documentation files in this checkpoint change; the entire
candidate diff still includes the preceding read-only model/auditor/probe
and their tests. Exact final packet HEAD/tree are recorded in draft PR #21
after commit, avoiding a self-referential identity claim here.

No independent review, canonical adoption, main merge, Stable promotion or
release was performed. Protected files remain private and outside Git.
