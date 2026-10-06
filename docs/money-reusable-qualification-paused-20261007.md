# Money reusable qualification — preserved partial candidate

Disposition: **USER_REQUESTED_STOP / QUALIFICATION INCOMPLETE**.

The owner stopped lifecycle work and authorized preservation, review, commit and
push of push-safe material on `codex/money-reusable-qualification-20261007`.
This record does not claim `READY_FOR_INDEPENDENT_REVIEW` for the complete
qualification, and does not report a predicate failure or a Human-only blocker.
No further gameplay was performed after the stop request. A previously submitted
movement command had already completed; only the dedicated emulator process was
then shut down. The original Goal is paused.

## Authority and implementation

Fresh remote main and candidate base:
`f28c1099db6d3155d40db268b0b0fe42afb94d9f`.
Reviewed supporting evidence, independently inspected before implementation:
`codex/post-fl2-acceptance-design-20261007` at
`93c070215181bb9e1a83c1b1b0bc82110a726793`.
The supporting branch was used as preregistration, not canonical code.
Canonical main was not mutated.

The controlling qualification authorization is
`docs/money-reusable-envelope-qualification.md`. Its preregistered range was
reconstructed from the reviewed packet: counters `0..0x7ffffffe`, consecutive
with slot index equal to counter parity, newest selected unambiguously.

The implementation connects only FL2 Money to the new candidate. It requires:

- exact v0.22 ROM SHA, schema 1 with strict integer schema type, profile version
  `v0.22 demo`, and agreement of module ROM/private-root/fixed-target contracts;
- owner-designated private source, supported size `0x20000` or `0x20010`;
- both slots valid, IDs 0–13 exactly once, valid signatures and covered checksums,
  one counter per slot, the ordinary consecutive/parity predicate above;
- both encryption keys zero, both Money values in `0..9,999,999`, both party
  counts `0..6` and record bounds valid;
- exactly one JSON request key `money`, strictly integer `7,654,321`, active
  current value different from target; duplicate JSON keys are rejected;
- clone source and change only active logical section 1 Money LE32 at `0x0290`
  plus its covered checksum at `0xFF6`; diff nonempty, checksum itself may remain
  equal; full equality to an independently computed candidate;
- repository verification and independent parser/auditor acceptance, unchanged
  active slot/counter/metadata/keys/party/inactive slot/extra sectors/footer/tails;
- resolved regular private input, symlink-path rejection, distinct nonexistent
  output, exclusive 0600 creation, fsync, persisted equality, source/ROM hash
  rechecks before/after write, created-file identity checks and bounded cleanup.

Party and Inventory exact-save eligibility remain unchanged. The retained Money
module remains unchanged for regression comparison. Shared publication checks
also strengthen ROM rechecks, symlink handling and output-path identity checks.
The independent audit module imports neither repository writer nor verifier.
It checks structure, but cannot authenticate save origin or build by itself.

## Private identities and completed evidence

Only SHA-256 identities and structural facts are published. Private files,
screenshots, generated scripts and raw logs are excluded.

| Artifact | SHA-256 |
| --- | --- |
| Exact v0.22 ROM | `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0` |
| Original retained Money canary | `d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf` |
| Canary candidate, identical to legacy derivation and historical output | `15bdac0d6635c6237549565c49e3752c167e85a33643b89ff722ed3c7d17d569` |
| Preregistered naturally progressed non-canary | `b32abee33dc951c61068b4a83f4bc06215db8a86d880f07620a1aece82ccca50` |
| First non-canary Money output | `b9c2eabd41a48eeddf659a5653626bed8defef708bf532228b810fbf0e631650` |
| Game working save after first normal SAVE and shutdown | `b1ac6cc623791955b119937d75fe7a423d14edb4976cca3a53eb5b5a48d3d75b` |
| Later read of original source path during publication checks | `fded760ba7a9707a9cb96c6aca3d720eff8018bcb756cb3da3a7854e5f27fe6b` |

