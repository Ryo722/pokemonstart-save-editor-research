"""Read-only E4 complete-record native qualification, sanitized aggregates only.

Isolated exact RAM execution, not Human gameplay/game-load/flash SAVE evidence.
Native stack tail is replaced only through the traced native evolution setter.
Explicit moves/PP replace automatic learnsets using exact native setters.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_creation_baseline_audit as independent
import pokemonstart_v022_creation_model as production
import pokemonstart_v022_party_audit as e3
from pokemonstart_v022_creation_probe import ConstructorExperiment
from pokemonstart_v022_creation_initialization_probe import call


def probe(raw,rom,*,broad=False):
    baseline=independent.BaselineAudit(raw,rom)
    maker=production.Creator(raw,rom)
    e=ConstructorExperiment(raw,rom)
    species_set=sorted(independent.ORDINARY) if broad else [1,19,25,29,32,63,129,133,150,288]
    cases=0;maximum_attempts=0;genders=set();growth=set();lengths=set()
    for species in species_set:
        for level in (1,3,20,100):
            for nature in (0,1,12,24):
                moves=[33,1] if level>=20 else [33]
                request={'species':species,'level':level,'nature':nature,'moves':moves}
                expected=baseline.record(species,level,moves,nature=nature)
                if maker.record(request)!=expected:raise ValueError('independent/production baseline inequality')
                personality=int.from_bytes(expected[:4],'little')
                for attempt in range(256):
                    seed=int.from_bytes(hashlib.sha256(b'E4 constructor RNG v1\0'+baseline.owner[10:14]+
                                    struct.pack('<HBBB',species,level,nature,attempt)).digest()[:4],'little')
                    actual=e.construct(species,level,personality,0,seed=seed)
                    if not e.native_shiny() and actual[:4]==expected[:4] and actual[17]==expected[17]:break
                else:raise ValueError('bounded native supported outcome exhausted')
                # Sole baseline storage canonicalization: exact default-name
                # predicate invokes setter with exact fixed species-name field.
                call(e,0x08042C5C,0x02001000,species,species)
                for j,move in enumerate(moves+[0]*(4-len(moves))):
                    if move and call(e,0x0804070C,move,0,j)!=expected[52+j]:
                        raise ValueError('native initial maximum PP disagreement')
                    e.cpu.mem_write(0x02008000,struct.pack('<I',move))
                    call(e,0x0803FA70,0x02001000,13+j,0x02008000)
                    e.cpu.mem_write(0x02008000,struct.pack('<I',expected[52+j]))
                    call(e,0x0803FA70,0x02001000,17+j,0x02008000)
                actual=bytes(e.cpu.mem_read(0x02001000,100))
                if actual!=expected:raise ValueError('complete native record inequality')
                trainer=int.from_bytes(baseline.owner[10:14],'little')
                if call(e,0x08043AE4,trainer,personality) or call(e,0x080425A4,personality)!=nature:
                    raise ValueError('native shiny/nature postcondition failed')
                ratio=rom[0x19B8B40+species*32+16]
                gender=ratio if ratio in (0,254,255) else 254 if personality&255<ratio else 0
                if call(e,0x0803EEF8,species,personality)!=gender or call(e,0x0803EE8C,0x02001000)!=gender:
                    raise ValueError('independent native gender disagreement')
                if call(e,0x0804042C,0x02001000)!=e3.reconstruct(expected,rom)['resolved_ability']:
                    raise ValueError('native ordinary ability disagreement')
                cases+=1;maximum_attempts=max(maximum_attempts,attempt+1)
                genders.add(gender);growth.add(rom[0x19B8B40+species*32+19]);lengths.add(expected[8:15].index(255))
    identity_cases=0
    for species in species_set:
        for level in (1,3,20,100):
            for nature in range(25):
                record=maker.record({'species':species,'level':level,'nature':nature,'moves':[33]})
                if record!=baseline.record(species,level,[33],nature=nature):
                    raise ValueError('all-nature independent identity baseline inequality')
                personality=int.from_bytes(record[:4],'little');trainer=int.from_bytes(record[4:8],'little')
                e.cpu.mem_write(0x02001000,record)
                if call(e,0x08043AE4,trainer,personality) or call(e,0x080425A4,personality)!=nature:
                    raise ValueError('all-nature native identity predicates failed')
                ratio=rom[0x19B8B40+species*32+16]
                gender=ratio if ratio in (0,254,255) else 254 if personality&255<ratio else 0
                if call(e,0x0803EEF8,species,personality)!=gender:
                    raise ValueError('all-nature native gender failed')
                if call(e,0x0804042C,0x02001000)!=e3.reconstruct(record,rom)['resolved_ability']:
                    raise ValueError('all-nature native ordinary ability failed')
                identity_cases+=1
    origin_cases=0
    for group,regions in baseline.domain.items():
        for number,region in enumerate(regions):
            e.cpu.mem_write(e.BLOCK1_ADDRESS+4,bytes((group,number)))
            if call(e,0x08055B20)!=region:raise ValueError('native current-region disagreement')
            origin_cases+=1
    shiny_cases=0
    for trainer in (0,0x12345678,0xFFFFFFFF):
        for score in range(33):
            low=0x4321;high=(trainer&65535)^(trainer>>16)^low^score
            if bool(call(e,0x08043AE4,trainer,low|(high<<16)))!=(score<8):
                raise ValueError('independent shiny predicate disagreement')
            shiny_cases+=1
    # All primary/secondary type outcomes over native RNG controls. Primary
    # selection is a native permitted outcome, not an equivalence assertion.
    tera_cases=0
    for species in species_set:
        allowed=set(rom[0x19B8B40+species*32+6:0x19B8B40+species*32+8]);outputs=set()
        for seed in range(32):
            e.cpu.mem_write(0x03005040,struct.pack('<I',seed))
            result=call(e,0x090F4D64,species)
            if result not in allowed:raise ValueError('native type outcome outside ordinary species types')
            outputs.add(result);tera_cases+=1
        if rom[0x19B8B40+species*32+6] not in outputs:raise ValueError('primary native type outcome missing')
    overrides=0
    for species in (1,19,25,288):
        for level in (1,3,20,100):
            for nature in (3,10):
                request={'species':species,'level':level,'nature':nature,'moves':[33,39,98,0],
                         'ivs':[31,0,17,31,5,29] if nature==3 else [31]*6,
                         'evs':[0]*6 if level<20 else [4,252,0,0,252,0],
                         'friendship':123,'held_item':(0,139,142,200)[(species+level+nature)%4]}
                abilities=maker.tables.species[species].abilities[:2]
                request['ability']=abilities[1] or abilities[0]
                final=maker.record(request)
                if final!=independent.expected_record(raw,rom,request):raise ValueError('independent override record inequality')
                e.construct(species,level,int.from_bytes(final[:4],'little'),0)
                e.cpu.mem_write(0x02001000,final)
                call(e,0x0803DBE8,0x02001000)
                if bytes(e.cpu.mem_read(0x02001000,100))!=final:raise ValueError('native override stat recalculation changed record')
                if call(e,0x0804042C,0x02001000)!=request['ability']:raise ValueError('native override ability mismatch')
                overrides+=1
    return {'rom_sha256':profile.sha(rom),'save_sha256':profile.sha(raw),
            'evidence_class':'exact-ROM isolated private-input machine qualification',
            'complete_100_byte_cases':cases,'all_25_nature_identity_cases':identity_cases,'complete_record_agreement':True,
            'maximum_native_outcome_attempts':maximum_attempts,'gender_classes':sorted(genders),
            'growth_groups':sorted(growth),'name_lengths':sorted(lengths),
            'qualified_map_groups':len(baseline.domain),'native_origin_cases':origin_cases,
            'synthetic_owner_shiny_predicate_cases':shiny_cases,'native_type_outcome_cases':tera_cases,
            'independent_override_native_recalculation_cases':overrides,
            'native_predicates_agree':True,'unexplained_creator_bytes':0,'human_gameplay':False,
            'limits':['ordinary standalone RAM context; no game-load or full UI rendering',
                      'excluded map groups and regionFF fail closed; no global map-count claim',
                      'explicit moves replace automatic learnsets; no arbitrary nickname/identity controls']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--save',type=Path,required=True)
    p.add_argument('--broad',action='store_true');args=p.parse_args()
    rp=profile._private_file(args.rom,'ROM',must_exist=True);sp=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rp.read_bytes(),sp.read_bytes();result=probe(raw,rom,broad=args.broad)
    if rp.read_bytes()!=rom or sp.read_bytes()!=raw:raise ValueError('source inputs changed')
    result['sources_immutable']=True;print(json.dumps(result,indent=2))

if __name__=='__main__':main()
