"""Bounded local mGBA research transport and Money proof preparation.

This is research infrastructure, not a save editor or a public network service.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import time

import pokemonstart_save_verifier as verifier

REPO = Path(__file__).resolve().parent
HOST_SCOPE = REPO.parents[1]
ROM_SHA256 = "48ecc0ef2df7fe9bbe389f0adbfbe7e277696a461ec631c65bcdf750898e4e12"
MAX_REQUEST = 256
MAX_REPLY = 1100
MAX_READ = 512
RAM = ((0x02000000, 0x02040000), (0x03000000, 0x03008000))
COMMANDS = frozenset({"health", "meta", "read8", "read16", "read32", "read_range",
                      "get_keys", "set_keys", "frames", "screenshot", "save_state",
                      "load_state", "load_save", "reset", "arm_money", "write8", "write16", "write32"})
OWNED_PIDS: set[int] = set()


class HarnessError(ValueError):
    pass


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_loopback(host: str) -> None:
    if host != "127.0.0.1":
        raise HarnessError("IPv4 loopback address required")


def ram_range(address: int, width: int) -> bool:
    return type(address) is int and type(width) is int and width > 0 and any(
        lo <= address and address + width <= hi for lo, hi in RAM
    )


def validate_command(op: str, args: tuple[int, ...], allowed: frozenset[int],
                     money_candidate: int | None = None) -> None:
    if op not in COMMANDS:
        raise HarnessError("unknown command")
    if any(type(a) is not int or a < 0 or a > 0xFFFFFFFF for a in args):
        raise HarnessError("invalid numeric argument")
    if op in ("health", "meta", "get_keys", "load_save", "reset"):
        expected = 0
    elif op in ("read8", "read16", "read32", "set_keys", "frames", "screenshot", "save_state", "load_state"):
        expected = 1
    else:
        expected = 2
    if len(args) != expected:
        raise HarnessError("wrong argument count")
    if op.startswith("read") and op != "read_range":
        if not ram_range(args[0], int(op[4:]) // 8):
            raise HarnessError("read outside RAM")
    if op == "read_range" and not (1 <= args[1] <= MAX_READ and ram_range(*args)):
        raise HarnessError("read range outside bounded RAM")
    if op == "set_keys" and args[0] > 0x3FF:
        raise HarnessError("GBA key mask out of range")
    if op == "frames" and not 1 <= args[0] <= 120:
        raise HarnessError("frame count out of range")
    if op in ("screenshot", "save_state", "load_state") and not 1 <= args[0] <= 99:
        raise HarnessError("artifact id out of range")
    if op == "arm_money":
        if (allowed or money_candidate != args[0] or not ram_range(args[0], 4)
                or args[0] % 4):
            raise HarnessError("money arm rejected")
    if op.startswith("write"):
        width = int(op[5:]) // 8
        address, value = args
        if not ram_range(address, width) or address % width or value >= 1 << (width * 8):
            raise HarnessError("invalid RAM write")
        if not all(address + i in allowed for i in range(width)):
            raise HarnessError("write not allowlisted")


def parse_line(line: bytes, limit: int = MAX_REPLY) -> tuple[str, ...]:
    if len(line) > limit or not line.endswith(b"\n") or b"\r" in line or b"\x00" in line:
        raise HarnessError("malformed or oversized protocol line")
    try:
        fields = line[:-1].decode("utf-8").split("\t")
    except UnicodeDecodeError as exc:
        raise HarnessError("invalid UTF-8") from exc
    if not fields or not fields[0] or any("\n" in field for field in fields):
        raise HarnessError("malformed fields")
    return tuple(fields)


def encode_command(op: str, args: tuple[int, ...]) -> bytes:
    payload = ("\t".join([op, *(str(a) for a in args)]) + "\n").encode("ascii")
    if len(payload) > MAX_REQUEST:
        raise HarnessError("request too large")
    return payload


def validate_reply(op: str, reply: tuple[str, ...], args: tuple[int, ...]) -> None:
    if reply[0] == "error":
        if len(reply) != 2:
            raise HarnessError("malformed error response")
        return
    if reply[0] != "ok" or len(reply) != (4 if op == "meta" else 2):
        raise HarnessError("malformed success response")
    if op == "meta":
        if not reply[1].isdigit() or any(not field for field in reply[2:]):
            raise HarnessError("malformed metadata")
    elif op == "read_range":
        expected = args[1] * 2
        if len(reply[1]) != expected or any(c not in "0123456789abcdef" for c in reply[1]):
            raise HarnessError("malformed memory range")
    elif not reply[1].isdigit():
        raise HarnessError("malformed numeric response")


def outside_repo(path: Path) -> None:
    if path.resolve().is_relative_to(REPO):
        raise HarnessError("session artifact inside repository")


def render_bridge(host: str, port: int, token: str, working_save: Path, artifacts: Path) -> str:
    require_loopback(host)
    if not 1 <= port <= 65535 or len(token) < 32:
        raise HarnessError("invalid session configuration")
    for path in (working_save, artifacts):
        outside_repo(path)
    template = (REPO / "research_harness" / "mgba_bridge.lua").read_text()
    values = {"@@HOST@@": host, "@@PORT@@": str(port), "@@TOKEN@@": token,
              "@@SAVE@@": json.dumps(str(working_save), ensure_ascii=False)[1:-1],
              "@@ARTIFACT_DIR@@": json.dumps(str(artifacts), ensure_ascii=False)[1:-1]}
    for marker, value in values.items():
        template = template.replace(marker, value)
    return template


def save_money(raw: bytes) -> tuple[int, int, int, bytes]:
    result = verifier.verify_bytes(raw)
    active = result.slots[result.active_slot]
    key = int.from_bytes(active.section(0).data[0xF20:0xF24], "little")
    if key != 0:
        raise HarnessError("Money proof requires the observed zero encryption key")
    block = active.section(1).data
    money = int.from_bytes(block[0x290:0x294], "little") ^ key
    saved = int.from_bytes(active.section(2).data[0x210:0x214], "little")
    return money, result.party_count, saved, block[0x38:0x38 + 100]


def independent_save_money(raw: bytes) -> dict:
    """Decode the narrow two-valid-slot proof save without calling the verifier."""
    if len(raw) not in (0x20000, 0x20010):
        raise HarnessError("independent money audit: save size")
    slots = []
    for slot in (0, 1):
        sections = {}
        counters = set()
        for position in range(14):
            start = (slot * 14 + position) * 0x1000
            sector = raw[start:start + 0x1000]
            section_id = struct.unpack_from("<H", sector, 0xFF4)[0]
            signature = struct.unpack_from("<I", sector, 0xFF8)[0]
            counter = struct.unpack_from("<I", sector, 0xFFC)[0]
            if section_id > 13 or section_id in sections or signature != 0x08012025:
                raise HarnessError("independent money audit: sector metadata")
            sections[section_id] = sector
            counters.add(counter)
        if len(sections) != 14 or len(counters) != 1:
            raise HarnessError("independent money audit: slot structure")
        slots.append((counters.pop(), sections))
    first, second = slots[0][0], slots[1][0]
    if (first - second) & 0xFFFFFFFF == 1:
        active_slot = 0
    elif (second - first) & 0xFFFFFFFF == 1:
        active_slot = 1
    else:
        raise HarnessError("independent money audit: counter transition")
    counter, sections = slots[active_slot]
    key = struct.unpack_from("<I", sections[0], 0xF20)[0]
    money = struct.unpack_from("<I", sections[1], 0x290)[0] ^ key
    saved = struct.unpack_from("<I", sections[2], 0x210)[0]
    party_count = sections[1][0x34]
    party0_sha = hashlib.sha256(sections[1][0x38:0x38 + 100]).hexdigest()
    return {"active_slot": active_slot, "counter": counter, "key": key,
            "money": money, "saved": saved, "party_count": party_count,
            "party0_sha256": party0_sha}


def discover_money(ewram: bytes, money: int, party_count: int, saved: int, party0: bytes) -> int:
    if len(ewram) != 0x40000 or not 0 <= money <= 9_999_999 or not 0 <= party_count <= 6:
        raise HarnessError("invalid discovery inputs")
    needle = money.to_bytes(4, "little")
    candidates = []
    start = 0
    while True:
        pos = ewram.find(needle, start)
        if pos < 0:
            break
        base = pos - 0x290
        if (base >= 0 and base + 0x1204 <= len(ewram)
                and ewram[base + 0x34] == party_count
                and ewram[base + 0x38:base + 0x38 + 100] == party0
                and int.from_bytes(ewram[base + 0x1200:base + 0x1204], "little") == saved):
            candidates.append(0x02000000 + pos)
        start = pos + 1
    if len(candidates) != 1:
        raise HarnessError(f"Money location not unique: {len(candidates)} supported candidates")
    return candidates[0]


class Bridge:
    def __init__(self, conn: socket.socket, token: str, log_path: Path,
                 artifact_dir: Path | None = None):
        self.conn = conn
        self.conn.settimeout(30)
        self.file = conn.makefile("rb")
        self.allowed: frozenset[int] = frozenset()
        self.money_candidate: int | None = None
        self.created_states: set[int] = set()
        self.log_path = log_path
        self.artifact_dir = artifact_dir or log_path.parent
        try:
            hello = self._read(MAX_REQUEST)
        except (HarnessError, OSError):
            conn.close()
            raise
        if hello != ("hello", token):
            conn.close()
            raise HarnessError("bridge authentication failed")
        self.log("authenticated")

    def log(self, event: str, **details) -> None:
        with self.log_path.open("a", encoding="utf-8") as output:
            output.write(json.dumps({"time": time.time(), "event": event, **details}, sort_keys=True) + "\n")

    def _read(self, limit: int) -> tuple[str, ...]:
        line = self.file.readline(limit + 1)
        return parse_line(line, limit)

    def command(self, op: str, *args: int) -> tuple[str, ...]:
        validate_command(op, args, self.allowed, self.money_candidate)
        if op == "load_state" and args[0] not in self.created_states:
            raise HarnessError("savestate was not created by this session")
        payload = encode_command(op, args)
        self.conn.sendall(payload)
        try:
            reply = self._read(MAX_REPLY)
            validate_reply(op, reply, args)
        except (HarnessError, OSError):
            self.conn.close()
            raise
        self.log("command", op=op, args=args, reply=reply if op != "read_range" else (reply[0], "hex-redacted"))
        if reply[0] != "ok":
            raise HarnessError(f"bridge {op}: {reply}")
        if op == "save_state":
            self.created_states.add(args[0])
        if op in ("save_state", "screenshot"):
            name = ("state-" + str(args[0]) + ".ss0" if op == "save_state"
                    else "screen-" + str(args[0]) + ".png")
            artifact = self.artifact_dir / name
            if not artifact.is_file():
                raise HarnessError(f"artifact was not created: {name}")
            self.log("artifact", name=name, sha256=sha(artifact))
        return reply[1:]

    def arm_money(self, address: int, expected: int) -> None:
        self.command("arm_money", address, expected)
        self.allowed = frozenset(range(address, address + 4))
        self.log("money_allowlist", address=address)

    def read_ewram(self) -> bytes:
        data = bytearray()
        for offset in range(0, 0x40000, MAX_READ):
            part = self.command("read_range", 0x02000000 + offset, MAX_READ)
            if len(part) != 1 or len(part[0]) != MAX_READ * 2:
                raise HarnessError("short EWRAM read")
            data.extend(bytes.fromhex(part[0]))
        return bytes(data)


def prepare(rom: Path, save: Path, base: Path | None = None) -> dict:
    for source in (rom, save):
        resolved = source.resolve()
        if not resolved.is_relative_to(HOST_SCOPE) or resolved.is_relative_to(REPO):
            raise HarnessError("private input must be in the host workspace and outside Git")
    if not rom.is_file() or not save.is_file() or rom.resolve() == save.resolve():
        raise HarnessError("exact ROM and save file paths required")
    rom_hash = sha(rom)
    if rom_hash != ROM_SHA256:
        raise HarnessError("ROM build SHA-256 mismatch")
    source_hash = sha(save)
    raw = save.read_bytes()
    money, party_count, saved, party0 = save_money(raw)
    if money != 1_234_567:
        raise HarnessError(f"unexpected source money {money}")
    root = base or Path(tempfile.gettempdir()) / "pokemonstart-mgba-harness"
    outside_repo(root)
    root.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix="session-", dir=root))
    working_rom = session / "research.gba"
    working_save = session / "research.sav"
    shutil.copyfile(rom, working_rom)
    shutil.copyfile(save, working_save)
    if sha(working_rom) != ROM_SHA256 or sha(working_save) != source_hash or sha(save) != source_hash:
        raise HarnessError("input changed during private copy")
    return {"session": session, "rom": working_rom, "source_rom": rom, "save": working_save,
            "source": save, "source_sha": source_hash, "rom_sha": rom_hash,
            "money": money, "party_count": party_count, "saved": saved, "party0": party0}


def find_live_money(bridge: Bridge, prepared: dict, expected: int, saved: int,
                    screenshot_base: int = 10) -> int:
    """Read-only scan with operator-inspected, bounded title-screen navigation."""
    for attempt in range(12):
        bridge.command("screenshot", screenshot_base + attempt)
        ewram = bridge.read_ewram()
        candidate = None
        try:
            candidate = discover_money(ewram, expected, prepared["party_count"], saved,
                                       prepared["party0"])
        except HarnessError as exc:
            if "not unique: 0 supported" not in str(exc):
                raise
        print(f"Inspect screen-{screenshot_base + attempt}.png; candidate={hex(candidate) if candidate else 'none'}", flush=True)
        choice = input("Inspected action [ready/start/a/b/wait/stop]: ").strip().lower()
        if choice == "stop":
            raise HarnessError("operator stopped before live Money discovery")
        if choice == "ready":
            if candidate is None:
                raise HarnessError("cannot accept live Money before unique discovery")
            bridge.log("screen_confirmed", screenshot=screenshot_base + attempt,
                       address=candidate)
            bridge.money_candidate = candidate
            return candidate
        mask = {"start": 1 << 3, "a": 1, "b": 1 << 1, "wait": 0}.get(choice)
        if mask is None:
            raise HarnessError("unrecognized controller action")
        bridge.command("set_keys", mask)
        bridge.command("frames", 2)
        bridge.command("set_keys", 0)
        bridge.command("frames", 90)
    raise HarnessError("live Money not found after bounded inspected actions")


def mgba_pids() -> set[int]:
    result = subprocess.run(["/usr/bin/pgrep", "-x", "mGBA"], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise HarnessError("cannot inspect mGBA process identity")
    return {int(line) for line in result.stdout.splitlines() if line.isdigit()}


def launch_owned_mgba(executable: Path, rom: Path) -> int:
    """Launch a separate macOS app instance; refuse if no unique new PID appears."""
    before = mgba_pids()
    app = executable.parents[2]
    subprocess.run(["/usr/bin/open", "-n", "-a", str(app), "--args", str(rom)], check=True)
    for _ in range(30):
        new = mgba_pids() - before
        if len(new) == 1:
            pid = next(iter(new))
            OWNED_PIDS.add(pid)
            return pid
        if len(new) > 1:
            raise HarnessError("ambiguous new mGBA processes")
        time.sleep(0.25)
    raise HarnessError("mGBA did not start a distinct process")


def stop_owned_mgba(pid: int) -> None:
    if pid not in mgba_pids():
        raise HarnessError("owned mGBA process already exited")
    os.kill(pid, signal.SIGTERM)
    for _ in range(60):
        if pid not in mgba_pids():
            OWNED_PIDS.discard(pid)
            return
        time.sleep(0.25)
    raise HarnessError("owned mGBA process did not stop")


def stop_leftover_owned_processes() -> None:
    for pid in tuple(OWNED_PIDS):
        try:
            stop_owned_mgba(pid)
        except (HarnessError, OSError):
            pass


atexit.register(stop_leftover_owned_processes)


def scripting_view_predicate(menu_bar: tuple[str, ...], file_items: tuple[str, ...]) -> bool:
    """Source-backed mGBA 0.10.5 ScriptingView identity check; AX windows are irrelevant."""
    return (all(name in menu_bar for name in ("Apple", "mGBA", "File"))
            and "Tools" not in menu_bar
            and "Load script..." in file_items
            and "Reset" in file_items)


def normal_mgba_predicate(menu_bar: tuple[str, ...], tools_items: tuple[str, ...]) -> bool:
    return (all(name in menu_bar for name in ("Apple", "mGBA", "Tools", "File"))
            and "Scripting..." in tools_items)


def exact_recent_script(entries: tuple[str, ...], path: Path) -> bool:
    return entries.count(str(path.resolve())) == 1


def stable_bridge_path() -> Path:
    """One stable, repo-external script path under the private temp harness root."""
    path = Path(tempfile.gettempdir()) / "pokemonstart-mgba-harness" / "bootstrap" / "bridge-current.lua"
    outside_repo(path)
    return path


def write_stable_bridge(host: str, port: int, token: str, working_save: Path,
                        artifacts: Path) -> Path:
    """Atomically replace the session payload while preserving its Script MRU path."""
    target = stable_bridge_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = render_bridge(host, port, token, working_save, artifacts)
    pending = target.with_name(f"bridge-current-{secrets.token_hex(8)}.pending.lua")
    pending.write_text(payload, encoding="utf-8")
    os.replace(pending, target)
    return target


def _osascript(pid: int, body: str) -> str:
    if type(pid) is not int or pid <= 0:
        raise HarnessError("invalid dedicated mGBA PID")
    source = ("tell application \"System Events\"\n"
              f"  tell first application process whose unix id is {pid}\n"
              f"    {body}\n"
              "  end tell\nend tell")
    result = subprocess.run(["/usr/bin/osascript", "-e", source], capture_output=True,
                            text=True, timeout=20)
    if result.returncode:
        raise HarnessError(f"osascript failed for PID {pid}: {result.stderr.strip()}")
    return result.stdout.strip()


def _menu_snapshot(pid: int) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Read the menu bar, Tools items, and File items from this exact process."""
    body = ("set menuNames to name of every menu bar item of menu bar 1\n"
            "set toolsNames to {}\n"
            "set fileNames to {}\n"
            "if menuNames contains \"Tools\" then set toolsNames to name of every menu item of "
            "menu 1 of menu bar item \"Tools\" of menu bar 1\n"
            "if menuNames contains \"File\" then set fileNames to name of every menu item of "
            "menu 1 of menu bar item \"File\" of menu bar 1\n"
            "set AppleScript's text item delimiters to ASCII character 30\n"
            "set menuText to menuNames as text\n"
            "set toolsText to toolsNames as text\n"
            "set fileText to fileNames as text\n"
            "return menuText & (ASCII character 29) & toolsText & (ASCII character 29) & fileText")
    encoded = _osascript(pid, body)
    parts = encoded.split("\x1d")
    if len(parts) != 3:
        raise HarnessError(f"unexpected mGBA menu response for PID {pid}: {encoded!r}")
    split_names = lambda value: tuple(item.strip() for item in value.split("\x1e") if item.strip())
    return split_names(parts[0]), split_names(parts[1]), split_names(parts[2])


