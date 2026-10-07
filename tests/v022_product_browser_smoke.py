"""Optional real Chromium acceptance: loopback only, private downloads, no traces."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pokemonstart_v022_product_acceptance as acceptance


def run(url,source,rom,output_directory):
    from playwright.sync_api import sync_playwright, expect
    core=acceptance.core
    if urlsplit(url).scheme!='http' or urlsplit(url).hostname!='127.0.0.1':
        raise ValueError('only loopback browser smoke is supported')
    source=core.profile._private_file(source,'source',must_exist=True)
    output_directory=core.profile._private_file(output_directory,'downloads',must_exist=False)
    if not output_directory.is_dir():raise ValueError('downloads directory must exist')
    raw=source.read_bytes();rom_sha=core.profile._check_rom_file(rom)
    receipt=acceptance.prepare(raw,rom_sha,1);request=receipt['transaction']['request']
    expected,transaction=core.derive(raw,rom_sha,request)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,downloads_path=str(output_directory))
        try:
            context=browser.new_context(accept_downloads=True)
            context.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page()
            page.goto(url,wait_until='networkidle')
            page.locator('input[type=file]').set_input_files(str(source))
            page.get_by_text('読み込み済み',exact=False).wait_for()
            page.get_by_role('tab',name='Trainer',exact=True).click()
            page.get_by_label('Money',exact=True).fill(str(request['money']))
            page.get_by_role('tab',name='Party',exact=True).click()
            page.get_by_label('Friendship — Party #1',exact=True).fill(str(request['party'][0]['changes']['friendship']))
            page.get_by_role('tab',name='Items',exact=True).click()
            page.get_by_label('Quantity',exact=True).fill(str(request['items']['potion_quantity']))
            page.get_by_role('button',name='Preview',exact=True).click()
            page.get_by_text('プレビューを確認して出力を作成してください。',exact=True).wait_for()
            text=page.locator('body').inner_text()
            for line in transaction['semantic_diff']:
                if line not in text:raise ValueError('semantic preview missing requested edit')
            page.get_by_role('button',name='検証して別 save を生成',exact=True).click()
            page.get_by_text('検証済みの別 save を生成しました。',exact=True).wait_for()
            with page.expect_download() as download:
                page.get_by_role('button',name='検証済み .sav を保存',exact=True).click()
            output=Path(download.value.path()).read_bytes()
            if output!=expected:raise ValueError('real browser/core byte inequality')
            if source.read_bytes()!=raw or core.profile._check_rom_file(rom)!=rom_sha:
                raise ValueError('source/ROM mutation')
            destination=output_directory/'cycle1_product_verified.sav'
            with destination.open('xb') as handle:handle.write(output)
            destination.chmod(0o400)
            core.v.verify_bytes(destination.read_bytes())
            # A control edit must disable the previous download and generation.
            page.get_by_role('tab',name='Trainer',exact=True).click()
            page.get_by_label('Money',exact=True).fill('42')
            page.get_by_label('Money',exact=True).press('Tab')
            expect(page.get_by_role('button',name='検証済み .sav を保存',exact=True)).to_be_disabled(timeout=5000)
            return {'workflow':'real Chromium private GUI composed transaction','browser_version':browser.version,
                    'input_sha256':transaction['input_sha256'],'output_sha256':transaction['output_sha256'],
                    'core_equality':True,'source_immutable':True,'rom_immutable':True,
                    'verifier_accepted':True,'semantic_preview_checked':True,'stale_controls_rejected':True,
                    'semantic_diff':transaction['semantic_diff'],'game_roundtrip':False}
        finally:browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True);parser.add_argument('--output-directory',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(args.url,args.source,args.rom,args.output_directory),ensure_ascii=False,indent=2))
