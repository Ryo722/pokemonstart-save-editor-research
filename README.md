# PokemonStart save editor research

Research notes for a future, user controlled PokemonStart v0.15 save editor. This repository contains documentation only. It contains no ROM, save, game asset, package payload, or executable extracted from the distribution.

## Current conclusion

A single party HP IV edit survived a game load and normal resave. That supports a narrow save writer proof, not a general editor. The next step is an independent, read only verifier for slot selection, section checksums, party decoding, and byte preservation on locally supplied saves. Broader fields and a Windows GUI follow only after reversible field specific write tests.

See [evidence](docs/evidence.md) and [decision record](docs/decision-record.md). Values labeled **local recheck** were checked against the three attached save files available in this session. Values labeled **prior observation** come from the referenced conversation or its pasted command output and need source artifacts to reproduce independently.

## Data boundary

Never commit or upload ROMs, `.sav` files, copyrighted game assets, `.pks` payloads, BPS patches, patcher executables, or other proprietary package contents. Use legally obtained local inputs. See [contributing](CONTRIBUTING.md).