def mgba_ui_state(pid: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Read only menu bar and File menu names (no window-count assumption)."""
    menus, _, file_items = _menu_snapshot(pid)
    return menus, file_items


def _process_alive(pid: int) -> bool:
    return pid in mgba_pids()


def wait_normal_mgba_ready(pid: int, timeout: float = 30.0,
                           poll_interval: float = 0.4) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Do read-only AX queries until the exact new process exposes normal menus."""
    deadline = time.monotonic() + timeout
    last_error = "no menu snapshot"
    while time.monotonic() < deadline:
        if not _process_alive(pid):
            raise HarnessError(f"dedicated mGBA PID {pid} exited during startup readiness")
        try:
            menus, tools, _ = _menu_snapshot(pid)
            if normal_mgba_predicate(menus, tools):
                return menus, tools
            last_error = f"normal menu predicate false: menus={menus!r}, Tools={tools!r}"
        except HarnessError as exc:
            # Early Qt/AX index failures are transient while this exact process forms its UI.
            last_error = str(exc)
        time.sleep(poll_interval)
    raise HarnessError(f"mGBA startup readiness timed out for PID {pid}: {last_error}")


def _click_menu(pid: int, menu: str, item: str) -> None:
    # Names are fixed call-site constants; no user or bridge value enters AppleScript syntax.
    deadline = time.monotonic() + 10
    while True:
        try:
            _osascript(pid, f"click menu item {json.dumps(item)} of menu 1 of menu bar item "
                            f"{json.dumps(menu)} of menu bar 1")
            return
        except HarnessError as exc:
            if ("-1719" not in str(exc) or not _process_alive(pid)
                    or time.monotonic() >= deadline):
                raise
            # -1719 can be a transient AX index while the same dedicated UI updates.
            time.sleep(0.25)


def _wait_scripting_view(pid: int, timeout: float = 10.0) -> tuple[tuple[str, ...], tuple[str, ...]]:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            menus, items = mgba_ui_state(pid)
            if scripting_view_predicate(menus, items):
                return menus, items
            last = f"menus={menus!r}, File={items!r}"
        except HarnessError as exc:
            last = str(exc)
        time.sleep(0.25)
    raise HarnessError(f"mGBA 0.10.5 ScriptingView predicate timed out for PID {pid}: {last}")


def mgba_recent_scripts(pid: int) -> tuple[str, ...]:
    body = ("set recentNames to name of every menu item of menu \"Load recent script\" of "
            "menu item \"Load recent script\" of menu 1 of menu bar item \"File\" of menu bar 1\n"
            "set AppleScript's text item delimiters to ASCII character 30\n"
            "return recentNames as text")
    try:
        result = _osascript(pid, body)
    except HarnessError as exc:
        if "Load recent script" in str(exc):
            return ()
        raise
    return tuple(item.strip() for item in result.split("\x1e") if item.strip())


def click_recent_script(pid: int, exact_path: Path) -> None:
    """Click only an exact path already observed in the recent-script submenu."""
    observed = mgba_recent_scripts(pid)
    target = str(exact_path.resolve())
    if observed.count(target) != 1:
        raise HarnessError("stable bridge path is not a unique Load recent script entry")
    _osascript(pid, f"click menu item {_applescript_string(target)} of menu \"Load recent script\" "
                    "of menu item \"Load recent script\" of menu 1 of menu bar item \"File\" "
                    "of menu bar 1")


def _applescript_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _target_process_ui_tree(pid: int) -> str:
    source = ("tell application \"System Events\"\n"
              f"tell first application process whose unix id is {pid}\n"
              "get entire contents\nend tell\nend tell")
    result = subprocess.run(["/usr/bin/osascript", "-e", source], capture_output=True,
                            text=True, timeout=20)
    if result.returncode:
        raise HarnessError(f"osascript UI tree failed for PID {pid}: {result.stderr.strip()}")
    return result.stdout


def _focus_exact_process(pid: int) -> None:
    """Make only the already-identified dedicated process the keyboard target."""
    _osascript(pid, "set frontmost to true")


def attach_cold_bridge_ui(pid: int, script: Path) -> dict:
    """Prefer the exact stable Script MRU entry; enroll once with a verified chooser."""
    ready_menus, ready_tools = wait_normal_mgba_ready(pid)
    _focus_exact_process(pid)
    _click_menu(pid, "Tools", "Scripting...")
    menus, items = _wait_scripting_view(pid)
    recent = mgba_recent_scripts(pid)
    target = str(script.resolve())
    if exact_recent_script(recent, script):
        click_recent_script(pid, script)
        return {"selected_path": target, "load_method": "recent", "automated": True,
                "ready_menus": ready_menus, "ready_tools": ready_tools}
    if target in recent:
        raise HarnessError("stable bridge path appears more than once in Script MRU")
    _focus_exact_process(pid)
    _click_menu(pid, "File", "Load script...")
    # The source-backed chooser title must identify exactly one window before any keys.
    window_check = ("set names to name of every window\n"
                    "set matches to 0\n"
                    "repeat with windowName in names\n"
                    "if windowName as text is \"Select script to load\" then set matches to matches + 1\n"
                    "end repeat\n"
                    "if matches is not 1 then return \"WINDOWS\" & (names as text) & \";MATCHES=\" & matches\n"
                    "return \"UNIQUE\"")
    deadline = time.monotonic() + 10
    while True:
        tree = _osascript(pid, window_check)
        if tree == "UNIQUE" or time.monotonic() >= deadline:
            break
        time.sleep(0.5)
    if tree != "UNIQUE":
        raise HarnessError(f"file chooser was not uniquely identified for PID {pid}: {tree}")
    print("COLD_FILE_CHOOSER=unique title='Select script to load'; hierarchy inspected read-only",
          flush=True)
    # Inspect this unique, source-backed Open panel before keyboard input.
    chooser_tree = _target_process_ui_tree(pid)
    if (chooser_tree.count("window Select script to load") < 1
            or chooser_tree.count("button Open of splitter group 1 of window Select script to load") != 1
            or chooser_tree.count("button Cancel of splitter group 1 of window Select script to load") != 1):
        raise HarnessError(f"mGBA script chooser tree is ambiguous for PID {pid}; accessible tree captured")
    # Require the Go to Folder sheet before typing; never send text to an unknown UI.
    _focus_exact_process(pid)
    _osascript(pid, 'keystroke "g" using {command down, shift down}')
    go_tree = ""
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        go_tree = _target_process_ui_tree(pid)
        go_parts = {part.strip() for part in go_tree.split(", ")}
        if "sheet 1 of window Select script to load of application process mGBA" in go_parts:
            break
        time.sleep(0.25)
    go_parts = {part.strip() for part in go_tree.split(", ")}
    expected_sheet = "sheet 1 of window Select script to load of application process mGBA"
    expected_field = "text field 1 of sheet 1 of window Select script to load of application process mGBA"
    if expected_sheet not in go_parts or expected_field not in go_parts:
        relevant = tuple(part for part in go_tree.split(", ")
                         if "sheet" in part or "text field" in part or "Go to" in part)
        raise HarnessError("Go to Folder sheet was not uniquely identified; no path text was sent; "
                           f"sheet_count={sum(part.startswith('sheet 1 of window Select script to load of application process mGBA') for part in go_parts)}, "
                           f"relevant_elements={relevant!r}")
    path_literal = _applescript_string(str(script.resolve()))
    _osascript(pid, f"keystroke {path_literal}")
    _osascript(pid, "keystroke return")
    time.sleep(0.5)
    selected_tree = _target_process_ui_tree(pid)
    preview_marker = f"static text {script.name} of scroll area"
    if (selected_tree.count(preview_marker) != 1
            or selected_tree.count("button Open of splitter group 1 of window Select script to load") != 1
            or "sheet 1 of window Select script to load" in selected_tree):
        raise HarnessError(f"exact generated Lua file is not uniquely previewed in mGBA chooser: {selected_tree}")
    _osascript(pid, "keystroke return")
    return {"selected_filename": script.name, "selected_path": str(script.resolve()),
            "open_activated": True, "load_method": "chooser-enrollment", "automated": True,
            "ready_menus": ready_menus, "ready_tools": ready_tools}


def prepare_bootstrap_proof(rom: Path, save: Path,
                            base: Path | None = None) -> dict:
    """Create a disposable read-only bootstrap clone from explicit inputs."""
    rom, save = rom.resolve(), save.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if (not rom.is_file() or not rom.is_relative_to(HOST_SCOPE) or rom.is_relative_to(REPO)
            or not save.is_file() or not save.is_relative_to(HOST_SCOPE)
            or save.is_relative_to(REPO)):
        raise HarnessError("explicit private ROM and save inputs are required")
    if sha(rom) != ROM_SHA256:
        raise HarnessError("bootstrap proof ROM build SHA-256 mismatch")
    input_before = sha(save)
    raw = save.read_bytes()
    verifier.verify_bytes(raw)
    decoded = independent_save_money(raw)
    root = base or Path(tempfile.gettempdir()) / "pokemonstart-mgba-harness"
    outside_repo(root)
    if not root.resolve().is_relative_to(temp_root):
        raise HarnessError("save automation workspace must be under the system temp root")
    root.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix="bootstrap-proof-", dir=root))
    working_rom, working_save = session / "research.gba", session / "research.sav"
    shutil.copyfile(rom, working_rom)
    shutil.copyfile(save, working_save)
    if sha(working_rom) != ROM_SHA256 or sha(working_save) != input_before or sha(save) != input_before:
        raise HarnessError("bootstrap clone copy verification or input immutability check failed")
    record = {"session": session, "rom": working_rom, "save": working_save,
              "input_save": save, "input_sha": input_before,
              "rom_sha": ROM_SHA256, "save_sha": sha(working_save),
              "decoded": decoded}
    (session / "audit.jsonl").write_text(json.dumps({
        "event": "bootstrap_proof_prepared", "git": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "mgba": subprocess.check_output(
            ["/Applications/mGBA.app/Contents/MacOS/mGBA", "--version"], text=True).strip(),
        "rom_sha": ROM_SHA256, "input_sha": input_before,
        "working_sha": record["save_sha"],
        "initial_decode": decoded, "session": session.name,
    }, sort_keys=True) + "\n", encoding="utf-8")
    return record


