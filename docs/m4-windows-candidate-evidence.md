# M4 Windows validation candidate evidence — 2026-10-05

## Authority and scope

Fresh-fetched GitHub `main` was `d80b0deb9be235344a6bbb0dc54fc98dfaefa02d`.
This feature branch is a reviewable candidate only. Canonical M4 is ADOPTED /
IN PROGRESS, with Windows write and download still disabled. No private ROM or
save was copied into this repository or used in these tests. Open GitHub state
at validation: PR #3 remains open; no open issues were returned.

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

`pokemonstart_m4_windows_candidate.py` is an unadopted direct-call experiment.
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
execution, and power-loss behavior remain unverified. The candidate is not
ready to replace production publication or enable Windows write delivery.

## Private gate and decision surface

Private Windows S0/P/C, local ROM/root hashes, Windows-local journal binding,
one new private output, and private NiceGUI workflow are **not run**. The
authorized ROM and retained save paths have not been supplied on this host.
No additional game canary is required by the current evidence. A later
decision must name the exact candidate commit SHA, resolve the above
filesystem limits, supply private Windows evidence, and explicitly authorize
any Windows enablement or merge. M4 completion criteria are not met.
