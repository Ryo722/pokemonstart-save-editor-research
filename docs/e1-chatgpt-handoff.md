# E1 / Issue #20: broader planning handoff for ChatGPT

> Historical checkpoint. The current restricted-state E1 decision is in
> [e1-restricted-state-qualification.md](e1-restricted-state-qualification.md);
> the implemented E2 candidate and completed combined Human gate are in
> [e1-e2-inventory-candidate.md](e1-e2-inventory-candidate.md).
> Earlier STOP/unknown-field statements below describe the preceding checkpoint.


Repository: `Ryo722/pokemonstart-save-editor-research`.
Open work: Issue #20, draft PR #21, branch `codex/e1-v022-inventory-model-qualification`.
Main at fresh preparation: `785e113fa1885ac17e19da842a74740f62a8e789`.
The tested/read-only-inspected implementation checkpoint is `98173a4dc0a2cd84710ea1110d6138f4899f80c3`; the current packet-bearing candidate HEAD/tree is in PR #21.

## Request

The Human wants the next effort planned as a coherent milestone, instead of repeatedly stopping after individual offsets or small checks. Please assess the current evidence and provide one bounded execution instruction covering the remaining E1 qualification and, only if that gate actually passes, the E2 candidate checkpoint. This is planning, not independent review or merge/adoption authorization.

Use current GitHub main as the sole durable canonical authority. Candidate findings below are provisional evidence to examine, not automatically adopted authority. Fresh-read the branch/diff and distinguish exact-ROM reproduced facts, native observed facts, upstream source support and unresolved hypotheses.

## Required reading

From current main:

- docs/decision-record.md
- docs/v022-pkhex-like-editor-expansion.md
- docs/e1-e5-implementation-readiness-research.md
- docs/e1-codex-handoff.md
- docs/reviews/e1-e2-inventory-independent-review-contract.md

From the current PR #21 candidate:

- docs/e1-inventory-candidate.md
- docs/e1-inventory-private-evidence.json
- docs/e1-inventory-publication.md (historical initial receipt)
- docs/e1-native-transition-results.md and .json (new results)
- current decoder/auditor/probe code and boundary tests
- complete diff and exact PR HEAD/tree

## Product objective and position

The earlier exact-v0.22 practical Party/Items/Money product is adopted and complete. The current authorized expansion is E1 inventory qualification, E2 practical ordinary-item editing, E3 general existing-Party editing, E4 Party-only ordinary Pokemon construction, E5 practical UX/acceptance. Money is maintenance-only. Do not restart R1-R4 or make Box, arbitrary all-items, another version, Stable promotion or public release prerequisites.

E1 is still **BOUNDED_STOP_WITH_CONCRETE_EVIDENCE**. E2 has not begun. No independent review has been performed.

## Evidence now available

1. The actual exact v0.22 ROM disagrees with the upstream layout candidate: 700 regular records, 75 Key Items, 50 Balls, 128 TM/HM and 72 Berries, with a 32-byte Key Items/Balls gap. Regular slots 0..324 are in section 13; 325..699 are in global sector 30. Exact descriptor, hooked code, private records and synthetic boundary tests support the candidate map.
2. An actual-ROM in-memory catalog derives 837 valid nonzero entries from the 839-entry, 40-byte item table. Catalog existence does not grant write authority. Proposed initial ordinary selection is recovery medicines 13..22, conditioned on exact metadata; broader safety remains unqualified.
3. The production read-only model and a separate RAM-reconstruction auditor cover all five pockets. Both reject nonzero key and the exact-build alternate ten-slot bag mode. Give All remains disabled.
4. The Human completed T1/T2/T3 using immutable inputs, a dedicated private working copy, normal SAVE, full mGBA exit and separately hashed/read-only snapshots. The reported absence of unintended operations is qualified by their recollection.
5. Four snapshots pass structural and both decoder checks at counters/statistics 11..14. Leading Potion removal compacts the remaining two entries by post-SAVE; Potion reacquisition appends at the first free slot; existing Antidote quantity goes 1 to 3 without reordering. Other decoded pockets and complete occupied Party records are unchanged.
6. T1/T2 also alter sector30 offset 0x716 in the non-pocket gap; T3 does not. Its semantics and necessary writer coupling are unknown. Do not label it a cursor/count solely from correlation.
7. Exact existing-stack code supports a candidate 999 bound, while native observations cover only small quantities. The key0 getter/setter model and broader native acquisition behavior must not be inferred from baseline FireRed alone.

## Decisions needed for the next coherent milestone

Please propose concrete deliverables and an objective stop gate for a batch covering:

- Identify the 0x716 field and relevant readers/writers from the exact ROM; decide with evidence whether E2 must update it, preserve it, or constrain eligibility.
- Trace removal, menu rebuild/compaction/sort and SAVE sufficiently to specify a safe ordinary-item writer policy. Determine which exact execution timing matters for an editor and which observed state constraints can safely bound other modes out.
- Qualify the quantity range and ordinary-item set needed for a useful first E2. Assess whether a narrowly supported range/subset can meet the canonical contract, or whether additional exact-ROM/native evidence is necessary. Do not silently broaden or weaken the adopted criteria.
- Identify relevant custom/anti-cheat/configuration effects for that capability. Specify the required completeness of evidence without turning global game-code absence into an unbounded research goal.
- Reconcile the E1 PASS / FAIL / NOT ESTABLISHED matrix, separating reproduced static/native facts from inference.
- If every necessary E1 gate passes, define the E2 core/UI candidate and representative normal-game acceptance matrix. Otherwise deliver one concrete bounded-stop packet identifying the cheapest discriminating proof, not repeated speculative canaries.

The code contract permits bounded E2 only after E1 qualifies. During this planning handoff, the Human has paused further analysis/implementation to obtain broader direction. Do not treat the proposed batch as already executed or newly authorized outside the canonical scope.

## Execution shape to preserve

Autonomous non-Human work should run through the agreed milestone without asking at every internal step. Stop for genuinely required Human gameplay/evidence, unresolved writer semantics, independent review or adoption boundaries. Group necessary native actions into a small clear matrix and prepare the full local operator procedure before asking the Human to act.

For native verification use the Human-preferred procedure recorded in e1-native-transition-results.md. Do not request protected files in ChatGPT or publish private paths. Inputs/snapshots stay outside Git; only sanitized semantics/hashes/diff metadata are publishable.

## Boundaries

No main merge, canonical capability adoption, independent review by the implementation agent, release, Stable promotion, other-version work, public/LAN GUI, unsafe Give All, Key Item/event/story/Pokedex/quest/RTC/Box writes or protected-data publication. Expanded writer candidates require a separate fresh-context independent reviewer and Human adoption decision.

## Desired response

Return one goal-oriented execution contract: recommended next milestone, grouped work packages with dependencies, capability-specific evidence gates, required Human transitions only where static analysis cannot discriminate, verification/publication deliverables, and clear terminal outcomes. Explain any proposed material scope change before recommending it. A new implementation is not requested from ChatGPT in this handoff.
