"""Candidate reusable edits of present ordinary Party records; bounded stat model."""
from __future__ import annotations
from dataclasses import replace
import struct
import pokemonstart_save_verifier as v
import pokemonstart_fl2_core as profile
import pokemonstart_fastlab_v022_party_editor as existing
import pokemonstart_v022_product_stats as calculations
from pokemonstart_fastlab_v022_level import medium_slow_exp, level_from_medium_slow_exp

SPECIES = existing.SUPPORTED_SPECIES
MOVES = {1: 'Pound', 33: 'Tackle'}
STAT_FIELDS = existing.STAT_FIELDS


def integer(value, lower, upper, label):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f'{label} must be an integer in {lower}..{upper}')
    return value


def qualify(raw, rom_sha256, slot):
    profile._require_rom_hash(rom_sha256)
    result = v.verify_bytes(raw)
    integer(slot, 0, result.party_count-1, 'occupied Party slot')
    mon = result.party[slot]
    if (mon.species == 0 or mon.sanity != 2 or mon.backup_species != 0
            or raw[result.slots[result.active_slot].section(1).physical_sector * 4096
                   + v.PARTY_OFFSET + slot*100 + 75] & 0x40
            or not 1 <= mon.level <= 100 or not 0 <= mon.hp <= mon.max_hp):
        raise ValueError('Party requires an ordinary non-egg record with valid HP/level')
    return result, mon


def stat_eligible(mon):
    # Retain the established exact-v0.22 calculator instead of extrapolating.
    expected = calculations.stats(mon)
    actual = (mon.hp,mon.max_hp,mon.attack,mon.defense,mon.speed,mon.sp_attack,mon.sp_defense)
    if actual != expected or mon.ability_num != 0 or mon.held_item != 0:
        raise ValueError('cached stats / ability / held item outside the qualified model')
    if level_from_medium_slow_exp(mon.experience) != mon.level:
        raise ValueError('EXP and level are inconsistent')


def capabilities(raw, rom_sha256, slot):
    _,mon=qualify(raw,rom_sha256,slot)
    result={'friendship':True,'moves':mon.pp_bonuses == 0 and mon.moves[0] in MOVES
            and mon.pp[0] <= 35, 'stats':False, 'stats_reason':''}
    try:
        stat_eligible(mon)
        result['stats']=True
    except ValueError as exc:
        result['stats_reason']=str(exc)
    return result


def derive(raw, rom_sha256, slot, changes):
    before,mon=qualify(raw,rom_sha256,slot)
    if not isinstance(changes,dict) or not changes or set(changes)-existing.WRITABLE_FIELDS:
        raise ValueError('unsupported or empty Party changes')
    requested=dict(changes)
    if 'friendship' in requested:
        integer(requested['friendship'],0,255,'friendship')
    for field, maximum in (('ivs',31),('evs',252)):
        if field in requested:
            values=requested[field]
            if not isinstance(values,(list,tuple)) or len(values)!=6:
                raise ValueError(f'{field} requires six values')
            requested[field]=tuple(integer(x,0,maximum,field) for x in values)
    if sum(requested.get('evs',mon.evs)) > 510:
        raise ValueError('EV total exceeds 510')
    if 'species' in requested and (type(requested['species']) is not int or requested['species'] not in SPECIES):
        raise ValueError('species supports Bulbasaur/Ivysaur only')
    if 'level' in requested:
        integer(requested['level'],5,6,'supported level')
    if 'experience' in requested:
        integer(requested['experience'],medium_slow_exp(5),medium_slow_exp(7)-1,'supported EXP')
    if ('level' in requested and 'experience' in requested
            and level_from_medium_slow_exp(requested['experience']) != requested['level']):
        raise ValueError('level/EXP conflict')
    section=before.slots[before.active_slot].section(1)
    base=section.physical_sector*4096
    record_base=base+v.PARTY_OFFSET+slot*100
    record=bytearray(raw[record_base:record_base+100])
    desired=mon
    if set(requested) & STAT_FIELDS:
        stat_eligible(mon)
        level=requested.get('level',mon.level)
        exp=requested.get('experience',medium_slow_exp(level) if 'level' in requested else mon.experience)
        level=level_from_medium_slow_exp(exp)
        desired=replace(mon,species=requested.get('species',mon.species),level=level,experience=exp,
                        ivs=requested.get('ivs',mon.ivs),evs=requested.get('evs',mon.evs))
        stats=calculations.stats(desired)
        desired=replace(desired,hp=stats[0],max_hp=stats[1],attack=stats[2],defense=stats[3],
                        speed=stats[4],sp_attack=stats[5],sp_defense=stats[6])
        struct.pack_into('<H',record,32,desired.species)
        struct.pack_into('<I',record,36,desired.experience)
        record[84]=desired.level
        word=struct.unpack_from('<I',record,72)[0] & 0xC0000000
        word |= sum(iv << (i*5) for i,iv in enumerate(desired.ivs))
        struct.pack_into('<I',record,72,word)
        record[56:62]=bytes(desired.evs)
        struct.pack_into('<7H',record,86,*stats)
    if 'friendship' in requested:
        record[41]=requested['friendship']
        desired=replace(desired,friendship=requested['friendship'])
    if 'moves' in requested:
        moves=requested['moves']
        if (not isinstance(moves,dict) or set(moves)!={0}
                or type(moves[0]) is not int or moves[0] not in MOVES
                or mon.moves[0] not in MOVES or mon.pp_bonuses != 0 or mon.pp[0]>35):
            raise ValueError('only slot1 Pound/Tackle with zero PP-Ups is supported')
        struct.pack_into('<H',record,44,moves[0])
        record[52]=35 # Replacement restores base PP; all other move/PP bytes preserved.
        desired=replace(desired,moves=(moves[0],*desired.moves[1:]),pp=(35,*desired.pp[1:]))
    output=bytearray(raw)
    output[record_base:record_base+100]=record
    struct.pack_into('<H',output,base+v.SECTION_CHECKSUM_OFFSET,
                     v.calculate_save_checksum(output[base:base+v.SECTION_LENGTHS[1]]))
    candidate=bytes(output)
    after=v.verify_bytes(candidate)
    if after.party[slot] != desired:
        raise ValueError('Party semantic postcondition mismatch')
    allowed={base+0xFF6,base+0xFF7}
    for field, offsets in (('friendship',[41]),('moves',[44,45,52])):
        if field in requested:allowed.update(record_base+x for x in offsets)
    if set(requested)&STAT_FIELDS:
        allowed.update(record_base+x for x in [32,33,36,37,38,39,84,*range(56,62),*range(72,76),*range(86,100)])
    diffs=[i for i,(a,b) in enumerate(zip(raw,candidate)) if a!=b]
    if not diffs:raise ValueError('Party unchanged; no output')
    if not set(diffs)<=allowed:raise ValueError('Party byte envelope mismatch')
    return candidate,{'slot':slot,'before':existing._semantic(mon),'after':existing._semantic(after.party[slot]),
                      'changed_offsets':diffs,'verifier_accepted':True}
