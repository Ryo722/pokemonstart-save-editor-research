# Post-FL2 Phase A / B Human decision packet

2026-10-07 JST。状態: **PASS_POST_FL2_PRIVATE_ACCEPTANCE / DESIGN PREREGISTERED / IMPLEMENTATION NOT AUTHORIZED**。

## 正本・実行範囲

- fresh fetch した remote main: `d4740a665d1a4f070a7540d8964e6838e393392b`。
- FL2 採用 SHA: `e44e85358be9a1e72e0cd84c65d446eec5bd81c2`。`git diff` で採用時から current main まで Python と capability JSON の変更なしを確認。
- docs/decision-record.md、post-fl2-acceptance-and-reusable-envelope-plan.md、post-fl2-codex-goal-handoff.md を支配契約として fresh-read。README、FL2 candidate record、capability、evidence ledger、CLI/core、3 bounded editors、関連 tests も確認。
- canonical code を `git archive origin/main` でこの packet 隣の canonical/ に展開し、変更せず実行。リポジトリの現在の作業ブランチ・既存ファイルは変更なし。
- local main は `5d81e77358f95394dea62f94ba993e3ba24a4197`。これは remote main と異なるが、実行基準に使わず、更新もしない。
- private inputs は既存 private workspace と module-configured path の読み取りで発見。ROM/save やゲーム assets を Git にコピーせず、新規 save 出力は CLI の PRIVATE_ROOT 制約に沿う repo-external disposable directory のみ。
- 実行環境: macOS 26.6.2 arm64 / Python 3.13.7 / Clang 17。

## Phase A: 再現した証拠

ROM SHA-256: `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`。

capability JSON SHA-256: `cb5f4ebc55df500c6dd739004c462e95a3a59741793da2704d1cc25f050d9cbf`。

Money / Party input: `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`。
Inventory input: `b32abee33dc951c61068b4a83f4bc06215db8a86d880f07620a1aece82ccca50`。
どちらも 131,088 bytes。前者 active slot 1 / counter 3、旧 slot 0 / counter 2、両方 key 0 / Money 1,234,567。
後者 active slot 0 / counter 2 / Money 3032、旧 slot 1 / counter 1 / Money 3000、両方 key 0。
これらの構造値は今回 writer/verifier を import しない独立 read-only auditor でも確認した。

全件で subprocess により current unified CLI の inspect / preview / write を実行。
inspect の family support、preview の semantic/diff、underlying derive と candidate bytes の一致、preview hash と persisted bytes の一致、repository verifier 再検証を assertion で確認。
preview 前後に private directory 全ファイルのサイズ/mtime inventory を比較し publication がないことを確認。
各出力への再 write および source への write は exit 2 で拒否し既存 bytes は不変。
ROM と検証開始時の全 retained saves の SHA-256 は実行後も一致。
独立 auditor で全チェックサム、signature、section mapping / counter / active slot、完全 byte diff、inactive slot、sectors 28–31、opaque footer の不変も確認。

| Case | exact request | changed bytes | Output SHA-256 | prior live output comparison |
| --- | --- | ---: | --- | --- |
| money | `{"money":7654321}` | 5 | `15bdac0d6635c6237549565c49e3752c167e85a33643b89ff722ed3c7d17d569` | 一致 |
| friendship | `{"friendship":51}` | 2 | `cb817b561c1eb29813b5e58524d8536dbdf42cb13065b90b5603a47a73f2a37d` | 一致 |
| iv | `{"ivs":[31,0,26,23,27,29]}` | 5 | `5a688c2c3f2e3f2ba4e9f73788ead12da715adaae861880aa0ef5f7faeb620de` | 一致 |
| level | `{"level":6}` | 10 | `09e58a8cda8277ea107991cbf01ea99fa0d0724ce476330be45ef1d5456ed6dc` | 一致 |
| species | `{"species":2}` | 10 | `fb0d649fe39e286a7bbe5c8bbd8e62e373b3dc8e6048b2405d8f1f647dc54f4f` | 一致 |
| composed | `{"species":2,"level":6,"moves":{"0":1},"ivs":[31,0,26,23,27,29],"evs":[8,0,0,0,0,0],"friendship":53}` | 17 | `29380e12b8c43df9dfd12f3070e2bbe2925e300e9b4a1f3fcafda9fef56ef0d5` | 一致 |
| move | `{"moves":{"0":1}}` | 3 | `75ecb4f2b95ff716524a66593ad4a24412aadf38578bdb451f93e5c172b646d4` | 対応する同一入力の live identity なし |
| inventory | `{"slot":0,"item_id":13,"quantity":3}` | 1 | `51129cdd5168f2f9f3d28966085bfdd4ae094c2a705052253001cc3d189c987b` | 一致 |

