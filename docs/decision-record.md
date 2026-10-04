# Canonical re-evaluation — 2026-10-05

## Evidence hierarchy and current state

GitHub `main` is the durable canonical source. Protected binaries remain outside Git. Current conclusions distinguish repository evidence, independently checked public CFRU-JP source, local private-input verification, human observation, prior observations/command logs, and hypotheses.

M1 / Gate 1 is complete. The merged read-only verifier has no write path, its synthetic tests cover malformed/ambiguous cases, and retained private original/test/resave inputs reproduced the expected slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without changing the input files.

M2 / Gate 2 is complete for one exact allowlisted proof transformation. The bounded repository writer accepts only the known before-test save SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`, changes only party slot 0 HP IV 31 -> 30, refuses input overwrite and pre-existing output paths, requires the complete diff to be exactly `0x10080 BF->BE` plus `0x10FF6 62->61`, and requires output SHA-256 `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`.

The repository-generated proof output completed a fresh human game load + normal-save round trip. The resulting private resave independently passed structural verification with both slots valid, slot 0 counter 2 uniquely newest, HP IV 30 retained, checked unrelated party values stable, sectors 30/31 preserved, and the prior slot retained byte-for-byte. The optional 16-byte external footer remains opaque and is not assigned semantics.

## Refined North Star

Enable a PokemonStart player to inspect a **positively supported** save, make a small **evidence-proven** party edit into a **separate output file**, independently verify that output, and retain a reliable recovery path. Malformed, ambiguous, or unsupported saves must fail closed rather than be guessed about.

A Windows GUI is a delivery option only after the save/profile boundary and individual field writes have evidence. Proven field safety and proven save support determine UI scope, not the reverse.

## Milestone architecture

1. **M1 — reproducible read audit — COMPLETE.**
2. **M2 — exact one-field writer proof — COMPLETE.**
3. **M3A — supported-save / reusable write-envelope characterization — COMPLETE.** The support/profile boundary and common transaction contract are recorded in `docs/m3a-support-envelope-findings.md`.
4. **M3B — same-field reusable transaction proof — NOT YET AUTHORIZED.** Recommended next proof keeps the semantic field family fixed while testing a different save-state/physical-slot condition inside the already-qualified private v0.15 lineage.
5. **M3C — field-by-field expansion — NOT YET AUTHORIZED.** Each new field or tightly coupled field group requires a separate reversible proof with explicit expected diff, checksum/coupling analysis, invariant checks, and game round trip.
6. **M4 — usable editor — NOT AUTHORIZED.** Expose only proven fields and qualified save profiles, with read-only preview, validation, separate output path, and recovery instructions.

The original M3A plan and authorization boundary are recorded in `docs/m3a-support-envelope-plan.md`.

Current canonical position: **M1 COMPLETE; M2 COMPLETE; M3A COMPLETE; stopped before M3B implementation authorization.**

## 2026-10-05 milestone-boundary audit decision

The M2 result validates the original M1 -> M2 ordering, but M2 also exposed a cross-cutting gap: the proof deliberately fixed the exact input hash, starting value, physical changed bytes, checksum byte, and output hash. Repeating that pattern across many fields would increase field evidence while leaving reusable user-save support and transaction semantics unresolved.

The roadmap was therefore **REFINED, not redesigned**. Field-by-field proof remains required, but the one-time M3A support-envelope gate was inserted before further capability expansion. M3A is not a repeating review layer for each future field.

## M3A completion findings

Fresh upstream verification confirms the pinned CFRU-JP `main` revision remains `e24a16fe39e27ae162faf5b78596d1f3df18489d`.

M3A produced the following cross-cutting conclusions:

- **Structural compatibility is not PokemonStart build identity.** The default save signature/layout is format evidence, not a unique title/build identifier. The source can also accept compile-time custom file signatures. No current canonical evidence establishes a save-resident build identifier. Arbitrary structurally similar saves therefore remain unsupported unless provenance/profile evidence qualifies them.
- **Writer support is layered.** Future support requires structural eligibility + provenance/profile eligibility + field capability eligibility. Passing the structural verifier alone is insufficient.
- **Sectors 30/31 are game-managed expanded save data.** Pinned `src/save.c` explicitly loads and saves them. Their application-level semantics are not decoded here, so party-field writers must preserve them byte-for-byte.
- **Sections 0/4/13 contain game-managed parasite data in checksum-uncovered tails.** A writer must preserve the entire file outside explicitly proven field/checksum bytes rather than treating unchecked tail bytes as disposable padding.
- **Slot/counter parity matters to actual game loading.** The pinned load path chooses the physical slot from `gSaveCounter % 2`; the observed lineage matches counter 1 -> slot 1 and counter 2 -> slot 0. Writer eligibility must therefore require the selected active slot index to equal `active_counter % 2`.
- **Physical section permutation must be preserved.** Locate data through verified logical section IDs; do not normalize/reorder sectors.
- **External editing should not emulate a normal game save.** For the next bounded proof, preserve counters, slot selection, physical order, inactive slot, sectors 28–31, parasite tails, and the external footer; change only the proven field bytes and affected checksum.
- **The 16-byte external footer remains preservation-only.** Preserve it in tool-generated output, but do not require it to remain equal after a later emulator/game resave.

Detailed evidence, support predicates, fail-closed matrix, and transaction invariants are in `docs/m3a-support-envelope-findings.md`.

## Supported-save/profile boundary after M3A

### Structural eligibility S0

A future bounded writer candidate must require at least:

- file size exactly `0x20000` or `0x20010`;
- current fail-closed slot/section/signature/checksum validation;
- one unique active slot;
- internally consistent active counter;
- active slot index equals `counter % 2`;
- successful decoding of the target capability's required party layout;
- preservation of existing physical section order.

S0 proves structure only, not title/build identity.

### Provenance/profile eligibility P0

For the next proof, only the retained private M2 v0.15 lineage is currently qualified. Arbitrary external saves, other PokemonStart builds, and structurally similar files without qualified provenance remain unsupported.

A stronger future user-facing build-profile mechanism should prefer independently verified local build/ROM identity. The target ROM hash currently recorded elsewhere is prior command-log evidence only and is not promoted by M3A.

### Capability eligibility C(field)

Each field transformation needs its own proof. At M3A completion, the only completed write capability remains the exact M2 HP-IV 31 -> 30 transformation.

## Reusable transaction contract after M3A

A future bounded writer using this contract must:

- hash/read the input before mutation;
- reject input/output aliasing and existing output paths;
- run structural and writer-support preflight checks;
- locate the active logical section through verified metadata;
- require slot/counter parity;
- preserve physical section permutation and all section metadata/counters;
- mutate only explicitly authorized field bytes;
- recalculate only checksum(s) whose covered payload changed unless field-specific evidence proves additional coupling;
- require every output byte change to be explained by the authorized field encoder or checksum update;
- preserve every other byte including inactive slot, sectors 28–31, checksum-uncovered parasite tails, and optional external footer;
- re-verify the complete output;
- use exclusive new-file creation, verify written bytes, re-hash the input, and clean up a newly created output on post-write failure when safely possible;
- report exact diff and output hash.

A fixed expected output SHA-256 is useful for a bounded proof candidate but is not a reusable invariant for arbitrary future values/inputs.

## Recommended M3B candidate

The cheapest next uncertainty reducer is a same-field proof against the fresh M2 round-trip resave:

- input SHA-256 `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
- retained P0 private v0.15 lineage only;
- both slots valid, active physical slot 0, counter 2;
- party[0] HP IV starts at 30;
- proposed transformation: HP IV `30 -> 31` in the active slot;
- preserve counters, inactive slot, section order/metadata, all non-target bytes, sectors 28–31, parasite tails, and footer;
- recompute only logical section 1 checksum;
- derive and freeze exact diff/output hash before execution;
- output to a new path only;
- require a human game load + normal-save round trip before M3B completion.

