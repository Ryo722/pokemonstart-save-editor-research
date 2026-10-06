from __future__ import annotations

import hashlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import pokemonstart_prepare_private_build as prepare


def number(value: int) -> bytes:
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value == 0:
            encoded.append(byte | 0x80)
            return bytes(encoded)
        encoded.append(byte)
        value -= 1


def fixture_patch(source: bytes) -> tuple[bytes, bytes]:
    # SourceRead all bytes, TargetRead "!", then an overlapping TargetCopy.
    target = source + b"!!!"
    body = (b"BPS1" + number(len(source)) + number(len(target)) + number(0)
            + number((len(source) - 1) << 2)
            + number((1 - 1) << 2 | 1) + b"!"
            + number((2 - 1) << 2 | 3) + number(len(source) * 2))
    checksums = struct.pack("<II", zlib.crc32(source), zlib.crc32(target))
    body += checksums
    return body + struct.pack("<I", zlib.crc32(body)), target


def pack_patch(source: bytes, target: bytes, actions: bytes) -> bytes:
    body = (b"BPS1" + number(len(source)) + number(len(target)) + number(0)
            + actions + struct.pack("<II", zlib.crc32(source), zlib.crc32(target)))
    return body + struct.pack("<I", zlib.crc32(body))


class PrivateBuildTests(unittest.TestCase):
    def test_parse_and_apply_all_basic_action_types(self) -> None:
        source = b"owned-rom"
        patch_bytes, expected = fixture_patch(source)
        parsed = prepare.parse_patch(patch_bytes, 0)
        self.assertEqual(parsed.end, len(patch_bytes))
        self.assertEqual(prepare.apply_patch(source, patch_bytes, parsed), expected)

    def test_false_positive_signature_is_ignored(self) -> None:
        self.assertEqual(prepare.scan_patches(b"xxBPS1not-a-patch"), [])

    def test_source_copy_supports_signed_relative_offsets(self) -> None:
        source = b"abcdef"
        target = b"ec"
        # SourceCopy e from +4, then c from relative -3.
        actions = number(2) + number(8) + number(2) + number(7)
        patch_bytes = pack_patch(source, target, actions)
        parsed = prepare.parse_patch(patch_bytes, 0)
        self.assertEqual(prepare.apply_patch(source, patch_bytes, parsed), target)

    def test_prepare_requires_unique_compatible_patch_and_new_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.gba"
            package = root / "package.pks"
            output = root / "new.gba"
            original = b"owned-rom"
            patch_bytes, target = fixture_patch(original)
            source.write_bytes(original)
            package.write_bytes(patch_bytes)
            result = prepare.prepare(package, source, output)
            self.assertEqual(output.read_bytes(), target)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(result["source_sha256"], hashlib.sha256(original).hexdigest())
            with self.assertRaisesRegex(prepare.PrepareError, "already exists"):
                prepare.prepare(package, source, output)

    def test_pks_container_without_recoverable_patch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.gba"
            package = root / "package.pks"
            source.write_bytes(b"owned-rom")
            package.write_bytes(b"PKS1" + bytes(range(256)))
            with self.assertRaisesRegex(prepare.PrepareError, "no statically recoverable"):
                prepare.prepare(package, source, root / "new.gba")

    def test_prepared_rom_cannot_be_written_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.gba"
            package = root / "package.bps"
            source.write_bytes(b"owned-rom")
            package.write_bytes(fixture_patch(b"owned-rom")[0])
            output = prepare.REPO / "fl2-g0-protected-output-test.gba"
            try:
                with self.assertRaisesRegex(prepare.PrepareError, "outside the repository"):
                    prepare.prepare(package, source, output)
            finally:
                output.unlink(missing_ok=True)

    def test_multiple_compatible_patches_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.gba"
            package = root / "package.bin"
            source.write_bytes(b"owned-rom")
            patch_bytes, _ = fixture_patch(b"owned-rom")
            package.write_bytes(patch_bytes + patch_bytes)
            with self.assertRaisesRegex(prepare.PrepareError, "found 2"):
                prepare.prepare(package, source, root / "new.gba")


if __name__ == "__main__":
    unittest.main()
