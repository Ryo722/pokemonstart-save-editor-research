# M4 Windows validation — COMPLETE for bounded support

**Status: COMPLETE / ADOPTED for the bounded Windows path merged in PR #14.**

PR #14 exact candidate `a2f61ac9fa34164a531b5a884a40102de3bc52cf` was explicitly authorized and merged as `2547650cf898c89450a1d95b5252cf9c52e0f634`.

The adopted Windows boundary is deliberately narrow:

- semantic/in-memory/browser delivery only when the explicit host gate accepts Windows build `26200.9457`;
- filesystem publication only to a user-controlled local fixed NTFS destination;
- every existing destination-parent component must be non-reparse;
- destination must be a new `.sav` outside the repository and not alias the input;
- network, removable, non-NTFS, reparse-parent, existing-destination, and unvalidated-build cases fail closed.

This document records the validation disposition. Detailed executed evidence and labels are in `m4-windows-candidate-evidence.md`; exact completion authority is in `m4-completion.md`.

## Dependency and network boundary

- Python 3.10+ runs the save-analysis, S0/P/C, transaction, receipt, and CLI core.
- NiceGUI remains an optional UI dependency pinned in `requirements-m4-ui.txt`.
- NiceGUI binds only to `127.0.0.1` with `on_air=False`.
- No relay, LAN/public listener, remote hosting, or external private-save upload is supported.
- Private save and ROM/build bytes stay local and outside Git.

## Executed Windows platform evidence

Actual Windows validation used Windows 11 build `26200.9457` on local NTFS.

The production-integrated Windows suite recorded **88 tests OK with 12 macOS-only skips**. Executed coverage included:

- exact Windows host gate and changed-build fail-closed behavior;
- production S0/P/C core;
- CLI preview/commit;
- localhost NiceGUI browser simulation and listener configuration;
- in-memory verified browser download independent from filesystem publication;
- local-NTFS publication success;
- existing destination and alias rejection;
- hard-link alias rejection;
- repository-destination rejection;
- junction/reparse-parent rejection;
- competing final-name creator no-clobber behavior;
- short-write, staged-audit, link, source-mutation, and post-publication-audit failures;
- preservation of a rival replacement rather than deleting a path no longer owned by the transaction;
- process exit immediately before and immediately after final-link publication;
- deterministic fail-closed decisions for network/removable/non-NTFS cases where an actual unsupported volume was unavailable.

These are local execution results, not GitHub Actions reproduction.

## Private Windows S0/P/C validation

Using locally authorized private inputs outside Git:

1. the selected PokemonStart v0.15 ROM/build and retained private root were independently rehashed locally;
2. a fresh Windows-local hash/metadata-only journal was created rather than treating the macOS journal as Windows proof;
3. the retained root passed S0 and P;
4. the core returned only the bounded `party[0]` markings `1 -> 0` action for that starting state;
5. one new private `.sav` was published in a local NTFS private directory through the Windows validation path;
6. the normal receipt and a separate complete-byte audit passed;
7. exactly the markings byte and one required section checksum byte changed;
8. all section checksums and preservation invariants passed;
9. the source remained byte-identical;
10. the private NiceGUI workflow returned bytes identical to the independently verified filesystem output without creating a duplicate lineage edge.

After production integration, a read-only private check confirmed the production host gate, S0/P/C inspection, preview hash, independent audit, and BrowserWorkflow preview matched the previously audited private result. It created no new private save and no new game canary.

## Filesystem publication contract

On adopted Windows filesystem commit:

1. destination boundary is checked;
2. source identity and candidate audit are checked;
3. a private same-directory stage is created;
4. all candidate bytes are written, flushed, and `os.fsync` is called;
5. stage bytes are reread and independently audited;
6. source identity is checked again;
7. a no-clobber same-directory hard link exposes the final name;
8. final bytes are reread and independently audited;
9. source identity is checked again;
10. the transaction-owned stage is cleaned up on normal completion/failure;
11. post-publication cleanup removes a final entry only when it is still demonstrably the transaction-owned link.

The untouched input is always the recovery anchor.

Tested process exits before final-link creation left no final pathname and a complete private stage; tested exits immediately after link creation left a complete final file and stage.

## NiceGUI browser/UI result

Windows NiceGUI validation established:

- localhost-only startup on `127.0.0.1`;
- `on_air=False`;
- no dependency on NTFS publication for browser/in-memory delivery;
- unsupported or unqualified input exposes no edit action;
- eligible input exposes only the core-returned bounded markings action;
- stale plans fail closed;
- commit uses the same core transaction and independent receipt audit;
- download becomes available only after output verification;
- input remains immutable;
- no automatic emulator live-save write occurs.

## Explicit non-claims retained after adoption

The adopted Windows path does **not** claim:

- support for Windows builds outside the exact validated host gate;
- network/removable/non-NTFS filesystem publication;
- general Windows filesystem safety outside local fixed NTFS;
- protection against hostile concurrent parent-junction/final-name replacement after path validation;
- Windows directory-metadata or final-name persistence across sudden power loss;
- actual Windows symlink-fixture execution where the validation account lacked the necessary privilege;
- arbitrary save, broader build/version, broader capability, or broader party-index support.

These limits are part of the support contract rather than pending hidden proof obligations for the completed first slice.

## Game-boundary disposition

No additional game/emulator canary was required merely because the host OS changed. The bounded markings FAMILY already had representative retained-lineage game-boundary evidence in both directions. Windows validation targeted the OS-specific delivery, filesystem publication, private S0/P/C, and fail-closed boundaries instead.

## Completion

The Windows delivery gap identified at M4 entry is closed under the exact narrow boundary above. Together with the adopted macOS evidence, this satisfies the cross-platform acceptance requirement for the bounded first slice.

M4 completion is recorded in `docs/m4-completion.md` and the canonical current state is defined in `docs/decision-record.md`.
