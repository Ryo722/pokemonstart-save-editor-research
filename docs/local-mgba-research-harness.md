# Local mGBA research harness, bounded proof

Starting canonical main: `5d81e77358f95394dea62f94ba993e3ba24a4197`.
This work is on `codex/local-mgba-harness-proof` until live proof and review.

The locally inspected binary is `/Applications/mGBA.app/Contents/MacOS/mGBA`,
which reports `mGBA 0.10.5 (26b7884bc25a5933960f3cdcd98bac1ae14d42e2)`.
Its `--help` has no script-loader option. The [mGBA stable scripting API](https://mgba.io/docs/scripting.html)
documents Lua loading through Tools → Scripting and the CoreAdapter and socket
methods used here. The local runner automates only the dedicated process's
Tools → Scripting → Load script workflow through System Events. It identifies
ScriptingView by the 0.10.5 menu predicate (Apple, mGBA, File; no Tools; File
contains `Load script...` and `Reset`), not by AX window count. It then requires
the uniquely titled `Select script to load` panel, enters the generated absolute
bridge path through Go to Folder, verifies the exact filename in the panel
preview, and activates Open. No other process or window is targeted.

On this macOS host, supplied private inputs must be inside `~/claude-workspace/`
and outside the repository; the runner checks this before reading them. The
session itself uses the system temporary directory as an ephemeral artifact
location.

The runner launches a distinct mGBA app instance with macOS `open -n`, compares
process IDs before and after launch, and shuts down only that new instance.
It refuses an ambiguous or reused process so the cold reload is a real process
boundary. The Python listener binds exactly `127.0.0.1:0`. It creates a random 256-bit
token and a session Lua script under the system temporary directory. A disposable
ROM copy and `.sav` copy share a basename there, so mGBA never points a writable
session at the supplied source save. All screenshots, savestates, token-bearing
script, and JSONL audit remain in this private session directory.

Protocol: one UTF-8 tab-delimited command per line, maximum 256 request bytes;
bounded replies, an explicit command enum, decimal numeric arguments, and no
arbitrary path or code arguments. Reads are limited to EWRAM/IWRAM and 512 bytes
per `read_range`. `arm_money` succeeds only after the Python read-only discovery
identifies a unique address; writes must fit the exact four-byte field and remain
inside writable RAM. The generated Lua repeats these checks. ROM, MMIO, VRAM,
OAM, palette, and register writes have no RPC path.

Discovery scans all EWRAM bytes for the independently decoded money word and
corroborates each candidate with SaveBlock1 party count, party[0] bytes, and the
saved-game count mapping. Multiple candidates stop the proof. A unique RAM
candidate is still not accepted for a write until the operator inspects a
screenshot and confirms that the game is in a safe controllable state. The current
first canary changes only `1,234,567` to `1,234,568` after a research savestate;
nearby bytes are compared and a screenshot is captured. START input is gated on
screen inspection. Manual normal SAVE is requested only after the live canary.

The first proof completed the one bounded manual normal SAVE, shut down mGBA, and
verified the resulting working `.sav`. The cold-only `--cold-resume` mode then
reused that exact working ROM/save without copying the source save, writing RAM,
or saving again. A fresh mGBA 0.10.5 PID loaded a new session bridge; read-only
EWRAM scanning uniquely rediscovered Money at `0x0202571c`, corroborated by
party count, party bytes, and saved-game count. Live Money was `1,234,568`.
After cold shutdown, the repository verifier passed and an independent decoder
reported active slot 0, counter 4, key 0, party count 1, and saved count 4.
The source `.sav` SHA-256 remained
`d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf`; the
disposable working `.sav` remained
`35fd9c501a23484c5ba0f5414e97fba8a8f07bc14dde6cc26189f1bfbba00490`.
The ROM SHA-256 matched the expected PokemonStart v0.15 build
`48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12`.
The cold bridge also saved a repo-external screenshot. A research savestate is
never counted as persistence evidence. This harness does not change P-direct,
P-reanchor, the Money GUI, M5A completion, M5B, or M5C status.

## Stable bootstrap repeatability (2026-10-06)

The launcher now refreshes one repo-external
`$TMPDIR/pokemonstart-mgba-harness/bootstrap/bridge-current.lua` path
atomically for each session. The file contents receive a fresh random token,
fresh ephemeral `127.0.0.1` port, disposable save path, and session artifact
directory; the path itself stays fixed so mGBA's Script MRU can be reused.
Startup UI queries are read-only and bounded until the exact process exposes
Apple/mGBA/File/Tools and `Tools -> Scripting...`. ScriptingView is identified
by its source-backed Apple/mGBA/File menu and `Load script...`/`Reset` items,
without requiring an AX window count. First enrollment uses the uniquely
identified chooser; later launches require the exact stable path in
`Load recent script`.

Two consecutive fresh mGBA 0.10.5 processes passed this bootstrap on the exact
ROM: first launch enrolled the stable path through the chooser, second launch
used the MRU entry. Each authenticated over loopback, returned `POKEMON FIRE` /
`AGB-BPRJ`, passed health, uniquely rediscovered Money at `0x0202571c` with
value `1,234,568`, and shut down with the disposable save SHA unchanged at
`35fd9c501a23484c5ba0f5414e97fba8a8f07bc14dde6cc26189f1bfbba00490`.
Neither cycle sent controller input, wrote RAM, or performed a normal save.

Automated normal SAVE remains blocked at runtime-state corroboration. After
Continue, the field menu was visibly open, but the pinned addresses
`sStartMenuCallback=0x02037024`, `sStartMenuCursorPos=0x02037028`,
`sNumStartMenuItems=0x02037029`, and `sStartMenuOrder=0x0203702A` all read zero
while the menu was displayed. The implementation stopped there without
selecting SAVE or confirming a dialog. No save/cold-reload transition from this
automation attempt is claimed. The observed contradiction must be resolved
against the exact build before normal SAVE automation can continue.
