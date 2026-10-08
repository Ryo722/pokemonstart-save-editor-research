"""Actual GUI full-Party E4 rejection using an in-memory private fixture."""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pokemonstart_v022_product_core as core


def run(url,source,rom):
    from playwright.sync_api import sync_playwright
    if urlsplit(url).scheme!='http' or urlsplit(url).hostname!='127.0.0.1':
        raise ValueError('only loopback browser smoke is supported')
    source=core.profile._private_file(source,'source',must_exist=True)
    rom=core.profile._private_file(rom,'ROM',must_exist=True)
    raw,rom_bytes=source.read_bytes(),rom.read_bytes();digest=core.profile.sha(rom_bytes)
    inspection=core.inspect(raw,digest,rom_bytes=rom_bytes)
    if len(inspection['party'])!=5 or not inspection['creator'].get('eligible'):
        raise ValueError('full-Party smoke requires the privately verified Cycle 1 five-member output')
    options=inspection['creator']['options'];species=1 if 1 in options['species'] else next(iter(options['species']))
    ability=next(x for x in options['abilities'][species][:2] if x)
    move=33 if 33 in options['moves'] else next(x for x in options['moves'] if x)
    create={'species':species,'level':3,'nature':0,
            'friendship':inspection['creator']['friendship_defaults'][species],
            'ability':ability,'held_item':0,'ivs':[0]*6,'evs':[0]*6,'moves':[move,0,0,0]}
    full,receipt=core.derive(raw,digest,{'create':[create]},rom_bytes=rom_bytes)
    if core.v.verify_bytes(full).party_count!=6 or not receipt['independent_e4_audit']['complete_output_equal']:
        raise ValueError('in-memory full-Party fixture failed independent E4 reconstruction')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,channel='chrome')
        try:
            context=browser.new_context(viewport={'width':1440,'height':1000})
            context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page();page.set_default_timeout(20000)
            page.goto(url,wait_until='networkidle')
            page.locator('input[type=file]').set_input_files({'name':'private-full-party.sav',
                 'mimeType':'application/octet-stream','buffer':full})
            page.get_by_text('読み込み済み',exact=False).wait_for()
            page.get_by_text('Create Pokémon 非対応: Party is full; Box creation is not supported',exact=True).wait_for()
            if page.get_by_text('Create Pokémon — Party #',exact=False).count():
                raise ValueError('full Party exposed a creation control')
            if source.read_bytes()!=raw or rom.read_bytes()!=rom_bytes:
                raise ValueError('full-Party GUI check changed source or ROM')
            return {'status':'REAL_CHROMIUM_FULL_PARTY_BOX_REJECTION','browser_version':browser.version,
                    'party_count':6,'independent_full_output_audit':True,
                    'explicit_box_not_supported':True,'create_control_absent':True,
                    'source_rom_immutable':True,'loopback_only':True,'gameplay_acceptance':False}
        finally:browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(args.url,args.source,args.rom),ensure_ascii=False,indent=2))
