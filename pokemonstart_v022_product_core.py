"""One deterministic immutable-input transaction across independent product families."""
from __future__ import annotations
import copy
import pokemonstart_fl2_core as profile
import pokemonstart_save_verifier as v
import pokemonstart_v022_product_money as money
import pokemonstart_v022_product_party as party
import pokemonstart_v022_product_inventory as items
import pokemonstart_v022_inventory_editor as medicine_items


def inspect(raw, rom_sha256, *, rom_bytes=None):
    profile._require_rom_hash(rom_sha256)
    if rom_bytes is not None:profile._require_rom_hash(profile.sha(rom_bytes))
    verified=v.verify_bytes(raw)
    report={'input_sha256':verified.file_sha256,'active_slot':verified.active_slot,
            'counter':verified.slots[verified.active_slot].counter,'money':None,
            'party':[], 'items':None, 'rejections':{}}
    try:report['money']=money.inspect(raw,rom_sha256)
    except ValueError as exc:report['rejections']['money']=str(exc)
    for slot,mon in enumerate(verified.party):
        record={'slot':slot,**party.existing._semantic(mon),'capabilities':{}}
        try:
            if rom_bytes is not None:
                _,_,_,tables,decoded,eligibility=party.ordinary_inspect(raw,rom_bytes,slot)
                record.update(species_name=decoded['species_name'],held_item_name=decoded['held_item_name'],resolved_ability=decoded['resolved_ability'],
                              hidden_ability=decoded['hidden_ability'],ordinary_eligibility=eligibility)
                record['capabilities']={'e3':True,**{field:eligibility['eligible'] for field in
                    ('friendship','moves','stats','level_exp','effective_nature','ability','held_item')},
                    'stats_reason':'; '.join(eligibility['reasons'])}
                record['options']=party.ordinary_options(tables)
                record['ability_options']=sorted(set(x for x in tables.species[mon.species].abilities if x)) if 0<mon.species<len(tables.species) else []
            else:record['capabilities']=party.capabilities(raw,rom_sha256,slot)
        except ValueError as exc:record['rejection']=str(exc)
        report['party'].append(record)
    try:report['items']=(medicine_items.inspect(raw,rom_bytes) if rom_bytes is not None
                         else items.inspect(raw,rom_sha256))
    except ValueError as exc:report['rejections']['items']=str(exc)
    return report


def derive(raw, rom_sha256, request, *, rom_bytes=None):
    profile._require_rom_hash(rom_sha256)
    if rom_bytes is not None:profile._require_rom_hash(profile.sha(rom_bytes))
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
            families.append((f'party_{slot}',*party.derive(raw,rom_sha256,slot,edit['changes'],rom_bytes=rom_bytes)))
    if 'items' in request:
        family=(medicine_items.derive(raw,rom_bytes,request['items']) if rom_bytes is not None
                else items.derive(raw,rom_sha256,request['items']))
        families.append(('items',*family))
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
            after={entry['item_id']:entry['quantity'] for entry in receipt['after']['entries']}
            names={entry['item_id']:entry['name'] for entry in receipt['before']['entries']+receipt['after']['entries']}
            for item_id in sorted(before.keys()|after.keys()):
                old,new=before.get(item_id,0),after.get(item_id,0)
                if old!=new:semantics.append(f"{names[item_id]}: x{old} → x{new}")
        else:
            e3_tables=None
            if receipt.get('e3'):
                e3_tables=party.ordinary_inspect(raw,rom_bytes,receipt['slot'])[3]
            for field,before in receipt['before'].items():
                after=receipt['after'][field]
                if after!=before:
                    if e3_tables is not None and field in ('nature_mint','ability_selector','hidden_ability'):
                        continue  # Storage details remain available in Advanced.
                    label={'species':'Species','level':'Level','experience':'EXP','friendship':'Friendship',
                           'moves':'Moves','pp':'PP','ivs':'IVs','evs':'EVs','cached_stats':'Stats',
                           'effective_nature':'Effective nature','resolved_ability':'Ability','held_item':'Held item',
                           'pp_bonuses':'PP-Up'}.get(field,field)
                    if e3_tables is not None and field=='effective_nature':
                        from pokemonstart_v022_party_model import NATURE_NAMES
                        before,after=NATURE_NAMES[before],NATURE_NAMES[after]
                    if e3_tables is not None and field=='pp_bonuses':
                        before,after=([((value>>(2*i))&3) for i in range(4)] for value in (before,after))
                    if e3_tables is not None and field=='held_item':
                        names={0:'None',**{i:x.name for i,x in e3_tables.items.items()}}
                        before,after=names.get(before,before),names.get(after,after)
                    if field=='species':
                        names=party.ordinary_options(e3_tables)['species'] if e3_tables is not None else party.SPECIES
                        before=names.get(before,f'Species #{before}')
                        after=names.get(after,f'Species #{after}')
                    if field=='moves':
                        for index,(old,new) in enumerate(zip(before,after)):
                            if old!=new:
                                names=party.ordinary_options(e3_tables)['moves'] if e3_tables is not None else party.MOVES
                                semantics.append(f"Party #{receipt['slot']+1} Move {index+1}: {names.get(old,old)} → {names.get(new,new)}")
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
    for name,family_candidate,receipt in families:
        if name=='money':
            if money.inspect(candidate,rom_sha256)['money']!=receipt['money']['to']:
                raise ValueError('composed Money postcondition failed')
        elif name=='items':
            current=(medicine_items.inspect(candidate,rom_bytes) if rom_bytes is not None
                     else items.inspect(candidate,rom_sha256))
            if current!=receipt['after']:
                raise ValueError('composed Items postcondition failed')
        else:
            if receipt.get('e3'):
                section=result.slots[result.active_slot].section(1)
                start=section.physical_sector*4096+v.PARTY_OFFSET+receipt['slot']*100
                if candidate[start:start+100]!=family_candidate[start:start+100]:
                    raise ValueError('composed ordinary Party postcondition failed')
            elif party.existing._semantic(result.party[receipt['slot']])!=receipt['after']:
                raise ValueError('composed Party postcondition failed')
    independent=None
    if any(receipt.get('e3') for _,_,receipt in families):
        import pokemonstart_v022_product_audit as audit
        independent=audit.audit_e3(raw,candidate,rom_bytes,request)
    report={'input_sha256':verified.file_sha256,'output_sha256':result.file_sha256,
                      'request':copy.deepcopy(request),'semantic_diff':semantics,
                      'families':reports,'changed_offsets':offsets,'verifier_accepted':True,
                      'active_slot':verified.active_slot,'counter':verified.slots[verified.active_slot].counter}
    if independent is not None:report['independent_e3_audit']=independent
    return candidate,report
