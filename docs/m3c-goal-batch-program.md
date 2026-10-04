# M3C goal-driven batch program — 2026-10-05

## Status

**AUTHORIZED / IN PROGRESS.**

This document records the bounded M3C execution contract adopted after M3C-F1. It changes process granularity, not the North Star or fail-closed writer boundary.

## Goal

Advance the retained PokemonStart v0.15 lineage from isolated field proofs toward a useful bounded party-edit capability set while minimizing repetitive human round trips.

## Operating rule

**Field-specific evidence remains mandatory; human game evidence is grouped by coupling/risk class.**

For every candidate field/group, retain:

- source-backed storage/layout evidence;
- validity/range/catalog rules;
- coupling classification;
- explicit allowed byte-diff envelope;
- checksum consequences;
- synthetic/property tests;
- exact private-copy differential proof;
- independent post-generation verification;
- a capability status of `PROVEN`, `CANARY_READY`, `BLOCKED`, or `UNSUPPORTED`.

A batch may combine only fields whose coupling evidence is compatible. The batch must generate:

1. individual variants for isolation;
2. one combined canary;
3. a machine-readable or deterministic manifest of intended semantic edits, exact byte diffs, checksum changes, input/output hashes, and preserved regions.

If the combined canary fails, do not infer which field failed. Use the prepared variants/bisection path.

## Risk classes

### L — direct / low-coupling

Examples may include bounded scalar/cosmetic fields whose stored value is directly consumed and does not require recomputing derived party state. Source/range checks are still required.

### M — catalog / encoding dependent

Examples include values whose representation is direct but whose safe value domain depends on the exact build/profile or encoding table. Require a target-profile catalog/encoding proof before mutation.

### C — derived-state coupled

Examples include IV/EV/nature/hyper-training/stat families, EXP/level/HP/stats, and moves/PP/PP-Up. Treat the coupled state as one capability group and recompute/validate all derived values required by game semantics.

### H — identity / form / broader-state

Species/form/ability/PID-like identity or other changes with broad game-state implications require a separate research gate unless independent evidence reduces them to a narrower class.

## Evidence order

1. current repository `main`;
2. pinned CFRU-JP upstream source;
3. retained private PokemonStart v0.15 inputs and outputs, outside Git;
4. public CFRU-family editors such as PUSE as supporting/reference evidence only;
5. other public implementations only when independently useful and license-compatible.

No public reference implementation is PokemonStart authority.

## Required transaction invariants

- never overwrite input;
- exact profile/preflight before mutation;
- locate active logical section from verified metadata;
- active-slot/counter parity must hold;
- preserve counters, IDs, signatures, physical section permutation, inactive slot, sectors 28–31, parasite tails, external footer, and all unrelated bytes unless separately proven otherwise;
- recompute only affected checksum(s);
- every changed byte must map to an authorized semantic field or required checksum;
- re-run verifier and field/group validators after generation;
- re-hash input after output generation to prove immutability.

## Human interaction policy

Do not pause after every successful scalar proof. Continue autonomously through research, implementation, tests, private differential proofs, and preparation of all variants within the authorized batch program.

Pause only when:

- a representative game/emulator canary is required;
- private input necessary for the next proof is unavailable;
- evidence leaves a consequential unresolved design/safety choice;
- work would cross into arbitrary/non-lineage saves, M4 GUI, box/bag editing, overwrite mode, protected-data publication, or another unauthorized scope.

## Initial execution target

Start with the largest defensible low-coupling party batch on the fresh M3C-F1 round-trip save. Prefer useful fields and avoid adding fields merely because their offsets are easy. Use the M3C-F1 returned resave as the next private lineage anchor when its exact hash/profile re-verifies.

Then research catalog-dependent and derived-state groups. A high-coupling group must not be smuggled into the low-coupling canary simply to reduce the number of human interactions.

## Stop / completion surface

At the next human gate, present:

- capability matrix;
- exact input lineage and profile;
- source/reference evidence per field/group;
- test results;
- individual-variant hashes;
- combined-canary hash and exact manifest;
- independent verification result;
- blocked/unsupported capabilities and why;
- minimal game-round-trip instructions;
- batch PR state.

Final merge of new M3C batch capability remains separately authorized.
