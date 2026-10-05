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

**M4 — bounded usable-editor implementation is ADOPTED / IN PROGRESS.** PR #13 merged the macOS-proven bounded S0/P/C implementation, retained-lineage `party[0]` markings `0 ↔ 1` FAMILY, CLI/audit path, hardened macOS publication path, and localhost-only NiceGUI browser delivery. Windows production write/download is still fail-closed on canonical `main`, but a **bounded Windows integration candidate is now authorized** under `docs/m4-windows-bounded-integration-authorization.md`. That candidate may integrate validated Windows browser/in-memory delivery and filesystem publication only to user-controlled local fixed NTFS with reparse parents rejected. Network/removable/non-NTFS paths remain unsupported; no hostile concurrent-junction or power-loss durability claim is authorized. PR #14 merge and M4 completion remain separate Human gates.

See `docs/m4-entry-decision.md` for the adopted design, `docs/m4-bounded-implementation-authorization.md` for the bounded implementation authority, `docs/m4-delivery-correction.md` for the controlling GUI-delivery correction, `docs/m4-pr13-adoption.md` for the exact PR #13 adoption/merge authority, and `docs/m4-windows-bounded-integration-authorization.md` for the current Windows integration-candidate authority.

The bounded M4 implementation is now on canonical `main`. See `docs/m4-implementation-progress.md` for current adopted evidence and `docs/m4-windows-validation.md` for the Windows proof plan. Draft PR #14 contains the Windows validation/integration work and remains unmerged. The M4 CLI and localhost-only NiceGUI browser adapter use the same S0/P/C core. The only edit family remains the evidence-qualified party[0] markings `0 ↔ 1` FAMILY on the retained PokemonStart v0.15 lineage/build/environment. Unsupported saves expose no edit action. NiceGUI binds to `127.0.0.1`; it never writes automatically to an emulator live-save location. Windows production write/download stays disabled on canonical `main` until a later exact-candidate review and explicit adoption.

Tkinter was the initial delivery experiment and is superseded by the canonical NiceGUI delivery correction. The old Tk adapter remains as historical reference and is not part of M4 acceptance.

New private `.sav` proof outputs must be written outside this repository. The shared transaction/publication paths reject unsupported output behavior, and private saves/ROMs remain outside Git.

The refined North Star is: enable a PokemonStart player to inspect a positively supported save, make a small evidence-proven party edit into a separate output file, independently verify that output, and retain a reliable recovery path. Malformed, ambiguous, or unsupported saves must fail closed.

## Run the verifier

Python 3.10+ is sufficient for the core verifier; the browser delivery layer adds NiceGUI as a separate UI dependency.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero for malformed, ambiguous, internally inconsistent, or unsupported layouts.

## Bounded M4 local browser adapter

The NiceGUI layer is optional and is kept separate from the standard-library save core and CLI. Install its pinned UI dependency from `requirements-m4-ui.txt`, then run `pokemonstart_m4_web.py` with the local private lineage journal, selected ROM/build, and matching environment ID. The server binds only to `127.0.0.1`. On the currently adopted macOS path, the browser returns a verified new `.sav` download; save it as a separate recovery copy and never choose an emulator live-save path. Windows browser/in-memory delivery has supporting validation evidence but remains disabled on canonical `main` pending the authorized integration candidate, exact review, and separate adoption.

This implementation is a bounded research slice for its retained lineage only. It does not provide a general save editor or general PokemonStart build support.

## Proof writers and transaction infrastructure

The repository's proof writers and transaction tooling are research infrastructure, not a user-facing general editor. They must reject unsupported profiles/starting states, unexplained diffs, input/output path aliasing, in-repository private-save outputs, and existing output paths where filesystem publication is used; generated files are re-verified and inputs remain immutable.

M3C preserved **field-level evidence** while reducing **human-level repetition**: fields were grouped by coupling/risk class, individual variants and combined canaries were prepared, and representative game round trips were used for each defensible group. Success remains bounded to the named transformations and retained v0.15 lineage.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic save bytes. No `.sav` fixture is committed.

## Evidence and scope

See `docs/evidence.md`, `docs/decision-record.md`, `docs/m3a-support-envelope-findings.md`, `docs/m3b-proof-candidate.md`, `docs/m3c-f1-friendship-proof.md`, `docs/m3c-goal-batch-program.md`, `docs/m3c-batch-low-coupling.md`, `docs/m3c-derived-stats-canary.md`, `docs/m3c-exit-assessment.md`, `docs/m4-entry-decision.md`, `docs/m4-bounded-implementation-authorization.md`, `docs/m4-delivery-correction.md`, `docs/m4-implementation-progress.md`, `docs/m4-p-transition-model.md`, `docs/m4-windows-validation.md`, `docs/m4-pr13-adoption.md`, and `docs/m4-windows-bounded-integration-authorization.md`.

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See `CONTRIBUTING.md`.
