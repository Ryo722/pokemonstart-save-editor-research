# E5 product-closure fresh review packet

Status: **prepared; independent review not performed**. This packet is for a
fresh reviewer after Human acceptance and return verification. It does not
represent approval or adoption.

## Candidate identity

- Canonical base: `5864e7ada132408d39df8cc3dc2b56a75805b24a`
- Implementation candidate: `70c9894c7b104e144f727b283bd7eda7fdabd487`
- Implementation tree: `f3ec70adf8e4c99936d311708edca98b004b11b7`
- Branch: `codex/e5-v022-product-closure`
- Review the later reporting-only commit separately; do not mistake its
  documents for implementation changes.

## Read set

Fresh-fetch GitHub `main` and this candidate. Read `README.md`,
`docs/decision-record.md`, `docs/evidence.md`,
`docs/v022-pkhex-like-editor-expansion.md`, E1/E2 adoption and qualification,
E3 qualification and review, E4 qualification/review/acceptance, current
product core/GUI, all relevant product/GUI/acceptance tests, this E5 candidate
record and the eventual Human evidence record. Query current open issues and
pull requests. Reconstruct E0–E4 adoption, E5 scope, authorization and
protected-data boundaries from the fresh canonical records.

## Review questions

1. Does the GUI expose all six Party positions and present supported existing
   Party fields in a usable Main/Stats/Moves organization?
2. Are unsupported identity/storage fields absent from normal editing?
3. Does creation remain E4 Party-only, first-empty sequential, and fail with
   the adopted full-Party refusal?
4. Does Inventory UX map only to adopted E2 requests? Does Money map only to
   its adopted request? Do E3 and E4 controls map exactly to their existing
   request semantics?
5. Does the one-family-per-failed-capability behavior remain fail-closed and
   allow unrelated adopted families only as already authorized?
6. Does the shared GUI preserve immutable uploaded bytes, exact-ROM checks,
   stale-preview rejection, re-derivation, verified separate output,
   exclusive private export and independent complete-output audit?
7. Does the actual GUI browser evidence cover the all-family transaction and
   full-Party behavior, with a loopback-only server and no protected data in
   Git?
8. Do Cycle 1 and Cycle 2 machine return checks prove normal SAVE transition,
   prior active-slot preservation, section rotation, requested state
   persistence, explainable gameplay drift, Inventory/Money consistency and
   continued applicable eligibility?
9. Are Human observations clearly kept separate from machine evidence, and
   are both returned saves checked after emulator close/flush?
10. Does the diff add any write authority, version support, protected data,
    private path, or unsupported claim?

## Fresh reviewer instruction

Use an independent context and fresh remote reads. Do not rely on Maker
conclusions as correctness evidence. Reproduce focused E5 and E1–E4 suites,
full discovery, browser checks and exact-v0.22 machine gates where available.
For private-input evidence, record only that a fresh check occurred and its
classification; never copy private saves, ROMs, receipts, paths, hashes or
secrets into Git or a public report. Identify platform skips precisely.
Provide findings with file/line and exact reproduction, or a reasoned review
disposition for a separate Human adoption decision. Do not merge or perform
any prohibited scope expansion. This prompt is a review plan, not evidence of
review completion.
