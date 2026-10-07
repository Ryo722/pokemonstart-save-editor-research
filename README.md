# PokemonStart save editor research

Evidence-first research and tooling for a user-controlled PokemonStart save editor. Protected game data is not part of this repository.

## Current strategy

The project uses a canonical **two-lane model**:

- **Stable Lane** — durable supported capabilities require stronger lifecycle/provenance/recovery/delivery evidence and a separate adoption decision.
- **Fast Lab Lane** — exact-build experimental capabilities may be developed rapidly on private, recoverable save copies while preserving immutable originals, separate outputs, explainable diffs, verifier acceptance, and exact-build live confirmation where practical.

Fast Lab evidence does **not** imply Stable support.

The controlling strategy/next-work records are:

- `docs/decision-record.md`
- `docs/v022-practical-product-sprint.md`
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md`
- `docs/v022-creation-proofs-and-gui-prototype.md`
- `docs/v022-composed-gui-transaction-proof.md`
- `docs/fast-lab-two-lane-adoption.md`

## North Star

For each currently supported PokemonStart build/profile, the owner should be able to take a save produced through ordinary gameplay, safely apply supported edits locally, return to the game, continue playing and saving, and later edit the newly progressed save again **without preregistering each individual save hash**.

Unsupported builds, malformed or ambiguous saves, unsupported save states, and unsupported operations must fail closed rather than be guessed.

The project optimizes for **continuous owner use on a supported current build**, not for maximizing isolated proofs or field count.

## Terminal goal

For the currently selected PokemonStart build/profile (currently exact v0.22), provide a **user-operable, recoverable local editor** that supports repeated:

`edit -> play/save -> ordinary progress -> save -> edit`

cycles on naturally progressed owner saves using build-specific and capability-specific eligibility predicates rather than exact-save-hash allowlists.

The practical terminal product is a PKHeX-familiar local GUI for a useful **Party / Items / Money** slice. It preserves original inputs, writes only separate outputs, previews semantic changes, verifies generated outputs, and rejects unsupported cases rather than guess.

Terminal completion does **not** require all PokemonStart versions, all save fields, PKHeX parity, generic CFRU support, public release, Box editing, arbitrary Pokémon synthesis, or Stable promotion of every Fast Lab capability.

## Current position

### Stable Lane

- **M1 — reproducible read-only verifier: COMPLETE.**
- **M2 — exact one-field HP-IV writer proof: COMPLETE.**
- **M3A — reusable write-envelope characterization: COMPLETE.**
- **M3B — bounded same-field transaction proof: COMPLETE.**
- **M3C — bounded party-field expansion: COMPLETE.**
- **M4 — bounded usable-editor first slice: COMPLETE.**
- **M5A — Money: FAMILY IMPLEMENTATION + LIFECYCLE CLOSURE EVIDENCE COMPLETE; MILESTONE ADOPTION NOT YET COMPLETE.**

Stable provenance work remains separate and is not on the current practical terminal critical path.

### Fast Lab

- **FL0 — exact-build private ROM preparation + harness: COMPLETE.**
- **FL1 — practical core editing slice: COMPLETE EXPERIMENTALLY.** Exact PokemonStart v0.22 evidence includes bounded Money editing, practical/composed Party editing, and bounded Inventory editing.
- **FL2-G0 — durable Fast Lab baseline reconciliation: COMPLETE / MERGED.**
- **FL2 — unified practical local CLI: COMPLETE / MERGED.**
- **Post-FL2 private acceptance: COMPLETE for retained exact inputs.**
- **Frozen reusable-Money work:** preserved on `codex/money-reusable-qualification-20261007` as reference/evidence only until reconciled against current `main`.
- **Exact-v0.22 Party append + Inventory insertion + localhost GUI: COMPLETE EXPERIMENTALLY / ADOPTED.**
- **Exact-v0.22 composed Party append + Antidote insertion GUI transaction: COMPLETE EXPERIMENTALLY / ADOPTED.**

The remaining practical gap is converting exact-canary capabilities into a reusable product for naturally progressed exact-v0.22 saves.

The authorized forward sprint is:

- **R1 — reusable exact-v0.22 eligibility**
- **R2 — practical reusable Party / Items / Money core**
- **R3 — PKHeX-familiar localhost GUI**
- **R4 — two-cycle naturally-progressed-save product acceptance**

See `docs/v022-practical-product-sprint.md` for the exact scope and stop conditions.

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
- **Party:** friendship, IV/stat recalculation, move replacement/PP handling, bounded level/EXP editing, bounded Bulbasaur→Ivysaur species transformation, and composed multi-field editing.
- **Inventory:** bounded existing-item quantity editing plus exact-input insertion evidence.
- **Ability:** selector storage is decoded, but practical resolved-ability writing remains unsupported.

These remain experimental until capability-specific reusable predicates and lifecycle evidence are established.

## Localhost GUI

The existing NiceGUI prototype provides upload, inspection, preview and verified separate downloads, bound only to `127.0.0.1`:

```bash
.venv/bin/python pokemonstart_v022_web.py --rom /path/inside/PokemonStart-private/exact-v022.gba
```

The R3 sprint work converts this research-oriented operation/JSON surface into the practical Party / Items / Trainer editor UI while retaining the same localhost and verified-output safety model unless fresh evidence justifies otherwise.

## Product sprint candidate (not adopted)

The candidate practical GUI is available with ordinary Party / Items / Trainer
controls and composed verified downloads:

```bash
.venv/bin/python pokemonstart_v022_product_web.py --rom /path/inside/PokemonStart-private/exact-v022.gba
```

The candidate supports reusable Money, bounded existing Party edits, Potion
quantity, and Antidote x1 insertion/removal for the exact observed regular-item
record shape. A Human-verified two-cycle GUI/game workflow is recorded. The
bounded candidate is ready for fresh-context independent review; it is not
canonical adoption or Stable support. Pocket capacity, general item mapping and
Give All Items remain unqualified. See [candidate limits and
evidence](docs/v022-product-candidate.md).
The prior research GUI and bounded APIs retain their existing behavior.

## Shared safeguards

Both lanes retain the same non-negotiable boundaries:

- source ROMs and source saves remain immutable;
- writers create new output files and refuse source overwrite;
- malformed, ambiguous, and unsupported inputs fail closed;
- private/protected artifacts stay out of Git and public distribution;
- exact-build support is tracked by capability profile rather than inferred across versions;
- emulator live-save state is never automatically replaced;
- public/generic support claims require later review.

## Run the verifier

```bash
python3 pokemonstart_save_verifier.py /path/to/private/save.sav
```

The verifier accepts only `0x20000` flash bytes or `0x20010` with a 16-byte opaque emulator footer and fails closed on malformed/ambiguous/inconsistent layouts.

## Canonical records

- `docs/decision-record.md` — controlling North Star, terminal goal, current milestone/authority state, and forward path
- `docs/v022-practical-product-sprint.md` — authorized R1–R4 exact-v0.22 product sprint scope
- `docs/post-fl2-acceptance-and-reusable-envelope-plan.md` — historical/adopted post-FL2 acceptance and reusable-envelope plan
- `docs/money-reusable-envelope-qualification.md` — historical bounded reusable-Money qualification record
- `docs/v022-creation-proofs-and-gui-prototype.md` — exact-v0.22 Party append, Inventory insertion and localhost GUI scope record
- `docs/v022-composed-gui-transaction-progress.md` — composed proof/publication record
- `docs/fast-lab-v022-capability.json` — exact-v0.22 capability evidence/profile
- `docs/evidence.md`

## Current non-claims

Unless separately proven and adopted, the project does not claim generic arbitrary-save support, broad PokemonStart-version compatibility, Stable v0.22 support, resolved-ability editing, generic inventory mutation across unknown pockets, Pokédex/story/quest/event editing, public/LAN delivery, public release guarantees, Box editing, or PKHeX parity.
