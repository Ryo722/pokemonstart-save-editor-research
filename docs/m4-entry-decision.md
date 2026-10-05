# M4 entry decision package — 2026-10-05

## Decision and authority

**Recommendation: a thin, local Tkinter GUI over one reusable, capability-gated
Python core, with a CLI adapter for audit and tests. M4 implementation is not
authorized by this document.** The UI remains read-only for any input without
positively qualified provenance/profile **and** a proven capability. The first
M4 uncertainty is reusable eligibility across a normal game save, followed
by one bounded capability family that remains selectable when its semantic
preconditions still hold. Another exact one-input canary alone would leave a
one-shot proof launcher behind the GUI.

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
memory, without an output path; each rejected the input profile/hash. This is
direct code evidence for the current exact-hash boundary, not evidence that
the proposed reusable boundary is already safe.

## Exact support and capability registry at entry

`PROVEN` below means a particular transformation from a particular exact
private input lineage, backed by the cited game-boundary evidence. It is not a
numeric range, another party index, or any structurally similar save. Current
proof writers use full input SHA-256, semantic baseline, profile checks, and
fixed output seals. These are **exact proof vectors** and regression evidence,
not a reusable capability family. Their seals cannot silently become
authority for arbitrary inputs or targets.

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

No M3C field research must reopen before **design**. M4 must first qualify a
reusable retained-lineage eligibility rule. A new exact friendship `52 -> 53`
canary by itself would leave the next normal resave unsupported. A bounded
two-state party[0] markings `0 <-> 1` family is one low-coupling candidate for
repeated use; the existing `0 -> 1` proof is one exact vector, while `1 -> 0`
and use across newly qualified saves remain **BLOCKED**. Confirm that this is
a meaningful player action before choosing it for implementation. No
Tera/item/move/identity research is a prerequisite to the minimum product.

## Confirmed one-shot failure and evidence for reusable P

The exact-hash concern is confirmed. Each writer rejects unknown full input
SHA-256; the shared `Profile` additionally fixes slot/counter, physical
section 1, party[0] record SHA-256, sectors 30/31 and footer SHA-256. M3A and
the retained canaries show that a normal save increments the counter, rotates
the active slot, and may change the opaque footer. Thus if an eligible A is
edited to new B and the game normally saves B as C, the current code has no
entry for C and rejects it even if S0 passes. The supplied counter-6 return
save is a concrete example: it passes structural verification but all five
current proof writers reject it. This conclusion concerns the current
implementation; it does not prove that C is safe for a new write.

The following evidence is available for a **candidate** bounded P rule:

| Evidence | What it can establish | Limit |
| --- | --- | --- |
| Retained private root/return saves and canonical game-canary records | An observed v0.15 lineage, exact root hashes, successful slot/counter transitions and retained party state | Does not qualify an unrelated save |
| CFRU-JP section signature/layout, checksums, section permutation and parity | S0 and expected game-save mechanics | Signature `0x08012025` is format evidence, not a unique PokemonStart build ID |
| Sectors 30/31 and unchecked parasite tails | Known preservation/transition comparisons | Application semantics are not decoded; similarity alone is not provenance |
| Stable party identity/semantic fields across observed returns | A narrow transition fingerprint | A matching record could be copied or arise elsewhere; not sufficient alone |
| Target ROM SHA-256 `48ecc0ef...` in the evidence ledger | A possible build identifier | Only a prior command log; no independent local rehash in this review, and a ROM hash alone cannot prove which build produced an arbitrary save |

There is no verified save-resident build identifier in current canonical
evidence. No ROM/build file is tracked in the repository; the private local ROM hash,
the exact build used for each future normal-save observation, and a full
transition rule still need independent verification. Do not promote the
prior command-log ROM hash or generic layout into P authority.

**Smallest proposed P mechanism, conditional on validation:** enroll only an
already observed private lineage root whose full hash and game provenance are
recorded; independently hash the locally selected PokemonStart v0.15 ROM
read-only and bind that build hash to the user-confirmed emulator environment
used for the observed lineage; recheck it when that environment is selected
again.
Store a local, private lineage journal outside Git with root hash, build hash,
each approved editor output hash, active-slot hash/counter, party identity and
semantic fingerprint, and preservation hashes. The journal contains hashes
and metadata, not save bytes. The editor records B automatically after its
independent output audit; neither a user-entered hash nor a filename enrolls
a save.

For candidate C, re-evaluate S0 first. Then accept a *single observed normal
save transition* from journaled B only if C's inactive slot is byte-identical
to B's active slot (or its full slot hash matches), C has the unique next
counter in the opposite parity-correct slot, expected section rotation,
the complete active party record and other bounded semantic invariants match
B, and sectors 28–31 plus unchecked regions satisfy the explicitly qualified
normal-save comparison. Allow the external footer to change across the game
save, while preserving it exactly in editor output. Re-hash the selected ROM
for the environment claim and require the private game-observation record.
Only then may the journal add C's newly computed hash and inspected
fingerprints **automatically** and re-evaluate C. A missing B/journal,
unexpected game-side change, unknown
build, or non-matching transition fails closed. This is a chain from an
enrolled local root, not acceptance of arbitrary v0.15 saves; a copied or
forged matching file remains a provenance limitation, so claim bounded
observed-lineage eligibility, not cryptographic proof of game origin.

