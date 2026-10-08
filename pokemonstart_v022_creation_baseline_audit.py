"""Independent read-only E4 complete baseline, not a save writer.

Direct owner/ROM reads and the adopted independent E3 calculator. No production
constructor/writer imports. No source-save hash whitelist, captured PID reuse,
arbitrary identity controls, native stack contents or save mutation.
"""
from __future__ import annotations
import hashlib
import struct
import pokemonstart_v022_party_audit as e3
import pokemonstart_v022_inventory_audit as inventory

ORDINARY=frozenset(range(1,152))|{288}


def integer(value,lo,hi):
    if type(value) is not int or not lo<=value<=hi:raise ValueError('creation semantic integer range')
    return value


def native_shiny_score(owner,personality):
    return (owner&65535)^(owner>>16)^(personality&65535)^(personality>>16)


def map_domain(rom):
    """Bound only adjacent, aligned, compact group tables measured natively.

    Groups without an independently bounded adjacent extent are excluded.
    This is an explicit creator subset, not a global map-count claim.
    """
    result={}
    for group in range(79):
        start,end=struct.unpack_from('<II',rom,0x9A3D6C+group*4)
        distance=end-start
        if start%4 or end%4 or distance%4 or not 0<distance//4<=255:continue
        if not 0x08000000<=start<end<=0x08000000+len(rom):continue
        values=[]
        for number in range(distance//4):
            header=struct.unpack_from('<I',rom,start-0x08000000+number*4)[0]-0x08000000
            if not 0<=header<=len(rom)-28:
                raise ValueError('exact map header descriptor invalid')
            values.append(rom[header+20])
        result[group]=tuple(values)
    return result


class BaselineAudit:
    def __init__(self,raw,rom):
        self.report=e3.inspect(raw,rom)  # independent exact ROM/save/context gate
        self.parsed=e3.structure.parse(raw)
        self.sections=self.parsed['slots'][self.parsed['active']]['sections']
        self.context=self.report['saved_context']
        if self.context['flag_0x930']:raise ValueError('saved facility context unsupported')
        if self.sections[0][0xF26]&8:raise ValueError('saved flag0x913 shiny creation unsupported')
        if any(e3.ordinary_reasons(x,rom,self.context) for x in self.parsed['records']):
            raise ValueError('source Party outside ordinary creation runtime subset')
        inventory.restricted(raw,rom)  # independently validate restored bag image
        owner=self.sections[0]
        if owner[8] not in (0,1):raise ValueError('owner gender outside ordinary save encoding')
        if 255 not in owner[:8] or owner[:8].index(255)==0:
            raise ValueError('owner name lacks ordinary saved terminator')
        self.owner=owner
        self.rom=rom
        self.domain=map_domain(rom)
        group,number=self.sections[1][4:6]
        if group not in self.domain or number>=len(self.domain[group]):
            raise ValueError('saved map identifiers outside qualified creator domain')
        self.region=self.domain[group][number]
        if self.region==255:raise ValueError('met regionFF unsupported by creator')
        self.used_personalities={int.from_bytes(x[:4],'little') for x in self.parsed['records']}

    def personality(self,species,level,nature):
        owner=self.owner[10:14]
        for attempt in range(256):
            digest=hashlib.sha256(b'E4 ordinary non-shiny identity v1\0'+owner+
                                 struct.pack('<HBBB',species,level,nature,attempt)).digest()
            value=int.from_bytes(digest[:4],'little')
            value=value-value%25+nature
            if value>0xFFFFFFFF or value in self.used_personalities:continue
            if native_shiny_score(int.from_bytes(owner,'little'),value)>=8:return value
        raise ValueError('bounded identity generator exhausted')

    def record(self,species,level,moves,*,nature=0):
        if type(species) is not int or species not in ORDINARY:raise ValueError('ordinary creator species required')
        integer(level,1,100);integer(nature,0,24)
        if not isinstance(moves,(list,tuple)) or not 1<=len(moves)<=4:
            raise ValueError('creation requires one to four explicit supported moves')
        move_ids=[integer(x,0,997) for x in moves]+[0]*(4-len(moves))
        if not any(move_ids):raise ValueError('creation requires an occupied move slot')
        personality=self.personality(species,level,nature)
        metadata=self.rom[0x19B8B40+species*32:0x19B8B40+(species+1)*32]
        nickname=self.rom[0x16570A4+species*8:0x16570A4+species*8+7]
        if 255 not in nickname or any(x!=255 for x in nickname[nickname.index(255)+1:]):
            raise ValueError('exact species name canonical storage unsupported')
        record=bytearray(100)
        struct.pack_into('<II',record,0,personality,int.from_bytes(self.owner[10:14],'little'))
        record[8:15]=nickname
        record[17:20]=bytes([metadata[6],1,2])
        record[20:27]=self.owner[:7]
        struct.pack_into('<H',record,32,species)
        growth=metadata[19]
        if growth>=8:raise ValueError('growth group unsupported')
        experience=struct.unpack_from('<I',self.rom,0x14C5D54+growth*1024+level*4)[0]
        struct.pack_into('<I',record,36,experience)
        record[41:43]=bytes([metadata[18],3])
        for j,move in enumerate(move_ids):
            pp=self.rom[0x14A3238+move*12+4] if move else 0
            if move and not pp:raise ValueError('occupied move base PP unresolved')
            struct.pack_into('<H',record,44+j*2,move);record[52+j]=pp
        record[69]=self.region
        struct.pack_into('<H',record,70,level|(4<<7)|(self.owner[8]<<15))
        if struct.unpack_from('<H',metadata,26)[0] and personality&1:record[75]=128
        record[84:86]=bytes([level,255])
        stats=e3.reconstruct(bytes(record),self.rom)['ordinary_expected_stats']
        if stats is None:raise ValueError('ordinary initial stats unavailable')
        struct.pack_into('<7H',record,86,stats[0],*stats)
        final=bytes(record)
        if e3.ordinary_reasons(final,self.rom,self.context):raise ValueError('complete baseline eligibility failed')
        return final


def expected_record(raw,rom,request):
    """Independent final record, including adopted independent E3 overrides."""
    if (not isinstance(request,dict) or not {'species','level','moves'}<=set(request)
            or set(request)-{'species','level','moves','nature','ivs','evs','friendship','ability','held_item','shiny'}):
        raise ValueError('independent creator request contract')
    baseline=BaselineAudit(raw,rom)
    count=len(baseline.parsed['records'])
    if not 1<=count<6:
        raise ValueError('Party capacity unsupported; Box creation is not supported')
    sid=request['species']
    record=baseline.record(sid,request['level'],request['moves'],nature=request.get('nature',0))
    if 'ability' in request:
        metadata=rom[0x19B8B40+sid*32:0x19B8B40+(sid+1)*32]
        choices=(int.from_bytes(metadata[22:24],'little'),int.from_bytes(metadata[26:28],'little'))
        if type(request['ability']) is not int or not request['ability'] or request['ability'] not in choices:
            raise ValueError('independent ordinary ability target')
    if type(request.get('shiny',False)) is not bool:
        raise ValueError('independent shiny request')
    changes={x:request[x] for x in ('ivs','evs','friendship','ability','held_item') if x in request}
    if request.get('shiny') is True:changes['shiny']=True
    if changes:
        record,_=e3.expected_record(record,rom,baseline.context,changes)
    if int.from_bytes(record[:4],'little') in baseline.used_personalities:
        raise ValueError('independent personality collision')
    if record[71]&16 or e3.ordinary_reasons(record,rom,baseline.context):
        raise ValueError('independent final creator ordinary gate')
    return record


def expected_output(raw,rom,requests):
    if not isinstance(requests,list) or not requests:
        raise ValueError('independent nonempty creator list required')
    current=raw
    for request in requests:
        parsed=e3.structure.parse(current)
        count=len(parsed['records'])
        start=parsed['slots'][parsed['active']]['positions'][1]*4096
        record=expected_record(current,rom,request)
        out=bytearray(current)
        out[start+52]=count+1
        out[start+56+count*100:start+56+(count+1)*100]=record
        out[start+4086:start+4088]=e3.structure.checksum(out[start:start+4080]).to_bytes(2,'little')
        current=bytes(out)
    e3.inspect(current,rom)
    return current


def audit_output(raw,after,rom,requests):
    if after!=expected_output(raw,rom,requests):
        raise ValueError('independent complete creator output inequality')
    return {'complete_output_equal':True,'complete_record_reconstruction':True,
            'unrelated_bytes_preserved':True,'editor_footer_preserved':True,
            'gameplay_acceptance':False}
