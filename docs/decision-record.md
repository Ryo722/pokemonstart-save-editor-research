# Canonical re-evaluation — 2026-10-05

## Authority and evidence discipline

GitHub `main` is the durable canonical authority. Protected binaries remain outside Git. Conclusions must distinguish repository/canonical evidence, independently checked public upstream source, local private-input verification, human observation, prior observations/command logs, and hypotheses.

Do not generalize from a single successful save edit. Unsupported, malformed, ambiguous, or unqualified saves must fail closed.

## Refined North Star

Enable a PokemonStart player to inspect a **positively supported** save, make a small **evidence-proven** party edit into a **separate output file**, independently verify that output, and retain a reliable recovery path.

A GUI is a delivery layer only after save/profile eligibility and field capability are proven. The project is not trying to maximize editable fields or reproduce a generic PKHeX-style editor by default.

## Milestone architecture

1. **M1 — reproducible read audit — COMPLETE.**
   - fail-closed structural verifier;
   - slot/section/signature/checksum validation;
   - counter selection including wrap behavior;
   - section permutation handling;
   - party decoding for the observed 100-byte records;
   - optional 16-byte external footer separated as opaque;
   - sectors 30/31 reported without mutation.

2. **M2 — exact one-field writer proof — COMPLETE.**
   - exact private input SHA-256 allowlist;
   - `party[0]` HP IV `31 -> 30` only;
   - exactly two changed bytes: field + logical section 1 checksum;
   - exclusive new-file output and input immutability;
   - human game load + normal-save round trip PASS.

3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.**
   - structural compatibility is not PokemonStart build identity;
   - writer support is layered: structural eligibility + provenance/profile eligibility + field capability eligibility;
   - sectors 30/31 are CFRU-JP game-managed expanded save data;
   - logical sections 0/4/13 contain game-managed parasite data in checksum-uncovered tails;
   - active-slot/counter parity is part of actual game-load behavior;
   - physical section permutation must be preserved;
   - party-field transactions preserve the complete file outside explicitly proven field/checksum bytes.

