# Evidence ledger

## v0.22 practical product adoption — 2026-10-07

Human adoption decision followed independent correction re-review disposition `APPROVED_FOR_HUMAN_ADOPTION_DECISION`. PR #16 merged the exact reviewed packet-bearing candidate `cb4ef2fac0d3c9877ebcd984d4fde7fb501a647a` into canonical `main` as merge commit `ab18419108eeed91288d440a6f154cac33a1cf2e`. R1–R4 and the exact-v0.22 current-build terminal goal are therefore canonical COMPLETE / ADOPTED. This adoption does not claim Stable promotion, public release, cross-version support, broader item semantics, Box/Pokédex/story/event/RTC editing, or arbitrary Pokémon synthesis.

## v0.22 practical product sprint candidate — 2026-10-07

**Interim snapshot, superseded by the completion evidence below.** This entry
was written before the R4 Human game cycles and Inventory evidence harvest.
Its statements that R4 gameplay had not occurred and Antidote insertion/removal
were blocked describe that earlier state only. See the later R4 and native
Inventory/template-import evidence for the final candidate evidence classes.

Candidate from fresh canonical `7e7435c5507abfec183c3b370dcb1fa381b22186`:
[implementation record](v022-product-candidate.md) and
[sanitized validation](v022-product-candidate-evidence.json). Exact-build Money,
bounded Party/Potion reusable predicates, ordinary-controls NiceGUI, composed
in-memory outputs and read-only R4 tooling are implemented candidate-only.
Private non-canary input, actual NiceGUI/Chromium, core equality, independent
basic transaction audit and source immutability were reproduced. R4 Human game
cycles were not performed. Inventory insertion/removal/capacity remain blocked;
canonical exact-root insertion is preserved. A newly reproduced pinned-source
`+5` vs legacy `+level` stat formula discrepancy is documented, with corrected
candidate arithmetic and explicit lack of new stat normal-SAVE evidence.
No canonical adoption, Stable promotion or release is claimed.

### Independent review corrections — candidate follow-up

The source `+5` vs legacy `+level` discrepancy is unresolved for the exact
integrated game revision. Candidate stat-changing writes now fail closed at
level 6, including Level/EXP requests that would produce level 6. Level-5
stat calculations remain enabled where their independent predicates pass;
Friendship and Move 1 retain their separate predicates, including for level-6
records. No new Human game cycle was needed for these code guards. The
Antidote insert/remove helpers now enforce key0 in their shared qualification
path. The template-import product writer has no generic record builder and
remains gated by the exact source and complete record hashes. R4 evidence is
retained without modification. These are candidate implementation/test
claims, not canonical adoption or new game evidence.

## FL2-G0 durable Fast Lab baseline candidate — 2026-10-06

Fresh canonical base: `13ecd37cc8817d5a5a3d4f9e38c8ba5f51f8b022`. The FL1 implementation/profile/test chain was reconciled onto a candidate based on this exact `main` HEAD. Candidate scope and exclusions are recorded in `docs/fl2-g0-reconciliation.md`; exact v0.22 capability bounds remain in `docs/fast-lab-v022-capability.json`.

The local source branch contained write support for inherited Party fields that the canonical FL1 record classifies as candidate-only (ball, markings, nature mint, remaining IV/EV values). Reconciliation closes those paths, restricts reusable Party writes to the exact retained canary input and live-confirmed transitions/composition, and moves the needed stat calculation into a Fast Lab-only module. The Stable M3C derived-stat writer matches canonical `main` unchanged. No capability was promoted to Stable and no additional field was researched.

Verification on the candidate: focused FL0/FL1 tests **65 passed**; full repository suite **166 tests, 150 passed, 16 skipped**; `py_compile` **66 repository Python files passed**; capability-profile JSON validation passed; `git diff --check` passed; changed-path protected/executable suffix scan found no matches; Gitleaks scanned the candidate source/docs and found no leaks. No protected binary inputs were used or copied into the candidate.

This is a reconciliation candidate only. Candidate preparation did not modify canonical `main`; the review branch `codex/fl2-g0-durable-baseline` has since been pushed. Human merge authorization remains required.

