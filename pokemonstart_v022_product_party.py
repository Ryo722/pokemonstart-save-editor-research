"""Candidate reusable edits of present ordinary Party records; bounded stat model."""
from __future__ import annotations
from dataclasses import replace
import hashlib
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
            and mon.pp[0] <= 35, 'stats':False, 'stats_reason':'', 'level_exp':False,
            'level_exp_reason':'Level 6 stat formula is unqualified for this exact build.'}
    try:
        stat_eligible(mon)
        result['stats']=True
        result['level_exp']=True
        result['level_exp_reason']='Level changes are disabled; EXP is limited to the supported level-5 range.'
    except ValueError as exc:
        result['stats_reason']=str(exc)
    return result


def derive(raw, rom_sha256, slot, changes, *, rom_bytes=None):
    if rom_bytes is not None:
        profile._require_rom_hash(rom_sha256)
        return derive_ordinary(raw, rom_bytes, slot, changes)
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
        integer(requested['level'],5,5,'supported level')
    if 'experience' in requested:
        integer(requested['experience'],medium_slow_exp(5),medium_slow_exp(6)-1,'supported level-5 EXP')
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
        if level != 5:
            raise ValueError('stat-changing requests must remain at level 5; level-6 stat formula is unqualified')
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


def ordinary_inspect(raw, rom, slot):
    import pokemonstart_v022_party_model as model
    import pokemonstart_v022_party_audit as audit
    tables = model.extract_tables(rom)
    verified = v.verify_bytes(raw)
    integer(slot, 0, verified.party_count-1, 'occupied Party slot')
    base = verified.slots[verified.active_slot].section(1).physical_sector*4096
    record = raw[base+v.PARTY_OFFSET+slot*100:base+v.PARTY_OFFSET+(slot+1)*100]
    eligibility = model.write_eligibility(record, tables, model.saved_context(verified))
    independent = audit.inspect(raw, rom)
    if independent['saved_context'] != model.saved_context(verified):
        raise ValueError('independent saved context disagreement')
    independent_reasons = audit.ordinary_reasons(record, rom, independent['saved_context'])
    if independent_reasons:
        eligibility['eligible'] = False
        eligibility['reasons'] += ['independent eligibility: '+x for x in independent_reasons]
    decoded = model.decode_record(record, slot, tables)
    return verified, base, record, tables, decoded, eligibility


def ordinary_options(tables):
    import pokemonstart_v022_party_model as model
    names = [move.name for move in tables.moves[1:] if move.name and move.base_pp]
    duplicates = {name for name in names if names.count(name)>1}
    return {'abilities': {i: list(tables.species[i].abilities) for i in sorted(model.ORDINARY_SPECIES) if i<len(tables.species)},
            'species': {i: tables.species[i].name for i in sorted(model.ORDINARY_SPECIES)
                        if i < len(tables.species) and tables.species[i].name and all(tables.species[i].bases)},
            'moves': {0: 'Empty', **{m.move_id: (f'{m.name} (#{m.move_id})' if m.name in duplicates else m.name) for m in tables.moves[1:]
                                    if m.name and m.base_pp}},
            'held_item': {0: 'None', **{i: tables.items[i].name for i in model.HELD_TARGET_METADATA
                                       if model.held_eligibility(i, tables)['safe_new_target']}}}


def shiny_personality(personality, ot_id, ratio, shiny):
    """Deterministic PID-only shiny transition keeping OT/TID, nature and gender.

    Ability selector/hidden bits, IVs and tera type are stored separately and
    are untouched. Only ordinary species without PID-derived forms reach here.
    """
    import pokemonstart_v022_party_model as model
    trainer = (ot_id >> 16) ^ (ot_id & 0xFFFF)
    for attempt in range(4096):
        digest = hashlib.sha256(b'E6 PID-only shiny transition v1\0' + struct.pack(
            '<IIBH', personality, ot_id, int(shiny), attempt)).digest()
        low = int.from_bytes(digest[:2], 'little')
        high = trainer ^ low ^ (digest[2] & 7) if shiny else int.from_bytes(digest[2:4], 'little')
        value = high << 16 | low
        if ((model.shiny_score(ot_id, value) < 8) == shiny and value != personality
                and value % 25 == personality % 25
                and model.native_gender(ratio, value) == model.native_gender(ratio, personality)):
            return value
    raise ValueError('bounded shiny personality search exhausted')


