# Exact-v0.22 Fast Lab creation proofs + localhost GUI prototype — 2026-10-07

Status: **CANONICAL AUTHORIZATION / ACTIVE NEXT-WORK BOUNDARY**

GitHub `main` remains the only durable canonical authority.

## Human authorization

Controlling authorization:

> `AUTHORIZE EXACT-V0.22 FAST-LAB PARTY-APPEND + INVENTORY-INSERTION PROOFS AND LOCALHOST GUI PROTOTYPE`

This authorization intentionally pivots the Fast Lab critical path from the paused Money reusable-envelope lifecycle proof toward two concrete creation capabilities and a small local delivery prototype.

## Money qualification status

The Money reusable-envelope qualification is **PAUSED / INCOMPLETE**, not failed and not adopted.

Preserved review branch:

- `codex/money-reusable-qualification-20261007`
- exact pushed HEAD `909e3e50d4cb6a173188d6c97538f03aed464417`
- base `f28c1099db6d3155d40db268b0b0fe42afb94d9f`

That branch contains useful partial implementation/evidence but is not canonical writer capability. Do not build the new creation work on top of it. Start from fresh canonical `main` and keep the Money branch frozen unless separately resumed.

The paused Money record also documents that custody/immutability of one previously used source pathname could not be established across the entire work period. New creation proofs must therefore establish a fresh immutable proof root rather than assuming prior private-path identity.

## Operator-provided private starting condition

Evidence class: **operator-provided / not yet independently reproduced**.

The owner reports that the current exact-v0.22 private game state has been advanced and saved with:

- three party Pokémon;
- the player positioned in front of a shop clerk;
- the exact private v0.22 ROM retained locally.

Local Codex must independently re-hash the ROM, identify the current save, verify structural validity/profile assumptions, confirm the party count and inventory state, and create a fresh immutable/disposable proof snapshot before any writer experiment. Do not treat the live emulator save pathname as an immutable proof input.

## Goal of this work unit

Answer two practical questions as cheaply and safely as possible:

1. Can an additional party entry be created in the first empty party slot and survive exact-v0.22 load + normal save without unexplained corruption?
2. Can an item type not currently present in the regular-items pocket be inserted into a newly observed valid slot and survive exact-v0.22 load + normal save without unexplained corruption?

If both proofs succeed, build a **localhost-only experimental v0.22 GUI prototype** that exposes only the exact capabilities actually proven or already canonical Fast Lab capabilities whose gates still pass.

This is not authorization for arbitrary Pokémon generation, arbitrary item insertion, boxes, arbitrary pockets, broad Party reuse, broad Inventory reuse, nonzero-key support, or public release.

## Phase 0 — fresh proof root

Before writer work:

- fresh-read current remote `main` and this authorization;
- create a new work branch from current `main`;
- stop/flush the dedicated emulator session as needed before snapshotting;
- hash the exact ROM and current save;
- verify exact v0.22 ROM/profile identity;
- run repository verifier plus an independent read-only structural audit;
- record party count, active slot/counter, section mapping, encryption key, current Money, current regular-items records, footer presence and save size;
- copy the current private save to one or more new repo-external proof snapshots; never use the emulator live-save pathname as writer output;
- re-hash source snapshots before/after every experiment.

Protected/private bytes stay outside Git.

## Phase 1 — bounded Party append proof

### Proof target

Prove **party-slot append**, not arbitrary Pokémon synthesis.

Preferred cheapest proof:

- confirm current party count is exactly 3 as reported;
- identify the first empty party slot using source-backed/verifier-backed party layout rather than guessing;
- select one existing valid current party record as an exact 100-byte template;
- create a candidate with party count `3 -> 4` and copy that exact valid record byte-for-byte into the first empty party slot;
- do not alter the copied record's species/PID/OT/name/moves/stats/ability/EXP or other internal bytes in this proof;
- recompute only the required checksum(s);
- preserve all bytes outside the exact party-count/new-record/checksum envelope.

If the current party count or layout differs after independent reproduction, adapt only the slot number/count transition required by the same principle: append one exact existing valid record to the first empty slot, maximum party size 6, no record synthesis. Record the actual bounded transition.

### Required evidence

- independent pre/post byte-diff audit;
- repository verifier acceptance;
- source unchanged;
- exact-v0.22 load reaches normal gameplay;
- party UI/live memory shows one additional member and the appended 100-byte record matches the candidate;
- existing original party records remain byte-identical at initial load;
- perform a normal in-game save;
- independently audit the returned save's slot/counter/rotation transition and confirm the appended member persists;
- reload if needed to distinguish transient RAM acceptance from normal-save persistence.

Failure must not be repaired by broad speculative edits. If exact-copy append does not survive, stop/characterize before attempting record synthesis.

### Non-claim

Success proves one bounded party append primitive. It does **not** prove arbitrary Pokémon creation, legal PID generation, arbitrary species/templates, egg/box creation, Pokédex/event coupling, breeding legality, or generic Party reusable eligibility.

## Phase 2 — bounded Inventory insertion proof

