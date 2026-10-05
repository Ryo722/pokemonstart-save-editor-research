# M5A private money read audit — 2026-10-05

## Scope and evidence label

This record covers a **read-only** audit of a user-supplied retained private PokemonStart v0.15 save. No save bytes are committed to this repository and no writer was implemented or executed.

Evidence label: **local private-input verification**, with the source-derived money formula still requiring human display confirmation before it is treated as independently reproduced game semantics.

## Input identity

- uploaded private file size: `131,088` bytes (`0x20010`)
- SHA-256: `fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b`
- this SHA-256 exactly matches the canonical original / before-test retained-lineage save already recorded in `docs/evidence.md`
- flash body size: `0x20000`
- opaque emulator footer size: `16` bytes
- footer SHA-256: `9e5dd419cf323817943c6282d4f51936fb4913fe6f0c83458aa5b4f5742ae877`

The input was read only. No output save was produced.

## Independent structural audit

A throwaway parser, separate from the repository M5A probe, independently reproduced the adopted section/checksum rules.

Observed state:

- slot 0: fully erased
- slot 1: 14 non-erased sectors, counter `1`
- physical/logical order in slot 1: `13,0,1,2,3,4,5,6,7,8,9,10,11,12`
- all 14 signatures valid (`0x08012025`)
- all 14 section checksums valid using the pinned per-section lengths
- active slot: slot 1
- logical section 0 is physical sector 15
- logical section 1 is physical sector 16
- sector 30: 23 nonzero bytes
- sector 31: 0 nonzero bytes
- party count: 1
- party[0] species: 1
- party[0] level: 5
- party[0] EXP: 134

These observations are consistent with the existing retained-lineage evidence, but this audit was recomputed from the supplied bytes rather than assumed from prior records.

## Money hypothesis evaluation

Pinned CFRU-JP source places:

- `SaveBlock1.money` at SaveBlock1 offset `0x0290`;
- `SaveBlock2.encryptionKey` at SaveBlock2 offset `0x0F20`;
- SaveBlock2 in logical section 0;
- the first SaveBlock1 chunk in logical section 1.

The current source-derived candidate decode rule is:

`money = LE32(active logical section 1 @ 0x0290) XOR LE32(active logical section 0 @ 0x0F20)`

For this private input, the independent read-only audit obtained:

- encryption key: `0x00000000`
- stored money word: `0x00000BB8`
- XOR-decoded candidate money: **`3000`**

Because the key is zero in this particular save, the stored and decoded values are identical. This does **not** justify assuming an unencrypted representation for later saves; the writer/read model must continue to use the key-derived XOR rule.

## Remaining confirmation and revised cheapest proof

The user has not yet supplied an explicit human observation of the in-game displayed money for this exact save. Therefore `3000` is currently a strongly source-supported decoded candidate value, not yet an independently reproduced display-semantic proof.

If the game displays `3000` for this exact save, a game-generated purchase before/after differential is no longer required as the cheapest next proof. Instead, the project may propose a single exact bounded canary:

- exact input hash above;
- target displayed money `9,999,999`;
- encode with the active SaveBlock2 key;
- mutate only the four-byte money word in logical section 1 plus the required logical-section-1 checksum bytes;
- preserve every other byte under the existing transaction envelope;
- write only to a new file;
- independently audit the complete output;
- human-load the candidate, confirm displayed money, perform one normal in-game save, and return the resave for read-only audit.

That canary still requires fresh Human authorization before any money writer implementation or private-save mutation.
