# E4 Party creator: grouped Human acceptance and review handoff

This Maker report supplements the historical construction qualification. Human
gameplay and returned-save verification are now recorded for the exact candidate
below. Fresh independent review is the next gate; this report is neither that
review nor Human adoption authorization. Canonical `main` remains unchanged.

## Frozen implementation and evidence identities

- Human-played implementation commit: `3fd7c9ca43b1190feb47e89d2b1684a6344617bd`.
- Human-played tree: `74d0f559c8af542d8fc0d6d13a7cbc0ee95b37fe`.
- Canonical base / merge base: `381bc80080919952c9a32bb7982dfcf24bc92ea5`.
- Branch: `codex/e4-v022-party-creator`. The follow-up reporting commit adds this
  document only; it does not change the played implementation. Do not substitute
  a branch HEAD for the frozen Human-played SHA without inspecting its diff.
- Exact ROM SHA-256:
  `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
- Immutable grouped source SHA-256:
  `108d9e17e138375f7f0099af742eb22aaf783794abbaf66bbc50ea072b77f3bd`.
- Independently audited machine oracle and actual Human GUI output SHA-256:
  `1cac20037f8a2c276763a4ebdcdc6ec8439828bec1673929cf5270978d88ab49`.
- Human returned save SHA-256:
  `4f68eaa69b3894b73d7100bee8f7fcfd04df8a66b9d874fb4a6d2874b311e8aa`.

ROM/save bytes, private receipts, observation files, raw record/identity material
and local paths remain private and are not included in Git. Hashes and bounded
semantic summaries index retained evidence; they are not substitutes for it.

## One grouped GUI / gameplay transaction

The source is the retained eligible ordinary normal save, counter 12, Party 4,
map 5/3. Its historical source provenance and the complete construction model
remain described in [construction qualification](../e4-party-creator-construction-qualification.md)
and [construction evidence](../e4-party-creator-construction-evidence.json).
Those records describe the pre-Human checkpoint; this document records the
subsequent acceptance evidence without retroactively changing their claims.

The operator used the actual product GUI with the immutable source copy. The
GUI output passed structural verification, complete byte equality to the
machine oracle and independent E4 full-output reconstruction before gameplay.
The oracle was a comparison artifact, not the gameplay input. A separately
copied exact ROM and verified GUI save formed the isolated mGBA 0.10.5 pair.
The returned working save and frozen return copy are byte-identical, and mGBA
was closed when the agent checked them. Original ROM/source and immutable
copies remain unchanged.

| Created member | Semantic request |
| --- | --- |
| Party #5 | Bulbasaur Lv3, Hardy, Tackle / Growl / empty / empty, IV 0/0/0/0/0/0, EV all zero, friendship 50, ordinary ability 1 (Overgrow), no held item |
| Party #6 | Rattata Lv20, Adamant, Tackle / Tail Whip / Quick Attack / empty, IV 31/17/9/25/0/13 in HP/Attack/Defense/Speed/Sp.Atk/Sp.Def order, EV all zero, friendship 50, ordinary ability 2 (Guts), Leftovers |

**Human gameplay attestation:** the operator reported both summaries, moves,
abilities and battle/use normal; Rattata's Leftovers correct; existing Party
normal; no nickname/display anomalies or crash/freeze/visual anomalies; exactly
one normal SAVE; and mGBA fully closed before the return copy. The conversation
attestation matches the retained observations file. The agent did not perform
or directly observe this gameplay. No exact encounter/turn replay was supplied.

## Independently rerun local return verification

The exact frozen candidate's `pokemonstart_v022_creation_acceptance.py
check-return` was rerun against the actual private return, source, ROM and
prepared receipt. Its result equals the retained operator-generated report:

`MACHINE_RETURN_PASS_HUMAN_ATTESTATION_AND_DRIFT_REVIEW_REQUIRED`

It verifies counter **12 -> 13**, active-slot change, normal section rotation,
previous active-slot preservation, Party count 6, created semantic invariant
persistence, independent ordinary record reconstruction, Money/Inventory
equality and actual full-Party creation rejection with the Box-not-supported
reason. The editor's generated output preserved the source footer; the footer
changed after normal emulator SAVE, as the contract permits.

| Member | Reported gameplay drift | Maker assessment |
| --- | --- | --- |
| Existing Party #1 | EXP 151 -> 172; Speed EV 1 -> 2 | Consistent with ordinary battle participation |
| Created Party #5 | EXP 57 -> 78; Speed EV 0 -> 1; Tackle PP 35 -> 34 | Consistent with ordinary battle use |
| Created Party #6 | EXP 8000 -> 8026; Speed EV 0 -> 1; Tackle PP 35 -> 34; current HP 48 -> 46, max HP 48 | Consistent with ordinary battle use |

No additional Party drift was reported. Invariant species/identity/nature/
ability/move IDs/IV/origin bytes passed the verifier, and Leftovers persisted.
This bounded consistency assessment is not an exact encounter replay or a
proof that every unrelated world-state byte remains equal after gameplay.
Ordinary gameplay may change world state; the return checker has explicit
Party, SAVE structure and Money/Inventory boundaries.

## Verification provenance and limits

The full repository suite was rerun against the already-pushed implementation
`3fd7c9ca43b1190feb47e89d2b1684a6344617bd`, starting with a clean worktree and
without changing any implementation or tests:
**305 tests, 290 passed, 15 Windows-only skips**. The command is
`.venv/bin/python -m unittest discover -s tests -v`. The reporting commit changes
no implementation, GUI, verifier or tests. Its document diff receives separate
whitespace, protected-artifact/private-path and secret scans before push.

Prior exact-candidate isolated ROM/native and real Chromium qualification is
indexed in the construction evidence and retained local execution reports.
These are machine evidence, not Human gameplay. Synthetic cases, retained
private input checks, upstream navigation and Human attestation retain their
original evidence classes. No new native matrix or browser automation run is
claimed in this reporting action. Fresh review must reproduce the checks it
needs rather than treating Maker conclusions as independent approval.

## Fresh-context independent-review prompt

Use a genuinely fresh reviewer context; do not conduct the independent review
in this Maker conversation. Suggested task:

> Fresh-fetch `Ryo722/pokemonstart-save-editor-research` main and
> `codex/e4-v022-party-creator`. Record the current remote identities and inspect
> reporting-only changes after Human-played commit
> `3fd7c9ca43b1190feb47e89d2b1684a6344617bd` (tree
> `74d0f559c8af542d8fc0d6d13a7cbc0ee95b37fe`, base
> `381bc80080919952c9a32bb7982dfcf24bc92ea5`). Read the canonical contracts,
> E3 qualification/review, E4 construction matrix/evidence and this acceptance
> report. Do not use the prompt or Maker conclusions as correctness evidence.
> Review the expanded Party-only creator independently, including complete
> initialization, nickname-tail equivalence limits, saved creation-mode gates,
> owner-derived non-shiny personality/nature/ability/gender policy, bounded
> origin domain, explicit moves/PP defaults, independent full-record/full-save
> audit, insertion/checksum/footer preservation, composition and GUI stale-state
> and exclusive-export behavior. Examine return-checker coverage and the Human
> attestation/drift evidence separately. Reproduce appropriate machine tests
> and private exact-ROM checks where available; identify unavailable evidence
> explicitly without publishing protected data. Report blocking findings with
> file/line references and exact reproduction, or a disposition for a separate
> Human adoption decision. Do not merge, conduct new gameplay, expand E5/Box,
> edit Pokédex/story/event/RTC, release, promote Stable, add cross-version
> support, or publish protected data.

The next action is fresh independent review. No merge, adoption decision,
E5 expansion or additional Human gameplay request has been made here.
