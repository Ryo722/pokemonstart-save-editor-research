# Exact-v0.22 composed creation transaction — review candidate

Canonical base: `720f56dac8851e0fd17870dc3bd41c36cbf0f726`.
Review branch: `codex/v022-composed-gui-transaction-20261007`.
Scope: [the controlling authorization](v022-composed-gui-transaction-proof.md).
Disposition: `READY_FOR_INDEPENDENT_REVIEW`, subject to the accompanying
validation/publication evidence. No canonical merge/adoption is performed.

## Exact independent composition

The ROM SHA-256 is
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
The immutable source SHA-256 is
`2d7ac8d6214e8b94018a3fe3f65c30270198098a9cb658318248b514242511ac`.
Fresh repository verification and independent stdlib parsing agree on active
slot 1, counters 4/5, Party count 3, key0, Money 3032 and the observed ordered
regular-items prefix ID13 x2, ID533 x1, empty slot2/tail.

`party_append_inventory_insert` accepts only an empty request and this exact
root under the unchanged ROM/profile gate. It directly copies the full slot0
100-byte Party record into slot3, changes count 3 to 4, recalculates section1's
checksum and inserts Antidote ID14 x1 at regular slot2. Logical section IDs
determine physical locations. Neither single-operation writer gate is relaxed.

Candidate SHA-256:
`96ce6b3a7c26e6116ce1150ebbf34d345209529f1ce7f192b735164c68f7c7fb`.
Independent complete construction equals the product candidate. Independently
reproduced Party changes (52 bytes) and Inventory changes (2 bytes) have an exact
54-byte union equal to the composed changed-offset set. Both primitive orders
equal the direct candidate at the complete-byte level. The count was derived,
then compared to prior evidence; 54 is not a writer/auditor acceptance constant.
Original Party records, item order/tail, Money, key, inactive slot, counters,
footer and every unrelated byte remain unchanged. The repository verifier passes.

The two single-operation outputs still reproduce their canonical hashes:

- Party: `e22309a73236504d201d393f8146f113eb261d2486527c66ca0fd8e8f4bf2a5b`.
- Inventory: `588b4cb5b96468cd2baf4d67c36f4048020f5205fa28ff57c3a094147409c596`.

## One SAVE and fresh-process cold reload

Only repo-external disposable ROM/save copies were used. Pre-SAVE startup
attempts ended without normal SAVE; bootstrap enrollment and title/Continue
readiness were resolved by inspecting the owned emulator UI. RAM contents alone
were not treated as gameplay readiness. The successful session visibly reached
normal shop gameplay and independently reproduced count4, all four complete
100-byte records, all three ordered item records and Money3032 before SAVE.

Exactly one ordinary Report/SAVE was performed. Returned save SHA-256:
`274dece5fd8828710d2fccf470e4e2cf47cac6998ef306f114727f5d3565ec24`.
Independent audit proves slot1 to slot0, counter5 to counter6, rotation+1,
saved-game statistic5 to6, prior active-slot preservation, all four Party records,
the complete observed Inventory tail, Money3032 and key0. The verifier accepts it.

All logical payload changes are published as offsets: play-time region (3),
EventObjects region (10), EventObjectTemplates region (177), saved-game statistic
(1). Region labels retain the adopted source-backed classifications and do not
qualify a general volatility predicate. All logical metadata/checksum changes
and section mappings are also recorded. Sectors28/29/30/31 were unchanged in this
run. Footer offsets4/5/6/8/9 changed, with field semantics unqualified. The full
physical byte-change count is 3736, including the normal new-slot write.

A distinct fresh mGBA process cold-loaded a separate returned-save copy, visibly
reached normal gameplay and reproduced count4, all four complete records,
ID13 x2 / ID533 x1 / ID14 x1 and Money3032. Its save stayed byte-identical after
shutdown. Screenshots and raw memory/logs remain private. Direct live key-address
qualification was not added: independently read root/returned key0 and the live
item/Money representation establish this proof's key0 assumption.

## Explicit localhost combined choice

The existing single choices remain available under their original gates. The
GUI adds exactly `Party append + Antidote insertion`. Preview shows both Party
3 to4 / slot0 to3 and Antidote ID14 x1 / slot2 / Money unchanged. Source, ROM,
preview and download checks retain the existing in-memory delivery safeguards.

Actual private-root NiceGUI user simulation and real Chromium each performed
upload, inspect, select, preview, generate and download for all three creation
choices. All downloads equal their corresponding independently audited core
candidates. The combined download equals the game-confirmed candidate above;
no second game round trip was performed. Chromium checked both displayed semantic
changes. The real listener was exclusively IPv4 `127.0.0.1:18866`; browser network
requests were restricted to loopback. No screenshots, video or traces were enabled
in the browser proof. The owned server and emulator processes were stopped.

## Validation and publication boundary

The [sanitized evidence JSON](v022-composed-gui-transaction-evidence.json) records
exact offsets, identities, proof results and final static/security checks.

- Composition: 8 tests PASS; Party append: 5 PASS; Inventory insertion: 5 PASS.
- Focused v0.22: 28 PASS, including 7 GUI unit/simulation tests.
- Actual private NiceGUI and Chromium: 3 operations each PASS.
- Exact private negative inputs: 13 PASS without gate mocks, including altered
  Party/template/destination/Inventory shapes and normal-progressed/single-output
  sources. Additional tests cover ROM/profile, nonempty requests, Money/FL2
  composition attempts, stale source/ROM/preview, and corrupt download rejection.
- Fast Lab: 21 PASS; FL2: 10 PASS; M4 delivery: 45 PASS with 15 existing skips.
- Full repository unittest: 202 PASS with 15 existing environment-gated skips.
- Python compilation, all repository JSON parse, diff check, protected-artifact
  scan and redacted Gitleaks scans are recorded in the evidence JSON.

Only source/tests/auditor/docs/sanitized metadata enter the review branch.
Original ROM/save, immutable proof root and disposable ROM hashes are rechecked.
Browser dependencies/binaries, ROMs, saves, private logs, screenshots, memory,
patches, packages and other protected assets remain excluded from publication.

## Non-claims

This proves only the exact-root composition of these two adopted operations.
It establishes no arbitrary generation/templates/items/quantities/slots/pockets,
deletion/reordering, Money or other FL2 composition, reusable progressed-save
eligibility, self-application, nonzero keys, broader builds, arbitrary operation
commutativity, normal-save volatility predicate, Stable promotion, LAN/public
delivery or public release. The paused Money candidate remains excluded.
Canonical main is unchanged; review and adoption remain separate Human gates.
