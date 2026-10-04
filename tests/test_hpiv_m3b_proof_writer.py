import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_hpiv_m3b_proof_writer as w
import pokemonstart_save_verifier as v


def _make_party_record(hp_iv=30):
    record = bytearray(v.POKEMON_SIZE)
    ivs = (hp_iv, 29, 26, 23, 27, 29)
    struct.pack_into(
        "<I", record, 72, sum(value << (5 * i) for i, value in enumerate(ivs))
    )
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


def _make_slot(counter, permutation, hp_iv=30):
    logical = []
    for section_id in range(v.SLOT_SECTORS):
        payload = bytearray(v.SECTION_LENGTHS[section_id])
        if section_id == 1:
            payload[v.PARTY_COUNT_OFFSET] = 1
            mon = _make_party_record(hp_iv)
            payload[v.PARTY_OFFSET : v.PARTY_OFFSET + len(mon)] = mon
        logical.append(_make_sector(section_id, counter, payload))
    return b"".join(logical[section_id] for section_id in permutation)


def _make_save(counter0=2, counter1=1, hp_iv=30):
    body = bytearray(b"\x00" * v.FLASH_SIZE)
    body[: 14 * v.SECTOR_SIZE] = _make_slot(
        counter0, [12, 13] + list(range(12)), hp_iv
    )
    body[14 * v.SECTOR_SIZE : 28 * v.SECTOR_SIZE] = _make_slot(
        counter1, [13] + list(range(13)), hp_iv
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


class M3BWriterTests(unittest.TestCase):
    def test_canonical_candidate_constants_are_bounded_and_sealed(self):
        self.assertEqual(
            w.EXPECTED_INPUT_SHA256,
            "c103d8d3eb158bb9e9ca3de3b2d00fe46849e1dfc25c6e7b27a01057005767ac",
        )
        self.assertEqual(
            w.EXPECTED_OUTPUT_SHA256,
            "cf2ca33a303b6409300ac4032c7c47efd9859562bc06fe18e89481bb93ea5f1f",
        )
        self.assertEqual(
            w.EXPECTED_DIFFS,
            ((0x3080, 0xBE, 0xBF), (0x3FF6, 0x20, 0x21)),
        )
        self.assertEqual(w.EXPECTED_ACTIVE_SLOT, 0)
        self.assertEqual(w.EXPECTED_ACTIVE_COUNTER, 2)
        self.assertEqual(w.EXPECTED_INACTIVE_COUNTER, 1)
        self.assertEqual(w.EXPECTED_OLD_HP_IV, 30)
        self.assertEqual(w.TARGET_HP_IV, 31)

    def test_derive_uses_both_valid_rotated_slots_and_stays_in_envelope(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            output, fingerprint = w.derive_candidate_fingerprint(raw)

        self.assertNotEqual(output, raw)
        self.assertEqual(fingerprint.active_slot, 0)
        self.assertEqual(fingerprint.active_counter, 2)
        self.assertEqual(fingerprint.section1_physical_sector, 3)
        self.assertEqual(fingerprint.old_hp_iv, 30)
        self.assertEqual(fingerprint.new_hp_iv, 31)
        allowed = {
            fingerprint.iv_offset,
            fingerprint.checksum_offset,
            fingerprint.checksum_offset + 1,
        }
        self.assertTrue(all(offset in allowed for offset, _, _ in fingerprint.diffs))
        after = v.verify_bytes(output)
        self.assertEqual(after.party[0].ivs, (31, 29, 26, 23, 27, 29))

    def test_private_seal_rejects_unrelated_synthetic_fingerprint(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, "non-allowlisted M3B diff"):
                w.build_proof_output(raw)

    def test_slot_counter_parity_mismatch_is_rejected(self):
        raw = _make_save(counter0=3, counter1=2)
        patches = _profile_patches(raw)
        with (
            patches[0],
            patches[1],
            patches[2],
            patches[3],
            mock.patch.object(w, "EXPECTED_ACTIVE_COUNTER", 3),
            mock.patch.object(w, "EXPECTED_INACTIVE_COUNTER", 2),
        ):
            with self.assertRaisesRegex(w.WriterError, "parity"):
                w.derive_candidate_fingerprint(raw)

    def test_wrong_starting_hp_iv_is_rejected(self):
        raw = _make_save(hp_iv=31)
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, "HP IV is 31"):
                w.derive_candidate_fingerprint(raw)

    def test_synthetic_override_can_exercise_new_file_and_overwrite_safety(self):
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