4. **M3B — bounded same-field transaction proof — COMPLETE for the exact retained private v0.15 lineage once PR #8 is merged.**
   - exact input SHA-256 `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
   - both slots valid, active slot 0 counter 2, inactive counter 1;
   - `party[0]` HP IV `30 -> 31` only;
   - exact two-byte diff `0x3080 BE->BF` and `0x3FF6 20->21`;
   - exact output SHA-256 `cf2ca33a303b6409300ac4032c7c47efd9859562bc06fe18e89481bb93ea5f1f`;
   - source-backed parity preflight, complete byte-diff confinement, output re-verification, new-file-only semantics;
   - human game round trip PASS: returned resave has slot 0 counter 2, slot 1 counter 3 active, parity PASS, HP IV 31 retained, old slot 0 byte-for-byte preserved, sectors 28–31 byte-for-byte preserved, and checked unrelated party values stable.

5. **M3C — field-by-field expansion — NOT AUTHORIZED.**
   - each new field or tightly coupled field group requires its own semantic/coupling analysis, bounded encoder, expected-diff contract, checksum analysis, invariant checks, and game round trip before being called safe.

6. **M4 — usable editor / GUI — NOT AUTHORIZED.**
   - expose only proven fields and qualified save profiles;
   - read-only preview, fail-closed validation, separate output path, explicit recovery path.

Detailed M3A support-envelope evidence is in `docs/m3a-support-envelope-findings.md`. Detailed M3B evidence is in `docs/m3b-proof-candidate.md`.

## Current position

On canonical `main` before PR #8 merge: **M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; M3B candidate evidence PASS but not yet canonicalized.**

If PR #8 is explicitly authorized and merged, the canonical position becomes: **M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; M3B COMPLETE; stopped at the M3C authorization boundary.**

## What M3B actually proves

M3B does **not** prove a general writer or arbitrary-save support. It validates the M3A transaction envelope on a second bounded save-state condition while keeping the field family fixed:

- the input hash differs from the original M2 proof input;
- both save slots are valid;
- the active physical slot is the opposite slot from M2;
- the writer discovers the target logical section through metadata rather than fixed physical location;
- the tool changes only the proven field/checksum bytes and preserves all other bytes;
- the actual game accepts that output and carries the edited HP-IV value into the next normal-save slot.

This materially reduces uncertainty around slot/counter state, section permutation, and the reusable transaction envelope. It does not expand the supported provenance profile beyond the retained private v0.15 lineage.

## Supported-save / writer-support boundary

A future writer-supported save must pass all applicable layers:

### S0 — structural eligibility

- file size `0x20000` or `0x20010`;
- fail-closed slot/section/signature/checksum validation;
- one unique active slot;
- internally consistent active counter;
- active slot index equals `counter % 2`;
- target capability's required party layout decodes successfully;
- existing physical section order is preserved.

### P0 — provenance/profile eligibility

Current bounded write evidence is only for the retained private PokemonStart v0.15 lineage. Structural similarity alone does not establish title/build identity. Arbitrary external saves and other builds remain unsupported.

A stronger future user-facing profile mechanism should prefer independently verified local build/ROM identity rather than infer build identity from save structure.

### C(field) — capability eligibility

Every editable field or tightly coupled field group requires its own proof. M2/M3B establish only the HP-IV field family under the exact bounded proof conditions above.

## Reusable transaction contract retained

Future bounded writers must:

- hash/read input before mutation;
- reject input/output aliasing and existing output paths;
- run structural + writer-support preflight;
- locate the active logical section through verified metadata;
- require active-slot/counter parity;
- preserve section permutation and section counters/IDs/signatures;
- mutate only explicitly authorized field bytes;
- recompute only checksum(s) whose covered payload changed unless field evidence proves additional coupling;
- require the complete byte diff to be explainable by authorized field/checksum changes;
- preserve every other byte including inactive slot, sectors 28–31, parasite tails, and optional external footer;
- re-verify generated bytes;
- use exclusive new-file creation, verify written bytes, re-hash the original input, and clean up a newly created output on post-write failure when safely possible;
- report exact diff and output hash.

The external 16-byte footer is preservation-only for tool output; equality is not required after a later game/emulator resave.

## M3B boundary check / next-step posture

M3B produced no evidence that invalidates the refined North Star or the M3A transaction contract. It instead confirms that the transaction envelope works across the intended second bounded slot state.

Therefore no roadmap redesign is currently justified. The nominal next milestone remains **M3C field-by-field expansion**, but it must not start merely because the roadmap names it. Before authorization, select the cheapest new field or tightly coupled field group whose proof materially advances the user outcome and does not introduce unresolved coupling that is cheaper to investigate first.

Broad arbitrary-save/profile generalization remains a separate future qualification problem and is not automatically inserted ahead of every field proof.

## Remaining risks and unresolved uncertainties

- PokemonStart version/build mismatch outside the retained private lineage;
- no positive build identity derived from save structure alone;
- arbitrary external/non-lineage save support;
- field coupling outside HP IV;
- expanded IDs and other game-specific field semantics;
- interrupted-save behavior outside the external new-file transaction model;
- application-level semantics/integrity of sectors 30/31 and parasite tails beyond byte preservation;
- exact distribution/package provenance gaps and independently reproduced target-build identity;
- GUI readiness remains unproven until useful editable fields and profile support exist.

## Authorization boundary

The human authorization on 2026-10-05 covered the bounded M3B same-field proof: implementation, exact private candidate derivation/sealing, one new private proof output, human round-trip preparation, and read-only verification of the returned resave.

It does **not** authorize:

- PR #8 merge unless separately authorized;
- M3C/new editable fields;
- non-lineage or arbitrary save writing;
- general writer capability expansion;
- save overwrite behavior;
- GUI work;
- box editing;
- protected-data publication;
- executing Defender-blocked executables;
- ROM / `.sav` / `.pks` / patches / executables / proprietary payload uploads.

The immediate human gate is **PR #8 merge authorization**. After merge, M3C remains a separate authorization boundary.
