# PokemonStart save editor research

Evidence-first research and tooling for a future, user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

**M1 — reproducible read-only save verifier is COMPLETE.** `pokemonstart_save_verifier.py` validates the supported observed CFRU-JP-derived save layout without modifying the input file.

**M2 — exact one-field HP-IV writer proof is COMPLETE.**

**M3A — supported-save / reusable write-envelope characterization is COMPLETE.** The reusable contract is fail closed, preserve every non-target byte, preserve section order/counters/inactive slot/sectors 28–31/parasite tails/footer, write only to a new file, and re-verify the result.

**M3B — bounded same-field transaction proof is COMPLETE for the retained private v0.15 lineage.**

**M3C — goal-driven bounded party-field expansion is COMPLETE.** Low-coupling friendship/markings/ball and the first nontrivial derived-state nature-mint/EV/IV/stat group survived representative game round trips. Remaining fields are explicitly BLOCKED/UNSUPPORTED rather than guessed.

**M4 — bounded usable-editor first slice is COMPLETE.** PR #13 adopted the retained-lineage S0/P/C core, repeated-use `party[0]` markings `0 ↔ 1` FAMILY, CLI/audit path, hardened macOS publication, and localhost-only NiceGUI delivery. PR #14 exact candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was explicitly adopted and merged as `2547650cf898c89450a1d95b5252cf9c52e0f634`, adding the bounded Windows path. See `docs/m4-completion.md`.

The M4 completion boundary is intentionally narrow:

- retained PokemonStart v0.15 lineage/build/environment only;
- only `party[0]` markings `0 ↔ 1` as the reusable FAMILY;
- malformed, ambiguous, unsupported, non-lineage, or capability-ineligible saves fail closed;
- macOS uses the adopted staged/no-clobber publication path;
- Windows semantic/browser delivery requires validated Windows build `26200.9457`;
- Windows filesystem publication additionally requires a user-controlled local fixed NTFS destination with no reparse component in its existing parent chain;
- network/removable/non-NTFS Windows publication is unsupported;
- no hostile concurrent-junction/final-name replacement or sudden-power-loss final-name durability claim is made;
- NiceGUI binds only to `127.0.0.1`, with no relay/LAN/public exposure;
- the tool never automatically writes an emulator live-save path and never overwrites the source.

This completion does **not** make the repository a general PokemonStart/PKHeX-style editor. Arbitrary saves, broader builds/versions, other party indices, unrestricted values, boxes/bags, and unproven fields remain outside scope.

See `docs/decision-record.md` for the canonical milestone/current-state definition; `docs/m4-completion.md` for the exact M4 completion authority and evidence; `docs/m4-windows-candidate-evidence.md` for the Windows evidence packet; and the earlier M4 design/adoption records for the authority chain.

The refined North Star is: enable a PokemonStart player to inspect a positively supported save, make a small evidence-proven party edit into a separate output file, independently verify that output, and retain a reliable recovery path. That North Star is now demonstrated for the bounded M4 first slice above.

## Run the verifier

Python 3.10+ is sufficient for the core verifier; the browser delivery layer adds NiceGUI as a separate UI dependency.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero for malformed, ambiguous, internally inconsistent, or unsupported layouts.

## Bounded M4 local browser adapter

The NiceGUI layer is optional and kept separate from the standard-library save core and CLI. Install the pinned dependency from `requirements-m4-ui.txt`, then run `pokemonstart_m4_web.py` with the local private lineage journal, selected ROM/build, and matching environment ID.

The server binds only to `127.0.0.1`. A positively qualified host/save exposes only the core-returned bounded markings action. Output bytes are independently verified before browser download. Keep the original save as the recovery copy and never replace a live emulator save automatically.

On Windows, an OS build outside the exact validated host gate remains fail closed for write delivery. Filesystem commit additionally rejects destinations outside the adopted local fixed NTFS boundary.

## Proof writers and transaction infrastructure

The repository's proof writers and transaction tooling are research infrastructure, not a general editor. They reject unsupported profiles/starting states, unexplained diffs, input/output aliasing, in-repository private-save outputs, existing output paths where filesystem publication is used, and unsupported platform/filesystem boundaries. Generated files are re-verified and inputs remain immutable.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic save bytes. No `.sav` fixture is committed. The documented macOS and Windows test counts are local execution evidence, not GitHub Actions reproduction.

## Evidence and scope

Key records include:

- `docs/evidence.md`
- `docs/decision-record.md`
- `docs/m3a-support-envelope-findings.md`
- `docs/m3c-exit-assessment.md`
- `docs/m4-entry-decision.md`
- `docs/m4-bounded-implementation-authorization.md`
- `docs/m4-delivery-correction.md`
- `docs/m4-pr13-adoption.md`
- `docs/m4-windows-validation.md`
- `docs/m4-windows-candidate-evidence.md`
- `docs/m4-windows-bounded-integration-authorization.md`
- `docs/m4-completion.md`

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See `CONTRIBUTING.md`.
