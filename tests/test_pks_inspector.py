from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import pokemonstart_pks_inspector as pks


def package_for(members: list[tuple[str, bytes]]) -> bytes:
    payload = bytearray(struct.pack("<I", len(members)))
    for name, data in members:
        encoded_name = name.encode("utf-8")
        payload.extend(struct.pack("<H", len(encoded_name)))
        payload.extend(encoded_name)
        payload.extend(struct.pack("<I", len(data)))
        payload.extend(data)
    digest = hashlib.sha256(payload).digest()
    nonce = digest[:16]
    compressor = zlib.compressobj(wbits=-15)
    compressed = compressor.compress(payload) + compressor.flush()
    seed = bytearray(52)
    seed[:32] = pks.KEY
    seed[32:48] = nonce
    encrypted = bytearray(len(compressed))
    for offset in range(0, len(compressed), 32):
        seed[48:52] = (offset // 32).to_bytes(4, "little")
        stream = hashlib.sha256(seed).digest()
        for index, value in enumerate(compressed[offset:offset + 32]):
            encrypted[offset + index] = value ^ stream[index]
    return b"PKS1" + nonce + digest + encrypted


class PKSInspectorTests(unittest.TestCase):
    def test_roundtrip_decodes_member_table_and_hashes(self) -> None:
        member_data = b"BPS1 synthetic bytes"
        package = package_for([("nested/Pokemon.bps", member_data)])
        decoded = pks.decode_bytes(package)
        self.assertEqual(decoded.payload_sha256, hashlib.sha256(
            struct.pack("<I", 1) + struct.pack("<H", len(b"nested/Pokemon.bps"))
            + b"nested/Pokemon.bps" + struct.pack("<I", len(member_data))
            + member_data).hexdigest())
        self.assertEqual(decoded.members[0].name, "nested/Pokemon.bps")
        self.assertEqual(decoded.members[0].data, member_data)
        self.assertEqual(decoded.members[0].file_type, "BPS patch")

    def test_payload_hash_mismatch_is_rejected(self) -> None:
        package = bytearray(package_for([("a.txt", b"ok")]))
        package[20] ^= 1
        with self.assertRaisesRegex(pks.PackageError, "SHA-256 mismatch"):
            pks.decode_bytes(bytes(package))

    def test_malformed_member_table_is_rejected(self) -> None:
        # Integrity passes, but the single declared member has no name bytes.
        payload = struct.pack("<I", 1) + struct.pack("<H", 20)
        digest = hashlib.sha256(payload).digest()
        compressor = zlib.compressobj(wbits=-15)
        compressed = compressor.compress(payload) + compressor.flush()
        nonce = digest[:16]
        seed = bytearray(52)
        seed[:32] = pks.KEY
        seed[32:48] = nonce
        encrypted = bytearray(len(compressed))
        for offset in range(0, len(compressed), 32):
            seed[48:52] = (offset // 32).to_bytes(4, "little")
            stream = hashlib.sha256(seed).digest()
            for index, value in enumerate(compressed[offset:offset + 32]):
                encrypted[offset + index] = value ^ stream[index]
        with self.assertRaisesRegex(pks.PackageError, "member name"):
            pks.decode_bytes(b"PKS1" + nonce + digest + encrypted)

    def test_extraction_is_new_and_sanitizes_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "sample.pks"
            output = root / "decoded"
            package.write_bytes(package_for([("../../folder/a.txt", b"hello")]))
            report = pks.extract(package, output)
            member = report["members"][0]
            self.assertEqual(member["logical_name"], "../../folder/a.txt")
            self.assertEqual((output / member["output_name"]).read_bytes(), b"hello")
            self.assertTrue((output / "members.json").is_file())
            json.loads((output / "members.json").read_text())
            with self.assertRaisesRegex(pks.PackageError, "already exists"):
                pks.extract(package, output)

    def test_repo_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(pks.PackageError, "outside the repository"):
            pks.extract(Path("missing.pks"), pks.REPO / "out")


if __name__ == "__main__":
    unittest.main()
