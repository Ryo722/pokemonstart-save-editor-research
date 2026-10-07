"""Read-only exact-ROM E4-A discriminators. No baseline/save constructor.

Tail fills are adversarial controls, never proposed creator representations.
Native copies and string consumers are measured separately. Reports contain
only hashes, bounded semantics and address/offset metadata.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_audit as audit
import pokemonstart_v022_party_model as model
from pokemonstart_v022_creation_probe import ConstructorExperiment

FLAG_STORAGE = {0x828: (1, 0xFE5, 1), 0x913: (0, 0xF26, 8),
                0x930: (0, 0xF2A, 1), 0x12F8: (4, 0xE0B, 1)}


def call(experiment, entry, *args):
    cpu, reg = experiment.cpu, experiment.reg
    cpu.reg_write(reg.UC_ARM_REG_SP, 0x03007000)
    cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
    for name in ('R4','R5','R6','R7','R8','R9','R10','R11','R12'):
        cpu.reg_write(getattr(reg, 'UC_ARM_REG_'+name), 0)
    for register, value in zip((reg.UC_ARM_REG_R0, reg.UC_ARM_REG_R1,
                               reg.UC_ARM_REG_R2, reg.UC_ARM_REG_R3), args):
        cpu.reg_write(register, value)
    cpu.emu_start(entry | 1, 0x06000000, count=1000000)
    if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
        raise ValueError('native discriminator instruction budget exceeded')
    return cpu.reg_read(reg.UC_ARM_REG_R0)


def rom_region(rom, group, number):
    """Independent lookup for measured map keys, NOT general map eligibility.

    Pointer validation is not proof that arbitrary indices are map entries.
    This probe accepts only owner-save inputs and compares native execution.
    """
    def pointer(offset):
        if not 0 <= offset <= len(rom)-4:
            raise ValueError('map pointer read outside ROM')
        value = struct.unpack_from('<I', rom, offset)[0] - 0x08000000
        if not 0 <= value < len(rom):
            raise ValueError('map pointer outside exact ROM')
        return value
    group_table = pointer(0x9A3D6C + group*4)
    header = pointer(group_table + number*4)
    if header+20 >= len(rom):
        raise ValueError('map header outside ROM')
    return rom[header+20]


def probe(raw, rom):
    e = ConstructorExperiment(raw, rom)
    rows = []
    for species in (1,19,25,63,129,133,150,288):
        record = e.construct(species, 5, 0x12345678, 0)
        terminator = record[8:15].index(255)
        variants = []
        for fill in (0,255,0xA5,0x5A):
            changed = bytearray(record)
            changed[9+terminator:15] = bytes([fill])*(6-terminator)
            variants.append(bytes(changed))
        results = []
        for name, entry, args in (
            ('GetBoxMonData',0x0803F4B0,(0x02001000,2,0x02008000)),
            ('GetMonData',0x0803F354,(0x02001000,2,0x02008000)),
            ('GetMonNickname',0x08120AD0,(0x02001000,0x02008000))):
            outputs = []
            for variant in variants:
                e.cpu.mem_write(0x02001000, variant)
                e.cpu.mem_write(0x02008000, bytes([0xCC])*40)
                call(e, entry, *args)
                outputs.append(bytes(e.cpu.mem_read(0x02008000,40)))
            prefixes = [v[:v.index(255)+1] for v in outputs]
            results.append({'consumer':name,
                'prefix_and_terminator_equal':len(set(prefixes))==1,
                'complete_copy_equal':len(set(outputs))==1,
                'changed_copy_offsets':sorted({i for v in outputs
                    for i,(a,b) in enumerate(zip(outputs[0],v)) if a!=b})})
        string_rows = []
        for variant in variants:
            e.cpu.mem_write(0x02008000, variant[8:15]+bytes([255]))
            e.cpu.mem_write(0x02008100, variants[0][8:15]+bytes([255]))
            string_rows.append((call(e,0x08008984,0x02008000),
                                call(e,0x080089A4,0x02008000,0x02008100)))
        semantics = []
        for variant in variants:
            decoded = audit.reconstruct(variant,rom)
            decoded.pop('record_sha256')
            semantics.append(decoded)
        rows.append({'species':species,'name_length':terminator,
            'tail_variants':len(variants),'consumers':results,
            'native_string_length_and_compare_equal':len(set(string_rows))==1,
            'E3_semantics_equal':all(v==semantics[0] for v in semantics),
            'E3_eligibility_equal':all(audit.ordinary_reasons(v,rom,e.context)==
                audit.ordinary_reasons(variants[0],rom,e.context) for v in variants)})
    flags = []
    for flag,(sid,offset,mask) in FLAG_STORAGE.items():
        e.construct(19,5,0x12345678,0)
        saved = bool(e.sections[sid][offset]&mask)
        native = bool(call(e,0x0806DEC4,flag))
        call(e,0x0806DE9C,flag)
        before = bytes(e.cpu.mem_read(0x02000000,0x40000))
        call(e,0x0806DE74,flag)
        after = bytes(e.cpu.mem_read(0x02000000,0x40000))
        changes = [{'RAM':hex(0x02000000+i),'mask':a^b}
                   for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        flags.append({'flag':hex(flag),'section':sid,'offset':hex(offset),'mask':mask,
                      'saved_value':saved,'native_value':native,'saved_matches_native':saved==native,
                      'native_clear_set_changed_bits':changes})
    ordinary = e.construct(19,5,0x12345678,0)
    shiny_before = e.native_shiny()
    forced = e.construct(19,5,0x12345678,0,set_flags=(0x913,))
    shiny_after = e.native_shiny()
    e.construct(19,5,0x12345678,0)
    group,number = e.block1[4:6]
    region = call(e,0x08055B20)
    independent = rom_region(rom,group,number)
    origin_rows = []
    saved_owner = e.sections[0]
    for gender in (0,1):
        owner = bytearray(saved_owner)
        owner[8] = gender
        e.sections[0] = bytes(owner)
        for level in (1,3,20,100):
            record = e.construct(19,level,0x12345678,0,clear_flags=(0x913,))
            packed = int.from_bytes(record[70:72],'little')
            origin_rows.append({'requested_level':level,'synthetic_owner_gender':gender,
                'met_location':record[69],'met_level':packed&127,
                'met_game':(packed>>7)&15,'origin_bits_11_to_14':(packed>>11)&15,
                'OT_gender_bit':packed>>15})
    e.sections[0] = saved_owner
    runtime_rows = []
    baseline = e.construct(19,5,0x12345678,0,clear_flags=(0x913,))
    for address,width in ((0x03005040,4),(0x03005ED8,1),(0x020397E4,4),
                          (0x0203DFC0,1),(0x0203DFD0,4),(0x03003569,1)):
        for value in (1,2,(1 << (width*8))-1):
            row = {'address':hex(address),'controlled_value':value}
            try:
                variant = e.construct(19,5,0x12345678,0,clear_flags=(0x913,),
                                      runtime_controls=((address,value),))
                row['changed_record_offsets']=[i for i,(a,b) in enumerate(zip(baseline,variant)) if a!=b]
                row['native_shiny']=e.native_shiny()
            except Exception as exc:
                row['execution_failure_class']=type(exc).__name__
            runtime_rows.append(row)
    return {'rom_sha256':model.sha(rom),'save_sha256':model.sha(raw),
        'evidence_class':'exact-ROM isolated execution with partially reconstructed RAM',
        'disjoint_save_images_and_native_party_restored':True,
        'runtime_adversarial_cases_under_cleared_913':runtime_rows,
        'nickname':rows,'flags_ordinary_runtime_route':flags,
        'flag_913_effect':{'personality_changed':ordinary[:4]!=forced[:4],
                           'native_shiny_before':shiny_before,'native_shiny_after':shiny_after},
        'origin':{'saved_map_group':group,'saved_map_number':number,'native_region':region,
                  'independent_region':independent,'match':region==independent,
                  'special_region_fallback':independent==255},
        'origin_level_gender_synthetic_controls':origin_rows,
        'complete_independent_constructor_established':False,
        'writer_or_GUI_added':False,'human_gameplay':False,
        'limits':['getter copies transport post-terminator bytes; downstream material consumers unresolved',
                  'flag routing runtime byte is controlled zero, not game-load reconstruction',
                  'native bag/runtime initialization and personality generator not qualified',
                  'map table index bounds and special-region fallback remain unresolved']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--save',type=Path,required=True)
    args=parser.parse_args()
    rp=profile._private_file(args.rom,'ROM',must_exist=True)
    sp=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rp.read_bytes(),sp.read_bytes()
    report=probe(raw,rom)
    if rp.read_bytes()!=rom or sp.read_bytes()!=raw:
        raise ValueError('private inputs changed')
    report['sources_immutable']=True
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
