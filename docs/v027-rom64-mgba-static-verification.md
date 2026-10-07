# PokemonStart v0.27 rom64 mGBA build, static verification

Disposition: **STATIC_VERIFICATION_SUFFICIENT_FOR_LATER_BOUNDED_TESTING**.
This is a bounded static inspection record, not a runtime proof, review,
adoption decision, or authorization to execute the artifact. It was produced
in a session separate from the ongoing v0.27 ROM/save investigation and does
not depend on it.

Authority used: static inspection and optional scratch-source build only.
Nothing was executed, installed, or added to PATH; no Wine/CrossOver; no
GitHub mutation other than pushing this record. The ZIP and extracted binaries
stay private and are not committed (see [CONTRIBUTING](../CONTRIBUTING.md)).

Evidence labels: `INDEPENDENTLY_REPRODUCED`, `UPSTREAM_MGBA_SOURCE_EVIDENCE`,
`UPSTREAM_POKEMONSTART_EVIDENCE`, `PRIVATE_BINARY_STATIC_VERIFICATION`,
`HYPOTHESIS_UNVERIFIED`.

## ARTIFACT_IDENTITY

Artifact: Human-provided `mGBA-celio-2.0.0-rom64-win64.zip`.

| Item | SHA-256 |
|---|---|
| ZIP (37,814,440 bytes) | `7a3abada5655e60a039029f281a3a21401efcdc7346bb7dead373776a46ebf96` |
| `mGBA-celio-rom64/mGBA.exe` | `69afb3724a77281a4e8d532e8413186b99869b6f7d167a7a9c06f11cf3cee473` |
| `mGBA-celio-rom64/readme.txt` | `226809dc20368e2a44bd7057283b3e0e226fc447ae08310f5066be329bb2fef9` |
| updater-stub embedded in `mGBA.exe` `.rdata` (245,248 bytes) | `b65545210e51aa769cdd000ae94dd3861009b83e6f76a80e8d2759d9960c68a3` |
| `Qt5Core.dll` | `47ee86118fbe5d4605be0194fda92e9528bbae478cf1266e07f5315090115d57` |
| `Qt5Network.dll` | `49ac1fa977e0ae3ffc2e57d35dd7f3aa3c38cf2dfbb2627820de2877c943acd0` |
| `lua54.dll` | `7df433c01c1b46f987ce5fd7744257d1f413e268e8e9d7e1b0e8e788f31c5847` |
| `libzip.dll` | `67c521647ba161a42325e92cb949ec5913463386d722d97f8ac347349b1837af` |

- `INDEPENDENTLY_REPRODUCED`: the ZIP hash equals the GitHub Release API
  `digest` of asset `mGBA-celio-2.0.0-rom64-win64.zip` on release
  `rom64-2.0.0` of `onikoro334274-cell/mGBA_celio_edition` (uploaded
  2026-10-07T15:03:00Z by the repository owner). The local download's
  `kMDItemWhereFroms` points at that repository's release-assets URL.
- Inventory: 48 entries, all under `mGBA-celio-rom64/`: one `mGBA.exe`,
  one `readme.txt`, 46 DLLs (root, `audio/`, `imageformats/`,
  `mediaservice/`, `platforms/`, `styles/`). No scripts, config files or
  licence texts.
- Archive anomalies: none. No path traversal, absolute paths, symlinks,
  encryption, duplicate names, local/central header mismatches, gaps,
  overlaps or trailing data; CRC test clean.
- `INDEPENDENTLY_REPRODUCED`: **all 46 DLLs are byte-identical** to files in
  official MSYS2 `mingw64` packages fetched from `repo.msys2.org`, including
  qt5-base `5.15.18+kde+r109-4`, qt5-multimedia `5.15.18-1`, lua `5.4.8-1`,
  libzip `1.11.4-1`, icu `78.2-1`, gcc-libs `15.2.0-13`, glib2 `2.86.4-1`,
  sqlite3 `3.51.2-1`, zlib `1.3.2-1`. Package pacman signatures were not
  verified (HTTPS transport only).

## STATIC_BINARY_FACTS

`PRIVATE_BINARY_STATIC_VERIFICATION` for `mGBA.exe`:

- PE32+ x86-64, Windows GUI subsystem; HIGH_ENTROPY_VA, DYNAMIC_BASE,
  NX_COMPAT; manifest `requestedExecutionLevel asInvoker`.
- Toolchain: MSYS2 MINGW64 (msvcrt), GNU ld 2.46, GCC 15.2, LTO
  (`.lto_priv` symbols). Not stripped: COFF symbol table present; DWARF
  exists only for MinGW CRT objects and contains no builder-specific paths.
