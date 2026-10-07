"""E4-A read-only constructor investigation, never a save writer.

Executes the owned exact ROM in isolated RAM. Unrestored runtime globals are
explicit experimental controls, not native gameplay or a reconstructed runtime.
Reports hashes, semantic checks and address metadata; never identity bytes,
raw records, ROM tables/instructions or private paths.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as model
import pokemonstart_v022_party_audit as audit


class ConstructorExperiment:
    BLOCK1_ADDRESS = 0x02010000
    BLOCK2_ADDRESS = 0x02014000
    def __init__(self, raw: bytes, rom: bytes):
        self.tables = model.extract_tables(rom)
        self.parsed = audit.structure.parse(raw)
        self.sections = self.parsed['slots'][self.parsed['active']]['sections']
        self.block1 = b''.join(self.sections[sid][:audit.structure.LENGTHS[sid]] for sid in (1,2,3,4))
        self.parasite = (self.sections[0][0xF24:0xFF0] + self.sections[4][0xD98:0xFF0]
                         + self.sections[13][0x450:0xFF0]
                         + raw[30*4096:30*4096+0xFF0]
                         + raw[31*4096:31*4096+0xFF0])
        self.context = audit.inspect(raw, rom)['saved_context']
        if self.context['flag_0x930']:
            raise ValueError('saved facility state is unsupported')
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_READ
        from unicorn import arm_const as reg
        self.reg = reg
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in ((0x08000000, 0x2000000), (0x02000000, 0x40000),
                              (0x03000000, 0x8000), (0x06000000, 4096)):
            self.cpu.mem_map(address, size)
        self.cpu.mem_write(0x08000000, rom)
        self.rom = rom
        self.reads = set()
        self.flags = set()
        self.variables = set()
        self.cpu.hook_add(UC_HOOK_CODE, self._code)
        self.cpu.hook_add(UC_HOOK_MEM_READ, self._read)

    def _code(self, cpu, address, size, data):
        if address == 0x06000000:
            cpu.emu_stop()
        if address == 0x0806DEC4:
            self.flags.add(cpu.reg_read(self.reg.UC_ARM_REG_R0))
        if address == 0x0806DD5C:
            self.variables.add(cpu.reg_read(self.reg.UC_ARM_REG_R0))

    def _read(self, cpu, access, address, size, value, data):
        # Classify supplied save images, constructor target and ABI stack.
        supplied = ((0x02001000, 0x02001064),
                    (self.BLOCK2_ADDRESS, self.BLOCK2_ADDRESS+len(self.sections[0])),
                    (self.BLOCK1_ADDRESS, self.BLOCK1_ADDRESS+len(self.block1)),
                    (0x020241E4, 0x020241E4+600), (0x02023F89, 0x02023F8A),
                    (0x0203B0E8, 0x0203B0E8+len(self.parasite)),
                    (0x03006000, 0x03007100), (0x03005048, 0x03005050))
        if (0x02000000 <= address < 0x03008000
                and not any(start <= address and address+size <= end for start, end in supplied)):
            self.reads.add((cpu.reg_read(self.reg.UC_ARM_REG_PC), address, size))

    def construct(self, species, level, personality, fixed_iv, *, fill=0xA5,
                  seed=0, runtime_byte=0, ot_type=0, set_flags=(), stack_fill=0,
                  clear_flags=(), runtime_controls=()):
        """RAM-only result; personality/OT controls are research ABI, not UX."""
        if species not in model.ORDINARY_SPECIES or not 1 <= level <= 100:
            raise ValueError('investigation requires E3 ordinary species and level')
        if not 0 <= fixed_iv <= 31 or not 0 <= fill <= 255:
            raise ValueError('invalid experimental IV/fill')
        cpu, reg = self.cpu, self.reg
        cpu.mem_write(0x02000000, bytes(0x40000))
        cpu.mem_write(0x03000000, bytes(0x8000))
        cpu.mem_write(0x03006000, bytes([stack_fill])*0x1100)
        cpu.mem_write(self.BLOCK2_ADDRESS, self.sections[0])
        cpu.mem_write(0x0300504C, struct.pack('<I', self.BLOCK2_ADDRESS))
        cpu.mem_write(self.BLOCK1_ADDRESS, self.block1)
        cpu.mem_write(0x03005048, struct.pack('<I', self.BLOCK1_ADDRESS))
        cpu.mem_write(0x02023F89, bytes([self.parsed['count']]))
        cpu.mem_write(0x020241E4, self.sections[1][0x38:0x38+600])
        cpu.mem_write(0x0203B0E8, self.parasite)
        # Controlled unresolved RNG/runtime state, deliberately not claimed
        # to represent its values after a real game load.
        cpu.mem_write(0x03005040, struct.pack('<I', seed))
        cpu.mem_write(0x0203DFC0, bytes([runtime_byte]))
        target, stack = 0x02001000, 0x03007000
        # Exact E1-qualified initializer derives pocket pointers/capacities
        # from the restored image; no allocator/FlagGet interception.
        cpu.reg_write(reg.UC_ARM_REG_SP, stack)
        cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
        cpu.reg_write(reg.UC_ARM_REG_R0, 0)
        cpu.emu_start(0x090D39A5, 0x06000000, count=1000000)
        if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
            raise ValueError('native bag initializer instruction budget exceeded')
        allowed_controls = {0x03005040:4, 0x03005ED8:1, 0x020397E4:4,
                            0x0203DFC0:1, 0x0203DFD0:4, 0x03003569:1}
        for address, value in runtime_controls:
            width = allowed_controls.get(address)
            if width is None or not 0 <= value < 1 << (width*8):
                raise ValueError('unsupported runtime experimental control')
            cpu.mem_write(address, value.to_bytes(width, 'little'))
        for flag in clear_flags:
            cpu.reg_write(reg.UC_ARM_REG_SP, stack)
            cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
            cpu.reg_write(reg.UC_ARM_REG_R0, flag)
            cpu.emu_start(0x0806DE9D, 0x06000000, count=1000000)
            if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
                raise ValueError('FlagClear instruction budget exceeded')
        for flag in set_flags:
            cpu.reg_write(reg.UC_ARM_REG_SP, stack)
            cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
            cpu.reg_write(reg.UC_ARM_REG_R0, flag)
            cpu.emu_start(0x0806DE75, 0x06000000, count=1000000)
            if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
                raise ValueError('FlagSet instruction budget exceeded')
        cpu.mem_write(target, bytes([fill])*100)
        cpu.mem_write(stack, struct.pack('<4I', 1, personality, ot_type, 0))
        cpu.reg_write(reg.UC_ARM_REG_SP, stack)
        cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
        for name in ('R4','R5','R6','R7','R8','R9','R10','R11','R12'):
            cpu.reg_write(getattr(reg, 'UC_ARM_REG_'+name), 0)
        for register, value in zip((reg.UC_ARM_REG_R0, reg.UC_ARM_REG_R1,
                                    reg.UC_ARM_REG_R2, reg.UC_ARM_REG_R3),
                                   (target, species, level, fixed_iv)):
            cpu.reg_write(register, value)
        cpu.emu_start(0x0803D1C1, 0x06000000, count=1000000)
        if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
            raise ValueError('constructor instruction budget exceeded')
        return bytes(cpu.mem_read(target, 100))

    def native_shiny(self):
        """Query the last RAM-only result without returning identity material."""
        cpu, reg = self.cpu, self.reg
        cpu.reg_write(reg.UC_ARM_REG_SP, 0x03007000)
        cpu.reg_write(reg.UC_ARM_REG_LR, 0x06000001)
        cpu.reg_write(reg.UC_ARM_REG_R0, 0x02001000)
        cpu.emu_start(0x08043AB9, 0x06000000, count=1000000)
        if cpu.reg_read(reg.UC_ARM_REG_PC) != 0x06000000:
            raise ValueError('native shiny-query instruction budget exceeded')
        return bool(cpu.reg_read(reg.UC_ARM_REG_R0))


def probe(raw: bytes, rom: bytes, *, broad=False) -> dict:
    experiment = ConstructorExperiment(raw, rom)
    species_set = sorted(model.ORDINARY_SPECIES) if broad else [1,19,25,63,129,133,150,288]
    cases, disagreements, observations = 0, [], {}
    constant_disagreements=[]
    for species in species_set:
        for level in (1,3,20,100):
            for parity in (0,1):
                # Fixed synthetic identity, no captured record replay.
                personality = 0x12345678 + parity
                record = experiment.construct(species, level, personality, 0 if parity==0 else 31)
                alternate = experiment.construct(species, level, personality, 0 if parity==0 else 31, fill=0x5A)
                if record != alternate:
                    raise ValueError('constructor depends on old destination contents')
                rebuilt = audit.reconstruct(record, rom)
                zero_offsets=(15,16,27,28,29,30,31,34,35,40,43,*range(56,69),*range(76,84))
                unexpected=[i for i in zero_offsets if record[i]]
                if unexpected:
                    constant_disagreements.append({'species':species,'level':level,'offsets':unexpected})
                eligibility = audit.ordinary_reasons(record, rom, experiment.context)
                supplied_identity = int.from_bytes(record[:4], 'little') == personality
                if eligibility or rebuilt['species'] != species or rebuilt['stored_level'] != level:
                    disagreements.append({'species':species,'level':level,'reasons':eligibility,
                                          'species_equal':rebuilt['species']==species,
                                          'level_equal':rebuilt['stored_level']==level})
                owner = experiment.sections[0]
                if record[4:8] != owner[10:14] or record[20:27] != owner[:7]:
                    raise ValueError('owner identity source disagreement')
                key = str(species)
                observations.setdefault(key, {'growth':rebuilt['growth_rate'],
                    'ability2_present':bool(experiment.tables.species[species].abilities[1]),
                    'tera_matches_primary_type':record[17]==rom[model.SPECIES_TABLE+species*32+6],
                    'nickname_matches_ROM_prefix':record[8:15]==rom[model.SPECIES_NAMES+species*8:model.SPECIES_NAMES+species*8+7],
                    'language':record[18], 'ball':record[42], 'sanity':record[19],
                    'pokerus_timer':record[85], 'native_moves_by_level':{},
                    'identity_preserved_in_all_cases':True})
                observations[key]['native_moves_by_level'][str(level)] = [x['move_id'] for x in rebuilt['moves']]
                observations[key]['identity_preserved_in_all_cases'] &= supplied_identity
                cases += 1
    reference = experiment.construct(19,5,0x12345678,0)
    reference_shiny = experiment.native_shiny()
    runtime_variants = []
    for value in (1,2,255):
        changed = experiment.construct(19,5,0x12345678,0,runtime_byte=value,seed=1)
        runtime_variants.append({'controlled_byte':value,
                                'changed_record_offsets':[i for i,(a,b) in enumerate(zip(reference,changed)) if a!=b],
                                'personality_equal':changed[:4]==reference[:4]})
    flag_variants = []
    for flag in sorted(experiment.flags):
        changed = experiment.construct(19,5,0x12345678,0,set_flags=(flag,),seed=1)
        flag_variants.append({'flag':flag,
                              'changed_record_offsets':[i for i,(a,b) in enumerate(zip(reference,changed)) if a!=b],
                              'personality_equal':changed[:4]==reference[:4],
                              'native_shiny':experiment.native_shiny(),
                              'species_equal':changed[32:34]==reference[32:34]})
    stack_variants=[]
    for species in species_set:
        left=experiment.construct(species,5,0x12345678,0,stack_fill=0xA5)
        right=experiment.construct(species,5,0x12345678,0,stack_fill=0x5A)
        changed=[i for i,(a,b) in enumerate(zip(left,right)) if a!=b]
        if changed:
            stack_variants.append({'species':species,'changed_record_offsets':changed})
    return {'rom_sha256':model.sha(rom), 'save_sha256':model.sha(raw),
            'evidence_class':'exact-ROM isolated execution with partially reconstructed RAM',
            'constructor_entry':'0x0803D1C0', 'box_constructor_entry':'0x09075150',
            'baseline_cases':cases, 'destination_fill_comparisons':cases,
            'ordinary_disagreements':disagreements, 'species_observations':observations,
            'baseline_constant_disagreements':constant_disagreements,
            'runtime_variants':runtime_variants,
            'flag_variants':flag_variants,
            'reference_native_shiny':reference_shiny,
            'stack_fill_comparisons':len(species_set),'stack_dependent_records':stack_variants,
            'unreconstructed_reads':[{'pc':hex(pc),'address':hex(address),'size':size}
                                      for pc,address,size in sorted(experiment.reads)],
            'flag_queries':sorted(experiment.flags),'variable_queries':sorted(experiment.variables),
            'complete_independent_constructor_established':False,
            'writer_or_gui_creation_added':False,'human_gameplay':False,
            'limits':['runtime bag/key state and fishing state are not reconstructed',
                      'native default move algorithm not independently reconstructed',
                      'PID postprocessing and generated metadata not completely qualified',
                      'complete destination overwrite does not prove correct initialization']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--save',type=Path,required=True)
    parser.add_argument('--broad',action='store_true')
    args = parser.parse_args()
    rom_path=profile._private_file(args.rom,'ROM',must_exist=True)
    save_path=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rom_path.read_bytes(),save_path.read_bytes()
    result=probe(raw,rom,broad=args.broad)
    if rom_path.read_bytes()!=rom or save_path.read_bytes()!=raw:
        raise ValueError('private inputs changed during investigation')
    result['sources_immutable']=True
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