This candidate changes previously unproven save-state dimensions while keeping the field family fixed. It does **not** establish arbitrary-save support.

## M2 design decision retained

The M2 writer remains intentionally non-general and exact-hash bounded. It is evidence, not the future user-facing architecture.

## Remaining risks and unresolved uncertainties

Known risks remain: PokemonStart version/build mismatch outside the retained lineage; no positive build identity from save structure alone; future variants with different signatures/layouts; field coupling; expanded IDs; broader build/profile qualification; interrupted-save behavior; arbitrary non-lineage save support; and unproven fields.

The application-level meaning/integrity of expanded sector 30/31 data and checksum-uncovered parasite tails is not decoded. Current safety derives from byte-for-byte preservation, not semantic validation.

Broader provenance gaps also remain: exact distribution URL/package hash, complete extraction transcript, and independently reproduced target-build identity.

## Authorization boundary

The 2026-10-05 authorization covered the roadmap refinement and M3A read-only research/design/canonical documentation. That work is now complete.

It does **not** authorize:

- M3B writer implementation or save mutation;
- non-lineage/arbitrary save writing;
- another editable field;
- save overwrite behavior;
- GUI work;
- box editing;
- protected-data publication;
- executing Defender-blocked executables;
- ROM / `.sav` / `.pks` / patches / executables / proprietary payload uploads.

The next human gate is explicit authorization of the bounded M3B candidate above. M3C remains a later separate authorization.