7 件は capability profile の prior live-confirmed hash と一致し、既存 retained FL1 output と bytes 単位でも一致。
move 単独の historical output `ded29c2b307343b662ebcdf0889f7b2e24f0952a453e7622049b655e40891efb` は IV 編集後の入力から生成されたもの。
今回の unified move は baseline input に対する bounded operation なので、その identity への一致を要求しない。
この 1 件は **unified-wrapper acceptance のみ**。過去とは異なる output への新しい live/gameplay 証拠には数えない。
新規 mGBA 実行は不要だった。現行 unified path と対応する underlying module の差異はない。

fail-closed checks: generated Money output の inspect は UNSUPPORTED_SAVE_PROFILE、Money preview は拒否。
ability_selector write、Money target 1、Inventory target 2、v0.15 ROM も拒否。
exclusive-create の実装は O_CREAT | O_EXCL、0600。実際の existing-file/source overwrite 拒否を再現し、同時競合時の仕様はコードと既存 tests を根拠にする。新しい race stress test を実行したとは主張しない。

## コマンドと検証

各 case の正確な argv / exit / status は local private log に保存。非機密の request / exit / status と結果は post-fl2-acceptance-results-20261007.json に記録。実行 assertions は local acceptance.py に保存。
識別用の入力・出力名を置換した共通実行形は以下。

```text
git fetch origin main
git log -1 --format='%H %s' origin/main
git archive origin/main -o /private/tmp/post-fl2-canonical.tar
git diff e44e85358be9a1e72e0cd84c65d446eec5bd81c2 origin/main -- '*.py' docs/fast-lab-v022-capability.json
python3 pokemonstart_fl2_cli.py inspect INPUT --rom ROM
python3 pokemonstart_fl2_cli.py preview INPUT --operation FAMILY --changes-json REQUEST --rom ROM
python3 pokemonstart_fl2_cli.py write INPUT NEW_OUTPUT --operation FAMILY --changes-json REQUEST --rom ROM
python3 pokemonstart_fl2_cli.py write INPUT EXISTING_OUTPUT --operation FAMILY --changes-json REQUEST --rom ROM
python3 pokemonstart_fl2_cli.py write INPUT INPUT --operation FAMILY --changes-json REQUEST --rom ROM
python3 /private/tmp/post-fl2-acceptance-20261007/independent-audit.py
```

unified CLI に verify subcommand はない。write の内部 persisted revalidation と `verifier.verify_file(OUTPUT)` を別途実行して verify requirement を満たした。

- FL2 focused 10 passed。
- Fast Lab named tests 21 passed。準備/PKS/read-path 14 passed。合計 35。
- mGBA harness 11 passed。
- full repository 176 total / 160 passed / 16 skipped / 0 failed / 0 errors。
- py_compile 70 Python files PASS、capability JSON parse PASS。
- canonical adoption→remote main diff check、現作業ツリー diff check PASS。
- tracked 110 paths の protected/executable suffix scan: 0 matches。
- Gitleaks canonical snapshot: no leaks、exit 0。
- ローカル assertion harness の初回は JSON の move key が CLI では string、Python 内では integer になるため比較 assertion で停止。比較側を JSON round-trip 正規化して全件再実行し PASS。production code は変更していない。初回の既生成 outputs は別 disposable directory に残し再使用・上書きしなかった。

16 skipped は新しい Windows/GUI/live acceptance を意味しない。静的 verifier は game semantics や unchecked-tail integrity の一般保証でもない。

## Phase B: family ごとの独立比較

次の条件は **設計事前登録**。現行 writer eligibility を変更せず、他 family へ条件を横展開しない。
3 family 共通の候補 build gate は上記 exact ROM SHA / schema 1 / profile hash agreement。
save file 自体には ROM identity 証明がないため、exact ROM を supplied した事実だけで save origin を認定しない。
owner がこの build 用と指定した private save に限定し、未知 build の自動移行・判定は対象外。

比較用の保守的 slot gate: 両 slot valid、全 logical IDs 0–13 が各 1 個、全 signatures / covered checksums valid、slot 内 counter 一意。
両 counter は 0..0x7ffffffe、隣接差 1、slot index == counter % 2、新しい方を active と verifier が選択。
physical order は決め打ちせず logical ID から再構成。empty slot、counter wrap/sign-boundary、equal/nonconsecutive counters、partial erased slot は初回 reusable proof の対象外として拒否。
Party count は各 valid slot で 0..6、record bounds に収まること。record count 以外の一般的な party correctness を verifier が保証すると解釈しない。

