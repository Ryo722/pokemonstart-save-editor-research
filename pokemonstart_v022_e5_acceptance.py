"""Bounded E5 exact-v0.22 recipe and round-trip checks.

Receipts gate only a particular acceptance run. They are never product
eligibility rules, and reports never claim Human gameplay attestation.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import pokemonstart_v022_product_core as core
import pokemonstart_v022_party_audit as party_audit
import pokemonstart_v022_inventory_audit as inventory_audit


def _json(value):
    return json.loads(json.dumps(value, sort_keys=True))


def _restore_receipt(receipt):
    result=copy.deepcopy(receipt)
    for edit in result.get('transaction',{}).get('request',{}).get('party',[]):
        for field in ('moves','pp','pp_up'):
            if field not in edit['changes']:continue
            restored={}
            for key,value in edit['changes'][field].items():
                if type(key) is str:
                    if key not in ('0','1','2','3'):raise ValueError('invalid JSON move-slot key')
                    key=int(key)
                if type(key) is not int or key in restored:raise ValueError('ambiguous move-slot key')
                restored[key]=value
            edit['changes'][field]=restored
    return result


# Gameplay may only raise EXP/level/EVs and consume one-use held items; every
# other requested field must persist exactly through the ordinary SAVE.
_HELD_CONSUMABLE=(139,142)


def _assert_requested_persisted(changes, expected, actual, label, source=None):
    """Fail closed unless each requested Party field survived the returned SAVE.

    `source` (pre-edit semantics) lets lower-bound fields detect a lost
    decrease: returning to the pre-edit value counts as not persisted.
    """
    def fail(field):
        raise ValueError(f'E5 requested Party state did not persist: {label} {field}')
    def reverted(key, field):
        return source is not None and source[field]!=expected[field] and actual[key]==source[field]
    for field,requested in changes.items():
        if field=='moves':
            current=[x['move_id'] for x in actual['moves']]
            if any(current[int(i)]!=v for i,v in requested.items()):fail('moves')
        elif field=='pp_up':
            if any(actual['moves'][int(i)]['pp_up_count']!=v for i,v in requested.items()):fail('pp_up')
        elif field=='pp':
            if any(not 0<=actual['moves'][int(i)]['pp']<=actual['moves'][int(i)]['maximum_pp']
                   for i in requested):fail('pp')
        elif field in ('level','experience'):
            key='stored_level' if field=='level' else 'experience'
            if actual[key]<expected[field] or reverted(key,field):fail(field)
        elif field=='evs':
            if any(a<b for a,b in zip(actual['evs'],expected['evs'])) or reverted('evs','evs'):fail('evs')
        elif field=='held_item':
            consumed=expected['held_item'] in _HELD_CONSUMABLE and actual['held_item']==0
            if actual['held_item']!=expected['held_item'] and not consumed:fail('held_item')
            if consumed and (source is None or source['held_item']==0):
                fail('held_item (loss indistinguishable from consumption)')
        elif field in ('ability','resolved_ability'):
            if actual['resolved_ability']!=expected[field]:fail('ability')
        elif field in ('species','friendship','ivs','effective_nature','nature'):
            key='effective_nature' if field=='nature' else field
            if actual[key]!=expected[field]:fail(field)
        else:raise ValueError(f'E5 persistence check has no rule for requested field: {field}')


def _build_recipe(raw: bytes, rom: bytes):
    digest=core.profile.sha(rom)
    report=core.inspect(raw,digest,rom_bytes=rom)
    creator=report.get('creator',{})
    if not creator.get('eligible') or creator.get('first_slot',6)>4:
        raise ValueError('E5 cycle 1 requires an eligible Party with at least two empty positions')
    if not report['money']:
        raise ValueError('E5 cycle 1 requires adopted Money eligibility')
    if not report['items'] or not report['items'].get('e2'):
        raise ValueError('E5 cycle 1 requires adopted E2 Inventory eligibility')
    eligible=[p for p in report['party'] if p.get('ordinary_eligibility',{}).get('eligible')]
    if not eligible:raise ValueError('E5 cycle 1 requires an E3-eligible existing member')
    mon=eligible[0]
    changes={'friendship':(mon['friendship']+1)%256}
    # Exercise Stats with a bounded non-HP field when the natural source permits it.
    if mon['ivs'][1]<31:
        ivs=list(mon['ivs']);ivs[1]+=1;changes['ivs']=ivs
    elif mon['evs'][1]<252 and sum(mon['evs'])<510:
        evs=list(mon['evs']);evs[1]+=1;changes['evs']=evs
    # Exercise Moves using the E3-advertised move catalog.
    move_options=mon['options']['moves']
    target_move=next((move for move in (33,45,39,98) if move in move_options and move!=mon['moves'][0]),None)
    if target_move is None:
        target_move=next((move for move in move_options if move and move!=mon['moves'][0]),None)
    if target_move is None:raise ValueError('E5 source has no alternate E3-supported move target')
    changes['moves']={0:target_move}

    item=report['items'];entries=item['entries'];editable=[e for e in entries if e['editable']]
    if not editable:raise ValueError('E5 source has no editable E2 medicine')
    first=editable[0]
    ops=[{'op':'set','item_id':first['item_id'],
          'quantity':first['quantity']+1 if first['quantity']<999 else first['quantity']-1}]
    if len(editable)>1:
        ops.append({'op':'remove','item_id':editable[1]['item_id']})
    held={e['item_id'] for e in entries}
    additions=[item_id for item_id in sorted(item['supported_names']) if item_id not in held]
    if additions and item['occupied']<item['capacity']:
        ops.append({'op':'add','item_id':additions[0],'quantity':1})

    options=creator['options'];species=19 if 19 in options['species'] else next(iter(options['species']))
    moves=options['moves'];move=33 if 33 in moves and 33 else next(x for x in moves if x)
    abilities=[x for x in options['abilities'][species][:2] if x]
    if not abilities:raise ValueError('E5 creator species has no adopted ordinary ability')
    create={'species':species,'level':12,'nature':3,
            'friendship':creator['friendship_defaults'][species],'ability':abilities[0],
            'held_item':0,'ivs':[20]*6,'evs':[0]*6,'moves':[move,0,0,0]}
    target_money=1234567 if report['money']['money']!=1234567 else 7654321
    request={'money':target_money,'party':[{'slot':mon['slot'],'changes':changes}],
             'items':ops,'create':[create]}
    _,transaction=core.derive(raw,digest,request,rom_bytes=rom)
    return {'schema':'e5-v022-recipe-1','source_sha256':core.profile.sha(raw),
            'rom_sha256':digest,'status':'PREPARED_NOT_GAME_ACCEPTED',
            'transaction':transaction,'created_slot':creator['first_slot'],
            'gameplay_attestation':False}


def prepare(raw: bytes, rom: bytes):
    return _build_recipe(raw,rom)


def prepare_cycle2(raw: bytes, rom: bytes, *, created_slot: int):
    digest=core.profile.sha(rom)
    report=core.inspect(raw,digest,rom_bytes=rom)
    if type(created_slot) is not int or not 0<=created_slot<len(report['party']):
        raise ValueError('Cycle 2 created slot is outside the current Party')
    mon=report['party'][created_slot]
    if not mon.get('ordinary_eligibility',{}).get('eligible'):
        raise ValueError('Cycle 2 created member is not E3-eligible after game progress')
    target=(mon['friendship']+1)%256
    request={'party':[{'slot':created_slot,'changes':{'friendship':target}}]}
    _,transaction=core.derive(raw,digest,request,rom_bytes=rom)
    return {'schema':'e5-v022-cycle2-1','source_sha256':core.profile.sha(raw),
            'rom_sha256':digest,'status':'PREPARED_NOT_GAME_ACCEPTED',
            'transaction':transaction,'gameplay_attestation':False}


def audit_export(source: bytes, actual: bytes, rom: bytes, receipt: dict):
    receipt=_restore_receipt(receipt)
    digest=core.profile.sha(rom)
    if receipt.get('rom_sha256')!=digest or receipt.get('source_sha256')!=core.profile.sha(source):
        raise ValueError('E5 receipt source/ROM identity mismatch')
    if receipt.get('schema')=='e5-v022-recipe-1':
        regenerated=prepare(source,rom)
    elif receipt.get('schema')=='e5-v022-cycle2-1':
        regenerated=prepare_cycle2(source,rom,created_slot=receipt['transaction']['request']['party'][0]['slot'])
    else:raise ValueError('unsupported E5 receipt schema')
    if _json(regenerated)!=_json(receipt):raise ValueError('E5 receipt differs from dynamically regenerated recipe')
    expected,transaction=core.derive(source,digest,copy.deepcopy(receipt['transaction']['request']),rom_bytes=rom)
    if actual!=expected:raise ValueError('actual GUI output differs from independent core output')
    audit=transaction.get('independent_e4_audit') or transaction.get('independent_e3_audit')
    if not audit or not audit.get('complete_output_equal'):
        raise ValueError('independent complete-output reconstruction missing')
    return {'status':'GUI_OUTPUT_EQUALS_INDEPENDENT_CORE_AND_AUDIT',
            'input_sha256':core.profile.sha(source),'output_sha256':core.profile.sha(actual),
            'families':list(transaction['families']),'complete_output_equal':True,
            'source_immutable':True,'rom_immutable':True,'gameplay_acceptance':False}


def check_cycle1_return(source: bytes, returned: bytes, rom: bytes, receipt: dict):
    receipt=_restore_receipt(receipt)
    audit_export(source,core.derive(source,core.profile.sha(rom),receipt['transaction']['request'],rom_bytes=rom)[0],rom,receipt)
    digest=core.profile.sha(rom)
    expected,transaction=core.derive(source,digest,receipt['transaction']['request'],rom_bytes=rom)
    before=party_audit.structure.parse(expected);after=party_audit.structure.parse(returned)
    old=before['slots'][before['active']];new=after['slots'][after['active']]
    if len(expected)!=len(returned) or after['active']==before['active'] or new['counter']!=old['counter']+1:
        raise ValueError('E5 return requires exactly one ordinary SAVE slot/counter transition')
    if before['count']!=after['count'] or after['count']!=len(party_audit.inspect(expected,rom)['party']):
        raise ValueError('E5 return Party count changed')
    prior=before['active']*14*4096
    if expected[prior:prior+14*4096]!=returned[prior:prior+14*4096]:
        raise ValueError('E5 prior active slot was not preserved')
    for sid in range(14):
        if new['positions'][sid]%14!=(old['positions'][sid]%14+1)%14:
            raise ValueError('E5 normal SAVE section rotation mismatch')
    if after['money']!=receipt['transaction']['request']['money']:
        raise ValueError('E5 returned Money differs from requested value')
    if [p['entries'] for p in inventory_audit.restricted(expected,rom)['pockets']] != [
            p['entries'] for p in inventory_audit.restricted(returned,rom)['pockets']]:
        raise ValueError('E5 returned Inventory differs from exported state')
    inspection=core.inspect(returned,digest,rom_bytes=rom)
    if not inspection.get('money') or not inspection.get('items') or not inspection['items'].get('e2'):
        raise ValueError('E5 returned save lost adopted Money/E2 eligibility')
    if not any(p.get('ordinary_eligibility',{}).get('eligible') for p in inspection['party']):
        raise ValueError('E5 returned save has no E3-eligible Party member')
    if not inspection.get('creator',{}).get('eligible'):
        raise ValueError('E5 returned save is no longer E4-eligible: '+inspection.get('creator',{}).get('reason','unknown'))
    expected_party=party_audit.inspect(expected,rom)['party']
    actual_audit=party_audit.inspect(returned,rom)
    actual_party=actual_audit['party']
    parsed_source=party_audit.structure.parse(expected)
    parsed_return=party_audit.structure.parse(returned)
    initial_count=party_audit.structure.parse(source)['count']
    allowed={*range(34,40),41,*range(52,62),*range(80,85),*range(86,100)}
    drifts=[]
    for slot,(left,right,old_record,new_record) in enumerate(zip(expected_party,actual_party,
            parsed_source['records'],parsed_return['records'])):
        if party_audit.ordinary_reasons(new_record,rom,actual_audit['saved_context']):
            raise ValueError(f'E5 returned Party member is not ordinary-eligible: slot {slot+1}')
        changes=[i for i,(a,b) in enumerate(zip(old_record,new_record)) if a!=b]
        if not set(changes)<=allowed:
            raise ValueError(f'E5 unexplained Party drift in slot {slot+1}')
        for field in ('species','moves','ivs','effective_nature','ability_selector',
                      'hidden_ability','resolved_ability','hyper_training'):
            a,b=left[field],right[field]
            if field=='moves':a,b=[x['move_id'] for x in a],[x['move_id'] for x in b]
            if a!=b:raise ValueError(f'E5 invariant Party field changed: slot {slot+1} {field}')
        if left['held_item']!=right['held_item'] and not (left['held_item'] in (139,142) and right['held_item']==0):
            raise ValueError(f'E5 unexpected held-item transition in slot {slot+1}')
        if right['experience']<left['experience'] or any(a<b for a,b in zip(right['evs'],left['evs'])):
            raise ValueError(f'E5 EXP/EV decreased in slot {slot+1}')
        for field in ('held_item','experience','stored_level','friendship','evs','cached_hp_stats','moves'):
            if left[field]!=right[field]:drifts.append({'slot':slot,'created':slot>=initial_count,'field':field})
    for edit in receipt['transaction']['request']['party']:
        expected_after=dict(receipt['transaction']['families'][f"party_{edit['slot']}"]['after'])
        expected_after['ability']=expected_after['resolved_ability']
        _assert_requested_persisted(edit['changes'],expected_after,actual_party[edit['slot']],
                                    f"slot {edit['slot']+1}",
                                    receipt['transaction']['families'][f"party_{edit['slot']}"]['before'])
    for created in receipt['transaction']['families']['create']['created']:
        actual=actual_party[created['slot']]
        comparisons={'species':created['species'],'ivs':created['ivs'],
                     'effective_nature':created['nature'],'resolved_ability':created['ability']}
        comparisons['moves']=created['moves']
        for field,value in comparisons.items():
            current=[x['move_id'] for x in actual['moves']] if field=='moves' else actual[field]
            if current!=value:
                raise ValueError(f'E5 created Pokémon invariant did not persist: {field}')
        _assert_requested_persisted({'level':created['level'],'friendship':created['friendship'],
                                     'held_item':created['held_item'],'evs':created['evs']},
                                    created,actual,f"created slot {created['slot']+1}")
    return {'status':'MACHINE_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED','counter':[old['counter'],new['counter']],
            'previous_active_preserved':True,'normal_section_rotation':True,
            'money_inventory_persisted':True,'continued_e1_e2_e3_e4_eligibility':True,
            'requested_fields_persisted':True,
            'reported_gameplay_drift_fields':drifts,'human_gameplay_attestation':False,
            'independent_e4_audit':transaction['independent_e4_audit']}


def check_cycle2_return(source: bytes, returned: bytes, rom: bytes, receipt: dict):
    receipt=_restore_receipt(receipt)
    expected,transaction=core.derive(source,core.profile.sha(rom),receipt['transaction']['request'],rom_bytes=rom)
    audit_export(source,expected,rom,receipt)
    core.v.verify_bytes(returned)
    before=party_audit.structure.parse(expected);after=party_audit.structure.parse(returned)
    old=before['slots'][before['active']];new=after['slots'][after['active']]
    if (after['active']==before['active'] or new['counter']!=old['counter']+1
            or before['count']!=after['count']):
        raise ValueError('E5 Cycle 2 requires exactly one ordinary SAVE transition')
    prior=before['active']*14*4096
    if expected[prior:prior+14*4096]!=returned[prior:prior+14*4096]:
        raise ValueError('E5 Cycle 2 prior active slot was not preserved')
    for sid in range(14):
        if new['positions'][sid]%14!=(old['positions'][sid]%14+1)%14:
            raise ValueError('E5 Cycle 2 normal SAVE section rotation mismatch')
    inspection=party_audit.inspect(returned,rom)
    if inspection['saved_context']['flag_0x930'] or not any(
            not party_audit.ordinary_reasons(record,rom,inspection['saved_context'])
            for record in after['records']):
        raise ValueError('E5 Cycle 2 returned save lost ordinary E3 eligibility')
    product=core.inspect(returned,core.profile.sha(rom),rom_bytes=rom)
    if not product.get('money') or not product.get('items') or not product['items'].get('e2'):
        raise ValueError('E5 Cycle 2 returned save lost Money/E2 eligibility')
    if not product.get('creator',{}).get('eligible'):
        raise ValueError('E5 Cycle 2 returned save lost E4 eligibility')
    if core.money.inspect(source,core.profile.sha(rom))['money']!=product['money']['money']:
        raise ValueError('E5 Cycle 2 Money changed unexpectedly')
    if inventory_audit.restricted(source,rom)['pockets']!=inventory_audit.restricted(returned,rom)['pockets']:
        raise ValueError('E5 Cycle 2 Inventory changed unexpectedly')
    returned_party=inspection['party']
    for edit in receipt['transaction']['request']['party']:
        expected_after=dict(transaction['families'][f"party_{edit['slot']}"]['after'])
        expected_after['ability']=expected_after['resolved_ability']
        _assert_requested_persisted(edit['changes'],expected_after,returned_party[edit['slot']],
                                    f"Cycle 2 slot {edit['slot']+1}",
                                    transaction['families'][f"party_{edit['slot']}"]['before'])
    return {'status':'MACHINE_CYCLE2_RETURN_PASS_HUMAN_ATTESTATION_REQUIRED',
            'counter':[old['counter'],new['counter']],'previous_active_preserved':True,
            'normal_section_rotation':True,'continued_e1_e2_e3_e4_eligibility':True,
            'requested_fields_persisted':True,
            'independent_e3_audit':transaction['independent_e3_audit'],
            'human_gameplay_attestation':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=core.profile.ROM_DEFAULT)
    sub=parser.add_subparsers(dest='action',required=True)
    for action in ('prepare','prepare-cycle2'):
        p=sub.add_parser(action);p.add_argument('source',type=Path);p.add_argument('--receipt',type=Path)
        if action=='prepare-cycle2':p.add_argument('--created-slot',type=int,required=True)
    for action in ('audit-export','check-return'):
        p=sub.add_parser(action);p.add_argument('source',type=Path)
        p.add_argument('artifact',type=Path);p.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args(argv)
    rom=core.profile._private_file(args.rom,'ROM',must_exist=True).read_bytes()
    source=core.profile._private_file(args.source,'save',must_exist=True).read_bytes()
    if args.action in ('prepare','prepare-cycle2'):
        receipt=prepare(source,rom) if args.action=='prepare' else prepare_cycle2(source,rom,created_slot=args.created_slot)
        report=json.dumps(receipt,ensure_ascii=False,indent=2)
        if args.receipt is None:print(report)
        else:
            path=core.profile._private_file(args.receipt,'receipt',must_exist=False)
            with path.open('x',encoding='utf-8') as handle:handle.write(report+'\n')
            print(json.dumps({'status':receipt['status'],'receipt_saved':True,'schema':receipt['schema'],
                              'human_readable_changes':receipt['transaction']['semantic_diff']},
                             ensure_ascii=False,indent=2))
    else:
        artifact=core.profile._private_file(args.artifact,'save',must_exist=True).read_bytes()
        receipt=json.loads(core.profile._private_file(args.receipt,'receipt',must_exist=True).read_text(encoding='utf-8'))
        if args.action=='audit-export':result=audit_export(source,artifact,rom,receipt)
        elif receipt.get('schema')=='e5-v022-recipe-1':result=check_cycle1_return(source,artifact,rom,receipt)
        else:result=check_cycle2_return(source,artifact,rom,receipt)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
