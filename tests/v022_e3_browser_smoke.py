"""Exact candidate GUI smoke, loopback only; no gameplay or emulator interaction."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pokemonstart_v022_product_acceptance as acceptance


def run(url, source, rom, directory, screenshot=None):
    from playwright.sync_api import sync_playwright, expect
    core=acceptance.core
    if urlsplit(url).scheme!='http' or urlsplit(url).hostname!='127.0.0.1':
        raise ValueError('loopback URL required')
    source=core.profile._private_file(source,'source',must_exist=True)
    rom=core.profile._private_file(rom,'ROM',must_exist=True)
    directory=directory.resolve(strict=True)
    if not directory.is_dir() or not directory.is_relative_to(core.profile.PRIVATE_ROOT):
        raise ValueError('existing private directory required')
    raw,rom_bytes=source.read_bytes(),rom.read_bytes()
    packet=acceptance.prepare_e3(raw,rom_bytes)
    request=packet['transaction']['request']
    expected,transaction=core.derive(raw,core.profile.sha(rom_bytes),request,rom_bytes=rom_bytes)
    inspection=core.inspect(raw,core.profile.sha(rom_bytes),rom_bytes=rom_bytes)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,downloads_path=str(directory))
        try:
            context=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':1000})
            context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page();page.set_default_timeout(20000)
            page.goto(url,wait_until='networkidle')
            page.locator('input[type=file]').set_input_files(str(source))
            page.get_by_text('読み込み済み',exact=False).wait_for()
            def choose(control,label):
                control.click();control.fill(label)
                page.get_by_role('option',name=label,exact=True).click()
            for edit in request['party']:
                mon=inspection['party'][edit['slot']];changes=edit['changes']
                header=f"Party #{mon['slot']+1} — {mon['species_name']} • Lv.{mon['level']} • HP {mon['cached_stats'][0]}/{mon['cached_stats'][1]}"
                card=page.locator('.q-expansion-item').filter(has=page.get_by_text(header,exact=True))
                if not card.locator('.q-expansion-item__content').is_visible():
                    page.get_by_text(header,exact=True).click()
                for field,label in (('species','Species'),('effective_nature','Effective nature'),('held_item','Held item'),('ability','Ability')):
                    if field not in changes:continue
                    value=changes[field]
                    if field=='species':name=mon['options']['species'][value]
                    elif field=='effective_nature':
                        from pokemonstart_v022_party_model import NATURE_NAMES
                        name=NATURE_NAMES[value]
                    elif field=='held_item':name=mon['options']['held_item'][value]
                    else:
                        choices=mon['options']['abilities'][changes.get('species',mon['species'])]
                        index=choices.index(value)
                        name=f"{('通常特性 1','通常特性 2','隠れ特性')[index]} (#{value})"
                    choose(card.get_by_label(label,exact=True),name)
                for field,label in (('level','Level'),('experience','EXP'),('friendship',f"Friendship — Party #{mon['slot']+1}")):
                    if field in changes:card.get_by_label(label,exact=True).fill(str(changes[field]))
                for field in ('ivs','evs'):
                    if field not in changes:continue
                    for index,name in enumerate(('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')):
                        card.get_by_label(f'{name} {field.upper()}',exact=True).fill(str(changes[field][index]))
                for field,prefix in (('moves','Move'),('pp','PP'),('pp_up','PP-Up')):
                    for index,value in changes.get(field,{}).items():
                        control=card.get_by_label(f'{prefix} {index+1}',exact=True)
                        if field=='moves':choose(control,mon['options']['moves'][value])
                        else:control.fill(str(value))
            page.get_by_role('tab',name='Trainer',exact=True).click()
            page.get_by_label('Money',exact=True).fill(str(request['money']))
            page.get_by_role('tab',name='Items',exact=True).click()
            for operation in request['items']:
                name=inspection['items']['supported_names'][operation['item_id']]
                page.get_by_label('Quantity — '+name,exact=True).fill(str(operation['quantity']))
            page.get_by_role('button',name='Preview',exact=True).click()
            page.get_by_text('プレビューを確認して出力を作成してください。',exact=True).wait_for()
            visible=page.locator('body').inner_text()
            for line in transaction['semantic_diff']:
                if line not in visible:raise ValueError('GUI semantic preview differs from grouped recipe')
            if screenshot:
                page.get_by_role('tab',name='Party',exact=True).click()
                page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
            page.get_by_role('button',name='検証して別 save を生成',exact=True).click()
            page.get_by_text('検証済みの別 save を生成しました。',exact=True).wait_for()
            with page.expect_download() as download:
                page.get_by_role('button',name='検証済み .sav を保存',exact=True).click()
            exported=Path(download.value.path()).read_bytes()
            if exported!=expected:raise ValueError('GUI export differs from independently reconstructed candidate')
            destination=directory/'E3_GROUPED_GUI_VERIFIED.sav'
            with destination.open('xb') as handle:handle.write(exported)
            destination.chmod(0o400)
            page.get_by_role('tab',name='Trainer',exact=True).click()
            page.get_by_label('Money',exact=True).fill('42');page.get_by_label('Money',exact=True).press('Tab')
            expect(page.get_by_role('button',name='検証済み .sav を保存',exact=True)).to_be_disabled()
            if source.read_bytes()!=raw or rom.read_bytes()!=rom_bytes:raise ValueError('private source mutation')
            return {'source_sha256':core.profile.sha(raw),'rom_sha256':core.profile.sha(rom_bytes),
                    'output_sha256':core.profile.sha(exported),'browser_version':browser.version,
                    'semantic_preview_equal':True,'independent_complete_output_equal':True,
                    'stale_controls_rejected':True,'sources_immutable':True,'loopback_only':True,
                    'gameplay_acceptance':False}
        finally:browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--screenshot',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.url,args.source,args.rom,args.directory,args.screenshot),indent=2))
