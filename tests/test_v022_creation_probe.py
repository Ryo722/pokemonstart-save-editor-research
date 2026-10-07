"""Synthetic fail-closed tests; no exact ROM execution in the unit suite."""
import unittest
import sys
from unittest.mock import patch

import pokemonstart_v022_creation_probe as probe
from test_v022_party_writer import synthetic_inputs


class CreationInvestigationGates(unittest.TestCase):
    def test_wrong_rom_rejected_before_native_cpu(self):
        with patch.dict(sys.modules, {'unicorn':None}):
            with self.assertRaisesRegex(ValueError, 'exact ROM identity'):
                probe.ConstructorExperiment(bytes(0x20000), bytes(64))

    def test_corrupt_save_rejected_before_native_cpu(self):
        raw, rom = synthetic_inputs()
        corrupt = bytearray(raw)
        corrupt[0] ^= 1
        with patch.object(probe.model, 'extract_tables'), \
                patch.dict(sys.modules, {'unicorn':None}):
            with self.assertRaisesRegex(ValueError, 'checksum'):
                probe.ConstructorExperiment(bytes(corrupt), rom)

    def test_facility_context_rejected_before_native_cpu(self):
        raw, rom = synthetic_inputs()
        with patch.object(probe.model, 'extract_tables'), \
                patch.object(probe.audit, 'inspect', return_value={'saved_context':{'flag_0x930':True}}), \
                patch.dict(sys.modules, {'unicorn':None}):
            with self.assertRaisesRegex(ValueError, 'facility'):
                probe.ConstructorExperiment(raw, rom)


if __name__ == '__main__':
    unittest.main()
