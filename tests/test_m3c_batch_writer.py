import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_m3c_batch_writer as w
import pokemonstart_save_verifier as v


def _make_party_record(friendship=51, markings=0, ball=3):
    record = bytearray(v.POKEMON_SIZE)
    record[27] = markings
    struct.pack_into('<H', record, 32, 1)
    struct.pack_into('<I', record, 36, 134)
    record[41] = friendship
    record[42] = ball
    struct.pack_into('<HHHH', record, 44, 33, 45, 0, 0)
    record[52:56] = bytes((35, 40, 0, 0))
    ivs = (31, 29, 26, 23, 27, 29)
    struct.pack_into('<I', record, 72, sum(x << (5 * i) for i, x in enumerate(ivs)))
    record[84] = 5
    record[85] = 255
    struct.pack_into('<HHHHHHH', record, 86, 21, 21, 9, 11, 10, 13, 12)
    return bytes(record)


def _make_sector(section_id, counter, payload=None):
    sector = bytearray(v.SECTOR_SIZE)
    if payload is not None:
        sector[:len(payload)] = payload
    struct.pack_into('<H', sector, v.SECTION_ID_OFFSET, section_id)
    struct.pack_into('<H', sector, v.SECTION_CHECKSUM_OFFSET,
                     v.calculate_save_checksum(sector[:v.SECTION_LENGTHS[section_id]]))
    struct.pack_into('<I', sector, v.SECTION_SIGNATURE_OFFSET, v.FILE_SIGNATURE)
    struct.pack_into('<I', sector, v.SECTION_COUNTER_OFFSET, counter)
    return bytes(sector)


def _make_slot(counter, permutation):
    logical = []
    for sid in range(v.SLOT_SECTORS):
        payload = bytearray(v.SECTION_LENGTHS[sid])
        if sid == 1:
            payload[v.PARTY_COUNT_OFFSET] = 1
            mon = _make_party_record()
            payload[v.PARTY_OFFSET:v.PARTY_OFFSET + len(mon)] = mon
        logical.append(_make_sector(sid, counter, payload))
    return b''.join(logical[sid] for sid in permutation)


def _make_save():
    body = bytearray(b'\x00' * v.FLASH_SIZE)
    perm0 = [10, 11, 12, 13, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    perm1 = [11, 12, 13, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    body[:14 * v.SECTOR_SIZE] = _make_slot(4, perm0)
    body[14 * v.SECTOR_SIZE:28 * v.SECTOR_SIZE] = _make_slot(3, perm1)
    body[30 * v.SECTOR_SIZE] = 1
    return bytes(body) + bytes(range(16))


def _profile_patches(raw):
    r = v.verify_bytes(raw)
    return (
        mock.patch.object(w, 'EXPECTED_INPUT_SHA256', hashlib.sha256(raw).hexdigest()),
        mock.patch.object(w, 'EXPECTED_SECTOR30_SHA256', hashlib.sha256(r.sector30).hexdigest()),
        mock.patch.object(w, 'EXPECTED_SECTOR31_SHA256', hashlib.sha256(r.sector31).hexdigest()),
        mock.patch.object(w, 'EXPECTED_FOOTER_SHA256', hashlib.sha256(r.footer).hexdigest()),
    )


class BatchTests(unittest.TestCase):
    def test_private_seals_are_exact(self):
        self.assertEqual(w.EXPECTED_INPUT_SHA256,
                         '6beecced342360dff979b627890c800c6f5b71849cf633464800add33db3c600')
        self.assertEqual(w.CAPABILITIES['ball'].new_value, 11)
        self.assertEqual(
            w.EXPECTED_SEALS[('ball', 'friendship', 'markings')]['output_sha256'],
            '65820082d6ced2ad3081e24b27884b6f6f29b5a321b49aecc057995f24ad58bd')

    def test_each_field_derives_in_own_envelope(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            for name in ('friendship', 'markings', 'ball'):
                out, fp = w.derive_candidate(raw, (name,))
                after = v.verify_bytes(out).party[0]
                self.assertEqual(getattr(after, name), w.CAPABILITIES[name].new_value)
                allowed = {
                    0x5000 + v.PARTY_OFFSET + w.CAPABILITIES[name].record_offset,
                    0x5000 + v.SECTION_CHECKSUM_OFFSET,
                    0x5000 + v.SECTION_CHECKSUM_OFFSET + 1,
                }
                self.assertTrue(all(i in allowed for i, _, _ in fp.diffs))

    def test_combined_is_order_independent_and_changes_only_authorized_fields(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            a, fa = w.derive_candidate(raw, ('friendship', 'ball', 'markings'))
            b, fb = w.derive_candidate(raw, ('markings', 'friendship', 'ball'))
        self.assertEqual(a, b)
        self.assertEqual(fa.selected_fields, ('ball', 'friendship', 'markings'))
        self.assertEqual(fa, fb)
        mon = v.verify_bytes(a).party[0]
        self.assertEqual((mon.friendship, mon.markings, mon.ball), (52, 1, 11))

    def test_unknown_or_unsealed_combinations_reject(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, 'unsupported batch field'):
                w.derive_candidate(raw, ('held_item',))
            with self.assertRaisesRegex(w.WriterError, 'not sealed'):
                w.derive_candidate(raw, ('friendship', 'ball'))

    def test_wrong_starting_value_rejects(self):
        raw = bytearray(_make_save())
        raw[0x5000 + v.PARTY_OFFSET + 41] = 50
        base = 0x5000
        struct.pack_into('<H', raw, base + v.SECTION_CHECKSUM_OFFSET,
                         v.calculate_save_checksum(raw[base:base + v.SECTION_LENGTHS[1]]))
        raw = bytes(raw)
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(w.WriterError, 'profile mismatch'):
                w.derive_candidate(raw, ('friendship',))

    def test_private_seal_rejects_synthetic_candidate(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            _, fp = w.derive_candidate(raw, ('ball', 'friendship', 'markings'))
            with self.assertRaisesRegex(w.WriterError, 'non-allowlisted|unexpected batch output'):
                w.require_sealed(fp)

    def test_new_file_and_overwrite_safety(self):
        raw = _make_save()
        patches = _profile_patches(raw)
        with patches[0], patches[1], patches[2], patches[3]:
            out, fp = w.derive_candidate(raw, ('ball', 'friendship', 'markings'))
            with mock.patch.dict(
                w.EXPECTED_SEALS,
                {fp.selected_fields: {'output_sha256': fp.output_sha256, 'diffs': fp.diffs}},
                clear=True,
            ):
                with tempfile.TemporaryDirectory() as td:
                    src = Path(td) / 'in.sav'
                    dst = Path(td) / 'out.sav'
                    src.write_bytes(raw)
                    result = w.write_output(src, dst, fp.selected_fields)
                    self.assertEqual(result, fp)
                    self.assertEqual(src.read_bytes(), raw)
                    self.assertEqual(dst.read_bytes(), out)
                    with self.assertRaisesRegex(w.WriterError, 'overwrite the input'):
                        w.write_output(src, src, fp.selected_fields)
                    with self.assertRaisesRegex(w.WriterError, 'existing output path'):
                        w.write_output(src, dst, fp.selected_fields)

if __name__ == '__main__':
    unittest.main()
