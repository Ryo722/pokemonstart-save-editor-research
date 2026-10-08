"""Actual Chromium E5 transaction over the loopback GUI; no game interaction."""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pokemonstart_v022_e5_acceptance as acceptance
import pokemonstart_v022_party_model as party_model


def run(url,source,rom,receipt_path,directory):
    from playwright.sync_api import sync_playwright,expect
    core=acceptance.core
    if urlsplit(url).scheme!='http' or urlsplit(url).hostname!='127.0.0.1':
        raise ValueError('only loopback browser smoke is supported')
    source=core.profile._private_file(source,'source',must_exist=True)
    rom=core.profile._private_file(rom,'ROM',must_exist=True)
    receipt_path=core.profile._private_file(receipt_path,'receipt',must_exist=True)
    directory=directory.resolve(strict=True)
    if not directory.is_dir() or not directory.is_relative_to(core.profile.PRIVATE_ROOT):
        raise ValueError('download directory must be inside the private workspace')
    raw,rom_bytes=source.read_bytes(),rom.read_bytes()
    receipt=acceptance._restore_receipt(json.loads(receipt_path.read_text(encoding='utf-8')))
    packet=acceptance.audit_export(raw,core.derive(raw,core.profile.sha(rom_bytes),
         receipt['transaction']['request'],rom_bytes=rom_bytes)[0],rom_bytes,receipt)
    request=receipt['transaction']['request']
    expected,transaction=core.derive(raw,core.profile.sha(rom_bytes),request,rom_bytes=rom_bytes)
    inspection=core.inspect(raw,core.profile.sha(rom_bytes),rom_bytes=rom_bytes)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,channel='chrome',downloads_path=str(directory))
        try:
            context=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':1000})
            context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page();page.set_default_timeout(20000)
            page.goto(url,wait_until='networkidle')
            page.locator('input[type=file]').set_input_files(str(source))
            page.get_by_text('読み込み済み',exact=False).wait_for()

            def choose(control,label):
                if control.input_value()==label:return
                control.click();control.fill(label)
                page.get_by_role('option',name=label,exact=True).last.click()
                expect(control).to_have_value(label)

            for edit in request.get('party',[]):
                mon=inspection['party'][edit['slot']];changes=edit['changes']
                header=(f"Party #{mon['slot']+1} — {mon.get('species_name') or 'Species'} • "
                        f"Lv.{mon['level']} • HP {mon['cached_stats'][0]}/{mon['cached_stats'][1]}")
                card=page.locator('.q-expansion-item').filter(has=page.get_by_text(header,exact=True))
                if not card.locator('.q-expansion-item__content').is_visible():page.get_by_text(header,exact=True).click()
                if 'friendship' in changes:
                    card.get_by_label(f"Friendship — Party #{edit['slot']+1}",exact=True).fill(str(changes['friendship']))
                for field in ('ivs','evs'):
                    for index,name in enumerate(('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')):
                        if field in changes:card.get_by_label(f'{name} {field.upper()}',exact=True).fill(str(changes[field][index]))
                for raw_index,move in changes.get('moves',{}).items():
                    index=int(raw_index)
                    choose(card.get_by_label(f'Move {index+1}',exact=True),mon['options']['moves'][move])
            if 'create' in request:
                options=inspection['creator']['options'];count=len(inspection['party'])
                for index,creation in enumerate(request['create']):
                    slot=count+index+1;header=f'Party #{slot} — Empty'
                    page.get_by_text(header,exact=True).click()
                    card=page.locator('.q-expansion-item').filter(has=page.get_by_text(header,exact=True))
                    card.get_by_text(f'Create Pokémon — Party #{slot}',exact=True).click()
                    choose(card.get_by_label(f'Create Species — Party #{slot}',exact=True),options['species'][creation['species']])
                    card.get_by_label(f'Create Level — Party #{slot}',exact=True).fill(str(creation['level']))
                    choose(card.get_by_label('Create Nature',exact=True),party_model.NATURE_NAMES[creation['nature']])
                    ability_index=options['abilities'][creation['species']][:2].index(creation['ability'])
                    choose(card.get_by_label('Create Ability',exact=True),f'通常特性 {ability_index+1} (#{creation["ability"]})')
                    choose(card.get_by_label('Create Held item',exact=True),options['held_item'][creation['held_item']])
                    card.get_by_label('Create Friendship',exact=True).fill(str(creation['friendship']))
                    for field in ('ivs','evs'):
                        for j,name in enumerate(('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')):
                            card.get_by_label(f'Create {name} {field.upper()}',exact=True).fill(str(creation[field][j]))
                    for j,move in enumerate(creation['moves']):
                        choose(card.get_by_label(f'Create Move {j+1}',exact=True),options['moves'][move])
            if 'money' in request:
                page.get_by_role('tab',name='Trainer',exact=True).click()
                page.get_by_label('Money',exact=True).fill(str(request['money']))
            if 'items' in request:
                page.get_by_role('tab',name='Items',exact=True).click()
                supported=inspection['items']['supported_names']
                for operation in request['items']:
                    name=supported[operation['item_id']]
                    if operation['op']=='set':
                        page.get_by_label(f'Quantity — {name}',exact=True).fill(str(operation['quantity']))
                    elif operation['op']=='remove':
                        page.get_by_text(f'Remove — {name}',exact=True).click()
                    else:
                        page.get_by_text('Add Item',exact=True).click()
                        choose(page.get_by_label('Item',exact=True),name)
                        page.get_by_label('Quantity — Add Item',exact=True).fill(str(operation['quantity']))
            page.get_by_role('button',name='Preview',exact=True).click()
            page.get_by_text('プレビューを確認して出力を作成してください。',exact=True).wait_for()
            body=page.locator('body').inner_text()
            if any(line not in body for line in transaction['semantic_diff']):
                raise ValueError('semantic preview differs from independent transaction')
            headings=[]
            if 'party' in request:headings.append('Party')
            if 'create' in request:headings.append('Created Pokémon')
            if 'items' in request:headings.append('Items')
            if 'money' in request:headings.append('Trainer')
            if any(heading not in body for heading in headings):
                raise ValueError('semantic family heading missing')
            page.get_by_role('button',name='検証して別 save を生成',exact=True).click()
            page.get_by_text('検証済みの別 save を生成しました。',exact=True).wait_for()
            with page.expect_download() as download:
                page.get_by_role('button',name='検証済み .sav を保存',exact=True).click()
            actual=Path(download.value.path()).read_bytes()
            if actual!=expected:raise ValueError('actual Chromium output differs from core oracle')
            audit=acceptance.audit_export(raw,actual,rom_bytes,receipt)
            destination=directory/('E5_CYCLE1_GUI.sav' if 'create' in request else 'E5_CYCLE2_GUI.sav')
            with destination.open('xb') as handle:handle.write(actual)
            destination.chmod(0o400)
            if 'money' in request:
                page.get_by_role('tab',name='Trainer',exact=True).click()
                control=page.get_by_label('Money',exact=True);control.fill('42');control.press('Tab')
                expect(page.get_by_role('button',name='検証済み .sav を保存',exact=True)).to_be_disabled()
            if source.read_bytes()!=raw or rom.read_bytes()!=rom_bytes:
                raise ValueError('source save or ROM changed during browser smoke')
            core.v.verify_bytes(actual)
            return {'status':'REAL_CHROMIUM_GUI_CORE_AUDIT_EQUAL','browser_version':browser.version,
                    'cycle':1 if 'create' in request else 2,'source_sha256':core.profile.sha(raw),
                    'rom_sha256':core.profile.sha(rom_bytes),'output_sha256':core.profile.sha(actual),
                    'semantic_preview_equal':True,'independent_audit':audit['complete_output_equal'],
                    'source_rom_immutable':True,'stale_preview_rejected':True,
                    'loopback_only':True,'gameplay_acceptance':False}
        finally:browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True);parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.url,args.source,args.rom,args.receipt,args.directory),ensure_ascii=False,indent=2))
