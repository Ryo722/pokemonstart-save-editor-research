# PokemonStart save editor research

Evidence-first research and tooling for a future, user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

**M1 — reproducible read-only save verifier is complete.** `pokemonstart_save_verifier.py` validates the supported observed CFRU-JP-derived save layout without modifying the input file.

**M2 — exact one-field HP-IV writer proof is complete.**

**M3A — supported-save / reusable write-envelope characterization is complete.** The reusable contract is fail closed, preserve every non-target byte, preserve section order/counters/inactive slot/sectors 28–31/parasite tails/footer, write only to a new file, and re-verify the result.

**M3B — bounded same-field transaction proof is complete for the retained private v0.15 lineage.**

**M3C-F1 — friendship `50 -> 51` proof is complete and merged.** It survived a human game load + normal save and returned with friendship 51 and the checked party record preserved.

**M3C low-coupling batch — COMPLETE on the retained v0.15 lineage.** Friendship 52, marking 1, and Premier Ball 11 survived a combined game round trip and were merged via #10.

**M3C derived-state batch — COMPLETE for its exact retained-lineage transformations.** Nature mint `0 -> 4`, HP EV `0 -> 80` with HP `21/21 -> 22/22`, and Attack IV `29 -> 0` with cached stats updated together survived the combined game round trip. The returned private save re-verified at SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`.

**M3C — COMPLETE.** The field-expansion milestone is closed with a useful bounded party-edit capability set, a reusable fail-closed transaction envelope, explicit blocked/unsupported capabilities, and a formal exit assessment. Further field proofs require a new evidence-backed need rather than continuing M3C by default.

**M4 — bounded usable-editor implementation is AUTHORIZED / IN PROGRESS.** PR #12 adopted the evidence-gated M4 design. The authorized first slice is retained-lineage S0/P/C qualification, one bounded repeated-use `party[0]` markings family, hardened new-file transaction/publication, independent verification, CLI/audit delivery, and a **localhost-only NiceGUI browser UI** with required private canaries. The earlier Tkinter delivery choice has been superseded by `docs/m4-delivery-correction.md`. Arbitrary/non-lineage save support, boxes/bags, unrestricted values, remote/browser exposure, and final implementation-PR merge remain unauthorized.

See `docs/m4-entry-decision.md` for the adopted design, `docs/m4-bounded-implementation-authorization.md` for the bounded implementation authority, and `docs/m4-delivery-correction.md` for the controlling GUI-delivery correction.

New private `.sav` proof outputs must be written outside this repository. The shared M3C transaction writer rejects output paths within the repository. Historical preflight files under ignored `work/` are not committed.

The refined North Star is: enable a PokemonStart player to inspect a positively supported save, make a small evidence-proven party edit into a separate output file, independently verify that output, and retain a reliable recovery path. Malformed, ambiguous, or unsupported saves must fail closed.

## Run the verifier

Python 3.10+ is sufficient for the core verifier; the browser delivery layer adds NiceGUI as a separate UI dependency.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero for malformed, ambiguous, internally inconsistent, or unsupported layouts.

## Proof writers and transaction infrastructure

The repository's proof writers and transaction tooling are research infrastructure, not a user-facing general editor. They must reject unsupported profiles/starting states, unexplained diffs, input/output path aliasing, in-repository private-save outputs, and existing output paths; generated files are re-verified and inputs remain immutable.

M3C preserved **field-level evidence** while reducing **human-level repetition**: fields were grouped by coupling/risk class, individual variants and combined canaries were prepared, and representative game round trips were used for each defensible group. Success remains bounded to the named transformations and retained v0.15 lineage.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic save bytes. No `.sav` fixture is committed.

## Evidence and scope

See `docs/evidence.md`, `docs/decision-record.md`, `docs/m3a-support-envelope-findings.md`, `docs/m3b-proof-candidate.md`, `docs/m3c-f1-friendship-proof.md`, `docs/m3c-goal-batch-program.md`, `docs/m3c-batch-low-coupling.md`, `docs/m3c-derived-stats-canary.md`, `docs/m3c-exit-assessment.md`, `docs/m4-entry-decision.md`, `docs/m4-bounded-implementation-authorization.md`, and `docs/m4-delivery-correction.md`.

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See `CONTRIBUTING.md`.
