"""Bounded exact-v0.22 ordinary Party record construction from semantics.

No save insertion, arbitrary identity control, source SHA whitelist or templates.
Default moves must be explicit; primary native tera type is selected internally.
"""
from __future__ import annotations
import hashlib
import struct
import pokemonstart_save_verifier as verifier
import pokemonstart_v022_party_model as e3
import pokemonstart_v022_product_party as transformations
import pokemonstart_v022_inventory_model as inventory


def location(rom, group, number):
    if not 0 <= group < 79:
        raise ValueError('map group outside qualified creator domain')
    start, end = struct.unpack_from('<II', rom, 0x9A3D6C + group*4)
    count = (end-start)//4
    if (start%4 or end%4 or (end-start)%4 or not 1 <= count <= 255
            or not 0x08000000 <= start < end <= 0x08000000+len(rom)
            or number >= count):
        raise ValueError('map identifiers outside qualified creator domain')
    header = struct.unpack_from('<I', rom, start-0x08000000+number*4)[0]-0x08000000
    if not 0 <= header <= len(rom)-28:
        raise ValueError('map header outside exact ROM')
    region = rom[header+20]
    if region == 255:
        raise ValueError('met regionFF unsupported by creator')
    return region


class Creator:
    def __init__(self, raw, rom):
        self.tables = e3.extract_tables(rom)
        self.verified = verifier.verify_bytes(raw)
        self.context = e3.saved_context(self.verified)
        active = self.verified.slots[self.verified.active_slot]
        section = active.section(1)
        self.base = section.physical_sector*4096
        if self.verified.party_count == 6:
            raise ValueError('Party is full; Box creation is not supported')
        if self.verified.party_count < 1:
            raise ValueError('empty source Party runtime context unsupported')
        if self.context['reasons']:
            raise ValueError('; '.join(self.context['reasons']))
        owner = active.section(0).data
        if owner[0xF26]&8:
            raise ValueError('saved flag 0x913 shiny creation mode unsupported')
        if owner[8] not in (0,1) or 255 not in owner[:8] or owner[:8].index(255)==0:
            raise ValueError('owner save identity encoding unsupported')
        self.used = set()
        for slot in range(self.verified.party_count):
            pos=self.base+56+slot*100
            record=raw[pos:pos+100]
            eligibility=e3.write_eligibility(record,self.tables,self.context)
            if not eligibility['eligible']:
                raise ValueError('source Party outside ordinary creator class: '+ '; '.join(eligibility['reasons']))
            self.used.add(int.from_bytes(record[:4],'little'))
        inventory.restricted(raw,rom)
        self.owner=owner
        self.rom=rom
        self.region=location(rom,*section.data[4:6])
        self.options=transformations.ordinary_options(self.tables)

    def personality(self,species,level,nature):
        owner=self.owner[10:14]
        trainer=int.from_bytes(owner,'little')
        for attempt in range(256):
            seed=b'E4 ordinary non-shiny identity v1\0'+owner+struct.pack('<HBBB',species,level,nature,attempt)
            value=int.from_bytes(hashlib.sha256(seed).digest()[:4],'little')
            value+=nature-value%25
            if value>0xFFFFFFFF or value in self.used:
                continue
            score=(trainer&65535)^(trainer>>16)^(value&65535)^(value>>16)
            if score>=8:
                return value
        raise ValueError('bounded personality generator exhausted')

    def record(self,request):
        allowed={'species','level','moves','nature','ivs','evs','friendship','ability','held_item','shiny'}
        if not isinstance(request,dict) or set(request)-allowed or not {'species','level','moves'}<=set(request):
            raise ValueError('creation requires species, level and explicit moves; unsupported controls rejected')
        number=transformations.integer
        sid=number(request['species'],1,1488,'species')
        if sid not in self.options['species']:
            raise ValueError('species outside qualified ordinary creator subset')
        level=number(request['level'],1,100,'level')
        nature=number(request.get('nature',0),0,24,'nature')
        moves=request['moves']
        if not isinstance(moves,(list,tuple)) or not 1<=len(moves)<=4:
            raise ValueError('one to four explicit move selections required')
        move_ids=[number(x,0,997,'move') for x in moves]+[0]*(4-len(moves))
        if not any(move_ids) or any(x not in self.options['moves'] for x in move_ids):
            raise ValueError('at least one qualified occupied move required')
        species=self.tables.species[sid]
        if 'ability' in request and (type(request['ability']) is not int
                                    or request['ability'] not in species.abilities[:2]
                                    or not request['ability']):
            raise ValueError('creator supports only ordinary first/second ability')
        identity=self.personality(sid,level,nature)
        record=bytearray(100)
        struct.pack_into('<II',record,0,identity,int.from_bytes(self.owner[10:14],'little'))
        name=self.rom[e3.SPECIES_NAMES+sid*8:e3.SPECIES_NAMES+sid*8+7]
        if 255 not in name or any(x!=255 for x in name[name.index(255)+1:]):
            raise ValueError('exact canonical default species name unavailable')
        record[8:15]=name
        record[17:20]=bytes((self.rom[e3.SPECIES_TABLE+sid*32+6],1,2))
        record[20:27]=self.owner[:7]
        struct.pack_into('<H',record,32,sid)
        struct.pack_into('<I',record,36,self.tables.experience[species.growth][level])
        record[41:43]=bytes((self.rom[e3.SPECIES_TABLE+sid*32+18],3))
        for slot,move in enumerate(move_ids):
            struct.pack_into('<H',record,44+slot*2,move)
            record[52+slot]=self.tables.moves[move].base_pp if move else 0
        record[69]=self.region
        struct.pack_into('<H',record,70,level|(4<<7)|(self.owner[8]<<15))
        if species.abilities[1] and identity&1:
            record[75]=128
        record[84:86]=bytes((level,255))
        stats=e3.decode_record(bytes(record),0,self.tables)['ordinary_expected_stats']
        if stats is None:
            raise ValueError('ordinary initial stats unavailable')
        struct.pack_into('<7H',record,86,stats[0],*stats)
        if 'shiny' in request and type(request['shiny']) is not bool:
            raise ValueError('shiny requires true or false')
        changes={key:request[key] for key in ('ivs','evs','friendship','ability','held_item') if key in request}
        if request.get('shiny'):
            changes['shiny']=True
        result=(transformations.transform_ordinary(bytes(record),self.tables,self.context,changes)
                if changes else bytes(record))
        if int.from_bytes(result[:4],'little') in self.used:
            raise ValueError('generated personality collides with an existing Party member')
        if not e3.write_eligibility(result,self.tables,self.context)['eligible'] or result[71]&16:
            raise ValueError('created record outside qualified ordinary class')
        return result
