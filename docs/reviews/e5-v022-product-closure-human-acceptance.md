# E5 exact-v0.22 product closure — Human acceptance and return evidence

Disposition: **READY_FOR_INDEPENDENT_REVIEW**. Not reviewed, not adopted, not
merged, not released. This is a reporting-only record; the implementation
candidate is unchanged.

## Identities

- Canonical `main` at completion: `5864e7ada132408d39df8cc3dc2b56a75805b24a`
  (fresh-fetched 2026-10-08; unchanged during E5).
- Human-played implementation: `70c9894c7b104e144f727b283bd7eda7fdabd487`,
  tree `f3ec70adf8e4c99936d311708edca98b004b11b7`.
- Prior reporting head: `42a43e62c19ef58e316a93051e45b7e90b032bd4`
  (docs only). This record adds only this file.

## Machine evidence (Maker-recorded, private inputs outside Git)

Classification: local private-input machine verification on exact v0.22 with
installed stock mGBA 0.10.5. Not independent reproduction.

- Cycle 1 GUI export: `GUI_OUTPUT_EQUALS_INDEPENDENT_CORE_AND_AUDIT`
  (money, party_0, items, create); source and ROM immutable.
- Cycle 1 return after one normal SAVE: `MACHINE_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED`;
  counter 12→13, previous active slot preserved, normal section rotation,
  Money/Inventory persisted, independent E4 complete-output audit equal,
  continued E1–E4 eligibility. Gameplay drift reported only for Party #1 and
  created #5: EXP, EVs and move PP. A pre-existing non-supported regular item
  was preserved unchanged.
- Cycle 2: the progressed Cycle 1 return was reopened in the actual GUI
  without a preregistered source hash; Party #5 Friendship 50→51 via
  Preview/Verify/Export; `GUI_OUTPUT_EQUALS_INDEPENDENT_CORE_AND_AUDIT`
  (party_4).
- Cycle 2 return after one normal SAVE: `MACHINE_CYCLE2_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED`;
  counter 13→14, previous active slot preserved, normal rotation, independent
  E3 audit equal, Friendship 51 persisted, Money/Inventory unchanged,
  continued E1–E4 eligibility.
- Full discovery on the owner host at the implementation tree:
  309 tests, OK, 15 Windows-specific skips (NiceGUI tests included). In the
  agent sandbox those NiceGUI tests cannot start (process-pool semaphore
  denial); that environment limitation is not counted as a pass.

## Human gameplay attestation (owner's words, summarized without extension)

- Cycle 1: game displayed normally; no visible corruption, crash or freeze;
  Bag also contained フシギバナイト ×1; hidden stats (IVs/EVs) are not
  visible in the ordinary UI and were not verified visually; one normal SAVE
  completed and mGBA was fully closed.
- Cycle 2: Pokémon display normal; SAVE succeeded.

Not claimed: visual verification of IVs/EVs/friendship values, specific
battle outcomes, or field-by-field in-game comparison.

## Observation for the reviewer

The Cycle 1 recipe set Party #1 Move 1 to Growl while Move 2 was already
Growl, producing a duplicate move. This is existing adopted E3 behavior
(no duplicate-move guard) and loaded/saved normally, but the reviewer should
decide whether it warrants a separate follow-up.

## Next gate

Fresh-context independent review per
`docs/reviews/e5-v022-product-closure-independent-review.md`, then a separate
explicit Human adoption decision. No merge, release or Stable promotion is
implied.
