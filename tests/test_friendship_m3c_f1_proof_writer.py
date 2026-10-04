import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_friendship_m3c_f1_proof_writer as w
import pokemonstart_save_verifier as v


def _make_party_record(friendship=50):
    record = bytearray(v.POKEMON_SIZE)
    struct.pack_into("<H", record, 32, 1)
    struct.pack_into("<I", record, 36, 134)
    record[41] = friendship
    record[42] = 3
    struct.pack_into("<HHHH", record, 44, 33, 45, 0, 0)
    record[52:56] = bytes((35, 40, 0, 0))
    ivs = (31, 29, 26, 23, 27, 29)
    struct.pack_into(
        "<I", record, 72, sum(value << (5 * i) for i, value in enumerate(ivs))
    )
    record[84] = 5
    struct.pack_into("<HHHHHHH", record, 86, 21, 21, 9, 11, 10, 13, 12)
    return bytes(record)


def _make_sector(section_id, counter, payload=None):
    sector = bytearray(v.SECTOR_SIZE)
    if payload is not None:
        sector[: len(payload)] = payload
    struct.pack_into("<H", sector, v.SECTION_ID_OFFSET, section_id)
    checksum = v.calculate_save_checksum(sector[: v.SECTION_LENGTHS[section_id]])
    struct.pack_into("<H", sector, v.SECTION_CHECKSUM_OFFSET, checksum)
    struct.pack_into("<I", sector, v.SECTION_SIGNATURE_OFFSET, v.FILE_SIGNATURE)
    struct.pack_into("<I", sector, v.SECTION_COUNTER_OFFSET, counter)
    return bytes(sector)


def _make_slot(counter, permutation, friendship=50):
    logical = []
    for section_id in range(v.SLOT_SECTORS):
        payload = bytearray(v.SECTION_LENGTHS[section_id])
        if section_id == 1:
            payload[v.PARTY_COUNT_OFFSET] = 1
            mon = _make_party_record(friendship)
            payload[v.PARTY_OFFSET : v.PARTY_OFFSET + len(mon)] = mon
        logical.append(_make_sector(section_id, counter, payload))
    return b"".join(logical[section_id] for section_id in permutation)


def _make_save(friendship=50, counter0=2, counter1=3):
    body = bytearray(v.FLASH_SIZE)
    body[: 14 * v.SECTOR_SIZE] = _make_slot(
        counter0, [12, 13] + list(range(12)), friendship
    )
    body[14 * v.SECTOR_SIZE : 28 * v.SECTOR_SIZE] = _make_slot(
        counter1, [11, 12, 13] + list(range(11)), friendship
    )
    body[30 * v.SECTOR_SIZE] = 1
    return bytes(body) + bytes(range(16))


def _profile_patches(raw):
    result = v.verify_bytes(raw)
    return (
        mock.patch.object(w, "EXPECTED_INPUT_SHA256", hashlib.sha256(raw).hexdigest()),
        mock.patch.object(
            w, "EXPECTED_SECTOR30_SHA256", hashlib.sha256(result.sector30).hexdigest()
        ),
        mock.patch.object(
            w, "EXPECTED_SECTOR31_SHA256", hashlib.sha256(result.sector31).hexdigest()
        ),
        mock.patch.object(
            w, "EXPECTED_FOOTER_SHA256", hashlib.sha256(result.footer).hexdigest()
        ),
    )


class M3CF1FriendshipWriterTests(unittest.TestCase):
    def test_canonical_candidate_constants_are_bounded_and_sealed(self):
        self.assertEqual(
            w.EXPECTED_INPUT_SHA256,
            "d8f193de253dd3a1d3a5060273044fb165b3dfb09938bd8331aaa22eb879f282",
        )
        self.assertEqual(
            w.EXPECTED_OUTPUT_SHA256,
            "10f13894cab59922989e2b0508b41f2eef276e8c45b2778d6e6b1a309d2f98ae",
        )
        self.assertEqual(
            w.EXPECTED_DIFFS,
            ((0x12061, 0x32, 0x33), (0x12FF7, 0x1C, 0x1D)),
        )
        self.assertEqual(
            (w.EXPECTED_ACTIVE_SLOT, w.EXPECTED_ACTIVE_COUNTER, w.EXPECTED_INACTIVE_COUNTER),
            (1, 3, 2),
        )
        self.assertEqual((w.EXPECTED_OLD_FRIENDSHIP, w.TARGET_FRIENDSHIP), (50, 51))

    def test_derive_uses_active_slot1_rotation_and_preserves_record(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            output, fingerprint = w.derive_candidate_fingerprint(raw)

        self.assertEqual(fingerprint.active_slot, 1)
        self.assertEqual(fingerprint.active_counter, 3)
        self.assertEqual(fingerprint.section1_physical_sector, 18)
        self.assertEqual(fingerprint.old_friendship, 50)
        self.assertEqual(fingerprint.new_friendship, 51)
        after = v.verify_bytes(output)
        self.assertEqual(after.party[0].friendship, 51)

    def test_private_seal_rejects_unrelated_synthetic_fingerprint(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, "non-allowlisted M3C-F1 diff"):
                w.build_proof_output(raw)

    def test_slot_counter_parity_mismatch_is_rejected(self):
        raw = _make_save(counter0=3, counter1=4)
        patches = _profile_patches(raw)
        with (
            patches[0],
            patches[1],
            patches[2],
            patches[3],
            mock.patch.object(w, "EXPECTED_ACTIVE_COUNTER", 4),
            mock.patch.object(w, "EXPECTED_INACTIVE_COUNTER", 3),
        ):
            with self.assertRaisesRegex(w.WriterError, "parity"):
                w.derive_candidate_fingerprint(raw)

    def test_wrong_starting_friendship_is_rejected(self):
        raw = _make_save(friendship=49)
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, "friendship is 49"):
                w.derive_candidate_fingerprint(raw)

    def test_synthetic_override_exercises_new_file_and_overwrite_safety(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            expected, fingerprint = w.derive_candidate_fingerprint(raw)
            with (
                mock.patch.object(w, "EXPECTED_DIFFS", fingerprint.diffs),
                mock.patch.object(
                    w, "EXPECTED_OUTPUT_SHA256", fingerprint.output_sha256
                ),
                tempfile.TemporaryDirectory() as temp_dir,
            ):
                root = Path(temp_dir)
                source = root / "in.sav"
                destination = root / "out.sav"
                source.write_bytes(raw)
                result = w.write_proof_file(source, destination)

                self.assertEqual(source.read_bytes(), raw)
                self.assertEqual(destination.read_bytes(), expected)
                self.assertEqual(result, fingerprint)

                with self.assertRaisesRegex(w.WriterError, "overwrite the input"):
                    w.write_proof_file(source, source)
                with self.assertRaisesRegex(w.WriterError, "existing output path"):
                    w.write_proof_file(source, destination)


if __name__ == "__main__":
    unittest.main()