## M5A exact money round trip and repeated-use canary — 2026-10-06

Fresh `main` before this bounded work was `f76ae2dd512f6db6f22d6b0d893b851130c6a6ef`. The supplied private return save SHA-256 independently reproduced as `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4` (131,088 bytes). The repository verifier accepted the supported `0x20000` flash + 16-byte opaque footer layout; all 28 saved sections have signature `0x08012025` and valid section-specific checksums. Slot 0/counter 2 is active; slot 1/counter 1 remains valid. The read-only money probe selected logical sections by ID, read key `0`, and decoded active money as `9,999,999`. The previous slot's logical section 1 party[0] record is byte-identical to active party[0]. Slot 1 retains `9,999,999` and the first candidate's counter-1 state; this is consistent with the exact `3000 -> 9,999,999` candidate being loaded and normally resaved. Evidence label: **game-proven exact transformation**, based on the returned normal-save state plus the human-reported game round trip; the return file alone does not reveal the displayed UI value.

The transition independently reproduces slot/counter `1/1 -> 0/2`, section positions `[1,2,...,13,0] -> [2,3,...,0,1]`, saved-game statistic `1 -> 2`, play time `00:02:15 -> 00:02:31` (monotonic), unchanged sectors 28–31, unchanged party[0], and unchanged opaque footer. The early-game SaveBlock1 difference includes `EventObjectTemplate` array region offsets `0x09E0..0x0ED9` (89 changed bytes, initialized from zero in these bytes); the pinned CFRU-JP `include/global.h` layout places `eventObjectTemplates[64]` at SaveBlock1 offset `0x9E0`. The checksum-excluded parasite tail changed at four bytes in logical section 4, offsets `0xEDE`, `0xEDF`, `0xEE8`, `0xEE9` within the unchecked `0xD98..0xFF0` tail. Pinned CFRU-JP `src/save.c` stores/loads parasite data in the section 0/4/13 unchecked tails. This is **observed bounded early-game transition evidence**, not a new volatility mask or a general provenance rule. The unchanged M4 predicate rejects it at `game-save payload changed outside qualified envelope`; both stable payload and tail fingerprints differ. No M4 code was changed.

The exact repeated-use canary accepts only input SHA-256 `1db3ec065a32b36c1d8aad5f24b7ffd1a86cef936a0a0df41f40b5cdb7363cb4`, checks decoded start `9,999,999`, and targets `1,234,567`. Independent derivation sealed output SHA-256 `b232f80f82a0908e015d3bd948ec3e32c90dc44890865a5a1f920ee2e61677c7` and the complete five-byte diff at absolute offsets `0x03290..0x03292` and `0x03FF6..0x03FF7`. The separate auditor imports neither writer nor repository verifier and checks exact hashes/diff, all signatures/checksums, slot/counter, permutation/metadata, key/decoded money, inactive slot, tails, party bytes, sectors 28–31, and footer. Private execution generated the exact new repo-external file; writer and post-run SHA checks confirmed source immutability. The independent audit returned PASS and the repository verifier accepted the output. Synthetic M5A tests and the full suite were run: `python3 -m unittest discover -s tests -v` -> **107 tests OK, 16 skipped**. Status: **GENERATED / INDEPENDENTLY AUDITED; awaiting Human game round trip**. No reusable arbitrary-money FAMILY is adopted.

## M3C derived-stat canary preflight — 2026-10-05

Fresh `main` is `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3`, which merged the human-passed low-coupling canary. Its private returned save re-verified read-only at SHA-256 `baf0b88fd357c54e17743601bbfa26b436db467a2fd78cd1d2c598fb714c50fa`, active slot 1/counter 5, retaining friendship 52, marking 1, and ball 11. The next class-C nature-mint/HP-EV/Attack-IV batch has source-backed layout and stat formulas, 43/43 local synthetic tests, four exact private-copy outputs, and a separate checksum/byte-diff audit PASS. It is **CANARY_READY**, not game-proven. Full source links, capability boundaries, output hashes, exact diffs, and the human gate are in `docs/m3c-derived-stats-canary.md`. No save bytes are committed.

## M3C derived-stat round trip — 2026-10-05

