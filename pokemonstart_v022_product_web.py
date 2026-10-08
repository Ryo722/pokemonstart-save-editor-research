"""Local practical editor; candidate-only bounded exact-v0.22 capabilities."""
from __future__ import annotations
import argparse
import copy
import os
import re
from pathlib import Path
import pokemonstart_v022_product_core as core
from pokemonstart_v022_web import BrowserWorkflow as LegacyWorkflow, server_options, ui


class ProductWorkflow(LegacyWorkflow):
    def _read_rom(self):
        return self.rom_path.read_bytes()

    def upload(self, filename, raw):
        self._reset()
        name=Path(filename).name
        if Path(name).suffix.lower()!='.sav' or type(raw) is not bytes:
            raise ValueError('select a local .sav file')
        rom=core.profile._check_rom_file(self.rom_path)
        report=core.inspect(raw,rom,rom_bytes=self._read_rom())
        self.source_raw,self.source_sha256,self.source_name=raw,core.profile.sha(raw),name
        return report

    def invalidate(self):
        self.plan=None
        self._clear_output()

    def _derive(self, request):
        if self.source_raw is None or core.profile.sha(self.source_raw)!=self.source_sha256:
            raise ValueError('missing or stale source')
        rom=core.profile._check_rom_file(self.rom_path)
        return core.derive(self.source_raw,rom,request,rom_bytes=self._read_rom())

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

    def export_verified(self, directory):
        """Optional private host export; refuses every existing destination."""
        parent=Path(directory).resolve(strict=True)
        if not parent.is_dir() or not parent.is_relative_to(core.profile.PRIVATE_ROOT):
            raise ValueError('export directory must be inside the private workspace')
        raw,name=self.download()
        destination=parent/name
        with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as handle:
            handle.write(raw)
        if destination.read_bytes()!=raw or self.download()[0]!=raw:
            raise ValueError('private export equality failed')
        return destination


CAPABILITY_SUMMARY='''対応（exact v0.22 のみ・条件を満たす場合）
• Party: 種族 / Level・EXP / 技・PP・PP-Up / なつき度 / IV・EV / 性格 / 特性 / 持ち物 / 色違い（Shiny）切替
• Pokémon 作成: Party の最初の空きスロットへ通常個体を作成（色違い指定可）
• Items: 回復系 32 種の追加・数量変更・削除、Give All（32 種を各 99 個）
• Trainer: お金 0〜9,999,999
• PC Box: 全 Box 閲覧、Box 1〜19 の既存ポケモン編集（候補版）

非対応（変更しません）
• Box 20〜25 の編集・Box への作成、ニックネーム / OT / TID / Ball / 生成情報
• 回復系 32 種以外の道具（ボール・きのみ・技マシン・大切なもの等）、全道具 Give All
• 図鑑 / ストーリー / イベント / 時計、v0.22 以外の版'''


SPECIES_NAMES={1:'Bulbasaur',2:'Ivysaur',25:'Pikachu',288:'Zigzagoon'}
NATURE_NAMES=('Hardy','Lonely','Brave','Adamant','Naughty','Bold','Docile','Relaxed','Impish','Lax','Timid','Hasty','Serious','Jolly','Naive','Modest','Mild','Quiet','Bashful','Rash','Calm','Gentle','Sassy','Careful','Quirky')
STAT_NAMES=('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')


def control_integer(value):
    if type(value) not in (int,float) or value!=int(value):raise ValueError('整数を入力してください')
    return int(value)