This rule is a **design hypothesis**, not currently PROVEN. Before enabling
P for writes, independently compare the retained A/B/C private bytes across
multiple observed normal saves (including both slot parities), verify the
local ROM/build hash and environment record, pin allowed transition
invariants, and test both successful continuation and near-miss rejection.
If the normal game legitimately changes any comparison region, narrow or
explain that region from source and further private evidence rather than
silently relaxing the rule. Do not store private saves or journal data in Git.

**C remains separate from P.** A reusable field capability needs a source-
backed encoding/semantic rule; explicit party index, permitted from/to states
and combinations; all coupled-field invariants; complete byte/checksum
envelope; synthetic property and negative tests across qualified counters
and both slot parities; independent private differentials on more than one
P-qualified source hash; and a representative game load/resave that retains
the edit. The existing friendship `50 -> 51` and `51 -> 52` exact vectors
suggest a narrow family candidate but do not prove `+1` for other values or
other saves. Until that bounded cross-hash evidence is adopted, generalized
friendship and markings families remain BLOCKED; the UI exposes only exact
PROVEN vectors whose source passes P and C.

## Delivery options

| Shape | Usefulness, safety and testability | Portability, dependencies and packaging | Decision |
| --- | --- | --- | --- |
| A. CLI-first editor | Smallest implementation; explicit paths and deterministic audit; ordinary players must type commands and interpret errors | Python stdlib, macOS/Windows source-run; packaging optional | Keep as core adapter and diagnostic path, not the sole player UI |
| B. Minimal local GUI coupled directly to writers | Easy file picking and preview, but duplicates gates in callbacks and makes proof scripts UI-facing | Tkinter is light; coupling makes regression and future changes harder | Reject |
| C. Thin GUI over one transaction/capability core | Clear select/preview/confirm/recovery flow; S0/P/C and lineage continuation remain testable below UI | Tkinter plus stdlib core; OS-specific bundle builds when release-ready | **Recommended** after reusable P and one bounded C family are qualified |
| D. Guided read-only verifier plus sealed proof launcher | Even smaller; safe if it only lists exact allowed actions | stdlib, no GUI dependency; normal resave still returns to read-only | Useful interim diagnostic, insufficient M4 completion |

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
2. **Profile eligibility (P):** distinguish a reviewed exact root/vector
   hash from a newly computed descendant hash. The latter qualifies only
   through the locally journaled, evidence-validated game-save transition
   rule above, including the independently checked build/environment
   binding. Check slot/counter/parity, party identity and stable profile,
   sectors 30/31 and footer policy on every reopen. A structurally valid
   unknown save without a qualified ancestor remains read-only. The supplied
   `ffd0...` hash is a named observed return, not a general profile rule.
3. **Capability registry (C):** distinguish `EXACT_VECTOR` entries tied to
   one source hash from `FAMILY` entries tied to a qualified P profile plus
   explicit semantic preconditions. Each binds party index, permitted
   from/to states and combinations, source/game evidence, encoder/validator,
   allowed byte/checksum envelope, and status. Only a proven entry whose
   preconditions pass appears in the UI. `BLOCKED`, `CANARY_READY`, and
   `UNSUPPORTED` never become actions. No Cartesian product of individually
   proven edits and no open numeric input is inferred.
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
   construction; one writer's success flag is insufficient. A successful
   output audit records the new journal edge but does not pre-approve the
   later game-resaved file.
8. **Recovery/output policy and adapters:** UI/CLI receive only a verified
   receipt and recovery instructions. They cannot bypass P or C.

The existing `write_new` uses exclusive creation, fsync, readback, source
rehash, and best-effort cleanup on Python exceptions. A process crash during
direct destination writing can still leave a partial destination. Before M4
claims "failed writes leave no partial output", stage a private temporary
file in the destination directory, fsync and verify it, then publish without
clobbering an existing path. **Atomicity and no-clobber behavior on both
macOS and Windows are implementation proof obligations**, including crash,
race, filesystem, and cleanup tests; this design does not assume one Python
rename primitive has identical guarantees on both systems. If the required
primitive is unavailable, refuse publication. Recheck source and destination
identity, including aliases/symlinks, before publication; verify published
bytes and hashes after publication. Do not call an ordinary replacing rename
on a user-selected existing path. The user keeps the original as rollback.

## Player workflow and recovery

1. Select a local `.sav`; open read-only and show SHA-256, structure/profile
   result, party[0] original values, and a plain reason when edits are
   unavailable. Do not infer build support from filename or layout alone.
2. Present only exact proof-vector or bounded family choices returned by
   S0+P+C; never an unrestricted number box or an edit on `ffd0...` until P
   and a matching C are separately qualified. Show which values will change
   together (including cached HP/stats).
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
   if the generated copy is rejected by the game. When a later normal resave
   is reopened, re-run S0/P/C; never rely on the prior UI result. Do not
   claim a game-load pass from structural verification alone.

