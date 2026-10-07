# PokemonStart v0.22 practical product correction re-review packet

## Review target

- Canonical base: `main` at `7e7435c5507abfec183c3b370dcb1fa381b22186`.
- Candidate branch: `codex/v022-practical-product-sprint`.
- Predecessor implementation reviewed with `CHANGES_REQUESTED`:
  `7b84f7f940ea110f9839baa6fe14550a4f08e0bb` (tree
  `62ec5ccd7fe7000d25055833a3e17a92251d0e62`).
- Predecessor review packet commit:
  `5350f62b60d246cb724a7815641cfd3245f8b2dd`.
- Corrected implementation commit:
  `53a96ffdc9281b5cc8f1108150943a4a0ad0e881` (tree
  `af5e7b06484be8ca9405240ba6e5b47a54cac75c`).
- Packet-bearing candidate state: the candidate branch tip containing this
  packet and the exact correction diff artifact. Its immutable commit OID is
  supplied in the push handoff; fetch and verify the branch tip before review.
- Exact predecessor-to-corrected-implementation diff:
  [`v022-practical-product-correction.diff`](v022-practical-product-correction.diff)
  (SHA-256 `947d17cb0dd706be4dc6d783f4a559407b837268f7c52f6a9eb056ee9b6c21ee`,
  700 lines). Reproduce with:
  `git diff --binary 7b84f7f940ea110f9839baa6fe14550a4f08e0bb 53a96ffdc9281b5cc8f1108150943a4a0ad0e881`.

This is a claim and evidence index. It contains no review verdict. The previous
independent disposition was `CHANGES_REQUESTED`; a separate fresh-context
reviewer must determine the new disposition without relying on maker reasoning.

## Scope and exact corrections

Only the four requested bounded corrections were made. No terminal criterion
or product scope changed.

1. **Unqualified level-6 stat calculation.** The exact upstream integration
   revision remains unestablished, so the candidate no longer selects either
   disputed formula for level 6. Stat-changing requests and Level/EXP requests
   that result in level 6 reject. Level-5 stat operations remain available
   when their cached-stat and record predicates pass. The GUI has no writable
   Level control, bounds EXP to the level-5 range, and displays an explicit
   read-only reason for level. Level-6 records show Level/EXP as read-only.
   Friendship and bounded Move 1 retain their independent predicates,
   including on a level-6 record where those predicates pass.
2. **Antidote key gate.** `_observed_antidote_state()` now enforces key0 before
   accepting the observed prefix/tail shape. Both direct insert and remove
   helpers reject a structurally valid nonzero-key save. No nonzero-key support
   was added.
3. **Exact Rattata import writer.** The production module no longer exports
   `build_candidate(raw, record)`. `derive()` checks exact ROM, source SHA and
   full-record SHA before reaching its single bounded count/record/checksum
   write path. Generic expected-byte construction remains in the independent
   audit module and tests. The supported claim remains one exact source plus
   one exact complete game-generated record.
4. **Evidence ledger.** The earlier no-R4 / blocked-Inventory paragraph in
   `docs/evidence.md` is explicitly labeled as an interim state superseded by
   later evidence. The R4 and native Inventory evidence itself was retained.

The sanitized candidate evidence also records that no new Human gameplay was
gathered for these code guards, the existing R4 evidence was not changed, and
no new terminal scope was introduced.

## Validation

- Focused product tests in the existing NiceGUI environment: **17 passed**.
- `python3 -m unittest discover -s tests -v`: **229 run, 209 passed,
  20 skipped, 0 failures**.
- `.venv/bin/python -m unittest discover -s tests -v`: **229 run, 214 passed,
  15 skipped, 0 failures**. This includes NiceGUI upload/preview/download
  simulation and the level-5/level-6 control checks.
- Tracked Python compile: **100 files passed**.
- Candidate product module import validation: **6 modules passed**.
- Tracked JSON parse: **5 files passed**.
- `git diff --check`: **PASS**.
- Gitleaks on the changed tracked files: **no findings**. The broad no-Git
  worktree scan reported three generic-key findings only in ignored `work/`
  browser dependency assets; none are tracked candidate files. The correction
  commit hook also scanned the commit content with no findings.
- Protected-suffix scan: no tracked `.sav`, `.gba`, `.pks`, `.bps`, `.ips`,
  executable, library or ROM paths. The correction diff contains no absolute
  private artifact-root reference. Private originals were not changed or
  copied into Git.

See `docs/v022-product-candidate-evidence.json` for the sanitized follow-up
record and the completion evidence for the preserved R1–R4 evidence classes.

## Remaining qualification gaps and non-claims

- A level-6 stat-changing output remains unsupported until exact-build formula
  evidence exists. No speculative source-to-ROM identity claim is made for
  CFRU-JP commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`.
- No new normal-save round trip was performed for stat-changing output or for
  a GUI-created Antidote edit.
- Broader item IDs, capacity, later-slot compaction and Give All remain outside
  this correction. Arbitrary Pokémon synthesis, species constructors, Box,
  Pokédex/story/event/RTC editing, other game versions, Stable promotion and
  public release remain unclaimed.
- The Rattata game proof remains one exact complete record import. It is not a
  generic template feature or arbitrary Pokémon creation claim.

## Authority boundary

The controlling authorization remains
`AUTHORIZE V0.22 PRACTICAL PRODUCT SPRINT REALIGNMENT AND BOUNDED R1-R4
IMPLEMENTATION`. It permits this bounded candidate correction, candidate
commit and candidate-branch push. It does not permit merge/adoption on `main`,
Stable promotion, public release, another build, broader editor scope, or
protected-data publication. No merge or release is requested or implied by
this packet.

## Required independent reviewer checks

1. Fresh-fetch and verify canonical `main`, the candidate branch tip, this
   packet-bearing commit, the corrected implementation commit/tree, and both
   predecessor identifiers above.
2. Inspect the exact diff artifact and independently confirm all four findings
   are corrected without expanding capability or weakening tests.
3. Inspect the stat capability and GUI paths, including level-5 output bytes,
   level-6 rejection, and independent Friendship/Move 1 behavior.
4. Verify both Antidote direct helpers enforce key0 before writes.
5. Verify every production template-import write is unreachable until the
   exact source and complete-record SHA gates pass, and that no generic writer
   surface remains.
6. Reconcile the evidence ledger and preserve separate Human, private-input,
   candidate, canonical and upstream evidence classes.
7. Confirm test/scan results and protected-data/authority boundaries. Do not
   perform merge, release, Stable promotion or scope expansion as part of this
   review.

Permitted dispositions: `APPROVED_FOR_HUMAN_ADOPTION_DECISION`,
`CHANGES_REQUESTED`, or `BLOCKED_WITH_CONCRETE_EVIDENCE`. Approval is a review
disposition only and does not itself authorize adoption, merge or release.
