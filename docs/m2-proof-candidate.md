# M2 bounded one-field writer proof — candidate

Date: 2026-10-04

Base canonical `main`: `709dee262d9e3e54a64faa228fb4db61203131c0`

## Authorization and scope

The user authorized continuing from the M1-complete checkpoint into M2. This candidate is deliberately narrower than a general save writer.

It may only:

- accept the exact known PokemonStart v0.15 before-test/original input SHA-256 `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`;
- edit `party[0]` HP IV from 31 to 30;
- recompute the active slot's logical section 1 checksum;
- write to a new path that does not already exist.

It must refuse unknown input hashes, an already-modified HP IV, input/output path identity, an existing output file, non-allowlisted byte differences, or any post-write verification failure. It does not change slot counters, create a new slot, expose arbitrary IV values, edit other fields, overwrite an input save, or implement GUI behavior.

## Candidate implementation

`pokemonstart_hpiv_proof_writer.py` reuses the merged M1 verifier before and after mutation. For the exact known input it requires the output to match all of these retained proof constants:

- expected output SHA-256: `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`;
- exact byte diff `0x10080: BF -> BE`;
- exact byte diff `0x10FF6: 62 -> 61`;
- active slot remains slot 1;
- only HP IV changes in the six-IV tuple, from `31/29/26/23/27/29` to `30/29/26/23/27/29`;
- opaque 16-byte emulator footer is unchanged;
- sectors 30 and 31 are unchanged.

The writer uses exclusive-create mode (`xb`) and refuses both the input path and any existing destination. It re-hashes the input after the write and removes a newly-created output if a write/verification exception occurs.

## Synthetic tests

A six-test writer suite covers:

1. fixed proof constants;
2. HP-IV/checksum-only mutation with verifier invariants;
3. rejection of an unknown input hash;
4. rejection when HP IV is not 31;
5. refusal to overwrite input or an existing output;
6. successful creation of a separate output while preserving the input.

Local execution on 2026-10-04: `python3 -m unittest discover -s tests -v` for the new writer suite -> **6/6 PASS**. The existing M1 verifier implementation is unchanged.

Evidence level: **synthetic implementation/proof evidence**.

## Private-input reproduction

The candidate algorithm was executed locally against the privately supplied `PokemonStart_v0.15_BEFORE_HPIV_TEST.sav` and byte-identical original backup. Neither private input is stored in Git.

Observed result:

- input SHA-256 before and after execution: `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`;
- output SHA-256: `569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc`;
- active slot: 1;
- logical section 1 physical sector: 16;
- exact diff count: 2 bytes;
- `0x10080: BF -> BE`;
- `0x10FF6: 62 -> 61`;
- parsed output IVs: `30/29/26/23/27/29`;
- 16-byte footer preserved;
- sector 30 preserved with 23 nonzero bytes;
- sector 31 preserved with zero nonzero bytes.

The repository-generated output is byte-for-byte identical to the retained private `PokemonStart_v0.15_TEST_HPIV30.sav` that underlies the previously observed successful game load and subsequent normal resave. This is a strong equivalence bridge to the historical round-trip evidence, but the candidate does not treat that as permission to broaden writer capability.

Evidence level: **local private-input verification** plus byte-identity comparison to the retained prior test artifact.

## Current gate

This branch is an M2 candidate only. Canonical `main` remains M1-complete/read-only until a separate human authorization merges the candidate.

The cheapest additional confidence check, if desired before merge, is to load the newly repository-generated private output in the game and perform one normal save. A fresh round trip is not required to establish byte identity with the retained already-round-tripped artifact, but it would remove the remaining provenance/causal ambiguity at negligible technical scope.

Not authorized by this candidate: general save writing, other IV values, other party members, EV/level/EXP/move/item writes, box editing, GUI work, save overwrite, protected-data publication, or support for other PokemonStart builds.
