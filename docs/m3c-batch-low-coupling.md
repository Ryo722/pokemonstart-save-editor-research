# M3C low-coupling batch — 2026-10-05

## Status

**HUMAN COMBINED CANARY PASS / MERGED INTO `main` VIA #10.**

The canonical merge commit `c9ce00718e385571497b3a1d47cb74d7fa5fb1e3` records the human game load/normal-save PASS. The returned private resave SHA-256 is `baf0b88fd357c54e17743601bbfa26b436db467a2fd78cd1d2c598fb714c50fa`: active slot 1/counter 5, with friendship 52, markings 1, and ball 11 retained. The checked party record, prior active slot, and sectors 28–31 were preserved. The external footer remains preservation-only across tool output, not normal game saves. This result is limited to the exact retained v0.15 lineage and three bounded fields.

This batch is the first execution of the authorized goal-driven M3C program. It uses the exact M3C-F1 human-round-trip resave as the next private lineage anchor and prepares individual variants plus one combined canary.

It does not authorize arbitrary saves, another PokemonStart build, held items, IV/EV/stat groups, moves/PP, species/form/ability, box/bag editing, GUI work, overwrite mode, or final merge without a later human decision.

## Input profile

- size: `131,088` bytes;
- SHA-256: `6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600`;
- both slots valid;
- active slot `0`, counter `4`; inactive counter `3`;
- active parity `0 == 4 % 2`;
- active logical section 1 in physical sector `5`;
- party count `1`;
- party[0]: species 1, level 5, EXP 134, friendship 51, markings 0, ball 3, moves 33/45/0/0, PP 35/40/0/0, EVs zero, IVs 31/29/26/23/27/29, HP 21/21, stats 9/11/10/13/12;
- sector 30 SHA-256 `335dbe9fd34f7d6baf1d3c4fdff8647b121872de1fdf779a0d1a49f9de068525`;
- sector 31 SHA-256 `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7`;
- opaque footer SHA-256 `8ef79aef38d8658aa715ea718edef3246c6af1fc3147990a4f3b3209ae585c69`.

Evidence level: **local private-input verification**. Private bytes remain outside Git.

## Field selection and source evidence

Pinned primary upstream remains `kapibarasan000/CFRU-JP` commit `e24a16fe39e27ae162faf5b78596d1f3df18489d`.

The pinned `include/pokemon.h` defines the in-save 100-byte `Pokemon` layout used by the verifier, including direct fields `markings`, `friendship`, and `pokeball`. `MAX_FRIENDSHIP` is 255.

Pinned `include/new/catching.h` defines ball IDs 0–26 as player ball types, with Poké Ball 3, Luxury Ball 10, Premier Ball 11, Dream Ball 26, and `NUM_BALLS = 27`. `src/scripting.c` accepts a ball edit only when `ballType < NUM_BALLS` before calling `SetMonData(... MON_DATA_POKEBALL ...)`.

Supporting reference only: `Zannael/PUSE` `master` commit `ff1074ce919515d3bdc0bb56b3995e20472c9a66` is an MIT-licensed Unbound/CFRU-family editor. Its party implementation independently treats happiness/friendship and ball as directly editable values and constrains ball IDs to 0–26. PUSE is not PokemonStart authority and its Unbound-specific save/checksum rules are not imported.

For markings, the pinned CFRU-JP structure gives a direct `u8 markings` byte. Vanilla Gen III `pret/pokeemerald` independently exposes `MON_DATA_MARKINGS` as a direct 8-bit get/set field. The batch uses only `0 -> 1`, the smallest nonzero bit, and makes no broader claim about all possible markings values.

### Capability classification

| Capability | Change | Class | Status before game canary | Rationale |
| --- | --- | --- | --- | --- |
| friendship | `51 -> 52` | L | CANARY_READY | same direct field family already proven by M3C-F1; one-step change |
| markings | `0 -> 1` | L | CANARY_READY | direct byte; smallest nonzero marking bit; no derived stat coupling identified |
| ball | `3 -> 11` | L | CANARY_READY | direct byte; target is source-defined valid Premier Ball; avoids Luxury Ball friendship behavior |

