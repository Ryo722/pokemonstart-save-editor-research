# PokemonStart save editor research

Evidence-first research and tooling for a future, user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current position

M1 is the reproducible read-only save verifier. A bounded implementation candidate now exists in `pokemonstart_save_verifier.py` with synthetic unit tests. It validates the observed CFRU-JP-derived save layout without modifying the input file, separates a 128 KiB flash body from an optional 16-byte opaque emulator footer, validates both 14-section slots, selects a unique newest valid slot, decodes supported 100-byte party records, and reports sectors 30/31.

The M1 gate is **not complete yet**. The candidate passed synthetic tests and a private local check against the retained HP-IV-30 test save, but the canonical gate still requires reproduction on the private original and normal-resave files plus review of the exact candidate. Those protected files must not enter Git history.

The prior successful single-field HP IV write remains evidence for a narrow writer proof, not permission to broaden writer scope or begin GUI work.

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
