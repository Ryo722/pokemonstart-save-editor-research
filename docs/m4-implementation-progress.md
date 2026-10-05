# Bounded M4 implementation progress — 2026-10-05

## Authority and adoption state

- PR #13 exact candidate `2612df5de7bac7a1ebce6650eb9ed69b440fbc4d` was explicitly authorized for bounded merge as **M4 IN PROGRESS** and merged into `main` as `4685edd4fa61d7e02a29d1cb6279e0e8858bdaa7`.
- The post-merge adoption authority is recorded in `docs/m4-pr13-adoption.md`. M4 remains IN PROGRESS; Windows write/download support and M4 completion are not adopted.
- The allowed capability remains only repeated party[0] markings `0 ↔ 1` for the observed retained PokemonStart v0.15 root, selected ROM/build, and local emulator environment. Unsupported saves expose no edit action.
- S0 structure, P retained-lineage continuation, and C capability semantics are separate decisions. No arbitrary saves, broader versions/builds, fields, party indices, boxes, bags, or unrestricted values are supported.

## Evidence disposition

- The private v4 hash-only journal binds the single retained M3C root to the locally selected PokemonStart v0.15 ROM/build and matching emulator environment, then records A→B→C→D→E→F. Per-save and ROM/build fingerprints stay outside Git; the journal contains hashes and bounded metadata, not save or ROM bytes.
- Human game canaries B→C (`1→0`) and D→E (`0→1`) both loaded, displayed the expected party[0] markings, and completed a normal in-game save. C/D are proof outputs; E is the second game-return direction.
- P is evidence-backed by the independently audited retained transitions with counters 5→6, 6→7, and 7→8. The narrow source model masks SaveBlock2 play-time fields, selected source-defined EventObject runtime/movement fields, and the saved-game statistic with exact `+1`. Other payload bytes remain equality-checked. See [`m4-p-transition-model.md`](m4-p-transition-model.md).
- The independent D→E audit passed every adopted S0/P transition check, including slot/counter/parity, prior slot, party, sectors 28–31, tails, checksums, and footer policy. Every non-checksum payload difference maps to the source-backed volatility model; none remain unexplained.
- The FAMILY gate is enabled in the core on the validated macOS host. Private C/E establish both representative game-boundary directions; no GUI-specific game canary is needed because the adapters call the same core transaction and audit functions.

## Adopted delivery

- `pokemonstart_m4_core.py` owns structural eligibility, retained-lineage profile checks, the sole PROVEN capability, semantic plans, stale-plan rejection, byte-level independent output audits, journal updates, and the host-platform write gate. The CLI remains a thin adapter. The core and CLI import successfully in an environment without NiceGUI.
- Write delivery is gated by the validated host platform at the core boundary. macOS retains its proven action; an unvalidated platform may inspect S0/P but receives no C action, and core/browser preview, commit, and download reject before journal or output changes.
- `pokemonstart_m4_web.py` is the adopted NiceGUI-only delivery adapter. The supported server options pin host to `127.0.0.1`, disable `on_air` and reload, and reject invalid ports. The UI accepts one local `.sav`, displays S0/P/C and party[0], lists only core-returned actions, previews the exact mutation, requires explicit commit, audits output before exposing download bytes, shows source/output hashes and recovery guidance, and never writes to an emulator path.
- The browser path keeps input and candidate bytes in process memory. `commit_download` reuses the existing core plan/transaction/audit logic; filesystem publication remains available to CLI/core tests. Reproducing a byte-identical previously journaled output reuses its matching bounded fingerprint without adding a duplicate parent edge.
- NiceGUI is pinned in `requirements-m4-ui.txt`; it is not imported by the save core or CLI. The old Tk adapter and Tk smoke test remain historical reference only and are excluded from M4 acceptance.
- Synthetic browser-adapter tests cover loopback configuration, unsupported input/action gating, core-derived action visibility, preview/commit, stale-plan rejection, independent receipt verification, verified download bytes, source immutability, and fail-closed behavior on an unvalidated platform.
- The NiceGUI 3.17.0 source-run page was started and served over `127.0.0.1`; an HTTP GET returned the editor page with disabled edit/commit/download controls before an eligible upload. No LAN/public listener was used.

## Platform evidence and remaining boundary

- **macOS:** S0/P/C and both human game-boundary markings directions are qualified for the bounded retained lineage. The private CLI edit path produced and verified F. The NiceGUI `BrowserWorkflow` consumed F, repeated the core action, independently checked the receipt and output hash, exposed the verified in-memory download payload, and confirmed F remained byte-identical. The resulting bytes matched the already journaled E node and did not add a duplicate lineage edge. The server page was fetched over loopback. Synthetic NiceGUI browser simulation drives actual adapter upload, preview, commit, unsupported-save gating, and download callbacks; the private save was exercised through that same `BrowserWorkflow`, not through a live browser session.
- **macOS filesystem publication:** staged, flushed, fsynced, no-clobber new-file publication and failure injection are covered by local tests on this host. This does not establish every crash point or other operating systems.
- **Windows:** not run. Windows may perform read-only S0/P inspection; the core returns no C write action and rejects preview, in-memory commit, filesystem commit, browser commit, and browser download before journal/output changes. NTFS publication semantics, links/junctions/races, durability, private Windows S0/P/C validation, and Windows browser/UI validation remain unproven. See [`m4-windows-validation.md`](m4-windows-validation.md).
- Local regression evidence at the adopted PR #13 head: **72/72 tests pass** in the NiceGUI UI virtual environment; the system Python run records **71 pass / 1 skip** for the optional NiceGUI browser simulation. These are local execution results, not GitHub Actions reproduction.
- Private save and ROM/build files were not committed or uploaded. No live emulator save is overwritten.

## Remaining work before M4 completion

The cheapest remaining uncertainty-reducing work is Windows validation under `docs/m4-windows-validation.md`: synthetic/platform checks, NTFS publication proof, private Windows S0/P/C validation, and localhost NiceGUI/browser validation. Windows write/download remains disabled until that evidence is separately reviewed and adopted.

M4 completion is not implied by PR #13 adoption. The project must either satisfy the existing cross-platform M4 acceptance criteria or later re-evaluate those criteria from fresh canonical evidence through a separate human decision.
