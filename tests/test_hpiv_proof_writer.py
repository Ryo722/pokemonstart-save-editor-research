import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_save_verifier as v
import pokemonstart_hpiv_proof_writer as w


def _party(hp_iv=31):
    record = bytearray(v.POKEMON_SIZE)
    struct.pack_into("<I", record, 0, 0x11223344)
    struct.pack_into("<I", record, 4, 0x55667788)
    record[8:15] = bytes.fromhex("01020304050607")
    record[15] = 3
    record[16] = 0x15
    record[17] = 12
    record[18] = 1
    record[19] = 2
    record[20:27] = bytes.fromhex("11121314151617")
    record[27] = 4
    struct.pack_into("<H", record, 28, 1)
    struct.pack_into("<H", record, 32, 1)
    struct.pack_into("<H", record, 34, 9)
    struct.pack_into("<I", record, 36, 134)
    record[41] = 50
    record[42] = 3
    struct.pack_into("<4H", record, 44, 33, 45, 0, 0)
    record[52:56] = bytes((35, 40, 0, 0))
    ivs = (hp_iv, 29, 26, 23, 27, 29)
    struct.pack_into("<I", record, 72, sum(value << (5 * i) for i, value in enumerate(ivs)))
    record[84] = 5
    struct.pack_into("<7H", record, 86, 21, 21, 9, 11, 10, 13, 12)
    return bytes(record)


def _sector(section_id, counter, payload=None):
    sector = bytearray(v.SECTOR_SIZE)
    if payload is not None:
        sector[: len(payload)] = payload
    struct.pack_into("<H", sector, v.SECTION_ID_OFFSET, section_id)
    struct.pack_into(
        "<H",
        sector,
        v.SECTION_CHECKSUM_OFFSET,
        v.calculate_save_checksum(sector[: v.SECTION_LENGTHS[section_id]]),
    )
    struct.pack_into("<I", sector, v.SECTION_SIGNATURE_OFFSET, v.FILE_SIGNATURE)
    struct.pack_into("<I", sector, v.SECTION_COUNTER_OFFSET, counter)
    return bytes(sector)


def _slot(counter, hp_iv=31):
    logical = []
    for section_id in range(v.SLOT_SECTORS):
        payload = bytearray(v.SECTION_LENGTHS[section_id])
        if section_id == 1:
            payload[v.PARTY_COUNT_OFFSET] = 1
            mon = _party(hp_iv)
            payload[v.PARTY_OFFSET : v.PARTY_OFFSET + len(mon)] = mon
        logical.append(_sector(section_id, counter, payload))
    permutation = [13] + list(range(13))
    return b"".join(logical[section_id] for section_id in permutation)


def _save(hp_iv=31):
    body = bytearray(b"\x00" * v.FLASH_SIZE)
    body[: 14 * v.SECTOR_SIZE] = b"\xFF" * (14 * v.SECTOR_SIZE)
    body[14 * v.SECTOR_SIZE : 28 * v.SECTOR_SIZE] = _slot(1, hp_iv)
    body[30 * v.SECTOR_SIZE] = 1
    return bytes(body) + bytes(range(16))


def _manual_expected(raw):
    before = v.verify_bytes(raw)
    section = before.slots[before.active_slot].section(1)
    base = section.physical_sector * v.SECTOR_SIZE
    iv_offset = base + v.PARTY_OFFSET + 72
    checksum_offset = base + v.SECTION_CHECKSUM_OFFSET
    out = bytearray(raw)
    word = struct.unpack_from("<I", out, iv_offset)[0]
    struct.pack_into("<I", out, iv_offset, (word & ~31) | 30)
    struct.pack_into(
        "<H",
        out,
        checksum_offset,
        v.calculate_save_checksum(bytes(out[base : base + v.SECTION_LENGTHS[1]])),
    )
    output = bytes(out)
    diffs = tuple((i, a, b) for i, (a, b) in enumerate(zip(raw, output)) if a != b)
    return output, diffs


class WriterTests(unittest.TestCase):
    def test_canonical_proof_constants_are_bounded(self):
        self.assertEqual(
            w.EXPECTED_INPUT_SHA256,
            "fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b",
        )
        self.assertEqual(
            w.EXPECTED_OUTPUT_SHA256,
            "569fc5b2b18c77593a0f55bbe01fd20a603fe96ce9c5f955b978710d117db0dc",
        )
        self.assertEqual(
            w.EXPECTED_DIFFS,
            ((0x10080, 0xBF, 0xBE), (0x10FF6, 0x62, 0x61)),
        )

    def test_build_changes_only_hpiv_and_checksum(self):
        raw = _save(31)
        expected, diffs = _manual_expected(raw)
        with (
            mock.patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()),
            mock.patch.object(w, "EXPECTED_OUTPUT_SHA256", hashlib.sha256(expected).hexdigest()),
            mock.patch.object(w, "EXPECTED_DIFFS", diffs),
        ):
            output, result = w.build_proof_output(raw)
        self.assertEqual(output, expected)
        before = v.verify_bytes(raw)
        after = v.verify_bytes(output)
        self.assertEqual(after.party[0].ivs, (30, 29, 26, 23, 27, 29))
        self.assertEqual(after.footer, before.footer)
        self.assertEqual(after.sector30, before.sector30)
        self.assertEqual(after.sector31, before.sector31)
        self.assertEqual(result.diffs, diffs)

    def test_rejects_unrecognized_input_hash(self):
        with self.assertRaisesRegex(w.WriterError, "unsupported proof input sha256"):
            w.build_proof_output(_save(31))

    def test_rejects_if_hpiv_is_not_31(self):
        raw = _save(30)
        with mock.patch.object(
            w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()
        ):
            with self.assertRaisesRegex(w.WriterError, "HP IV is 30"):
                w.build_proof_output(raw)

    def test_write_never_overwrites_input_or_existing_output(self):
        raw = _save(31)
        expected, diffs = _manual_expected(raw)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "in.sav"
            existing = root / "existing.sav"
            src.write_bytes(raw)
            existing.write_bytes(b"keep")
            with (
                mock.patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()),
                mock.patch.object(w, "EXPECTED_OUTPUT_SHA256", hashlib.sha256(expected).hexdigest()),
                mock.patch.object(w, "EXPECTED_DIFFS", diffs),
            ):
                with self.assertRaisesRegex(w.WriterError, "overwrite the input"):
                    w.write_proof_file(src, src)
                with self.assertRaisesRegex(w.WriterError, "existing output path"):
                    w.write_proof_file(src, existing)
            self.assertEqual(src.read_bytes(), raw)
            self.assertEqual(existing.read_bytes(), b"keep")

    def test_write_creates_new_file_and_preserves_input(self):
        raw = _save(31)
        expected, diffs = _manual_expected(raw)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "in.sav"
            dst = root / "out.sav"
            src.write_bytes(raw)
            with (
                mock.patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()),
                mock.patch.object(w, "EXPECTED_OUTPUT_SHA256", hashlib.sha256(expected).hexdigest()),
                mock.patch.object(w, "EXPECTED_DIFFS", diffs),
            ):
                result = w.write_proof_file(src, dst)
            self.assertEqual(src.read_bytes(), raw)
            self.assertEqual(dst.read_bytes(), expected)
            self.assertEqual(result.output_sha256, hashlib.sha256(expected).hexdigest())


if __name__ == "__main__":
    unittest.main()
