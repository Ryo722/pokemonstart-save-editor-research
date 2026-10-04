# Canonical re-evaluation — 2026-10-04

## Evidence hierarchy and current state

GitHub `main` is the durable canonical source. Protected binaries remain outside Git. Current conclusions distinguish repository evidence, independently checked public CFRU-JP source, local private-input verification, and older observations.

The M1 read-only verifier was merged through PR #1. The verifier is original repository code, has no write path, and its synthetic unit tests pass 12/12. Public CFRU-JP source independently fixes the section footer offsets, section-specific checksum lengths, counter behavior, SaveBlock1 party offsets, and 100-byte party record layout used by the verifier.

The remaining M1 private-input gap has now been closed using privately supplied files kept outside Git. The before-test save and original backup are byte-identical at SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`; both have slot 0 erased, slot 1 valid at counter 1, and HP IV 31. The normal in-game resave has SHA-256 `c8e086f925b1187639eda7df3bbdb99f4c4e1817f6198a81f44c77db3d5f3cdd`, both slots valid, slot 0 counter 2 selected as newest, and HP IV 30. All checked files preserve the expected party data, a 16-byte opaque footer, sector 30 with 23 nonzero bytes, and sector 31 with zero nonzero bytes. Read-only inspection did not change the input hashes.

## Final goal

Enable a PokemonStart player to inspect and make a small, explicitly chosen party edit to their own save, verify it, and recover the original if anything fails. A Windows GUI is a delivery option after the file format and individual field writes have evidence. The current proof supports continuing toward that goal, but does not justify treating untested fields as safe.

## Minimal roadmap and gates

1. **Reproducible read audit — COMPLETE.** Original read-only verifier merged; synthetic malformed/ambiguous cases fail closed; private original, test, and normal-resave inputs reproduce slot selection, section validation, party decoding, footer separation, and sectors 30/31 diagnostics without modifying inputs.
2. **One-field writer proof — NOT AUTHORIZED TO BEGIN.** If separately authorized, implement output-to-new-file only, with backup guidance and structural validation. Reproduce HP IV 31→30 on a private copy and require an allowlisted two-byte diff, checksum update, footer/unrelated-sector preservation, and successful load/resave. Gate: repeatable diff and in-game round trip using the repository implementation, not only the earlier manual proof.
3. **Field-by-field expansion.** Test each additional field on a separate reversible fixture, including derived-stat, EXP, ID-table, and UI constraints. Gate: explicit expected diff, invariant checks, and game round trip for each field or field group.
4. **Usable editor.** Add a Windows interface only for proven fields, with read-only preview, validation, separate output path, and recovery instructions. Gate: end-to-end user test on supported save variants and clear rejection of unsupported inputs.

Current position: **M1 / Gate 1 COMPLETE; stopped before M2 implementation authorization.**

## Fresh roadmap re-evaluation

The newly reproduced private-input evidence closes M1 but does not justify changing the North Star or skipping the writer proof. The existing sequence remains the cheapest and safest path: prove one bounded write with strict byte-diff and round-trip invariants before expanding fields or building a GUI.

The evidence does reduce uncertainty materially: the verifier now reproduces both the pre-edit state and the normal in-game resave, including the expected slot transition from one valid slot at counter 1 to two valid slots with counter 2 newest, while preserving the observed HP-IV change. That is enough to exit the read-only milestone. It is not enough to generalize to other PokemonStart builds or other editable fields.

## Adjustment to prior plan

The earlier GUI-first idea remains rejected. Proven field safety determines UI scope, not the reverse. M1 completion changes only the project position: the project may now consider a bounded M2 one-field writer proof if explicitly authorized.

## Authorization and risks

The authorization used for this closure covers recording the private-input verification results and declaring M1 Gate 1 complete. It does **not** authorize M2 writer implementation, save overwrites, GUI work, additional editable fields, box editing, protected-data publication, executing Defender-blocked executables, or broadening distribution scope.

Known technical risks remain: PokemonStart version/build mismatch; inability to prove title identity from structural save layout alone; future variants with different signatures/layouts; emulator-footer semantics beyond opaque preservation; field coupling; expanded IDs; checksum/write ordering; slot/counter behavior during interrupted saves; and the fact that a successful one-field historical round trip is not general writer safety evidence.

The next meaningful human authorization gate is therefore: **authorize or decline M2 — the bounded one-field HP-IV writer proof**. Until that authorization, the project remains read-only.