| Design surface | Money | Party（最小候補: friendship のみ） | Inventory（最小候補: existing Potion のみ） |
| --- | --- | --- | --- |
| gate / key | 共通 build/slot gate、両 slot key 0、Money range 0..9,999,999 | 共通 gate、両 slot key 0、party count 1、active party[0] 完全100 bytes が retained baseline record と一致 | 共通 gate、両 slot key 0、active section13 offset ADC に ID13/qty2、AE0..FF3 が全0 |
| semantics / request | integer（bool拒否）target 7,654,321 のみ、現在値が target なら拒否 | request {friendship:51} のみ、starting friendship50、species1/level5/EXP134 等全recordを固定 | request {slot:0,item_id:13,quantity:3} のみ、全値strict integer、既存 qty2→3 |
| representation | sec1@290 LE32、sec0@F20 LE32 key（0のみ） | sec1@38 + record offset41 u8、名前/PID等はprivate baseline比較、publicにはrecord bytesを掲載しない | sec13@ADC LE16 ID + LE16 quantity、key low16 XOR（0のみ） |
| checksum coverage | money word は sec1 covered FF0 内、checksumを再計算 | friendshipはsec1 covered、checksumを再計算 | quantityはsection13 covered450外、checksum変更禁止 |
| coupling / caches | party / inventory / key を完全保存、既知 Money cache 更新なし。未知 coupling はprivate proofで検証 | friendship のみなら stats/EXP/moves/cache 変更なし。level/EXP134の不一致を維持 | item ID/pocket/order/qty high byte/他record変更禁止、capacity不明、cacheとnormal persistenceは要証明 |
| exact diff | sec1 base+290..293 と FF6..FF7 のみ、値/ checksumは独立計算 | party0 base+41 と sec1 checksum 2 bytes のみ | sec13 base+ADE の low byte 02→03 のみ、high byte0保存 |
| invariant / preservation | 編集範囲外すべて同一、inactive全体、sec28–31、footer、各tail、party、section metadata保存 | 同左。ability bits / stat caches / full party record minus friendship も同一 | 同左。unchecked tail は quantity 1 byte 以外完全同一 |
| post validation | verifier PASS、独立 Money decode / checksum / full outside-range equality | verifier PASS、friendship51、full record差分と独立 checksum | verifier PASS に加え独立 quantity decode/full-tail差分。verifierだけでは edited tailを検出不能 |
| malformed / ambiguity | 共通 gate や source race / key / range / request違反はreject | record不一致、friendship違い、extra party、他request、stat操作はreject | shape不一致、別item/slot/quantity/extra tail/nonzero keyはreject |
| normal resave / chain proof | 非canary progressed save→固定target編集→通常resave→通常Money変化→同target再編集が必要 | game activityでrecordが変わると狭いpredicateから外れやすい。少なくともrecord不変のresaveとMoney編集後のfriendship操作を要確認 | 複数normal resavesで qty2のsame-shapeを認識し、qty3保存と既存slot保持、game側のqty変化後再編集を要確認 |
| user value | 通常progressでsave hashが変わっても同じ補充操作が使える | 他save bytesだけ変わる状況には有効。実際のparty成長は対象外 | Potion 1個増加だけ、single populated pocket形状への依存が強い |
| complexity / failure cost | 最低。4 bytes+checksum、誤slotはreload/recoveryが必要だが原本保存で回復可 | friendshipだけは小さいが認識が狭い。practical Party全体に広げるとspecies/growth/PP/HP/ability等のcoupling急増 | 1 byte編集だがpayload tailがunchecked、shapeが偶然一致するリスク、layout/capacity認識が弱い |
| existing evidence | 今回private受入、prior v0.22 Money live、既存v0.15 lifecycle（別build参考のみ）、v0.22 retained normal pair Money3000→3032 | 今回friendship/IV/level/species/composed受入、prior full100-byte live、normal v0.22 Party再利用は未証明 | 今回qty2→3受入、v0.22同file normal pair qty1→2、prior live3 |
| cheapest missing proof | v0.22 noncanaryで独立diff→load→normal resave→game Money変化→2回目編集→reload | record完全一致の新saveを用意しfriendship→load/resaveを確認。record認識を緩める根拠が別途必要 | unchecked-tail認識と通常resave後のqty保存/同一slot認識をもう1系統で確認 |

