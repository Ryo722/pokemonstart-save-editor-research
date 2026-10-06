# v0.22 creation proof progress

Canonical base: `88d5981bb35ce379fd018986b013a522ab0340b3`.
Review branch: `codex/v022-creation-proofs-gui-20261007`.

The controlling scope remains `v022-creation-proofs-and-gui-prototype.md`.
The paused Money candidate has not been imported. No canonical main mutation
or capability adoption is claimed.

## Fresh private proof root

The exact ROM rehashed to
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`
(33,554,432 bytes). The previously running dedicated emulator had no game
file open and no window; its shutdown was confirmed before snapshotting.
New repo-external read-only copies were created and rehashed. The source save
identity is
`2d7ac8d6214e8b94018a3fe3f65c30270198098a9cb658318248b514242511ac`
(131,088 bytes, including a 16-byte opaque footer).

Repository verification and the independent stdlib parser agree: active slot
1, counters 4/5, key 0, party count 3, Money 3032. All three complete party
records were compared privately; only their hashes are published. Live RAM
corroborated regular items slot 0 ID 13 quantity 2 and slot 1 ID 533 quantity 1,
with no other populated records in the observed 450-entry live pocket.

The starting screen was inside a shop. The reported exact clerk-facing
position was not independently established at initial load. The operator later
moved the disposable session to the intended interaction position. A screenshot
of that position stays private; it is not a saved proof root or writer gate.

## Party append: passed bounded game persistence proof

The first unoccupied index is 3 according to the verified party count. Its
storage contained stale bytes; unoccupied does not mean all-zero. The experiment
copies the existing slot 0's exact 100-byte record into slot 3, increments the
count 3 to 4, and recomputes only the active logical section 1 checksum.

The product derivation equals an independently computed complete candidate.
Its SHA-256 is
`e22309a73236504d201d393f8146f113eb261d2486527c66ca0fd8e8f4bf2a5b`.
Exactly 52 bytes change: one count byte, 49 bytes within the 100-byte destination
record, and two section checksum bytes. Every other byte, including original
party records, slots/counters, item records, Money, and footer, is unchanged.
The complete changed-offset list is in `v022-creation-proof-evidence.json`.
Logical section IDs determine physical locations; rotation is not hardcoded.

The disposable candidate reached normal gameplay. Party UI showed four members,
and all four live 100-byte records equalled their offline counterparts.
A normal in-game Report/SAVE completed. The returned save reverified and hashed
to `ff8c60e100bf8df8f005ddd6fb1d70e6a7f2b061b82f026a7c36dde0b279bae0`.
The independent audit confirmed slot 1 to 0, counter 5 to 6, rotation +1,
previous active slot preserved, all four party records unchanged, and Money
3032 preserved. A fresh mGBA process cold-loaded that returned save, reached
normal gameplay, and reproduced all four complete live records. The cold-load
copy remained byte-identical after shutdown.

Normal-save payload changes are reported in full as offsets. They fall within
play time, EventObjects, EventObjectTemplates, and the saved-game statistic.
Fresh-read pinned CFRU-JP
[`include/global.h`](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/include/global.h)
places EventObjects at 0x6A0 and EventObjectTemplates at **0x8E0**, through 0xEDF.
These are region classifications of this observed transition, not a reusable
volatility predicate or a claim that every byte in those regions is harmless.
Opaque footer changes are reported separately without assigned semantics.

## Inventory insertion: passed bounded game persistence proof

The retained pre-purchase root is the same immutable source as the Party proof.
The operator moved the disposable session to the clerk and opened the sales
list. The agent reproduced clerk-facing A -> Buy A, inspected the bag as well
as RAM, and bought exactly one absent Antidote for 200. Live RAM then showed
slot 2, ID 14, quantity 1, with Money 3032 -> 2832. The two existing items and
all three party records remained unchanged.

Normal Report/SAVE produced post-purchase identity
`374ce5825800e65b3f992b23e568fa791ac352b82170a4aea14763eca1365b00`.
A new read-only repo-external post-purchase snapshot was retained. Independent
logical-section reconstruction across slot/counter 1/5 -> 0/6 and rotation +1
confirmed the empty -> ID14/quantity1 record at logical section 13 offset
0xAE4. Existing records/order and the remaining regular tail were preserved.
The observed quantity is a little-endian u16 under key0; nonzero-key behavior
is not proven. The field is beyond section 13's 0x450 checksum coverage.

The complete acquisition diff is retained as offsets in the sanitized JSON.
It distinguishes the item insertion and expected Money charge from play time,
EventObjects/Templates, script-variable-region updates, save/step/shop counts,
and three auxiliary state bytes with unqualified field semantics. In particular,
section 4 @ 0xCA and section 13 @ 0x778/0x7DE are reported, not masked. Public
pinned [save.c](https://github.com/kapibarasan000/CFRU-JP/blob/e24a16fe39e27ae162faf5b78596d1f3df18489d/src/save.c)
backs parasite-tail storage and sectors 30/31; the exact build's differential
controls the item placement. This is no generic volatility/eligibility envelope.

The offline insertion returns to the immutable pre-purchase root. Its complete
candidate SHA-256 is
`588b4cb5b96468cd2baf4d67c36f4048020f5205fa28ff57c3a094147409c596`.
Product and independently computed candidates agree in every byte. Only absolute
offsets 76516 and 76518 change; checksums, Money 3032, existing items, party,
footer, counters and all other bytes are preserved.

The candidate reached normal gameplay, showed Antidote x1 in Bag, and reproduced
all three live party records, existing item records/order, and Money 3032.
The Report macro performed a normal SAVE, producing
`b34f5bc4f3e9bf8930be95c66fa5ae451d7c10903f1f9735d767bf8d443ba686`.
The independent audit reproduced slot 1 -> 0, counter 5 -> 6, rotation +1,
old active slot preservation, all party records, Money and the complete observed
regular-items tail. Ordinary save also updated sector 30 offsets 1814/1816/1818;
these are fully reported as extended-save state with field semantics unqualified.
The offline writer did not touch them. A new mGBA process then cold-loaded the
returned save, reached gameplay and reproduced the three items, three party
records and Money 3032. The cold-load save stayed byte-identical after shutdown.

## Localhost GUI prototype: proof gates passed

Both creation proofs passed before GUI implementation began.
`pokemonstart_v022_web.py` reuses M4's in-memory delivery pattern and loopback
server options, with the v0.22 creation/FL2 core and no v0.15 journal authority.
The prototype exposes read-only inspection, canonical FL2 operations only under
their unchanged existing gates, and exactly the two new creation operations on
the exact fresh root SHA. New operations are Fast Lab experimental. It has no
save-filesystem publication or live-save overwrite API: only separate verified
downloads. Upload/failed-preview/change events invalidate prior plans and outputs.
ROM identity is rechecked on upload, preview, commit and download.

NiceGUI user-simulation tests cover upload -> inspect -> preview -> commit ->
download for both operations, stale source/ROM/output rejection, unsupported
inputs, source immutability and unchanged canonical Money/Party/Inventory gates.
Private user-simulation smokes used the actual read-only ROM/root with no gate
mocks. Both downloads equalled the game-confirmed core output identities and
passed the separate stdlib complete-candidate audit plus repository verifier.

Real Chromium 153.0.8010.12 (Playwright 1.63.0) also performed both workflows
against the actual loopback server and private root. Both downloads matched the
same core identities exactly. The test enabled no video, screenshots or tracing
and blocked non-loopback requests. Browser payloads stayed repo-external.
The real socket probe observed only IPv4 127.0.0.1:18766, and the initial HTTP
page returned 200. No second game round trip is needed for identical GUI bytes.

Launch with the existing UI dependency environment:

```sh
.venv/bin/python pokemonstart_v022_web.py --rom /path/inside/PokemonStart-private/exact-v022.gba
```

The default port is 8766. Host binding is fixed to 127.0.0.1. This branch is a
review candidate, not canonical adoption, Stable support or a public release.

## Controller macros

`research_harness/v022_macros.py` contains controller-only title/Continue and
Report sequences. Title readiness must first be confirmed visually: save data
can already exist in RAM during the opening animation. Report requires the
observed field state and default menu cursor. Macros do not constitute proof;
their resulting gameplay and save must still be audited. No macro writes RAM,
ROM, source files, or the emulator's original live save.

## Non-claims

This Party proof is exact-input, template-slot-0 duplication only. Arbitrary
Pokémon synthesis, other input saves/templates, PID/OT/name generation,
Pokédex/event coupling, battle/legal behavior, generic inventory creation,
nonzero-key support, Stable promotion, and public delivery remain unproven.
Final validation/publication results are recorded below and in the sanitized JSON.

## Final validation

- Party creation focused tests: 5 PASS; Inventory insertion focused tests: 5 PASS.
- v0.22 focused suite: 20 PASS, including 7 GUI unit/simulated-browser tests.
- Actual private Chromium workflows: 2 PASS, core/independent equality.
- Fast Lab regressions: 21 PASS; FL2 regressions: 10 PASS.
- M4 delivery regressions: 45 tests, PASS with 15 environment-gated skips.
- Full repository unittest: 194 tests, PASS with the same 15 skips.
- Python 3.13.7 py_compile: all 80 repository Python files PASS.
- Capability JSON parse and git diff --check: PASS.
- Push-safe text/artifact scan: 124 files, no binary/protected save/ROM/package/
  patch/executable/image/memory artifacts or newly embedded raw hexdumps.
- Gitleaks 8.30.1 directory scan of the push-safe file set: no findings.
- Original ROM/save, immutable proof ROM/save, and all disposable ROM copies
  retain their expected hashes.

Skips retain their platform/private-fixture gates; Windows private integration
and public/cross-platform release are not inferred from this macOS run.
Playwright/Chromium are optional test-only dependencies in ignored local work
storage, and no browser binaries, payload downloads, private raw logs or game
screenshots are publication material. Review-branch publication is distinct from
canonical merge/adoption. Exact published HEAD is returned in the handoff.
