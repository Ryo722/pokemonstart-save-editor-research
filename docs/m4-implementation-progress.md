# Bounded M4 implementation progress — 2026-10-05

## Authority and branch

- Canonical `origin/main` was freshly fetched at `b6d430f93a30fab78410c6b9cc7d7748d5e6a87f`; its decision record, bounded authorization, and delivery correction are controlling.
- Work remains on `m4-bounded-editor-slice`. M4 implementation is authorized; PR merge is not.
- The allowed capability is only repeated party[0] markings `0 ↔ 1` for the observed retained PokemonStart v0.15 root, selected ROM/build, and local emulator environment. Unsupported saves expose no edit action.
- S0 structure, P retained-lineage continuation, and C capability semantics are separate decisions. No arbitrary saves, broader versions/builds, fields, party indices, boxes, bags, or unrestricted values are supported.

## Evidence disposition

- The private v4 hash-only journal binds the single retained M3C root to the locally selected PokemonStart v0.15 ROM/build and matching emulator environment, then records A→B→C→D→E→F. Per-save and ROM/build fingerprints stay outside Git; the journal contains hashes and bounded metadata, not save or ROM bytes.
- Human game canaries B→C (`1→0`) and D→E (`0→1`) both loaded, displayed the expected party[0] markings, and completed a normal in-game save. C/D are proof outputs; E is the second game-return direction.
- P is evidence-backed by the independently audited retained transitions with counters 5→6, 6→7, and 7→8. The narrow source model masks SaveBlock2 play-time fields, selected source-defined EventObject runtime/movement fields, and the saved-game statistic with exact `+1`. Other payload bytes remain equality-checked. See [`m4-p-transition-model.md`](m4-p-transition-model.md).
- The independent D→E audit passed every adopted S0/P transition check, including slot/counter/parity, prior slot, party, sectors 28–31, tails, checksums, and footer policy. Every non-checksum payload difference maps to the source-backed volatility model; none remain unexplained.
- The FAMILY gate is enabled in the core. Private C/E establish both representative game-boundary directions; no GUI-specific game canary is needed because the adapters call the same core transaction and audit functions.

## Implemented delivery

- `pokemonstart_m4_core.py` owns structural eligibility, retained-lineage profile checks, the sole PROVEN capability, semantic plans, stale-plan rejection, byte-level independent output audits, and journal updates. The CLI remains a thin adapter. The core and CLI import successfully in an environment without NiceGUI.
- `pokemonstart_m4_web.py` adds a NiceGUI-only delivery adapter. The supported server options pin host to `127.0.0.1`, disable `on_air` and reload, and reject invalid ports. The UI accepts one local `.sav`, displays S0/P/C and party[0], lists only core-returned actions, previews the exact mutation, requires explicit commit, audits output before exposing download bytes, shows source/output hashes and recovery guidance, and never writes to an emulator path.
- The browser path keeps input and candidate bytes in process memory. `commit_download` reuses the existing core plan/transaction/audit logic; filesystem publication remains available to CLI/core tests. Reproducing a byte-identical previously journaled output reuses its matching bounded fingerprint without adding a duplicate parent edge.
- NiceGUI is pinned in `requirements-m4-ui.txt`; it is not imported by the save core or CLI. The old Tk adapter and Tk smoke test remain historical reference only and are excluded from M4 acceptance.
- Synthetic browser-adapter tests cover loopback configuration, unsupported input/action gating, core-derived action visibility, preview/commit, stale-plan rejection, independent receipt verification, verified download bytes, and source immutability. NiceGUI's browser simulation drives upload, preview, commit, download, then uploads an unsupported save and confirms all edit buttons stay disabled.
- The NiceGUI 3.17.0 source-run page was started and served over `127.0.0.1`; an HTTP GET returned the editor page with disabled edit/commit/download controls before an eligible upload. The sandbox initially denied local socket binding; the same authorized loopback-only check was rerun with host permission and succeeded. No LAN/public listener was used.

## Platform evidence and remaining boundary

- **macOS:** S0/P/C and both human game-boundary markings directions are qualified for the bounded retained lineage. The private CLI edit path has produced and verified F. The NiceGUI `BrowserWorkflow` has also consumed F, repeated the core action, independently checked the receipt and output hash, exposed the verified in-memory download payload, and confirmed F remained byte-identical. The resulting bytes matched the already journaled E node and did not add a duplicate lineage edge. The server page was fetched over loopback. Synthetic NiceGUI browser simulation drives actual adapter upload, preview, commit, unsupported-save gating, and download callbacks; the private save was exercised through that same `BrowserWorkflow`, not through a live browser session.
- **macOS filesystem publication:** staged, flushed, fsynced, no-clobber new-file publication and failure injection are covered by tests on this host. This does not establish every crash point or other operating systems.
- **Windows:** not run. Windows publication remains fail-closed before I/O. The available macOS synthetic test checks that rejection; NTFS semantics, links/junctions/races, durability, private Windows validation, and Windows GUI behavior remain unproven. See [`m4-windows-validation.md`](m4-windows-validation.md).
- Regression result after the delivery correction: **70/70 pass** in the NiceGUI UI virtual environment; the system Python run passes all non-UI tests and skips only the optional NiceGUI browser simulation. Core and CLI import without NiceGUI installed.
- Private save and ROM/build files are never committed, uploaded, or published. No live emulator save is overwritten. No implementation PR is merged without separate human authorization.