The user-supplied return save SHA-256 `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86` passed a separate read-only audit: all 28 section checksums valid; new active slot 0/counter 6; old slot 1/counter 5 retained byte-for-byte; active 100-byte party record byte-identical to the combined candidate; sectors 28–31 unchanged; external footer changed as allowed. This proves the exact nature-mint/HP-EV/Attack-IV combined transformation for the retained v0.15 lineage. The returned file was copied with exclusive creation to the repo-external private lineage directory and verified at the same SHA-256. The source and candidate files remained unchanged. Details are in `docs/m3c-derived-stats-canary.md`.

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

## M2 bounded repository writer proof — COMPLETE — 2026-10-04

M2 is deliberately constrained to a single proof transformation. `pokemonstart_hpiv_proof_writer.py` accepts only the known before-test input hash and refuses every other save. It writes only to a new path using exclusive creation and refuses both input overwrite and pre-existing output paths.

The proven proof contract is:

| Item | Required value | Evidence level |
| --- | --- | --- |
| Input SHA-256 | `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b` | local private-input verification + allowlist |
| Starting field | `party[0] HP IV = 31` | local private-input verification |
| Target field | `party[0] HP IV = 30` | bounded M2 design |
| Allowed data diff | `0x10080: BF -> BE` | local repository-writer preflight |
| Allowed checksum diff | `0x10FF6: 62 -> 61` | local repository-writer preflight |
| Output SHA-256 | `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc` | local repository-writer preflight |
| Retained proof comparison | byte-identical to retained `PokemonStart_v0.15_TEST_HPIV30.sav` | local private-input verification |
| Input immutability | before/after SHA-256 unchanged | local repository-writer preflight |

The writer first invokes the M1 verifier on the input. It locates logical section 1 from the verified active slot instead of assuming a physical section order, changes only the low five HP-IV bits in party record 0, recalculates section 1's checksum, and then requires the complete output diff and output SHA-256 to match the fixed proof contract. It re-runs the M1 verifier on the generated bytes and requires active-slot, party-count, non-HP IVs, opaque footer, sector 30, and sector 31 invariants to hold.

Six new synthetic writer tests cover the bounded constants, HP-IV/checksum-only transformation, rejection of unrecognized input hashes, rejection of the wrong starting HP IV, refusal to overwrite the input or an existing output path, and successful new-file creation while preserving the input. A local implementation preflight passed all six tests. No `.sav` fixture is committed.

A private local execution against `PokemonStart_v0.15_BEFORE_HPIV_TEST.sav` produced:

- input SHA-256 unchanged at `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`;
- output SHA-256 `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`;
- active slot 1, logical section 1 in physical sector 16;
- exactly two changed bytes: `0x10080 BF->BE` and `0x10FF6 62->61`;
- generated output byte-for-byte identical to the retained earlier HP-IV-30 proof save.

Evidence level: **local private-input verification / repository-writer preflight**. The private input and generated save remain outside Git.

### Fresh M2 human game round trip — PASS

The user reported loading the repository-generated private output in PokemonStart v0.15 and completing one normal in-game save. The resulting private resave was then inspected read-only and kept outside Git.

| Observation | Value | Evidence level |
| --- | --- | --- |
| Resave size / SHA-256 | `131,088` bytes / `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac` | local private-input verification |
| Flash-body SHA-256 | `8318c04bd726b11de4ce3c46da0d567090d557dfdf11048308c6e994a278f723` | local private-input verification |
| Game accepted proof output and normal save completed | yes | human observation |
| Slot 0 | valid; counter 2; all 14 section IDs present once; all signatures/checksums pass | local private-input verification |
| Slot 1 | valid; counter 1; all 14 section IDs present once; all signatures/checksums pass | local private-input verification |
| Active slot | slot 0, uniquely newer | local private-input verification |
| Party in both slots | count 1; species 1; level 5; EXP 134; friendship 50; ball 3; moves 33/45; PP 35/40; EVs zero | local private-input verification |
| IVs in both slots | `30/29/26/23/27/29`; IV word `0x3BBBEBBE` | local private-input verification |
| HP / stats in both slots | HP `21/21`; Atk 9, Def 11, Spe 10, SpA 13, SpD 12 | local private-input verification |
| Sector 30 | SHA-256 `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525`; 23 nonzero bytes | local private-input verification |
| Sector 31 | SHA-256 `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7`; 0 nonzero bytes | local private-input verification |
| Opaque footer | 16 bytes present; SHA-256 `0f5e9be128e35fb5926268e15f441e442ff54ab712ba7fa50418761a4170ed0f` | local private-input verification |

