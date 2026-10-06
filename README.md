# PokemonStart save editor research

Evidence-first research and tooling for a user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current strategy

The project uses a canonical **two-lane model**:

- **Stable Lane** — durable supported capabilities require stronger lifecycle/provenance/recovery/delivery evidence and a separate adoption decision.
- **Fast Lab Lane** — exact-build experimental capabilities may be developed rapidly on private, recoverable save copies while preserving immutable originals, separate outputs, explainable diffs, verifier acceptance, and exact-build live confirmation where practical.

Fast Lab evidence does **not** imply Stable support.

The controlling strategy/next-work records are:

- `docs/decision-record.md`
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`
- `docs/v022-creation-proofs-and-gui-prototype.md`
- `docs/v022-composed-gui-transaction-proof.md`
- `docs/fast-lab-two-lane-adoption.md`
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md`

## North Star

For each currently supported PokemonStart build/profile, the owner should be able to take a save produced through ordinary gameplay, safely apply supported edits locally, return to the game, continue playing and saving, and later edit the newly progressed save again **without preregistering each individual save hash**.

Unsupported builds, malformed or ambiguous saves, unsupported save states, and unsupported operations must fail closed rather than be guessed.

The project optimizes for **continuous owner use on a supported current build**, not for maximizing isolated proofs or field count.

## Terminal goal

For the currently selected PokemonStart build/profile (currently exact v0.22), provide a **user-operable, recoverable local editor** that supports repeated:

`edit -> play/save -> ordinary progress -> save -> edit`

cycles on naturally progressed owner saves using build-specific and capability-specific eligibility predicates rather than exact-save-hash allowlists.

The editor preserves original inputs, writes only separate outputs, previews semantic and byte-level changes, verifies generated outputs, and rejects unsupported cases rather than guess.

Terminal completion does **not** require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, public release, or Stable promotion of every Fast Lab capability. Later PokemonStart versions are onboarded separately from fresh ROM/save evidence when they become relevant.

## Current position

### Stable Lane

- **M1 — reproducible read-only verifier: COMPLETE.**
- **M2 — exact one-field HP-IV writer proof: COMPLETE.**
- **M3A — reusable write-envelope characterization: COMPLETE.**
- **M3B — bounded same-field transaction proof: COMPLETE.**
- **M3C — bounded party-field expansion: COMPLETE.**
- **M4 — bounded usable-editor first slice: COMPLETE.**
- **M5A — Money: FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.**

Stable provenance work such as P-direct/P-reanchor remains separate and is not on the current practical terminal critical path.

### Fast Lab

- **FL0 — exact-build private ROM preparation + harness: COMPLETE.**
- **FL1 — practical core editing slice: COMPLETE EXPERIMENTALLY.** Exact PokemonStart v0.22 evidence includes bounded Money editing, practical/composed Party editing, and one bounded existing-item Inventory quantity edit.
- **FL2-G0 — durable Fast Lab baseline reconciliation: COMPLETE / MERGED.** Human-authorized candidate `44c90e8217061cc8ac294a392984dfe73e622d80` was fast-forwarded into canonical `main`.
- **FL2 — unified practical local CLI: COMPLETE / MERGED.** Human-authorized candidate `e44e85358be9a1e72e0cd84c65d446eec5bd81c2` was fast-forwarded into canonical `main`. The unified CLI durably exposes inspect / preview / bounded write / verify for the already-evidenced Money / Party / Inventory operations without expanding capability ranges.
- **Post-FL2 acceptance: COMPLETE for retained exact inputs.** Current write eligibility remains tied to retained exact input-save SHA-256 values unless a family has separately proven reusable eligibility.
- **Money reusable qualification: PAUSED / INCOMPLETE.** Supporting work remains on the separate frozen branch `codex/money-reusable-qualification-20261007`; its candidate writer eligibility is not canonical.
- **Exact-v0.22 Party append + Inventory insertion: COMPLETE EXPERIMENTALLY / ADOPTED.** Exact-input proofs passed load, normal SAVE and cold reload without broadening reusable eligibility.
- **Exact-v0.22 composed Party append + Antidote insertion GUI transaction: COMPLETE EXPERIMENTALLY / ADOPTED.** The combined exact-root output passed independent composition checks, one normal SAVE/cold reload, and GUI/core byte equality.
- **Localhost v0.22 GUI experimental slice: COMPLETE.** The bounded slice described below provides inspection, preview and verified separate downloads under the existing FL2 and exact-input creation gates.

The primary practical gap is now **reusable eligibility on naturally progressed exact-v0.22 owner saves**. The forward critical path is R1 reusable-save eligibility -> R2 practical reusable core -> R3 continuous-use GUI closure, as defined in `docs/decision-record.md`.

## Exact v0.22 Fast Lab profile

Current exact private build evidence is keyed to:

- upstream commit `ddd054d46fc1bd0555badf738572620b1ee4670d`
- package SHA-256 `d22bc25d7427899e8d0b2e29e7fd6b604602781167b78cfa8a90c8a2da9e4060`
- owned FireRed source SHA-256 `1e4af44b0c75cc8649bfb8649dc4ae5850bf5358bd6b9cd0bf779c99f9db1486`
- verified private PokemonStart v0.22 ROM SHA-256 `6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`

