"""Local practical editor; candidate-only bounded exact-v0.22 capabilities."""
from __future__ import annotations
import argparse
import copy
import re
from pathlib import Path
import pokemonstart_v022_product_core as core
from pokemonstart_v022_web import BrowserWorkflow as LegacyWorkflow, server_options, ui


class ProductWorkflow(LegacyWorkflow):
    def upload(self, filename, raw):
        self._reset()
        name=Path(filename).name
        if Path(name).suffix.lower()!='.sav' or type(raw) is not bytes:
            raise ValueError('select a local .sav file')
        rom=core.profile._check_rom_file(self.rom_path)
        report=core.inspect(raw,rom)
        self.source_raw,self.source_sha256,self.source_name=raw,core.profile.sha(raw),name
        return report

    def invalidate(self):
        self.plan=None
        self._clear_output()

    def _derive(self, request):
        if self.source_raw is None or core.profile.sha(self.source_raw)!=self.source_sha256:
            raise ValueError('missing or stale source')
        rom=core.profile._check_rom_file(self.rom_path)
        return core.derive(self.source_raw,rom,request)

    def preview(self, request):
        self.invalidate()
        _,report=self._derive(request)
        self.plan=copy.deepcopy(report)
        return copy.deepcopy(report)

    def commit(self):
        self._clear_output()
        if self.plan is None:raise ValueError('preview first')
        output,report=self._derive(self.plan['request'])
        if report!=self.plan:
            self.invalidate()
            raise ValueError('stale preview')
        core.v.verify_bytes(output)
        stem=re.sub(r'[^A-Za-z0-9_-]+','_',Path(self.source_name).stem).strip('_') or 'save'
        self.output_raw=output
        self.output_name=f'{stem}_product_verified.sav'
        return output,copy.deepcopy(report)

    def download(self):
        if self.output_raw is None or self.plan is None:raise ValueError('no verified output')
        expected,report=self._derive(self.plan['request'])
        if expected!=self.output_raw or report!=self.plan:
            self.invalidate()
            raise ValueError('download equality/stale preview failed')
        core.v.verify_bytes(expected)
        return expected,self.output_name


SPECIES_NAMES={1:'Bulbasaur',2:'Ivysaur',25:'Pikachu',288:'Zigzagoon'}
STAT_NAMES=('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')


def control_integer(value):
    if type(value) not in (int,float) or value!=int(value):raise ValueError('整数を入力してください')
    return int(value)


