# E3 existing-Party writer candidate — exact v0.22

This continues the historical [read-only checkpoint](e3-existing-party-readonly-qualification.md).
That checkpoint remains evidence, not writer authority. GitHub `main` is the
only durable canonical authority. This branch is a candidate awaiting one
grouped Human acceptance; no merge, Stable promotion, release or E4 is authorized.

## Ordinary capability predicate

The exact owned ROM gate remains SHA-256
`6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0`.
Production eligibility and independent eligibility both require valid consecutive
save slots, an occupied sane non-egg record, consistent EXP/level/caches,
valid IV/EV/nature/occupied-move PP, and current HP at most max HP. The bounded
species domain is internal IDs 1–151 and 288. This is a practical conservative
domain, not authority for every metadata-decodable species.

Saved runtime mode selectors are reconstructible from the active save:
flag `0x930` is section 0 offset `0xF2A` bit 0; variable `0x5018` is
section 4 offsets `0xEFC–0xEFD`. Exact FlagGet/VarGet and SaveParasite execution
corroborate the mapping. The separate auditor concatenates the parasite
fragments (section 0 `F24:FF0`, section 4 `D98:FF0`, section 13 `450:FF0`)
and reads image byte 6 / bytes 560–561. These tails are outside the ordinary
section checksum coverage; both paths explicitly preserve and examine them.
Every set flag is rejected, including facility tiers beyond Average Mons (13),
350 Cup (12), and Scalemons (11). An unset flag makes the dormant tier irrelevant.
Normal-looking Party records alone never establish this context.

Eggs, nonzero backup species, hyper-training, unsupported forms/species,
Shedinja (303), ability-override species 496/497/498/913/1460, invalid caches,
unknown metadata and unsafe retained held items fail closed. Exact execution
activates the special ability 319 override under synthetic player-OT,
shiny/perfect-IV conditions; those species stay excluded. Item 835 doubles
both HP and non-HP stats (Shedinja HP remains 1), so it is excluded. Move 548
can change species 700/757 in the native setter; both species are excluded,
and enter/leave transitions are checked across the admitted domain.

Held metadata decoding, safe retention and new-target eligibility are separate
results. New targets are only removal (0), Oran (139), Sitrus (142), and
Leftovers (200), with exact pocket/importance/type/effect/parameter tuples
pinned independently. Light Ball (202) is retained-only. Exact stat and ability
execution checks the retained/target set across every admitted species;
retention does not grant new-target authority. Key/event/form/HP-coupled items,
unsupported types/effects/pockets, item 835, unknown metadata and all other
catalog entries remain outside the target subset. E2 Inventory authority is
not inherited by Party held-item editing.

## Moves and HP

Untouched move slots preserve all bytes, including stale PP and PP-Up bits in
empty slots. Replacing/filling a slot initializes its PP using the target's
exact maximum and retained or explicitly requested PP-Up count; explicit PP
must lie within that maximum. A changed PP-Up count also initializes the
maximum unless explicit PP is requested. Clearing uses the native
SetMonMoveSlot representation: ID 0, base PP 35, retained PP-Up bits. Setting
an already-empty slot to 0 preserves its PP. Direct empty-slot PP/PP-Up editing
is unsupported. Other slots are never normalized. Move 996 ignores PP-Up
bonuses. Duplicate decoded names display IDs in GUI choices.

The native stat routine's decreasing-max branch depends on the unsaved
in-battle flag: when current HP exceeds the new maximum, out-of-battle code
clamps it but in-battle code can retain an invalid current HP. Save reconstruction
does not establish that flag. Therefore the writer rejects precisely those
decreases before producing output. It admits decreases with current HP at most
the new maximum, preserving current HP in both contexts. Fainted HP remains 0;
a live max-HP increase adds the maximum delta to current HP. Exact execution
checks full/damaged/fainted/equal-boundary/increase cases in both contexts.
This is a capability restriction, not removal of the adopted HP coupling field.

For the retained Lv5 full-HP records, level-only targets 1–4 are blocked (4 of
99 alternate levels); the damaged Lv3 Rattata has no blocked alternate level
from this HP rule and qualifies for Lv2 with HP 3/13. Other edits are evaluated
from their actual target stats; this count is not a universal level policy.

## Fresh coupling matrix

PASS means machine-qualified within the explicit predicate. Human gameplay
acceptance for every generalized coupling remains NOT ESTABLISHED until the
single grouped transaction is returned and independently checked.

