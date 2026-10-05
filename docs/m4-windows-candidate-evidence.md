# M4 Windows validation candidate evidence — 2026-10-05

## Authority and scope

Fresh-fetched GitHub `main` was `d80b0deb9be235344a6bbb0dc54fc98dfaefa02d`.
This feature branch is a reviewable Draft PR only. Canonical M4 is ADOPTED /
IN PROGRESS, with Windows write and download still disabled on `main`. No
private ROM or save was copied into this repository. The initial synthetic
phase used no private inputs. At that baseline, PR #3 was open and no open
issues were returned.

## Actual Windows baseline

- Host: Windows 11 Home, version `10.0.26200`, command-line build
  `10.0.26200.9457`.
- Python: bundled Windows CPython `3.12.14`; the system `py` launcher reports
  no installed Python. NiceGUI was absent at baseline. `nicegui==3.17.0` was
  then installed in a temporary directory outside the repository.
- Test destination: Windows temporary directory on the local C: NTFS volume.
  Windows volume inventory returned `NTFS`; the candidate independently checks
  the actual destination volume with `GetVolumePathNameW`, `GetDriveTypeW`, and
  `GetVolumeInformationW`.
- The unmodified main suite ran as-is: 72 tests, 3 failures, 3 errors, 13
  skips. Those six failures came from tests assuming macOS write delivery on a
  real Windows host. They were made explicit synthetic macOS-gate tests in this
  branch. The separate actual-Windows gate test confirms S0/P inspection,
  zero C actions, and preview, in-memory commit, filesystem commit, browser
  preview/commit/download rejection, with no journal, source, or output change.

## Publication primitive and executed synthetic evidence

The initial `pokemonstart_m4_windows_candidate.py` was an unadopted direct-call experiment.
It rejects nonfixed/non-NTFS destination volumes and reparse-point parents,
including junctions. It stages a private file in the destination directory,
writes and flushes it with `os.fsync`, independently audits staged bytes,
rehashes the source, and uses same-directory `os.link` to create the final name
without replacement. It then rereads and audits final bytes and rehashes the
source. It only removes a published final path if it still names its own stage.

Actual NTFS tests passed for complete publication, source preservation,
existing destination, source alias, hard-link alias, repository destination,
junction parent, competing creator, short write, staged audit failure, link
failure, source mutation, owned-link post-publication cleanup, and process
exits immediately before and after link creation. A pre-link process exit
leaves no final path and one complete private stage; an after-link exit leaves
a complete final file and stage. Normal success/failure paths clean their
stage. Symlink creation was unavailable to this Windows account (WinError
1314), so the symlink hazard was checked by the candidate's existing-path
rejection but not executed as an actual symlink fixture. Network-share and
non-NTFS rejection branches are implemented but not tested on such volumes.

The synthetic validation harness patches the core gate in test scope only and
routes `core.commit` through the candidate publisher. Actual Windows S0/P/C,
markings `0 -> 1`, independent receipt, source immutability, and browser
workflow byte equality passed. Unsupported synthetic save and stale-plan
paths rejected. NiceGUI's actual browser simulation passed upload, preview,
commit, independent output validation, download, and unsupported-save checks;
an actual short-lived Windows process listened at `127.0.0.1` only, with
`on_air=False` from `server_options`. No live emulator path was used.

With pinned NiceGUI available, the branch's full suite ran **82 tests: OK,
12 skipped**. The skipped tests are macOS-only publication and host tests.

## Upstream source evidence and limits

- [Microsoft CreateHardLinkW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createhardlinkw)
  describes NTFS-only, same-volume hard-link creation. Existing-link no-clobber
  behavior was independently exercised on this NTFS host.
- [Microsoft FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)
  describes flushing an open file's buffers. The candidate calls Python
  `os.fsync` on the staged file; no Windows directory metadata flush or
  power-loss durability proof was established.
