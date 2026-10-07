# Exact-v0.22 practical product candidate

Canonical base: `7e7435c5507abfec183c3b370dcb1fa381b22186`.
Candidate branch: `codex/v022-practical-product-sprint`.
Candidate implementation at the start of this evidence refresh: `e9883529e82571db9b34a006930db6c774e860a4`.

This is an experimental candidate, not canonical adoption or Stable support.
The exact v0.22 profile gate is mandatory. Normal use is a localhost GUI at
`127.0.0.1`, with immutable uploaded input, in-memory edits, semantic preview,
repository verification, and a separate download. No save path writer or live
emulator replacement is exposed.

## Candidate disposition

**TERMINAL_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW**, subject to the matrix and
review questions in `docs/v022-product-sprint-completion-evidence.json` and the
fresh-context packet under `docs/reviews/`.

This disposition combines four distinct evidence classes: canonical evidence
already adopted on `main`; candidate code and synthetic tests; reproduced local
private-input verification; and Human-attested game interaction. Pinned CFRU-JP
source is separately identified as upstream evidence. None of those classes is
promoted into another by the acceptance harness. The harness intentionally
continues to say `r4_complete: false` because software cannot self-attest Human
gameplay.

## Supported exact-v0.22 candidate surface

- **Eligibility / R1:** strict verifier plus exact ROM profile; Money's
  capability-specific predicate requires two valid consecutive slots,
  supported counter range/parity, key0 and decoded values in `0..9,999,999`.
  It does not allowlist input save hashes. Party and Items have separate
  structural predicates and do not inherit Money eligibility.
- **Money / R2:** GUI editing throughout `0..9,999,999`, with only the active
  Money representation and its required section checksum changed.
- **Party / R2:** existing ordinary occupied members only. Friendship
  `0..255` is editable when the record passes structural checks. Move 1 can
  switch Pound/Tackle for records already using one of those moves, with zero
  PP-Up bonuses and bounded PP; replacement sets PP to the evidenced base 35.
  Source-backed stat edits are limited to Bulbasaur/Ivysaur at levels 5/6,
  Serious/Modest nature, no mint or hyper-training, coherent EXP and cached
  stats, with bounded species/level/EXP/IV/EV requests and recomputed stats.
  Other fields remain read-only. Friendship is Human-tested in both R4 game
  cycles. The source-backed target-stat writer has not had a new normal-save
  round trip and remains a bounded qualification caveat for independent review.
- **Items / R2:** Potion quantity `1..3`, plus Antidote x1 insertion/removal
  at observed slot 2 when the leading records are Potion x3, item #533 x1,
  and the rest of the observed section13 tail is zero. Removal zeroes the slot
  in place. These operations work on previously unseen save hashes when their
  own predicate passes. The UI surfaces only the currently valid add/remove
  action. No later occupied slots, general compaction, pocket capacity, other
  item IDs/quantities, other pockets, key/event items or Give All behavior is
  claimed.
- **Exact-record template import:** a separate experimental API copies one
  unchanged game-generated Rattata record into the first empty Party slot and
  updates Party count and checksum. The exact candidate loaded, displayed,
  healed, entered battle, acted and completed a normal game save. This is
  evidence only; it is not exposed as a general Party constructor or GUI
  operation.

## R4 evidence

Cycle 1 began from an unseen save SHA and ran through the actual GUI. The Human
loaded the separate verified output in exact v0.22, observed the requested
Money/Friendship/Potion edits, and completed a normal SAVE. The returned save
advanced counter `6 -> 7`, retained requested semantics and remained eligible.

Ordinary gameplay then included normal inventory deletion and repurchase,
separate normal saves, and a game-native Rattata capture/save. The post-purchase
save SHA was new, advanced counter `7 -> 9`, passed reusable Money/Party/Items
predicates and generated the second GUI transaction. (The Rattata capture was a
separate evidence branch from the exact Cycle 2 source.)

Cycle 2 used the actual GUI on that naturally progressed save. The Human loaded
the separate output in exact v0.22, observed Money `7,654,321` and Potion x2,
observed a normal Party, and completed a normal SAVE. Structural verification
confirmed counter `9 -> 10`, retained Money/Friendship/Potion semantics, and
reusable eligibility. After mGBA fully exited, the live disposable save and
frozen returned snapshot had identical SHA-256 values. The harness still
reports a structural pass requiring Human attestation; Human observation is
recorded separately here.

See the sanitized [completion evidence](v022-product-sprint-completion-evidence.json)
and [native Inventory/template evidence](v022-native-inventory-and-template-import-evidence-20261007.md).

## Evidence limitations and non-claims

- Exact-v0.22 only; no support inference to another build/version.
- Key0 only; nonzero keys, counter wrap/sign boundary, ambiguous saves and
  malformed structures reject.
- No arbitrary item, pocket, capacity, later-slot ordering or compaction
  support; no Give All Items.
- No arbitrary Pokémon synthesis, generic template catalog, legality
  generation, Box, Pokédex/story/event/RTC editing, or ability writing.
- The imported Rattata proof demonstrates only one exact complete record and
  its Party-count/checksum envelope. It does not prove arbitrary template
  imports are safe.
- The candidate calculator follows pinned CFRU-JP `e24a16fe39e27ae162faf5b78596d1f3df18489d`
  (`+5` non-HP stat formula). The pinned source is not established as the exact
  integration revision of the patched game. A fresh stat-changing game
  round-trip remains useful qualification work, but the R4 acceptance used
  friendship and did not depend on target-stat recalculation.
- Fast Lab experimental candidate status does not imply Stable support,
  canonical adoption, a public release or a merge authorization.

## Publication and authority boundary

No ROM, save, patch, executable, private save bytes, hexdump or copyrighted
asset is stored in Git. Private paths are not part of the public evidence.
This candidate has not been merged to `main` or publicly released. A separate
fresh-context review and explicit Human adoption decision remain required.
