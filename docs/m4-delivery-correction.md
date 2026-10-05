# M4 delivery correction — 2026-10-05

## Status

**AUTHORIZED / IN PROGRESS.**

Human authorization:

> `AUTHORIZE M4 DELIVERY CORRECTION: replace the Tkinter adapter with a localhost-only NiceGUI browser UI using the existing S0/P/C core and verified download-output flow; retain CLI, fail-closed capability gates, private-data boundaries, and the existing no-merge boundary.`

This correction changes only the M4 delivery layer. It does not broaden writer authority, provenance/profile eligibility, capability eligibility, supported save/build scope, or merge authority.

## Controlling correction

For the bounded M4 implementation slice, the previously authorized thin Tkinter GUI is superseded by a **localhost-only NiceGUI browser UI** over the same trusted core.

The retained architecture is:

1. structural eligibility (S0);
2. retained-lineage provenance/profile eligibility (P);
3. bounded capability eligibility (C);
4. immutable inspection / mutation-plan core;
5. hardened new-file transaction and independent receipt verification;
6. CLI/audit adapter;
7. localhost-only NiceGUI delivery adapter.

The UI remains outside the trust boundary. It must not supply raw offsets, arbitrary values, writable buffers, checksum instructions, or bypass S0/P/C capability gates.

## Browser/locality boundary

The NiceGUI service must bind only to loopback, e.g. `127.0.0.1`. LAN/public binding, remote hosting, and NiceGUI relay / `on_air` style exposure are outside this authorization.

Private save bytes and ROM/build data must not be uploaded to any remote service. Browser interaction is local-machine-only.

## Output model

The preferred browser delivery flow is:

- select/upload a local private `.sav` into the local process;
- inspect and preview through the existing S0/P/C core;
- execute only a core-returned PROVEN capability;
- independently verify the generated output;
- offer the verified output as a browser download / save action.

The original input remains immutable. The UI must not automatically write to or replace an emulator live-save path. Existing fail-closed output, audit, recovery, and private-data requirements remain in force.

Implementation may retain a hardened filesystem publication path in the core/CLI for audit and platform proof, but the browser UI itself need not depend on native file-dialog or Tk event-loop behavior.

## Dependency / testing boundary

NiceGUI is an added third-party delivery dependency; the underlying save core remains independently testable without the UI dependency.

The implementation must add focused browser-adapter tests for at least:

- localhost-only configuration;
- S0/P/C-gated action visibility;
- preview state and stale-plan rejection;
- verified output generation/download;
- unsupported inputs exposing no write action;
- no remote/public binding in the supported configuration.

A GUI-specific game canary is not required merely because the caller is NiceGUI when the browser adapter invokes the same already-proven core transaction path. New game-boundary evidence remains required only when a semantic capability, provenance/profile rule, or transaction behavior itself is not yet proven.

## Preserved authorization boundary

This correction retains the existing authorization for:

- retained-lineage S0/P/C qualification;
- one bounded repeated-use `party[0]` markings family;
- local/private lineage journal metadata;
- hardened new-file transaction/publication and independent verification;
- CLI/audit delivery;
- synthetic/regression/fault tests;
- required private/game-boundary canaries;
- macOS validation and preparation for Windows validation;
- feature branches, commits, documentation, and review-ready implementation PR preparation.

It still does **not** authorize:

- arbitrary/non-lineage saves;
- broad PokemonStart build/version generalization;
- unrestricted values or arbitrary party indices;
- boxes/bags;
- unrelated new fields;
- automatic live-emulator replacement;
- protected-data publication;
- execution of blocked/proprietary binaries;
- merging any M4 implementation PR into `main` without a separate explicit human merge authorization.

## Execution consequence

Stop spending implementation time on Tkinter visible-event-loop debugging unless later evidence makes Tk specifically necessary. Reuse the existing S0/P/C core, transaction, journal, CLI, private evidence, and tests; replace only the outer GUI adapter with the bounded localhost-only NiceGUI path.
