import copy
import struct
import unittest
import pokemonstart_v022_product_acceptance as a
from test_v022_product_core import save,ROM


def resave(raw):
    result=a.core.v.verify_bytes(raw);old=result.active_slot;new=1-old
    out=bytearray(raw);counter=result.slots[old].counter+1
    for sec in result.slots[old].sections:
        dest=(new*14+(sec.physical_sector%14+1)%14)*4096
        start=sec.physical_sector*4096
        out[dest:dest+4096]=raw[start:start+4096]
        struct.pack_into('<I',out,dest+0xFFC,counter)
    return bytes(out)


class AcceptanceTests(unittest.TestCase):
    def test_two_synthetic_cycles_never_claim_game_proof(self):
        source=save();receipt=a.prepare(source,ROM,1)
        export,_=a.core.derive(source,ROM,receipt['transaction']['request'])
        returned=resave(export)
        result=a.check_return(source,returned,ROM,receipt)
        self.assertFalse(result['r4_complete']);self.assertTrue(result['requested_semantics_retained'])
        progressed=resave(returned)
        next_cycle=a.check_progress(returned,progressed,ROM)['cycle2']
        output,_=a.core.derive(progressed,ROM,next_cycle['transaction']['request'])
        self.assertFalse(a.check_return(progressed,resave(output),ROM,next_cycle)['r4_complete'])

    def test_wrong_save_receipt_no_roundtrip_fail_closed(self):
        raw=save();receipt=a.prepare(raw,ROM,1)
        out,_=a.core.derive(raw,ROM,receipt['transaction']['request'])
        with self.assertRaises(ValueError):a.check_return(raw,out,ROM,receipt)
        bad=copy.deepcopy(receipt);bad['transaction']['output_sha256']='0'*64
        with self.assertRaises(ValueError):a.check_return(raw,resave(out),ROM,bad)
        with self.assertRaises(ValueError):a.check_progress(raw,raw,ROM)

    def test_independent_basic_audit_catches_unrelated_changes(self):
        import pokemonstart_v022_product_audit as audit
        raw=save();receipt=a.prepare(raw,ROM,1)
        output,_=a.core.derive(raw,ROM,receipt['transaction']['request'])
        report=audit.audit_basic(raw,output,receipt['transaction']['request'])
        self.assertTrue(report['complete_candidate_equality'])
        bad=bytearray(output);bad[-1]^=1
        with self.assertRaises(ValueError):audit.audit_basic(raw,bytes(bad),receipt['transaction']['request'])
