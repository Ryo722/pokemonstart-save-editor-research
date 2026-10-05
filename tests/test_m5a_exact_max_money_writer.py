import hashlib, importlib.util, struct, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('w',str(Path(__file__).parents[1]/'pokemonstart_m5a_exact_max_money_writer.py'))
w=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(w)

def mksec(sid,counter,payload=None):
    s=bytearray(w.SECTOR_SIZE)
    if payload: s[:len(payload)]=payload
    struct.pack_into('<H',s,w.SECTION_ID_OFFSET,sid)
    struct.pack_into('<I',s,w.SECTION_SIGNATURE_OFFSET,w.FILE_SIGNATURE)
    struct.pack_into('<I',s,w.SECTION_COUNTER_OFFSET,counter)
    struct.pack_into('<H',s,w.SECTION_CHECKSUM_OFFSET,w.checksum(s[:w.SECTION_LENGTHS[sid]]))
    return bytes(s)

def mksave(money=3000,key=0):
    sections={}
    for sid in range(14):
        p=bytearray(w.SECTION_LENGTHS[sid])
        if sid==0: struct.pack_into('<I',p,w.KEY_OFFSET,key)
        if sid==1: struct.pack_into('<I',p,w.MONEY_OFFSET,money^key)
        sections[sid]=mksec(sid,1,p)
    order=[13,0,1,2,3,4,5,6,7,8,9,10,11,12]
    slot1=b''.join(sections[i] for i in order)
    flash=bytearray(b'\x00'*w.FLASH_SIZE)
    flash[:14*w.SECTOR_SIZE]=b'\xff'*(14*w.SECTOR_SIZE)
    flash[14*w.SECTOR_SIZE:28*w.SECTOR_SIZE]=slot1
    return bytes(flash)+bytes(range(16))

def manual_candidate(raw):
    out=bytearray(raw)
    money_abs=16*w.SECTOR_SIZE+w.MONEY_OFFSET
    struct.pack_into('<I',out,money_abs,w.TARGET_MONEY)
    base=16*w.SECTOR_SIZE
    struct.pack_into('<H',out,base+w.SECTION_CHECKSUM_OFFSET,w.checksum(out[base:base+w.SECTION_LENGTHS[1]]))
    return bytes(out)

class Tests(unittest.TestCase):
    def test_synthetic_exact_transform_and_full_diff(self):
        raw=mksave(); expected=manual_candidate(raw)
        diffs=w.exact_diffs(raw,expected)
        with patch.object(w,'EXPECTED_INPUT_SHA256',hashlib.sha256(raw).hexdigest()), \
             patch.object(w,'EXPECTED_DIFFS',diffs), patch.object(w,'EXPECTED_OUTPUT_SHA256',None):
            out,r=w.derive_candidate(raw)
        self.assertEqual(out,expected); self.assertEqual(r['target_money'],9_999_999)
        self.assertEqual(w.inspect(out)['money'],9_999_999)

    def test_nonzero_key_xor_semantics_in_helper_path(self):
        raw=mksave(key=0x12345678); expected=bytearray(raw)
        struct.pack_into('<I',expected,16*w.SECTOR_SIZE+w.MONEY_OFFSET,w.TARGET_MONEY^0x12345678)
        base=16*w.SECTOR_SIZE
        struct.pack_into('<H',expected,base+w.SECTION_CHECKSUM_OFFSET,w.checksum(expected[base:base+w.SECTION_LENGTHS[1]]))
        expected=bytes(expected); diffs=w.exact_diffs(raw,expected)
        with patch.object(w,'EXPECTED_INPUT_SHA256',hashlib.sha256(raw).hexdigest()), \
             patch.object(w,'EXPECTED_KEY',0x12345678), patch.object(w,'EXPECTED_DIFFS',diffs), \
             patch.object(w,'EXPECTED_OUTPUT_SHA256',None):
            out,_=w.derive_candidate(raw)
        self.assertEqual(w.inspect(out)['money'],9_999_999)

    def test_wrong_hash_rejected(self):
        with self.assertRaisesRegex(w.ProofError,'unrecognized input'):
            w.derive_candidate(mksave())

    def test_wrong_starting_money_rejected(self):
        raw=mksave(money=2999)
        with patch.object(w,'EXPECTED_INPUT_SHA256',hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(w.ProofError,'money mismatch'):
                w.derive_candidate(raw)

    def test_new_file_only_and_source_immutable(self):
        raw=mksave(); expected=manual_candidate(raw); diffs=w.exact_diffs(raw,expected)
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'in.sav'; out=Path(d)/'out.sav'; src.write_bytes(raw)
            before=hashlib.sha256(src.read_bytes()).hexdigest()
            with patch.object(w,'EXPECTED_INPUT_SHA256',before), patch.object(w,'EXPECTED_DIFFS',diffs), patch.object(w,'EXPECTED_OUTPUT_SHA256',None):
                r=w.write_new(src,out)
                self.assertTrue(out.exists()); self.assertTrue(r['source_immutable'])
                with self.assertRaisesRegex(w.ProofError,'output already exists'):
                    w.write_new(src,out)
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),before)

if __name__=='__main__': unittest.main()