def create_page(rom_path,export_directory=None):
    if ui is None:raise RuntimeError('install requirements-m4-ui.txt')
    workflow=ProductWorkflow(rom_path)
    ui.label('PokemonStart v0.22 Editor').classes('text-h4')
    ui.label('候補版 / Fast Lab • ローカル専用 • 元の save は変更せず、検証済みの別 save を出力')
    with ui.expansion('対応機能 / 非対応機能').classes('w-full'):
        ui.label(CAPABILITY_SUMMARY).classes('whitespace-pre-line text-body2')
    ui.label('Open Save  →  Edit  →  Preview  →  Verify  →  Export').classes('text-subtitle1')
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
        element=ui.number(label=label,value=value,min=lower,max=upper,step=1).classes('w-48')
        element.on_value_change(lambda _:invalidate())
        return element

    def select(label,options,value):
        element=ui.select(options,label=label,value=value,with_input=True).classes('w-64')
        element.on_value_change(lambda _:invalidate())
        return element

    def render(report):
        editor.clear();controls.clear()
        with editor:
            with ui.tabs() as tabs:
                party_tab=ui.tab('Party');items_tab=ui.tab('Items');box_tab=ui.tab('PC Box');trainer_tab=ui.tab('Trainer')
            with ui.tab_panels(tabs,value=party_tab).classes('w-full'):
                with ui.tab_panel(party_tab):
                    ui.label('Party positions 1–6 — 編集は対応するメンバーのみ。作成は最初の空きから順に行います。')
                    creator=report.get('creator',{})
                    if creator and not creator.get('eligible'):
                        ui.label('Create Pokémon 非対応: '+creator['reason'])
                    controls['creations']=[]
                    for slot in range(6):
                        if slot>=len(report['party']):
                            with ui.expansion(f'Party #{slot+1} — Empty').classes('w-full'):
                                if creator.get('eligible'):
                                    options=creator['options'];fields={}
                                    enabled=ui.checkbox(f'Create Pokémon — Party #{slot+1}')
                                    fields['enabled']=enabled
                                    controls['creations'].append(fields)
                                    if slot>len(report['party']):enabled.disable()
                                    def toggle_creation(event, index=len(controls['creations'])-1):
                                        pending=controls['creations']
                                        if not event.value:
                                            for later in pending[index+1:]:
                                                later['enabled'].value=False
                                                later['enabled'].disable()
                                        elif index+1<len(pending):pending[index+1]['enabled'].enable()
                                        invalidate()
                                    enabled.on_value_change(toggle_creation)
                                    sid=next(iter(options['species']))
                                    fields['species']=select(f'Create Species — Party #{slot+1}',options['species'],sid)
                                    fields['level']=number(f'Create Level — Party #{slot+1}',3,1,100)
                                    fields['nature']=select('Create Nature',{i:n for i,n in enumerate(NATURE_NAMES)},0)
                                    fields['friendship']=number('Create Friendship',creator['friendship_defaults'][sid],0,255)
                                    def choices(species):
                                        return {aid:f'通常特性 {i+1} (#{aid})' for i,aid in enumerate(options['abilities'][species][:2]) if aid}
                                    fields['ability']=select('Create Ability',choices(sid),options['abilities'][sid][0])
                                    def species_changed(event, fields=fields, creator=creator):
                                        abilities=creator['options']['abilities'][event.value][:2]
                                        fields['ability'].options={aid:f'通常特性 {i+1} (#{aid})' for i,aid in enumerate(abilities) if aid}
                                        fields['ability'].value=abilities[0];fields['ability'].update()
                                        fields['friendship'].value=creator['friendship_defaults'][event.value]
                                        invalidate()
                                    fields['species'].on_value_change(species_changed)
                                    fields['held_item']=select('Create Held item',options['held_item'],0)
                                    fields['shiny']=ui.checkbox(f'Create Shiny（色違い） — Party #{slot+1}')
                                    fields['shiny'].on_value_change(lambda _:invalidate())
                                    for field,maximum in (('ivs',31),('evs',252)):
                                        fields[field]=[]
                                        with ui.row():
                                            for name in STAT_NAMES:
                                                fields[field].append(number(f'Create {name} {field.upper()}',0,0,maximum))
                                    ui.label('EV 合計 ≤ 510。技を明示選択してください（自動 learnset は非対応）。PP は最大、PP-Up は 0。')
                                    fields['moves']=[]
                                    for index in range(4):
                                        fields['moves'].append(select(f'Create Move {index+1}',options['moves'],33 if index==0 and 33 in options['moves'] else 0))
                                    ui.label('生成 identity: 元 save の OT、種族名。色違いは上のチェックで指定。PID / OT / Ball / 生成メタデータは直接編集できません。Pokédex は変更しません。')
                                else:ui.label('Create Pokémon 非対応')
                            continue
                        mon=report['party'][slot];cap=mon['capabilities'];fields={}
                        with ui.expansion(f"Party #{slot+1} — {'★ ' if mon.get('shiny') else ''}{mon.get('species_name') or SPECIES_NAMES.get(mon['species'],'Species #'+str(mon['species']))} • Lv.{mon['level']} • HP {mon['cached_stats'][0]}/{mon['cached_stats'][1]}",value=slot==0).classes('w-full'):
                            if mon.get('rejection'):ui.label('非対応: '+mon['rejection'])
                            ui.label('Main').classes('text-subtitle1')
                            if cap.get('friendship'):fields['friendship']=number(f'Friendship — Party #{slot+1}',mon['friendship'],0,255)
                            if cap.get('e3') and cap.get('stats'):
                                options=mon['options']
                                fields['species']=select('Species',options['species'],mon['species'])
                                fields['level']=number('Level',mon['level'],1,100)
                                fields['experience']=number('EXP',mon['experience'],1,2000000)
                                ui.label('Level の変更では EXP も再計算します。EXP も変更する場合は Level と一致させてください。')
                                if cap.get('shiny'):
                                    fields['shiny']=ui.checkbox(f'Shiny（色違い） — Party #{slot+1}',value=bool(mon.get('shiny')))
                                    fields['shiny'].on_value_change(lambda _:invalidate())
                                    ui.label('色違い切替は PID のみ変更（OT / TID / 性格 / 性別 / 特性 / IV は維持）。種族変更とは別に行ってください。').classes('text-caption')
                                fields['effective_nature']=select('Effective nature',{i:name for i,name in enumerate(NATURE_NAMES)},mon['effective_nature'])
                                def ability_choices(sid):
                                    result={}
                                    for label,aid in zip(('通常特性 1','通常特性 2','隠れ特性'),options['abilities'][sid]):
                                        if aid:result.setdefault(aid,f'{label} (#{aid})')
                                    return result
                                fields['ability']=select('Ability',ability_choices(mon['species']),mon['resolved_ability'])
                                def update_ability(event,fields=fields,mon=mon,options=options):
                                    choices={}
                                    for label,aid in zip(('通常特性 1','通常特性 2','隠れ特性'),options['abilities'][event.value]):
                                        if aid:choices.setdefault(aid,f'{label} (#{aid})')
                                    control=fields['ability'];control.options=choices
                                    if control.value not in choices:control.value=next(iter(choices))
                                    control.update();invalidate()
                                fields['species'].on_value_change(update_ability)
                                held=dict(options['held_item'])
                                if mon['held_item'] not in held:held[mon['held_item']]=(mon.get('held_item_name') or str(mon['held_item']))+'（保持のみ）'
                                fields['held_item']=select('Held item',held,mon['held_item'])
                                ui.label('Stats').classes('text-subtitle1')
                                fields['ivs']=[];fields['evs']=[]
                                for field,maximum in (('ivs',31),('evs',252)):
                                    with ui.row():
                                        for index,name in enumerate(STAT_NAMES):
                                            fields[field].append(number(f'{name} {field.upper()}',mon[field][index],0,maximum))
                                ui.label('EV 合計 ≤ 510。現在 HP を下回る最大 HP への減少は非対応です。')
                            elif cap.get('stats'):
                                fields['species']=select('Species',core.party.SPECIES,mon['species'])
                                ui.label('Level: 読み取り専用 — Level 6 の stat 計算は exact build で未確認です。')
                                fields['experience']=number('EXP (Lv.5 range)',mon['experience'],135,178)
                                ui.label('IV / EV — 合計 EV ≤ 510。最大 HP の減少は非対応。')
                                ui.label('Stats').classes('text-subtitle1')
                                fields['ivs']=[];fields['evs']=[]
                                for field,maximum in (('ivs',31),('evs',252)):
                                    with ui.row():
                                        for index,name in enumerate(STAT_NAMES):
                                            fields[field].append(number(f'{name} {field.upper()}',mon[field][index],0,maximum))
                            else:ui.label('Species / Level / EXP / IV / EV: 読み取り専用 — '+cap.get('stats_reason','構造未対応'))
                            ui.label('Derived stats (read-only): '+', '.join(f'{name} {value}' for name,value in zip(STAT_NAMES,mon['cached_stats'][1:])))
                            ui.label('Moves').classes('text-subtitle1')
                            with ui.row():
                                for index,move in enumerate(mon['moves']):
                                    with ui.column():
                                        ui.label(f'Move {index+1}')
                                        if cap.get('e3') and cap.get('moves'):
                                            fields.setdefault('moves',{})[index]=select(f'Move {index+1}',mon['options']['moves'],move)
                                            fields.setdefault('pp',{})[index]=number(f'PP {index+1}',mon['pp'][index],0,255)
                                            fields.setdefault('pp_up',{})[index]=number(f'PP-Up {index+1}',(mon['pp_bonuses']>>(index*2))&3,0,3)
                                        elif index==0 and cap.get('moves'):
                                            fields['move']=select('Move 1',core.party.MOVES,move)
                                        else:ui.label(core.party.MOVES.get(move,'Empty' if move==0 else f'Move #{move}'))
                                        if not cap.get('e3') or not cap.get('moves'):
                                            ui.label(f"PP {mon['pp'][index]} • PP-Up {(mon['pp_bonuses']>>(index*2))&3} (read-only)")
                            ui.label(f"Effective nature: {NATURE_NAMES[mon['effective_nature']]} • Held item: {mon.get('held_item_name') or mon['held_item']}")
                            if not cap.get('e3'):ui.label('Ability / nature / held item / ball: 読み取り専用。解決・結合規則が未確立。')
                            if cap.get('e3'):ui.label('空技の未編集 PP は保持します。技変更時はその枠の PP を初期化します。Ball / identity は読み取り専用です。')
                        controls[slot]=fields
                with ui.tab_panel(items_tab):
                    ui.label('Items — 対応する回復薬のみ編集できます。')
                    item_report=report['items']
                    if item_report and item_report.get('e2'):
                        controls['medicine_rows']={}
                        with ui.row().classes('w-full items-center'):
                            ui.label('Item').classes('font-bold w-48')
                            ui.label('Quantity').classes('font-bold w-48')
                            ui.label('Action').classes('font-bold')
                        for entry in item_report['entries']:
                            with ui.row().classes('w-full items-center'):
                                ui.label(entry['name']).classes('w-48')
                                if entry['editable']:
                                    quantity=number('Quantity — '+entry['name'],entry['quantity'],1,999)
                                    remove=ui.checkbox('Remove — '+entry['name'])
                                    remove.on_value_change(lambda _:invalidate())
                                    controls['medicine_rows'][entry['item_id']]=(quantity,remove)
                                else:ui.label(f"x{entry['quantity']}（読み取り専用）")
                        held={e['item_id'] for e in item_report['entries']}
                        choices={i:name for i,name in item_report['supported_names'].items() if i not in held}
                        if choices and item_report['occupied']<item_report['capacity']:
                            controls['add_medicine']=ui.checkbox('Add Item')
                            controls['add_medicine'].on_value_change(lambda _:invalidate())
                            controls['medicine_name']=select('Item',choices,next(iter(choices)))
                            controls['medicine_quantity']=number('Quantity — Add Item',1,1,999)
                        ui.label('数量は 1〜999。削除は Remove を選択してください。その他の道具は読み取り専用です。')
                        give_all=item_report.get('give_all') or {}
                        ui.separator()
                        controls['give_all']=ui.checkbox(
                            f"Give All Supported Items — 対応 {give_all.get('supported_items','?')} 種を各 {give_all.get('quantity',99)} 個に")
                        controls['give_all'].on_value_change(lambda _:invalidate())
                        if give_all.get('enabled'):
                            ui.label(f"{give_all['changes']} 種を追加 / 99 に変更します（99 超の所持数は減らしません）。"
                                     '回復系のみ・全道具ではありません。Give All は他の Items 変更と同時には使えません。').classes('text-caption')
                        else:
                            controls['give_all'].disable()
                            ui.label('Give All 無効: '+str(give_all.get('reason','未対応'))).classes('text-caption')
                    elif item_report:
                        for entry in item_report['entries']:
                            with ui.row():
                                ui.label(entry['name'])
                                if entry['editable']:controls['potion']=number('Quantity',entry['quantity'],1,3)
                                else:ui.label(f"x{entry['quantity']} (read-only)")
                        if item_report['can_insert_antidote']:
                            controls['insert']=ui.checkbox('Add Antidote x1（観測済み第3枠）')
                            controls['insert'].on_value_change(lambda _:invalidate())
                        if item_report['can_remove_antidote']:
                            controls['remove']=ui.checkbox('Remove Antidote x1（観測済み第3枠）')
                            controls['remove'].on_value_change(lambda _:invalidate())
                        ui.label('Antidote の追加・削除は Potion x1..3 / item #533 x1 / 第3枠とゼロ tail が一致する場合のみ対応。後続枠・容量・一般的な並べ替えは未確立。Give All Supported Ordinary Items は保留。')
                    else:ui.label('Items 非対応: '+report['rejections'].get('items',''))
                    ui.label('Balls / Berries / TM / Key Items: 編集非対応（Give All の対象外）。')
                with ui.tab_panel(box_tab):
                    render_boxes(report)
                with ui.tab_panel(trainer_tab):
                    if report['money']:controls['money']=number('Money',report['money']['money'],0,9999999)
                    else:ui.label('Money 非対応: '+report['rejections'].get('money',''))
                    ui.label('Trainer identity / story / Pokédex / RTC: read-only; editing is unsupported.')

    def render_boxes(report):
        boxes=report.get('box');controls['box_edits']={}
        ui.label('PC Box — Box 1〜19 の既存ポケモンを編集できます（候補版）。Box 20〜25 は閲覧のみ。Box への作成は非対応。')
        if not boxes:
            ui.label('PC Box 読み取り非対応: '+report['rejections'].get('box','ROM が必要です'));return
        by_position={(row['box'],row['position']):row for row in boxes['occupied']}
        counts={box_number:sum(1 for row in boxes['occupied'] if row['box']==box_number) for box_number in range(1,boxes['boxes']+1)}
        first=next((box_number for box_number in counts if counts[box_number]),1)
        ui.label(f"格納数: {len(boxes['occupied'])} 匹。セルを選ぶと下に詳細・編集欄が開きます。★ = 色違い。").classes('text-caption')
        box_select=ui.select({box_number:f'Box {box_number}（{counts[box_number]} 匹）'+('・閲覧のみ' if box_number>19 else '')
                              for box_number in counts},value=first,label='Box').classes('w-64')
        grid=ui.grid(columns=6).classes('gap-1')
        detail=ui.column().classes('w-full')
        options=boxes['options']

        def editor(row):
            key=(row['box'],row['position']);prefix=f"Box {key[0]} #{key[1]}"
            with detail:
                container=ui.column().classes('w-full')
            with container:
                ui.label(f"{prefix} — {('★ ' if row['shiny'] else '')}{row['species_name']} Lv.{row['level_from_exp']}").classes('text-subtitle1')
                if not row['editable']:
                    ui.label('編集不可: '+'; '.join(row['edit_reasons']))
                    ui.label(f"Held item: {row['held_item_name']} • Moves: {' / '.join(row['move_names'])} • IVs {row['ivs']} • EVs {row['evs']}")
                    return container,{}
                mon=row['semantic'];fields={}
                fields['shiny']=ui.checkbox(f'Shiny（色違い） — {prefix}',value=mon['shiny'])
                fields['shiny'].on_value_change(lambda _:invalidate())
                with ui.row():
                    fields['species']=select(f'Species — {prefix}',options['species'],mon['species'])
                    fields['level']=number(f'Level — {prefix}',mon['level'],1,100)
                    fields['effective_nature']=select(f'Nature — {prefix}',{i:n for i,n in enumerate(NATURE_NAMES)},mon['effective_nature'])
                with ui.row():
                    abilities={aid:f'特性 #{aid}' for aid in row['ability_options']}
                    fields['ability']=select(f'Ability — {prefix}',abilities,mon['resolved_ability'])
                    def update_ability(event,control=fields['ability']):
                        choices={}
                        for label,aid in zip(('通常特性 1','通常特性 2','隠れ特性'),options['abilities'][event.value]):
                            if aid:choices.setdefault(aid,f'{label} (#{aid})')
                        control.options=choices
                        if control.value not in choices:control.value=next(iter(choices))
                        control.update();invalidate()
                    fields['species'].on_value_change(update_ability)
                    held=dict(options['held_item'])
                    if mon['held_item'] not in held:held[mon['held_item']]=row['held_item_name']+'（保持のみ）'
                    fields['held_item']=select(f'Held item — {prefix}',held,mon['held_item'])
                    fields['friendship']=number(f'Friendship — {prefix}',mon['friendship'],0,255)
                for field,maximum in (('ivs',31),('evs',252)):
                    fields[field]=[]
                    with ui.row():
                        for index,name in enumerate(STAT_NAMES):
                            fields[field].append(number(f'{name} {field.upper()} — {prefix}',mon[field][index],0,maximum))
                fields['moves']={};fields['pp_up']={}
                with ui.row():
                    for index in range(4):
                        with ui.column():
                            fields['moves'][index]=select(f'Move {index+1} — {prefix}',options['moves'],mon['moves'][index])
                            fields['pp_up'][index]=number(f'PP-Up {index+1} — {prefix}',mon['pp_up'][index],0,3)
                ui.label('Box では PP / 能力値は保存されず、引き出し時にゲームが再計算します。色違いと種族変更は別々に行ってください。').classes('text-caption')
            return container,fields

        def choose(row):
            key=(row['box'],row['position'])
            if key not in controls['box_edits']:
                container,fields=editor(row)
                controls['box_edits'][key]=(container,fields,row)
            for other,(container,_,_) in controls['box_edits'].items():
                container.set_visibility(other==key)

        def show_box():
            grid.clear()
            with grid:
                for position in range(1,31):
                    row=by_position.get((box_select.value,position))
                    if row is None:
                        ui.button(f'{position}. —').props('flat dense').classes('text-xs w-36').disable();continue
                    text=f"{position}. {'★' if row['shiny'] else ''}{row['species_name']} Lv{row['level_from_exp']}"
                    ui.button(text,on_click=lambda _,row=row:choose(row)).props(
                        'outline dense' if row['editable'] else 'flat dense').classes('text-xs w-36')
        box_select.on_value_change(lambda _:show_box())
        show_box()
        with ui.expansion('一覧（全 Box）').classes('w-full'):
            rows=[{'box':row['box'],'position':row['position'],
                   'species':('★ ' if row['shiny'] else '')+(row['species_name'] or f"#{row['species']}"),
                   'level':row['level_from_exp'],'held':row['held_item_name'],'moves':' / '.join(row['move_names']),
                   'ivs':'/'.join(map(str,row['ivs'])),'evs':'/'.join(map(str,row['evs'])),
                   'edit':'可' if row['editable'] else '不可'} for row in boxes['occupied']]
            columns=[{'name':key,'label':label,'field':key,'align':'left'} for key,label in (
                ('box','Box'),('position','#'),('species','Species'),('level','Lv'),('held','Held item'),
                ('moves','Moves'),('ivs','IVs'),('evs','EVs'),('edit','編集'))]
            if rows:ui.table(columns=columns,rows=rows,row_key='position',pagination=30).classes('w-full')
            else:ui.label('Box は空です。')

    async def upload(event):
        invalidate();preview_button.disable();editor.clear();controls.clear();inspection.clear()
        try:
            report=workflow.upload(event.file.name,await event.file.read())
            inspection.update(report);render(report)
            status.text='読み込み済み — Party / Items / PC Box / Trainer を編集できます。'
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
            for field in ('species','level','experience','friendship','ivs','evs','effective_nature','ability','held_item'):
                if field not in fields:continue
                value=([control_integer(e.value) for e in fields[field]] if field in ('ivs','evs')
                       else control_integer(fields[field].value))
                if value!=mon['resolved_ability' if field=='ability' else field]:changes[field]=value
            if 'shiny' in fields and bool(fields['shiny'].value)!=bool(mon.get('shiny')):
                changes['shiny']=bool(fields['shiny'].value)
            if 'move' in fields and fields['move'].value!=mon['moves'][0]:
                changes['moves']={0:control_integer(fields['move'].value)}
            for field in ('moves','pp','pp_up'):
                if field not in fields:continue
                mapping={}
                for index,control in fields[field].items():
                    value=control_integer(control.value)
                    old=((mon['pp_bonuses']>>(2*index))&3) if field=='pp_up' else mon[field][index]
                    if value!=old:mapping[index]=value
                if mapping:changes[field]=mapping
            if changes:edits.append({'slot':mon['slot'],'changes':changes})
        if edits:result['party']=edits
        creations=[];gap=False
        for fields in controls.get('creations',[]):
            if not fields['enabled'].value:
                gap=True;continue
            if gap:raise ValueError('最初の空 Party スロットから順に作成してください')
            creation={key:control_integer(fields[key].value) for key in
                      ('species','level','nature','friendship','ability','held_item')}
            for key in ('ivs','evs','moves'):
                creation[key]=[control_integer(c.value) for c in fields[key]]
            if fields.get('shiny') is not None and fields['shiny'].value:creation['shiny']=True
            creations.append(creation)
        if creations:result['create']=creations
        box_edits=[]
        for (box_number,position),(_,fields,row) in controls.get('box_edits',{}).items():
            if not fields:continue
            mon=row['semantic'];changes={}
            if bool(fields['shiny'].value)!=mon['shiny']:changes['shiny']=bool(fields['shiny'].value)
            for field in ('species','level','effective_nature','held_item','friendship'):
                value=control_integer(fields[field].value)
                if value!=mon[field]:changes[field]=value
            value=control_integer(fields['ability'].value)
            if value!=mon['resolved_ability']:changes['ability']=value
            for field in ('ivs','evs'):
                values=[control_integer(c.value) for c in fields[field]]
                if values!=mon[field]:changes[field]=values
            for field in ('moves','pp_up'):
                mapping={index:control_integer(c.value) for index,c in fields[field].items()
                         if control_integer(c.value)!=mon[field][index]}
                if mapping:changes[field]=mapping
            if changes:box_edits.append({'box':box_number,'position':position,'changes':changes})
        if box_edits:result['box']=box_edits
        if inspection.get('items') and inspection['items'].get('e2'):
            operations=[]
            for entry in inspection['items']['entries']:
                fields=controls.get('medicine_rows',{}).get(entry['item_id'])
                if fields is None:continue
                quantity,remove=fields
                if remove.value:operations.append({'op':'remove','item_id':entry['item_id']})
                else:
                    value=control_integer(quantity.value)
                    if value!=entry['quantity']:
                        operations.append({'op':'set','item_id':entry['item_id'],'quantity':value})
            if 'add_medicine' in controls and controls['add_medicine'].value:
                operations.append({'op':'add','item_id':control_integer(controls['medicine_name'].value),
                                   'quantity':control_integer(controls['medicine_quantity'].value)})
            if 'give_all' in controls and controls['give_all'].value:
                if operations:raise ValueError('Give All は他の Items 変更と同時に使えません。どちらかを解除してください')
                operations=[{'op':'give_all'}]
            if operations:result['items']=operations
            return result
        item_changes={}
        if 'potion' in controls:
            quantity=control_integer(controls['potion'].value)
            if quantity!=inspection['items']['entries'][0]['quantity']:item_changes['potion_quantity']=quantity
        if 'insert' in controls and controls['insert'].value:item_changes['insert_antidote']=True
        if 'remove' in controls and controls['remove'].value:item_changes['remove_antidote']=True
        if item_changes:result['items']=item_changes
        return result

    def preview():
        invalidate()
        try:
            report=workflow.preview(request())
            groups={'Party':[],'Created Pokémon':[],'PC Box':[],'Items':[],'Trainer':[]}
            in_creation=False
            for line in report['semantic_diff']:
                if line.startswith('Money:'):
                    groups['Trainer'].append(line);in_creation=False
                elif line.startswith('Box '):
                    groups['PC Box'].append(line);in_creation=False
                elif line.startswith('Party #'):
                    groups['Party'].append(line);in_creation=False
                elif line.startswith('Create Pokémon'):
                    groups['Created Pokémon'].append(line);in_creation=True
                elif in_creation:
                    groups['Created Pokémon'].append(line)
                else:
                    groups['Items'].append(line)
            rendered=['Preview — semantic changes']
            rendered.extend(f"\n{family}\n"+'\n'.join(lines) for family,lines in groups.items() if lines)
            preview_text.text=''.join(rendered)
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
            if export_directory is not None:
                destination=workflow.export_verified(export_directory)
                status.text='別 save を保存しました: '+destination.name
            else:
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
    parser.add_argument('--open',action='store_true',help='open the editor in the default browser')
    parser.add_argument('--export-directory',type=Path,
                        help='Optional existing private directory for exclusive separate save export')
    args=parser.parse_args(argv)
    core.profile._check_rom_file(args.rom)
    if args.export_directory is not None:
        directory=args.export_directory.resolve(strict=True)
        if not directory.is_dir() or not directory.is_relative_to(core.profile.PRIVATE_ROOT):
            raise ValueError('export directory must be inside the private workspace')
    if ui is None:raise RuntimeError('install requirements-m4-ui.txt')
    @ui.page('/')
    def page():create_page(args.rom,args.export_directory)
    options=server_options(args.port);options['title']='PokemonStart v0.22 Editor'
    options['show']=bool(args.open)
    ui.run(**options)
    return 0


if __name__=='__main__':raise SystemExit(main())
