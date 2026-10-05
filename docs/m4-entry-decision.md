# M4 entry decision package — 2026-10-05

## Decision and authority

**Recommendation: a thin, local Tkinter GUI over one reusable, capability-gated
Python core, with a CLI adapter for audit and tests. M4 implementation is not
authorized by this document.** The UI should remain read-only for any input
that has no positively qualified transformation. The first product gate is to
qualify at least one useful transformation on an actually available private
save; otherwise a GUI would only wrap historical proof launchers.

Fresh `git fetch origin main` on 2026-10-05 resolved GitHub `main` to
`d6bebad6b44bcba5fdcdf6102d9317a074db308e`; the clean local `main`
matched. Current [README](../README.md), [decision record](decision-record.md),
[evidence](evidence.md), [M3A findings](m3a-support-envelope-findings.md),
[M3C program](m3c-goal-batch-program.md), [low-coupling batch](m3c-batch-low-coupling.md),
[derived-state canary](m3c-derived-stats-canary.md), and
[exit assessment](m3c-exit-assessment.md) were read against that tree. The
canonical decision is **M1, M2, M3A, M3B, M3C COMPLETE; M4 NOT AUTHORIZED**.
Merged PRs [#9](https://github.com/Ryo722/pokemonstart-save-editor-research/pull/9),
[#10](https://github.com/Ryo722/pokemonstart-save-editor-research/pull/10), and
[#11](https://github.com/Ryo722/pokemonstart-save-editor-research/pull/11)
corroborate the M3C sequence. Open PR #3 is an old M2 proof candidate; it
does not supersede current `main`. There are no other open issues or PRs at
review time.

The supplied private return save was inspected read-only outside Git. Size is
131,088 bytes and SHA-256 is
`ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86`.
The current verifier accepts it: both slots valid, active slot 0/counter 6,
party count 1, friendship 52, marking 1, ball 11, mint 4, HP EV 80, Attack IV
0, HP 22/22, Attack 9, Sp. Attack 10. This rechecks structure and current
values, not eligibility for a new write or another game load. The full
synthetic suite passed locally, 43/43. No CI or Windows execution is claimed.
All five current proof writers were also invoked against these bytes in
memory, without an output path; each rejected the input profile/hash.

## Exact support and capability registry at entry

`PROVEN` below means a particular transformation from a particular exact
private input lineage, backed by the cited game-boundary evidence. It is not a
numeric range, another party index, or any structurally similar save. Current
proof writers use full input SHA-256, semantic baseline, profile checks, and
fixed output seals. Seals for a *proof* may later become regression vectors;
they cannot silently become authority for arbitrary inputs or targets.

| Exact input SHA-256 | Party[0] options actually sealed | Status and limit |
| --- | --- | --- |
| `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b` (M2) | HP IV `31 -> 30` | PROVEN exact M2 input/output |
| `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac` (M3B) | HP IV `30 -> 31` | PROVEN exact M3B input/output |
| `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282` (M3C-F1) | friendship `50 -> 51` | PROVEN exact input/output |
| `6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600` (M3C low-coupling) | friendship `51 -> 52`, markings `0 -> 1`, ball `3 -> 11` (Premier Ball), each alone or **all three** | PROVEN exact input and sealed groups; two-field subsets are not sealed |
| `baf0b88fd357c54e17743601bbfa26b436db467a2fd78cd1d2c598fb714c50fa` (M3C derived state) | mint `0 -> 4` with cached stats; HP EV `0 -> 80` with max/current HP `21/21 -> 22/22`; Attack IV `29 -> 0` with cached Attack; each alone or **all three** | PROVEN exact input and sealed groups; two-field subsets are not sealed |
| `ffd0d9d598c82af23adfe3a8a9ec5c0e9213fe3cddcd62796538c2353ae9ee86` (supplied return save) | **none** | structural read passes; no current writer input/profile or forward transformation seal |

The current code-level registry is dispersed across
[`pokemonstart_hpiv_proof_writer.py`](../pokemonstart_hpiv_proof_writer.py),
[`pokemonstart_hpiv_m3b_proof_writer.py`](../pokemonstart_hpiv_m3b_proof_writer.py),
[`pokemonstart_friendship_m3c_f1_proof_writer.py`](../pokemonstart_friendship_m3c_f1_proof_writer.py),
[`pokemonstart_m3c_batch_writer.py`](../pokemonstart_m3c_batch_writer.py), and
[`pokemonstart_m3c_derived_stats_writer.py`](../pokemonstart_m3c_derived_stats_writer.py).
The shared [`pokemonstart_transaction.py`](../pokemonstart_transaction.py)
contains a transaction envelope, not independent field authority. The
[`pokemonstart_save_verifier.py`](../pokemonstart_save_verifier.py) decodes
additional fields for inspection, but those offsets are structural knowledge.

| Remaining surface | Entry classification | Reason |
| --- | --- | --- |
| Tera type | BLOCKED for writing | byte/read path known; no PokemonStart mutation canary |
| Held item | BLOCKED | target-build catalog plus battle/form interactions unresolved |
| Hyper-training | BLOCKED | effective-IV/cached-stat coupling unproved for that edit |
| EXP/level/HP/stats | BLOCKED | growth, learnset, and HP transition require a coupled proof |
| Moves/PP/PP-Up | BLOCKED | move catalog, legal selection, PP coupling unproved |
| Ability; species/form/identity | BLOCKED | catalog and broader identity/form state unresolved |
| Arbitrary values, other party members, other saves/builds/versions, boxes/bags | UNSUPPORTED | no positive writer eligibility or capability proof |

No M3C field research must reopen before **design** or core interface work.
Before calling M4 a usable editor for the supplied current save, however, one
additional exact, useful forward transformation and representative private
game round trip are necessary. A bounded friendship `52 -> 53` on this input
is a possible low-coupling candidate, **not yet PROVEN or authorized**. Select
it only after source/range review and a concrete user-value check; any other
choice needs the same evidence. More Tera/item/move/identity research is not a
prerequisite to the minimum product.

## Delivery options

| Shape | Usefulness, safety and testability | Portability, dependencies and packaging | Decision |
| --- | --- | --- | --- |
| A. CLI-first editor | Smallest implementation; explicit paths and deterministic audit; ordinary players must type commands and interpret errors | Python stdlib, macOS/Windows source-run; packaging optional | Keep as core adapter and diagnostic path, not the sole player UI |
| B. Minimal local GUI coupled directly to writers | Easy file picking and preview, but duplicates gates in callbacks and makes proof scripts UI-facing | Tkinter is light; coupling makes regression and future changes harder | Reject |
| C. Thin GUI over one transaction/capability core | Clear select/preview/confirm/recovery flow; all gating stays testable below UI | Tkinter plus stdlib core; OS-specific bundle builds when release-ready | **Recommended** once a current edit is qualified |
| D. Guided read-only verifier plus sealed proof launcher | Even smaller; safe if it only lists exact allowed actions | stdlib, no GUI dependency; still cannot edit the supplied return save | Useful interim diagnostic, insufficient M4 completion |

A GUI is justified for the North Star's file selection, before/after preview,
destination choice, and recovery explanation. It does not justify a large
framework or exposing values without capability proof. Python's
[Tkinter documentation](https://docs.python.org/3/library/tkinter.html)
lists macOS and Windows availability; a specific interpreter distribution
must still be checked. PySide6 would add Qt binaries and license/deployment
review for no required widget in this slice ([Qt for Python](https://doc.qt.io/qtforpython-6/),
[deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)).
The first acceptance target is a local source-run GUI on both OSes with a
tested Python/Tk installation. For self-contained distribution, build and
test separate macOS and Windows bundles; [PyInstaller is not a
cross-compiler](https://pyinstaller.org/en/stable/usage.html). Signing and
platform release UX need a later distribution decision. No security bypass or
permanent exclusion is part of this design.

## Trust boundaries and minimum refactor

The UI and CLI may ask the core for an `Inspection` and an immutable
`MutationPlan`; neither may pass raw offsets, values, or writable buffers.
The core alone decides which menu choices exist. Recommended order:

1. **Structural verifier (S0):** keep strict size, section, checksum, unique
   active slot and party decoding; add a writer-specific parity check. A
   structural pass is inspection permission only.
2. **Profile eligibility (P):** look up the *full* input hash in a reviewed
   allowlist, then check slot/counter/parity, physical section mapping,
   party count and record fingerprint, sectors 30/31, footer policy, and
   expected semantic baseline. An unknown full hash yields an empty edit
   menu. The supplied `ffd0...` hash may be a named read-only profile now;
   it gains write eligibility only through a separate proof decision.
3. **Capability registry (C):** each entry binds profile ID and exact input
   hash, party index, exact from/to semantics, permitted combination,
   source/game evidence reference, encoder/semantic validator, allowed byte
   region/checksum rule, and status. Only `PROVEN` entries with complete
   evidence are selectable. `BLOCKED`, `CANARY_READY`, and `UNSUPPORTED`
   never become menu actions. Make combination rules explicit rather than
   forming a Cartesian product of individually proven edits.
4. **Semantic/group validators:** check all starting fields and coupled
   derived state before any mutation; compute and verify the complete desired
   `PartyRecord`. A scalar and a coupled group use the same interface, with
   group-specific logic behind it.
5. **Plan builder:** produce a preview containing source hash, exact selected
   capability, original and target values, predicted changed bytes,
   checksum changes, and preservation invariants. Re-read/re-hash source
   immediately before commit; a stale plan is refused.
6. **Transaction engine:** reuse the proven active logical section lookup,
   patch/checksum envelope and full diff accounting. Preserve counters,
   section order/metadata, inactive slot, sectors 28–31, excluded tails,
   opaque footer, and every unrelated byte.
7. **Complete diff auditor and output verifier:** independently decode the
   generated bytes, require the expected semantic result and *no other*
   party-field changes, recompute all relevant checksums, recheck profile
   invariants and every changed byte, and compare the in-memory candidate
   with bytes read from disk. Keep the audit path separate from patch
   construction; one writer's success flag is insufficient.
8. **Recovery/output policy and adapters:** UI/CLI receive only a verified
   receipt and recovery instructions. They cannot bypass P or C.

The existing `write_new` uses exclusive creation, fsync, readback, source
rehash, and best-effort cleanup on Python exceptions. A process crash during
direct destination writing can still leave a partial destination. Before M4
claims "failed writes leave no partial output", stage a private temporary
file in the destination directory, fsync and verify it, then use an atomic,
no-clobber publication primitive tested on macOS and Windows. If that
primitive is unavailable, refuse publication. Recheck source and destination
identity, including aliases/symlinks, before publication; verify published
bytes and hashes after publication. Do not call an ordinary replacing rename
on a user-selected existing path. The user keeps the original as rollback.

## Player workflow and recovery

1. Select a local `.sav`; open read-only and show SHA-256, structure/profile
   result, party[0] original values, and a plain reason when edits are
   unavailable. Do not infer build support from filename or layout alone.
2. Present only exact choices returned by P+C; never an unrestricted number
   box or an edit on `ffd0...` until separately qualified. Show which values
   will change together (including cached HP/stats).
3. Preview full before/after semantic summary, changed byte/checksum count,
   source/destination paths, and the fact that original is the rollback.
4. User selects a separate, nonexistent private destination outside the
   repository and confirms that it is not the emulator's live save path.
   Reject source aliases and existing destinations. The program cannot
   reliably discover every emulator's live directory, so never auto-install
   into one.
5. Commit only after all gates pass. Show input and output hashes, exact
   diff/checksum audit, independent verification result, and a concise
   recovery instruction: keep the original untouched and restore it manually
   if the generated copy is rejected by the game. Do not claim a game-load
   pass from structural verification alone.

No ROM, `.gba`, `.sav`, `.pks`, BPS/IPS patch, proprietary executable, or
copyrighted game asset enters Git, a PR, a release asset, or a log. During
development private outputs remain outside the repository. No live emulator
save is written automatically.

## M4 acceptance and tests

M4 implementation should not be marked complete until all of these are
demonstrated on macOS **and** Windows for the approved first slice:

1. A real, currently available, positively qualified private input offers at
   least one meaningful `PROVEN` party[0] choice. For the supplied `ffd0...`
   save this requires a new exact proof and private game round trip; historical
   proof options alone do not satisfy this criterion.
2. Select/inspect shows original values and provenance; malformed,
   ambiguous, non-lineage, and unsupported files expose no edit action.
3. Only exact approved from/to transformations and approved groups can be
   selected; unsupported values, pairings, fields and party indices fail
   closed through the core, including direct CLI/API calls.
4. User chooses a new destination; input and pre-existing output remain
   byte-identical. Repository output, aliases, and overwrite are rejected;
   the UI never chooses a live-emulator path automatically and asks the user
   to confirm the selected path is not live. Fault injection shows no
   published partial save.
5. Independent output audit proves complete semantic before/after state,
   every changed byte and checksum, preserved regions, source/output hashes,
   and source immutability. A deliberate unexplained diff fails.
6. The local UI displays the verified receipt and original-file recovery
   path. It does not report "game compatible" until a representative actual
   game load and normal-save return has passed for that exact new capability.
7. The stdlib core/CLI tests and thin UI integration tests pass on both OSes;
   a private-copy canary and read-only return audit pass without committing
   private data. Bundled builds, if distributed, must be produced/tested on
   their respective OSes and contain no protected artifacts.

Test the layers at their real boundaries: synthetic malformed/slot/parity
profiles; exact allowlist and semantic/group matrices; changed-byte property
checks; existing-output, alias, symlink, stale-plan and write-fault cases;
independent private differential review; and representative game round trip.
The current 43 synthetic tests are regression evidence for M1–M3, not proof
of M4 UI, atomic publication, cross-platform behavior, or new write support.

## First implementation slice, risks, and authorization surface

If M4 is later authorized, implement the smallest vertical slice in this
order: (a) typed S/P/C inspection and plan API with a read-only result for
`ffd0...`; (b) one **separately qualified** exact forward party[0] edit on
that available save, with individual canary, independent private audit and
human game round trip before it is labeled `PROVEN`; (c) hardened atomic
new-file transaction and independent receipt verifier; (d) a one-window
Tkinter select/preview/save/results UI plus CLI adapter; (e) macOS/Windows
source-run validation. Preserve historical exact seals as regression vectors.
No boxes, bags, arbitrary values, arbitrary saves, other builds, or additional
fields are in this slice.

The main risk is **very narrow practical reach**: an exact-hash allowlist
supports only enrolled private snapshots. Broader player usefulness needs a
future, independently justified lineage/profile rule and regression corpus;
structural similarity cannot substitute for provenance. Other risks are
coupled-stat mistakes, divergent verifier and writer assumptions, path races,
and OS-specific publication/packaging behavior. The design counters these
with exact registry entries, separate semantic output auditing, independent
private verification, fault injection, and OS-specific testing. A GUI adds
some packaging cost but substantially improves path choice and recovery UX.

**Smallest human authorization to start:** explicitly authorize this bounded
M4 implementation slice, including read-only core/UI work and one proposed
exact capability qualification on the supplied lineage. Require a separate
human game canary and explicit adoption of that proof before enabling its
edit action or claiming M4 completion. This document and its review PR are
design only; they do not grant that authorization.
