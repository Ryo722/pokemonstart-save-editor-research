# M4 PR #13 bounded implementation adoption — 2026-10-05

## Status

**ADOPTED / MERGED AS M4 IN PROGRESS.**

Human authorization:

> `AUTHORIZE PR #13 BOUNDED M4 IMPLEMENTATION MERGE AS IN-PROGRESS: merge exact candidate 2612df5de7bac7a1ebce6650eb9ed69b440fbc4d into main; retain Windows write/download disabled and unproven, retain M4 IN PROGRESS, and do not broaden save/build/capability scope or declare M4 COMPLETE.`

The exact approved PR #13 candidate was:

- PR: `#13 — M4: bounded retained-lineage markings editor with localhost NiceGUI`
- head: `2612df5de7bac7a1ebce6650eb9ed69b440fbc4d`
- base at approval: `b6d430f93a30fab78410c6b9cc7d7748d5e6a87f`

PR #13 was marked ready for review without changing its head and merged with merge commit:

- `4685edd4fa61d7e02a29d1cb6279e0e8858bdaa7`

## Adopted bounded implementation

The merge canonically adopts the macOS-proven bounded M4 slice already documented in `docs/m4-implementation-progress.md` and `docs/m4-p-transition-model.md`:

- separate S0 structural, P retained-lineage, and C capability gates;
- a retained-lineage-only `party[0]` markings `0 <-> 1` FAMILY;
- hash/metadata-only private lineage journal outside Git;
- source-backed normal-save P transition handling for the qualified volatile fields while unrelated payload remains fail-closed;
- independent byte/checksum/output audit;
- hardened macOS new-file/no-clobber filesystem publication;
- CLI/audit adapter;
- localhost-only NiceGUI adapter bound to `127.0.0.1`, with verified browser download output;
- private B->C and D->E game-boundary evidence for both markings directions;
- Windows write/download fail-closed gating while Windows remains unvalidated.

The local regression evidence recorded by PR #13 is 72/72 tests passing in the NiceGUI virtual environment and 71 passing / 1 optional NiceGUI simulation skipped under system Python. This is local execution evidence, not GitHub Actions reproduction.

## Preserved boundary

This adoption does **not** authorize or claim:

- M4 COMPLETE;
- Windows write/download support;
- Windows NTFS publication safety;
- arbitrary/non-lineage saves;
- broader PokemonStart builds/versions;
- additional fields or party indices;
- unrestricted values;
- boxes/bags;
- automatic live-emulator overwrite;
- remote/LAN/public browser exposure;
- protected-data publication.

Windows remains read-only for S0/P inspection; C write actions and preview/commit/download remain disabled until separate Windows validation is completed and later human adoption explicitly enables that platform.

## Next milestone boundary

M4 remains **IN PROGRESS**. The cheapest remaining uncertainty-reducing work is the bounded Windows validation plan in `docs/m4-windows-validation.md`: synthetic/platform checks, NTFS publication proof, private Windows S0/P/C validation, and localhost NiceGUI/browser validation. A later evidence review must decide whether that evidence satisfies the existing cross-platform M4 completion criteria or whether those criteria themselves should be reconsidered from canonical evidence.

No further capability expansion or M4 completion declaration is implied by this merge.
