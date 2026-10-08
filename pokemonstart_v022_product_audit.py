"""Independent stdlib auditor for the basic Money/friendship/observed-Items recipe.

No writer, profile loader or repository verifier imports. audit_basic retains the original restricted contract; audit_e3 independently
reconstructs composed ordinary Party edits. Neither certifies gameplay.
"""
import hashlib
import struct

LENGTHS=(0xF24,0xFF0,0xFF0,0xFF0,0xD98,*([0xFF0]*8),0x450)


def checksum(data):
    total=sum(x[0] for x in struct.iter_unpack('<I',data))&0xFFFFFFFF
    return ((total&0xFFFF)+(total>>16))&0xFFFF


def parse(raw):
    if len(raw) not in (0x20000,0x20010):raise ValueError('unsupported length')
    slots=[]
    for slot in range(2):
        sections={};counters=set()
        for physical in range(slot*14,(slot+1)*14):
            base=physical*4096
            logical,stored,signature,counter=struct.unpack_from('<HHII',raw,base+0xFF4)
            if logical>=14 or logical in sections or signature!=0x08012025:
                raise ValueError('section/signature ambiguity')
            if checksum(raw[base:base+LENGTHS[logical]])!=stored:raise ValueError('checksum mismatch')
            sections[logical]=base;counters.add(counter)
        if len(counters)!=1:raise ValueError('counter ambiguity')
        counter=counters.pop()
        if not 0<=counter<=0x7FFFFFFE or counter%2!=slot:raise ValueError('unsupported counter')
        if struct.unpack_from('<I',raw,sections[0]+0xF20)[0]!=0:raise ValueError('unqualified key')
        slots.append({'sections':sections,'counter':counter})
    if abs(slots[0]['counter']-slots[1]['counter'])!=1:raise ValueError('counters not consecutive')
    active=int(slots[1]['counter']>slots[0]['counter'])
    return slots[active]['sections'],active


def audit_basic(before,after,request):
    sections,active=parse(before);parse(after)
    if not isinstance(request,dict) or set(request)!={'money','party','items'}:
        raise ValueError('auditor supports basic three-family receipt only')
    money=request['money']
    if type(money) is not int or not 0<=money<=9999999:raise ValueError('Money invalid')
    source_money=struct.unpack_from('<I',before,sections[1]+0x290)[0]
    if source_money>9999999:raise ValueError('source Money invalid')
    expected=bytearray(before);allowed=set()
    struct.pack_into('<I',expected,sections[1]+0x290,money)
    allowed.update(range(sections[1]+0x290,sections[1]+0x294))
    count=before[sections[1]+0x34];seen=set()
    if not isinstance(request['party'],list) or not request['party']:raise ValueError('Party recipe invalid')
    for edit in request['party']:
        if not isinstance(edit,dict) or set(edit)!={'slot','changes'}:raise ValueError('Party recipe invalid')
        slot=edit['slot'];changes=edit['changes']
        if (type(slot) is not int or not 0<=slot<count<=6 or slot in seen
                or not isinstance(changes,dict) or set(changes)!={'friendship'}
                or type(changes['friendship']) is not int or not 0<=changes['friendship']<=255):
            raise ValueError('only ordinary friendship recipe is independently audited')
        seen.add(slot);record=sections[1]+0x38+slot*100
        if before[record+19]!=2 or struct.unpack_from('<H',before,record+28)[0]!=0 or before[record+75]&0x40:
            raise ValueError('not an ordinary Party record')
        expected[record+41]=changes['friendship'];allowed.add(record+41)
    pocket=sections[13]+0xADC
    rows=[struct.unpack_from('<HH',before,pocket+4*i) for i in range(3)]
    if (rows[0][0]!=13 or not 1<=rows[0][1]<=3 or rows[1]!=(533,1)
            or rows[2] not in ((0,0),(14,1)) or any(before[pocket+12:sections[13]+0xFF0])):
        raise ValueError('observed Items prefix/tail mismatch')
    changes=request['items']
    if not isinstance(changes,dict) or not changes or set(changes)-{'potion_quantity','insert_antidote'}:
        raise ValueError('Items recipe unsupported')
    if 'potion_quantity' in changes:
        quantity=changes['potion_quantity']
        if type(quantity) is not int or not 1<=quantity<=3:raise ValueError('Potion range invalid')
        struct.pack_into('<H',expected,pocket+2,quantity);allowed.update((pocket+2,pocket+3))
    if 'insert_antidote' in changes:
        if changes['insert_antidote'] is not True or rows[2]!=(0,0):raise ValueError('Antidote vacancy invalid')
        struct.pack_into('<HH',expected,pocket+8,14,1);allowed.update(range(pocket+8,pocket+12))
    base=sections[1]
    struct.pack_into('<H',expected,base+0xFF6,checksum(expected[base:base+0xFF0]))
    allowed.update((base+0xFF6,base+0xFF7))
    if after!=bytes(expected):raise ValueError('complete candidate inequality')
    offsets=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
    if not offsets or not set(offsets)<=allowed:raise ValueError('diff envelope mismatch')
    return {'input_sha256':hashlib.sha256(before).hexdigest(),'output_sha256':hashlib.sha256(after).hexdigest(),
            'complete_candidate_equality':True,'all_unrelated_bytes_preserved':True,
            'active_slot':active,'changed_offsets':offsets,'game_roundtrip':False}