- [Python `os.link`](https://docs.python.org/3/library/os.html#os.link)
  documents Windows support. The macOS publication proof was not treated as
  Windows evidence.

The path checks do not pin parent directory handles against a concurrent
malicious junction swap. The intended first proof is a private local NTFS
directory under the user's control, not a shared or adversarial directory.
Stronger path-race resistance, symlink fixture execution, unsupported-volume
execution, and power-loss behavior remain unverified. This was the boundary
at the validation-candidate stage; the later canonical authorization permits
the bounded integration described below without claiming those proofs.

## Local private-input Windows verification

The user supplied exact Windows-local ROM and retained-save paths outside Git.
Independent SHA-256 calculations matched the previously recorded retained
ROM/build and M3C root identifiers. The save was 131,088 bytes. The input
directory and new output directory passed the candidate's local-NTFS check.
No private absolute paths or new private hashes are published here; a detailed
hash/metadata report remains in the private Windows validation directory.

The exact retained root passed S0, then P against a freshly enrolled
Windows-local hash/metadata-only journal bound to the independently checked
ROM and `windows11-ntfs-private-validation`. The production Windows gate still
returned no C action. Under the explicit test-only gate, the core returned
exactly one FAMILY capability: `party[0]` markings `1 -> 0`. The private
runner used that returned capability without constructing its own.

One new `.sav` was published in the private local NTFS directory through
`core.commit` and the PR #14 candidate publisher. `audit_output` and a
separate read-only execution of `m4_independent_markings_audit.py` passed.
Full byte comparison showed **two changed bytes**: the party[0] markings
byte and one necessary section-1 checksum byte. Structural verification and
all section checksums passed. Active slot/counters, section permutation and
metadata, other party semantics, inactive slot, sectors 28–31,
checksum-excluded tails, and opaque footer remained unchanged. The source
SHA-256 remained identical after filesystem publication and browser exercise.
The new journal had exactly two nodes and one editor edge.

The retained private input then passed `BrowserWorkflow` upload, S0/P,
single-action preview, commit, independent receipt check, and download.
Browser bytes equaled the verified filesystem candidate. Repeating the
deterministic output did not add a duplicate journal node or edge. The
application's server options remained `127.0.0.1`, `on_air=False`; no public
or relay service was used. No emulator live-save path was written and no game
load was performed. A repository test runner records the reproducible checks
without embedding private paths: `tests/m4_windows_private_validation.py`.

After the private gate, the complete actual-Windows synthetic suite with
NiceGUI 3.17.0 ran **82 tests: OK, 12 macOS-only skips**. The separate private
byte audit also passed.

## Bounded production integration candidate

Canonical authorization
[`m4-windows-bounded-integration-authorization.md`](m4-windows-bounded-integration-authorization.md)
permits Draft PR #14 to integrate the narrow path without merging it. The PR
now has two distinct production gates:

- `pokemonstart_m4_host.py` qualifies the exact observed Windows 11 kernel
  build/update revision `26200.9457` for semantic, in-memory, CLI preview,
  and localhost NiceGUI delivery. Other Windows builds, missing build evidence,
  and other platforms except the adopted macOS path fail closed. Browser
  delivery does not check NTFS because it publishes no filesystem pathname.
- `pokemonstart_m4_publication.py` dispatches macOS to its prior publisher and
  Windows to the promoted same-directory NTFS hard-link publisher. The Windows
  path separately checks the current destination volume is fixed and NTFS,
  rejects every reparse component in its parent chain, existing destinations,
  aliases, and repository destinations. Network, removable, and non-NTFS
  volume responses fail before source I/O. No semantic mutation logic was
  duplicated.

**Actual Windows executed integration evidence:** Production `core.inspect`
returned only the bounded synthetic markings action; `preview`, filesystem
`commit`, the CLI preview/commit path, and `BrowserWorkflow` commit/download
used the unpatched production gates and publisher. Output bytes and
independent receipts agreed; source bytes stayed unchanged. A separate test
forced NTFS publication to reject while in-memory/browser delivery still
passed, proving the logical gate split. Production publisher tests covered
the earlier NTFS success, alias, junction, race, write/audit/link fault, and
process-exit cases, plus deterministic network/removable/non-NTFS rejections
and an unvalidated-Windows-build rejection. The NiceGUI user simulation
used the actual Windows gate, and a short-lived process was observed listening
on `127.0.0.1` only with `on_air=False`.

A **read-only** integration check reused the already generated private
Windows output, source, ROM, and journal. It passed the new production host
gate, S0/P/C inspection and preview, `audit_output`, the independent
complete-byte oracle, and BrowserWorkflow upload/preview. The predicted
output hash exactly matched the earlier private output. It created no new
save, journal, browser commit, or game/emulator canary. Private paths and new
hashes remain outside this PR.

The full actual-Windows suite with pinned NiceGUI 3.17.0 was run after
integration: **88 tests OK, 12 macOS-only skips**. The test run included
production core, CLI, NiceGUI browser simulation, localhost listener, NTFS
publication fault/race/crash checks, post-publication rival-replacement
preservation, and the unsupported-volume mocks.
This host cannot execute the macOS OS-specific publication suite. The macOS
branch was left structurally unchanged, and existing synthetic macOS-gate
regressions ran on Windows; earlier executed macOS evidence remains the
OS-specific basis for that adopted path.

## Decision surface and non-claims

This candidate is bounded to the retained v0.15 lineage/build/environment,
`party[0]` markings `0 <-> 1`, the exact validated Windows build for semantic
delivery, and user-controlled local fixed NTFS for filesystem publication.
The input save remains the recovery anchor and is never overwritten. Tested
process exits before publication left no final pathname; tested exits just
after publication left complete bytes. A private stage may remain after a
process exit.

Actual symlink fixture execution was unavailable without changing host
privileges. Actual unsupported-volume execution was unavailable; deterministic
runtime mocks exercised those branches. Hostile concurrent parent-junction
or final-name replacement after path validation is not protected against.
Windows directory-metadata and sudden power-loss persistence are not proven. No
general Windows filesystem or arbitrary-save support is claimed.

Canonical `main` still disables Windows write/download. The exact future
Human decision is whether to adopt and merge this **bounded** PR after fresh
review; the present authorization does not merge it or mark M4 COMPLETE.
No new semantic/game canary is indicated by the integrated-path evidence.
