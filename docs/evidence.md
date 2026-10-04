# Evidence ledger

## Provenance and patch chain

The referenced work describes a PokemonStart v0.15 `.pks` distribution. It was extracted as data without executing Defender-blocked executables. A BPS stream was extracted from `パッチ当て.exe` as data and applied by an original Python script; the patcher EXE was not executed. The full `.pks` file, its download URL, its SHA-256, and the extraction script are unavailable here, so their exact provenance and extraction behavior remain **unverified in this repository**. Do not invent package hashes.

The user-pasted application log records:

| Artifact or parameter | Observed value | Evidence level |
| --- | --- | --- |
| Patcher EXE SHA-256 | `58a04c631228e8fa1c47ad312a6e18e5f84bb0937a7c15931d479d7df934b030` | prior command log |
| Embedded BPS offset / size | `3180` / `17,879,020` bytes | prior command log |
| Embedded BPS SHA-256 | `58f05fa30d6b7fc7abb615c02b44e7c514858be4e535e7856c35f4b4a1c8c2d2` | prior command log |
| BPS source size / CRC32 | `16,777,216` / `3B2056E9` | prior command log |
| BPS target size / CRC32 | `33,554,432` / `C8039921` | prior command log |
| BPS patch CRC32 | `B17329E1` | prior command log |
| BPS metadata | `PokemonStart v0.15 デモ版（カントー・ななしま・ホウエン）・2026-10-04 15:10 作成・git 1499a6dc` | prior command log |
| Source ROM SHA-256 | `1e4af44b0c75cc8649bfb8649dc4ae5850bf5358bd6b9cd0bf779c99f9db1486` | prior command log |
| Target ROM SHA-256 | `48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12` | prior command log |

The log reports a matching source CRC and output CRC, with the target ROM written successfully. The hashes identify private local inputs; they do not confer redistribution rights.

## Save and structure

| Observation | Value | Evidence level |
| --- | --- | --- |
| Original / before-test save | `131,088` bytes (`0x20010`), SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b` | local private-input verification |
| Original backup | Byte-identical to the before-test save; same size and SHA-256 | local private-input verification |
| Normal-resaved file | `131,088` bytes, SHA-256 `c8e086f925b1187639eda7df3bbdb99f4c4e1817f6198a81f44c77db3d5f3cdd` | local private-input verification |
| Supported mGBA-style layout | `0x20000` flash bytes plus 16-byte opaque emulator footer | verifier behavior + local private-input verification |
| Initial active slot | slot 0 erased; slot 1 valid, counter 1 | local private-input verification |
| Normal-resave slot state | slot 0 valid counter 2; slot 1 valid counter 1; slot 0 selected as newest | local private-input verification |
| Section format | 14 logical sections per slot, signature `0x08012025`; all checked sections pass section-specific checksums | upstream source evidence + local private-input verification |
| Extra sectors | sector 30 has 23 nonzero bytes; sector 31 has 0 nonzero bytes on the checked original and resave | local private-input verification |
| Party | count 1; 100-byte `Pokemon` record with species 1, level 5, EXP 134, friendship 50, ball 3, moves 33/45, PP 35/40, EVs all zero | local private-input verification |
| Original IVs | HP/Atk/Def/Spe/SpA/SpD = `31/29/26/23/27/29` | local private-input verification |
| Normal-resave IVs | HP/Atk/Def/Spe/SpA/SpD = `30/29/26/23/27/29` in the newest slot | local private-input verification |

The private inputs remained byte-for-byte unchanged across verification: SHA-256 before and after each read-only check matched. No private save bytes are stored in Git.

## M1 verifier source basis — upstream source evidence

The M1 implementation pins its structural constants to public `kapibarasan000/CFRU-JP` `main` commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`, observed as current on 2026-10-04.

- `include/save.h` defines a `0x1000`-byte `SaveSection` with `data[0xFF4]`, then `u16 id`, `u16 checksum`, `u32 signature`, and `u32 counter`. This fixes footer offsets `0xFF4`, `0xFF6`, `0xFF8`, and `0xFFC`.
- `src/save.c` defines 14 sectors per slot, signature `0x08012025`, and section checksum lengths: section 0 `0xF24`; sections 1–3 `0xFF0`; section 4 `0xD98`; sections 5–12 `0xFF0`; section 13 `0x450`. `GetSaveValidStatus` validates signatures/checksums and special-cases counter wrap `0xFFFFFFFF -> 0` before otherwise comparing counters as signed 32-bit values.
- `include/global.h` places `playerPartyCount` at SaveBlock1 offset `0x34` and `playerParty` at `0x38`.
- `include/pokemon.h` defines the extended in-save `Pokemon` field order used by the verifier. The listed fields total 100 bytes, including 7-byte nickname, nature mint, hyper-training flags, tera type, expanded growth/attack/EV/IV data, level, HP, and battle stats.

