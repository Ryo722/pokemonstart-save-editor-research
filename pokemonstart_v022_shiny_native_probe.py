"""Read-only native qualification of PID-only shiny transitions, sanitized booleans.

Isolated exact-ROM function execution (Unicorn JIT; requires host execution),
not Human gameplay, game-load or flash SAVE evidence. Nothing is written.
"""
import argparse
import json
from pathlib import Path
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as model
import pokemonstart_v022_product_party as party
from pokemonstart_v022_creation_probe import ConstructorExperiment
from pokemonstart_v022_creation_initialization_probe import call

MON = 0x02001000
IS_SHINY_OTID_PERSONALITY = 0x08043AE4
IS_MON_SHINY = 0x08043AB8
NATURE_FROM_PERSONALITY = 0x080425A4
GET_MON_GENDER = 0x0803EE8C
GET_MON_ABILITY = 0x0804042C


def native_record(e, record):
    e.cpu.mem_write(MON, bytes(record))
    return {'shiny': bool(call(e, IS_MON_SHINY, MON)),
            'nature': call(e, NATURE_FROM_PERSONALITY, int.from_bytes(record[:4], 'little')),
            'gender': call(e, GET_MON_GENDER, MON), 'ability': call(e, GET_MON_ABILITY, MON)}


def probe(raw, rom):
    e = ConstructorExperiment(raw, rom)
    tables = model.extract_tables(rom)
    threshold = []
    for tid in (0, 0x1234ABCD, 0xFFFF0001):
        for score in range(16):
            pid = ((((tid >> 16) ^ (tid & 0xFFFF) ^ score ^ 0x5A5A) & 0xFFFF) << 16) | 0x5A5A
            native = bool(call(e, IS_SHINY_OTID_PERSONALITY, tid, pid))
            if native != (model.shiny_score(tid, pid) < 8):
                raise ValueError('native shiny threshold disagreement')
            threshold.append(native)
    verified = model.verifier.verify_bytes(raw)
    context = model.saved_context(verified)
    base = verified.slots[verified.active_slot].section(1).physical_sector*4096 + model.verifier.PARTY_OFFSET
    transitions = 0
    for slot in range(verified.party_count):
        record = raw[base+slot*100:base+(slot+1)*100]
        if not model.write_eligibility(record, tables, context)['eligible']:
            continue
        before = native_record(e, record)
        personality, ot_id = struct.unpack_from('<II', record, 0)
        if before['shiny'] != (model.shiny_score(ot_id, personality) < 8):
            raise ValueError('native stored shiny state disagreement')
        target = party.transform_ordinary(record, tables, context, {'shiny': not before['shiny']}, slot=slot)
        restored = party.transform_ordinary(target, tables, context, {'shiny': before['shiny']}, slot=slot)
        for changed, expected_shiny in ((target, not before['shiny']), (restored, before['shiny'])):
            after = native_record(e, changed)
            if after != {**before, 'shiny': expected_shiny} or changed[4:] != record[4:]:
                raise ValueError('native PID-only shiny postcondition failed')
            transitions += 1
    if not transitions:
        raise ValueError('no eligible ordinary Party record to qualify')
    return {'status': 'NATIVE_SHINY_PID_ONLY_QUALIFIED_NOT_GAME_ACCEPTED',
            'threshold_cases': len(threshold), 'threshold_shiny_cases': sum(threshold),
            'record_transitions': transitions,
            'invariants': ['IsMonShiny', 'nature', 'GetMonGender', 'GetMonAbility', 'bytes 4..99 unchanged'],
            'human_gameplay': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--save', type=Path, required=True)
    args = parser.parse_args()
    rom = profile._private_file(args.rom, 'ROM', must_exist=True).read_bytes()
    raw = profile._private_file(args.save, 'save', must_exist=True).read_bytes()
    print(json.dumps(probe(raw, rom), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
