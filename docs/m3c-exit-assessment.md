# M3C exit assessment — 2026-10-05

## Status

**ADOPTED: M3C COMPLETE after PR #11 merge. M4 remains NOT AUTHORIZED.**

Human authorization `AUTHORIZE PR #11 MERGE AND M3C CLOSURE` accepts this exit assessment, authorizes merging the derived-stat proof branch, and closes M3C. It does not authorize M4 implementation.

## Evidence boundary

Canonical `main` at the assessment start was `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3`; it contains the human-passed low-coupling batch. The derived-stat batch on PR #11 then passed its combined private return-save audit at SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`, with counter 6 selected, the prior slot and complete party record retained, and sectors 28–31 unchanged. See `docs/m3c-derived-stats-canary.md` for exact diffs and verification.

The returned save was independently rechecked before the closure decision: all 28 ordinary section checksums validate; active slot/counter is `0/6`; nature mint 4, HP EV 80, Attack IV 0, HP 22/22, Attack 9, and Sp. Attack 10 are retained; footer change is within the established normal-resave rule.

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
| Another exact field canary | Adds one bounded edit; Tera type is the easiest candidate | Diminishing value while support remains deliberately profile/capability gated |
| Widen positively supported save coverage | Makes existing proven edits useful beyond one retained snapshot | Requires a new provenance/profile eligibility argument and private-lineage regression set; no arbitrary-save claim is justified |
| Harden transaction/recovery | Improves safety across all supported edits | Shared envelope already protects input/output and byte preservation; user-facing recovery belongs in delivery design |
| Begin M4 entry/design | Converts the proven foundation into a selectable, inspectable player workflow | Requires an explicit M4 design/implementation authorization boundary |

## Exit decision

**M3C is complete.** More exact field canaries are not required to satisfy the milestone. The project now has:

- a reproducible read verifier;
- a proven reusable save-write envelope;
- repeated slot/counter game-round-trip evidence;
- low-coupling and derived-state capability proofs;
- a shared fail-closed transaction layer;
- exact diff/checksum accounting and input immutability;
- explicit blocked/unsupported field handling;
- private-output isolation outside the repository.

Additional Tera/item/move/species/form/identity work should be justified by a concrete M4 product need or new evidence, not by offset availability.

## Next boundary

The North Star is demonstrated as a bounded proof foundation on the retained lineage, but a general player workflow is not yet delivered. The next useful work is therefore an **M4 entry/design review** covering supported-save eligibility, capability registry exposure, recovery/output UX, architecture, platform/dependency choice, and minimal measurable success criteria.

M4 implementation, GUI work, arbitrary/non-lineage support, boxes/bags, overwrite behavior, and new unproven capability work remain unauthorized until a separate human decision.
