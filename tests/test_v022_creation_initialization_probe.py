"""Synthetic malformed-map gates; these do not qualify native ROM semantics."""
import struct
import unittest
import pokemonstart_v022_creation_initialization_probe as probe


class OriginLookupGates(unittest.TestCase):
    def test_malformed_group_pointer_rejects_instead_of_reading_other_memory(self):
        rom = bytearray(0x9A3D70)
        struct.pack_into('<I',rom,0x9A3D6C,0x02000000)
        with self.assertRaisesRegex(ValueError,'outside exact ROM'):
            probe.rom_region(bytes(rom),0,0)

    def test_malformed_map_pointer_rejects_instead_of_using_pointer_as_header(self):
        rom = bytearray(0x9A3D70)
        struct.pack_into('<I',rom,0x9A3D6C,0x08000100)
        struct.pack_into('<I',rom,0x100,0xFFFFFFFF)
        with self.assertRaisesRegex(ValueError,'outside exact ROM'):
            probe.rom_region(bytes(rom),0,0)


if __name__=='__main__':
    unittest.main()
