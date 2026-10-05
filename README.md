# PokemonStart save editor research

Evidence-first research and tooling for a user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

**M1 — reproducible read-only save verifier is COMPLETE.** `pokemonstart_save_verifier.py` validates the supported observed CFRU-JP-derived save layout without modifying the input file.

**M2 — exact one-field HP-IV writer proof is COMPLETE.**

**M3A — supported-save / reusable write-envelope characterization is COMPLETE.** The reusable contract is fail closed, preserve every non-target byte, preserve section order/counters/inactive slot/sectors 28–31/parasite tails/footer, write only to a new file, and re-verify the result.

**M3B — bounded same-field transaction proof is COMPLETE for the retained private v0.15 lineage.**

**M3C — goal-driven bounded party-field expansion is COMPLETE.** Low-coupling friendship/markings/ball and the first nontrivial derived-state nature-mint/EV/IV/stat group survived representative game round trips. Remaining fields are explicitly BLOCKED/UNSUPPORTED rather than guessed.

**M4 — bounded usable-editor first slice is COMPLETE.** PR #13 adopted the retained-lineage S0/P/C core, repeated-use `party[0]` markings `0 ↔ 1` FAMILY, CLI/audit path, hardened macOS publication, and localhost-only NiceGUI delivery. PR #14 exact candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was explicitly adopted and merged as `2547650cf898c89450a1d95b5252cf9c52e0f634`, adding the bounded Windows path. See `docs/m4-completion.md`.

**M5A — Money capability is IN PROGRESS.** The exact `3000 -> 9,999,999` transformation has a successful game round trip, freshly read-audited from return SHA-256 `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`. One sealed repeated-use proof writer has generated and independently audited a second exact candidate, `9,999,999 -> 1,234,567`, output SHA-256 `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7`. **The second candidate awaits a human game round trip. No reusable arbitrary-money FAMILY is adopted.** The early-game EventObjectTemplate/parasite differences are bounded observations and do not expand M4 provenance. See `docs/m5a-exact-max-money-canary.md`.

The adopted M4 reusable write boundary remains intentionally narrow while M5 research proceeds:

- retained PokemonStart v0.15 lineage/build/environment only;
- only `party[0]` markings `0 ↔ 1` is currently an adopted reusable write FAMILY;
- malformed, ambiguous, unsupported, non-lineage, or capability-ineligible saves fail closed;
- macOS uses the adopted staged/no-clobber publication path;
- Windows semantic/browser delivery requires validated Windows build `26200.9457`;
- Windows filesystem publication additionally requires a user-controlled local fixed NTFS destination with no reparse component in its existing parent chain;
- network/removable/non-NTFS Windows publication is unsupported;
- no hostile concurrent-junction/final-name replacement or sudden-power-loss final-name durability claim is made;
- NiceGUI binds only to `127.0.0.1`, with no relay/LAN/public exposure;
- the tool never automatically writes an emulator live-save path and never overwrites the source.

The expanded North Star is: build an evidence-first local editor for the owner's positively supported PokemonStart save lineage that can perform the common practical edits the owner actually wants while retaining fail-closed provenance/capability gates, separate outputs, independent verification, and recovery. The target sequence is money → inventory/items → practical party-Pokemon editing; Pokédex is future work and general progression/event flag editing is excluded.

This roadmap is not a blanket support claim. Arbitrary saves, broader builds/versions, unrestricted values, boxes/bags, reusable money writing, inventory writing, species changes, and every other unadopted capability remain unsupported until independently proven and explicitly adopted.

## M5A Money

Pinned CFRU-JP source evidence places the stored money word at SaveBlock1 offset `0x0290` and the SaveBlock2 encryption key at offset `0xF20`. CFRU-JP save mapping puts these in active logical sections 1 and 0 respectively, and CFRU-JP records a patch increasing maximum money to `9,999,999`.

The read/write representation under investigation is:

```text
money = LE32(active logical section 1 @ 0x0290)
        XOR LE32(active logical section 0 @ 0x0F20)
```

For exact retained input SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`, independent read-only analysis decoded `3000`, and the user confirmed the game display is `3000`.

The authorized exact canary writer then generated only one target: `9,999,999`. Its output SHA-256 is `e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69`. Only three money bytes and two section-checksum bytes differ; an independent complete-byte audit passed and the source remained immutable.

The initial record below describes the evidence level before the return save was supplied; the current audit supersedes that status.

Fresh read-only audit of the returned save confirms the exact `3000 -> 9,999,999` round trip: slot 1/counter 1 retains decoded `9,999,999`; slot 0/counter 2 is active after the normal save; and the early-game transition includes EventObjectTemplate-region initialization and a section 4 checksum-excluded parasite-tail change. These are observed bounded transition facts. M4 provenance masks and predicates remain unchanged. A second sealed writer accepts only that return SHA and changes `9,999,999 -> 1,234,567`; its output is generated and independently audited but has not been loaded in game. Details and limits are in the M5A canary record.

## Run the verifier

Python 3.10+ is sufficient for the core verifier; the browser delivery layer adds NiceGUI as a separate UI dependency.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero for malformed, ambiguous, internally inconsistent, or unsupported layouts.

## Bounded M4 local browser adapter

The NiceGUI layer is optional and kept separate from the standard-library save core and CLI. Install the pinned dependency from `requirements-m4-ui.txt`, then run `pokemonstart_m4_web.py` with the local private lineage journal, selected ROM/build, and matching environment ID.

The server binds only to `127.0.0.1`. A positively qualified host/save currently exposes only the adopted bounded markings action. Output bytes are independently verified before browser download. Keep the original save as the recovery copy and never replace a live emulator save automatically.

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
- `docs/post-m4-strategy-and-m5a-money.md`
- `docs/m5a-money-private-read-audit.md`
- `docs/m5a-exact-max-money-canary.md`

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See `CONTRIBUTING.md`.
