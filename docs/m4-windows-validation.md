# M4 Windows validation plan

**Status: NOT RUN; Windows private writes/downloads are disabled.** The current
implementation permits read-only S0/P inspection on an unvalidated host. It
returns no C write actions and rejects preview, core commit, browser commit, and
browser download until Windows validation is completed and a later human
decision explicitly adopts Windows write delivery. Do not describe Windows as
supported before that decision.

## Dependency and network boundary

- Python 3.10+ runs the save-analysis, S0/P/C, transaction, receipt, and CLI
  core. These do not import or require NiceGUI.
- NiceGUI is an optional UI dependency only, pinned in
  `requirements-m4-ui.txt`.
- The NiceGUI service must bind only to `127.0.0.1`. The supported configuration
  must set `on_air=False`; no relay, LAN/public listener, or remote hosting is
  allowed. Private save and ROM/build bytes must remain on the local machine.
- Windows source-run validation must confirm browser upload → S0/P/C inspection
  → bounded preview → explicit commit → independent output audit → verified
  browser download. Before Windows write delivery is adopted, the UI must show
  that writes are disabled and keep preview, commit, and download unavailable.

## Synthetic platform gate

Run the full suite with the optional UI dependency installed and distinguish
executed tests from skips:

```text
py -m unittest discover -s tests -v
```

The suite must prove that simulated `win32` keeps valid S0/P inspection
read-only, returns no editable capability, and rejects both
`core.commit_download` and filesystem `core.commit` even when given a plan
created on macOS. It must also reject browser preview/commit/download at the
workflow boundary. Verify that no journal node or edge is added, no destination
file is created, and the source remains byte-identical. macOS write behavior
must continue to pass unchanged.

## Windows NTFS filesystem publication: CLI/core

Before enabling filesystem publication on Windows, validate the intended
new-file/no-clobber implementation on the selected filesystem, beginning with
synthetic data in a private NTFS test directory outside the repository and any
emulator live-save directory:

1. Stage in the destination directory, write all bytes, flush the file, and
   independently audit staged bytes before exposing a final name.
2. Prove no-clobber creation against existing files, symlinks, hard links,
   junctions/parent aliases, source aliases, repository destinations, and a
   competing creator. Do not use replacing rename.
3. Inject short writes, audit rejection, file/link failures, and process exits
   immediately before and after publication. Before publication the final path
   must be absent; after publication it must contain the complete audited
   bytes. Preserve source and pre-existing destination bytes and record stage
   cleanup.
4. Validate atomicity and durability APIs on actual NTFS, including
   permissions and directory-sync behavior. If only NTFS is proved, reject or
   leave other filesystems unsupported.
5. Confirm core/CLI fails before I/O on every unvalidated platform/filesystem.

macOS `os.link` and fsync tests do not establish Windows behavior.

## Windows private S0/P/C validation

Only after synthetic platform checks pass, and only using locally authorized
private inputs outside Git:

1. Rehash the selected PokemonStart v0.15 ROM/build locally and validate the
   retained private save's S0 structure on Windows.
2. Independently establish the retained P binding for that host and verify the
   bounded C family remains only party[0] markings `0 ↔ 1`. Keep any Windows
   journal hash-only and private. Do not infer Windows eligibility from a
   filename, save layout, macOS journal, or matching ROM hash alone.
3. Confirm unsupported or unqualified private saves expose no edit action and
   that all Windows write/download entry points remain disabled until the
   platform proof is adopted.
4. Do not repeat a game canary merely because the host platform changed. If
   source/profile or semantic evidence reveals a material platform-specific
   uncertainty, stop and seek the smallest controlled evidence needed.

Keep saves, ROM/build data, and generated outputs outside Git, PR contents,
logs, and release bundles. Do not overwrite the source or an emulator live-save
path.

## Windows NiceGUI browser/UI validation

On Windows, verify that the service starts only on `127.0.0.1`, with
`on_air=False`, and that it cannot be reached through a LAN/public interface.
Exercise synthetic supported-shaped and unsupported inputs first, then the
authorized retained private input only after the S0/P/C checks above:

- unsupported/unqualified input displays S0/P results but no edit action;
- the eligible preview describes only the core-returned markings action;
- stale plans fail closed;
- commit uses the existing core transaction and independent receipt audit;
- download is exposed only after output verification and preserves source
  bytes; no automatic write to an emulator path occurs;
- host/network configuration contains no relay, `on_air`, or public binding.

Record Windows browser results separately from filesystem publication results.
Do not claim Windows UI write support until both the core gate and these checks
are reviewed and explicitly adopted.

## Completion record

Record the OS/build, Python and NiceGUI versions, filesystem, exact tests run and
skipped, source/build/journal verification outcome without publishing private
file bytes or per-save hashes. A green cross-platform synthetic suite alone
does not establish private Windows S0/P/C acceptance. M4 remains IN PROGRESS
until the canonical cross-platform acceptance criteria are satisfied or a
later human decision changes them.