def bootstrap_repeatability(prepared: dict, mgba: Path, cycles: int = 2) -> list[dict]:
    """Prove consecutive cold launches load one stable MRU script read-only."""
    if cycles != 2:
        raise HarnessError("bootstrap proof requires exactly two fresh launches")
    version = subprocess.check_output([str(mgba), "--version"], text=True).strip()
    if "mGBA 0.10.5" not in version:
        raise HarnessError("stable Script MRU proof requires mGBA 0.10.5")
    original_working_sha = sha(prepared["save"])
    if original_working_sha != prepared["save_sha"]:
        raise HarnessError("working save changed before bootstrap proof")
    results = []
    audit = prepared["session"] / "audit.jsonl"
    decoded = prepared["decoded"]
    party0 = save_money(prepared["save"].read_bytes())[3]
    for index in (1, 2):
        cycle = prepared["session"] / f"bootstrap-{index}"
        cycle.mkdir()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        server.settimeout(120)
        token = secrets.token_hex(32)
        stable = write_stable_bridge("127.0.0.1", server.getsockname()[1], token,
                                     prepared["save"], cycle)
        with audit.open("a", encoding="utf-8") as output:
            output.write(json.dumps({"event": "bootstrap_start", "cycle": index,
                                     "session": cycle.name, "pid": None, "mgba": version,
                                     "script_path": str(stable), "working_sha": original_working_sha},
                                    sort_keys=True) + "\n")
        pid = None
        conn = None
        try:
            pid = launch_owned_mgba(mgba, prepared["rom"])
            with audit.open("a", encoding="utf-8") as output:
                output.write(json.dumps({"event": "bootstrap_pid", "cycle": index,
                                         "pid": pid}, sort_keys=True) + "\n")
            ui = attach_cold_bridge_ui(pid, stable)
            peer_conn, peer = server.accept()
            if peer[0] != "127.0.0.1":
                peer_conn.close()
                raise HarnessError("bootstrap bridge peer is not IPv4 loopback")
            conn = peer_conn
            bridge = Bridge(conn, token, audit, cycle)
            meta = bridge.command("meta")
            bridge.command("health")
            if len(meta) != 3 or meta[0] != "0" or not meta[1]:
                raise HarnessError(f"unexpected bootstrap game metadata: {meta}")
            bridge.command("load_save")
            bridge.command("reset")
            bridge.command("frames", 120)
            address = discover_money(bridge.read_ewram(), decoded["money"],
                                     decoded["party_count"], decoded["saved"], party0)
            value = int(bridge.command("read32", address)[0])
            if address != 0x0202571C or value != 1_234_568:
                raise HarnessError(f"bootstrap Money mismatch at {address:#010x}: {value}")
            if sha(prepared["save"]) != original_working_sha:
                raise HarnessError("working save changed during read-only bootstrap")
            result = {"cycle": index, "pid": pid, "mgba": version,
                      "script_path": str(stable), "load_method": ui["load_method"],
                      "metadata": meta, "address": address, "money": value,
                      "working_sha": sha(prepared["save"]), "status": "pass"}
            with audit.open("a", encoding="utf-8") as output:
                output.write(json.dumps({"event": "bootstrap_pass", **result,
                                         "ready_menus": ui["ready_menus"],
                                         "ready_tools": ui["ready_tools"]}, sort_keys=True) + "\n")
            results.append(result)
        finally:
            if pid is not None and pid in mgba_pids():
                stop_owned_mgba(pid)
            if conn is not None:
                conn.close()
            server.close()
    if results[0]["script_path"] != results[1]["script_path"]:
        raise HarnessError("stable bootstrap bridge path changed between launches")
    if results[1]["load_method"] != "recent":
        raise HarnessError("second cold launch did not use the stable Script MRU entry")
    if (sha(prepared["save"]) != original_working_sha
            or sha(prepared["input_save"]) != prepared["input_sha"]):
        raise HarnessError("input save changed during bootstrap proof")
    return results


