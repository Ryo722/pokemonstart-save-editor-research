from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pokemonstart_fastlab_v022_money_reusable as money
import pokemonstart_fl2_core as core
import pokemonstart_money_reusable_audit as auditor
from test_fastlab_v022_money import _slot


def save(counters=(2, 3), values=(3000, 1234567), keys=(0, 0), footer=True):
    slots = []
    for counter, value, key in zip(counters, values, keys):
        sections = [_slot(counter, value, key)[i * 4096:(i + 1) * 4096] for i in range(14)]
        rotation = counter % 14
        slots.append(b''.join(sections[rotation:] + sections[:rotation]))
    return b''.join(slots) + bytes(4 * 4096) + (bytes(range(16)) if footer else b'')


def mutate(raw, slot, logical, offset, fmt, value, repair=True):
    out = bytearray(raw)
    for physical in range(slot * 14, (slot + 1) * 14):
        base = physical * 4096
        if struct.unpack_from('<H', raw, base + 0xFF4)[0] == logical:
            struct.pack_into(fmt, out, base + offset, value)
            if repair:
                struct.pack_into('<H', out, base + 0xFF6,
                                 auditor.checksum(bytes(out[base:base + auditor.LENGTHS[logical]])))
            return bytes(out)
    raise AssertionError('section missing')


