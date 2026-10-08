# E5 exact-v0.22 product-closure candidate

Disposition: **E5_CANDIDATE_READY_FOR_HUMAN_ACCEPTANCE**. This is a bounded
candidate at the Human-acceptance handoff. It is not E5 terminal completion,
canonical adoption, independent review, merge, release, or Stable promotion.

## Authority and provenance

The canonical base was freshly fetched and verified as GitHub `main`
`5864e7ada132408d39df8cc3dc2b56a75805b24a`. The bounded candidate branch is
`codex/e5-v022-product-closure`. Implementation commit:
`70c9894c7b104e144f727b283bd7eda7fdabd487`, tree
`f3ec70adf8e4c99936d311708edca98b004b11b7`. This candidate is based directly
on canonical main. The separate v0.23+ read-profile research branch was not
incorporated.

Fresh canonical review covered `README.md`, `docs/decision-record.md`,
`docs/evidence.md`, `docs/v022-pkhex-like-editor-expansion.md`, E1/E2
qualification and adoption records, E3 qualification/review, E4
qualification/review/acceptance, current product core and GUI, product/GUI/
acceptance tests, and current GitHub issues and pull requests. No open issue or
pull request changed the scope. The evidence supports the boundary disposition
`E5_REMAINS_NEXT`.

The current user request authorizes bounded E5 implementation, tests, local
machine/browser qualification, preparation of a private Human kit, and fresh
review preparation. It does not authorize merge/adoption, release, Stable, or
new write semantics.

## Adopted capabilities and E5 boundary

E0 exact-v0.22 source/ROM profile and local exact-ROM gate remain controlling.
E1/E2 adopt only the supported recovery-medicine Inventory subset. E3 adopts
the existing ordinary Party edit subset. E4 adopts Party-only ordinary
Pokémon creation beginning at the first empty position; a full Party fails
with `Box creation is not supported`. Money remains within the adopted
0–9,999,999 range. E5 composes these existing capabilities; **no new write
authority or save semantics were added**.

E5 remains exact-v0.22 and local-only. Box editing/creation, nickname, PID,
shiny, OT and other identity controls, unsupported Ball editing, Pokédex,
story/event/quest/RTC, broader items, Give All, other game versions,
LAN/public serving, packaging/release and Stable promotion remain outside
scope. Unsupported fields fail closed or remain read-only.

## Product UX contract

The actual GUI remains a localhost-only NiceGUI application. The normal flow
is `Open Save → Edit → Preview → Verify → Export`, with explicit current stage.
Uploaded source bytes remain immutable; exact-ROM checks, stale-preview
invalidation, re-derivation, verified separate output, exclusive private host
export and independent composed auditing are retained.

Party represents all six positions. Occupied supported members group semantic
controls under Main, Stats and Moves; unsupported identity/storage internals
are absent from normal editing controls and can remain in collapsed
diagnostics. Empty slots expose sequential creation only when eligible, and
full Party creation is explicitly refused. Items are presented as Item,
Quantity and Action for the adopted subset; unsupported entries are not
implied editable. Trainer exposes Money and marks identity/story/Pokédex/RTC
read-only. Preview groups semantic changes under Party, Created Pokémon,
Items and Trainer. No copyrighted game assets were added.

## Changed files

Implementation commit `70c9894` changes:

- `pokemonstart_v022_product_web.py` — clearer everyday workflow and semantic
  grouping, preserving the existing writer/core boundary.
- `pokemonstart_v022_e5_acceptance.py` — dynamic all-family Cycle 1 recipe,
  output audit and normal-SAVE return checks, plus un-hash-gated Cycle 2
  preparation and checks using existing independent E1–E4 audit logic.
- `tests/test_v022_creation_web.py` — six-position and unsupported normal
  control assertions.
- `tests/test_v022_e5_acceptance.py` — composed recipe, independent output,
  simulated returns, Cycle 2 and GUI stale-state coverage.
- `tests/v022_e5_browser_smoke.py` — real Chrome loopback all-family GUI
  workflow, semantic preview, verified output equality, stale rejection and
  immutable input checks.
- `tests/v022_e5_full_party_browser_smoke.py` — real GUI full-Party refusal.

The two documents added in the reporting-only commit are not part of the
implementation candidate tree above.

## Automated and browser evidence

On the exact implementation candidate, full repository discovery completed:
**309 tests passed, 15 skipped** (`.venv/bin/python -m unittest discover -s
tests -v`, 179.636 seconds). The 15 skips are Windows-specific NTFS/server/
validation/host tests unavailable on this macOS host. Existing NiceGUI teardown
emits a `RuntimeWarning` that an upload coroutine was never awaited; it did not
fail the suite. Focused E5 tests and the adopted E1–E4 suites are included in
that run.

