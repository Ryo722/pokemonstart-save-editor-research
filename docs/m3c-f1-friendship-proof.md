# M3C-F1 bounded friendship proof — 2026-10-05

## Status

**BOUNDED EVIDENCE COMPLETE; MERGE AUTHORIZATION PENDING.**

The exact retained private PokemonStart v0.15 lineage proof for `party[0] friendship 50 -> 51` completed synthetic preflight, sealed private preflight, proof-file generation, human game load + normal save, and read-only verification of the returned resave.

## Exact private fingerprint

- input SHA-256: `d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282`;
- initial slot state: slot 1 counter 3 active, slot 0 counter 2 inactive;
- field diff: `0x12061: 32 -> 33`;
- section-1 checksum: `0x1C33 -> 0x1D33`, stored byte diff `0x12FF7: 1C -> 1D`;
- complete diff count: 2 bytes;
- proof-output SHA-256: `10f13894cab59922989e2b0508b41f2eef276e8c45b2778d6e6b1a309d2f98ae`;
- synthetic implementation preflight: `6/6 PASS`;
- no private `.sav` committed.

## Human game round trip — PASS

Returned private resave:

- size `131,088` bytes;
- SHA-256 `6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600`;
- flash SHA-256 `f3f1069f632a2bae691a949622eb1f97e9328f1cebd15f93907b926120f683e5`;
- slot 0 valid counter 4;
- slot 1 valid counter 3;
- slot 0 uniquely active and parity `0 == 4 % 2` PASS;
- active logical section 1 physical sector 5;
- friendship 51 retained;
- active party record byte-identical to the proof output's active record: species 1, level 5, EXP 134, ball 3, moves `33/45/0/0`, PP `35/40/0/0`, EVs zero, IVs `31/29/26/23/27/29`, HP `21/21`, stats `9/11/10/13/12`;
- proof-output slot 1 preserved byte-for-byte;
- sectors 28–31 preserved byte-for-byte;
- sector 30/31 hashes remain `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525` / `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7`;
- footer changed to SHA-256 `8ef79aef38d8658aa715ea718edef3246c6af1fc3147990a4f3b3209ae585c69`, consistent with the established preservation-only rule across later game/emulator resaves.

## Verdict

**M3C-F1 COMPLETE for this exact bounded private-lineage friendship proof, pending only a separate merge decision.**

This does not establish another field, arbitrary/non-lineage save support, a general writer, overwrite behavior, GUI readiness, box editing, or protected-data publication.

M3C-F1 also creates a natural roadmap reassessment point: the one-field proof loop works, but further field expansion should evaluate a bounded higher-throughput batch/goal-driven process rather than mechanically repeating a full human gate for every scalar field.
