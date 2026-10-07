"""Exact native ordinary creation mode/outcome controls; read-only experiment.

Saved Party/bag are restored by the exact initializer. RAM flag/fishing/battle
variants are explicitly synthetic. Acceptance of a native non-shiny/primary
outcome is separate from recreating a game's RNG stream or special modes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_creation_baseline_audit as baseline
from pokemonstart_v022_creation_probe import ConstructorExperiment
from pokemonstart_v022_creation_initialization_probe import call,FLAG_STORAGE


def probe(raw,rom):
    from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ
    a=baseline.BaselineAudit(raw,rom);e=ConstructorExperiment(raw,rom);u,r=e.cpu,e.reg
    variants=[(),((0x0203DFC0,1),),((0x0203DFC0,255),),((0x0203DFD0,1),),
              ((0x0203DFD0,0xFFFFFFFF),),((0x03003569,2),),((0x03003569,255),),
              ((0x0203DFC0,255),(0x0203DFD0,0xFFFFFFFF),(0x03003569,255))]
    cases=0;maximum=0;helpers=set();reads=set()
    def events(cpu,pc,size,data):
        if pc in (0x090B7380,0x090B7E6C,0x08099948):helpers.add(hex(pc))
    def runtime_reads(cpu,access,address,size,value,data):
        if address in (0x03005ED8,0x0203DFC0,0x0203DFD0,0x03003569,0x020397E4):reads.add(hex(address))
    h=u.hook_add(UC_HOOK_CODE,events);read_hook=u.hook_add(UC_HOOK_MEM_READ,runtime_reads)
    for flag828 in (False,True):
        for flag12f8 in (False,True):
            true=[f for f,v in ((0x828,flag828),(0x12F8,flag12f8)) if v]
            false=[0x913,*[f for f,v in ((0x828,flag828),(0x12F8,flag12f8)) if not v]]
            for species in (1,19,25,288):
                for controls in variants:
                    expected=a.record(species,20,[33,39],nature=3)
                    personality=int.from_bytes(expected[:4],'little')
                    for attempt in range(256):
                        seed=int.from_bytes(hashlib.sha256(b'E4 creation context control v1\0'+
                                            struct.pack('<HBBB',species,flag828,flag12f8,attempt)).digest()[:4],'little')
                        actual=e.construct(species,20,personality,0,seed=seed,
                                          set_flags=true,clear_flags=false,runtime_controls=controls)
                        if not e.native_shiny() and actual[:4]==expected[:4] and actual[17]==expected[17]:break
                    else:raise ValueError('ordinary native context has no bounded supported construction outcome')
                    call(e,0x08042C5C,0x02001000,species,species)
                    for j,move in enumerate((33,39,0,0)):
                        u.mem_write(0x02008000,struct.pack('<I',move));call(e,0x0803FA70,0x02001000,13+j,0x02008000)
                        u.mem_write(0x02008000,struct.pack('<I',expected[52+j]));call(e,0x0803FA70,0x02001000,17+j,0x02008000)
                    if bytes(u.mem_read(0x02001000,100))!=expected:
                        raise ValueError('native context changes complete supported record')
                    cases+=1;maximum=max(maximum,attempt+1)
    bag_cases=0
    original_key_start=30*4096+0x5DC
    key_entries=[struct.unpack_from('<HH',raw,original_key_start+i*4) for i in range(75)]
    for keep471 in (False,True):
        for keep833 in (False,True):
            modified=bytearray(raw)
            entries=[row for row in key_entries if row[0] and (row[0]!=471 or keep471) and (row[0]!=833 or keep833)]
            modified[original_key_start:original_key_start+300]=bytes(300)
            for i,row in enumerate(entries):struct.pack_into('<HH',modified,original_key_start+i*4,*row)
            struct.pack_into('<H',modified,0x1E718,len(entries))
            context_raw=bytes(modified)
            context=baseline.BaselineAudit(context_raw,rom)
            native=ConstructorExperiment(context_raw,rom)
            for species in (1,19,25,288):
                expected=context.record(species,20,[33],nature=3)
                pid=int.from_bytes(expected[:4],'little')
                for seed in range(256):
                    actual=native.construct(species,20,pid,0,seed=seed)
                    if not native.native_shiny() and actual[:4]==expected[:4] and actual[17]==expected[17]:break
                else:raise ValueError('bag context supported outcome exhausted')
                call(native,0x08042C5C,0x02001000,species,species)
                for j,move in enumerate((33,0,0,0)):
                    native.cpu.mem_write(0x02008000,struct.pack('<I',move));call(native,0x0803FA70,0x02001000,13+j,0x02008000)
                    native.cpu.mem_write(0x02008000,struct.pack('<I',expected[52+j]));call(native,0x0803FA70,0x02001000,17+j,0x02008000)
                if bytes(native.cpu.mem_read(0x02001000,100))!=expected:
                    raise ValueError('bag context changes complete record')
                if bool(call(native,0x08099948,471,1))!=keep471 or bool(call(native,0x08099948,833,1))!=keep833:
                    raise ValueError('native saved key bag context disagrees')
                bag_cases+=1
    u.hook_del(h);u.hook_del(read_hook)
    e.construct(19,5,0x12345678,0)
    flags=[]
    for flag,(section,offset,mask) in FLAG_STORAGE.items():
        e.construct(19,5,0x12345678,0)
        saved=bool(e.sections[section][offset]&mask)
        if bool(call(e,0x0806DEC4,flag))!=saved:raise ValueError('native saved flag disagreement')
        flags.append({'flag':hex(flag),'section':section,'offset':hex(offset),'mask':mask,'saved_native_agree':True})
    e.construct(19,5,0x12345678,0)
    bag=[{'item_id':x,'present':bool(call(e,0x08099948,x,1))} for x in (471,833)]
    e.construct(19,5,0x12345678,0,clear_flags=(0x913,))
    ordinary=not e.native_shiny()
    forced=e.construct(19,5,0x12345678,0,set_flags=(0x913,))
    if not ordinary or not e.native_shiny():raise ValueError('saved913 force/reject discriminator failed')
    # Exact current-region returns the header byte unchanged, even FF.
    # Inject only the loaded register at its exact return boundary; this is
    # not a claim that a retained save naturally inhabits a regionFF map.
    region_controls=[]
    for value in (0,88,89,255):
        def override(cpu,pc,size,data):
            if pc==0x08055B3E:cpu.reg_write(r.UC_ARM_REG_R0,value)
        h=u.hook_add(UC_HOOK_CODE,override)
        result=call(e,0x08055B20);u.hook_del(h)
        if result!=value:raise ValueError('current region unexpectedly transforms loaded header byte')
        region_controls.append({'loaded_region':value,'native_return_equal':True})
    return {'rom_sha256':profile.sha(rom),'save_sha256':profile.sha(raw),
            'evidence_class':'exact-ROM private-input execution with synthetic saved-mode/runtime controls',
            'complete_record_context_cases':cases,'complete_record_saved_bag_presence_cases':bag_cases,'maximum_native_outcome_attempts':maximum,
            'flag_storage':flags,'actual_native_saved_bag_queries':bag,'native_helpers_reached':sorted(helpers),
            'observed_runtime_reads':sorted(reads),'region_return_controls':region_controls,
            'saved913_false_ordinary_true_shiny_discriminator':True,'human_gameplay':False,
            'limits':['routing03005ED8=0 is supported ordinary standalone context; alternate routes are excluded',
                      'valid bag pointer is reconstructed, not adversarial garbage admitted',
                      'fishing/live-battle controls may affect RNG branches; only accepted non-shiny/primary outcomes qualified',
                      'no global runtime irrelevance or complete game-load reconstruction claim']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--save',type=Path,required=True);args=p.parse_args()
    rp=profile._private_file(args.rom,'ROM',must_exist=True);sp=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rp.read_bytes(),sp.read_bytes();result=probe(raw,rom)
    if rp.read_bytes()!=rom or sp.read_bytes()!=raw:raise ValueError('source inputs changed')
    result['sources_immutable']=True;print(json.dumps(result,indent=2))

if __name__=='__main__':main()
