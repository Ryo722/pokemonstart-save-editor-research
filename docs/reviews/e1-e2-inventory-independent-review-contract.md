# Fresh-context independent review contract — E1/E2 inventory expansion

Review target: the exact candidate packet produced from the E1/E2 Codex work.

## Review mode

Use current GitHub remote state as canonical evidence.

Fresh-read:
- current `main`;
- `README.md`;
- `docs/decision-record.md`;
- `docs/v022-pkhex-like-editor-expansion.md`;
- `docs/e1-e5-implementation-readiness-research.md`;
- exact candidate branch / HEAD / tree;
- candidate evidence packet and complete diff;
- relevant implementation/tests.

Do not use prior chat conclusions, maker reasoning, packet-preparation reasoning, or old reviewer conclusions as review evidence.

Do not mutate GitHub, private files, emulator state, or protected artifacts during review.

## Controlling questions

### 1. Exact candidate identity
- Is candidate HEAD exact and unchanged?
- Is canonical base exact?
- Is the diff fully bounded and reviewable?

### 2. Evidence separation
- Are exact-v0.22 reproduced facts separated from upstream CFRU/FireRed source evidence?
- Are inferred mappings independently corroborated rather than silently promoted?
- Is any claim based on an unproven assumption about the integrated upstream revision?

### 3. Scatter serialization model
Adversarially verify:
- section0 / section4 / section13 parasite mapping;
- regular-item start at section13 `0xADC`;
- regular slot 324 -> 325 transition into sector30;
- pocket starts/capacities used by the candidate;
- any extra-sector bytes touched;
- checksum-covered vs non-checksum-covered regions.

A writer must not treat section13 alone as the entire regular pocket if the qualified model spans sector30.

### 4. Exact-ROM item catalog
- Is the catalog derived from the exact-v0.22 profile/ROM rather than copied from upstream constants?
- Are names/pockets/importance validated?
- Are invalid/placeholder/out-of-range entries rejected?
- Is the safe product allowlist narrower than raw item-table existence where story/event risk is unresolved?

### 5. Quantity / key semantics
- Is the supported quantity range actually qualified?
- Does key0 handling match current evidence?
- If nonzero-key is unsupported, does the implementation fail closed everywhere instead of partially decoding/writing it?

### 6. Insertion/removal/order
- Does insertion follow the established first-free/order model?
- Does removal implement the established zero/compaction behavior at the correct time?
- Are middle-slot cases tested?
- Are regular-pocket sort/config behaviors accounted for?

### 7. Capability scope
For each GUI/API operation, can the reviewer trace:
user action -> capability predicate -> exact bytes -> independent decode -> postcondition?

Reject capability broadening by analogy.

### 8. Give All Supported Items
If present, require all:
- exact safe catalog;
- proven capacities for every included pocket;
- deterministic duplicate handling;
- quantity policy;
- no Key Item/event/story entries;
- output audit;
- exact-v0.22 game/save evidence.

If any prerequisite is missing, Give All must be absent/disabled. Its absence is not a blocker for E2.

### 9. Safety and recovery
- source ROM/save immutable;
- separate output only;
- stale-state protection preserved;
- malformed/ambiguous state fails closed;
- protected artifacts absent from Git;
- public/LAN exposure not introduced.

### 10. Verification
- focused and full tests pass;
- boundary slots around storage-fragment transitions are covered;
- independent auditor is meaningfully separate from the writer;
- private exact-v0.22 evidence is adequate for the capability actually claimed;
- no test proves only a mocked predicate while production mapping remains untested.

## Review disposition

Use one:

- `APPROVED_FOR_HUMAN_ADOPTION_DECISION`
- `CHANGES_REQUESTED`
- `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`

Approval means the exact candidate may be presented to the Human for canonical merge/adoption. It does **not** itself authorize merge, release, Stable promotion, or scope expansion.

## Forward-look check

If E1/E2 is approved, briefly verify whether E3 remains the cheapest goal-aligned next milestone using fresh evidence. Do not automatically expand into E3 inside this review.
