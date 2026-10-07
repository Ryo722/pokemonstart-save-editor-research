"""Optional isolated exact-Thumb corroboration; no emulator/game/save mutation.

Requires Unicorn 2.1.4 locally. A host JIT restriction may prevent execution;
that is a probe limitation, never a successful qualification result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

import pokemonstart_v022_inventory_model as model
import pokemonstart_v022_inventory_audit as auditor
import pokemonstart_fl2_core as profile


def probe(rom: bytes) -> dict:
    model.extract_catalog(rom)
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(0x08000000, 0x02000000)
    cpu.mem_write(0x08000000, rom)
    cpu.mem_map(0x02000000, 0x40000)
    cpu.mem_map(0x03000000, 0x8000)
    cpu.mem_map(0x06000000, 0x1000)
    state = {'allocate': True}

    def external(uc, address, size, _):
        if address == 0x06000000:
            uc.emu_stop()
            return
        if address not in (0x08002B9C, 0x0806DEC4, 0x08002BC4, 0x08FE0606):
            return
        if address == 0x08002B9C:
            uc.reg_write(UC_ARM_REG_R0, 0x02010000 if state['allocate'] else 0)
        elif address == 0x0806DEC4:
            if uc.reg_read(UC_ARM_REG_R0) != 0x12EB:
                raise ValueError('unexpected isolated flag input')
            uc.reg_write(UC_ARM_REG_R0, 0)
        elif address == 0x08FE0606:
            dst, src, length = (uc.reg_read(x) for x in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            if not (0x02000000 <= dst < 0x02040000 and 0x02000000 <= src < 0x02040000
                    and 0 <= length <= 2800):
                raise ValueError('unexpected isolated memcpy envelope')
            uc.mem_write(dst, bytes(uc.mem_read(src, length)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, external)

    def call(address, first, second=0):
        cpu.reg_write(UC_ARM_REG_SP, 0x03007000)
        cpu.reg_write(UC_ARM_REG_LR, 0x06000001)
        cpu.reg_write(UC_ARM_REG_R0, first)
        cpu.reg_write(UC_ARM_REG_R1, second)
        cpu.emu_start(address | 1, 0x06000000, count=1000000)
        if cpu.reg_read(UC_ARM_REG_PC) != 0x06000000:
            raise ValueError('isolated instruction budget exceeded')
        return cpu.reg_read(UC_ARM_REG_R0)

    for item in range(839):
        actual = call(0x090B81F0, item)
        if actual != model.classification(item) or actual != int(item in auditor.NON_NEUTRAL_IDS):
            raise ValueError('isolated classifier disagreement')
    partition_cases = []
    for occupied in (0, 1, 3, 324, 325, 326, 699, 700):
        rows = [(533 if i % 3 else 13, 1 + i % 999) for i in range(occupied)]
        image = b''.join(struct.pack('<HH', *row) for row in rows) + bytes((700 - occupied) * 4)
        for allocation in (True, False):
            state['allocate'] = allocation
            cpu.mem_write(0x0203BA98, image)
            if call(0x090B8274, 0x0203BA98, 700) != occupied or bytes(cpu.mem_read(0x0203BA98, 2800)) != image:
                raise ValueError('isolated partition/count/order failed')
            partition_cases.append({'occupied': occupied, 'allocation_success': allocation,
                                    'count_and_complete_order_equal': True})
    cpu.mem_write(0x0300504C, struct.pack('<I', 0x02000000))
    quantity_cases = []
    for item in range(13, 23):
        for quantity in (1, 3, 99, 999):
            cpu.mem_write(0x0203BA98, bytes(2800))
            call(0x090D39A4, 0)
            if call(0x08099A8C, item, quantity) != 1 or call(0x080997A8, 0x0203BA9A) != quantity:
                raise ValueError('isolated medicine add/read failed')
            if call(0x08099A8C, item, 1000 - quantity) != 0:
                raise ValueError('isolated 1000 existing-stack rejection failed')
            if bytes(cpu.mem_read(0x0203BA98, 4)) != struct.pack('<HH', item, quantity):
                raise ValueError('isolated rejected add changed record')
            if call(0x08099BE0, item, quantity) != 1 or bytes(cpu.mem_read(0x0203BA98, 4)) != bytes(4):
                raise ValueError('isolated medicine removal failed')
            quantity_cases.append({'item_id': item, 'quantity': quantity, 'add_read_remove_and_1000_rejection': True})
    return {'rom_sha256': model.sha(rom), 'both_classifier_predicates_match_all_839_ids': True,
            'partition_cases': partition_cases, 'medicine_quantity_cases': quantity_cases,
            'limit': 'Isolated Thumb execution with allocator/FlagGet/memcpy/free intercepted; no gameplay proof.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    args = parser.parse_args()
    try:
        path = profile._private_file(args.rom, 'ROM', must_exist=True)
        rom = path.read_bytes()
        report = probe(rom)
        if path.read_bytes() != rom:
            raise ValueError('private ROM changed during probe')
    except (OSError, ValueError, ImportError):
        print('REJECTED: isolated exact probe unavailable or failed')
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