**Reproduced offline/private evidence:** retained canary output is byte-identical
to the unchanged legacy Money derivation. Non-canary qualification and full
independent audit passed. Its active Money changed `3032 -> 7,654,321`, active slot
0 / counter 2 unchanged, and changed offsets were exactly
`12944, 12945, 12946, 16374, 16375`. All bytes outside the transaction envelope were
equal. The first output was produced through the FL2 core inspect/preview/write
path, with preview/output hash equality and persisted revalidation. This private
execution used the core API; it is not a subprocess CLI acceptance claim.

**Local live observation:** a dedicated mGBA 0.10.5 process loaded a disposable
copy of the exact ROM/output. Boot-time live RAM corroborated Money `7,654,321`
at `0x0202571c`, party count 1, complete party[0] equality to offline bytes, and
regular-pocket Potion slot 0 quantity 2. The boot-time RAM observation preceded
Continue; it is not alone proof of gameplay acceptance. Continue subsequently
reached the field. Screenshots were inspected locally and are not published.
No game UI display of the target Money is claimed.

**Normal SAVE observation and independent audit:** the field menu's Report flow
and confirmation dialogs were inspected, normal SAVE was completed, and control
returned to the field. A separate independent read-only audit confirmed slot
`0 -> 1`, counter `2 -> 3`, all 14 logical section positions rotating `+1 mod 14`,
both keys zero, Money retained, and previous active slot byte-identical. Sectors
28–31 remained equal. The 16-byte opaque footer changed during game SAVE; this
is separate from the editor transaction, which preserved it exactly. A transient
read during SAVE saw an incomplete section layout; the completed and shutdown
save passed both independent parsing and repository verification.

The resulting target-bearing save rejected the same Money request as a noop.
The shutdown command recorded source ROM and preregistered source save hashes
matching their initial identities. A later publication-time read of the original
source path returned the different hash in the table above, with valid slots,
counters 2/3 and Money 3032 in both slots. The cause is unestablished; this is not
attributed to the owner, another process or the harness. The source was neither
restored nor rewritten. Source immutability across the entire work period is
therefore **not established**, and the earlier matching-hash observation must not
be extended beyond its actual checkpoint. The final read-only audit reconstructs
the original source in memory by reversing the first Money transaction to 3032
and recomputing its checksum; the reconstructed full SHA equals the preregistered
input SHA. That reconstruction corroborates transaction equality but does not
substitute for custody/immutability evidence of the original path.

Subsequent ordinary movement included one wild encounter and successful escape,
but no ordinary Money change was confirmed and no further normal SAVE occurred.
The shutdown working-save hash remained the first normal SAVE identity above.

## Negative coverage and remaining work

Synthetic tests cover both slot directions, rotated logical IDs, both supported
sizes and footer preservation, allowed counter endpoints, and checksum equality
without requiring checksum bytes to change. Rejections cover unsupported size,
erased/partial slots, bad signature/checksum, duplicate IDs, mixed/equal/
nonconsecutive/parity/wrap/sign-boundary counters, active/inactive nonzero key,
active/inactive Money range and party-count violations, noop, bool/float/string/
wrong target/extra request keys, duplicate JSON keys, combined requests, wrong
ROM/profile/module hash, and Party/Inventory non-canary eligibility.

Publication tests exercise existing output/source aliases, symlink and dangling
symlink destinations, source prewrite/postwrite races, ROM prewrite/postwrite
races, persisted corruption with cleanup, and a concurrent existing destination
that must be preserved. These are controlled synthetic failures, not a claim of
exhaustive adversarial filesystem race coverage. Wrong profile schema/version
were also checked read-only. Independent resave rotation/retained-slot checks
have a synthetic positive/negative test.

Still unproven: ordinary in-game Money change and resave, second qualification,
second reload/live confirmation, final normal SAVE and complete editor -> game
-> editor repeated-use proof. No predicate was relaxed. No arbitrary target,
nonzero-key support, Party/Inventory reuse, combined reusable operation, other
build, Stable promotion, GUI/public release or canonical adoption is claimed.

The implementation is preserved for review of this partial state only; full
qualification requires a later instruction to resume the missing lifecycle work.

Final validation/security results are recorded in the companion sanitized JSON.
