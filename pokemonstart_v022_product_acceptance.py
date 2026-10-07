"""Read-only prepare/return/progress harness. Metadata never proves Human gameplay."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import pokemonstart_v022_product_core as core


def prepare(raw, rom_sha256, cycle):
    if type(cycle) is not int or cycle not in (1,2):raise ValueError('cycle must be 1 or 2')
    report=core.inspect(raw,rom_sha256)
    if not report['money'] or not report['items'] or not report['party']:
        raise ValueError('acceptance recipe requires independently eligible Money, Party, Items')
    slot=next((p['slot'] for p in report['party'] if p['capabilities'].get('friendship')),None)
    if slot is None:raise ValueError('no ordinary Party member supports friendship')
    target_money=1234567 if cycle==1 else 7654321
    if report['money']['money']==target_money:target_money=7654321 if cycle==1 else 1234567
    target_friendship=180 if cycle==1 else 181
    if report['party'][slot]['friendship']==target_friendship:target_friendship=182
    quantity=3 if report['items']['entries'][0]['quantity']!=3 else 2
    request={'money':target_money,'party':[{'slot':slot,'changes':{'friendship':target_friendship}}],
             'items':{'potion_quantity':quantity}}
    _,transaction=core.derive(raw,rom_sha256,request)
    return {'schema':1,'cycle':cycle,'rom_sha256':rom_sha256,'transaction':transaction,
            'status':'PREPARED_NOT_GAME_ACCEPTED',
            'human_actions':['Open the immutable source snapshot in the product GUI.',
                             *transaction['semantic_diff'],
                             'Preview, generate, download a separate verified .sav.',
                             'Load only a disposable copy with the exact v0.22 ROM in mGBA.',
                             'Confirm edited values in game, then normal SAVE.',
                             'Close/flush mGBA; preserve this first returned save separately.',
                             'Cycle 1 only: ordinary gameplay progress, normal SAVE, preserve a second snapshot.',
                             'Cycle 2: normal SAVE, preserve returned snapshot; report observed actions.']}


def check_return(source, returned, rom_sha256, receipt):
    if (not isinstance(receipt,dict) or receipt.get('schema')!=1
            or receipt.get('rom_sha256')!=rom_sha256 or receipt.get('cycle') not in (1,2)):
        raise ValueError('receipt schema/profile/cycle mismatch')
    export,transaction=core.derive(source,rom_sha256,receipt['transaction']['request'])
    if transaction!=receipt['transaction']:raise ValueError('source/receipt mismatch or tampered receipt')
    before=core.v.verify_bytes(export);after=core.v.verify_bytes(returned)
    old=before.slots[before.active_slot];new=after.slots[after.active_slot]
    if (len(export)!=len(returned) or after.active_slot!=1-before.active_slot
            or old.counter is None or new.counter!=old.counter+1):
        raise ValueError('expected exactly one normal SAVE slot/counter transition')
    start=before.active_slot*14*4096;end=start+14*4096
    if export[start:end]!=returned[start:end]:raise ValueError('previous active export slot not preserved')
    for logical in range(14):
        if new.section(logical).physical_sector%14!=(old.section(logical).physical_sector%14+1)%14:
            raise ValueError('normal SAVE logical-section rotation mismatch')
    expected_money=receipt['transaction']['request']['money']
    if core.money.inspect(returned,rom_sha256)['money']!=expected_money:
        raise ValueError('returned Money differs from preview')
    for edit in receipt['transaction']['request']['party']:
        expected=receipt['transaction']['families'][f"party_{edit['slot']}"]['after']
        actual=core.party.existing._semantic(after.party[edit['slot']])
        fields=set(edit['changes'])
        if fields & core.party.STAT_FIELDS:fields.update(('species','level','experience','ivs','evs','cached_stats'))
        if 'moves' in fields:fields.update(('pp','pp_bonuses'))
        if any(actual[field]!=expected[field] for field in fields):
            raise ValueError('returned requested/coupled Party semantics differ from preview')
    if core.items.inspect(returned,rom_sha256)!=core.items.inspect(export,rom_sha256):
        raise ValueError('returned observed Items prefix differs from preview')
    return {'status':'STRUCTURAL_ROUNDTRIP_PASS_HUMAN_GAMEPLAY_ATTESTATION_REQUIRED',
            'cycle':receipt['cycle'],'export_sha256':before.file_sha256,
            'returned_sha256':after.file_sha256,'counter':[old.counter,new.counter],
            'previous_active_preserved':True,'requested_semantics_retained':True,
            'next_eligibility':core.inspect(returned,rom_sha256),
            'r4_complete':False}


def check_progress(previous_return, progressed, rom_sha256):
    before=core.v.verify_bytes(previous_return);after=core.v.verify_bytes(progressed)
    prior=before.slots[before.active_slot].counter;current=after.slots[after.active_slot].counter
    if (before.file_sha256==after.file_sha256 or prior is None or current is None or current<=prior):
        raise ValueError('progress snapshot requires a new hash and advanced SAVE counter')
    recipe=prepare(progressed,rom_sha256,2)
    return {'status':'NEW_SAVE_QUALIFIES_NOT_PROOF_OF_GAMEPLAY','previous_sha256':before.file_sha256,
            'progressed_sha256':after.file_sha256,'counter':[prior,current],
            'cycle2':recipe,'r4_complete':False}


def prepare_e3(raw, rom):
    """One grouped recipe chosen from actual eligible records, never a canary series."""
    import pokemonstart_v022_party_model as model
    digest = model.sha(rom)
    report = core.inspect(raw,digest,rom_bytes=rom)
    if not report['money'] or not report['items'] or not report['items'].get('e2'):
        raise ValueError('grouped E3 acceptance requires composed Money/E2 eligibility')
    tables = model.extract_tables(rom)
    eligible=[p for p in report['party'] if p.get('ordinary_eligibility',{}).get('eligible')]
    full=next((p for p in eligible if p['cached_stats'][0]==p['cached_stats'][1]),None)
    if full is None:raise ValueError('grouped E3 requires a full-HP specimen')
    damaged=None;lower_level=None
    for mon in sorted(eligible,key=lambda p:(p['level'],p['slot'])):
        current,oldmax=mon['cached_stats'][:2]
        if not 0<current<oldmax or mon['level']<2:continue
        level=mon['level']-1
        newmax=model.cached_stats(tables.species[mon['species']],level,tuple(mon['ivs']),tuple(mon['evs']),mon['effective_nature'],tables)[0]
        if current<=newmax<oldmax:
            damaged=mon;lower_level=level;break
    if damaged is None:raise ValueError('grouped E3 requires a naturally retained safe HP-decrease specimen')
    coverage=next((p for p in eligible if p['species'] not in (full['species'],damaged['species'])
                   and tables.species[p['species']].abilities[1]
                   and tables.species[p['species']].abilities[1]!=p['resolved_ability']
                   and len([x for x in p['moves'] if x])>=3),None)
    if coverage is None:raise ValueError('grouped E3 requires a distinct ordinary alternate-ability specimen')
    # Moderate stats on A, clean HP decrease on B, moves/ability/item on C.
    species_options=sorted(full['options']['species'])
    target_species=next((sid for sid in species_options if sid>full['species']),species_options[0])
    ivs=list(full['ivs']);ivs[0]=min(31,ivs[0]+1);ivs[1]=min(31,ivs[1]+2)
    evs=list(full['evs']);evs[3]=8 if evs[3]!=8 else 12
    if sum(evs)>510:raise ValueError('grouped moderate EV edit exceeds limit')
    empty=[i for i,move in enumerate(full['moves']) if move==0]
    if len(empty)<2:raise ValueError('grouped A requires two empty move slots')
    fill={empty[-2]:98,empty[-1]:996}
    occupied=[i for i,move in enumerate(coverage['moves']) if move]
    if len(occupied)<3:raise ValueError('grouped C requires three occupied move slots')
    first,second,last=occupied[0],occupied[1],occupied[-1]
    replacements={first:1 if coverage['moves'][first]!=1 else 33,
                  second:39 if coverage['moves'][second]!=39 else 45,last:0}
    changes_a={'species':target_species,'level':min(100,max(full['level']+3,12)),
               'ivs':ivs,'evs':evs,'effective_nature':3 if full['effective_nature']!=3 else 13,
               'friendship':200 if full['friendship']!=200 else 201,
               'moves':fill,'pp_up':{empty[-2]:2,empty[-1]:3}}
    changes_c={'moves':replacements,'pp_up':{first:0,second:1},
               'pp':{second:model.maximum_pp(replacements[second],1,tables)-1},
               'ability':tables.species[coverage['species']].abilities[1],'held_item':139}
    edits=[{'slot':full['slot'],'changes':changes_a},
           {'slot':damaged['slot'],'changes':{'level':lower_level}},
           {'slot':coverage['slot'],'changes':changes_c}]
    money=report['money']['money']
    target_money=money+137 if money<=9999862 else money-137
    item=next((row for row in report['items']['entries'] if row['editable']),None)
    if item is None:raise ValueError('grouped E3 acceptance needs an existing editable medicine')
    quantity=item['quantity']+2 if item['quantity']<=997 else item['quantity']-2
    request={'party':edits,'money':target_money,'items':[{'op':'set','item_id':item['item_id'],'quantity':quantity}]}
    _,transaction=core.derive(raw,digest,request,rom_bytes=rom)
    return {'schema':'e3-grouped-1','source_sha256':model.sha(raw),'rom_sha256':digest,
            'status':'PREPARED_NOT_GAME_ACCEPTED','gameplay_acceptance':False,
            'selected_members':[{'slot':p['slot'],'species':p['species'],'level':p['level']} for p in report['party'] if p['slot'] in {e['slot'] for e in edits}],
            'transaction':transaction}


def check_e3_return(source, returned, rom, receipt):
    """Independent normal-SAVE reconstruction and explicit gameplay drift list.

    Human attestation remains required. No live interaction, new output file,
    or automatic promotion. Ordinary HP/PP/EXP/EV/friendship progression can
    be reported; unexplained genotype, move, ability, or identity drift rejects.
    """
    import pokemonstart_v022_party_audit as audit
    import pokemonstart_v022_inventory_audit as inventory_audit
    digest=core.profile.sha(rom)
    if receipt.get('schema')!='e3-grouped-1' or receipt.get('rom_sha256')!=digest or receipt.get('source_sha256')!=core.profile.sha(source):
        raise ValueError('E3 receipt/source/ROM identity mismatch')
    receipt=copy.deepcopy(receipt)
    # JSON receipts stringify slot-map keys. Restore only the exact four
    # supported spellings, then compare with the recipe regenerated from the
    # immutable source; arbitrary/tampered acceptance recipes are not trusted.
    for edit in receipt['transaction']['request'].get('party',[]):
        for field in ('moves','pp','pp_up'):
            if field not in edit['changes']:continue
            mapping={}
            for key,value in edit['changes'][field].items():
                if type(key) is str:
                    if key not in ('0','1','2','3'):raise ValueError('E3 receipt move-slot spelling')
                    key=int(key)
                if type(key) is not int or key in mapping:raise ValueError('E3 receipt move-slot ambiguity')
                mapping[key]=value
            edit['changes'][field]=mapping
    def serialized(value):
        return json.loads(json.dumps(value))
    if serialized(prepare_e3(source,rom)['transaction'])!=serialized(receipt['transaction']):
        raise ValueError('E3 receipt differs from the dynamically regenerated grouped recipe')
    output,transaction=core.derive(source,digest,receipt['transaction']['request'],rom_bytes=rom)
    if serialized(transaction)!=serialized(receipt['transaction']):
        raise ValueError('E3 receipt does not reconstruct the complete candidate')
    before=audit.structure.parse(output);after=audit.structure.parse(returned)
    old=before['slots'][before['active']];new=after['slots'][after['active']]
    if (len(output)!=len(returned) or after['active']==before['active']
            or new['counter']!=old['counter']+1 or before['count']!=after['count']):
        raise ValueError('E3 expected exactly one normal SAVE, preserving Party count')
    prior=before['active']*14*4096
    if output[prior:prior+14*4096]!=returned[prior:prior+14*4096]:
        raise ValueError('E3 previous active slot changed')
    # Canonical normal-resave policy: the optional 16-byte emulator trailer
    # is opaque and may change after gameplay. Editor output still preserves
    # it byte-for-byte through the independent full-output audit above.
    footer={'changed':output[0x20000:]!=returned[0x20000:],
            'before_sha256':core.profile.sha(output[0x20000:]),
            'after_sha256':core.profile.sha(returned[0x20000:]),
            'semantics':'opaque emulator trailer; canonical normal-resave policy'}
    for sid in range(14):
        if new['positions'][sid]%14!=(old['positions'][sid]%14+1)%14:
            raise ValueError('E3 section rotation')
    decoded=audit.inspect(returned,rom)
    if decoded['saved_context']['flag_0x930']:
        raise ValueError('E3 returned facility context unsupported')
    drifts=[]
    baseline=audit.inspect(output,rom)
    for i,(original,record) in enumerate(zip(before['records'],after['records'])):
        if audit.ordinary_reasons(record,rom,decoded['saved_context']):
            raise ValueError('E3 returned ordinary reconstruction failed')
        current=decoded['party'][i];expected=baseline['party'][i]
        for key in ('species','moves','ivs','effective_nature','ability_selector','hidden_ability','resolved_ability','hyper_training'):
            left,right=expected[key],current[key]
            if key=='moves':left,right=[x['move_id'] for x in left],[x['move_id'] for x in right]
            if left!=right:raise ValueError('E3 persistent requested field drift: '+key)
        if original[:15]!=record[:15] or original[18:32]!=record[18:32] or original[42:44]!=record[42:44] or original[62:80]!=record[62:80] or original[85]!=record[85] or original[40]!=record[40] or original[15:18]!=record[15:18]:
            raise ValueError('E3 unexplained identity/opaque record drift')
        if expected['held_item']!=current['held_item'] and not (expected['held_item'] in (139,142) and current['held_item']==0):
            raise ValueError('E3 unexpected held-item transition')
        if current['experience']<expected['experience'] or any(x<y for x,y in zip(current['evs'],expected['evs'])):
            raise ValueError('E3 unexpected EXP/EV decrease')
        old_status=int.from_bytes(original[80:84],'little')
        new_status=int.from_bytes(record[80:84],'little')
        if old_status!=new_status:
            drifts.append({'slot':i,'field':'status','before':old_status,'after':new_status})
        for key in ('held_item','experience','stored_level','friendship','evs','cached_hp_stats','moves'):
            if expected[key]!=current[key]:drifts.append({'slot':i,'field':key,'before':expected[key],'after':current[key]})
    if after['money']!=receipt['transaction']['request']['money']:
        raise ValueError('E3 returned Money differs from preview')
    old_items=inventory_audit.restricted(output,rom);new_items=inventory_audit.restricted(returned,rom)
    if [p['entries'] for p in old_items['pockets']]!=[p['entries'] for p in new_items['pockets']]:
        raise ValueError('E3 returned inventory differs from preview')
    # Machine-only later-use check, without requesting a second gameplay canary.
    eligible=next(p for p in core.inspect(returned,digest,rom_bytes=rom)['party'] if p.get('ordinary_eligibility',{}).get('eligible'))
    _,repeat=core.derive(returned,digest,{'party':[{'slot':eligible['slot'],'changes':{'friendship':(eligible['friendship']+1)%256}}]},rom_bytes=rom)
    return {'status':'MACHINE_RECONSTRUCTION_PASS_HUMAN_ATTESTATION_AND_DRIFT_REVIEW_REQUIRED',
            'returned_sha256':core.profile.sha(returned),'counter':[old['counter'],new['counter']],
            'previous_active_preserved':True,'emulator_footer':footer,'independent_ordinary_reconstruction':True,
            'reported_gameplay_drifts':drifts,'later_edit_reconstructed':repeat['independent_e3_audit']['complete_output_equal'],
            'gameplay_acceptance':False,'e3_adopted':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=core.profile.ROM_DEFAULT)
    sub=parser.add_subparsers(dest='action',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('source',type=Path);prep.add_argument('--cycle',type=int,default=1)
    returned=sub.add_parser('check-return');returned.add_argument('source',type=Path)
    returned.add_argument('returned',type=Path);returned.add_argument('receipt',type=Path)
    progress=sub.add_parser('check-progress');progress.add_argument('previous',type=Path);progress.add_argument('progressed',type=Path)
    e3=sub.add_parser('prepare-e3');e3.add_argument('source',type=Path)
    e3return=sub.add_parser('check-e3-return');e3return.add_argument('source',type=Path)
    e3return.add_argument('returned',type=Path);e3return.add_argument('receipt',type=Path)
    args=parser.parse_args(argv)
    rom=core.profile._check_rom_file(args.rom)
    def read(path):return core.profile._private_file(path,'save',must_exist=True).read_bytes()
    if args.action=='prepare':report=prepare(read(args.source),rom,args.cycle)
    elif args.action=='check-return':report=check_return(read(args.source),read(args.returned),rom,json.loads(args.receipt.read_text()))
    elif args.action=='prepare-e3':report=prepare_e3(read(args.source),args.rom.read_bytes())
    elif args.action=='check-e3-return':report=check_e3_return(read(args.source),read(args.returned),args.rom.read_bytes(),json.loads(core.profile._private_file(args.receipt,'receipt',must_exist=True).read_text()))
    else:report=check_progress(read(args.previous),read(args.progressed),rom)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
