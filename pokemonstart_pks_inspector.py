#!/usr/bin/env python3
"""Statically decode PokemonStart PKS1 packages without running their payloads."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import re
import struct
import sys
import zlib

REPO = Path(__file__).resolve().parent
MAGIC = b"PKS1"
KEY = bytes((
    0x2F, 0xA8, 0x51, 0x0C, 0xE7, 0x94, 0x3B, 0x66,
    0xD2, 0x19, 0x7E, 0xC5, 0x08, 0xB3, 0x4A, 0xF1,
    0x5D, 0x86, 0x23, 0xEA, 0x70, 0x1B, 0xC9, 0x34,
    0x9F, 0x42, 0xDB, 0x05, 0xAE, 0x67, 0x18, 0xBC,
))
MAX_PACKAGE_SIZE = 64 * 1024 * 1024
MAX_PAYLOAD_SIZE = 128 * 1024 * 1024
MAX_MEMBERS = 4096


class PackageError(ValueError):
    """Raised when a package is invalid or unsafe to extract."""


@dataclass(frozen=True)
class Member:
    name: str
    data: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    @property
    def file_type(self) -> str:
        if self.data.startswith(b"MZ"):
            return "PE candidate"
        if self.data.startswith(b"BPS1"):
            return "BPS patch"
        if self.data.startswith(b"PK\x03\x04"):
            return "ZIP archive"
        if self.data.startswith(b"<!DOCTYPE html") or self.data.startswith(b"<html"):
            return "HTML data"
        if self.data.startswith((b"\xef\xbb\xbf", b"#", b"\n")):
            return "text data"
        return "unknown data"


@dataclass(frozen=True)
class DecodedPackage:
    package_sha256: str
    payload_sha256: str
    payload_size: int
    nonce: bytes
    members: tuple[Member, ...]


def _inflate_bounded(compressed: bytes) -> bytes:
    decoder = zlib.decompressobj(wbits=-15)
    output = bytearray()
    for offset in range(0, len(compressed), 64 * 1024):
        pending = compressed[offset:offset + 64 * 1024]
        while pending:
            allowance = MAX_PAYLOAD_SIZE + 1 - len(output)
            if allowance <= 0:
                raise PackageError("decoded payload exceeds size limit")
            piece = decoder.decompress(pending, allowance)
            output.extend(piece)
            if len(output) > MAX_PAYLOAD_SIZE:
                raise PackageError("decoded payload exceeds size limit")
            pending = decoder.unconsumed_tail
            if decoder.unused_data:
                raise PackageError("unexpected data after raw DEFLATE stream")
            if pending and not piece:
                raise PackageError("raw DEFLATE decoder made no progress")
    allowance = MAX_PAYLOAD_SIZE + 1 - len(output)
    output.extend(decoder.flush(max(1, allowance)))
    if len(output) > MAX_PAYLOAD_SIZE:
        raise PackageError("decoded payload exceeds size limit")
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise PackageError("incomplete or trailing raw DEFLATE data")
    return bytes(output)


def _members(payload: bytes) -> tuple[Member, ...]:
    if len(payload) < 4:
        raise PackageError("truncated member table")
    count = struct.unpack_from("<I", payload)[0]
    if count > MAX_MEMBERS:
        raise PackageError("member count exceeds supported limit")
    position = 4
    members: list[Member] = []
    for _ in range(count):
        if position + 2 > len(payload):
            raise PackageError("truncated member-name length")
        name_length = struct.unpack_from("<H", payload, position)[0]
        position += 2
        if name_length == 0 or position + name_length + 4 > len(payload):
            raise PackageError("invalid or truncated member name")
        try:
            name = payload[position:position + name_length].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageError("member name is not UTF-8") from exc
        position += name_length
        size = struct.unpack_from("<I", payload, position)[0]
        position += 4
        if size > len(payload) - position:
            raise PackageError("member data exceeds decoded payload")
        data = payload[position:position + size]
        position += size
        members.append(Member(name, data))
    if position != len(payload):
        raise PackageError("unexpected trailing bytes in member table")
    return tuple(members)


def decode_bytes(package: bytes) -> DecodedPackage:
    if len(package) < 52 or len(package) > MAX_PACKAGE_SIZE:
        raise PackageError("unsupported package size")
    if package[:4] != MAGIC:
        raise PackageError("PKS1 signature mismatch")
    nonce = package[4:20]
    expected_sha256 = package[20:52]
    encrypted = package[52:]
    seed = bytearray(52)
    seed[:32] = KEY
    seed[32:48] = nonce
    transformed = bytearray(len(encrypted))
    for offset in range(0, len(encrypted), 32):
        counter = offset // 32
        seed[48:52] = counter.to_bytes(4, "little")
        stream = hashlib.sha256(seed).digest()
        block = encrypted[offset:offset + 32]
        for index, value in enumerate(block):
            transformed[offset + index] = value ^ stream[index]
    payload = _inflate_bounded(bytes(transformed))
    digest = hashlib.sha256(payload).digest()
    if digest != expected_sha256:
        raise PackageError("decoded payload SHA-256 mismatch")
    members = _members(payload)
    return DecodedPackage(hashlib.sha256(package).hexdigest(), digest.hex(),
                          len(payload), nonce, members)


def _output_member_name(index: int, logical_name: str) -> str:
    basename = logical_name.replace("\\", "/").rsplit("/", 1)[-1]
    basename = re.sub(r"[^A-Za-z0-9._()\-\u0080-\uffff]", "_", basename)
    basename = basename[:120] or "member.bin"
    if basename in (".", ".."):
        basename = "member.bin"
    return f"{index:04d}-{basename}"


def extract(package_path: Path, output_dir: Path) -> dict[str, object]:
    package_path = package_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir == REPO or output_dir.is_relative_to(REPO):
        raise PackageError("extraction output must be outside the repository")
    if output_dir.exists():
        raise PackageError("output directory already exists; refusing to overwrite")
    decoded = decode_bytes(package_path.read_bytes())
    output_dir.mkdir(parents=True, exist_ok=False)
    created: list[Path] = []
    report_members = []
    try:
        for index, member in enumerate(decoded.members):
            filename = _output_member_name(index, member.name)
            destination = output_dir / filename
            with destination.open("xb") as output:
                created.append(destination)
                output.write(member.data)
                output.flush()
            report_members.append({
                "logical_name": member.name,
                "output_name": filename,
                "size": len(member.data),
                "sha256": member.sha256,
                "type": member.file_type,
                "magic": member.data[:12].hex(),
            })
        report = {
            "format": "PokemonStart PKS1",
            "package_sha256": decoded.package_sha256,
            "payload_sha256": decoded.payload_sha256,
            "payload_size": decoded.payload_size,
            "member_count": len(decoded.members),
            "members": report_members,
        }
        manifest = output_dir / "members.json"
        with manifest.open("x", encoding="utf-8") as output:
            created.append(manifest)
            json.dump(report, output, ensure_ascii=False, indent=2)
            output.write("\n")
        return report
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        output_dir.rmdir()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        report = extract(args.package, args.output_dir)
    except (OSError, PackageError, zlib.error) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("Payloads were written as data only; nothing was executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
