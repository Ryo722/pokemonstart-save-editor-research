# PokemonStart save editor research

Evidence-first research and tooling for a future, user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

**M1 — reproducible read-only save verifier is complete.** `pokemonstart_save_verifier.py` validates the supported observed CFRU-JP-derived save layout without modifying the input file.

**M2 — exact one-field HP-IV writer proof is complete.**

**M3A — supported-save / reusable write-envelope characterization is complete.** The reusable contract is fail closed, preserve every non-target byte, preserve section order/counters/inactive slot/sectors 28–31/parasite tails/footer, write only to a new file, and re-verify the result.

**M3B — bounded same-field transaction proof is complete for the retained private v0.15 lineage.**

**M3C-F1 — friendship `50 -> 51` proof is complete and merged.** It survived a human game load + normal save and returned with friendship 51 and the checked party record preserved.

**M3C — goal-driven batch field expansion is AUTHORIZED and IN PROGRESS.** Further field work is grouped by coupling/risk class. Field-specific source evidence, validators, synthetic/property tests, private differential proofs, and capability records remain mandatory, but human game round trips are consolidated into representative batch canaries with bisection/fallback variants prepared in advance. Final batch merge remains a human gate.

**M3C low-coupling batch — COMPLETE on the retained v0.15 lineage.** Friendship 52, marking 1, and Premier Ball 11 survived a combined game round trip and were merged via #10. The derived-stat batch also survived its combined return-save check and remains in an unmerged PR; see `docs/m3c-derived-stats-canary.md`.

The proven field set is ready for a formal M3C exit review; see `docs/m3c-exit-assessment.md`. This does not authorize M4 work or merge the derived-stat PR.

New private `.sav` proof outputs must be written outside this repository. The shared M3C transaction writer rejects output paths within the repository. Historical preflight files under ignored `work/` are not committed.

**M4 — usable editor / GUI remains not authorized.**

The refined North Star is: enable a PokemonStart player to inspect a positively supported save, make a small evidence-proven party edit into a separate output file, independently verify that output, and retain a reliable recovery path. Malformed, ambiguous, or unsupported saves must fail closed.

## Run the verifier

Python 3.10+ is sufficient; there are no third-party dependencies.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero for malformed, ambiguous, internally inconsistent, or unsupported layouts.

## Proof writers and batch program

The repository's proof writers and M3C batch tooling are research tools, not a user-facing general editor. They must reject unsupported profiles/starting states, unexplained diffs, input/output path aliasing, and existing output paths; generated files are re-verified and inputs remain immutable.

M3C batch execution keeps **field-level evidence** while reducing **human-level repetition**: low/medium-risk fields may be researched and implemented together, individual variants and a combined canary are generated, and a representative game round trip is used for the group. If the combined canary fails, prepared variants are used to isolate the failing field/group rather than treating the batch as proven.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic save bytes. No `.sav` fixture is committed.

## Evidence and scope

See `docs/evidence.md`, `docs/decision-record.md`, `docs/m3a-support-envelope-findings.md`, `docs/m3b-proof-candidate.md`, `docs/m3c-f1-friendship-proof.md`, and `docs/m3c-goal-batch-program.md`.

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See `CONTRIBUTING.md`.
