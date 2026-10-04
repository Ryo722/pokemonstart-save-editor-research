# M3A support-envelope plan — 2026-10-05

## Status

Human-authorized roadmap refinement after the M2 completion boundary audit.

This document records the current milestone plan. It does not expand writer capability by itself.

## Refined North Star

Enable a PokemonStart player to inspect a positively supported save, make a small evidence-proven party edit into a separate output file, independently verify that output, and retain a reliable recovery path. Ambiguous, malformed, or unsupported saves must fail closed rather than be guessed about.

A GUI is a delivery layer only for already-proven capabilities.

## Milestone sequence

1. **M1 — reproducible read audit — COMPLETE.**
   - Structural verifier merged.
   - Synthetic malformed/ambiguous cases fail closed.
   - Retained private v0.15 inputs reproduced the expected slot, section, checksum, party, footer-separation, and sectors 30/31 behavior.

2. **M2 — exact one-field writer proof — COMPLETE.**
   - Exact allowlisted `party[0]` HP IV `31 -> 30` proof only.
   - Exact complete diff and output hash required.
   - Separate-output semantics and input immutability enforced.
   - Repository-generated output completed a fresh human game load + normal-save round trip; the resulting private resave independently verified.

3. **M3A — supported-save / reusable write-envelope characterization — AUTHORIZED.**
   - Read-only evidence/design gate.
   - No new editable field.
   - No non-allowlisted writer implementation.
   - No save mutation.
   - Establish the smallest evidence-backed support predicate and common write transaction invariants required before reusable writing is attempted.

4. **M3B — same-field reusable transaction proof — NOT YET AUTHORIZED.**
   - If M3A supports proceeding, hold the semantic field constant and vary only the writer/save-state generalization dimension.
   - Candidate subject remains HP-IV so field coupling and writer generalization are not changed simultaneously.

5. **M3C — field-by-field expansion — NOT YET AUTHORIZED.**
   - Each new field or tightly coupled field group requires its own reversible proof, expected-diff/coupling analysis, invariant checks, and game round trip before being treated as safe.

6. **M4 — usable editor / GUI delivery — NOT AUTHORIZED.**
   - Only fields and save profiles proven by prior gates may be exposed.
   - Read-only preview, validation, separate output path, and recovery instructions remain required.

## Why M3A exists

M2 intentionally hard-codes an exact input SHA-256, exact starting value, exact physical changed bytes, exact output SHA-256, and one field. This is strong proof evidence but does not establish a reusable user-save boundary.

Repeating the same exact-hash pattern for many new fields would prove field semantics while leaving the common support/transaction boundary unresolved and could create downstream rework. M3A is therefore a one-time cross-cutting gate before further field expansion, not a repeating review layer for every edit.

## M3A research questions / exit criteria

M3A is complete only when current evidence can support explicit answers to all of the following, or explicitly record why a question remains unresolved and blocks M3B:

1. **Supported-save predicate**
   - What conditions beyond exact SHA-256 may safely identify a save as supported?
   - Which conditions are necessary vs merely observed?

2. **Version/build identity boundary**
   - Can save bytes positively identify a supported PokemonStart build?
   - If not, what external provenance/profile evidence is required?

3. **Common mutation envelope**
   - Which bytes/regions may a bounded field writer change?
   - Which regions must be preserved or rejected when uncertain?

4. **Slot/counter handling**
   - one-valid/one-erased input;
   - both-valid input;
   - counter wrap;
   - section permutation;
   - ambiguous/equal counters.

5. **Checksum behavior**
   - Locate the affected logical section from verified structure rather than fixed physical offsets.
   - Recalculate only checksums whose covered payload changed unless field-specific evidence proves additional coupling.

6. **Opaque/reserved regions**
   - inactive slot;
   - sectors 28–31 / Hall of Fame and observed extra sectors;
   - optional 16-byte emulator/RTC footer.

7. **Output transaction semantics**
   - input remains unchanged;
   - output path must be new/nonexistent;
   - full generated output is re-verified before success;
   - unexpected diff or unsupported structure is a hard failure;
   - failed newly-created output is cleaned up when safely possible.

8. **Fail-closed matrix**
   - malformed structure;
   - ambiguous newest slot;
   - unsupported file size/layout;
   - unknown or insufficiently proven profile/build;
   - unexpected field coupling;
   - unexpected output diff or verification change.

## M3A success criteria

M3A does **not** require a reusable writer implementation.

Success requires:

- an evidence-backed supported-save/profile boundary;
- a reusable transaction/invariant contract;
- an explicit list of remaining blockers to M3B, if any;
- a decision on whether M3B is the cheapest safe next proof;
- no silent generalization from the single M2 proof.

## Authorization boundary

Authorized now:

- public/source research;
- read-only repository analysis;
- synthetic/read-only test or design work that does not create new writer capability;
- canonical documentation of M3A evidence and conclusions.

Not authorized by this decision:

- non-allowlisted save writing;
- a reusable/general writer implementation;
- another editable field;
- save overwrite behavior;
- GUI implementation;
- box editing;
- protected data publication;
- ROM / `.sav` / `.pks` / patches / executables / proprietary payload uploads;
- Defender bypass or unsafe executable execution.

M3B or M3C capability expansion requires a later explicit human authorization after M3A evidence is reviewed.