Real headless Chrome 154 on loopback exercised the actual GUI against a
retained naturally progressed exact-v0.22 owner save with Party count 4 and
eligible adopted capabilities. One transaction exercised Money, Inventory,
an existing Party member, and one Party creation. The actual GUI artifact
matched both the composed core output and independent complete E3/E4 audit.
The smoke also checked grouped semantic preview, control-after-preview export
rejection, source/ROM immutability, exclusive private output and loopback
binding. A second real-GUI run with a full Party showed the explicit
Box-not-supported refusal and no creation control. The private run receipt and
artifacts remain outside Git. These are Maker-recorded local private-input
machine checks, not fresh independent reproduction or Human gameplay
attestation.

Evidence classes remain distinct:

- Canonical repository evidence: adopted E1–E4 scope and semantics from the
  verified base and its records.
- Synthetic/publicly reproducible: committed unit and NiceGUI tests.
- Local private-input machine verification: actual Chrome Cycle 1 export,
  independent equality, full-Party refusal and immutable input checks; private
  receipt retained outside Git.
- Human gameplay attestation: **pending**.
- Cycle 1 normal-SAVE return verification: **pending**.
- Cycle 2 reopen/edit/export and later normal SAVE/return verification:
  **pending**.
- Hypothesis/unverified: no cross-version behavior or unsupported feature is
  claimed.

## Human acceptance and remaining terminal gate

A private Human workflow kit has been prepared with the exact Cycle 1 recipe,
ordinary in-game observations requested, return-save machine-check command,
and Cycle 2 reopen/edit/export sequence. It contains the exact GUI-produced
artifact and isolated exact-v0.22 ROM/save pair. The protected inputs and
outputs, private receipt, and absolute private paths are not committed or
published.

The Human should verify visible Money, Inventory, existing member and created
member state; normal summaries/menus; a representative ordinary battle/use;
absence of obvious display corruption/crash/freeze; and successful normal
SAVE, then close the emulator fully. Machine return verification must pass
before Cycle 2. Cycle 2 must reopen the progressed Cycle 1 return through the
GUI without a preregistered source hash, edit the created Pokémon using one
supported E3 field, Preview/Verify/Export, pass complete independent output
equality, then load that artifact and perform another ordinary normal SAVE.
The second returned save must also pass the machine return checks.

Therefore E5 terminal success has **not** been claimed. Do not merge. After
Human acceptance and both return checks, freeze the exact candidate, add only
reporting evidence if needed, rerun applicable tests and stop at
`READY_FOR_INDEPENDENT_REVIEW`.

## Fresh-context independent-review prompt

Use a genuinely fresh reviewer context. Fresh-fetch
`Ryo722/pokemonstart-save-editor-research` and independently record the remote
`main` and candidate identities. Review candidate
`70c9894c7b104e144f727b283bd7eda7fdabd487` (tree
`f3ec70adf8e4c99936d311708edca98b004b11b7`, base
`5864e7ada132408d39df8cc3dc2b56a75805b24a`) and any later reporting-only
evidence commit. Read the canonical E1–E4 contracts, qualifications, reviews,
acceptance records, current core/GUI and tests, this candidate record, and the
Human return evidence when supplied. Independently examine whether the actual
normal GUI coherently composes adopted capabilities without broadening writes;
verify sequential creation/full-Party refusal; inspect preview invalidation,
exact-ROM/source handling, exclusive verified export, complete independent
output equality and both return-check cycles. Reproduce tests and private
exact-ROM checks where available, clearly classifying unavailable checks and
Maker-recorded private runs. Check the diff for protected data and unsupported
write authority. Report blocking findings with file/line references and exact
reproduction, or provide a review disposition for a separate explicit Human
adoption decision. Do not merge, add save semantics, incorporate v0.23+,
expand scope, release, promote Stable, or publish protected data.

## Post-acceptance correction and PR #25 (2026-10-08)

- Focused review finding: return checkers did not assert persistence of every
  requested field. Corrected in `08d2151`; strengthened after the PR #25
  focused review so a requested decrease returning to its pre-edit value, or
  an ambiguous one-use held-item loss, fails. Retained Cycle 1/2 return saves
  pass the corrected rule.
- Receipt reproducibility: the retained E5 receipts regenerate byte-exactly on
  the E5 commits. On the merged PR #25 head, the receipt JSON carries new
  report keys (shiny, Give All status), so `audit-export` against the old
  receipts reports a schema difference; the E5 requests still derive outputs
  byte-identical to the Human-accepted artifacts.
- Disposition: candidate for Human adoption via PR #25; not merged.