いずれも recovery policy は source immutable、新規/private/0600/exclusive output、hash receipt、原本の手動 reload。live emulator save の自動置換は禁止。
output は `<family>-<input_sha12>-<request_digest12>-<unique>.sav` 等の衝突しない新規名で作成し、既存path/symlink/source aliasを拒否。write前後のsource/ROM hash照合、persisted equality、fsync、失敗時はこの処理が作成したoutputだけcleanup。
game normal resave では counter・rotation・time・game state の変化を編集diffと混同しない。diff許可はwriter transactionのみに適用し、resaveは別のindependent transition監査で評価。新しいglobal volatility maskは導入しない。

## 選択: Money 1 family のみ

**最初の reusable-envelope family は Money（固定 target 7,654,321 / key0 / exact-v0.22）とする。**
選択は編集 byte 数だけでなく認識の強さ、再利用価値、必要 private proof の総コストによる。
retained Inventory source の active Money3032 は Money canary hash外だが同じ構造・key0。この自然progressed入力が既にローカルにあり、未知 artifact の入手待ちなしで次のproofへ進める。
現在はこれへの Money write を行っていない。正常構造が reusable eligibility を証明したとも主張しない。
Inventory はbyte数では小さくても unchecked tailとsingle-record shapeの追加検証が必要。
Party のfriendshipだけをrecord固定で再利用しても実用範囲が狭く、Party全体の再利用は Money よりcouplingが多い。

## Money exact fail-closed predicate（実装前事前登録）

以下すべて成立する場合に限る。条件の緩和は別承認。

1. owner-designated exact-v0.22 private input、supplied ROM SHA が exact profile ROM hash と一致、schema==1、各module/profileのbuild contract一致。recorded source file SHA はreceipt/race検出用に使い、旧canary membershipはこの将来Money-only pathでのみ置換候補。
2. file length は 0x20000 または0x20010。上の保守的 slot gate を両slotに適用し、全sectionsを独立checksumでも確認。empty/corrupt/ambiguous/wrap/sign-boundary/nonconsecutive/parity違反を拒否。
3. 両slot sec0@F20..F23==0。両slot sec1@290 decode が0..9,999,999、両slot party count0..6、record bounds valid。非zero keyとout-of-rangeを拒否。
4. request のkey集合は exactly {money}、valueの型は exactly integer（boolやfloat/string拒否）、value==7,654,321。active current value !=7,654,321。noopは outputなしでreject。arbitrary targetを追加しない。
5. active logical sec1 の physical baseを B とし、candidate Y は原本 X のclone、Y[B+0x290:B+0x294]=LE32(7654321)、Y[B+0xFF6:B+0xFF8]=LE16(C(Y[B:B+0xFF0]))。C(P)=fold16(sum(LE32 words(P)) mod2^32)。fold16(t)=((t&65535)+(t>>16))&65535。
6. exact postcondition は len(Y)==len(X) かつ Y が前項の独立計算 candidate と全byte一致。D={i:X[i]!=Y[i]} は非emptyかつ {B+290..B+293,B+FF6,B+FF7} の部分集合。checksumは値の結果として同じになる場合もあるので、checksum changed であること自体は要件にしない。
7. repository verifierと独立parserの両方でYをaccept。active index/counter、全slot/section metadata、両key、party count、party bytes、inactive slot全体、sectors28–31、footer、checksum-excluded tails はXと同一。active decoded Moneyは7654321。Money以外のsemantic操作は存在しない。
8. private paths resolved / regular input / separate nonexistent output / source aliasとsymlink rejection / exclusive creation。sourceとROMのhashがpreview→prewrite→postwriteで一致。persisted bytes==preview candidate、fsyncと再verifyが成功。失敗時はfail closed、newly-created outputのみ除去、原本不変。

このpredicateはMoney transactionの局所安全条件であり、save origin・全ゲームsemantics・他field eligibilityの認証ではない。
両slot valid/consecutiveの制限により初回saveやcounter境界は対象外。これが最初のbounded reusable sliceの明示的trade-off。

## 必須 private proof preregistration

次の実装承認後に実施し、全成功以前に reusable eligibility を採用しない。