class ReusableTests(unittest.TestCase):
    def test_both_directions_rotations_sizes_preserved(self):
        for counters in ((2, 3), (4, 3), (0, 1), (14, 15), (0x7FFFFFFE, 0x7FFFFFFD)):
            for footer in (False, True):
                with self.subTest(counters=counters, footer=footer):
                    raw = save(counters=counters, footer=footer)
                    out, receipt = money.derive(raw, {'money': auditor.TARGET})
                    self.assertEqual(receipt, auditor.audit(raw, out))
                    self.assertEqual(out[28 * 4096:], raw[28 * 4096:])
                    self.assertEqual(len(out), len(raw))

    def test_preregistered_structural_negatives(self):
        raw = save()
        cases = {
            'size': raw[:-1],
            'empty': b'\xff' * (14 * 4096) + raw[14 * 4096:],
            'partial': b'\xff' * 4096 + raw[4096:],
            'signature': mutate(raw, 0, 0, 0xFF8, '<I', 0, False),
            'checksum': mutate(raw, 1, 1, 0x290, '<I', 50, False),
            'duplicate': mutate(raw, 0, 2, 0xFF4, '<H', 1),
            'mixed counter': mutate(raw, 1, 2, 0xFFC, '<I', 5),
            'inactive key': save(keys=(1, 0)),
            'active key': save(keys=(0, 1)),
            'inactive range': save(values=(10_000_000, 30)),
            'active range': save(values=(30, 10_000_000)),
            'inactive party': mutate(raw, 0, 1, 0x34, '<B', 7),
            'active party': mutate(raw, 1, 1, 0x34, '<B', 7),
            'noop': save(values=(30, auditor.TARGET)),
        }
        for counters in ((2, 2), (2, 5), (3, 4), (0xFFFFFFFE, 0xFFFFFFFF),
                         (0, 0xFFFFFFFF), (0x7FFFFFFE, 0x7FFFFFFF)):
            cases[str(counters)] = save(counters=counters)
        for name, source in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                money.derive(source, {'money': auditor.TARGET})

    def test_requests_and_independent_corruption(self):
        raw = save()
        for request in (None, [], {}, {'money': True}, {'money': float(auditor.TARGET)},
                        {'money': str(auditor.TARGET)}, {'money': 1},
                        {'money': auditor.TARGET, 'party': {}}, {'money': auditor.TARGET, 'quantity': 3}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                money.derive(raw, request)
        out, _ = money.derive(raw, {'money': auditor.TARGET})
        corrupt = bytearray(out)
        corrupt[-1] ^= 1
        with self.assertRaises(ValueError):
            auditor.audit(raw, bytes(corrupt))

    def test_checksum_may_remain_equal(self):
        raw = save(values=(30, auditor.TARGET - 65535))
        out, receipt = money.derive(raw, {'money': auditor.TARGET})
        base = auditor.parse(raw)['slots'][1]['sections'][1]
        self.assertEqual(raw[base + 0xFF6:base + 0xFF8], out[base + 0xFF6:base + 0xFF8])
        self.assertTrue(receipt['changed_offsets'])

    def test_profile_module_and_request_gates(self):
        for supplied in ('0' * 64, ''):
            with self.assertRaises(ValueError):
                core.preview_bytes(save(), supplied, 'money', {'money': auditor.TARGET})
        with mock.patch.object(core.money, 'ROM_SHA256', '0' * 64), self.assertRaises(ValueError):
            core.inspect_bytes(save(), core.EXPECTED_ROM_SHA256)
        with mock.patch.object(core, '_profile_rom_sha', return_value='0' * 64), self.assertRaises(ValueError):
            core.inspect_bytes(save(), core.EXPECTED_ROM_SHA256)
        for request in ({'money': float(auditor.TARGET)}, {'money': True},
                        {'money': auditor.TARGET, 'party': {}}, {'money': '7654321'}):
            with self.assertRaises(ValueError):
                core.preview_bytes(save(), core.EXPECTED_ROM_SHA256, 'money', request)

    def test_party_inventory_stay_exact_gated(self):
        report = core.inspect_bytes(save(), core.EXPECTED_ROM_SHA256)
        self.assertEqual(report['supported_write_operations'], ['money'])
        for operation in ('party', 'inventory'):
            with self.assertRaises(ValueError):
                core.preview_bytes(save(), core.EXPECTED_ROM_SHA256, operation, {})

    def test_independent_resave_rotation_and_retained_slot(self):
        raw = save(values=(30, auditor.TARGET))
        parsed = auditor.parse(raw)
        out = bytearray(raw)
        for logical, base in parsed['slots'][1]['sections'].items():
            local = (base // 4096 % 14 + 1) % 14
            sector = bytearray(raw[base:base + 4096])
            struct.pack_into('<I', sector, 0xFFC, 4)
            out[local * 4096:(local + 1) * 4096] = sector
        transition = auditor.audit_resave(raw, bytes(out), auditor.TARGET)
        self.assertEqual(transition['new_counter'], 4)
        damaged = mutate(bytes(out), 1, 1, 0x290, '<I', 31)
        with self.assertRaises(ValueError):
            auditor.audit_resave(raw, damaged, auditor.TARGET)

    def test_file_publication_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source, output, rom = root / 'in.sav', root / 'out.sav', root / 'rom.gba'
            raw = save()
            source.write_bytes(raw)
            with mock.patch.object(core, 'PRIVATE_ROOT', root), \
                    mock.patch.object(core.money, 'PRIVATE_ROOT', root), \
                    mock.patch.object(core.party, 'PRIVATE_ROOT', root), \
                    mock.patch.object(core.inventory, 'PRIVATE_ROOT', root), \
                    mock.patch.object(core, '_check_rom_file', return_value=core.EXPECTED_ROM_SHA256):
                def write(destination=output):
                    return core.write_file(source, destination, rom, 'money', {'money': auditor.TARGET})
                write()
                auditor.audit(raw, output.read_bytes())
                for destination in (source, output):
                    with self.assertRaises(ValueError):
                        write(destination)
                alias = root / 'alias.sav'
                alias.symlink_to(source)
                with self.assertRaises(ValueError):
                    write(alias)
                dangling = root / 'dangling.sav'
                dangling.symlink_to(root / 'absent.sav')
                with self.assertRaises(ValueError):
                    write(dangling)
                fresh = root / 'fresh.sav'
                with mock.patch.object(core, '_check_rom_file', side_effect=[core.EXPECTED_ROM_SHA256, 'wrong']), \
                        self.assertRaises(ValueError):
                    write(fresh)
                self.assertFalse(fresh.exists())
                original = core._preview_bytes
                def race(*args):
                    result = original(*args)
                    source.write_bytes(raw[:-1])
                    return result
                with mock.patch.object(core, '_preview_bytes', side_effect=race), self.assertRaises(ValueError):
                    write(fresh)
                self.assertFalse(fresh.exists())
                source.write_bytes(raw)
                with mock.patch.object(core, '_check_rom_file', side_effect=[core.EXPECTED_ROM_SHA256,
                        core.EXPECTED_ROM_SHA256, 'wrong']), self.assertRaises(ValueError):
                    write(fresh)
                self.assertFalse(fresh.exists())
                self.assertEqual(source.read_bytes(), raw)
                read_bytes = Path.read_bytes
                def corrupt_read(path):
                    data = read_bytes(path)
                    return data[:-1] + bytes([data[-1] ^ 1]) if path == fresh else data
                with mock.patch.object(Path, 'read_bytes', corrupt_read), self.assertRaises(ValueError):
                    write(fresh)
                self.assertFalse(fresh.exists())
                def late_source_race(path):
                    data = read_bytes(path)
                    if path == fresh:
                        source.write_bytes(raw[:-1])
                    return data
                with mock.patch.object(Path, 'read_bytes', late_source_race), self.assertRaises(ValueError):
                    write(fresh)
                self.assertFalse(fresh.exists())
                source.write_bytes(raw)
                real_open = core.os.open
                def destination_race(path, flags, mode):
                    fresh.write_bytes(b'concurrent owner')
                    return real_open(path, flags, mode)
                with mock.patch.object(core.os, 'open', side_effect=destination_race), self.assertRaises(ValueError):
                    write(fresh)
                self.assertEqual(fresh.read_bytes(), b'concurrent owner')
                self.assertEqual(source.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