The fresh resave preserves the repository-generated proof output's entire old slot 1 byte-for-byte. Flash sectors 28–31 are also byte-identical to the proof output. The game wrote a new valid slot 0 at counter 2 and updated the opaque 16-byte footer. No semantics are assigned to the footer bytes.

The fresh resave also reproduces the same structural outcome as the earlier historical normal resave: two valid slots, counter 2 newest, and HP IV 30 retained. The two resaves are not byte-identical; that exact identity is not an M2 requirement.

This satisfies the bounded M2 round-trip evidence gate for the exact v0.15 proof transformation. PR #4 merged the exact reviewed candidate into canonical `main`; M2 is therefore complete for this proof contract. It does **not** establish a general writer, support other save hashes/builds, or prove any other field safe.

## Earlier manual writer proof and round trip

The earlier manual writer proof changed HP IV from 31 to 30 while other IVs remained 29/26/23/27/29. The exact reported two-byte difference from the original test input was `0x10080: BF→BE` and section 1 checksum `0x10FF6: 62→61`; all other bytes, including the emulator footer, were reported unchanged. At level 5, HP remained 21/21.

The earlier normal in-game resave is independently parseable as described above: slot 0 counter 2 is newest, slot 1 counter 1 remains valid, the party retains HP IV 30, and the structural checks pass. The fresh repository-generated round trip now independently closes the integration uncertainty that this historical observation alone could not close.

## Reproduction gaps

M1's read-only reproduction gap is closed for the supplied v0.15 original/test/resave set.

M2's bounded repository-writer and fresh game round-trip evidence requirements are closed for the exact allowlisted v0.15 proof input and HP-IV 31→30 transformation. The proof is now canonical on `main` via PR #4.

Broader gaps remain outside this milestone: exact distribution provenance, package hash/extraction transcript, exact PokemonStart/CFRU-JP integration revision, version/build generalization, emulator-footer semantics beyond opaque preservation/reporting, support for non-allowlisted saves, and field-specific writer coupling. No protected binary should enter this repository.

## Exact-v0.22 practical product sprint — candidate evidence refresh — 2026-10-07

The candidate branch independently reproduced the private Cycle 1 return
(`6 -> 7`), naturally progressed save (`7 -> 9`), and Cycle 2 return
(`9 -> 10`). Cycle 1 and Cycle 2 each passed the structural acceptance harness,
preserved the prior active slot, retained requested semantics and remained
eligible. The Cycle 2 return retained Money `7,654,321`, Friendship `181` and
Potion x2. The live disposable save and frozen returned snapshot matched after
mGBA was fully exited. The harness's `r4_complete=false` is retained because
only a Human can attest the visual/gameplay actions.

Human gameplay attestation is recorded separately: exact-v0.22 load and normal
SAVE in both cycles; ordinary Inventory deletion/save and Antidote purchase/save
between cycles; and, in the separate Rattata import check, summary/move display,
healing, battle action, battle completion and normal SAVE. These observations
are not inferred from counters or hashes.

Local private-input verification independently rechecked the three Inventory
record sequences and stable section13 checksum, the candidate's in-place
Antidote remove/insert round-trip, the exact template-import candidate hash,
Party count and byte envelope, and the returned Rattata structural identity.
Candidate implementation evidence includes the corresponding fail-closed
predicates and tests. The Rattata result remains one exact game-generated
record import; it does not claim arbitrary Pokémon creation. Details and
sanitized hashes are in `docs/v022-product-sprint-completion-evidence.json` and
`docs/v022-native-inventory-and-template-import-evidence-20261007.md`.

The sprint candidate is experimental and pending fresh-context independent
review. It has not been adopted on `main`, promoted to Stable or publicly
released. Private ROM/save inputs remain outside Git.
