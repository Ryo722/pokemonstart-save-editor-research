"""Localhost NiceGUI prototype over the exact-v0.22 Fast Lab core.

Uses the M4 in-memory upload/preview/verified-download delivery pattern, without
its v0.15 journal or eligibility model. No save filesystem write path exists.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

import pokemonstart_fastlab_v022_creation as core
import pokemonstart_save_verifier as verifier
from pokemonstart_m4_web import server_options as delivery_server_options

try:
    from nicegui import ui
except ImportError:
    ui=None


def server_options(port=8766):
    options=delivery_server_options(port)
    options['title']='PokemonStart v0.22 Fast Lab experimental'
    return options


class BrowserWorkflow:
    """One browser session; source and outputs remain immutable bytes in memory."""

    def __init__(self, rom_path):
        self.rom_path=Path(rom_path)
        self._reset()

    def _reset(self):
        self.source_raw=self.source_sha256=self.source_name=None
        self.plan=self.output_raw=self.output_name=None

    def _clear_output(self):
        self.output_raw=self.output_name=None

    def upload(self, filename, raw):
        self._reset()
        name=Path(filename).name
        if Path(name).suffix.lower()!='.sav' or not isinstance(raw,bytes):
            raise ValueError('select a local .sav file')
        if len(raw) not in (verifier.FLASH_SIZE,verifier.FLASH_SIZE+verifier.RTC_FOOTER_SIZE):
            raise ValueError('unsupported save size')
        rom_hash=core.fl2._check_rom_file(self.rom_path)
        report=core.inspect_bytes(raw,rom_hash)
        self.source_raw,self.source_sha256,self.source_name=raw,core.fl2.sha(raw),name
        return report

    def _derive(self, operation, changes):
        if self.source_raw is None or core.fl2.sha(self.source_raw)!=self.source_sha256:
            raise ValueError('missing or stale source')
        rom_hash=core.fl2._check_rom_file(self.rom_path)
        return core.derive_bytes(self.source_raw,rom_hash,operation,changes)

    def preview(self, operation, changes):
        self.plan=None
        self._clear_output()
        _,report=self._derive(operation,changes)
        self.plan=copy.deepcopy(report)
        return copy.deepcopy(report)

    def commit(self):
        self._clear_output()
        if self.plan is None:
            raise ValueError('preview first')
        output,report=self._derive(self.plan['operation'],self.plan['request'])
        if report!=self.plan:
            self.plan=None
            raise ValueError('stale preview')
        if verifier.verify_bytes(output).file_sha256!=report['output_sha256']:
            raise ValueError('output verification failed')
        if core.fl2.sha(self.source_raw)!=self.source_sha256:
            raise ValueError('source changed')
        stem=re.sub(r'[^A-Za-z0-9_-]+','_',Path(self.source_name).stem).strip('_') or 'save'
        self.output_name=f'{stem}_{report["operation"]}_verified.sav'
        self.output_raw=output
        receipt=copy.deepcopy(report)
        receipt.update(status='GENERATED',source_immutable=True)
        return output,receipt

    def download(self):
        if self.output_raw is None or self.plan is None or self.output_name is None:
            raise ValueError('no verified output')
        expected,_=self._derive(self.plan['operation'],self.plan['request'])
        if expected!=self.output_raw or core.fl2.sha(expected)!=self.plan['output_sha256']:
            self._clear_output()
            raise ValueError('download equality failed')
        verifier.verify_bytes(expected)
        return expected,self.output_name


DEFAULT_REQUESTS={'money':{'money':core.fl2.money.TARGET_MONEY},
                  'party':{'friendship':51},
                  'inventory':{'slot':0,'item_id':13,'quantity':3},
                  'party_append':{},'inventory_insert':{},'party_append_inventory_insert':{}}

OPERATION_LABELS = {'party_append_inventory_insert':'Party append + Antidote insertion'}


def create_page(rom_path):
    if ui is None: raise RuntimeError('install requirements-m4-ui.txt')
    workflow=BrowserWorkflow(rom_path)
    ui.label('PokemonStart v0.22 — Fast Lab experimental').classes('text-h5')
    ui.label('127.0.0.1 専用。元の save を保持し、検証した別ファイルだけをダウンロードします。')
    status=ui.label('ローカル .sav を選択してください。').classes('whitespace-pre-line')
    inspection=ui.label('').classes('whitespace-pre-wrap')
    operation=ui.select(options=[],label='対応操作')
    request=ui.textarea(label='変更（JSON）',value='{}')
    preview_detail=ui.label('').classes('whitespace-pre-wrap')
    preview_button=ui.button('プレビュー',on_click=lambda: do_preview()).disable()
    commit_button=ui.button('検証済み出力を作成',on_click=lambda: do_commit()).disable()
    download_button=ui.button('検証済み .sav を保存',on_click=lambda: do_download()).disable()

    def invalidate():
        workflow.plan=None
        workflow._clear_output()
        preview_detail.text=''
        commit_button.disable()
        download_button.disable()

    def operation_changed():
        invalidate()
        request.value=json.dumps(DEFAULT_REQUESTS.get(operation.value,{}))

    operation.on_value_change(lambda _: operation_changed())
    request.on_value_change(lambda _: invalidate())

    async def on_upload(event):
        invalidate()
        preview_button.disable()
        operation.options=[]
        operation.value=None
        try:
            report=workflow.upload(event.file.name,await event.file.read())
            status.text=f"{report['status']}\nSHA-256: {report['save_sha256']}"
            inspection.text=json.dumps({'semantics':report['semantics'],
                                        'capabilities':report['capabilities']},ensure_ascii=False,indent=2)
            choices=report['supported_write_operations']
            operation.options={op:OPERATION_LABELS.get(op,op) for op in choices}
            operation.value=choices[0] if choices else None
            operation.update()
            preview_button.set_enabled(bool(choices))
        except (OSError,ValueError) as exc:
            status.text=f'REJECTED: {exc}'
            inspection.text='非対応：検証済みの編集操作はありません。'
            operation.update()

    def do_preview():
        invalidate()
        try:
            changes=json.loads(request.value)
            report=workflow.preview(operation.value,changes)
            preview_detail.text=json.dumps(report,ensure_ascii=False,indent=2)
            status.text='PREVIEW — 元の save は変更していません。'
            commit_button.enable()
        except (OSError,ValueError) as exc:
            status.text=f'REJECTED: {exc}'

    def do_commit():
        download_button.disable()
        try:
            _,receipt=workflow.commit()
            status.text=f"GENERATED — verified SHA-256: {receipt['output_sha256']}"
            download_button.enable()
        except (OSError,ValueError) as exc:
            status.text=f'REJECTED: {exc}'

    def do_download():
        try:
            raw,name=workflow.download()
            ui.download.content(raw,name,media_type='application/octet-stream')
        except (OSError,ValueError) as exc:
            status.text=f'REJECTED: {exc}'
            download_button.disable()

    ui.upload(label='ローカル .sav を選択',auto_upload=True,on_upload=on_upload,
              max_file_size=verifier.FLASH_SIZE+verifier.RTC_FOOTER_SIZE,max_files=1).props('accept=.sav')


def run_server(rom_path,port=8766):
    options=server_options(port)
    core.fl2._check_rom_file(rom_path)
    if ui is None: raise RuntimeError('install requirements-m4-ui.txt')
    @ui.page('/')
    def page(): create_page(rom_path)
    ui.run(**options)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=core.fl2.ROM_DEFAULT)
    parser.add_argument('--port',type=int,default=8766)
    args=parser.parse_args(argv)
    run_server(args.rom,args.port)
    return 0


if __name__=='__main__': raise SystemExit(main())
