# M4 Windows validation plan

**Status: NOT RUN.** The M4 publication module currently fails closed on every
platform except macOS. macOS results do not establish Windows safety.

## Source-run prerequisites

- Python 3.10 or newer with Tkinter and no third-party package requirement.
- A private, local NTFS test directory outside the repository and outside an
  emulator live-save directory. Synthetic fixtures are sufficient for the
  initial safety checks.
- The independently checked PokemonStart v0.15 ROM and retained private save
  only after the synthetic platform checks pass. Do not include either in Git,
  a PR, logs, or a release bundle.

## Required Windows evidence before enabling publication

1. Run `py -m unittest discover -s tests -v`. Distinguish tests skipped by the
   macOS-only publication gate from tests actually executed on Windows.
2. Verify the intended Windows implementation on the selected filesystem:
   stage in the destination directory, write all bytes, flush the file, and
   independently audit the staged bytes before exposing the final name.
3. Prove no-clobber final-name creation against an existing file, a symlink,
   a hard link, a junction/parent alias, and a competing creator. Reject
   repository destinations and source aliases. Do not use replacing rename.
4. Force a short write, audit rejection, file/link failure, and process exit
   immediately before and after publication. Before publication the final
   path must be absent; after publication it must contain the complete,
   independently verified bytes. The source and any pre-existing destination
   must remain byte-identical. Record hidden-stage cleanup behavior.
5. Check the chosen durability and atomic-creation APIs against actual Windows
   behavior, including filesystem and permission differences. If the proof
   only covers NTFS, explicitly reject or leave unsupported other filesystem
   types; do not infer support from macOS `os.link` results.
6. Start the Tkinter GUI from source, select a synthetic valid save, confirm
   S0/P/C display and unavailable-action behavior, and exercise a synthetic
   qualified preview/commit without any live emulator location.
7. Rehash the selected ROM/build locally and repeat the approved private
   retained-lineage differential and game/emulator canary only after the
   platform publication proof and the M4 P/C evidence gate pass.

The Windows result must be recorded separately from macOS in the implementation
PR. A green cross-platform test run alone cannot prove private game acceptance.