- Link timestamp 2026-10-07T14:45:44Z; embedded updater-stub 14:44:32Z.
- Version resource: FileVersion `0.11.0.0`, CompanyName `endrift`,
  ProductVersion `mgba`, exactly as `res/mgba.rc.in` would produce.
- Embedded version globals, read through the symbol table:
  `gitCommit = 3da13060a586f2da8eb4ecbb167f642e2e4889c2`,
  `gitCommitShort = 3da13060a-dirty`, `gitBranch = (unknown)`,
  `gitRevision = 9007`, `projectVersion = 2.0.0`.
- Signing: no Authenticode signature (Security Directory empty); bundled
  DLLs also unsigned, which is normal for MSYS2.
- No packing or obfuscation: standard sections, maximum entropy 6.70; the
  overlay is exactly the COFF symbol and string tables.
- No `rom64`, `64MiB`, `0x0A000000` or PokemonStart-specific strings. Expected,
  because the source change adds no strings.
- Direct imports: Qt5 Core/Gui/Widgets/Network/Multimedia, libepoxy,
  freetype, json-c, lua54, libpng, sqlite3, zlib, libzip, libstdc++,
  libgcc_s, libwinpthread, plus system KERNEL32, msvcrt, WS2_32, SHELL32
  (`SHGetKnownFolderPath`), SHLWAPI, ole32, dwmapi. No SDL import, although
  `readme.txt` mentions SDL. That is a minor doc inconsistency.

## ROM64_CORRESPONDENCE

Freshly fetched upstream (`UPSTREAM_MGBA_SOURCE_EVIDENCE`):

- `refs/heads/rom64` = `refs/tags/rom64-2.0.0` =
  `770ab0bb8a19fdd11303ea4c42be0f9b81fb6959` (matches the earlier locator).
- Parent base: `3da13060a586f2da8eb4ecbb167f642e2e4889c2` (Exormeter tag
  `2.0.0`, lightweight). Delta: `4857dec6` "GBA: Support 64MiB ROMs"
  (`src/gba/gba.c`, `src/gba/memory.c`, `version.cmake`), then doc-only
  `a1894bcf` (readme.txt) and `770ab0bb` (README.md).
- `version.cmake` lets `ENV{MGBA_GIT_COMMIT}` override `GIT_COMMIT`. Upstream
  celio 2.0.0's `mGBACelioServer.lua` checks
  `system.commit ~= "3da13060…"`, and the upstream celio 2.0.0 win64 exe
  embeds the same commit. **The embedded commit string is therefore not
  provenance evidence.**

`UPSTREAM_POKEMONSTART_EVIDENCE`: PokemonStart `main` =
`23007d4ef95ae1dc8788fbb34c8f1d93118231d1` ("PokemonStart_v0.27.pks") credits
"64MB の ROM に対応させた mGBA" with source link
`…/mGBA_celio_edition/tree/rom64`. It does not link a specific binary asset.

Binary-to-source evidence (`PRIVATE_BINARY_STATIC_VERIFICATION`, disassembly):

1. ROM load (`GBALoadROM`, inlined into `_GBACoreLoadROM`):
   `cmpq $0x4000000, pristineRomSize` → `map(vf, 0x4000000)` →
   `romSize = pristineRomSize`, then the
   `if (romSize <= GBA_SIZE_ROM0) pristineRomSize = GBA_SIZE_ROM0` tail.
2. `GBALoad8/16/32`, `GBALoadMultiple`, `GBAPatch*`, `_agbPrintStore`:
   `cmp romSize, 0x2000001; sbb; and 0xFE000000; add 0x3FFFFF{F,E,C}`. This
   is the compiled `GBA_ROM_MASK(MEM, N)` macro; unmodified upstream would use
   a fixed `and $0x1FFFFF{F,E,C}`.
3. `_pristineCow`: `VirtualAlloc` size `romSize > 32MiB ? 0x4000000 : 0x2000000`.
4. `version.cmake` override: full `gitCommit` lacks `-dirty` while
   `gitCommitShort` has it, which is consistent with the override being used.
5. `readme.txt` is byte-identical to `rom64:readme.txt`; link time falls
   between commit `4857dec6` (14:43:54Z) and release creation (14:48:57Z).
6. About 7,100 defined function symbols all resolve to mGBA source
   identifiers, mGBA macro-generated bindings (`_mSTStructBinding*`,
   `_mLOG_CAT_*`, ARM/Thumb decoder tables), or MinGW CRT/strsafe. No foreign
   library or unexplained function names. Qt classes all exist in source
   (plus uic-generated `Ui_*`).

