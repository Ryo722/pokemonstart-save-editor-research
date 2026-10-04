# Canonical re-evaluation — 2026-10-05

## Evidence hierarchy and current state

GitHub `main` is the durable canonical source. Protected binaries remain outside Git. Current conclusions distinguish repository evidence, independently checked public CFRU-JP source, local private-input verification, human observation, older observations, and hypotheses.

M1 / Gate 1 is complete. The merged read-only verifier has no write path, its synthetic tests cover malformed/ambiguous cases, and the retained private original/test/resave set reproduced the expected slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without changing the input files.

M2 / Gate 2 is complete for one exact allowlisted proof transformation. The bounded repository writer accepts only the known before-test save SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`, changes only party slot 0 HP IV 31 -> 30, refuses input overwrite and pre-existing output paths, requires the complete diff to be exactly `0x10080 BF->BE` plus `0x10FF6 62->61`, and requires output SHA-256 `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`.

The repository-generated proof output completed a fresh human game load + normal-save round trip. The resulting private resave independently passed structural verification with both slots valid, slot 0 counter 2 uniquely newest, HP IV 30 retained, checked unrelated party values stable, sectors 30/31 preserved, and the prior slot retained byte-for-byte. The 16-byte emulator footer remains opaque and is not assigned semantics.

## Refined North Star

Enable a PokemonStart player to inspect a **positively supported** save, make a small **evidence-proven** party edit into a **separate output file**, independently verify that output, and retain a reliable recovery path. Malformed, ambiguous, or unsupported saves must fail closed rather than be guessed about.

A Windows GUI is a delivery option only after the save/profile boundary and individual field writes have evidence. Proven field safety and proven save support determine UI scope, not the reverse.

This is a bounded refinement of the prior goal, not a scope expansion: compatibility/support evidence is made explicit as part of the safety outcome already required by the project.

## Milestone architecture

1. **M1 — reproducible read audit — COMPLETE.** Original read-only verifier merged; synthetic malformed/ambiguous cases fail closed; retained private v0.15 original, test, and normal-resave inputs reproduce slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without modifying inputs.

2. **M2 — exact one-field writer proof — COMPLETE.** Repository implementation reproduces the exact HP IV 31->30 two-byte proof on the known private input, writes only to a new path, and the repository-generated output completed a fresh human game load + normal-save round trip. The resulting resave passes structural verification and preserves HP IV 30 plus required unrelated invariants.

3. **M3A — supported-save / reusable write-envelope characterization — AUTHORIZED.** This is a one-time cross-cutting, read-only evidence/design gate. It must establish the smallest evidence-backed supported-save/profile predicate and reusable transaction/invariant contract before reusable writing or further field expansion. It does not authorize a non-allowlisted writer, a new editable field, or save mutation.

4. **M3B — same-field reusable transaction proof — NOT YET AUTHORIZED.** If M3A supports proceeding, keep the semantic field fixed (candidate: HP IV) while varying only the save-state/writer-generalization dimension. This avoids changing field coupling and writer generalization simultaneously.

5. **M3C — field-by-field expansion — NOT YET AUTHORIZED.** Each new field or tightly coupled field group requires a separate reversible proof with explicit expected diff, checksum/coupling analysis, invariant checks, and game round trip before it can be treated as safe.

6. **M4 — usable editor — NOT AUTHORIZED.** Add a Windows interface only for fields and supported save profiles already proven in prior gates, with read-only preview, validation, separate output path, and recovery instructions.

The detailed M3A questions, success criteria, and authorization boundary are recorded in `docs/m3a-support-envelope-plan.md`.

Current canonical position after this authorized roadmap refinement: **M1 COMPLETE; M2 COMPLETE; M3A AUTHORIZED; M3B/M3C/M4 NOT AUTHORIZED.**

## 2026-10-05 milestone-boundary audit decision

The M2 result validates the original M1 -> M2 ordering. The exact repository-generated writer output survived a real game load and normal-save cycle, and the resulting save independently verified with the expected slot transition and party invariants.

However, M2 also exposes a cross-cutting gap that should be closed before repeatedly proving new fields. The M2 proof deliberately fixes the exact input hash, starting value, physical changed bytes, checksum byte, and output hash. This is excellent proof isolation, but repeating that exact-hash pattern across many fields would increase field evidence while leaving the reusable user-save support boundary and common transaction semantics unresolved.

Therefore the roadmap is **REFINED, not redesigned**. Field-by-field proof remains required, but a one-time M3A support-envelope gate is inserted before reusable writing or additional field expansion. The intent is specifically to avoid multiplying process: M3A is a single cross-cutting gate whose results should be reused by M3B/M3C rather than repeated for every field.

## M3A questions that must be closed

M3A must answer, from current canonical/private/source evidence without new save mutation:

- what conditions beyond exact SHA-256 can safely identify a save/profile as supported;
- whether save bytes can positively identify the relevant PokemonStart version/build, and if not what external provenance/profile evidence is required;
- the reusable mutation envelope and invariant regions;
- handling rules for one-valid/one-erased and both-valid slot states, counter wrap, section permutation, and ambiguous counters;
- checksum recomputation rules;
- preservation/rejection rules for inactive slot, sectors 28-31, and the optional opaque 16-byte emulator/RTC footer;
- new-output/input-immutability/post-write-verification/failure-cleanup semantics;
- a fail-closed matrix for malformed, ambiguous, unknown-profile, unsupported-layout, unexpected-coupling, and unexpected-diff cases.

M3A completion does not require a reusable writer implementation. It requires an evidence-backed support/profile boundary, a reusable transaction/invariant contract, an explicit blocker list if M3B cannot proceed, and a fresh decision on whether M3B is the cheapest safe next proof.

## M2 design decision retained

The proven M2 writer remains intentionally narrower than a reusable writer library:

- input is allowlisted by exact SHA-256;
- only party record 0 is targeted;
- only HP IV 31 -> 30 is accepted;
- the active slot and logical section 1 are discovered through the M1 verifier rather than assumed from physical position;
- section 1 checksum is recalculated after the one field change;
- the complete output diff and output SHA-256 are fixed expectations;
- footer, sectors 30/31, party count, active slot, and all non-HP IVs are invariant checks;
- output is created with exclusive new-file semantics and any post-write verification failure removes the newly created output when safely possible;
- the input is re-hashed after writing and must remain unchanged.

This design is intentionally non-general. Its value is evidence: unexpected behavior becomes a hard failure rather than an inferred save edit.

## Remaining risks and unresolved uncertainties

Known technical risks remain: PokemonStart version/build mismatch; inability to prove title identity from structural save layout alone unless new evidence closes that gap; future variants with different signatures/layouts; emulator-footer semantics beyond opaque preservation/reporting; field coupling; expanded IDs; checksum/write ordering; interrupted-save behavior; exact PokemonStart/CFRU-JP integration revision; both-valid-slot writer input behavior; non-allowlisted save support; and the fact that one successful HP-IV proof cannot establish safety for other fields.

Broader provenance gaps remain: exact distribution URL/package hash, complete extraction transcript, and version/build generalization. None of these gaps should be silently inferred closed from the successful M2 proof.

## Authorization boundary

The human authorization on 2026-10-05 covers:

- canonicalizing this bounded roadmap refinement;
- M3A public/source research;
- read-only repository/private-evidence analysis;
- synthetic/read-only design or test work that does not create new writer capability;
- canonical documentation of M3A evidence and conclusions.

It does **not** authorize:

- non-allowlisted save writing;
- a reusable/general writer implementation;
- another editable field;
- save overwrite behavior;
- GUI work;
- box editing;
- protected-data publication;
- executing Defender-blocked executables;
- ROM / `.sav` / `.pks` / patches / executables / proprietary payload uploads.

M3B or M3C capability expansion requires a later explicit human authorization after M3A evidence is reviewed.