| Adopted field | Status | Capability-specific reason |
| --- | --- | --- |
| species | PASS | Ordinary domain only; exact growth/base/ability metadata, preserved identity, recalculated caches |
| level / EXP | PASS | Exact ROM thresholds; explicit level/EXP conflicts rejected |
| moves 1–4 | PASS | Slot-local replacement/fill/clear, excluded form-changing species |
| PP | PASS | Occupied-slot range; legal empty stale PP preserved; direct empty PP edits FAIL |
| PP-Up | PASS | Four packed pairs, counts 0–3, move996 exception; direct empty bonus edit FAIL |
| friendship | PASS | Requested byte only; unrelated Party bytes preserved |
| IV | PASS | Six 0–31 values; egg/selector bits preserved; hyper-training FAIL |
| EV | PASS | Six 0–252 values, total at most 510; caches recalculated |
| effective nature | PASS | Mint/native distinction, exact integer stat modifiers; arbitrary PID editing FAIL |
| ability | PASS | Resolved ordinary first/second/hidden choices, zero fallback; minimal selector-bit change; special override species FAIL |
| held item | PASS | Three conservative targets plus removal; retained-only Light Ball; other targets FAIL |
| cached stats / HP | PASS | Complete reconstruction and context-invariant rule; current greater than decreased maximum FAIL |
| saved facility modes / exceptional states | FAIL | Explicit fail-closed rejection; no broad writer authority |
| unsaved live battle context | NOT ESTABLISHED | Context-sensitive decreases rejected; admitted transitions agree in both probed contexts |

## Product and independent reconstruction

The existing Party family and Money/Inventory composition path are generalized,
not replaced. Immutable source bytes, a separate exclusive private export,
checksums, semantic preview and stale-state invalidation remain mandatory.
Party-only and all three Money/Inventory combinations require independent
whole-output equality and a requested-field byte envelope. The Party auditor
imports neither the production Party model/writer nor the repository verifier.
Its section parser and forward arithmetic reconstruct the complete save;
the composition auditor also checks unchanged context and unrelated bytes.
Money and Inventory family implementations are unchanged.

No arbitrary PID/shiny/OT/nickname/ball editing, creation or Box path is added.
Synthetic and Unicorn evidence never represent Human gameplay.

## Reproducible verification and one Human transaction

Run all checks after committing/pushing, recording `git rev-parse HEAD` and
`git rev-parse HEAD^{tree}` plus the canonical base. Keep command logs, probe
reports, private receipts and generated saves in ignored/private storage.

```
.venv/bin/python -m unittest discover -s tests -p 'test_v022_party_writer.py' -v
.venv/bin/python -m unittest discover -s tests -p 'test_v022_party_model.py' -v
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python pokemonstart_v022_party_gate_probe.py --rom <private-ROM> --save <private-source>
.venv/bin/python pokemonstart_v022_party_static_probe.py --rom <private-ROM> --save <private-source>
.venv/bin/python pokemonstart_v022_product_acceptance.py --rom <private-ROM> prepare-e3 <private-source>
```

The grouped recipe dynamically selects full-HP A, naturally damaged low-level
B with a safe decrease, and a distinct ordinary C with a qualified alternate
ability from the actual save. It spreads stats/nature/friendship, HP decrease,
and move/PP/PP-Up/ability/item edits over those specimens, plus a small existing
Money and medicine regression. It uses one source and one GUI export.

The exact-candidate Human packet is generated separately after the pushed
candidate rerun, with SHA/tree/base, immutable source hash, every semantic edit,
GUI preview, expected visible observations and return paths. Human actions:
load the output with the exact ROM, inspect all three, exercise ordinary use,
perform ONE normal in-game SAVE, close/flush, and preserve the returned save.
No per-field canary or second gameplay cycle is requested.

Prepared returned-save command:

```
.venv/bin/python pokemonstart_v022_product_acceptance.py --rom <private-ROM> check-e3-return <immutable-source> <returned-save> <private-receipt.json>
```

It regenerates the recipe from the source, checks exact receipt/output identity,
valid save slots, counter +1, active-slot/section rotation and preserved old
active slot; independently reconstructs every Party record; checks requested
genotype/moves/ability/effective nature and opaque identity persistence; allows
only reported ordinary EXP/EV/friendship/HP/PP/status progression and qualified
berry consumption. Inventory and Money must match. Unexplained couplings reject.
A later editor-cycle dry run is machine-only. Human attestation and drift review
remain required; neither command promotes E3 automatically.

## Human-return verifier correction

The grouped Human return exposed an overly strict emulator-footer equality
check in the return harness. Canonical normal-resave policy already allows the
external opaque 16-byte trailer to change; editor output still preserves it.
The correction records footer hashes/change without guessing its semantics and
retains prior-active-slot equality, counter/rotation and complete Party checks.
It changes no writer/GUI behavior. See the [sanitized review handoff](reviews/e3-existing-party-independent-review.md)
for the played candidate identity, returned save, drift classification and
the correction to the untouched Zigzagoon move3 description. No second
gameplay canary or independent review is performed in the maker context.
