# M3B bounded same-field proof candidate — 2026-10-05

## Status

**AUTHORIZED; SEALED PRIVATE PREFLIGHT PASS; HUMAN GAME ROUND TRIP PENDING.**

M3B is not complete. The exact private candidate has now been derived, independently checked against the M3A transaction envelope, sealed into the repository writer, and emitted as one brand-new private proof output. A human game load + normal-save round trip and read-only verification of the resulting resave remain required before M3B completion or merge authorization.

## Exact authorized scope

- provenance profile: retained private PokemonStart v0.15 M2 lineage only;
- exact input SHA-256: `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac`;
- starting state: both save slots valid; active physical slot 0 at counter 2; inactive slot counter 1;
- field: `party[0]` HP IV only;
- transformation: `30 -> 31`;
- output: a new file only;
- preserve all counters, section IDs/signatures, physical section permutation, inactive slot, sectors 28–31, parasite tails, optional 16-byte footer, and all non-target bytes;
- recompute only the checksum covering the changed logical section 1 payload;
- require the complete exact diff and output hash to match the sealed candidate.

Explicitly out of scope: arbitrary saves, other PokemonStart builds/profiles, new editable fields, box editing, counter/slot rewriting, section reordering, save overwrite, GUI work, or protected-data publication.

## Sealed exact candidate fingerprint

The authorized private input was freshly available to the execution environment and independently re-hashed before mutation.

| Item | Sealed value |
| --- | --- |
| Input size | `131,088` bytes |
| Input SHA-256 | `c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac` |
| Active slot / counter | slot `0` / counter `2` |
| Inactive counter | `1` |
| Active slot parity | `0 == 2 % 2` — PASS |
| Logical section 1 physical sector | `3` |
| Starting IVs | `30/29/26/23/27/29` |
| Target IVs | `31/29/26/23/27/29` |
| Data diff | `0x3080: BE -> BF` |
| Section 1 checksum diff | `0x3FF6: 20 -> 21` |
| Complete diff count | `2` bytes |
| Output SHA-256 | `cf2ca33a303b6409300ac4032c7c47efd9859562bc06fe18e89481bb93ea5f1f` |

The two-byte diff is sealed in `EXPECTED_DIFFS`, and the output hash is sealed in `EXPECTED_OUTPUT_SHA256`. Production writing therefore succeeds only for this exact private candidate fingerprint.

Evidence level: **local private-input verification + sealed repository candidate evidence**. No private save bytes are committed.

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
- same active slot and counters after mutation;
- identical section metadata/physical permutation after mutation;
- same party count and all non-HP IVs;
- identical footer and sectors 30/31.

Because complete diff confinement is enforced, inactive-slot bytes, Hall of Fame sectors 28/29, parasite tails, and every other non-target byte are necessarily preserved as well.

## Private preflight result

The fresh private input matched every M3A profile condition:

- both slots validate completely;
- slot 0 counter 2 is uniquely newest;
- slot/counter parity passes;
- logical section 1 is in physical sector 3;
- party count is 1;
- `party[0]` IVs are `30/29/26/23/27/29`;
- sector 30 SHA-256 is `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525`;
- sector 31 SHA-256 is `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7`;
- the 16-byte opaque footer SHA-256 is `0f5e9be128e35fb5926268e15f441e442ff54ab712ba7fa50418761a4170ed0f`.

After applying only the authorized transformation and recomputing logical section 1's checksum:

- all 28 ordinary save-slot sectors still validate;
- active slot and both counters are unchanged;
- inactive slot is byte-identical;
- sectors 28–31 are byte-identical;
- the optional 16-byte footer is byte-identical;
- the complete file diff is exactly the sealed two bytes above;
- resulting IVs are `31/29/26/23/27/29`;
- the input SHA-256 remains unchanged after output creation;
- the new output is exactly `131,088` bytes with the sealed output SHA-256.

One private proof output was created at a new path only. It is not committed or published through GitHub.

## Synthetic implementation preflight

The synthetic test contract was updated for the sealed state. A local no-private-data sealed-state harness exercised the six repository test behaviors and passed **6/6**:

1. exact bounded sealed constants;
2. derive against two valid rotated slots while remaining inside the field/checksum envelope;
3. reject an unrelated synthetic candidate against the private seal;
4. reject active-slot/counter parity mismatch;
5. reject wrong starting HP IV;
6. allow a synthetically sealed new-file write while preserving input and refusing overwrite semantics.

No `.sav` fixture is committed. GitHub Actions is not the evidence source for this pass; this is a local synthetic preflight.

## Required human round-trip gate

The next step is intentionally human-visible and bounded:

1. load the generated private M3B proof output in the same PokemonStart v0.15 environment;
2. confirm the save loads normally;
3. perform one normal in-game save;
4. return the resulting resave for read-only verification;
5. verify both slots, counter transition, retained HP IV 31, unrelated party invariants, sectors 28–31, and footer handling;
6. only after that evidence may M3B completion / candidate merge be considered.

The current branch/PR must remain unmerged until that round-trip evidence is reviewed. No broader writer capability, new field, arbitrary-save support, or M3C work is authorized by this preflight.
