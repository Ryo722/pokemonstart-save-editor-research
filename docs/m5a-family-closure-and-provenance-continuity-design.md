# M5A FAMILY closure and provenance-continuity design — 2026-10-06

This record closes the bounded Money FAMILY lifecycle-test gap and presents a design-only decision surface for practical retained-lineage provenance continuity. It does **not** implement a broader provenance rule, expose money through the GUI, mark M5A complete, or authorize M5B/M5C.

## Human authorization

> `AUTHORIZE M5A FAMILY CLOSURE AND PROVENANCE-CONTINUITY DESIGN: from fresh current main, close the bounded Money FAMILY candidate evidence gaps without broadening writer capability by adding and executing end-to-end synthetic lifecycle coverage for bootstrap -> preview -> commit -> Human-observed game-return enrollment -> returned-save eligibility -> next preview/commit, plus negative journal/parent/duplicate/environment cases; fresh-run the full repository suite on the exact candidate and correct canonical environment wording so macos-mgba-0.10.5 is not overstated as machine-attested where it is only human-bound. In parallel, perform a design-only, evidence-first investigation of a practical retained-lineage provenance-continuity model that separates save ancestry from ordinary gameplay payload changes, using pinned CFRU-JP save-slot/counter/write behavior and independently reproduced round-trip evidence. Do not implement a broader provenance predicate, do not expose money through GUI, do not mark M5A COMPLETE, and do not begin M5B/M5C until the resulting decision surface is reviewed and separately authorized.`

Fresh canonical `main` at task start was `d32f30916fa623fdc6156a24b450ebe648c50b8b`.

## FAMILY closure evidence

A new synthetic lifecycle test module was added:

- `tests/test_m5a_money_family_lifecycle.py`

It covers the complete intended candidate lifecycle:

1. bootstrap a root journal;
2. inspect and preview an eligible root;
3. commit one bounded money edit to a separate output;
4. construct and enroll a Human-observed normal-save return;
5. verify the returned save becomes journal-eligible;
6. preview and commit a second bounded money edit from that returned save.

It also independently covers the requested negative surfaces:

- Human-observation flag required for return enrollment;
- wrong/non-editor parent rejection;
- duplicate game-return rejection;
- wrong environment rejection;
- journal environment tamper rejection;
- journal fingerprint tamper rejection.

No Money FAMILY writer implementation was broadened by this task.

### Fresh full-suite execution

A temporary branch-only GitHub Actions workflow was created solely to execute the repository suite because the chat container could not resolve `github.com` for a normal clone. The workflow was not retained for canonical integration.

First run on `5adc3cb2e40efe78009777f35e6c3da6ee03cad9` found one failure in the newly added test: the test incorrectly expected an exception for a tampered node fingerprint, while the implementation intentionally returns `eligible=False` with reason `journal fingerprint mismatch`. This was a test expectation error, not a writer/provenance bypass. The test was corrected without changing the Money FAMILY implementation.

The corrected executable/test candidate was exact commit:

- `3209f3aadb3b4dacbfab146dddbb27925895ac63`

Fresh GitHub Actions execution used Python 3.12 on Ubuntu 24.04 and ran:

```text
python3 -m unittest discover -s tests -v
```

Result:

- **119 tests OK**
- **28 skipped**
- **0 failures / 0 errors**

The skips are host-specific macOS/Windows validation paths already explicitly guarded by their existing tests. The new lifecycle tests all passed.

The temporary workflow was then removed. The tested executable/test tree remains the same apart from removal of that workflow and later documentation-only commits.

Evidence label: **fresh CI execution on exact bounded code/test candidate**.

## Environment-binding wording correction

`macos-mgba-0.10.5` is an **M5A human-attested environment binding label**, not a machine attestation of the emulator binary or its version.

The current code machine-checks:

- exact expected ROM/build SHA-256;
- exact environment-label string equality;
- actual `sys.platform == "darwin"` before Money FAMILY publication;
- all normal S0/journal/capability conditions.

The current code does **not** inspect the installed mGBA executable, hash it, query its version, or otherwise prove that mGBA 0.10.5 is the running emulator. The `mGBA 0.10.5` part of the label therefore derives from Human-observed environment evidence from the two successful game round trips.

Canonical language should describe the boundary as **human-attested macOS + mGBA 0.10.5, bound in code by an exact environment identifier and actual macOS publication gate**, not as machine-verified emulator-version identity.

## Provenance-continuity investigation — source evidence

