# M4 Windows bounded integration candidate authorization — 2026-10-05

## Human authorization

> `AUTHORIZE M4 WINDOWS BOUNDED INTEGRATION CANDIDATE: integrate the proven Windows path under a narrow boundary—validated Windows browser/in-memory delivery, and filesystem publication only to user-controlled local fixed NTFS with reparse parents rejected; keep network/removable/non-NTFS paths fail-closed, make no hostile concurrent-junction or power-loss durability claim, add no new save/build/capability scope, and do not merge PR #14 or declare M4 COMPLETE without a separate review and authorization.`

## Authorized change

This authorization permits a bounded production-integration **candidate** on Draft PR #14 or its exact continuation branch. It does not itself adopt or merge Windows write support.

The candidate may:

- enable the already-proven Windows browser/in-memory delivery path behind an explicit validated-Windows gate;
- integrate Windows filesystem publication only for a user-controlled local fixed NTFS destination;
- require every destination parent component to be non-reparse and reject junction/reparse parents;
- retain no-clobber staging/publication, independent output audit, source immutability checks, and hash/metadata-only retained-lineage binding;
- route filesystem publication through the Windows NTFS implementation only when that narrow runtime boundary positively qualifies;
- keep browser/in-memory delivery logically separate from filesystem-publication eligibility;
- add or update synthetic, actual-Windows, private-validation, negative, fault/race/process-boundary, CLI, and NiceGUI tests needed to prove the integrated candidate;
- update PR #14 documentation and evidence to state the exact supported and unsupported boundary.

## Required fail-closed boundary

The integration candidate must reject or leave unsupported:

- network shares;
- removable media;
- non-NTFS filesystems;
- destination paths whose parent chain contains a reparse point;
- existing destinations or aliases;
- repository destinations;
- malformed, ambiguous, unsupported, or non-lineage saves;
- unsupported capabilities, values, party indices, builds, or versions;
- remote/LAN/public NiceGUI exposure;
- automatic emulator live-save replacement.

## Explicit non-claims

The candidate must not claim:

- resistance to a malicious concurrent parent-junction swap after validation checks;
- power-loss durability of Windows directory metadata or final-name persistence;
- general Windows filesystem safety beyond the validated local fixed NTFS boundary;
- support for unvalidated Windows versions/environments merely because `sys.platform == "win32"`;
- arbitrary-save, broader-build, broader-version, or additional-field support.

A failed or interrupted Windows publication may leave only bounded transaction-owned artifacts consistent with the documented recovery model; the source save remains immutable.

## Evidence already available before this authorization

Draft PR #14 candidate `4513b91d111f46fcd09bd99aebb5f837c3c1aca5` recorded:

- actual Windows 11 build 26200.9457 validation on local NTFS;
- staged/flushed candidate bytes and no-clobber same-directory hard-link publication;
- race, fault, and process-exit checks;
- fresh Windows-local S0/P binding for the retained private v0.15 root and independently checked ROM/build;
- only the bounded `party[0]` markings `1 -> 0` action under the validation gate;
- one private Windows output with independent complete-byte audit and immutable source;
- private NiceGUI `BrowserWorkflow` output identical to the independently verified filesystem candidate;
- full actual-Windows suite result of 82 tests passing with 12 macOS-only skips.

These are evidence for constructing and reviewing the integration candidate, not automatic authority to merge or enable Windows support on canonical `main`.

## Authorization boundary

This authorization does **not** permit:

- merging PR #14;
- marking PR #14 ready solely on the basis of this authorization without completing and independently reviewing the integration candidate;
- enabling Windows write/download on canonical `main` before later explicit adoption;
- declaring M4 COMPLETE;
- adding new save/build/capability scope;
- weakening the current S0/P/C, transaction, audit, private-data, or localhost-only boundaries.

After the integration candidate is complete, it requires a fresh-context review of the exact candidate and a separate Human adoption/merge decision. Only that later decision may determine whether the bounded Windows path should be enabled on canonical `main` and whether the M4 completion criteria are satisfied.