No ROM, `.gba`, `.sav`, `.pks`, BPS/IPS patch, proprietary executable, or
copyrighted game asset enters Git, a PR, a release asset, or a log. During
development private outputs remain outside the repository. No live emulator
save is written automatically.

## M4 acceptance and tests

M4 implementation should not be marked complete until all of these are
demonstrated on macOS **and** Windows for the approved first slice:

1. A real, currently available private root passes a **validated reusable P
   rule** for the retained v0.15 lineage and offers at least one meaningful,
   bounded `PROVEN` party[0] capability family. Historical exact proof
   vectors alone do not satisfy this criterion; the supplied `ffd0...` save
   currently remains read-only.
2. **Repeated-use gate:** start from writer-eligible A, apply an authorized
   edit to new B, load B in the same independently checked PokemonStart v0.15
   environment and perform a normal save to produce C. Without code changes
   or manually adding C's full SHA-256 to an allowlist, reopen C. Re-evaluate
   S0, P and C independently. If C passes the proven lineage transition and
   still meets the capability family's exact semantic preconditions, its
   next permitted edit is available; otherwise fail closed with the specific
   unmet condition. This proves continuation for the tested bounded profile,
   not universal eligibility or an unlimited value range.
3. Select/inspect shows original values and provenance; malformed,
   ambiguous, non-lineage, and unsupported files expose no edit action.
4. Only exact approved from/to transformations and approved groups can be
   selected; unsupported values, pairings, fields and party indices fail
   closed through the core, including direct CLI/API calls.
5. User chooses a new destination; input and pre-existing output remain
   byte-identical. Repository output, aliases, and overwrite are rejected;
   the UI never chooses a live-emulator path automatically and asks the user
   to confirm the selected path is not live. Fault injection shows no
   published partial save.
6. Independent output audit proves complete semantic before/after state,
   every changed byte and checksum, preserved regions, source/output hashes,
   and source immutability. A deliberate unexplained diff fails.
7. The local UI displays the verified receipt and original-file recovery
   path. It does not report "game compatible" until a representative actual
   game load and normal-save return has passed for the bounded family.
8. The stdlib core/CLI tests and thin UI integration tests pass on both OSes;
   a private-copy continuation audit and representative game return audit
   pass without committing private data. Bundled builds, if distributed,
   must be produced/tested on their respective OSes and contain no protected
   artifacts.

Test the layers at their real boundaries: synthetic malformed/slot/parity
profiles; lineage-graph acceptance and forged/near-miss transition rejection;
exact-vector versus family semantic matrices; changed-byte property checks;
existing-output, alias, symlink, stale-plan and write-fault cases;
independent private differential review; and representative repeated-use game
round trip.
The current 43 synthetic tests are regression evidence for M1–M3, not proof
of M4 UI, atomic publication, cross-platform behavior, or new write support.

## First implementation slice, risks, and authorization surface

If M4 is later authorized, implement the smallest vertical slice in this
order: (a) verify the local build hash and retained private transition corpus,
then define/test one root-anchored, journaled P rule across normal saves;
(b) typed S0/P/C inspection and immutable plan API, distinguishing historical
exact vectors from a **separately qualified** narrow family (candidate:
party[0] markings `0 <-> 1`); (c) prove the two directions and cross-hash
continuation with source/semantic checks, individual private differential
audits, and representative human game round trips before exposing that
family; (d) hardened atomic new-file transaction and independent receipt
verifier; (e) a one-window Tkinter select/preview/save/results UI plus CLI
adapter; (f) macOS/Windows source-run validation. The UI may be developed
against synthetic data while P/C are blocked, but must not enable private
writes before those gates pass. Preserve historical exact seals as regression
vectors. No boxes, bags, arbitrary values, arbitrary saves, other builds, or
additional fields are in this slice.

The main risk is **narrow practical reach**: the proposed journal supports
only descendants of enrolled, observed private roots whose transitions and
semantic state stay within the qualified envelope. It may reject legitimate
game saves after unrelated state changes, lost journal state, or use of an
unqualified build. That is preferable to calling a matching signature P.
Broader user-save support needs a separate positive provenance/profile
argument and regression corpus. Other risks are a false transition rule,
overgeneralized capability semantics, coupled-stat mistakes, divergent
verifier/writer assumptions, path races, and OS-specific publication or
packaging behavior. Independent private comparisons, negative transition
tests, separate semantic output auditing, fault injection, and OS-specific
testing address these risks. A GUI adds packaging cost but improves path
choice and recovery UX.

**Recommended exact human authorization phrase:**

> AUTHORIZE BOUNDED M4 IMPLEMENTATION: retained-lineage S0/P/C qualification, one bounded repeated-use party[0] capability family, new-file transaction hardening, and thin Tkinter/CLI delivery; no arbitrary-save support or merge.

This phrase would authorize implementation and private preflight for that
slice only. Require
a separate human game canary and explicit adoption of the P/C proof before
enabling the family on private inputs or claiming M4 completion. This document
and its review PR are design only; they do not grant that authorization.
