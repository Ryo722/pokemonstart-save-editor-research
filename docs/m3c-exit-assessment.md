# M3C exit assessment — 2026-10-05

## Evidence boundary

Canonical `main` at the assessment start was `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3`; it contains the human-passed low-coupling batch. The derived-stat batch is in an unmerged PR. Its combined private output passed the user-supplied return-save audit at SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`, with counter 6 selected, the prior slot and entire party record retained, and sectors 28–31 unchanged. See `docs/m3c-derived-stats-canary.md` for exact diffs and verification.

## Capability matrix for the retained v0.15 lineage

| Party capability | Proven transformation | Status |
| --- | --- | --- |
| HP IV | `31 -> 30` and `30 -> 31`, earlier bounded proofs | PROVEN |
| Friendship | `50 -> 51` and `51 -> 52` | PROVEN |
| Markings | `0 -> 1` | PROVEN |
| Ball | `3 -> 11` (Premier Ball) | PROVEN |
| Nature mint + cached stats | `0 -> 4` (effective Adamant) | PROVEN on exact post-batch hash |
| HP EV + max/current HP | `0 -> 80`, HP `21/21 -> 22/22` | PROVEN on exact post-batch hash |
| Attack IV + cached Attack | `29 -> 0`; tested individually and combined | PROVEN on exact post-batch hash |
| Tera type | storage/read path identified; no PokemonStart mutation canary | BLOCKED for writing |
| Held item, moves/PP/PP-Up | target-profile catalogs and coupling incomplete | BLOCKED for writing |
| Hyper-training; EXP/level/HP/stats | coupled transformation not yet established beyond selected derived-stat case | BLOCKED for writing |
| Ability; species/form/identity | broader identity/catalog coupling | BLOCKED for writing |

`PROVEN` means the named bounded transformation on the tested private lineage, not arbitrary values, party members, save hashes, builds, or versions. Structural verification alone is insufficient writer eligibility. No ROM, save, or proprietary payload is in Git.

## Compare the next investments

| Next work | Information and player value | Cost/risk |
| --- | --- | --- |
| Another exact field canary | Adds one edit; Tera type is the easiest candidate | Diminishing value while the writer still recognizes only specific hashes and targets |
| Widen positively supported save coverage | Makes existing proven edits useful beyond one retained snapshot | Requires a new provenance/profile eligibility argument and private-lineage regression set; no arbitrary-save claim is justified |
| Harden transaction/recovery | Improves safety across all supported edits | Shared envelope now rejects in-repo output, preserves input/slots/tails/footer, verifies output; a user-facing recovery flow still belongs to delivery work |
| Begin minimal editor delivery | Turns proven capabilities into a selectable, inspectable output workflow | M4 is not authorized and needs a separate scope decision |

## Recommendation and authorization boundary

The field evidence is sufficient to **stop M3C field expansion for a formal exit review**. The next useful decision is whether to merge the derived-stat PR and enter a minimal M4 delivery phase scoped to positively supported v0.15 lineage saves, or continue M3C with supported-save/profile coverage and recovery hardening first. Additional Tera/item/move canaries should follow a specific player need or new target-profile evidence, not offset availability.

The North Star is demonstrated as a bounded proof on the retained lineage, but a general player workflow is not yet delivered. The current exact-hash writers do not qualify arbitrary external saves, other builds, boxes, or bags. The PR must not be merged, and M4 work must not begin, without the corresponding human decisions.