Not proven: `gitCommitShort = 3da13060a-dirty` and `gitRevision = 9007` (the
commit count at `3da13060`; `4857dec6` would be 9008) show the build tree's
HEAD was `3da13060` with uncommitted changes, not `4857dec6`/`770ab0bb`. Static
inspection cannot prove that the dirty working tree equalled `4857dec6`
exactly. A reproducible build was **skipped** because no mingw-w64 toolchain
is installed locally, and installing one was out of scope.

Classification: **`STRONGLY_CORROBORATED`**. The basis is the official
release channel with matching digest, plus every code hunk of the rom64
change confirmed at instruction level, with no foreign code. It does not rest
on the commit string. Exact build-tree identity with `770ab0bb` remains
`PLAUSIBLE_BUT_NOT_PROVEN`.

## SECURITY_OBSERVATIONS

Expected: a standard MSYS2 dynamic-link Qt5 deployment (windeployqt layout).
All third-party DLLs match official packages byte-for-byte.

Nothing unusual found:

- No strings for PowerShell/cmd, webhooks, Run keys, scheduled tasks,
  browser credential stores, or LOLBins.
- `mGBA.exe` has no registry, persistence, credential, or injection-related
  imports. Registry/CreateProcess imports exist only in MSYS2-identical Qt5Core,
  glib and Qt platform plugins.

Upstream-standard features to be aware of (`UPSTREAM_MGBA_SOURCE_EVIDENCE`
plus confirmed strings):

1. **Built-in application updater.** It fetches `https://mgba.io/latest.ini`,
   downloads an update, extracts the embedded updater-stub and `_execl`s it to
   replace files. The stub imports no networking and only extracts a
   previously downloaded archive. `updateAutoCheck` defaults to 0.
   `HYPOTHESIS_UNVERIFIED`: the channel resolves to `stable` (branch
   `(unknown)`, version `2.0.0`), and `2.0.0` > upstream `0.10.5`, so no
   update should be offered. On the `dev` channel, rev 9154 > 9007 would
   offer one, and accepting it would **replace this build with official mGBA
   and lose rom64 support**.
2. **No OpenSSL bundled.** Qt5Network references `libssl-3-x64` /
   `libcrypto-3-x64`, which are not shipped. HTTPS works only if they are on
   the DLL search path.
3. **Sockets.** WS2_32 socket/listen/connect are used by Celio link and
   scripting sockets. Other upstream URLs: Forwarder kit and chip-assets
   (GitHub).
4. **Lua.** `lua54.dll` exposes `os.execute`; any loaded Lua script runs with
   full user privileges.
5. **Not bundled.** No licence texts (MPL/LGPL) and no `mGBACelioServer.lua`.
   Neither is a security issue.

Requiring further inspection: no blocker. The only open item is a full
reproducible-build comparison of `mGBA.exe`.

## EXECUTION_READINESS

**`STATIC_VERIFICATION_SUFFICIENT_FOR_LATER_BOUNDED_TESTING`**

The release provenance and digest match. Every third-party DLL is
byte-identical to an official package. The single unique binary (exe plus
embedded stub) contains exactly the rom64 change with no foreign code, and no
suspicious import or string was found. Missing signatures are expected for
this distribution form. The residual uncertainty (unproven build-tree
identity, unsigned exe) is not a blocker and is handled by isolation during
any later runtime test.

## IF_RUNTIME_TESTING_IS_NEEDED

Runtime execution is **not** authorized by this record.

- Executable: `mGBA-celio-rom64\mGBA.exe` from a fresh extraction of the
  ZIP above. Re-check SHA-256 `69afb372…c53fdfbac` before launch.
- Why static analysis is insufficient: it cannot show actual guest-visible
  mapping (second half at `0x0A000000`–`0x0BFFFFFF`, first half at
  `0x08`/`0x0C`), or interactions with savedata/EEPROM, DMA and savestates.
  Source still keeps 32MiB in the `cart0` memory-block descriptor and rejects
  IPS/UPS patches larger than 32MiB.
- Inputs: a **copy** of the v0.27 ROM of exactly `0x4000000` bytes (other
  sizes take the legacy path) and a **copy** of the target `.sav`; originals
  kept read-only elsewhere.
- Expected test: load, pass title/initialization, reach second-half-dependent
  content. Compare bus reads `emu:read8(0x0A000000+x)` (not the `cart0`
  domain) against ROM file offset `0x2000000+x`. Load/write the save copy and
  diff hashes.
- Isolation: a disposable Windows environment (Windows Sandbox or a VM with
  snapshot rollback). Do not touch the host mGBA, PATH or file associations.
  Prefer no network and do not use Celio link. Never check for or apply
  updates. Load no external Lua scripts. Use a portable or throw-away profile.
- Remaining risks: unsigned exe with unproven exact build tree; possible
  32MiB-only residual paths producing wrong results or crashes; accidental
  updater use replacing the build; full-privilege Lua scripts.
