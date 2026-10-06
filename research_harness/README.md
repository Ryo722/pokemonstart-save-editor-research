# Local mGBA bridge

`mgba_bridge.lua` is a checked-in template for mGBA 0.10.x Tools → Scripting.
`pokemonstart_mgba_harness.py` generates a private session copy with a random token,
ephemeral port, and exact working paths. Do not load the template directly.

The Python process listens only on `127.0.0.1`. The Lua script connects outbound,
authenticates with the random token, and accepts a small tab-delimited command set.
All memory reads are bounded to GBA EWRAM/IWRAM; writes are disabled until the
controller proves a unique live Money address and arms exactly those four bytes.
The Lua side repeats the RAM boundary and write-envelope checks.

The initial runner creates a disposable ROM/save pair outside Git, checks the
private source files, performs a read-only Money search, and supports the
bounded RAM canary and controller input. The normal game SAVE was performed
manually on the disposable save. The cold-only `--cold-resume` mode reuses that
save and automates attachment to a fresh mGBA 0.10.5 process using the
source-backed ScriptingView menu predicate and exact generated bridge path. It
performs read-only Money rediscovery and never repeats the RAM write or game
save. Persistence evidence requires normal SAVE, process shutdown, cold reload,
live RAM verification, and `.sav` verification; a savestate is never sufficient.

For cold launches, the runner atomically refreshes one repo-external
`bridge-current.lua` under the temporary harness root with a new token and
ephemeral loopback port. It waits for the exact process's normal menu structure
before UI actions. Once enrolled, it loads that stable path through File → Load
recent script; the native chooser is used only for first enrollment. The
two-cycle `--bootstrap-proof` mode validates this path without controller input,
RAM writes, or a game save.

Run focused synthetic tests with `python3 -m unittest tests.test_mgba_harness -v`.
