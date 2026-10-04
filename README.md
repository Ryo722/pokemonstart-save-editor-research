# PokemonStart save editor research

Evidence-first research and tooling for a future, user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

**M1 — reproducible read-only save verifier is complete.** `pokemonstart_save_verifier.py` is merged and validates the supported observed CFRU-JP-derived save layout without modifying the input file. It separates a 128 KiB flash body from an optional 16-byte opaque emulator footer, validates both 14-section slots, selects a unique newest valid slot, decodes supported 100-byte party records, and reports sectors 30/31.

The repository test suite passes 12/12 synthetic cases covering valid layouts and fail-closed malformed/ambiguous cases. Private original, HP-IV-30 test, and normal in-game resave inputs were also verified locally without entering Git history. The before-test/original state reproduces HP IV 31 with slot 1 counter 1; the normal resave reproduces HP IV 30 with slot 0 counter 2 selected as newest. Input hashes were unchanged by verification.

The project is now stopped before **M2 — bounded one-field writer proof**. M2 has not been authorized. The prior successful manual HP-IV write is evidence for that narrow proof only; it does not authorize broader writer scope, additional editable fields, save overwrites, or GUI work.

## Run the verifier

Python 3.10+ is sufficient; there are no third-party dependencies.

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000`-byte flash images or `0x20010`-byte files with a 16-byte opaque footer. It exits nonzero and prints `status: REJECTED` for malformed, ambiguous, internally inconsistent, or unsupported layouts.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

Tests build synthetic save bytes in memory. No `.sav` fixture is committed.

## Evidence and scope

See [evidence](docs/evidence.md) and [decision record](docs/decision-record.md). Evidence levels distinguish independently reproduced/source-backed facts, private local verification, prior observations, and hypotheses. Nickname and OT-name bytes are currently reported as hex rather than decoded text because a complete, pinned charmap is not required for the structural M1 gate.

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS/IPS patches, patcher executables, extracted distribution executables, or other proprietary package contents. Use legally obtained local inputs. See [contributing](CONTRIBUTING.md).
