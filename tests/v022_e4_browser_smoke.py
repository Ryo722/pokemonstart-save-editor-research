"""Real loopback Chromium grouped creation; private downloads, no traces."""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pokemonstart_v022_creation_acceptance as acceptance


def run(url,source,rom):
    from playwright.sync_api import sync_playwright,expect
    core=acceptance.core
    if urlsplit(url).scheme!='http' or urlsplit(url).hostname!='127.0.0.1':raise ValueError('loopback URL required')
    source=core.profile._private_file(source,'source',must_exist=True)
    rom=core.profile._private_file(rom,'ROM',must_exist=True)
    raw,rom_bytes=source.read_bytes(),rom.read_bytes()
    packet=acceptance.prepare(raw,rom_bytes);request=packet['transaction']['request']
    output,transaction=core.derive(raw,core.profile.sha(rom_bytes),request,rom_bytes=rom_bytes)
    inspection=core.inspect(raw,core.profile.sha(rom_bytes),rom_bytes=rom_bytes)
    options=inspection['creator']['options'];count=len(inspection['party'])
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            context=browser.new_context(accept_downloads=True)
            context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page();page.set_default_timeout(20000)
            page.goto(url,wait_until='networkidle');page.locator('input[type=file]').set_input_files(str(source))
            page.get_by_text('読み込み済み',exact=False).wait_for()
            def choose(control,name):
                if control.input_value()==name:return
                control.click();control.fill(name)
                page.get_by_role('option',name=name,exact=True).last.click()
                expect(control).to_have_value(name)
            for index,creation in enumerate(request['create']):
                slot=count+index+1;header=f'Party #{slot} — Empty'
                page.get_by_text(header,exact=True).click()
                card=page.locator('.q-expansion-item').filter(has=page.get_by_text(header,exact=True))
                card.get_by_text(f'Create Pokémon — Party #{slot}',exact=True).click()
                choose(card.get_by_label(f'Create Species — Party #{slot}',exact=True),options['species'][creation['species']])
                card.get_by_label(f'Create Level — Party #{slot}',exact=True).fill(str(creation['level']))
                from pokemonstart_v022_party_model import NATURE_NAMES
                choose(card.get_by_label('Create Nature',exact=True),NATURE_NAMES[creation['nature']])
                choices=options['abilities'][creation['species']][:2]
                ability_index=choices.index(creation['ability'])
                choose(card.get_by_label('Create Ability',exact=True),f'通常特性 {ability_index+1} (#{creation["ability"]})')
                choose(card.get_by_label('Create Held item',exact=True),options['held_item'][creation['held_item']])
                card.get_by_label('Create Friendship',exact=True).fill(str(creation['friendship']))
                for field in ('ivs','evs'):
                    for j,name in enumerate(('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')):
                        card.get_by_label(f'Create {name} {field.upper()}',exact=True).fill(str(creation[field][j]))
                for j,move in enumerate(creation['moves']):
                    choose(card.get_by_label(f'Create Move {j+1}',exact=True),options['moves'][move])
            page.get_by_role('button',name='Preview',exact=True).click()
            page.get_by_text('プレビューを確認して出力を作成してください。',exact=True).wait_for()
            visible=page.locator('body').inner_text()
            if any(line not in visible for line in transaction['semantic_diff']):raise ValueError('creation semantic preview inequality')
            page.get_by_role('button',name='検証して別 save を生成',exact=True).click()
            page.get_by_text('検証済みの別 save を生成しました。',exact=True).wait_for()
            with page.expect_download() as download:page.get_by_role('button',name='検証済み .sav を保存',exact=True).click()
            actual=Path(download.value.path()).read_bytes()
            if actual!=output:raise ValueError('real Chromium creation export/core inequality')
            page.get_by_label(f'Create Level — Party #{count+1}',exact=True).fill('4')
            page.get_by_label(f'Create Level — Party #{count+1}',exact=True).press('Tab')
            expect(page.get_by_role('button',name='検証済み .sav を保存',exact=True)).to_be_disabled()
            # Reopen the actual downloaded artifact; no private persistence or
            # gameplay is needed to check the full-Party creator rejection.
            page.reload(wait_until='networkidle')
            page.locator('input[type=file]').set_input_files({'name':'E4_GROUPED_GUI_VERIFIED.sav','mimeType':'application/octet-stream','buffer':actual})
            page.get_by_text('Create Pokémon 非対応: Party is full; Box creation is not supported',exact=True).wait_for()
            if source.read_bytes()!=raw or rom.read_bytes()!=rom_bytes:raise ValueError('source inputs changed')
            return {'rom_sha256':core.profile.sha(rom_bytes),'source_sha256':core.profile.sha(raw),
                    'output_sha256':core.profile.sha(actual),'browser_version':browser.version,
                    'created_count':len(request['create']),'semantic_preview_equal':True,
                    'independent_full_output_equal':True,'sources_immutable':True,'loopback_only':True,
                    'stale_controls_rejected':True,'download_reopened_full_Party_rejected':True,
                    'gameplay_acceptance':False}
        finally:browser.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--rom',type=Path,required=True)
    args=p.parse_args();print(json.dumps(run(args.url,args.source,args.rom),indent=2))