Pinned CFRU-JP source remains commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`.

### Full normal-save write behavior

`src/save.c` shows that a full save (`SaveWriteToFlash(0xFFFF, ...)`) does the following before writing all 14 logical chunks:

1. preserves the current first-sector/counter in backup globals;
2. increments `gFirstSaveSector` by one modulo 14;
3. increments `gSaveCounter` by one;
4. writes every logical chunk through `HandleWriteSector`;
5. `HandleWriteSector` chooses the physical slot from `gSaveCounter % 2` and the rotated first-sector position;
6. sectors 30/31 are separately saved after the 14 chunks.

`GetSaveValidStatus` later chooses the newest valid slot by counter, including the special `0xFFFFFFFF -> 0` wrap rule.

This source model matches the independently reproduced private money round trips:

- first: active slot/counter `1/1 -> 0/2` with previous slot preserved;
- second: active slot/counter `0/2 -> 1/3` with previous slot preserved;
- exact one-position section rotation in both.

### Stable player identity available for corroboration

Pinned `include/global.h` places in SaveBlock2:

- player name at `0x000..`;
- gender at `0x008`;
- trainer ID at `0x00A..0x00D`.

These fields can corroborate a claimed continuation, but source layout alone does not make them cryptographic provenance. A copied or independently produced save could reproduce them.

## What the bytes can prove

### Class P-exact — already journaled exact node

This is the strongest current class: the entire save hash/fingerprint is already present in the private journal and bound to the exact build/environment label.

### Class P-direct — one full normal save from a journaled parent

A **single** full normal save from a known parent can be strongly evidenced without requiring gameplay payload equality when all of the following hold:

- candidate S0 is valid;
- opposite slot becomes active;
- counter is exactly parent + 1 with the adopted wrap rule;
- expected one-position section rotation occurs;
- the prior active slot is preserved byte-for-byte as the parent active slot;
- exact build binding remains satisfied;
- the Human attests that the exact parent was loaded and this candidate came from a normal in-game save.

The byte-identical previous slot is the important ancestry witness. Ordinary gameplay is allowed to change the newly written active payload; those gameplay changes do not need to be mistaken for editor-authorized diffs.

This is materially different from the current M5A canary-oriented `check_game_return`, which additionally requires money/party/stable-payload equality because it was designed to prove a very narrow immediate post-edit round trip.

### Multi-save gap — structural ancestry witness expires

The two-slot layout creates a hard limit. After another full normal save, the slot containing the original editor output may be overwritten. After two or more unobserved full saves, the current `.sav` bytes generally cannot prove exact ancestry back to the older editor output by byte identity alone.

Therefore a long-gap ordinary-play continuation cannot honestly be called cryptographically or structurally proven from the final save alone.

## Proposed design classes — NOT IMPLEMENTED

### P-direct structural continuation

Recommended for exactly one observed full normal-save step from a journaled node.

Proposed acceptance evidence:

- exact parent node in journal;
- S0-valid candidate;
- previous-slot byte identity to parent active slot;
- exact +1 counter and opposite-slot transition;
- expected section rotation;
- exact ROM/build binding;
- Human normal-save attestation;
- record the new full candidate fingerprint as a `game-direct` edge.

Under this class, arbitrary legitimate gameplay payload changes in the newly active slot would not break ancestry because ancestry is established by the preserved previous slot, not by payload equality.

### P-reanchor human-attested continuation

Recommended only when more than one ordinary full save may have occurred and the direct parent slot is no longer present.

A possible manual re-anchor gate would require at minimum:

- explicit Human statement that the candidate is the continuation of the retained private lineage;
- exact ROM/build SHA binding;
- S0-valid save;
- observed encryption-key boundary required by the Money capability;
- same stable player-identity tuple (player name / gender / trainer ID) as corroborating evidence;
- a counter relationship consistent with forward normal saving where it can be evaluated safely;
- explicit display that this is **Human-attested re-anchoring**, not structural proof;
- never automatic enrollment from structural similarity alone.

This class is weaker than P-direct. Player identity and counters are corroborative, not unforgeable. A structurally valid save with copied identity fields could satisfy them. The Human attestation is therefore an explicit part of authority, not an implementation detail to hide.

## Rejected design

Do **not** automatically admit an unknown save merely because it has:

- valid checksums/section structure;
- the expected ROM/build selected;
- matching trainer identity;
- a plausible newer counter;
- key `0`.

Those conditions establish compatibility and plausibility, not ancestry.

Likewise, do not broaden the existing M4 `check_game_transition` or M5A canary continuation mask to ignore arbitrary gameplay changes. That would conflate ancestry proof with payload volatility and would weaken unrelated capability evidence.

## Decision surface

### Option A — keep current strict canary-style continuation only

**Benefit:** strongest byte-level invariants; minimal authority change.

**Cost:** impractical for an actual editor because ordinary gameplay that changes money, items, party, events, or other state prevents the next save from being enrolled.

### Option B — adopt two-tier provenance continuity

1. **P-direct:** structural one-save descent using preserved previous-slot identity, exact +1 counter, rotation, S0, build binding, and Human normal-save attestation.
2. **P-reanchor:** explicit Human-attested re-anchor for longer ordinary-play gaps, with S0/build/player-identity/key/counter corroboration and clear weaker-evidence labeling.

**Benefit:** separates save ancestry from gameplay payload semantics and makes the editor usable during normal play while retaining fail-closed behavior.

**Risk/trade-off:** P-reanchor necessarily relies on Human authority because the two-slot file no longer contains an old byte-identical ancestor after enough saves.

**Recommended:** Option B, but only after separate Human authorization and implementation review. P-direct should be implemented first because it has strong source-backed and private-byte evidence. P-reanchor should remain explicit/manual and clearly labeled; it should never be inferred automatically.

### Option C — automatically trust matching identity/counter/build

**Rejected.** It overstates what those fields prove and would silently broaden arbitrary-save support.

## Current boundary after this task

- Money writer capability is unchanged.
- End-to-end FAMILY lifecycle closure is freshly tested.
- Full repository suite is freshly green on the exact bounded code/test candidate.
- `macos-mgba-0.10.5` is explicitly classified as a Human-attested environment label, not machine emulator-version attestation.
- Practical provenance continuity is **design-only**.
- Existing M4 provenance code is unchanged.
- Existing M5A canary-oriented continuation code is unchanged.
- Money GUI exposure is not authorized.
- M5A is not marked COMPLETE.
- M5B/M5C remain not authorized.
