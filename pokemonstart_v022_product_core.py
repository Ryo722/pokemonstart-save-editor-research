"""One deterministic immutable-input transaction across independent product families."""
from __future__ import annotations
import copy
import pokemonstart_fl2_core as profile
import pokemonstart_save_verifier as v
import pokemonstart_v022_product_money as money
import pokemonstart_v022_product_party as party
import pokemonstart_v022_product_inventory as items


def inspect(raw, rom_sha256):
    profile._require_rom_hash(rom_sha256)
    verified=v.verify_bytes(raw)
    report={'input_sha256':verified.file_sha256,'active_slot':verified.active_slot,
            'counter':verified.slots[verified.active_slot].counter,'money':None,
            'party':[], 'items':None, 'rejections':{}}
    try:report['money']=money.inspect(raw,rom_sha256)
    except ValueError as exc:report['rejections']['money']=str(exc)
    for slot,mon in enumerate(verified.party):
        record={'slot':slot,**party.existing._semantic(mon),'capabilities':{}}
        try:record['capabilities']=party.capabilities(raw,rom_sha256,slot)
        except ValueError as exc:record['rejection']=str(exc)
        report['party'].append(record)
    try:report['items']=items.inspect(raw,rom_sha256)
    except ValueError as exc:report['rejections']['items']=str(exc)
    return report


def derive(raw, rom_sha256, request):
    profile._require_rom_hash(rom_sha256)
    if not isinstance(request,dict) or not request or set(request)-{'money','party','items'}:
        raise ValueError('unsupported or empty product transaction')
    verified=v.verify_bytes(raw)
    families=[]
    if 'money' in request:families.append(('money',*money.derive(raw,rom_sha256,request['money'])))
    if 'party' in request:
        edits=request['party']
        if not isinstance(edits,list) or not edits:raise ValueError('Party edits require nonempty list')
        slots=set()
        for edit in edits:
            if not isinstance(edit,dict) or set(edit)!={'slot','changes'}:
                raise ValueError('Party edit requires slot and changes')
            slot=edit['slot']
            if type(slot) is not int or slot in slots:raise ValueError('duplicate/invalid Party slot')
            slots.add(slot)
            families.append((f'party_{slot}',*party.derive(raw,rom_sha256,slot,edit['changes'])))
    if 'items' in request:families.append(('items',*items.derive(raw,rom_sha256,request['items'])))
    output=bytearray(raw)
    occupied=set();covered=set();checksums=set();reports={};semantics=[]
    for name,candidate,receipt in families:
        if len(candidate)!=len(raw):raise ValueError('family output length mismatch')
        for section in verified.slots[verified.active_slot].sections:
            base=section.physical_sector*4096
            checksums.update((base+0xFF6,base+0xFF7))
        for offset,(old,new) in enumerate(zip(raw,candidate)):
            if old==new or offset in checksums:continue
            if offset in occupied:raise ValueError('family byte conflict')
            occupied.add(offset);output[offset]=new
        reports[name]=receipt
        if name=='money':semantics.append(f"Money: {receipt['money']['from']:,} → {receipt['money']['to']:,}")
        elif name=='items':
            before={entry['item_id']:entry['quantity'] for entry in receipt['before']['entries']}
            for entry in receipt['after']['entries']:
                old=before.get(entry['item_id'],0)
                if old!=entry['quantity']:semantics.append(f"{entry['name']}: x{old} → x{entry['quantity']}")
        else:
            for field,before in receipt['before'].items():
                after=receipt['after'][field]
                if after!=before:
                    label={'species':'Species','level':'Level','experience':'EXP','friendship':'Friendship',
                           'moves':'Moves','pp':'PP','ivs':'IVs','evs':'EVs','cached_stats':'Stats'}.get(field,field)
                    if field=='species':
                        before=party.SPECIES.get(before,f'Species #{before}')
                        after=party.SPECIES.get(after,f'Species #{after}')
                    if field=='moves':
                        for index,(old,new) in enumerate(zip(before,after)):
                            if old!=new:semantics.append(f"Party #{receipt['slot']+1} Move {index+1}: {party.MOVES.get(old,old)} → {party.MOVES.get(new,new)}")
                    else:semantics.append(f"Party #{receipt['slot']+1} {label}: {before} → {after}")
    if not occupied:raise ValueError('transaction unchanged; no output')
    for section in verified.slots[verified.active_slot].sections:
        base=section.physical_sector*4096
        if any(base<=offset<base+v.SECTION_LENGTHS[section.section_id] for offset in occupied):
            checksum=v.calculate_save_checksum(output[base:base+v.SECTION_LENGTHS[section.section_id]])
            output[base+0xFF6:base+0xFF8]=checksum.to_bytes(2,'little')
            covered.update((base+0xFF6,base+0xFF7))
    candidate=bytes(output)
    result=v.verify_bytes(candidate)
    offsets=[i for i,(a,b) in enumerate(zip(raw,candidate)) if a!=b]
    if not set(offsets)<=occupied|covered:raise ValueError('transaction envelope failed')
    # Recheck family-specific results after composition, not merely before it.
    for name,_,receipt in families:
        if name=='money':
            if money.inspect(candidate,rom_sha256)['money']!=receipt['money']['to']:
                raise ValueError('composed Money postcondition failed')
        elif name=='items':
            if items.inspect(candidate,rom_sha256)!=receipt['after']:
                raise ValueError('composed Items postcondition failed')
        else:
            if party.existing._semantic(result.party[receipt['slot']])!=receipt['after']:
                raise ValueError('composed Party postcondition failed')
    return candidate,{'input_sha256':verified.file_sha256,'output_sha256':result.file_sha256,
                      'request':copy.deepcopy(request),'semantic_diff':semantics,
                      'families':reports,'changed_offsets':offsets,'verifier_accepted':True,
                      'active_slot':verified.active_slot,'counter':verified.slots[verified.active_slot].counter}
