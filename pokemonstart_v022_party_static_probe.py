"""Optional isolated exact-ROM execution for E3; never writes ROMs or saves.

Unicorn 2.1.4 may require host JIT permission. Only the ordinary non-facility
branch is exercised: external FlagGet(0x930) is intercepted as false. Every
other instruction, including GetMonData/SetMonData and stat arithmetic, runs
from the SHA-gated owned ROM. This is not gameplay/normal-SAVE acceptance.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct

import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as model
import pokemonstart_v022_party_audit as auditor


def probe(raw: bytes, rom: bytes) -> dict:
    tables = model.extract_tables(rom)
    parsed = auditor.structure.parse(raw)
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x08000000, 0x02000000), (0x02000000, 0x40000),
                          (0x03000000, 0x8000), (0x06000000, 0x1000)):
        cpu.mem_map(address, size)
    cpu.mem_write(0x08000000, rom)
    intercepted = set()

    def external(uc, address, size, data):
        if address == 0x06000000:
            uc.emu_stop()
        elif address == 0x0806DEC4:
            flag = uc.reg_read(UC_ARM_REG_R0)
            if flag != 0x930:
                raise ValueError('unexpected external FlagGet context')
            intercepted.add(flag)
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, external)

    def call(address, *args):
        cpu.reg_write(UC_ARM_REG_SP, 0x03007000)
        cpu.reg_write(UC_ARM_REG_LR, 0x06000001)
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
            cpu.reg_write(reg, value)
        cpu.emu_start(address | 1, 0x06000000, count=1000000)
        if cpu.reg_read(UC_ARM_REG_PC) != 0x06000000:
            raise ValueError('isolated instruction budget exceeded')
        return cpu.reg_read(UC_ARM_REG_R0)

    address = 0x02001000
    retained = []
    variants = 0
    for slot, source in enumerate(parsed['records']):
        mon = model.decode_record(source, slot, tables)
        if mon['capabilities']['cached_stats']['reasons']:
            retained.append({'slot': slot, 'status': 'NOT ESTABLISHED',
                             'reasons': mon['capabilities']['cached_stats']['reasons']})
            continue
        cpu.mem_write(address, source)
        level = call(0x0803DF30, address)
        ability = call(0x0804042C, address)
        call(0x0803DBE8, address)
        returned = bytes(cpu.mem_read(address, 100))
        if (level != mon['exp_derived_level'] or ability != mon['resolved_ability']
                or returned != source):
            raise ValueError('exact retained record reconstruction mismatch')
        retained.append({'slot': slot, 'species': mon['species'], 'status': 'PASS',
                         'exact_recalculation_record_unchanged': True,
                         'resolved_ability': ability, 'exp_level': level})
        # Cross levels, natures, IV/EV extremes, PP-Ups and hidden/selector state.
        for level_target in (3, 6, 20, 50, 100):
            for mint in (0, 1, 10, 16, 24, 25):
                for allocated in (False, True):
                    record = bytearray(source)
                    species = tables.species[mon['species']]
                    struct.pack_into('<I', record, 36, tables.experience[species.growth][level_target])
                    record[84] = level_target
                    record[15] = mint
                    record[56:62] = bytes((4, 252, 0, 0, 252, 0)) if allocated else bytes(6)
                    ivs = (31, 0, 15, 30, 1, 31) if allocated else (0,)*6
                    struct.pack_into('<I', record, 72, sum(iv << (i*5) for i, iv in enumerate(ivs)))
                    # Deliberately set full HP 1/1; exact HP increase rule must
                    # produce newly calculated full HP without disk output.
                    struct.pack_into('<2H', record, 86, 1, 1)
                    expected = auditor.reconstruct(bytes(record), rom)
                    cpu.mem_write(address, bytes(record))
                    call(0x0803DBE8, address)
                    actual = list(struct.unpack('<7H', bytes(cpu.mem_read(address+86, 14))))
                    if actual != [expected['ordinary_expected_stats'][0], *expected['ordinary_expected_stats']]:
                        raise ValueError('isolated composed stat/nature/EXP mismatch')
                    if cpu.mem_read(address+84, 1)[0] != level_target:
                        raise ValueError('isolated level mismatch')
                    variants += 1
        for hidden in (False, True):
            for selector in (0, 1):
                record = bytearray(source)
                record[71] = (record[71] & ~16) | (16 if hidden else 0)
                record[75] = (record[75] & ~128) | selector*128
                expected = auditor.reconstruct(bytes(record), rom)['resolved_ability']
                cpu.mem_write(address, bytes(record))
                if call(0x0804042C, address) != expected:
                    raise ValueError('isolated selector/hidden/fallback mismatch')
    pp_cases = 0
    for move in range(1, model.MOVE_COUNT):
        for slot in range(4):
            for ups in range(4):
                actual = call(0x0804070C, move, ups << (slot*2), slot)
                if actual != model.maximum_pp(move, ups, tables):
                    raise ValueError('isolated exact maximum-PP mismatch')
                pp_cases += 1
    return {'rom_sha256': model.sha(rom), 'save_sha256': model.sha(raw),
            'retained_records': retained, 'stat_variants_passed': variants,
            'move_pp_cases_passed': pp_cases, 'intercepted_false_flags': sorted(intercepted),
            'limits': ['ordinary non-facility branch only', 'in-memory parameter variants are not native records',
                       'no game load, normal SAVE, writer or creation authority']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--save', required=True, type=Path)
    args = parser.parse_args()
    rom_path = profile._private_file(args.rom, 'ROM', must_exist=True)
    save_path = profile._private_file(args.save, 'save', must_exist=True)
    rom, raw = rom_path.read_bytes(), save_path.read_bytes()
    report = probe(raw, rom)
    if model.sha(rom_path.read_bytes()) != model.sha(rom) or model.sha(save_path.read_bytes()) != model.sha(raw):
        raise ValueError('private input changed')
    report['sources_immutable'] = True
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
