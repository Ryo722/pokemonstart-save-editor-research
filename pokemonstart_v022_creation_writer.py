"""Bounded semantic Party append, independently audited immutable output."""
import struct
import pokemonstart_save_verifier as v
import pokemonstart_v022_party_model as semantics
import pokemonstart_v022_creation_model as model
import pokemonstart_v022_creation_baseline_audit as independent


def derive(raw,rom,requests):
    if not isinstance(requests,list) or not requests:
        raise ValueError('creation requires nonempty semantic request list')
    source=v.verify_bytes(raw)
    if source.party_count==6:
        raise ValueError('Party is full; Box creation is not supported')
    if len(requests)>6-source.party_count:
        raise ValueError('requested creations exceed Party capacity; Box creation is not supported')
    current=raw;created=[]
    for request in requests:
        creator=model.Creator(current,rom)
        slot=creator.verified.party_count
        record=creator.record(request)
        out=bytearray(current)
        out[creator.base+v.PARTY_COUNT_OFFSET]=slot+1
        start=creator.base+v.PARTY_OFFSET+slot*100
        out[start:start+100]=record
        struct.pack_into('<H',out,creator.base+0xFF6,v.calculate_save_checksum(out[creator.base:creator.base+v.SECTION_LENGTHS[1]]))
        current=bytes(out)
        v.verify_bytes(current)
        decoded=semantics.decode_record(record,slot,creator.tables)
        created.append({'slot':slot,'species':decoded['species'],'species_name':decoded['species_name'],
                        'level':decoded['stored_level'],'nature':decoded['effective_nature'],
                        'moves':list(request['moves']),'ability':decoded['resolved_ability'],
                        'held_item':decoded['held_item'],'friendship':decoded['friendship'],
                        'ivs':decoded['ivs'],'evs':decoded['evs'],
                        'identity_policy':'Owner-consistent, non-shiny, default species name; generated identity is not editable'})
    proof=independent.audit_output(raw,current,rom,requests)
    return current,{'e4':True,'created':created,'party_count':{'from':source.party_count,'to':source.party_count+len(requests)},
                    'independent_audit':proof}
