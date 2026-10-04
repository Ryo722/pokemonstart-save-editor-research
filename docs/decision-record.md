# Canonical re-evaluation — 2026-10-04

## Evidence hierarchy and current state

GitHub `main` is the durable canonical source. Protected binaries remain outside Git. Current conclusions distinguish repository evidence, independently checked public CFRU-JP source, local private-input verification, human observation, and older observations.

M1 / Gate 1 is complete. The merged read-only verifier has no write path, its synthetic tests pass, and the supplied private original/test/resave set reproduced the expected slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without changing the input files.

M2 / Gate 2 is also complete for one exact allowlisted proof transformation. PR #4 merged the bounded repository writer after its repository-generated HP-IV-30 output completed a fresh human game load + normal-save round trip and the resulting private resave independently passed structural verification.

The M2 writer remains deliberately narrow: it accepts only the known before-test save SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`, changes only party slot 0 HP IV 31 -> 30, refuses input overwrite and pre-existing output paths, requires the complete diff to be exactly `0x10080 BF->BE` plus `0x10FF6 62->61`, and requires output SHA-256 `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`.

The fresh round-trip resave has SHA-256 `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`. Both slots validate, slot 0 counter 2 is uniquely newest, both slots retain HP IV 30 and the checked unrelated party values, sector 30/31 remain preserved, and the old slot 1 remains byte-identical to the repository-generated proof output. The 16-byte emulator footer remains opaque and is not assigned semantics.

## Final goal

Enable a PokemonStart player to inspect and make a small, explicitly chosen party edit to their own save, verify it, and recover the original if anything fails. A Windows GUI is a delivery option only after the file format and individual field writes have evidence. Proven field safety determines UI scope, not the reverse.

## Minimal roadmap and gates

1. **Reproducible read audit — COMPLETE.** Original read-only verifier merged; synthetic malformed/ambiguous cases fail closed; private original, test, and normal-resave inputs reproduce slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without modifying inputs.
2. **One-field writer proof — COMPLETE.** Repository implementation reproduces the exact HP IV 31→30 two-byte proof on the known private input, writes only to a new path, and the repository-generated output completed a fresh human game load + normal-save round trip. The resulting resave passes structural verification and preserves HP IV 30 plus the required unrelated invariants.
3. **Field-by-field expansion — NOT AUTHORIZED TO BEGIN.** Any next field must be independently selected and scoped from current evidence. Each field or tightly coupled field group requires a separate reversible proof with explicit expected diff, checksum/coupling analysis, invariant checks, and game round trip before it can be treated as safe.
4. **Usable editor — NOT AUTHORIZED.** Add a Windows interface only for fields already proven in prior gates, with read-only preview, validation, separate output path, and recovery instructions.

Current canonical position: **M1 COMPLETE; M2 COMPLETE; stopped before M3 implementation authorization.**

## Fresh roadmap re-evaluation

The M2 round trip removed the last material uncertainty inside the bounded one-field proof: the exact repository-generated file survived a real game load and normal-save cycle, and the resulting save independently verified with the expected slot transition and party invariants.

This evidence does not justify changing the North Star or skipping field-by-field proof. One successful allowlisted HP-IV write is not evidence for arbitrary IVs, EVs, moves, species, level/EXP, held items, box data, other PokemonStart builds, or a reusable general writer.

The roadmap therefore remains appropriate. The cheapest next uncertainty reducer is to choose the next candidate field or tightly coupled field group based on source-backed layout/coupling evidence, then design the smallest reversible proof. That selection itself is an M3 scope decision and is not authorized by the M2 merge authorization.

## M2 design decision

The proven M2 writer is intentionally narrower than a reusable writer library:

- input is allowlisted by exact SHA-256;
- only party record 0 is targeted;
- only HP IV 31 -> 30 is accepted;
- the active slot and logical section 1 are discovered through the M1 verifier rather than assumed from physical position;
- section 1 checksum is recalculated after the one field change;
- the complete output diff and output SHA-256 are fixed expectations;
- footer, sectors 30/31, party count, active slot, and all non-HP IVs are invariant checks;
- output is created with exclusive new-file semantics and any post-write verification failure removes the newly created output;
- the input is re-hashed after writing and must remain unchanged.

This design is intentionally non-general. Its value is evidence: unexpected behavior becomes a hard failure rather than an inferred save edit. The trade-off is that it cannot edit any other save or even the same save after a normal game resave. That is acceptable for M2 because M2 is a proof milestone, not a user-facing editor.

## Remaining risks and unresolved uncertainties

Known technical risks remain: PokemonStart version/build mismatch; inability to prove title identity from structural save layout alone; future variants with different signatures/layouts; emulator-footer semantics beyond opaque preservation; field coupling; expanded IDs; checksum/write ordering; interrupted-save behavior; exact PokemonStart/CFRU-JP integration revision; and the fact that one successful HP-IV proof cannot establish safety for other fields.

Broader provenance gaps also remain outside M2: exact distribution URL/package hash, complete extraction transcript, and version/build generalization. None of these gaps should be silently inferred closed from the successful M2 proof.

## Authorization boundary

The authorization used here covers merging the exact M2 bounded candidate and canonicalizing M2 completion. It does **not** authorize M3 implementation, generalizing the writer to other hashes, adding editable fields, overwriting saves, GUI work, box editing, protected-data publication, executing Defender-blocked executables, or broadening distribution scope.

The next meaningful human authorization gate is therefore an **M3 field-by-field expansion scope decision** based on fresh canonical evidence. Until that decision is explicitly authorized, no additional write capability should be implemented.