1. retained noncanary input `b32abee...ccca50`（正本profileのnormal pair、activeMoney3032）をhashで固定。ROM/sourceの前後hashを記録。Money predicateを全条件監査。現在canary `d707...25caf` でも旧exact output `15bd...7d569` が変わらないことを確認。
2. Money-only qualification candidateで noncanary→7,654,321 をprivate新規outputへ生成。writer/verifierをimportしないauditorで全署名/checksum/section map/semantic decode/full diff/保存範囲を検証。CLI inspect→preview（publicationなし）→write（exclusive）→persisted verifyを再実行。
3. その使い捨てcopyをexact-v0.22でloadし、表示/live Money7654321とparty/inventoryの非変更を観測。正常ゲームsaveでMoney維持、slot/counter/rotationとactive payloadを独立に監査。save成功をmetadataだけから推測しない。
4. ゲーム内の通常Money増減（例: 既知の購入）を行い、actual starting Moneyと取引額を記録して normal resave。新SHA / counter進行 / key0 / decodedMoney / 対象predicateを確認。新progressed saveから同targetを2回目編集し、新規outputを独立監査、reload/live値ともう1 normal resaveで保持を確認。これで writer→game→writerの繰り返しを証明する。target維持のresaveに対する同targetrequestはnoop拒否も確認。
5. 両slot方向、logical section rotation、0x20000/0x20010 opaque footer保存のoffline coverage。自然artifactがないvariantはsyntheticとして明記し、private/live evidenceと混同しない。
6. 負例: ROM違い/profile不一致、unsupported size、partial erase、bad checksum/signature、duplicate IDs、inconsistent/equal/nonconsecutive/parity/wrap counters、activeまたはinactive非zero key、Money range違反、party count違反、bool/float/string/extra key/他target、noop、source alias/symlink/existing output、source/ROM race、persisted corruption、unauthorized family combination。出力未生成と原本不変を確認。
7. focused/full/static/security と independent auditをすべてPASS。private/game observerのfactsと推論を分けたevidence recordをHumanへ返す。v0.15 lifecycleをv0.22の代用にしない。

chaining scopeは Money→normal game progress→Moneyのみ。Money→Party/Inventory combined writer eligibilityを意味しない。他familyとの同file編集が必要ならそのfamilyの現行exact gateを維持したまま、別のdesign/proofを要求する。

## Evidence labels / limitations

- **Reproduced evidence**: 今回の test/static/security、production delta absence、独立 auditor結果。
- **Local private-input verification**: ROM/source/output hashes、CLI/private保存挙動、7 retained output byte-equalities、8 bounded derivation equalities。
- **Prior observation**: canonical profileのFL1 live/game-memory observations。今回gameを新規操作したとは主張しない。
- **Upstream evidence**: canonical code/ledgerがpinする CFRU-JP / FireRed source layout/checksum/stat basis。upstream current revisionを再調査したわけではない。
- **Hypothesis / preregistration**: Money semantic predicateが naturally changed saves に十分かどうか。次のprivate lifecycle proofで試験予定で、まだprovenではない。

## Human decision surface

Phase A disposition: **PASS_POST_FL2_PRIVATE_ACCEPTANCE**。現行CLIの修正は不要。
Phase B disposition: **Moneyのみを最初の bounded reusable-envelope qualificationに推薦**。
benefit: 旧canary SHA以外の自然progressed owner saveで同じ既実証Money補充を使えるようにする。
risk/trade-off: source値の変化を許すためunknown couplingはgame lifecycleで要確認。両valid/consecutive/key0/固定target制限は残り、初回save/counter boundary等の利便性は限定。
downstream impact: Money-only support label/predicate/receiptとCLI/tests/profile docsの限定変更が候補。Party/Inventoryのexact SHA eligibility、Stable Lane、GUI/build/key/他fieldはこのauthorizationの対象外。

次に別途必要な正確なauthorization scope:

> AUTHORIZE EXACT-V0.22 KEY0 FIXED-TARGET MONEY REUSABLE-ENVELOPE QUALIFICATION

承認対象は本packetのMoney predicateだけを実装するlocal candidate branch、FL2 Money dispatch/inspect supportの限定接続、independent auditor/negative tests、上記 private proofと evidence record。
固定targetは7,654,321だけ。上記条件の緩和、arbitrary Money、Party/Inventory gate緩和、combined reusable operation、nonzero key、別build、Stable promotion、GUI/public release、protected publication、canonical main mergeは含まない。
資格実装とprivate proof後もcanonical adoption/mergeは別のHuman decision。

現時点は設計ゲートで停止。broader writer実装もexact-save gate変更も実施していない。

## 最終監査

remote main を再fetchして同じ d4740a6 を確認。展開した110 tracked filesはremote mainと全byte一致。local main SHAとclean worktreeは実行前後で不変。packet全体もGitleaks no leaks。12 completion conditionsの現状監査はpost-fl2-completion-audit-20261007.mdに記録。

## Evidence branch publication

Human は本gate完了後に作業ブランチのpushを承認。今回のdocs/evidenceだけをcandidate branchに記録し、canonical mainは変更しない。本文のclean worktree/main不変は受入検証実行時点の証拠。raw private command logと使い捨て検証scriptsはGitへ追加しない。
