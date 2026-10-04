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
| Original and backup save | Both `131,088` bytes (`0x20010`), SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b` | local recheck of attached files |
| Resaved file | `131,088` bytes, SHA-256 `c8e086f925b1187639eda7df3bbdb99f4c4e1817f6198a81f44c77db3d5f3cdd` | local recheck of attached file |
| mGBA layout | `0x20000` flash bytes plus 16-byte RTC footer, which must be preserved | prior analysis; upstream citation not recovered |
| Initial active slot | physical sectors 14–27, counter 1; sectors 0–13 erased | prior analysis |
| Section format | 14 logical sections per slot, signature `0x08012025`, all active checksums pass; reported section lengths include `0xF24`, `0xFF0`, `0xD98`, `0x450` | prior analysis of CFRU-JP and save |
| Extra sectors | sector 30 had 23 nonzero bytes, unchanged across test/resave; sector 31 zero. Earlier claim that both were zero was incorrect. | corrected prior analysis |
| Party | count 1; 100-byte `Pokemon` struct matched CFRU-JP fields including 7-byte nickname, natureMint, hyperTraining, teratype | prior analysis |

Parsed starter: フシギダネ, species 1, level 5, EXP 134, friendship 50, ball 3, moves 33/45, PP 35/40, EVs all zero, IVs HP/Atk/Def/Spe/SpA/SpD = 31/29/26/23/27/29. HP 21/21; Atk 9, Def 11, Spe 10, SpA 13, SpD 12. Nickname decoded using a CFRU-JP Japanese charmap. Money was reported as 3000. These are prior analysis, pending independent parser reproduction.

## Minimal writer proof and round trip

The prior analysis reports a test save with HP IV changed from 31 to 30 while other IVs remained 29/26/23/27/29. The exact two-byte difference from the original was `0x10080: BF→BE` and section 1 checksum `0x10FF6: 62→61`; all other bytes, including the RTC footer, were reported unchanged. At level 5, HP remained 21/21. The test save itself is unavailable here.

The user then loaded that output in the game and performed a normal resave. The attached resave's hash and size were locally rechecked. Prior analysis reports slot 0 counter 2, slot 1 counter 1, all 14 checksums passing in both, signature passing, IV word `3BBBEBBE`, HP IV 30 in both slots, and preserved other party values. This is strong observed evidence for that particular write, while wider editing claims remain untested.

## Reproduction gaps

Archive a source URL, release identity, package hash, extraction transcript, exact CFRU-JP revision/links, and original script provenance in a future evidence update when available. Recompute all parser claims from private inputs before using them as code assertions. No protected binary should enter this repository.
