# PokemonStart v0.27 / 64 MiB reconnaissance

Status: **INVESTIGATION RECORD — not canonical, not adopted.**
This branch records a read-only/static reconnaissance of exact PokemonStart
v0.27. It does not change the controlling [decision record](decision-record.md),
the E-series sequence, any writer, or the exact-v0.22 product. No other
PokemonStart version is supported by this record. Adoption of any conclusion or
sequencing change is Human-gated.

Sanitized data: [v027-64mib-reconnaissance-evidence.json](v027-64mib-reconnaissance-evidence.json).
No ROM, save, package, patch, decoded upstream script, disassembly or extracted
table bytes are stored in Git.

## Evidence labels

`CANONICAL_PROJECT_EVIDENCE`, `INDEPENDENTLY_REPRODUCED`,
`UPSTREAM_POKEMONSTART_EVIDENCE`, `UPSTREAM_MGBA_SOURCE_EVIDENCE`,
`PRIVATE_ROM_VERIFICATION`, `PRIVATE_SAVE_VERIFICATION` (none in this record),
`MIGRATION_TOOL_EVIDENCE`, `HYPOTHESIS_UNVERIFIED`.

## Summary

- v0.26 → v0.27 changed only Pokémon-picture placement (moved to the upper
  32 MiB) plus a new SD-card picture loader. Save machinery and E3/E4-relevant
  ROM semantics are identical to v0.26 modulo relocation.
- v0.22 → v0.27 E3/E4 ROM semantics are unchanged modulo table relocation; the
  material v0.22 → v0.27 difference is the v0.23 save-layout change.
- The unresolved E4-A blockers (nickname tail, flag-0x913 PID/shiny rewrite,
  unreconstructed runtime inputs, region fallback) are **still present and
  unchanged** in v0.27; they are neither resolved nor replaced.
- Recommendation for Human decision: `RUN_MINIMAL_V027_PRIVATE_GATE`.

## Fresh state

`CANONICAL_PROJECT_EVIDENCE`: remote `main` `381bc80`; E0–E3 complete/adopted;
E4 next, with the E4-A checkpoint (`69d1d5d`, `BOUNDED_STOP_WITH_CONCRETE_EVIDENCE`)
outside `main`. No open Issues/PRs. Another PokemonStart build, Box and E4
implementation each require separate authorization.

`UPSTREAM_POKEMONSTART_EVIDENCE`: upstream HEAD is still `23007d4` (v0.27); no
newer release. v0.18–v0.27 were published within about three days.

## v0.27 package and 64 MiB ROM

`INDEPENDENTLY_REPRODUCED`: package SHA-256 `d81b965d…fe5a90` (Git blob
`359a097` matches), PKS1 with four members; no emulator binary. BPS source
16,777,216 bytes / CRC `3B2056E9`; target **67,108,864** bytes / CRC
`84202DAB`; patch CRC valid; build `312547f4`.

`PRIVATE_ROM_VERIFICATION`: the owned source (unchanged) patched in scratch to
v0.27 SHA-256 `455f5294…3781ac`; re-deriving v0.22 reproduced the canonical
`6abce6aa…` exactly.

`UPSTREAM_POKEMONSTART_EVIDENCE`: the bundled text says the pictures live in the
latter half, only the 64 MiB mGBA plays correctly (other emulators, stock mGBA
and hardware lack pictures), and earlier `.sav` files remain usable when renamed
to match the ROM.

## mGBA `rom64`

`UPSTREAM_MGBA_SOURCE_EVIDENCE`: `rom64` (`770ab0b`) is Exormeter celio 2.0.0
plus three commits; the only code commit is `4857dec` (`gba.c`, `memory.c`,
`version.cmake`).

- Activation: ROM file exactly `0x04000000` bytes and header `0xAC` ≠ `'M'`.
- Mechanism: address decode only — ROM mask widened to `0x03FFFFFF`.
  `0x08/0x09` → lower half, `0x0A/0x0B` → upper half, `0x0C/0x0D` → lower-half
  mirror. No banking or mapper.
- Unchanged: waitstate tables (upper half uses WS1 settings), prefetch path
  (via the widened mask), save memory, RTC/GPIO, savestate format, Celio link.
- Side notes: `romCrc32` covers 64 MiB (cross-build savestates only warn);
  mGBA soft-patching still rejects >32 MiB outputs; cheat ROM hooks keep the
  32 MiB mask; the `cart1` memory block returns the ROM base pointer.
- Stock mGBA maps only the first 32 MiB, so `0x0A…` mirrors the lower half.
  Real hardware: `0x0A`/`0x0C` mirror `0x08`, 32 MB maximum (GBATEK). Other
  emulators and flash carts: no direct evidence (`HYPOTHESIS_UNVERIFIED`).

## Upper 32 MiB content

`PRIVATE_ROM_VERIFICATION`: used range `0x0A000000–0x0A163393`, remainder
`0xFF`. It begins with a `PKSPICS1` container (2804 entries) referenced by two
picture tables (1865 and 1484 entries, size `0x800`, tag = species index)
that existed at different lower-half addresses in v0.26. About 98% of the
upper blobs are byte-identical to v0.26 lower-half blobs. No executable-code
evidence; save, construction and data-table code remain in the lower half.

v0.27 also adds a branch in the hooked LZ77 wrapper (source in
`0x0A–0x0B` → new loader), a `0x520`-byte IWRAM ARM payload and a ~2.3 KB
Thumb block containing `PKSPICS.BIN`/`SDTEST.BIN`, FAT directory parsing and
SuperCard-SD-style register constants; no save-memory (`0x0E…`) literals. The
selection logic is `HYPOTHESIS_UNVERIFIED`.

