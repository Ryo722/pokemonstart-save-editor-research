# FL2-G0 durable Fast Lab baseline reconciliation — 2026-10-06

Status: **candidate prepared for Human review; not merged or pushed**

## Canonical basis and local source

- Fresh canonical base: `13ecd37cc8817d5a5a3d4f9e38c8ba5f51f8b022` (`origin/main`).
- Local experimental source: `codex/fast-lab-v022`, ending at `74530aaeb04cdda44ec1e146ac0a8caaf5e8eee6`.
- Local source ancestry diverged before the current canonical FL2-G0 decision. It was treated as experimental input, not as the candidate base.
- The source chain needed for FL0/FL1 reconstruction is `6d6e44abf15b5fa86db1788ddcb2bc36c4a7d409` (mGBA harness), `a5205d8dd416553ba6d8487b2a6cc4f9582406a1` (repeatable bootstrap), `886a6e6e85ef6abdd78cedcea2b2133540d08242` (private build preparation), `e2a3c3166d12dc51fa751c9e5571f7f6b09d9228` / `bc82c8cdb13836a7868d402249591b8f6c2a1716` (package/profile identity), `bc6c6f1ccc816d8e1ce8ec638919328e2111bc86` (Money), `b6c0a5cee4a3c41b36f3666b1210c9f0c1a48a94` / `0cdc86f70bdc9da8788bb02f2e600cf0829442a4` / `6c2d1864669a45b3c75676da1d0a015f9cff9759` / `18d710119a814b8908fdb758652a32c78e3a94ec` (Party), and `74530aaeb04cdda44ec1e146ac0a8caaf5e8eee6` (Inventory). The reconciliation uses reviewed file changes rather than importing the stale branch history wholesale.

## Durable reconstruction set

The candidate contains the exact-v0.22 build profile and private preparation/inspection tools, bounded mGBA harness and Lua bridge, Money/Party/Inventory experimental readers and writers, the Fast Lab party stat calculator, verifier ability-selector decoding, and synthetic tests. `docs/fast-lab-v022-capability.json` is the machine-readable exact build and capability profile; `docs/fast-lab-v022-package-inspection.md` and `docs/local-mgba-research-harness.md` describe how the private inputs and harness are reconstructed without storing them.

Stable M3C's derived-stat writer is byte-for-byte unchanged from the canonical base. The Fast Lab calculator lives in `pokemonstart_fastlab_v022_stats.py`; it is restricted to the evidenced Modest Bulbasaur/Ivysaur level 5/6 calculations. The reusable Party editor accepts only the exact retained canary save and the recorded transitions. Ball, markings, nature mint, held-item writes, other IV/EV values, other move changes, and unproven combinations remain rejected. These limits retain the profile's `inherited_candidate_only` classification and do not convert those fields into FL1 capabilities.

All Fast Lab operations remain labeled experimental and gated by the exact v0.22 ROM identity. The canonical FL1 scope remains Money, practical/composed Party editing, and the single existing Potion quantity case. The recorded no-claims and protected-data boundary in the canonical adoption documents continue to apply.

## Deliberate exclusions

- `docs/fast-lab-milestone-boundary-audit.md` is omitted because it predates the adopted FL2-G0 boundary and duplicates an older roadmap snapshot.
- No ROM, save, `.pks`, BPS/IPS, executable payload, copyrighted asset, or protected bytes are present in this candidate.
- No new field research, capability range expansion, Stable adoption, unified CLI work, merge, or push is part of this reconciliation.

## Review and verification record

Candidate parent and exact commit are recorded in the execution handoff/final report. The full candidate diff must be reviewed along with focused and full test results, Python compilation, profile JSON parsing, whitespace checks, protected-artifact scan, and secret scan before requesting Human merge authorization.
