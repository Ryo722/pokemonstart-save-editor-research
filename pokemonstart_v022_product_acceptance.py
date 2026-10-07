"""Read-only prepare/return/progress harness. Metadata never proves Human gameplay."""
from __future__ import annotations
import argparse
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


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=core.profile.ROM_DEFAULT)
    sub=parser.add_subparsers(dest='action',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('source',type=Path);prep.add_argument('--cycle',type=int,default=1)
    returned=sub.add_parser('check-return');returned.add_argument('source',type=Path)
    returned.add_argument('returned',type=Path);returned.add_argument('receipt',type=Path)
    progress=sub.add_parser('check-progress');progress.add_argument('previous',type=Path);progress.add_argument('progressed',type=Path)
    args=parser.parse_args(argv)
    rom=core.profile._check_rom_file(args.rom)
    def read(path):return core.profile._private_file(path,'save',must_exist=True).read_bytes()
    if args.action=='prepare':report=prepare(read(args.source),rom,args.cycle)
    elif args.action=='check-return':report=check_return(read(args.source),read(args.returned),rom,json.loads(args.receipt.read_text()))
    else:report=check_progress(read(args.previous),read(args.progressed),rom)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