### Differential acquisition

Use the prepared shop position to obtain a clean same-build observation if practical.

- inspect the current regular-items pocket and determine which shop-offered item types are absent;
- choose one inexpensive absent item whose identity can be established from source/game evidence;
- preserve a pre-purchase proof snapshot;
- perform one ordinary in-game purchase/acquisition of that absent item;
- perform a normal save and preserve a post-purchase snapshot;
- reconstruct logical sections across save rotation and independently classify all changes, including expected Money change and normal-save volatility;
- identify the exact inserted regular-item record, its slot/order/ID/quantity representation, encryption-key behavior and whether the bytes are checksum-covered.

If no absent shop item is available, choose the cheapest alternate ordinary game acquisition that can produce a single new regular-item type. Do not guess an insertion slot.

### Offline insertion proof

After the differential is understood:

- return to an immutable pre-acquisition snapshot;
- create a separate candidate that inserts exactly that one observed item record with the observed quantity into the exact proven empty slot;
- do **not** reproduce the purchase Money deduction; the editor proof is item insertion only;
- modify only bytes required for the inserted record plus any required checksum bytes;
- independently audit every changed byte and preserved surface;
- require repository verifier acceptance;
- exact-v0.22 load must show the item present with expected quantity and Money unchanged from the editor source;
- perform a normal in-game save and independently confirm the inserted item persists and other existing item records/order remain coherent.

### Non-claim

Success proves only the exact observed item/slot/quantity insertion shape under the reproduced key/layout. It does not prove arbitrary item IDs, arbitrary pockets, capacity, sorting, deletion, reordering, nonzero-key support or general Inventory insertion.

## Phase 3 — localhost GUI prototype

Enter this phase only if both Phase 1 and Phase 2 pass their required game/save persistence gates.

Reuse the already-proven M4 delivery pattern where useful:

- localhost-only NiceGUI (`127.0.0.1`);
- local file upload/selection;
- inspect before edit;
- explicit supported/unsupported capability presentation;
- preview semantic + byte diff;
- original input preserved;
- new verified output only;
- no automatic write into emulator live-save pathname;
- downloadable/new-file output;
- fail closed when an operation's exact proof gate does not pass.

Implement the v0.22 GUI against the current v0.22/FL2/Fast Lab core rather than reusing the old v0.15 M4 authority model as if it were the same save profile.

The GUI may expose:

- read-only exact-v0.22 inspection;
- existing canonical FL2 operations only where their existing eligibility gates pass;
- the exact bounded Party-append primitive proven in Phase 1;
- the exact bounded Inventory-insertion primitive proven in Phase 2.

Do not pull the paused Money reusable-envelope candidate into this branch. Canonical FL2 Money behavior may remain available only under its canonical existing gate.

The GUI must label new creation capabilities **Fast Lab experimental** and make unsupported states explicit.

### GUI acceptance

At minimum:

- browser/core unit tests;
- synthetic upload -> inspect -> preview -> verified download tests;
- actual private-source GUI smoke for each newly proven creation operation where safely reproducible without overwriting a live save;
- downloaded bytes must equal the corresponding non-GUI core candidate exactly;
- verifier/independent audit acceptance;
- source immutability;
- localhost bind check;
- no private bytes/logs committed.

A new game round trip solely because the GUI wrapped byte-identical already game-confirmed core output is not required unless a discrepancy appears.

## Branch/publication policy

Use a fresh branch from canonical `main`, for example:

`codex/v022-creation-proofs-gui-20261007`

Push is encouraged after validation, but only push-safe material may enter Git:

- source code;
- tests;
- independent auditor/differential tooling without protected bytes;
- sanitized evidence/design records;
- hashes, sizes, structural summaries and non-sensitive diff metadata.

Never push ROMs, saves, `.pks`, BPS/IPS, executables, proprietary payloads, copyrighted assets, screenshots/raw memory containing protected bytes, raw private command logs, or private save contents/hexdumps.

Do not mutate canonical `main`.

## Stop / decision rules

Codex should continue autonomously through cheap reversible investigation, bounded implementation, private proof and GUI prototype when the previous phase succeeds.

Stop with `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE` when:

- current private state materially contradicts the assumed exact-v0.22/key/layout boundary;
- Party append requires speculative record synthesis/coupling beyond the exact-copy proof;
- Inventory insertion cannot be isolated from an ordinary game transition without guessing;
- a required operation would overwrite the live save/source;
- protected data would need to enter Git;
- scope would need to expand materially beyond this authorization.

A successful result ends with a pushed exact review branch and:

`READY_FOR_INDEPENDENT_REVIEW`

Final packet must distinguish canonical evidence, reproduced local private-input evidence, prior observations and hypotheses/non-claims.

## Next Human gate

After branch publication, ChatGPT must independently fresh-read canonical `main`, inspect the exact branch diff/evidence, determine whether Party append, Inventory insertion and the GUI prototype are adequately proven, and then propose the next Goal. No canonical merge/adoption occurs without a separate Human authorization.
