"""Independent stdlib auditor for the basic Money/friendship/observed-Items recipe.

No writer, profile loader or repository verifier imports. It does not audit
stat-changing requests or certify gameplay. Only sanitized metadata is returned.
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