Held item is intentionally excluded because it participates in battle effects, form behavior, EV gain modifiers, and other semantics. IV/EV/nature/hyper-training, EXP/level, and moves/PP remain separate coupled groups.

## Exact private variants

All variants preserve slot counters, physical section permutation/metadata, inactive slot, sectors 28–31, parasite tails, footer, and every unrelated byte. Only logical section 1 checksum is recomputed.

### Friendship individual

- semantic: `party[0].friendship 51 -> 52`;
- output SHA-256: `75e3c7f1afcdd49d6c3678ae729e308b98563ec39ad666e43a07b7b2e85c0e07`;
- exact diffs:
  - `0x5061 33 -> 34`;
  - `0x5FF7 1D -> 1E`.

### Markings individual

- semantic: `party[0].markings 0 -> 1`;
- output SHA-256: `9baa0be361f52a6bc4b2a5cc6611bb302196d24ad9de3107600adcdd8b572ff3`;
- exact diffs:
  - `0x5053 00 -> 01`;
  - `0x5FF7 1D -> 1E`.

### Ball individual

- semantic: `party[0].ball 3 -> 11` (Poké Ball -> Premier Ball);
- output SHA-256: `be1c4ff04c1c5ab50672b492353d3de14609a40bf898293955d9b2f036103dfb`;
- exact diffs:
  - `0x5062 03 -> 0B`;
  - `0x5FF6 11 -> 19`.

### Combined canary

- semantics: friendship 52, markings 1, ball 11;
- output SHA-256: `65820082d6ced2ad3081e24b27884b6f6f29b5a321b49aecc057995f24ad58bd`;
- exact complete diff count: `5` bytes;
- exact diffs:
  - `0x5053 00 -> 01`;
  - `0x5061 33 -> 34`;
  - `0x5062 03 -> 0B`;
  - `0x5FF6 11 -> 19`;
  - `0x5FF7 1D -> 1F`.

## Synthetic implementation evidence

`tests/test_m3c_batch_writer.py` passed **7/7** locally. Coverage includes:

1. exact private seals/constants;
2. each field in its own field/checksum envelope;
3. combined application order independence;
4. rejection of unknown or non-sealed field combinations;
5. rejection of a wrong starting value/profile;
6. rejection of unrelated synthetic output against the private seal;
7. exclusive new-file output, input immutability, input-overwrite refusal, and existing-output refusal.

Together with the already-present M3C-F1 tests in the local harness: `python3 -m unittest discover -s tests -v` -> **13/13 PASS**. This is local synthetic evidence, not GitHub Actions evidence.

## Exact private preflight

The repository candidate writer generated all four private outputs from the exact input. A separate independent verification pass, not using the batch writer's sealing logic, then:

- recomputed all valid section checksums in both slots;
- reproduced each exact output SHA and full diff;
- decoded the expected semantic values;
- confirmed active slot/counters unchanged at `0 / [4,3]`;
- confirmed inactive slot byte-for-byte preservation;
- confirmed sectors 30/31 and footer byte-for-byte preservation;
- re-hashed the source after generation and reproduced the original input SHA.

Result: **PRIVATE BATCH PREFLIGHT PASS.**

## Human canary gate — completed

The normal path requires only the **combined canary** first:

1. load the exact combined canary in the same PokemonStart v0.15 environment;
2. confirm the save loads normally; visual confirmation of the Premier Ball/marking is useful if exposed by the game UI but is not sufficient by itself;
3. perform one normal in-game save;
4. return the resaved `.sav` privately;
5. verify the slot/counter transition, friendship 52, markings 1, ball 11, complete party-record invariants, sectors 28–31, and footer preservation-only rule.

If the combined canary fails, do **not** test random new edits. Use the three already-generated individual variants to isolate the failing capability. No extra implementation round is required before that isolation step.

## Merge boundary

This branch/PR must remain unmerged until the human combined-canary gate passes and a later explicit batch merge decision is given.