def cold_resume(session: Path, source_save: Path, mgba: Path) -> int:
    """Run only the final read-only cold verification against preserved artifacts."""
    session = session.resolve()
    source_save = source_save.resolve()
    outside_repo(session)
    if not session.is_dir() or not source_save.is_file():
        raise HarnessError("preserved session and explicit source save are required")
    rom, save = session / "research.gba", session / "research.sav"
    audit = session / "audit.jsonl"
    if not rom.is_file() or not save.is_file() or not audit.is_file():
        raise HarnessError("preserved cold-proof artifacts are incomplete")
    if sha(rom) != ROM_SHA256:
        raise HarnessError("preserved working ROM SHA-256 mismatch")
    source_before = sha(source_save)
    if source_before != "d707f51ddd96ad0570abce430e8b8daf138012f16f656e2f49872fdab9025caf":
        raise HarnessError("immutable source save SHA-256 mismatch")
    working_before = sha(save)
    if working_before != "35fd9c501a23484c5ba0f5414e97fba8a8f07bc14dde6cc26189f1bfbba00490":
        raise HarnessError("preserved working save SHA-256 mismatch")
    verifier.verify_file(save)
    decoded = independent_save_money(save.read_bytes())
    if decoded["money"] != 1_234_568:
        raise HarnessError("preserved working save does not contain expected Money")
    previous = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    if previous.get("event") != "start" or previous.get("rom_sha") != ROM_SHA256:
        raise HarnessError("original audit does not match preserved ROM proof")
    if sha(source_save) != source_before:
        raise HarnessError("immutable source save changed during preflight")

    version = subprocess.check_output([str(mgba), "--version"], text=True).strip()
    if "mGBA 0.10.5" not in version:
        raise HarnessError("cold resume requires the verified mGBA 0.10.5 build")
    cold_dir = session / ("cold-" + secrets.token_hex(8))
    cold_dir.mkdir()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(600)
    token = secrets.token_hex(32)
    script = write_stable_bridge("127.0.0.1", server.getsockname()[1], token, save, cold_dir)
    with audit.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"event": "cold_session_start", "session": cold_dir.name,
                                 "mgba": version, "rom_sha": sha(rom),
                                 "source_sha_before": source_before,
                                 "working_sha_before": working_before,
                                 "script": str(script), "mode": "cold-only"}) + "\n")
    pid = launch_owned_mgba(mgba, rom)
    with audit.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"event": "cold_process_started", "pid": pid,
                                 "session": cold_dir.name}) + "\n")
    print(f"COLD_PID={pid}", flush=True)
    print(f"COLD_SCRIPT={script}", flush=True)
    ui_result = attach_cold_bridge_ui(pid, script)
    with audit.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"event": "cold_script_attached", "pid": pid,
                                 "session": cold_dir.name, **ui_result}) + "\n")
    print("Waiting for the exact cold bridge attachment.", flush=True)
    try:
        conn, peer = server.accept()
        if peer[0] != "127.0.0.1":
            conn.close()
            raise HarnessError("non-loopback peer")
        bridge = Bridge(conn, token, audit, cold_dir)
        meta = bridge.command("meta")
        if len(meta) != 3 or meta[0] != "0" or not meta[1]:
            raise HarnessError(f"unexpected cold metadata: {meta}")
        bridge.command("health")
        bridge.command("load_save")
        bridge.command("reset")
        bridge.command("frames", 120)
        # The existing post-save proof established this exact structure. Scan only; no inputs or writes.
        prepared = {"party_count": decoded["party_count"],
                    "party0": save_money(save.read_bytes())[3]}
        address = discover_money(bridge.read_ewram(), decoded["money"],
                                 decoded["party_count"], decoded["saved"], prepared["party0"])
        value = int(bridge.command("read32", address)[0])
        if address != 0x0202571C or value != 1_234_568:
            raise HarnessError(f"cold Money mismatch at {address:#010x}: {value}")
        bridge.command("screenshot", 90)
        bridge.log("cold_reload", address=address, money=value, working_sha=working_before,
                   verifier="pass", independent_decoder=decoded, session=cold_dir.name)
        stop_owned_mgba(pid)
        conn.close()
    finally:
        server.close()
    verifier.verify_file(save)
    final_decoded = independent_save_money(save.read_bytes())
    working_after = sha(save)
    source_after = sha(source_save)
    if final_decoded["money"] != 1_234_568 or working_after != working_before:
        raise HarnessError("working save changed during read-only cold verification")
    if source_after != source_before:
        raise HarnessError("immutable source save changed")
    with audit.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"event": "cold_final", "session": cold_dir.name,
                                 "pid": pid, "mgba": version, "script": str(script),
                                 "script_loading_automated": True, "address": address,
                                 "live_money": value, "verifier": "pass",
                                 "independent_decoder": final_decoded,
                                 "source_sha_before": source_before,
                                 "source_sha_after": source_after,
                                 "working_sha_before": working_before,
                                 "working_sha_after": working_after,
                                 "cold_reload": "pass", "status": "pass"}) + "\n")
    print(f"COLD_PASS address={address:#010x} money={value} verifier=pass", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--save", type=Path)
    parser.add_argument("--cold-resume", type=Path,
                        help="run only cold verification from a preserved proof session")
    parser.add_argument("--source-save", type=Path,
                        help="explicit immutable source save for cold-resume audit")
    parser.add_argument("--bootstrap-save", type=Path,
                        help="explicit save input for the read-only two-launch bootstrap proof")
    parser.add_argument("--bootstrap-proof", action="store_true",
                        help="run two cold stable-MRU bridge cycles only; never input/save")
    parser.add_argument("--mgba", type=Path, default=Path("/Applications/mGBA.app/Contents/MacOS/mGBA"))
    args = parser.parse_args()
    if args.bootstrap_proof:
        if (not args.rom or not args.bootstrap_save or args.source_save or args.save
                or args.cold_resume):
            raise HarnessError("bootstrap proof requires --rom and --bootstrap-save only")
        prepared = prepare_bootstrap_proof(args.rom, args.bootstrap_save)
        results = bootstrap_repeatability(prepared, args.mgba)
        for result in results:
            print("BOOTSTRAP_PASS", json.dumps(result, sort_keys=True), flush=True)
        print(f"BOOTSTRAP_AUDIT={prepared['session'] / 'audit.jsonl'}", flush=True)
        return 0
    if args.cold_resume:
        if not args.source_save or args.rom or args.save:
            raise HarnessError("cold-resume requires --source-save and forbids --rom/--save")
        return cold_resume(args.cold_resume, args.source_save, args.mgba)
    if not args.rom or not args.save or args.source_save:
        raise HarnessError("normal proof requires --rom and --save")
    prepared = prepare(args.rom, args.save)
    version = subprocess.check_output([str(args.mgba), "--version"], text=True).strip()
    if "mGBA 0.10." not in version:
        raise HarnessError("unsupported mGBA version")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(600)
    token = secrets.token_hex(32)
    path = write_stable_bridge("127.0.0.1", server.getsockname()[1], token,
                               prepared["save"], prepared["session"])
    audit = prepared["session"] / "audit.jsonl"
    with audit.open("w") as output:
        output.write(json.dumps({"event": "start", "git": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(), "mgba": version,
            "rom_sha": prepared["rom_sha"], "source_sha": prepared["source_sha"],
            "working_sha": sha(prepared["save"]), "session": prepared["session"].name}) + "\n")
    process_pid = launch_owned_mgba(args.mgba, prepared["rom"])
    with audit.open("a") as output:
        output.write(json.dumps({"event": "owned_process", "pid": process_pid}) + "\n")
    print(f"Working ROM and save: {prepared['session']}", flush=True)
    print(f"mGBA: Tools -> Scripting... -> Load Script -> {path}", flush=True)
    print("Waiting for initial script attachment (10 minutes).", flush=True)
    conn, address = server.accept()
    if address[0] != "127.0.0.1":
        conn.close()
        raise HarnessError("non-loopback peer")
    bridge = Bridge(conn, token, audit)
    bridge.command("health")
    meta = bridge.command("meta")
    if len(meta) != 3 or meta[0] != "0" or not meta[1]:
        raise HarnessError(f"unexpected emulated platform/title: {meta}")
    print("Connected:", meta, flush=True)
    bridge.command("load_save")
    bridge.command("reset")
    bridge.command("frames", 120)
    address = find_live_money(bridge, prepared, prepared["money"], prepared["saved"])
    print(f"Read-only live Money: {prepared['money']} at {address:#010x}", flush=True)
    bridge.log("discovery", address=address, money=prepared["money"],
               party_count=prepared["party_count"], saved=prepared["saved"])
    bridge.command("save_state", 1)
    bridge.command("load_state", 1)
    if int(bridge.command("read32", address)[0]) != prepared["money"]:
        raise HarnessError("research savestate reload changed Money")
    bridge.command("screenshot", 1)
    before = bytes.fromhex(bridge.command("read_range", address - 16, 36)[0])
    print(f"Research savestate and pre-write screenshot: {prepared['session']}", flush=True)
    input("Inspect screen-1.png and press Enter for the bounded +1 RAM canary (Ctrl-C stops): ")
    bridge.arm_money(address, prepared["money"])
    bridge.command("write32", address, prepared["money"] + 1)
    after = bytes.fromhex(bridge.command("read_range", address - 16, 36)[0])
    if after[:16] != before[:16] or after[20:] != before[20:] or int.from_bytes(after[16:20], "little") != prepared["money"] + 1:
        raise HarnessError("RAM canary or nearby structure mismatch")
    bridge.command("screenshot", 2)
    bridge.log("ram_canary", address=address, before=prepared["money"], after=prepared["money"] + 1)
    print("RAM canary read-back and nearby bytes verified. Screenshot screen-2.png saved.", flush=True)
    input("Inspect screen-2.png, then press Enter for 2-frame START input (Ctrl-C stops): ")
    bridge.command("set_keys", 1 << 3)
    bridge.command("frames", 2)
    bridge.command("set_keys", 0)
    bridge.command("frames", 2)
    bridge.command("screenshot", 3)
    print("START injection complete. Inspect screen-3.png. Normal SAVE remains a manual gate.", flush=True)
    before_save_sha = sha(prepared["save"])
    bridge.log("working_save_before_manual_save", sha=before_save_sha)
    input("Perform a normal in-game SAVE on the disposable working save, then press Enter: ")
    bridge.command("set_keys", 0)
    bridge.command("frames", 120)
    bridge.command("screenshot", 4)
    stop_owned_mgba(process_pid)
    bridge.conn.close()
    server.close()
    working_after_sha = sha(prepared["save"])
    bridge.log("working_save_after_shutdown", sha=working_after_sha)
    if working_after_sha == before_save_sha:
        raise HarnessError("working save did not change after normal SAVE and shutdown")
    verifier.verify_file(prepared["save"])
    decoded, _, _, _ = save_money(prepared["save"].read_bytes())
    if decoded != prepared["money"] + 1:
        raise HarnessError(f"working save Money after shutdown is {decoded}, expected {prepared['money'] + 1}")
    bridge.log("post_shutdown_verifier", result="pass", money=decoded)
    if sha(prepared["source"]) != prepared["source_sha"]:
        raise HarnessError("source save changed")

    cold_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cold_server.bind(("127.0.0.1", 0))
    cold_server.listen(1)
    cold_server.settimeout(600)
    cold_token = secrets.token_hex(32)
    cold_path = write_stable_bridge("127.0.0.1", cold_server.getsockname()[1], cold_token,
                                    prepared["save"], prepared["session"])
    cold_pid = launch_owned_mgba(args.mgba, prepared["rom"])
    bridge.log("cold_process_started", pid=cold_pid)
    print(f"Cold process started. mGBA: Tools -> Scripting... -> Load Script -> {cold_path}", flush=True)
    cold_conn, cold_peer = cold_server.accept()
    if cold_peer[0] != "127.0.0.1":
        cold_conn.close()
        raise HarnessError("non-loopback cold peer")
    cold = Bridge(cold_conn, cold_token, audit)
    cold_meta = cold.command("meta")
    if cold_meta != meta:
        raise HarnessError("cold reload game metadata changed")
    cold.command("load_save")
    cold.command("reset")
    cold.command("frames", 120)
    cold_address = find_live_money(cold, prepared, decoded,
                                   (prepared["saved"] + 1) & 0xFFFFFFFF, 30)
    cold_read = int(cold.command("read32", cold_address)[0])
    if cold_read != decoded:
        raise HarnessError("cold live Money mismatch")
    cold.log("cold_reload", address=cold_address, money=cold_read,
             working_sha=working_after_sha, verifier="pass")
    print(f"Cold reload PASS: Money {cold_read} at {cold_address:#010x}", flush=True)
    stop_owned_mgba(cold_pid)
    cold_conn.close()
    cold_server.close()
    final_working_sha = sha(prepared["save"])
    verifier.verify_file(prepared["save"])
    final_money, _, _, _ = save_money(prepared["save"].read_bytes())
    if final_money != decoded:
        raise HarnessError("working save Money changed across cold audit")
    cold.log("final", source_sha=sha(prepared["source"]), working_sha=final_working_sha,
             money=final_money, verifier="pass", cold_result="pass")
    if sha(prepared["source"]) != prepared["source_sha"]:
        raise HarnessError("source save changed")
    if sha(prepared["source_rom"]) != prepared["rom_sha"]:
        raise HarnessError("source ROM changed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HarnessError, OSError, verifier.VerificationError) as exc:
        raise SystemExit(f"harness stopped: {exc}")
