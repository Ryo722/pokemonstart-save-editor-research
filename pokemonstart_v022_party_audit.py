"""Independent E3 reconstruction; no production Party model/writer imports.

Uses the existing independent section validator and direct byte reads. EXP is
found by a forward threshold walk; nature is reconstructed arithmetically and
cross-checked with ROM modifiers. Only decoded semantics/hashes are returned.
"""
from __future__ import annotations
import hashlib
import struct
import pokemonstart_v022_creation_audit as structure

EXACT = '6abce6aac402b18ab2b67a4b86b8b6153520afb0c92cebec570883b4880adbb0'


def reconstruct(record: bytes, rom: bytes) -> dict:
    if len(record) != 100:
        raise ValueError('independent record length')
    def u16(offset):
        return int.from_bytes(record[offset:offset+2], 'little')
    species = u16(32)
    metadata = rom[0x19B8B40 + species*32:0x19B8B40 + (species+1)*32] if 0 < species < 1489 else None
    exp = int.from_bytes(record[36:40], 'little')
    level = None
    growth = metadata[19] if metadata else None
    if growth is not None and growth < 8:
        thresholds = [int.from_bytes(rom[0x14C5D54 + growth*1024 + j*4:
                                        0x14C5D54 + growth*1024 + j*4+4], 'little') for j in range(101)]
        if thresholds[1] <= exp <= thresholds[100]:
            level = 1
            while level < 100 and exp >= thresholds[level+1]:
                level += 1
    nature = int.from_bytes(record[:4], 'little') % 25
    effective = record[15]-1 if 1 <= record[15] <= 25 else nature if record[15] == 0 else None
    ivword = int.from_bytes(record[72:76], 'little')
    ivs = [(ivword // (32**j)) % 32 for j in range(6)]
    evs = list(record[56:62])
    actual = list(struct.unpack_from('<7H', record, 86))
    calculations = []
    if (metadata and effective is not None and 1 <= record[84] <= 100 and not record[16]
            and max(evs) <= 252 and sum(evs) <= 510 and u16(34) != 835
            and species not in (303, 496, 497, 498, 913, 1460)):
        # Exact nature order: Attack, Defense, Speed, SpAttack, SpDefense.
        for constant in (5, record[84]):
            values = []
            for j in range(6):
                n = ((metadata[j]*2 + ivs[j] + evs[j]//4)*record[84])//100
                if j == 0:
                    n += record[84]+10
                else:
                    n += constant
                    position = j-1
                    modifier = 0 if effective//5 == effective%5 else 1 if position == effective//5 else -1 if position == effective%5 else 0
                    # Independent arithmetic must agree with the exact table.
                    signed = rom[0x20F550 + effective*5 + j-1]
                    if (signed if signed < 128 else signed-256) != modifier:
                        raise ValueError('independent nature order disagreement')
                    n = n*(10+modifier)//10
                values.append(n)
            calculations.append(values)
    selector = ivword >> 31
    hidden = bool(record[71] & 16)
    ability = None
    if metadata and species not in (496, 497, 498, 913, 1460):
        first = int.from_bytes(metadata[22:24], 'little')
        second = int.from_bytes(metadata[26:28], 'little')
        third = int.from_bytes(metadata[28:30], 'little')
        ability = third if hidden and third else second if selector and second else first
    moves = []
    for j in range(4):
        mid = u16(44+j*2)
        ups = record[40]//(4**j) % 4
        limit = None
        if mid < 998:
            pp = rom[0x14A3238 + mid*12+4]
            limit = pp if mid == 996 else (pp + pp*20*ups//100) % 256
        moves.append({'move_id': mid, 'pp': record[52+j], 'pp_up_count': ups, 'maximum_pp': limit})
    # Exact catalog already supplies public-facing names on the production
    # path; independently reconstruct numeric held-item metadata here.
    item = u16(34)
    held = None
    if 0 < item < 839:
        metadata_item = rom[0x15199C8 + item*40:0x15199C8 + (item+1)*40]
        if (int.from_bytes(metadata_item[10:12], 'little') == item
                and metadata_item[22] in range(1, 6) and metadata_item[20] in (0, 1, 2)
                and 255 in metadata_item[:10]):
            held = {'pocket': metadata_item[22], 'importance': metadata_item[20],
                    'item_type': metadata_item[23], 'hold_effect': metadata_item[14],
                    'hold_effect_parameter': metadata_item[15]}
    return {'record_sha256': hashlib.sha256(record).hexdigest(), 'species': species,
            'stored_level': record[84], 'experience': exp, 'growth_rate': growth,
            'exp_derived_level': level, 'moves': moves, 'friendship': record[41],
            'ivs': ivs, 'evs': evs, 'native_nature': nature, 'effective_nature': effective,
            'nature_mint': record[15], 'hyper_training': record[16],
            'ability_selector': selector, 'hidden_ability': hidden, 'resolved_ability': ability,
            'held_item': item, 'held_item_metadata': held, 'cached_hp_stats': actual,
            'ordinary_expected_stats': calculations[0] if calculations else None,
            'legacy_expected_stats': calculations[1] if calculations else None,
            'five_matches': bool(calculations and actual[1:] == calculations[0]),
            'level_matches': bool(calculations and actual[1:] == calculations[1]),
            'is_egg': bool(ivword & (1 << 30)), 'backup_species': u16(28)}


def inspect(raw: bytes, rom: bytes) -> dict:
    if len(rom) != 33554432 or hashlib.sha256(rom).hexdigest() != EXACT:
        raise ValueError('independent exact ROM identity')
    parsed = structure.parse(raw)
    sections = parsed['slots'][parsed['active']]['sections']
    # Independently join the serialized parasite; don't import model offsets.
    image = sections[0][0xF24:0xFF0] + sections[4][0xD98:0xFF0] + sections[13][0x450:0xFF0]
    flag = bool(image[6] & 1)
    tier = int.from_bytes(image[560:562], 'little')
    return {'save_sha256': hashlib.sha256(raw).hexdigest(), 'active_slot': parsed['active'],
            'counter': parsed['slots'][parsed['active']]['counter'],
            'saved_context': {'flag_0x930': flag, 'variable_0x5018': tier,
                              'ordinary_saved_context': not flag,
                              'reasons': ['saved facility flag 0x930 is set'] if flag else [],
                              'checksum_covers_context': False,
                              'runtime_in_battle_reconstructed': False},
            'party': [reconstruct(record, rom) for record in parsed['records']]}


def compare(production: dict, independent: dict) -> None:
    for key in ('save_sha256', 'active_slot', 'counter'):
        if production[key] != independent[key]:
            raise ValueError('independent save reconstruction disagreement: ' + key)
    if 'saved_context' in production and production['saved_context'] != independent['saved_context']:
        raise ValueError('independent saved context disagreement')
    if len(production['party']) != len(independent['party']):
        raise ValueError('independent occupancy disagreement')
    for candidate, rebuilt in zip(production['party'], independent['party']):
        for key, value in rebuilt.items():
            actual = candidate[key]
            if key == 'moves':
                actual = [{k: row[k] for k in value[0]} for row in actual]
            if actual != value:
                raise ValueError('independent Party reconstruction disagreement: ' + key)


def ordinary_reasons(record: bytes, rom: bytes, context: dict) -> list:
    row = reconstruct(record, rom)
    reasons = []
    if context['flag_0x930']:
        reasons.append('facility context')
    if record[19] != 2 or row['backup_species'] or row['is_egg'] or record[16]:
        reasons.append('egg/form/hyper-training/sanity')
    if row['species'] not in {*range(1, 152), 288}:
        reasons.append('ordinary species subset')
    if row['exp_derived_level'] != record[84] or not 1 <= record[84] <= 100:
        reasons.append('level/EXP')
    hp = row['cached_hp_stats']
    if not 0 <= hp[0] <= hp[1] or not hp[1] or row['ordinary_expected_stats'] != hp[1:]:
        reasons.append('HP/cache')
    if not row['resolved_ability']:
        reasons.append('ability')
    if row['held_item']:
        if not safe_item(row['held_item'], row['held_item_metadata'], retained=True):
            reasons.append('retained item')
    for move in row['moves']:
        if move['maximum_pp'] is None or move['move_id'] and (
                rom[0x14A3238+move['move_id']*12+4] == 0 or move['pp'] > move['maximum_pp']):
            reasons.append('occupied move/PP')
    return reasons


def safe_item(item_id, metadata, *, retained=False):
    if item_id == 0:
        return True
    expected = {139: (5,0,1,1,10), 142: (5,0,1,1,30), 200: (1,0,4,43,10)}
    if retained:
        expected[202] = (1,0,4,45,0)
    return metadata is not None and tuple(metadata[k] for k in (
        'pocket','importance','item_type','hold_effect','hold_effect_parameter')) == expected.get(item_id)


def independent_shiny_identity(record, rom: bytes, changes: dict):
    """Independent PID-only transition: same documented derivation, own checks."""
    want = changes['shiny']
    if type(want) is not bool or 'species' in changes:
        raise ValueError('independent shiny contract')
    old = int.from_bytes(record[0:4], 'little')
    tid = int.from_bytes(record[4:8], 'little')
    xor = lambda p: (tid & 65535) ^ (tid >> 16) ^ (p & 65535) ^ (p >> 16)
    if (xor(old) < 8) == want:
        if len(changes) == 1:
            raise ValueError('independent unchanged shiny state')
        return bytes(record[0:4]), set()
    ratio = rom[0x19B8B40 + int.from_bytes(record[32:34], 'little') * 32 + 16]
    sex = lambda p: ratio if ratio in (0, 254, 255) else (254 if p % 256 < ratio else 0)
    for attempt in range(4096):
        digest = hashlib.sha256(b'E6 PID-only shiny transition v1\0' + old.to_bytes(4, 'little')
                                + tid.to_bytes(4, 'little') + bytes((want,)) + attempt.to_bytes(2, 'little')).digest()
        low = digest[0] | digest[1] << 8
        high = ((tid & 65535) ^ (tid >> 16) ^ low ^ digest[2] % 8) if want else digest[2] | digest[3] << 8
        candidate = high * 65536 + low
        if (xor(candidate) < 8) is want and candidate != old and candidate % 25 == old % 25 and sex(candidate) == sex(old):
            return candidate.to_bytes(4, 'little'), {0, 1, 2, 3}
    raise ValueError('independent shiny search exhausted')


def expected_record(source: bytes, rom: bytes, context: dict, changes: dict):
    """Independent adopted E3 record arithmetic, reusable by creator audit."""
    def number(x, low, high):
        if type(x) is not int or not low <= x <= high:
            raise ValueError('independent integer/range')
        return x
    if len(source) != 100 or ordinary_reasons(source, rom, context):
        raise ValueError('independent ordinary source gate')
    permitted = {'species','level','experience','ivs','evs','effective_nature','ability',
                 'held_item','friendship','moves','pp','pp_up','shiny'}
    if not isinstance(changes, dict) or not changes or set(changes)-permitted:
        raise ValueError('independent field contract')
    old = reconstruct(source, rom)
    record = bytearray(source)
    envelope = set()
    if 'species' in changes:
        sid = number(changes['species'], 1, 1488)
        if sid not in {*range(1,152),288} or not all(rom[0x19B8B40+32*sid:0x19B8B40+32*sid+6]):
            raise ValueError('independent target species')
        record[32:34] = sid.to_bytes(2, 'little')
        envelope.update((32,33))
    sid = int.from_bytes(record[32:34], 'little')
    growth = rom[0x19B8B40+sid*32+19]
    thresholds = [int.from_bytes(rom[0x14C5D54+growth*1024+i*4:0x14C5D54+growth*1024+i*4+4], 'little')
                  for i in range(101)]
    level = number(changes.get('level', source[84]), 1, 100)
    exp = changes.get('experience', old['experience'])
    if 'experience' not in changes and (level != source[84] or growth != old['growth_rate']):
        exp = thresholds[level]
    number(exp, thresholds[1], thresholds[100])
    actual_level = 1
    while actual_level < 100 and exp >= thresholds[actual_level+1]:
        actual_level += 1
    if 'level' in changes and actual_level != level:
        raise ValueError('independent level/EXP conflict')
    if set(changes) & {'species','level','experience'}:
        record[36:40] = exp.to_bytes(4,'little')
        record[84] = actual_level
        envelope.update((*range(36,40),84))
    if 'friendship' in changes:
        record[41] = number(changes['friendship'],0,255)
        envelope.add(41)
    for field, maximum in (('ivs',31),('evs',252)):
        if field not in changes:
            continue
        values = changes[field]
        if not isinstance(values,(tuple,list)) or len(values) != 6:
            raise ValueError('independent six values')
        for x in values:
            number(x,0,maximum)
        if field == 'evs':
            if sum(values)>510:
                raise ValueError('independent EV total')
            record[56:62] = bytes(values)
            envelope.update(range(56,62))
        else:
            packed = int.from_bytes(record[72:76],'little')//(1<<30)*(1<<30)
            for i,x in enumerate(values):
                packed += x*32**i
            record[72:76] = packed.to_bytes(4,'little')
            envelope.update(range(72,76))
    if 'effective_nature' in changes:
        nature = number(changes['effective_nature'],0,24)
        if nature != old['effective_nature']:
            record[15] = 0 if nature == old['native_nature'] else nature+1
        envelope.add(15)
    if 'held_item' in changes:
        item = number(changes['held_item'],0,838)
        record[34:36] = item.to_bytes(2,'little')
        if not safe_item(item, reconstruct(record,rom)['held_item_metadata']):
            raise ValueError('independent held target')
        envelope.update((34,35))
    if 'ability' in changes:
        target = number(changes['ability'],1,65535)
        possibilities = []
        for selector in (0,1):
            for hidden in (False,True):
                test = bytearray(record)
                test[71] = test[71]%16 + (16 if hidden else 0) + test[71]//32*32
                test[75] = test[75]%128 + 128*selector
                if reconstruct(test,rom)['resolved_ability'] == target:
                    cost = int(selector != old['ability_selector']) + int(hidden != old['hidden_ability'])
                    possibilities.append((cost,selector,hidden))
        if not possibilities:
            raise ValueError('independent unavailable ability')
        _,selector,hidden = sorted(possibilities)[0]
        record[71] = record[71]%16 + 16*hidden + record[71]//32*32
        record[75] = record[75]%128 + 128*selector
        envelope.update((71,75))
    by_slot = {}
    for field in ('moves','pp','pp_up'):
        if field not in changes:
            continue
        mapping = changes[field]
        if not isinstance(mapping,dict) or not mapping:
            raise ValueError('independent slot map')
        for index,value in mapping.items():
            number(index,0,3)
            by_slot.setdefault(index,{})[field] = value
    for index, change in by_slot.items():
        before = old['moves'][index]
        move = number(change.get('moves',before['move_id']),0,997)
        bonus = number(change.get('pp_up',before['pp_up_count']),0,3)
        base_pp = rom[0x14A3238+12*move+4]
        if move and not base_pp:
            raise ValueError('independent unresolved move')
        if move == 0:
            if 'pp' in change or 'pp_up' in change:
                raise ValueError('independent empty PP edit')
            pp = base_pp if before['move_id'] != 0 else before['pp']
        else:
            maximum = base_pp if move == 996 else (base_pp*(5+bonus)//5)%256
            resetting = move != before['move_id'] or bonus != before['pp_up_count']
            pp = number(change.get('pp',maximum if resetting else before['pp']),0,maximum)
        record[44+index*2:46+index*2] = move.to_bytes(2,'little')
        record[52+index] = pp
        old_bonus = record[40]//(4**index)%4
        record[40] += (bonus-old_bonus)*4**index
        if 'moves' in change:
            envelope.update((44+2*index,45+2*index,52+index))
        if 'pp' in change:
            envelope.add(52+index)
        if 'pp_up' in change:
            envelope.update((40,52+index))
    if 'shiny' in changes:
        record[0:4], identity = independent_shiny_identity(record, rom, changes)
        envelope.update(identity)
    if set(changes) & {'species','level','experience','ivs','evs','effective_nature'}:
        stats = reconstruct(record,rom)['ordinary_expected_stats']
        current, maximum = old['cached_hp_stats'][:2]
        if stats is None or stats[0] < maximum and current > stats[0]:
            raise ValueError('independent context-sensitive HP decrease')
        hp = current if stats[0] <= maximum or current == 0 else current+stats[0]-maximum
        record[86:100] = struct.pack('<7H',hp,*stats)
        envelope.update(range(86,100))
    if ordinary_reasons(record,rom,context):
        raise ValueError('independent output ordinary gate')
    return bytes(record), envelope


def expected_edit(raw: bytes, rom: bytes, slot: int, changes: dict) -> tuple[bytes, set]:
    """Independent complete expected save, never importing the production writer.

    Duplicated contract is intentional: direct bytes, separate parser, separate
    range checks, threshold walk, nature arithmetic and field envelope.
    """
    report = inspect(raw, rom)
    parsed = structure.parse(raw)
    def number(x, low, high):
        if type(x) is not int or not low <= x <= high:
            raise ValueError('independent integer/range')
        return x
    number(slot, 0, parsed['count']-1)
    source = parsed['records'][slot]
    if ordinary_reasons(source, rom, report['saved_context']):
        raise ValueError('independent ordinary source gate')
    record, envelope = expected_record(source, rom, report['saved_context'], changes)
    section = parsed['slots'][parsed['active']]['positions'][1]*4096
    start = section+56+slot*100
    expected = bytearray(raw)
    expected[start:start+100] = record
    expected[section+4086:section+4088] = structure.checksum(expected[section:section+4080]).to_bytes(2,'little')
    return bytes(expected), {start+i for i in envelope} | {section+4086,section+4087}


def audit_edit(before, after, rom, slot, changes):
    expected, permitted = expected_edit(before,rom,slot,changes)
    rebuilt = inspect(after,rom)
    if expected != after or before == after:
        raise ValueError('independent complete Party output inequality')
    offsets = [i for i,(x,y) in enumerate(zip(before,after)) if x != y]
    if not set(offsets) <= permitted:
        raise ValueError('independent Party byte envelope')
    return {'complete_output_equal':True,'unrelated_bytes_preserved':True,
            'complete_postwrite_reconstruction':True,'changed_offsets':offsets,
            'output_sha256': rebuilt['save_sha256'], 'gameplay_acceptance':False}
