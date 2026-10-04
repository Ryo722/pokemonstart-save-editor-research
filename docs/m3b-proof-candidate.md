# M3B bounded same-field proof candidate — 2026-10-05

## Status

**AUTHORIZED; IMPLEMENTATION PREFLIGHT STARTED; PRIVATE CANDIDATE NOT YET SEALED.**

This candidate is intentionally fail-closed. It cannot create a production proof output until the exact private input bytes have been used to derive and review the complete byte diff and output SHA-256, and those values have then been sealed into the candidate constants.

M3B is not complete. A later human game load + normal-save round trip remains required after a sealed repository-generated proof output exists.

## Exact authorized scope

- provenance profile: retained private PokemonStart v0.15 M2 lineage only;
- exact input SHA-256: `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
- starting state: both save slots valid; active physical slot 0 at counter 2; inactive slot counter 1;
- field: `party[0]` HP IV only;
- transformation: `30 -> 31`;
- output: a new file only;
- preserve all counters, section IDs/signatures, physical section permutation, inactive slot, sectors 28–31, parasite tails, optional 16-byte footer, and all non-target bytes;
- recompute only the checksum covering the changed logical section 1 payload;
- require a complete exact diff and output hash to be frozen before production file creation.

Explicitly out of scope: arbitrary saves, other PokemonStart builds/profiles, new editable fields, box editing, counter/slot rewriting, section reordering, save overwrite, GUI work, or protected-data publication.

## Candidate implementation

`pokemonstart_hpiv_m3b_proof_writer.py` separates two stages:

1. `derive_candidate_fingerprint(raw)` — exact-input-constrained, in-memory only. It verifies the M3A support envelope, computes the proposed `30 -> 31` bytes and checksum, re-verifies the output in memory, and reports the exact diff/output hash. It does not write a file.
2. `build_proof_output` / `write_proof_file` — hard-refuses while `EXPECTED_DIFFS` or `EXPECTED_OUTPUT_SHA256` are unset. Production output creation becomes possible only after the exact fingerprint is independently reviewed and sealed.

This split prevents the inability to access the private input in one environment from silently weakening the proof contract.

## M3A support-envelope checks carried into M3B

The candidate requires:

- exact known input SHA-256;
- both slots valid;
- active slot 0;
- active counter 2 and inactive counter 1;
- source-backed slot/counter parity `active_slot == active_counter % 2`;
- `party[0]` present with HP IV 30;
- canonical retained sector 30 hash;
- canonical retained sector 31 hash;
- canonical retained opaque-footer hash;
- target logical section found through verified metadata rather than fixed physical assumptions;
- complete diff confined to the IV word bytes plus containing checksum bytes;
- same active slot and counters after the in-memory mutation;
- identical section metadata/physical permutation after mutation;
- same party count and all non-HP IVs;
- identical footer and sectors 30/31.

Because complete diff confinement is enforced, inactive-slot bytes, Hall of Fame sectors 28/29, parasite tails, and every other non-target byte are necessarily preserved as well.

## Synthetic implementation preflight

A local no-private-data harness reproduced the current verifier rules and exercised the candidate against synthetic two-valid-slot saves, including a rotated physical section order. Result: **4/4 PASS**.

The exercised behaviors were:

- derive a same-field candidate from both-valid slots with active slot 0/counter 2 and a rotated section permutation;
- refuse production build while exact diff/output hash are unsealed;
- reject an active-slot/counter parity mismatch;
- reject the wrong starting HP IV;
- after synthetic sealing, create only a new output while preserving the input and refusing input/existing-output overwrite (covered within the sealed-write test).

The repository test file additionally separates the bounded-constant and derive-envelope assertions into dedicated cases. No `.sav` fixture is committed.

Evidence level: **independently reproduced synthetic implementation preflight** for the local harness; repository candidate source for the branch implementation.

## Current private-input blocker

The required private file is retained in the user's private Project/Library as `PokemonStart_v0.15(1).sav`, size `131,088` bytes, corresponding canonically to the M2 fresh round-trip lineage. During this M3B session the Files layer listed the file, but raw-byte materialization into the execution container was refused by the platform. A second private-Library working snapshot was also refused raw materialization.

Therefore this session has **not** re-hashed or re-parsed the private bytes and has **not** derived the exact M3B output SHA-256/diff. No private save bytes were published or committed.

This is an execution-environment access blocker, not evidence that the candidate passed private preflight.

## Required next proof step

Once the exact private input bytes are available to the execution environment:

1. independently re-hash the input and require `c103d8d3...67ac`;
2. run the current canonical verifier and M3B profile checks read-only;
3. run `--derive-only` to obtain the exact complete diff and output SHA-256 without creating a file;
4. independently review that fingerprint against the M3A envelope;
5. seal `EXPECTED_DIFFS` and `EXPECTED_OUTPUT_SHA256` in the candidate;
6. rerun the complete synthetic suite;
7. generate one brand-new private proof output and verify input immutability;
8. only then ask for the human game load + normal-save round trip;
9. read-only verify the resulting resave before M3B can be considered complete.

No later step may infer success from this preflight alone.
