# v0.22 practical product candidate

Canonical base: `7e7435c5507abfec183c3b370dcb1fa381b22186` (fresh origin/main).
Candidate: `codex/v022-practical-product-sprint`. Initial working tree: clean.
Local main fast-forwarded to the canonical base; implementation occurs only on candidate.

Existing tests include Fast Lab Money/Party/Inventory, FL2, creation/composition,
NiceGUI delivery, verifier and earlier Stable tools. Existing APIs retain their
original gates. New product APIs are candidate-only and do not promote Stable support.

Protected boundary: ROM/save/package/patch/executable/game assets remain outside
Git. Private root is PokemonStart-private; only read inputs, immutable in-memory
outputs, and separate verified downloads are used. No emulator save replacement.

Frozen Money branch inspected as non-canonical reference. Reused conservative
key0/two-valid-slot/consecutive-counter ideas after reconciliation; no merge or
cherry-pick. Its fixed target is not a practical requirement. Nonzero keys remain
unsupported: existing exact-v0.22 evidence does not independently qualify them.
Open PR #3 is historical M2 work and does not affect this sprint; no open issues.
