# Bounded M4 implementation progress — 2026-10-05

## Authority and status

- **Canonical/repository:** freshly fetched `origin/main` is `ad24706a50f819992ab1a6395d8f3f4bc0246446`. M1, M2, M3A, M3B and M3C are COMPLETE. Bounded M4 implementation is AUTHORIZED / IN PROGRESS; implementation PR merge is not authorized. The only open PR observed is historical M2 #3.
- **Upstream-source:** pinned CFRU-JP `e24a16fe39e27ae162faf5b78596d1f3df18489d` `include/pokemon.h` exposes `MON_DATA_MARKINGS = 8` and a direct `u8 markings` in `struct Pokemon`, after seven OT-name bytes. This supports the direct byte layout, not a PokemonStart-wide capability claim.
- **Synthetic:** the M4 tests exercise S0 parity and malformed rejection, root/build/journal diagnostics, a modeled normal-save transition, a 0→1 editor output B, a modeled game return C in the opposite slot, and a 1→0 editor output D with no source-code change between B and D. The test patches the private authority constants and uses synthetic bytes. It does not qualify a private save or actual game behavior.
- **Local private-input:** not yet checked in this implementation run. The supplied root hash has not been independently reproduced here. No private save output was generated.
- **Human game/emulator:** no M4 canary has run. Earlier M3 canaries remain exact-vector regression evidence.
- **Hypothesis/unverified:** the normal-save rule currently requires equal logical section payload hashes, party[0] record, checksum-excluded tails and sectors 28–31; previous active slot preservation; counter increment; and one-position section rotation. Private A/B/C comparisons may reveal a legitimate narrower rule. Do not loosen it without source and transition evidence.

## Implemented on `m4-bounded-editor-slice`

- `pokemonstart_m4_core.py`: typed S0/P/C inspection, root-anchored JSON journal schema v2 with selected build hash and emulator environment ID, private-root enrollment guard, modeled B→C transition check, two-state party[0] markings mutation plan, independent byte/semantic audit, rehash-on-commit, and computed C journal continuation after an explicit human game observation claim. Party identity is stored as a hash; nickname/OT-name encodings are not retained. The journal is created with mode `0600` on POSIX and rejects unexpected fields or non-hash fingerprint content. `FAMILY_PROVEN` remains `False`; core returns no private edit capability.
- `pokemonstart_m4_publication.py`: macOS staged, flushed, fsynced, same-directory hard-link publication with no-clobber semantics and post-publication re-read. Windows fails closed until separately validated. The original stays untouched; the final pathname is absent before the complete staged file is linked.
- `pokemonstart_m4_cli.py`: inspect, eligibility, capability list, root enrollment, preview, commit, and observed-return commands all call the core. The current evidence gate rejects preview and commit. A user-selected `--environment` ID must match the journal for P.
- `pokemonstart_m4_gui.py`: one-window select/inspect/preview/new-file/results flow over the core. Actions stay disabled when the core has none. The default Homebrew Python 3.13 lacks `_tkinter`; system `/usr/bin/python3` imports Tk 8.5. A displayed window has not yet been validated.
- Existing proof writers remain exact-vector tools and were not promoted into FAMILY authority.

The journal must stay outside Git and stores only hashes and bounded metadata. Its build SHA is computed from selected ROM bytes locally; it does not prove a save was produced by that ROM. A human observation claim is recorded separately from structural acceptance. Neither filenames nor user-entered descendant hashes qualify a candidate. A forged local journal remains a provenance limitation and must not be described as cryptographic origin proof.

## Current checks and remaining gates

`python3 -m unittest discover -s tests -q`: **63/63 PASS** on macOS Homebrew Python 3.13 and system `/usr/bin/python3`. The publication tests cover complete output, no overwrite, symlink aliases, repository rejection, concurrent destination creation, short write, link failure, post-publication audit failure, source change, cleanup, and process exits immediately before and after the hard-link boundary. A crash at every possible machine instruction and a Windows run remain unverified. M4 `EditorWindow` construction and bounded hidden and visible Tk event-loop lifecycles passed under system Python. One earlier visible `root.update()` trial hung and was terminated; full user interaction with an eligible private save remains unverified.

Before a private action is exposed: independently rehash the retained root and ROM/build; compare the retained normal-save transition corpus for both parities; settle the exact P transition rule; independently derive private markings 0→1 and 1→0 differentials from more than one P-qualified hash; perform representative actual game load/save; and then change the core authority gate with an evidence record. The present code intentionally cannot write the private root.

The host's workspace boundary limits this agent to `~/claude-workspace/`. The supplied private ROM and save paths are in `~/Downloads/`, so this run has not read them. The next useful input is their placement in a private directory under `~/claude-workspace/` **outside this repository**, with absolute paths supplied privately. They must never enter Git.