Evidence level: **upstream source evidence**. This establishes the parser constants; it does not by itself prove that every PokemonStart build uses the same layout.

## M1 verifier implementation evidence

`pokemonstart_save_verifier.py` is original repository code and exposes no write path. It accepts only `0x20000` or `0x20010` bytes, treats any trailing 16 bytes as an opaque emulator footer, validates both slots, requires each non-empty slot to contain section IDs 0–13 exactly once with one counter value, validates section-specific checksums/signatures, refuses equal-counter ambiguity, decodes party count and 100-byte party records, and reports sectors 30/31 deterministically.

Synthetic tests construct bytes in memory and cover: one-valid/one-erased slot, section permutation, newest-slot choice, `0xFFFFFFFF -> 0` counter wrap, equal-counter rejection, checksum corruption, duplicate/missing section rejection, inconsistent counters, partial erase, party count > 6, 16-byte footer separation, unsupported size, and deterministic report output.

Local test command: `python3 -m unittest discover -s tests -v` -> **12/12 PASS** on 2026-10-04. Evidence level: **independently reproduced / synthetic test evidence**.

### Private retained HP-IV-30 test save

A retained private Library file named `PokemonStart_v0.15_TEST_HPIV30.sav` was materialized only for local verification and was not added to Git history.

| Observation | Value | Evidence level |
| --- | --- | --- |
| File size / SHA-256 | `131,088` bytes / `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc` | local private-input verification |
| Flash-body SHA-256 | `05066a91355796e52e43616b3b4dd37998a5112dc33b6e3c1a7919417f1dd637` | local private-input verification |
| Emulator footer | 16 bytes present; kept opaque by verifier | local private-input verification |
| Slot state | slot 0 erased; slot 1 valid, counter 1 | local private-input verification |
| Physical/logical order | sectors 14–27 contain logical sections `13,0,1,...,12` | local private-input verification |
| Section validation | all 14 signatures/checksums pass using the pinned per-section lengths | local private-input verification |
| Party | count 1; species 1; level 5; EXP 134; friendship 50; ball 3; moves 33/45; PP 35/40; EVs zero; IVs `30/29/26/23/27/29`; HP 21/21; stats 9/11/10/13/12 | local private-input verification |
| Extra sectors | sector 30 has 23 nonzero bytes; sector 31 has 0 nonzero bytes | local private-input verification |

A separate throwaway parser, not importing the candidate module, independently recomputed the 14 checksums and the party IV word for this file and obtained the same results.

## M1 original / normal-resave closure — 2026-10-04

Three private files were supplied for the M1 closure check and were kept outside Git:

1. `PokemonStart_v0.15_BEFORE_HPIV_TEST.sav`
2. `PokemonStart_v0.15_ORIGINAL_BACKUP.sav`
3. `PokemonStart_v0.15.sav` (normal in-game resave after the HP-IV-30 test)

Fresh local verification reproduced the supported layout and checksum logic against all three files. The two original files are byte-identical. The normal-resave file has both save slots valid, selects counter 2 as newest, and retains HP IV 30. All files retain a 16-byte footer, sector 30 has 23 nonzero bytes, and sector 31 is zero. The files were re-hashed after inspection and were unchanged.

Footer SHA-256 values were also recorded without publishing footer bytes:

- original / backup footer: `9e5dd419cf323817943c6282d4f51936fb4913fe6f0c83458aa5b4f5742ae877`
- normal-resave footer: `4fbf291759da2fbdc6a80665938fc63375f4cbc7971b154d950ebafa8b5387f4`

Evidence level: **local private-input verification**, corroborated by the source-backed verifier rules and the repository's synthetic tests.

This closes the M1 reproduction gap: the original and normal-resave inputs now reproduce the expected slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without modifying the inputs.

## Minimal writer proof and round trip

The earlier writer proof changed HP IV from 31 to 30 while other IVs remained 29/26/23/27/29. The exact reported two-byte difference from the original test input was `0x10080: BF→BE` and section 1 checksum `0x10FF6: 62→61`; all other bytes, including the emulator footer, were reported unchanged. At level 5, HP remained 21/21.

The normal in-game resave is now independently parseable as described above: slot 0 counter 2 is newest, slot 1 counter 1 remains valid, the party retains HP IV 30, and the structural checks pass. This strengthens the evidence for that one field only. It does **not** establish general writer safety or authorize additional fields.

## Reproduction gaps

M1's read-only reproduction gap is closed for the supplied v0.15 original/test/resave set.

Remaining broader gaps are outside M1: exact distribution provenance, package hash/extraction transcript, exact PokemonStart/CFRU-JP integration revision, version/build generalization, emulator-footer semantics beyond opaque preservation/reporting, and field-specific writer coupling. Archive those only when independently available. No protected binary should enter this repository.
