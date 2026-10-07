"""Read-only exact-ROM paired-tail downstream investigation, never a writer.

RAM widgets/I/O are common synthetic execution context, not game-load evidence.
No renderer/constructor routine is replaced. Stop hooks expose boundaries.
Only hashes, addresses and equality/length observations leave the experiment.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as model
import pokemonstart_v022_party_audit as audit
from pokemonstart_v022_creation_probe import ConstructorExperiment
from pokemonstart_v022_creation_initialization_probe import call


def tail_variants(record):
    if len(record)!=100:
        raise ValueError('paired record length')
    try:
        end=record[8:15].index(255)+8
    except ValueError:
        raise ValueError('paired record lacks valid nickname terminator') from None
    result=[]
    for fill in (0,255,0xA5,0x5A):
        v=bytearray(record)
        v[end+1:15]=bytes([fill])*(14-end)
        if v[:end+1]!=record[:end+1] or v[15:]!=record[15:]:
            raise ValueError('paired record changed outside nickname tail')
        result.append(bytes(v))
    return result


def terminated(data):
    return data[:data.index(255)+1]


def probe(raw,rom,*,broad=False):
    from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ
    e=ConstructorExperiment(raw,rom)
    u,r=e.cpu,e.reg
    u.mem_map(0x04000000,4096)  # common non-link serial register controls
    species_set=sorted(model.ORDINARY_SPECIES) if broad else [1,19,25,29,32,63,129,133,150,288]
    rows=[]
    for species in species_set:
        record=e.construct(species,5,0x12345678,0)
        variants=tail_variants(record)
        path_outputs={k:[] for k in ('summary','evolution_default_name','battle','serialization','party','ghost_predicate')}
        intermediate={k:[] for k in ('summary','battle','party','ghost_predicate')}
        default_status=[]; battle_calls=[]; party_calls=[]
        eos_checks=[]
        for variant in variants:
            # Reset each common runtime using the native constructor, then
            # install exactly the same paired record in the consumer's slot.
            e.construct(species,5,0x12345678,0)
            u.mem_write(0x02001000,variant)
            # Native evolution/default-name rule; same-species rename exposes
            # exact fixed-field normalization without changing any other field.
            setters=[]
            def evolution_hook(cpu,pc,size,data):
                if pc==0x0803FA70 and cpu.reg_read(r.UC_ARM_REG_R1)==2:
                    setters.append(True)
            h=u.hook_add(UC_HOOK_CODE,evolution_hook)
            call(e,0x08042C5C,0x02001000,species,species)
            u.hook_del(h)
            path_outputs['evolution_default_name'].append(bytes(u.mem_read(0x02001000,100)))
            default_status.append(bool(setters))
            # Summary currentMon offset independently identified by its getter.
            u.mem_write(0x02020000,bytes(0x3400))
            u.mem_write(0x0202323C,variant)
            u.mem_write(0x0203B0B4,struct.pack('<I',0x02020000))
            u.mem_write(0x0203B0B8,struct.pack('<I',0x02024000))
            summary_temp=[]; boundaries=[]
            def summary_hook(cpu,pc,size,data):
                if pc==0x08008E10:
                    summary_temp.append(bytes(cpu.mem_read(cpu.reg_read(r.UC_ARM_REG_R1),20)))
                if pc==0x081369D6:
                    boundaries.append(True);cpu.emu_stop()
            h=u.hook_add(UC_HOOK_CODE,summary_hook)
            u.reg_write(r.UC_ARM_REG_SP,0x03007000)
            u.reg_write(r.UC_ARM_REG_LR,0x06000001)
            u.emu_start(0x081368D9,0x06000000,count=1000000)
            u.hook_del(h)
            if len(boundaries)!=1 or len(summary_temp)!=1:
                raise ValueError('summary copy boundary not reached exactly once')
            intermediate['summary'].append(summary_temp[0])
            path_outputs['summary'].append(bytes(u.mem_read(0x02023034,20)))
            # Actual patched battle placeholder expansion; no generic-string
            # substitute. Player Party left-name token05 is measured native.
            u.mem_write(0x020241E4,variant)
            u.mem_write(0x02022AAC,bytes(4))
            u.mem_write(0x02023B2E,bytes(8))
            u.mem_write(0x03003F7C,bytes(1))
            u.mem_write(0x02008000,bytes([0xFD,5,0xFF]))
            u.mem_write(0x02008100,bytes([0xCC])*80)
            nickname_dest=[]; events=[]
            def battle_hook(cpu,pc,size,data):
                if pc==0x0803F354 and cpu.reg_read(r.UC_ARM_REG_R1)==2:
                    nickname_dest.append(cpu.reg_read(r.UC_ARM_REG_R2))
                    events.append(hex(cpu.reg_read(r.UC_ARM_REG_LR)-1))
            h=u.hook_add(UC_HOOK_CODE,battle_hook)
            call(e,0x080D88A8,0x02008000,0x02008100)
            u.hook_del(h)
            if len(nickname_dest)!=1:
                raise ValueError('battle ordinary nickname getter not reached once')
            intermediate['battle'].append(bytes(u.mem_read(nickname_dest[0],20)))
            path_outputs['battle'].append(bytes(u.mem_read(0x02008100,80)))
            battle_calls.append(events)
            # Party actual display path through native text printer; stop at
            # shared RenderText before glyph rendering, exposing its string.
            u.mem_write(0x02001000,variant)
            u.mem_write(0x02008000,bytes(128))
            u.mem_write(0x02008000,struct.pack('<I',0x02008040))
            u.mem_write(0x03003DD0,struct.pack('<I',0x083E30E8))
            printer_strings=[]; events=[]
            def party_hook(cpu,pc,size,data):
                if pc in (0x08121ED8,0x0812ED24,0x08002CF0,0x08002E4C,0x08005348,0x0800575C):
                    events.append(hex(pc))
                if pc==0x08121ED8:
                    printer_strings.append(bytes(cpu.mem_read(cpu.reg_read(r.UC_ARM_REG_R1),20)))
                if pc==0x0800575C:
                    cpu.emu_stop()
            h=u.hook_add(UC_HOOK_CODE,party_hook)
            u.reg_write(r.UC_ARM_REG_SP,0x03007000)
            u.reg_write(r.UC_ARM_REG_LR,0x06000001)
            for reg,value in zip((r.UC_ARM_REG_R0,r.UC_ARM_REG_R1,r.UC_ARM_REG_R2),(0x02001000,0x02008000,0)):
                u.reg_write(reg,value)
            u.emu_start(0x08121F0D,0x06000000,count=1000000)
            u.hook_del(h)
            if not printer_strings or '0x800575c' not in events:
                raise ValueError('Party display to RenderText boundary not reached')
            intermediate['party'].append(printer_strings[0])
            path_outputs['party'].append(terminated(printer_strings[0]))
            party_calls.append(events)
            # At the actual Party-selected font interpreter, EOS completes
            # without reading any later character. No glyph routine is mocked.
            u.mem_write(0x02008000,bytes(64))
            u.mem_write(0x02008100,printer_strings[0])
            end=printer_strings[0].index(255)
            u.mem_write(0x02008000,struct.pack('<I',0x02008100+end))
            reads=[]
            def eos_read(cpu,access,address,size,value,data):
                if 0x02008100<=address<0x02008114:
                    reads.append({'offset':address-0x02008100,'size':size})
            h=u.hook_add(UC_HOOK_MEM_READ,eos_read)
            result=call(e,0x08005348,0x02008000)
            u.hook_del(h)
            eos_checks.append({'result':result,'reads':reads,'terminator_offset':end,
                'read_after_terminator':any(v['offset']+v['size']>end+1 for v in reads)})
            # Actual nickname-sensitive Ghost gameplay predicate. The normal
            # player guard has no nickname read. An adversarial opponent-side
            # Ghost control additionally exercises its real normalize/compare
            # path; it is not admitted link/facility gameplay evidence.
            u.mem_write(0x02023B36,bytes((0,1,2,3)))
            u.mem_write(0x02022AAC,bytes(4));u.mem_write(0x02001000,variant)
            if call(e,0x08043EB0,0x02001000,0):raise ValueError('ordinary player Ghost guard failed')
            u.mem_write(0x02022AAC,bytes([255])*4)
            compared=[];buffers=[]
            def ghost_hook(cpu,pc,size,data):
                if pc==0x080089A4:
                    buffers.append(bytes(cpu.mem_read(cpu.reg_read(r.UC_ARM_REG_R0),20)))
                if pc==0x08043EF8:compared.append(cpu.reg_read(r.UC_ARM_REG_R0))
            h=u.hook_add(UC_HOOK_CODE,ghost_hook)
            result=call(e,0x08043EB0,0x02001000,1);u.hook_del(h)
            if len(compared)!=1 or len(buffers)!=1:raise ValueError('actual Ghost normalize/compare path not reached')
            intermediate['ghost_predicate'].append(buffers[0])
            path_outputs['ghost_predicate'].append(struct.pack('<II',result,compared[0]))
            # Exact serializer Party component invoked by SaveSerializedGame.
            # Different fixed field persists; no canonicalization is inferred.
            u.mem_write(0x020241E4,variant)
            call(e,0x0804B9A8)
            path_outputs['serialization'].append(bytes(u.mem_read(e.BLOCK1_ADDRESS+0x38,100)))
        canonical=rom[model.SPECIES_NAMES+species*8:model.SPECIES_NAMES+species*8+7]
        row={'species':species,'name_length':record[8:15].index(255),
             'variants':len(variants),'default_status':default_status,
             'evolution_normalizes_to_exact_fixed_species_field':all(v[8:15]==canonical for v in path_outputs['evolution_default_name']),
             'battle_getter_callers':battle_calls,'party_exact_paths':party_calls,
             'actual_Party_font_EOS_checks':eos_checks,
             'paths':{}}
        for name,outputs in path_outputs.items():
            if name=='serialization':
                end=record[8:15].index(255)+8
                values=[v[:end+1]+v[15:] for v in outputs]
            else:
                values=outputs if name in ('evolution_default_name','ghost_predicate') else [terminated(v) for v in outputs]
            row['paths'][name]={'complete_output_equal':len(set(outputs))==1,
                'semantic_output_equal':len(set(values))==1,
                'intermediate_buffer_equal':len(set(intermediate[name]))==1 if name in intermediate else None}
        row['serializer_preserves_each_input_record']=all(a==b for a,b in zip(path_outputs['serialization'],variants))
        # Negative visible-name control: distinguish a genuine default-name
        # predicate from an unconditional setter. Tail remains unchanged.
        custom=bytearray(record);custom[8]^=1
        u.mem_write(0x02001000,bytes(custom));setters=[]
        h=u.hook_add(UC_HOOK_CODE,evolution_hook)
        call(e,0x08042C5C,0x02001000,species,species)
        u.hook_del(h)
        row['changed_visible_prefix_is_not_default']=not setters
        row['custom_negative_record_untouched']=bytes(u.mem_read(0x02001000,100))==bytes(custom)
        if species in (29,32):
            comparison_results=[]
            for variant in variants:
                u.mem_write(0x02008100,variant[8:15]+bytes([255]))
                u.mem_write(0x02008200,bytes(64))
                results=[]
                def gender_hook(cpu,pc,size,data):
                    if pc==0x081220D0:
                        results.append(cpu.reg_read(r.UC_ARM_REG_R0));cpu.emu_stop()
                h=u.hook_add(UC_HOOK_CODE,gender_hook)
                u.reg_write(r.UC_ARM_REG_SP,0x03007000)
                u.reg_write(r.UC_ARM_REG_LR,0x06000001)
                for reg,value in zip((r.UC_ARM_REG_R0,r.UC_ARM_REG_R1,r.UC_ARM_REG_R2,r.UC_ARM_REG_R3),
                                     (0,species,0x02008100,0x02008200)):
                    u.reg_write(reg,value)
                u.emu_start(0x08122091,0x06000000,count=1000000)
                u.hook_del(h)
                if len(results)!=1:raise ValueError('native Nidoran default-name comparison boundary missing')
                comparison_results.extend(results)
            row['Party_Nidoran_default_name_native_results']=comparison_results
        row['E3_semantics_equal']=all({k:v for k,v in audit.reconstruct(x,rom).items() if k!='record_sha256'}==
            {k:v for k,v in audit.reconstruct(variants[0],rom).items() if k!='record_sha256'} for x in variants)
        rows.append(row)
    return {'rom_sha256':model.sha(rom),'save_sha256':model.sha(raw),
        'evidence_class':'exact-ROM isolated downstream execution, common synthetic UI/battle runtime',
        'species_cases':len(rows),'rows':rows,
        'canonical_representation_candidate':'exact seven-byte species table field, as intentionally written by native evolution rename',
        'nickname_closed':all(all(v['semantic_output_equal'] for v in row['paths'].values())
            and all(row['default_status']) and row['changed_visible_prefix_is_not_default']
            and row['custom_negative_record_untouched'] and row['serializer_preserves_each_input_record']
            and row['E3_semantics_equal'] and all(not x['read_after_terminator'] and x['result']==1
            for x in row['actual_Party_font_EOS_checks']) for row in rows),'writer_added':False,'human_gameplay':False,
        'limits':['bounded ordinary default-species names through traced summary, Party font, battle placeholder and evolution default-name paths; no rendered-pixel or whole-game attestation',
                  'serializer result covers Party RAM-to-SaveBlock1 component, not flash hardware execution',
                  'no arbitrary custom-name or link/trade/facility claim']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--save',type=Path,required=True)
    p.add_argument('--broad',action='store_true');args=p.parse_args()
    rp=profile._private_file(args.rom,'ROM',must_exist=True);sp=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rp.read_bytes(),sp.read_bytes();result=probe(raw,rom,broad=args.broad)
    if rp.read_bytes()!=rom or sp.read_bytes()!=raw:raise ValueError('source inputs changed')
    result['sources_immutable']=True
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
