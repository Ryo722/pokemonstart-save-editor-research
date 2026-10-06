# PokemonStart save editor research

Evidence-first research and tooling for a user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current strategy

The project uses a canonical **two-lane model**:

- **Stable Lane** — durable supported capabilities require stronger lifecycle/provenance/recovery/delivery evidence and a separate adoption decision.
- **Fast Lab Lane** — exact-build experimental capabilities may be developed rapidly on private, recoverable save copies while preserving immutable originals, separate outputs, explainable diffs, verifier acceptance, and exact-build live confirmation where practical.

Fast Lab evidence does **not** imply Stable support.

The controlling strategy/next-work records are:

- `docs/decision-record.md`
- `docs/fast-lab-two-lane-adoption.md`
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md`

## Terminal goal

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can inspect supported saves, preview supported edits, preserve the original input, write only a separate output, explain semantic/byte-level changes, verify the generated output, and reject unsupported cases rather than guess.

The goal is not unlimited feature accumulation. All versions, all fields, PKHeX parity, generic CFRU support, and Stable promotion of every Fast Lab capability are not required terminal conditions.

## Current position

### Stable Lane

- **M1 — reproducible read-only verifier: COMPLETE.**
- **M2 — exact one-field HP-IV writer proof: COMPLETE.**
- **M3A — reusable write-envelope characterization: COMPLETE.**
- **M3B — bounded same-field transaction proof: COMPLETE.**
- **M3C — bounded party-field expansion: COMPLETE.**
- **M4 — bounded usable-editor first slice: COMPLETE.**
- **M5A — Money: FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.**

Stable provenance work such as P-direct/P-reanchor remains separate and is not on the Fast Lab critical path.

### Fast Lab

- **FL0 — exact-build private ROM preparation + harness: COMPLETE.**
- **FL1 — practical core editing slice: COMPLETE EXPERIMENTALLY.** Exact PokemonStart v0.22 evidence includes bounded Money editing, practical/composed Party editing, and one bounded existing-item Inventory quantity edit.
- **FL2 — unified practical local CLI: NEXT MILESTONE.**
- **FL2-G0 — durable Fast Lab baseline reconciliation: NEXT EXECUTION STEP.** Before more CLI implementation accumulates, reconcile the already-existing local Fast Lab implementation/tests/profile into a fresh candidate based on current canonical `main`, review the full diff, run the full checks, and stop for Human merge authorization.

After FL2, profile broadening, GUI/delivery, and Stable promotion are **usage-driven alternatives**, not a fixed mandatory sequence.

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

- `docs/decision-record.md` — controlling milestone/authority state
- `docs/fl2-durable-baseline-and-terminal-goal-refinement.md` — controlling FL2-G0 and terminal-goal refinement
- `docs/fl2-g0-reconciliation.md` — candidate baseline reconstruction scope and review record
- `docs/fast-lab-two-lane-adoption.md` — controlling two-lane strategy and current v0.22 Fast Lab evidence
- `docs/evidence.md`
- `docs/m4-completion.md`
- `docs/m5a-second-roundtrip-and-money-family.md`
- `docs/m5a-family-closure-and-provenance-continuity-design.md`

## Current non-claims

Unless separately proven and authorized, the project does not claim generic arbitrary-save support, broad PokemonStart-version compatibility, nonzero-key Fast Lab support, Stable v0.22 support, resolved-ability editing, general Inventory insertion/deletion/reordering, Pokédex editing, event/story/quest editing, public/LAN delivery, or public release guarantees.
