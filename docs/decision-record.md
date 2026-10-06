# Canonical decision record — 2026-10-07

GitHub `main` is the only durable canonical authority for this project. Detailed proof history lives in the linked evidence/scope records; this file intentionally keeps only the current decision state.

## North Star

Provide a **user-operable, recoverable, profile-bounded local editor for the owner's PokemonStart saves** that can inspect supported saves, preview supported edits, preserve original inputs, write only separate outputs, explain changes, verify outputs, and reject unsupported cases rather than guess.

The goal does not require all versions, all fields, PKHeX parity, generic CFRU support, or Stable promotion of every Fast Lab capability.

## Current position

### Stable Lane

- M1–M4: complete.
- M5A Money: implementation + lifecycle evidence complete; Stable milestone adoption still incomplete.

### Fast Lab

- FL0 exact-v0.22 preparation: complete.
- FL1 practical bounded editing: complete experimentally.
- FL2 durable baseline + unified CLI: complete / merged.
- Money reusable-envelope qualification: paused / incomplete; not canonical writer capability.
- Exact-v0.22 Party append + Inventory insertion + localhost GUI: complete experimentally / adopted.
- Exact-v0.22 composed Party append + Antidote insertion GUI transaction: complete experimentally / adopted.

The composed operation remains **exact-input bounded, Fast Lab experimental, and not Stable**. It proves only the already-evidenced Party append and Antidote insertion together from the adopted proof root. It does not establish generic composition or reusable progressed-save eligibility.

Canonical proof/scope records:

- `docs/v022-creation-proofs-and-gui-prototype.md`
- `docs/v022-creation-proof-progress.md`
- `docs/v022-composed-gui-transaction-proof.md`
- `docs/v022-composed-gui-transaction-progress.md`
- `docs/v022-composed-gui-transaction-evidence.json`
- `docs/fast-lab-v022-capability.json`

## Shared safety contract

- source ROMs and saves remain immutable;
- writers create separate outputs only;
- malformed, ambiguous, or unsupported inputs fail closed;
- protected/private artifacts stay out of Git;
- capability support is exact-build/profile bounded;
- editor diffs remain explainable and outputs re-verify;
- emulator live-save state is never automatically overwritten;
- Fast Lab evidence does not imply Stable support.

## Current authorization boundary

Canonical code may be used only within its existing gates, including the adopted exact-root single and composed creation operations and localhost GUI.

No further capability expansion is currently authorized. In particular, this record does not authorize:

- applying creation operations to naturally progressed saves;
- generalized reusable eligibility;
- arbitrary Pokémon synthesis/templates;
- arbitrary item IDs/quantities/slots/pockets;
- Money or generic multi-operation composition;
- nonzero-key support;
- broader PokemonStart builds/versions;
- Stable promotion;
- public/LAN GUI exposure;
- adoption of the paused Money reusable candidate;
- publication of protected data.

## Next decision surface

The main unresolved practical limitation is **reusable eligibility on naturally progressed exact-v0.22 owner saves**.

Before starting that or any other expansion, fresh-read current `main`, reconstruct the current evidence, and choose the cheapest uncertainty-reducing next proof. Any broader writer capability requires a separate Human authorization.
