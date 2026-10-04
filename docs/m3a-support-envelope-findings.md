# M3A support-envelope findings — 2026-10-05

## Status

M3A read-only evidence/design work is complete enough to define the next bounded proof. This document does not authorize M3B implementation or save mutation.

## Evidence classes used here

- **independently reproduced / canonical evidence** — current repository state and current public upstream CFRU-JP source read during this M3A work;
- **local private-input verification** — retained facts already recorded in this repository for private PokemonStart saves;
- **human observation** — game load/save observations already recorded canonically;
- **prior observation / command log** — provenance/build hashes not independently re-established here;
- **hypothesis / unverified** — explicitly labeled where used.

## Upstream pin remains current

Fresh read on 2026-10-05 confirms `kapibarasan000/CFRU-JP` `main` is still commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`, the same source revision pinned by M1.

Evidence level: **independently reproduced / upstream source evidence**.

## Finding 1 — structural compatibility is not build identity

The inspected CFRU-JP save code uses default file signature `0x08012025`, but `IsValidFileSignature` can also accept compile-time `CUSTOM_FILE_SIGNATURE_OLD` and `CUSTOM_FILE_SIGNATURE` values. The save structure/signature is therefore a format-level discriminator, not evidence that uniquely identifies a PokemonStart title/build.

No current canonical evidence establishes a save-resident PokemonStart build identifier. A search of the pinned saved structures did not establish a version/build field that can positively identify the distribution. Absence of such a field is not proved universally; the safe conclusion is narrower: **do not infer PokemonStart build identity from structural compatibility alone**.

### Consequence

Writer support must be modeled as separate layers:

1. **Structural eligibility** — machine-checkable save/layout invariants.
2. **Provenance/profile eligibility** — evidence tying the save to a qualified PokemonStart build/profile.
3. **Field capability eligibility** — evidence that the requested field transformation is proven safe.

A save is writer-supported only when all applicable layers pass.

For the next bounded proof, the retained private M2 round-trip lineage can serve as a narrow provenance profile because its origin in the same observed PokemonStart v0.15 environment is already part of canonical evidence. This does **not** generalize support to arbitrary structurally similar saves or arbitrary PokemonStart v0.15 files.

For future broader user-facing support, a stronger build-profile mechanism such as an independently verified local ROM/build hash is preferred. The target-ROM hash currently recorded in the repository is only prior command-log evidence and is not promoted here.

## Finding 2 — sectors 30/31 are source-backed expanded save data

Pinned `src/save.c` defines `LoadSector30And31` and `SaveSector30And31` and explicitly reads/writes flash sectors 30 and 31. These sectors are therefore not merely unexplained trailing/extra sectors: they are part of CFRU-JP's expanded save mechanism.

Their application-level contents remain undecoded in this project. M3A therefore classifies them as:

> **source-backed game-managed expanded save sectors; semantics not decoded; preserve byte-for-byte unless a later field-specific proof explicitly targets them.**

The M2 proof already preserved them, and the fresh game round trip preserved flash sectors 28–31 while changing the external 16-byte footer.

Evidence level: **upstream source evidence + local private-input verification**.

## Finding 3 — section 0/4/13 unchecked tails contain game-managed parasite data

Pinned `src/save.c` uses otherwise-unused tails of logical sections 0, 4, and 13 for `SaveParasite` / `LoadParasite` data:

- section 0 tail begins after checksum-covered length `0xF24`;
- section 4 tail begins after checksum-covered length `0xD98`;
- section 13 tail begins after checksum-covered length `0x450`;
- parasite data extends through the normal `0xFF0` section-data area.

The normal section checksum covers only the section-specific chunk length, so these parasite tails are not protected by that checksum even though the game uses them.

### Consequence

A reusable party-field transaction must preserve the **entire input file byte-for-byte except the explicitly proven field bytes and checksum bytes**, not merely preserve all checksum-covered regions. Output verification can prove preservation of these tails, but cannot infer their semantic correctness from the section checksums.

Evidence level: **upstream source evidence**.

## Finding 4 — slot/counter parity is part of game-load behavior

Pinned `HandleLoadSector` selects the physical 14-sector slot using:

`NUM_SECTORS_PER_SAVE_SLOT * (gSaveCounter % 2)`.

Pinned full-save logic increments `gSaveCounter` before writing the next save and writes sectors into the slot selected by that counter parity. This matches the retained private lineage:

- counter 1 is in physical slot 1;
- the next normal in-game save creates counter 2 in physical slot 0.

Therefore a structurally valid file whose selected newest counter is stored in the opposite physical slot may be interpreted differently by the actual game than by a parser that only compares counters.

### Consequence

For writer eligibility, M3A adds a source-backed **game-load parity invariant**:

> selected active slot index must equal `active_counter % 2`.

The current M1 verifier remains a structural verifier and does not currently encode this as a separate writer-support gate. M3B must explicitly enforce/test the parity rule before any write attempt.

Equal-counter ambiguity, malformed/partially erased slots, duplicate/missing sections, inconsistent counters, and checksum/signature failures remain hard rejections.

Evidence level: **upstream source evidence + local private-input verification**.

## Finding 5 — physical section permutation should be preserved, not normalized

The game load path scans physical sectors and dispatches content by logical section ID; it records the physical location of logical section 0 for later save rotation. M1 already resolves sections by logical ID and does not assume fixed physical order.

M3A finds no reason for an external bounded party writer to normalize/reorder sections. Reordering would create unnecessary bytes and interact with the game's save-rotation state.

### Consequence

A writer must locate the target logical section through verified metadata, edit it in place, and preserve the existing physical permutation exactly.

Evidence level: **upstream source evidence + repository implementation evidence**.

## Finding 6 — external writer should not emulate a normal game save transaction

The normal game performs a broader transaction: it advances the save counter, rotates the first physical section, writes the full save slot, and writes sectors 30/31. M2 did none of these things; it changed the proven field in the currently active slot, updated the affected section checksum, preserved all other bytes, and the game accepted the result.

For the next bounded proof, incrementing counters or constructing a new slot would add unnecessary uncertainty and a substantially larger diff.

### Consequence

The reusable bounded transaction candidate is:

- select the already-valid active slot;
- require game-load parity;
- preserve slot counters, section IDs, signatures, physical order, inactive slot, sectors 28–31, parasite tails, and optional external footer;
- mutate only proven field bytes in the active logical section;
- recompute only checksum(s) whose covered payload changed;
- produce a brand-new output file.

This is a transaction design decision for future proofing, not an authorization to implement it now.

## Finding 7 — sectors 28/29 and the external footer remain preservation-only regions

Pinned source identifies flash sectors 28 and 29 as Hall of Fame sectors and writes them separately for Hall of Fame save paths. The current project has no need to edit them for party-field work.

The optional 16-byte bytes after the `0x20000` flash body are outside the CFRU-JP flash image. Their semantics remain unassigned here. M2 preserved those bytes in the generated output; the emulator/game round trip later changed them independently.

### Consequence

For party-field writing:

- sectors 28/29: preserve entire sectors;
- sectors 30/31: preserve entire sectors;
- 16-byte external footer, if present: preserve exactly in tool-generated output;
- do not require footer equality across a later emulator/game resave.

## Supported-save/profile boundary produced by M3A

### Structural eligibility S0

A candidate save is structurally eligible for a future bounded writer only if all of these pass:

- size is exactly `0x20000` or `0x20010`;
- the 128 KiB flash body satisfies the current fail-closed slot/section/signature/checksum rules;
- one unique active slot is selected;
- active slot counter is internally consistent;
- active slot index equals `counter % 2`;
- party count/record layout required by the target capability decodes successfully;
- physical section order is retained as input state, not normalized.

Passing S0 establishes structural compatibility only. It does not establish PokemonStart build identity.

### Provenance/profile eligibility P0

For M3B, the only currently qualified profile is the **retained private M2 v0.15 lineage** already tied by canonical evidence to the observed game environment.

Arbitrary external saves, other PokemonStart builds, and structurally similar saves without qualified provenance remain unsupported.

### Capability eligibility C(field)

The requested field transformation must have a separate bounded proof contract. At M3A completion, only the exact M2 HP-IV proof exists.

## Reusable transaction/invariant contract produced by M3A

A future bounded writer using this contract must:

1. read and hash the input before mutation;
2. reject input/output path aliasing and pre-existing output paths;
3. run structural verification and writer-support checks before mutation;
4. locate the active logical section through verified metadata, never fixed physical assumptions;
5. require slot/counter game-load parity;
6. preserve the physical section permutation;
7. mutate only the explicitly authorized field bytes;
8. recompute only checksum(s) covering changed bytes unless field-specific evidence proves other coupling;
9. require the complete byte diff to be explainable by the authorized field encoder plus checksum changes;
10. preserve every other byte, including unchecked parasite tails, inactive slot, sectors 28–31, and the optional external footer;
11. preserve all section counters/IDs/signatures for this external-edit transaction;
12. re-run structural and writer-support verification on generated bytes;
13. create a new file exclusively, verify the written bytes, and re-hash the original input;
14. remove the newly created output on post-write failure when safely possible;
15. report the output hash and exact diff for auditability.

A fixed expected output SHA-256 remains useful for a single proof candidate, but is **not** a reusable writer invariant for arbitrary values/inputs.

## Fail-closed matrix

| Condition | M3A disposition |
| --- | --- |
| unsupported file size | reject |
| malformed/partial slot | reject |
| invalid signature/checksum | reject |
| duplicate/missing sections | reject |
| inconsistent counters within slot | reject |
| equal/newest-slot ambiguity | reject |
| selected slot/counter parity mismatch | reject for writer eligibility |
| unknown/unqualified PokemonStart build/profile | reject for writer eligibility |
| unexpected physical reorder requested | reject / preserve existing order |
| unexpected field coupling | reject until field-specific proof |
| unexpected diff outside target/checksum | reject |
| attempted input overwrite | reject |
| existing output path | reject |
| changed inactive slot / sectors 28–31 / parasite tails / footer | reject for party-field proof |

## M3B recommendation

M3A finds that the cheapest next uncertainty reducer is still a same-field transaction proof, but its scope should stay narrower than arbitrary-save support.

Recommended bounded M3B candidate:

- private input: fresh M2 round-trip resave SHA-256 `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
- provenance: retained P0 private v0.15 lineage only;
- starting state: both slots valid; slot 0 counter 2 uniquely newest; party[0] HP IV 30;
- transformation: party[0] HP IV `30 -> 31` in the active slot;
- preserve counter 2, slot selection, physical permutation, inactive slot, all non-target bytes, sectors 28–31, parasite tails, and external footer;
- recompute only the affected logical section 1 checksum;
- derive and freeze the exact candidate diff/output hash before execution;
- generate only a new output path;
- require a later human game load + normal-save round trip before M3B completion.

Why this input is high-value: it simultaneously changes the previously unproven dimensions of **non-M2-input hash**, **both-valid-slot state**, and **opposite active physical slot**, while keeping the semantic field family fixed.

This M3B candidate still does **not** authorize arbitrary structurally compatible saves. Broad build/profile support remains a later qualification problem.

## M3A verdict

**M3A COMPLETE as an evidence/design gate.**

It closes the support-envelope and transaction-design questions sufficiently to define one bounded next proof. It also discovers two material source-backed refinements that must carry forward: sectors 30/31 are game-managed expanded save data, and slot/counter parity must be part of writer eligibility.

M3B implementation/save mutation remains outside the current authorization and requires explicit human approval.