No ROM, save, package, BPS/IPS, executable payload, or copyrighted game asset is stored in Git.

### Experimental v0.22 capabilities

Current Fast Lab evidence includes:

- **Money:** disposable output edit with verifier acceptance and live v0.22 confirmation.
- **Party:** friendship, IV/stat recalculation, move replacement/PP handling, bounded level/EXP editing, bounded Bulbasaur→Ivysaur species transformation, and a composed multi-field edit whose complete 100-byte live party record matched the offline output.
- **Inventory:** existing Potion slot 0, encryption key `0`, quantity `1→2` observed across retained normal-save slots; a separate-output `2→3` edit was accepted by the verifier and observed live under v0.22.
- **Ability:** selector storage is decoded, but practical resolved-ability writing remains unsupported.

These are **Fast Lab experimental** claims only. They do not establish arbitrary-save support, nonzero-key support, broad item/pocket support, broad species/move/level support, another PokemonStart version, normal-save lifecycle support for each field, or public-release readiness.

## Exact-input creation + GUI experimental slice

This slice provides two **Fast Lab experimental** operations on the fresh
exact-v0.22 proof root only: Party count 3->4 by copying the complete existing
slot0 record into slot3, and Antidote ID14 x1 into the game-observed regular slot2
without changing Money. Both passed load, normal SAVE and cold reload.
Other saves, templates, items, slots and quantities remain unsupported.
The exact-root Party append + Antidote insertion composed transaction also has
one normal SAVE + cold-reload proof and GUI/core byte equality. It is Fast Lab
experimental, exact-input bounded, not Stable, and provides no reusable
progressed-save eligibility. See
[the composition evidence](docs/v022-composed-gui-transaction-progress.md).
Existing FL2 gates are unchanged; the paused Money reusable candidate is not
included.

The localhost NiceGUI prototype provides upload, inspection, semantic/byte
preview and verified separate downloads, bound only to 127.0.0.1:

```bash
.venv/bin/python pokemonstart_v022_web.py --rom /path/inside/PokemonStart-private/exact-v022.gba
```

Use the existing `requirements-m4-ui.txt` environment. See
[`docs/v022-creation-proof-progress.md`](docs/v022-creation-proof-progress.md)
and the sanitized evidence JSON for exact identities, proof limits and
validation. This slice remains exact-input bounded and does not establish Stable
support or public-release readiness.

## Shared safeguards

Both lanes retain the same non-negotiable boundaries:

- source ROMs and source saves remain immutable;
- writers create new output files and refuse source overwrite;
- malformed, ambiguous, and unsupported inputs fail closed;
- private/protected artifacts stay out of Git and public distribution;
- exact-build support is tracked by capability profile rather than inferred across versions;
- public/generic support claims require later review;
- emulator live-save state is never automatically replaced.

## M5A Stable Money

Pinned CFRU-JP source places the stored money word at SaveBlock1 offset `0x0290` and the SaveBlock2 encryption key at offset `0x0F20`:

```text
money = LE32(active logical section 1 @ 0x0290)
        XOR LE32(active logical section 0 @ 0x0F20)
```

The retained v0.15 lineage has two consecutive normal-save round trips:

1. `3000 -> 9,999,999`
2. `9,999,999 -> 1,234,567`

The current bounded Stable FAMILY remains limited to its recorded v0.15 build/key/journal/macOS boundary and is not GUI-exposed.

## Run the verifier

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000` flash bytes or `0x20010` with a 16-byte opaque emulator footer and fails closed on malformed/ambiguous/inconsistent layouts.

## Canonical records

- `docs/decision-record.md` — controlling North Star, terminal goal, current milestone/authority state, and forward critical path
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md` — historical/adopted post-FL2 acceptance and reusable-envelope plan
- `docs/money-reusable-envelope-qualification.md` — historical bounded reusable-Money qualification record; currently paused/incomplete
- `docs/v022-creation-proofs-and-gui-prototype.md` — authorization/scope record for the exact-v0.22 Party append, Inventory insertion and localhost GUI experimental slice
- `docs/v022-composed-gui-transaction-proof.md` — scope record for the exact-root composed Party append + Antidote insertion GUI transaction proof
- `docs/v022-composed-gui-transaction-progress.md` — composed proof/publication record
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md` — historical FL2-G0 and prior terminal-goal refinement
- `docs/fl2-g0-reconciliation.md` — merged durable-baseline reconstruction record
- `docs/fl2-unified-cli-candidate.md` — merged FL2 implementation/validation record
- `docs/fast-lab-two-lane-adoption.md` — controlling two-lane strategy and current v0.22 Fast Lab evidence
- `docs/evidence.md`
- `docs/m4-completion.md`
- `docs/m5a-second-roundtrip-and-money-family.md`
- `docs/m5a-family-closure-and-provenance-continuity-design.md`

## Current non-claims

Unless separately proven and authorized, the project does not claim generic arbitrary-save support, broad PokemonStart-version compatibility, nonzero-key Fast Lab support, Stable v0.22 support, resolved-ability editing, general Inventory insertion/deletion/reordering, Pokédex editing, event/story/quest editing, public/LAN delivery, public release guarantees, or reusable write eligibility for naturally changed owner saves.