## Save architecture (v0.23+ including v0.27)

`MIGRATION_TOOL_EVIDENCE`: the bundled migration HTML is byte-identical in
v0.23, v0.26 and v0.27. Statically decoded (not executed), it writes five
sections per slot (sectors 0–4/5–9 by counter parity, unchanged checksum
lengths), keeps the section-0/4 parasites in place, and writes 17 single-copy
Box pages (IDs `0x40–0x50`, checksum length `0xFF0`) to sectors 10–26:
page 0 holds the storage header/tails, the former section-13 parasite at
`+0x18B` and 12 58-byte Box records at `+0xD2B`; pages 1–14 hold 70 records
each; pages 15/16 hold the former sectors 30/31. SaveBlock1 `+0x1400` receives
`SHEL`, a counter and the 17-entry page-sector table.

`PRIVATE_ROM_VERIFICATION`:

- v0.27 save code contains `SHEL`, `0x1408`, `0x1419`, `0xD2B` and the
  `0x0203B40C…0x0203BFAC` → page `+0x18B` copy, matching the tool.
- A native new game initialises the SHEL table to `0xFF`; load accepts page
  sectors 10–31 from the table and validates id/signature/checksum.
  Dynamic page allocation using spare sectors is `HYPOTHESIS_UNVERIFIED`.
- RAM fragment addresses used by Inventory are unchanged v0.22–v0.27.
- The save-machinery static closure (193 functions) is identical
  v0.23/v0.26 → v0.27 except the LZ77 wrapper. No v0.26 → v0.27 migration.

Party (`SB1+0x34/+0x38`) and Money (`SB1+0x290` ⊕ `SB2+0xF20`) offsets are very
likely unchanged (SaveBlock1 copied verbatim; vanilla code pointer-only), but no
real v0.23+ save was examined. Inventory now spans page 0 (`+0x817`) and page
15 and is covered by page checksums.

## Editor-relevant ROM comparison

`PRIVATE_ROM_VERIFICATION` (static, pointer/BL-normalized):

- Content-identical across v0.22/v0.26/v0.27, addresses moved: base stats,
  species names, moves, move names, EXP, natures, all 1489 learnsets; items and
  pocket descriptor identical modulo pointers.
- Map-header region section IDs identical for all 1190 parsed maps.
- v0.26 → v0.27 vanilla region: pointer updates only.
- E3/E4 root closure (125 functions from CreateMon, Get/SetMonData,
  CalculateMonStats, ability, nickname, flag/var and region roots): identical
  v0.26 ↔ v0.27; v0.22 ↔ v0.27 differs only in two held-item-835 /
  species-303 stat-doubling helpers that now read the held item directly at
  record `+0x22` instead of through GetMonData — judged semantically equivalent.
- v0.22 → v0.27 vanilla code: ten new hook stubs (save entry, SendMonToPC,
  PC), Box-count constants 25 → 39, Hall-of-Fame call removed. The native
  give-Pokémon hook path changed for the new Box storage (v0.26 = v0.27).

## E4 implication

E4-A semantic investigation transfers to v0.27 with an address profile.
Version-dependent parts are the E4-B write path (five-section slot, SHEL
preservation) and native give/Box paths. The earlier v0.26 reconnaissance
conclusion that E4 is substantially more version-sensitive than E3 is not
supported at the ROM-semantic level by this evidence.

## Profile architecture (decision surface only)

Splitting (1) save-layout family (legacy vs v0.23+), (2) per-build ROM
address profile verified by content hashes, and (3) runtime (harness-only
note) would lower per-version cost: tables move every build while content and
save layout are stable since v0.23. Finalise only after the private gate.

## Prepared read-only tooling

`research/v027/pokemonstart_v023plus_readonly_probe.py` — strictly read-only;
detects both layouts, follows the SHEL table, reports sector inventory, page
validity/counters, Party/Money/Inventory reconstructions and a `--against`
structural diff. Unknown states stay unknown; no repair/write path.
Synthetic tests: `python3 -m unittest discover -s research/v027 -v` (9 tests).

## Minimum Human experiment

Requires the `rom64` mGBA (published only as a Windows zip; macOS needs a source
build).

| Artifact | Action | Information gain |
| --- | --- | --- |
| S0 | copy of an existing retained exact-v0.22 save | baseline; no new gameplay |
| M | official migration HTML output | confirms the decoded migration layout on a real save |
| R1 | load M in v0.27, SAVE once, no other action | slot, counters, page rewrite/reallocation, SHEL counter, sectors 27–31, Party/Money placement |
| R2 | SAVE once more | steady state and spare-sector reuse |

If the owner already has a natural v0.27 save N, use N → R1 → R2 instead of
S0/M. Request a native-new-game save only if R1/R2 do not exercise allocation.

## Unknowns and limits

- Real-save page allocation and counter semantics; storage location of the six
  boxes beyond the 33 in the migration stream; former v0.22 use of
  `SB1+0x1400`; SD-path selection and hardware/flash-cart behaviour.
- Static closure is a lower bound (jump tables / data-driven callbacks not
  followed). Unicorn differential execution could not run in the sandbox (no
  JIT); no private save was read.

## Recommendation

`RUN_MINIMAL_V027_PRIVATE_GATE`: do not invest further in v0.22-only E4
writer/GUI work before one read-only v0.27 gate; profile-neutral E4-A semantic
investigation may continue. Requires Human authorization for a private v0.27
read-only experiment and a Human answer on which build the owner actually plays.
Canonical sequencing changes and any v0.27 writer/GUI need separate approval.