def transform_ordinary(source, tables, context, changes, *, slot=0):
    """Adopted E3 record transformations, shared with the qualified E4 baseline."""
    import pokemonstart_v022_party_model as model
    if len(source) != 100:
        raise ValueError('ordinary record length')
    mon = model.decode_record(source, slot, tables)
    eligibility = model.write_eligibility(source, tables, context)
    if not eligibility['eligible']:
        raise ValueError('ordinary Party rejected: ' + '; '.join(eligibility['reasons']))
    fields = {'species', 'level', 'experience', 'moves', 'pp', 'pp_up', 'friendship',
              'ivs', 'evs', 'effective_nature', 'ability', 'held_item', 'shiny'}
    if not isinstance(changes, dict) or not changes or set(changes)-fields:
        raise ValueError('unsupported or empty ordinary Party changes')
    options = ordinary_options(tables)
    record = bytearray(source)
    if 'species' in changes:
        sid = integer(changes['species'], 1, len(tables.species)-1, 'species')
        if sid not in options['species']:
            raise ValueError('species outside ordinary target subset')
        struct.pack_into('<H', record, 32, sid)
    species = tables.species[int.from_bytes(record[32:34], 'little')]
    level = integer(changes.get('level', mon['stored_level']), 1, 100, 'level')
    exp = changes.get('experience', mon['experience'])
    if 'experience' not in changes and (level != mon['stored_level'] or species.growth != mon['growth_rate']):
        exp = tables.experience[species.growth][level]
    integer(exp, 1, tables.experience[species.growth][100], 'EXP')
    derived = model.level_from_exp(exp, species.growth, tables)
    if derived is None or 'level' in changes and level != derived:
        raise ValueError('level/EXP conflict or unsupported EXP')
    if set(changes) & {'species', 'level', 'experience'}:
        struct.pack_into('<I', record, 36, exp)
        record[84] = derived
    for field, offset, limit in (('ivs',72,31), ('evs',56,252)):
        if field not in changes:
            continue
        values = changes[field]
        if not isinstance(values, (list, tuple)) or len(values) != 6:
            raise ValueError(field + ' requires six integers')
        values = tuple(integer(x, 0, limit, field) for x in values)
        if field == 'evs':
            if sum(values) > 510:
                raise ValueError('EV total exceeds 510')
            record[offset:offset+6] = bytes(values)
        else:
            word = int.from_bytes(record[72:76], 'little') & 0xC0000000
            struct.pack_into('<I', record, offset, word | sum(x << (5*j) for j,x in enumerate(values)))
    if 'effective_nature' in changes:
        nature = integer(changes['effective_nature'], 0, 24, 'effective nature')
        if nature != mon['effective_nature']:
            record[15] = 0 if nature == mon['native_nature'] else nature+1
    if 'friendship' in changes:
        record[41] = integer(changes['friendship'], 0, 255, 'friendship')
    if 'held_item' in changes:
        item = integer(changes['held_item'], 0, 838, 'held item')
        if not model.held_eligibility(item, tables)['safe_new_target']:
            raise ValueError('held item is not a qualified new target')
        struct.pack_into('<H', record, 34, item)
    if 'ability' in changes:
        target = integer(changes['ability'], 1, 65535, 'resolved ability')
        candidates = []
        for hidden in (False, True):
            for selector in (0, 1):
                first, second, third = species.abilities
                resolved = third if hidden and third else second if selector and second else first
                if resolved == target:
                    distance = int(hidden != mon['hidden_ability']) + int(selector != mon['ability_selector'])
                    candidates.append((distance, selector, hidden))
        if not candidates:
            raise ValueError('ability unavailable for target species')
        _, selector, hidden = min(candidates)
        record[71] = (record[71] & ~16) | (16 if hidden else 0)
        record[75] = (record[75] & ~128) | (128 if selector else 0)
    if 'shiny' in changes:
        if type(changes['shiny']) is not bool:
            raise ValueError('shiny requires true or false')
        if 'species' in changes:
            raise ValueError('combine shiny with species change in separate edits')
        personality, ot_id = struct.unpack_from('<II', record, 0)
        if (model.shiny_score(ot_id, personality) < 8) != changes['shiny']:
            ratio = tables.species[int.from_bytes(record[32:34], 'little')].gender_ratio
            struct.pack_into('<I', record, 0, shiny_personality(personality, ot_id, ratio, changes['shiny']))
        elif len(changes) == 1:
            raise ValueError('Pokémon already has the requested shiny state')
    # Slot-local operations: untouched slots preserve every byte, even empty
    # slots with stale PP/bonuses. No cosmetically canonical global rewrite.
    updates = {}
    for field in ('moves', 'pp', 'pp_up'):
        if field not in changes:
            continue
        values = changes[field]
        if not isinstance(values, dict) or not values:
            raise ValueError(field + ' requires a nonempty slot map')
        for index, value in values.items():
            integer(index, 0, 3, 'move slot')
            updates.setdefault(index, {})[field] = value
    for index, update in updates.items():
        original = mon['moves'][index]
        mid = integer(update.get('moves', original['move_id']), 0, 997, 'move ID')
        if mid not in options['moves']:
            raise ValueError('move target metadata unresolved')
        ups = integer(update.get('pp_up', original['pp_up_count']), 0, 3, 'PP-Up count')
        if mid == 0:
            if 'pp' in update or 'pp_up' in update:
                raise ValueError('empty-slot PP/PP-Up editing unsupported; retained bytes are preserved')
            # Exact SetMonMoveSlot(ID0) reads the ID0 base-PP table entry (35)
            # and preserves packed bonuses. This is deliberately not PP=0.
            pp = tables.moves[0].base_pp if mid != original['move_id'] else original['pp']
        else:
            maximum = model.maximum_pp(mid, ups, tables)
            reset = mid != original['move_id'] or ups != original['pp_up_count']
            pp = integer(update.get('pp', maximum if reset else original['pp']), 0, maximum, 'PP')
        struct.pack_into('<H', record, 44+2*index, mid)
        record[52+index] = pp
        mask = 3 << (2*index)
        record[40] = (record[40] & ~mask) | (ups << (2*index))
    if set(changes) & {'species', 'level', 'experience', 'ivs', 'evs', 'effective_nature'}:
        new_mon = model.decode_record(bytes(record), slot, tables)
        stats = new_mon['ordinary_expected_stats']
        current, old_max = mon['cached_hp_stats'][:2]
        if stats[0] < old_max and current > stats[0]:
            raise ValueError('HP decrease depends on unsaved in-battle context: current HP exceeds target maximum')
        hp = 0 if current == 0 else current + max(0, stats[0]-old_max)
        struct.pack_into('<7H', record, 86, hp, *stats)
    final = bytes(record)
    if not model.write_eligibility(final, tables, context)['eligible']:
        raise ValueError('ordinary output eligibility failed')
    return final


