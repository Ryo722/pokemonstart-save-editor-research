"""One grouped E4 preparation and conservative read-only returned-save checks.

All reports require separate Human attestation and drift review. No adoption,
input writes, emulator execution or protected identity material in receipts.
"""
import argparse
import copy
import json
from pathlib import Path
import pokemonstart_v022_product_core as core
import pokemonstart_v022_party_audit as party
import pokemonstart_v022_inventory_audit as inventory


def prepare(source,rom):
    report=core.inspect(source,core.profile.sha(rom),rom_bytes=rom)
    creator=report.get('creator',{})
    if not creator.get('eligible') or creator['capacity']<2:
        raise ValueError('grouped E4 acceptance needs one eligible natural source with at least two empty Party slots')
    options=creator['options']
    requests=[{'species':1,'level':3,'nature':0,'moves':[33,45,0,0],'ivs':[0]*6,'evs':[0]*6,
               'friendship':creator['friendship_defaults'][1],'ability':options['abilities'][1][0],'held_item':0},
              {'species':19,'level':20,'nature':3,'moves':[33,39,98,0],'ivs':[31,17,9,25,0,13],'evs':[0]*6,
               'friendship':creator['friendship_defaults'][19],
               'ability':options['abilities'][19][1] or options['abilities'][19][0],'held_item':200}]
    _,transaction=core.derive(source,core.profile.sha(rom),{'create':requests},rom_bytes=rom)
    return {'schema':'e4-grouped-1','source_sha256':core.profile.sha(source),'rom_sha256':core.profile.sha(rom),
            'status':'PREPARED_NOT_GAME_ACCEPTED','transaction':transaction,'gameplay_acceptance':False}


def check_return(source,returned,rom,receipt):
    serialized=lambda x:json.loads(json.dumps(x))
    if serialized(receipt)!=serialized(prepare(source,rom)):
        raise ValueError('E4 receipt differs from independently audited grouped source recipe')
    output,transaction=core.derive(source,core.profile.sha(rom),copy.deepcopy(receipt['transaction']['request']),rom_bytes=rom)
    before=party.structure.parse(output);after=party.structure.parse(returned)
    old=before['slots'][before['active']];new=after['slots'][after['active']]
    if (len(output)!=len(returned) or after['active']==before['active'] or new['counter']!=old['counter']+1
            or before['count']!=after['count']):
        raise ValueError('E4 requires one normal SAVE with unchanged created Party count')
    prior=before['active']*14*4096
    if output[prior:prior+14*4096]!=returned[prior:prior+14*4096]:
        raise ValueError('previous active save slot changed')
    for sid in range(14):
        if new['positions'][sid]%14!=(old['positions'][sid]%14+1)%14:
            raise ValueError('normal SAVE section rotation mismatch')
    expected=party.inspect(output,rom);actual=party.inspect(returned,rom)
    if actual['saved_context']['flag_0x930']:
        raise ValueError('returned facility context unsupported')
    initial_count=party.structure.parse(source)['count']
    allowed={*range(34,40),41,*range(52,62),*range(80,85),*range(86,100)}
    drifts=[]
    for slot,(left,right) in enumerate(zip(before['records'],after['records'])):
        if party.ordinary_reasons(right,rom,actual['saved_context']):
            raise ValueError('returned Party ordinary reconstruction failed')
        offsets=[i for i,(x,y) in enumerate(zip(left,right)) if x!=y]
        if not set(offsets)<=allowed:
            raise ValueError('unexplained identity/move/IV/origin/opaque Party coupling change')
        a,b=expected['party'][slot],actual['party'][slot]
        if a['held_item']!=b['held_item'] and not (a['held_item'] in (139,142) and b['held_item']==0):
            raise ValueError('unexplained held item change')
        if b['experience']<a['experience'] or any(x<y for x,y in zip(b['evs'],a['evs'])):
            raise ValueError('unexplained EXP/EV decrease')
        if not offsets and left!=right:raise ValueError('record comparison ambiguity')
        for field in ('held_item','experience','stored_level','friendship','evs','cached_hp_stats','moves'):
            if a[field]!=b[field]:
                drifts.append({'slot':slot,'created':slot>=initial_count,'field':field,'before':a[field],'after':b[field]})
        if left[80:84]!=right[80:84]:
            drifts.append({'slot':slot,'created':slot>=initial_count,'field':'status',
                           'before':int.from_bytes(left[80:84],'little'),'after':int.from_bytes(right[80:84],'little')})
    if before['money']!=after['money']:
        raise ValueError('Money regression state changed')
    a,b=inventory.restricted(output,rom),inventory.restricted(returned,rom)
    if [p['entries'] for p in a['pockets']]!=[p['entries'] for p in b['pockets']]:
        raise ValueError('Inventory regression state changed')
    # Complete input/output record equality applies before gameplay; after
    # gameplay each invariant byte remains exact and allowed drift is exposed.
    inspection=core.inspect(returned,core.profile.sha(rom),rom_bytes=rom)
    creator=inspection['creator']
    full=after['count']==6
    if full:
        try:core.derive(returned,core.profile.sha(rom),{'create':[receipt['transaction']['request']['create'][0]]},rom_bytes=rom)
        except ValueError as exc:
            if 'Box' not in str(exc):raise ValueError('full Party did not reject with Box reason') from exc
        else:raise ValueError('full Party incorrectly accepted creation')
    elif creator.get('eligible'):
        _,later=core.derive(returned,core.profile.sha(rom),{'create':[receipt['transaction']['request']['create'][0]]},rom_bytes=rom)
        if not later['independent_e4_audit']['complete_output_equal']:raise ValueError('subsequent creator audit failed')
    else:raise ValueError('subsequent creator eligibility lost: '+creator.get('reason','unknown'))
    return {'status':'MACHINE_RETURN_PASS_HUMAN_ATTESTATION_AND_DRIFT_REVIEW_REQUIRED',
            'returned_sha256':core.profile.sha(returned),'counter':[old['counter'],new['counter']],
            'previous_active_preserved':True,'normal_section_rotation':True,'created_semantic_invariants_persist':True,
            'reported_gameplay_drifts':drifts,'money_inventory_regression_equal':True,
            'editor_output_complete_audit':transaction['independent_e4_audit'],
            'returned_independent_reconstruction':True,'subsequent_creator_eligible':not full,
            'full_party_Box_rejection_checked':full,'emulator_footer_changed':output[0x20000:]!=returned[0x20000:],
            'gameplay_acceptance':False,'e4_adopted':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,default=core.profile.ROM_DEFAULT)
    p.add_argument('action',choices=('prepare','check-return'));p.add_argument('source',type=Path)
    p.add_argument('--returned',type=Path);p.add_argument('--receipt',type=Path);args=p.parse_args()
    def read(path):return core.profile._private_file(path,'private input',must_exist=True).read_bytes()
    rom=read(args.rom);source=read(args.source)
    if args.action=='prepare':result=prepare(source,rom)
    else:
        if args.returned is None or args.receipt is None:p.error('check-return requires --returned and --receipt')
        result=check_return(source,read(args.returned),rom,json.loads(read(args.receipt)))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