def audit_e3(before, after, rom, request):
    """Complete composed reconstruction from independent families only."""
    import pokemonstart_v022_party_audit as party
    import pokemonstart_v022_inventory_audit as inventory
    source = party.inspect(before,rom)
    parsed = party.structure.parse(before)
    section = parsed['slots'][parsed['active']]['positions'][1]*4096
    expected = bytearray(before)
    envelope = set()
    seen = set()
    if 'create' in request:
        import pokemonstart_v022_creation_baseline_audit as creation
        appended=creation.expected_output(before,rom,request['create'])
        count=len(parsed['records'])
        expected[section+52]=appended[section+52]
        envelope.add(section+52)
        start=section+56+count*100
        end=start+100*len(request['create'])
        expected[start:end]=appended[start:end]
        envelope.update(range(start,end))
    for edit in request.get('party',[]):
        slot = edit['slot']
        if type(slot) is not int or slot in seen:
            raise ValueError('independent duplicate/invalid slot')
        seen.add(slot)
        rebuilt, allowed = party.expected_edit(before,rom,slot,edit['changes'])
        start = section+56+slot*100
        expected[start:start+100] = rebuilt[start:start+100]
        envelope.update(allowed)
    if 'money' in request:
        # Both slot/key/range predicates remain the established Money contract.
        for slot in parsed['slots']:
            key = int.from_bytes(slot['sections'][0][0xF20:0xF24],'little')
            old_money = int.from_bytes(slot['sections'][1][0x290:0x294],'little')
            if key or old_money > 9999999:
                raise ValueError('independent Money source gate')
        target = request['money']
        if type(target) is not int or not 0 <= target <= 9999999:
            raise ValueError('independent Money range')
        expected[section+656:section+660] = target.to_bytes(4,'little')
        envelope.update(range(section+656,section+660))
    box_changes = {}
    if 'box' in request:
        import pokemonstart_v022_box_audit as box_audit
        box_changes, _, _ = box_audit.expected_changes(before, rom, request['box'])
        for offset, value in box_changes.items():
            expected[offset] = value
        envelope.update(box_changes)
    if 'items' in request:
        # Remove Party/Money changes before passing the isolated inventory
        # output to its established full independent auditor. It then admits
        # exactly its own bytes, without borrowing a production family result.
        isolated = bytearray(after)
        isolated[section:section+4096] = before[section:section+4096]
        for offset in box_changes:
            isolated[offset] = before[offset]
        inventory.audit_edit(before,bytes(isolated),rom,request['items'])
        for i,(x,y) in enumerate(zip(before,isolated)):
            if x != y:
                if i in envelope:
                    raise ValueError('independent family conflict')
                expected[i] = y
                envelope.add(i)
    expected[section+4086:section+4088] = checksum(expected[section:section+4080]).to_bytes(2,'little')
    envelope.update((section+4086,section+4087))
    rebuilt = party.inspect(after,rom)
    offsets = [i for i,(x,y) in enumerate(zip(before,after)) if x != y]
    if bytes(expected) != after or not offsets or not set(offsets) <= envelope:
        raise ValueError('independent complete composed output/envelope inequality')
    if rebuilt['saved_context'] != source['saved_context']:
        raise ValueError('independent context changed')
    return {'complete_output_equal':True,'complete_postwrite_reconstruction':True,
            'unrelated_bytes_preserved':True,'changed_offsets':offsets,'gameplay_acceptance':False}