def derive_ordinary(raw, rom, slot, changes):
    """Generalize the existing product family under separate E3 exact-ROM gates.

    In-memory immutable source; existing product workflow owns separate export.
    No PID/identity edits. Independent reconstruction is mandatory before return.
    """
    import pokemonstart_v022_party_model as model
    import pokemonstart_v022_party_audit as audit
    verified, base, source, tables, mon, eligibility = ordinary_inspect(raw, rom, slot)
    if not eligibility['eligible']:
        raise ValueError('ordinary Party rejected: ' + '; '.join(eligibility['reasons']))
    record = transform_ordinary(source, tables, model.saved_context(verified), changes, slot=slot)
    candidate = bytearray(raw)
    record_base = base+v.PARTY_OFFSET+slot*100
    candidate[record_base:record_base+100] = record
    struct.pack_into('<H', candidate, base+0xFF6,
                     v.calculate_save_checksum(candidate[base:base+v.SECTION_LENGTHS[1]]))
    candidate = bytes(candidate)
    if candidate == raw:
        raise ValueError('Party unchanged; no output')
    if record[:4] != source[:4] and any(
            raw[base+v.PARTY_OFFSET+i*100:base+v.PARTY_OFFSET+i*100+4] == record[:4]
            for i in range(verified.party_count) if i != slot):
        raise ValueError('generated personality collides with another Party member')
    after = v.verify_bytes(candidate)
    independent = audit.audit_edit(raw, candidate, rom, slot, changes)
    final = model.decode_record(bytes(record), slot, tables)
    final_eligibility = model.write_eligibility(bytes(record), tables, model.saved_context(after))
    if not final_eligibility['eligible']:
        raise ValueError('ordinary output eligibility failed')
    before_semantic = existing._semantic(verified.party[slot])
    after_semantic = existing._semantic(after.party[slot])
    before_semantic.update(resolved_ability=mon['resolved_ability'], hidden_ability=mon['hidden_ability'])
    after_semantic.update(resolved_ability=final['resolved_ability'], hidden_ability=final['hidden_ability'])
    before_semantic.update(shiny=model.shiny_score(*struct.unpack_from('<II', source, 0)) < 8)
    after_semantic.update(shiny=model.shiny_score(*struct.unpack_from('<II', record, 0)) < 8)
    return candidate, {'slot': slot, 'before': before_semantic, 'after': after_semantic,
                       'changed_offsets': independent['changed_offsets'], 'verifier_accepted': True,
                       'e3': True, 'eligibility': eligibility, 'independent_audit': independent}
