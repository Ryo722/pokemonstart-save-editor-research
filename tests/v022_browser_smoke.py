"""Optional real Chromium proof: private upload -> verified download, no traces.

Start pokemonstart_v022_web.py separately. Install Playwright in an isolated
test environment and its Chromium headless shell; neither is a product dependency.
All save inputs/outputs must remain inside the repo-external private boundary.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pokemonstart_fastlab_v022_creation as core
import pokemonstart_v022_creation_audit as audit
import pokemonstart_save_verifier as verifier
from pokemonstart_v022_web import OPERATION_LABELS


def run(url, source, rom, output_directory):
    from playwright.sync_api import sync_playwright
    parsed=urlsplit(url)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1':
        raise ValueError('browser smoke requires IPv4 loopback')
    source=core.fl2._private_file(source,'browser source',must_exist=True)
    output_directory=core.fl2._private_file(output_directory,'browser outputs',must_exist=False)
    if not output_directory.is_dir():raise ValueError('output directory must exist')
    rom_hash=core.fl2._check_rom_file(rom)
    raw=source.read_bytes()
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,downloads_path=str(output_directory))
        try:
            context=browser.new_context(accept_downloads=True)
            context.route('**/*',lambda route:route.continue_()
                          if urlsplit(route.request.url).hostname=='127.0.0.1' else route.abort())
            page=context.new_page()
            for operation in core.CREATION_OPERATIONS:
                page.goto(url,wait_until='networkidle')
                page.locator('input[type=file]').set_input_files(str(source))
                page.get_by_text('SUPPORTED',exact=False).first.wait_for()
                page.get_by_role('combobox').click()
                page.get_by_role('option',name=OPERATION_LABELS.get(operation,operation),exact=True).click()
                page.get_by_role('button',name='プレビュー',exact=True).click()
                page.get_by_text('PREVIEW — 元の save は変更していません。',exact=True).wait_for()
                if operation=='party_append_inventory_insert':
                    visible=page.locator('body').inner_text()
                    for marker in ('"party_append": {','"inventory_insert": {',
                                   '"append_slot": 3','"item_id": 14','"money_unchanged": true'):
                        if marker not in visible:raise ValueError('combined semantic preview incomplete')
                page.get_by_role('button',name='検証済み出力を作成',exact=True).click()
                page.get_by_text('GENERATED — verified SHA-256:',exact=False).wait_for()
                with page.expect_download() as download:
                    page.get_by_role('button',name='検証済み .sav を保存',exact=True).click()
                output=Path(download.value.path()).read_bytes()
                expected,receipt=core.derive_bytes(raw,rom_hash,operation,{})
                if output!=expected or source.read_bytes()!=raw:
                    raise ValueError('browser/core inequality or source mutation')
                verifier.verify_bytes(output)
                destination=output_directory/(operation+'-verified.sav')
                with destination.open('xb') as handle:handle.write(output)
                destination.chmod(0o400)
                results.append(dict(operation=operation,source_sha256=audit.sha(raw),
                                    output_sha256=audit.sha(output),real_browser=True,
                                    browser_version=browser.version,
                                    core_equality=True,independent_audit=receipt['independent_audit'],
                                    combined_semantic_preview_checked=operation=='party_append_inventory_insert',
                                    verifier_accepted=True,source_immutable=True))
        finally:
            browser.close()
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output-directory',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    report=run(args.url,args.source,args.rom,args.output_directory)
    if args.report.suffix!='.json':raise ValueError('report must be a new JSON file')
    with args.report.open('x',encoding='utf-8') as handle:
        handle.write(json.dumps(report,indent=2)+'\n')
    print('Real browser smoke PASS:',len(report),'operations; sanitized report only.')


if __name__=='__main__':main()
