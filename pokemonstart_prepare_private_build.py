#!/usr/bin/env python3
"""Statically apply one structurally valid BPS patch embedded in a package.

The package and source ROM are read-only. This tool never executes package
content and creates the patched ROM with exclusive-create semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

MAX_ROM_SIZE = 64 * 1024 * 1024
REPO = Path(__file__).resolve().parent


class PrepareError(ValueError):
    pass


@dataclass(frozen=True)
class Patch:
    start: int
    end: int
    source_size: int
    target_size: int
    metadata: bytes
    source_crc: int
    target_crc: int
    patch_crc: int


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _number(data: bytes, pos: int, limit: int) -> tuple[int, int]:
    value = 0
    shift = 1
    while True:
        if pos >= limit:
            raise PrepareError("truncated BPS variable integer")
        byte = data[pos]
        pos += 1
        value += (byte & 0x7F) * shift
        if byte & 0x80:
            return value, pos
        shift <<= 7
        value += shift
        if shift > 1 << 56:
            raise PrepareError("oversized BPS variable integer")


def _signed(value: int) -> int:
    magnitude = value >> 1
    return -magnitude if value & 1 else magnitude


def parse_patch(data: bytes, start: int) -> Patch:
    if data[start:start + 4] != b"BPS1":
        raise PrepareError("missing BPS1 signature")
    limit = len(data)
    pos = start + 4
    source_size, pos = _number(data, pos, limit)
    target_size, pos = _number(data, pos, limit)
    metadata_size, pos = _number(data, pos, limit)
    if source_size > MAX_ROM_SIZE or target_size > MAX_ROM_SIZE:
        raise PrepareError("BPS ROM size exceeds the supported bound")
    if pos + metadata_size > limit:
        raise PrepareError("truncated BPS metadata")
    metadata = data[pos:pos + metadata_size]
    pos += metadata_size
    output_size = 0
    source_relative = 0
    target_relative = 0
    # Actions are decoded to their exact semantic end; candidate bytes after
    # the footer may belong to a surrounding executable/container.
    while output_size < target_size:
        action, pos = _number(data, pos, limit)
        length = (action >> 2) + 1
        kind = action & 3
        if output_size + length > target_size:
            raise PrepareError("BPS action overruns declared target size")
        if kind == 1:  # TargetRead: literal bytes follow.
            pos += length
            if pos > limit:
                raise PrepareError("truncated BPS TargetRead")
        elif kind in (2, 3):
            delta, pos = _number(data, pos, limit)
            if kind == 2:
                source_relative += _signed(delta)
                if source_relative < 0 or source_relative + length > source_size:
                    raise PrepareError("BPS SourceCopy is outside source")
                source_relative += length
            else:
                target_relative += _signed(delta)
                if target_relative < 0 or target_relative >= output_size:
                    raise PrepareError("BPS TargetCopy starts outside prior output")
                target_relative += length
        output_size += length
    if pos + 12 > limit:
        raise PrepareError("truncated BPS CRC footer")
    end = pos + 12
    source_crc, target_crc, patch_crc = struct.unpack_from("<III", data, pos)
    if zlib.crc32(data[start:pos + 8]) & 0xFFFFFFFF != patch_crc:
        raise PrepareError("BPS patch CRC mismatch")
    return Patch(start, end, source_size, target_size, metadata,
                 source_crc, target_crc, patch_crc)


def scan_patches(package: bytes) -> list[Patch]:
    result: list[Patch] = []
    pos = 0
    while True:
        pos = package.find(b"BPS1", pos)
        if pos < 0:
            break
        try:
            result.append(parse_patch(package, pos))
        except PrepareError:
            pass  # A signature-like sequence is not a patch unless fully valid.
        pos += 1
    return result


def apply_patch(source: bytes, patch_data: bytes, patch: Patch) -> bytes:
    if len(source) != patch.source_size:
        raise PrepareError("source ROM size does not match BPS declaration")
    if zlib.crc32(source) & 0xFFFFFFFF != patch.source_crc:
        raise PrepareError("source ROM CRC does not match BPS declaration")
    result = bytearray()
    pos = patch.start + 4
    source_size, pos = _number(patch_data, pos, patch.end - 12)
    target_size, pos = _number(patch_data, pos, patch.end - 12)
    metadata_size, pos = _number(patch_data, pos, patch.end - 12)
    pos += metadata_size
    source_relative = 0
    target_relative = 0
    while len(result) < target_size:
        action, pos = _number(patch_data, pos, patch.end - 12)
        length = (action >> 2) + 1
        kind = action & 3
        if kind == 0:  # SourceRead at current output offset.
            begin = len(result)
            if begin + length > len(source):
                raise PrepareError("BPS SourceRead is outside source")
            result.extend(source[begin:begin + length])
        elif kind == 1:  # TargetRead
            result.extend(patch_data[pos:pos + length])
            pos += length
        elif kind == 2:  # SourceCopy
            delta, pos = _number(patch_data, pos, patch.end - 12)
            source_relative += _signed(delta)
            if source_relative < 0 or source_relative + length > len(source):
                raise PrepareError("BPS SourceCopy is outside source")
            result.extend(source[source_relative:source_relative + length])
            source_relative += length
        else:  # TargetCopy; bytewise semantics permit overlapping copies.
            delta, pos = _number(patch_data, pos, patch.end - 12)
            target_relative += _signed(delta)
            if target_relative < 0 or target_relative >= len(result):
                raise PrepareError("BPS TargetCopy starts outside prior output")
            for _ in range(length):
                if target_relative >= len(result):
                    raise PrepareError("invalid BPS TargetCopy reference")
                result.append(result[target_relative])
                target_relative += 1
    target = bytes(result)
    if len(target) != patch.target_size or zlib.crc32(target) & 0xFFFFFFFF != patch.target_crc:
        raise PrepareError("BPS target size or CRC mismatch")
    return target


def prepare(package_path: Path, source_path: Path, output_path: Path) -> dict[str, object]:
    package_path = package_path.resolve()
    source_path = source_path.resolve()
    output_path = output_path.resolve()
    if output_path in (package_path, source_path):
        raise PrepareError("output path must differ from package and source")
    if output_path.is_relative_to(REPO):
        raise PrepareError("prepared ROM output must be outside the repository")
    if output_path.exists():
        raise PrepareError("output already exists; refusing to overwrite")
    package = package_path.read_bytes()
    source_before = source_path.read_bytes()
    source_sha_before = sha256(source_before)
    patches = scan_patches(package)
    compatible = [p for p in patches if p.source_size == len(source_before)
                  and p.source_crc == (zlib.crc32(source_before) & 0xFFFFFFFF)]
    if len(compatible) != 1:
        kind = "PKS1 container has no statically recoverable supported patch" if package.startswith(b"PKS1") and not patches else ""
        raise PrepareError(kind or f"expected one source-compatible BPS patch, found {len(compatible)} (valid candidates={len(patches)})")
    patch = compatible[0]
    target = apply_patch(source_before, package, patch)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with output_path.open("xb") as output:
            created = True
            output.write(target)
            output.flush()
        written = output_path.read_bytes()
        if len(written) != patch.target_size or zlib.crc32(written) & 0xFFFFFFFF != patch.target_crc:
            raise PrepareError("written output failed size or CRC verification")
        if sha256(written) != sha256(target):
            raise PrepareError("written output SHA-256 differs from verified target")
    except Exception:
        if created and output_path.exists():
            output_path.unlink()
        raise
    source_after_sha = sha256(source_path.read_bytes())
    if source_after_sha != source_sha_before:
        output_path.unlink()
        raise PrepareError("source ROM changed during preparation")
    return {"package_sha256": sha256(package), "source_sha256": source_sha_before,
            "source_crc32": f"{patch.source_crc:08x}",
            "target_sha256": sha256(target), "target_crc32": f"{patch.target_crc:08x}",
            "patch_offset": patch.start, "patch_size": patch.end - patch.start,
            "source_size": patch.source_size, "target_size": patch.target_size}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("source_rom", type=Path)
    parser.add_argument("output_rom", type=Path)
    args = parser.parse_args()
    try:
        report = prepare(args.package, args.source_rom, args.output_rom)
    except (OSError, PrepareError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    for key, value in report.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