def create_page(rom_path):
    if ui is None:raise RuntimeError('install requirements-m4-ui.txt')
    workflow=ProductWorkflow(rom_path)
    ui.label('PokemonStart v0.22').classes('text-h4')
    ui.label('候補版 / Fast Lab • ローカル専用 • 元の save を保管し、別の検証済み save を出力')
    status=ui.label('ローカル .sav を開いてください。').classes('whitespace-pre-line')
    editor=ui.column().classes('w-full')
    preview_text=ui.label('').classes('whitespace-pre-line text-body1')
    with ui.expansion('Advanced / Details').classes('w-full'):
        details=ui.label('').classes('whitespace-pre-wrap font-mono text-xs')
    controls={};inspection={}

    def invalidate():
        workflow.invalidate();preview_text.text=''
        export_button.disable();download_button.disable()

    def number(label,value,lower,upper):
        element=ui.number(label=label,value=value,min=lower,max=upper,step=1)
        element.on_value_change(lambda _:invalidate())
        return element

    def select(label,options,value):
        element=ui.select(options,label=label,value=value,with_input=True)
        element.on_value_change(lambda _:invalidate())
        return element

    def render(report):
        editor.clear();controls.clear()
        with editor:
            with ui.tabs() as tabs:
                party_tab=ui.tab('Party');items_tab=ui.tab('Items');trainer_tab=ui.tab('Trainer')
            with ui.tab_panels(tabs,value=party_tab).classes('w-full'):
                with ui.tab_panel(party_tab):
                    ui.label('パーティの既存スロットを編集。空スロットの生成は非対応。')
                    for slot in range(6):
                        if slot>=len(report['party']):
                            with ui.card():ui.label(f'Party #{slot+1} — Empty')
                            continue
                        mon=report['party'][slot];cap=mon['capabilities'];fields={}
                        with ui.expansion(f"Party #{slot+1} — {SPECIES_NAMES.get(mon['species'],'Species #'+str(mon['species']))} • Lv.{mon['level']} • HP {mon['cached_stats'][0]}/{mon['cached_stats'][1]}",value=slot==0).classes('w-full'):
                            if mon.get('rejection'):ui.label('非対応: '+mon['rejection'])
                            if cap.get('friendship'):fields['friendship']=number(f'Friendship — Party #{slot+1}',mon['friendship'],0,255)
                            if cap.get('stats'):
                                fields['species']=select('Species',core.party.SPECIES,mon['species'])
                                with ui.row():
                                    fields['level']=number('Level',mon['level'],5,6)
                                    fields['experience']=number('EXP',mon['experience'],135,235)
                                ui.label('IV / EV — 合計 EV ≤ 510。最大 HP の減少は非対応。')
                                fields['ivs']=[];fields['evs']=[]
                                for field,maximum in (('ivs',31),('evs',252)):
                                    with ui.row():
                                        for index,name in enumerate(STAT_NAMES):
                                            fields[field].append(number(f'{name} {field.upper()}',mon[field][index],0,maximum))
                            else:ui.label('Species / Level / EXP / IV / EV: 読み取り専用 — '+cap.get('stats_reason','構造未対応'))
                            with ui.row():
                                for index,move in enumerate(mon['moves']):
                                    with ui.column():
                                        ui.label(f'Move {index+1}')
                                        if index==0 and cap.get('moves'):
                                            fields['move']=select('Move 1',core.party.MOVES,move)
                                        else:ui.label(core.party.MOVES.get(move,'Empty' if move==0 else f'Move #{move}'))
                                        ui.label(f"PP {mon['pp'][index]} • PP-Up {(mon['pp_bonuses']>>(index*2))&3} (read-only)")
                            ui.label('Stats: '+', '.join(f'{name} {value}' for name,value in zip(STAT_NAMES,mon['cached_stats'][1:])))
                            ui.label(f"Nature #{mon['effective_nature']} • Held item #{mon['held_item']} • Ball #{mon['ball']} • Ability selector {mon['ability_selector']}")
                            ui.label('Ability / nature / held item / ball: 読み取り専用。解決・結合規則が未確立。')
                        controls[slot]=fields
                with ui.tab_panel(items_tab):
                    ui.label('Regular Items — 観測済みの最初の3枠のみ。バッグ全体の容量は未確立。')
                    item_report=report['items']
                    if item_report:
                        for entry in item_report['entries']:
                            with ui.row():
                                ui.label(entry['name'])
                                if entry['editable']:controls['potion']=number('Quantity',entry['quantity'],1,3)
                                else:ui.label(f"x{entry['quantity']} (read-only)")
                        if item_report['can_insert_antidote']:
                            controls['insert']=ui.checkbox('Add Antidote x1（観測済み空き第3枠）')
                            controls['insert'].on_value_change(lambda _:invalidate())
                        ui.button('Remove item — 非対応').disable()
                        ui.label('削除・整列・容量の規則が未確立。Give All Supported Ordinary Items は保留。')
                    else:ui.label('Items 非対応: '+report['rejections'].get('items',''))
                    ui.label('Balls / Medicine / Berries / TM / Key Items / その他の pocket: 未確立・編集非対応。')
                with ui.tab_panel(trainer_tab):
                    if report['money']:controls['money']=number('Money',report['money']['money'],0,9999999)
                    else:ui.label('Money 非対応: '+report['rejections'].get('money',''))
                    ui.label('Trainer identity / story / Pokédex / RTC: 編集非対応。')

    async def upload(event):
        invalidate();preview_button.disable();editor.clear();controls.clear();inspection.clear()
        try:
            report=workflow.upload(event.file.name,await event.file.read())
            inspection.update(report);render(report)
            status.text='読み込み済み — Party / Items / Trainer から編集できます。'
            details.text=str(report);preview_button.enable()
        except (OSError,ValueError) as exc:status.text=f'REJECTED: {exc}'

    def request():
        result={}
        if 'money' in controls:
            target=control_integer(controls['money'].value)
            if target!=inspection['money']['money']:result['money']=target
        edits=[]
        for mon in inspection.get('party',[]):
            fields=controls.get(mon['slot'],{});changes={}
            for field in ('species','level','experience','friendship','ivs','evs'):
                if field not in fields:continue
                value=([control_integer(e.value) for e in fields[field]] if field in ('ivs','evs')
                       else control_integer(fields[field].value))
                if value!=mon[field]:changes[field]=value
            if 'move' in fields and fields['move'].value!=mon['moves'][0]:
                changes['moves']={0:control_integer(fields['move'].value)}
            if changes:edits.append({'slot':mon['slot'],'changes':changes})
        if edits:result['party']=edits
        item_changes={}
        if 'potion' in controls:
            quantity=control_integer(controls['potion'].value)
            if quantity!=inspection['items']['entries'][0]['quantity']:item_changes['potion_quantity']=quantity
        if 'insert' in controls and controls['insert'].value:item_changes['insert_antidote']=True
        if item_changes:result['items']=item_changes
        return result

    def preview():
        invalidate()
        try:
            report=workflow.preview(request())
            preview_text.text='Preview\n'+'\n'.join(report['semantic_diff'])
            details.text=str(report);status.text='プレビューを確認して出力を作成してください。'
            export_button.enable()
        except (OSError,ValueError) as exc:status.text=f'REJECTED: {exc}'

    def export():
        try:
            # Detect changed controls even if a UI event has not reached invalidate yet.
            if request()!=workflow.plan['request']:raise ValueError('stale controls; preview again')
            _,report=workflow.commit();details.text=str(report)
            status.text='検証済みの別 save を生成しました。';download_button.enable()
        except (OSError,ValueError,TypeError) as exc:
            invalidate();status.text=f'REJECTED: {exc}'

    def download():
        try:
            if request()!=workflow.plan['request']:raise ValueError('stale controls; preview again')
            raw,name=workflow.download();ui.download.content(raw,name,media_type='application/octet-stream')
        except (OSError,ValueError,TypeError) as exc:
            invalidate();status.text=f'REJECTED: {exc}'

    ui.upload(label='ローカル .sav を開く',auto_upload=True,on_upload=upload,max_files=1,
              max_file_size=core.v.FLASH_SIZE+core.v.RTC_FOOTER_SIZE).props('accept=.sav')
    with ui.row():
        preview_button=ui.button('Preview',on_click=preview).disable()
        export_button=ui.button('検証して別 save を生成',on_click=export).disable()
        download_button=ui.button('検証済み .sav を保存',on_click=download).disable()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=core.profile.ROM_DEFAULT)
    parser.add_argument('--port',type=int,default=8766)
    args=parser.parse_args(argv)
    core.profile._check_rom_file(args.rom)
    if ui is None:raise RuntimeError('install requirements-m4-ui.txt')
    @ui.page('/')
    def page():create_page(args.rom)
    options=server_options(args.port);options['title']='PokemonStart v0.22 Practical Editor Candidate'
    ui.run(**options)
    return 0


if __name__=='__main__':raise SystemExit(main())
