"""Machine-only exact-ROM E3 gate probe; immutable disk inputs.

Every saved FlagGet/VarGet and stat/ability/move instruction runs from the
SHA-gated ROM. RAM-only in-battle variants are explicit, never inferred from
Party caches. No game load, gameplay, normal SAVE, or Human acceptance claim.
"""
from pathlib import Path
import argparse
import json
import struct
import pokemonstart_fl2_core as profile
import pokemonstart_v022_party_model as m
import pokemonstart_v022_party_audit as a


def probe(raw: bytes, rom: bytes) -> dict:
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC
    tables=m.extract_tables(rom)
    p=a.structure.parse(raw)
    def require(condition):
        if not condition:raise ValueError('exact-ROM independent prediction disagreement')
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    for addr,n in ((0x08000000,0x2000000),(0x02000000,0x40000),(0x03000000,0x8000),(0x06000000,4096)):u.mem_map(addr,n)
    u.mem_write(0x08000000,rom)
    u.hook_add(UC_HOOK_CODE,lambda c,addr,size,data: c.emu_stop() if addr==0x06000000 else None)
    def call(addr,*args):
     u.reg_write(UC_ARM_REG_SP,0x03007000);u.reg_write(UC_ARM_REG_LR,0x06000001)
     for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
     u.emu_start(addr|1,0x06000000,count=1000000)
     if u.reg_read(UC_ARM_REG_PC)!=0x06000000:raise ValueError('budget')
     return u.reg_read(UC_ARM_REG_R0)
    sections=p['slots'][p['active']]['sections']
    image=sections[0][0xF24:0xFF0]+sections[4][0xD98:0xFF0]+sections[13][0x450:0xFF0]
    u.mem_write(0x0203B0E8,image)
    require(call(0x0806DEC4,0x930)==bool(image[6]&1))
    require(call(0x0806DD5C,0x5018)==int.from_bytes(image[560:562],'little'))
    require(not image[6]&1)
    addr=0x02001000
    retained=[]
    for slot,record in enumerate(p['records']):
        require(m.write_eligibility(record,tables,m.saved_context(m.verifier.verify_bytes(raw)))['eligible'])
        expected=a.reconstruct(record,rom)
        u.mem_write(addr,record)
        require(call(0x0804042C,addr)==expected['resolved_ability'])
        require(call(0x0803DF30,addr)==expected['exp_derived_level'])
        call(0x0803DBE8,addr)
        require(bytes(u.mem_read(addr,100))==record)
        retained.append({'slot':slot,'species':expected['species'],'exact_recalculation_record_unchanged':True})
    source=next(record for record in p['records'] if m.write_eligibility(record,tables,m.saved_context(m.verifier.verify_bytes(raw)))['eligible'])
    rows=[]
    target_max=a.reconstruct(source,rom)['ordinary_expected_stats'][0]
    for old,current in ((target_max+15,target_max+15),(target_max+15,target_max-2),
                        (target_max+15,target_max+5),(target_max+15,0),
                        (target_max-5,target_max-5),(target_max+15,target_max)):
     for battle in (False,True):
      record=bytearray(source);struct.pack_into('<HH',record,86,current,old)
      expected=a.reconstruct(record,rom)['ordinary_expected_stats']
      new=expected[0]
      hp=0 if current==0 else min(current,new) if new<old and not battle else current if new<old else current+new-old
      u.mem_write(addr,bytes(record));u.mem_write(0x03003569,bytes([2 if battle else 0]));call(0x0803DBE8,addr)
      out=bytes(u.mem_read(addr,100));require(list(struct.unpack_from('<7H',out,86))==[hp,*expected])
      rows.append({'old_max':old,'old_current':current,'new_max':new,'in_battle':battle,'returned_current':hp})
    # exact context modes
    contexts=[]
    for flag in (0,1):
     for tier in (0,11,12,13,65535):
      u.mem_write(0x0203B0EE,bytes([flag]));u.mem_write(0x0203B318,struct.pack('<H',tier))
      checks=[call(x) for x in (0x090AA76C,0x090AA798,0x090AA7C4)]
      require(checks==[int(flag and tier==13),int(flag and tier==12),int(flag and tier==11)])
      contexts.append({'flag':flag,'tier':tier,'average_350_scale':checks})
    u.mem_write(0x0203B0E8,image)
    # Execute the actual save serializer, not just a guessed RAM injection.
    serializer_cases=0
    for sid in (0,4,13):
        buffer=0x02028000
        u.mem_write(buffer,sections[sid])
        u.mem_write(0x030053E4,struct.pack('<I',buffer))
        call(0x090EAD2C)
        require(bytes(u.mem_read(buffer,4096))==sections[sid])
        serializer_cases+=1
    # slot-local set move, exact routine, stale other slots and packed PP-Ups preserved
    moves=0
    for slot in range(4):
     for ups in range(4):
      for old in (0,33,996):
       for target in (0,1,33,996):
        record=bytearray(source);record[40]=ups<<(2*slot)| (0xFF&~(3<<(2*slot)))
        struct.pack_into('<H',record,44+2*slot,old);record[52+slot]=35
        u.mem_write(addr,bytes(record));call(0x0803E0D0,addr,target,slot)
        expected=bytearray(record);struct.pack_into('<H',expected,44+2*slot,target);expected[52+slot]=tables.moves[target].base_pp
        require(bytes(u.mem_read(addr,100))==bytes(expected))
        actual=call(0x0804070C,target,record[40],slot)
        expected_pp=(tables.moves[target].base_pp+tables.moves[target].base_pp*ups//5)&255 if target==0 else m.maximum_pp(target,ups,tables)
        require(actual==expected_pp)
        moves+=1
    ordinary_cases=0
    for sid in sorted(m.ORDINARY_SPECIES):
     for level in (3,50,100):
      for mint in (0,10,16):
       for item in (0,139,142,200,202):
        record=bytearray(source);struct.pack_into('<HHI',record,32,sid,item,tables.experience[tables.species[sid].growth][level])
        record[15]=mint;record[84]=level;struct.pack_into('<2H',record,86,1,1)
        expected=a.reconstruct(record,rom)['ordinary_expected_stats']
        u.mem_write(addr,bytes(record));u.mem_write(0x03003569,b'\x00');call(0x0803DBE8,addr)
        require(list(struct.unpack_from('<7H',bytes(u.mem_read(addr,100)),86))==[expected[0],*expected])
        for hidden in (0,16):
         for selector in (0,128):
          record[71]=record[71]&~16|hidden;record[75]=record[75]&127|selector
          u.mem_write(addr,bytes(record));require(call(0x0804042C,addr)==a.reconstruct(record,rom)['resolved_ability'])
        ordinary_cases+=1
    form_move_cases=0
    for sid in sorted(m.ORDINARY_SPECIES):
        for old,target in ((1,548),(548,1)):
            record=bytearray(source)
            struct.pack_into('<H',record,32,sid)
            struct.pack_into('<H',record,44,old)
            expected=bytearray(record)
            struct.pack_into('<H',expected,44,target)
            expected[52]=tables.moves[target].base_pp
            u.mem_write(addr,bytes(record));call(0x0803E0D0,addr,target,0)
            require(bytes(u.mem_read(addr,100))==bytes(expected))
            form_move_cases+=1
    # Investigate excluded exceptional branches without granting authority.
    exceptions=[]
    player_id=sections[0][10:14]
    u.mem_write(0x02020000,sections[0])
    u.mem_write(0x0300504C,struct.pack('<I',0x02020000))
    for sid in (496,497,498,913,1460):
        record=bytearray(source)
        struct.pack_into('<H',record,32,sid)
        record[4:8]=player_id
        record[:4]=player_id  # synthetic shiny/perfect-IV activation
        struct.pack_into('<I',record,72,0x3FFFFFFF)
        record[71]&=~16
        u.mem_write(addr,bytes(record))
        ability=call(0x0804042C,addr)
        require(ability==319)
        exceptions.append({'species':sid,'shiny_perfect_IV_override':ability,'writer_eligible':False})
    special_stats=[]
    for sid,item,hyper in ((int.from_bytes(source[32:34],'little'),835,0),
                           (303,0,0),(303,835,0),
                           (int.from_bytes(source[32:34],'little'),0,63)):
        record=bytearray(source)
        struct.pack_into('<HH',record,32,sid,item)
        record[16]=hyper
        record[84]=20
        struct.pack_into('<I',record,36,tables.experience[tables.species[sid].growth][20])
        struct.pack_into('<2H',record,86,1,1)
        # Independent ordinary arithmetic inputs with explicit exceptional
        # rules, only in the probe. Production eligibility still rejects them.
        ordinary=bytearray(record)
        ordinary[16]=0
        if hyper:struct.pack_into('<I',ordinary,72,0x3FFFFFFF)
        struct.pack_into('<H',ordinary,34,0)
        if sid==303:
            # Reconstruct Shedinja's non-HP bases arithmetically, separately
            # from the independent ordinary auditor's intentional rejection.
            bases=tables.species[sid].bases
            ivs=[int.from_bytes(ordinary[72:76],'little')>>(j*5)&31 for j in range(6)]
            nature=ordinary[15]-1 if ordinary[15] else int.from_bytes(ordinary[:4],'little')%25
            expected=[1]
            for j in range(1,6):
                value=(2*bases[j]+ivs[j]+ordinary[56+j]//4)*20//100+5
                modifier=0 if nature//5==nature%5 else 1 if j-1==nature//5 else -1 if j-1==nature%5 else 0
                expected.append(value*(10+modifier)//10)
        else:expected=a.reconstruct(ordinary,rom)['ordinary_expected_stats']
        if item==835:expected=[expected[0] if sid==303 else expected[0]*2,*[x*2 for x in expected[1:]]]
        u.mem_write(addr,bytes(record));call(0x0803DBE8,addr)
        require(list(struct.unpack_from('<7H',bytes(u.mem_read(addr,100)),86))==[expected[0],*expected])
        special_stats.append({'species':sid,'item':item,'hyper_mask':hyper,'exact_special_prediction_equal':True,'writer_eligible':False})
    items=[]
    for mid in range(13,23):
     item=tables.items[mid];effect,param=tables.held_effects[mid]
     items.append({'id':mid,'pocket':item.pocket,'importance':item.importance,'type':item.item_type,'effect':effect,'parameter':param})
    return {'rom_sha256':m.sha(rom),'source_sha256':m.sha(raw),'saved_context':{'flag_0x930':bool(image[6]&1),'variable_0x5018':int.from_bytes(image[560:562],'little')},'retained_records':retained,'context_cases':contexts,'hp_cases':rows,'serializer_cases':serializer_cases,'move_transitions':moves,'form_move_cases':form_move_cases,'ordinary_stat_item_cases':ordinary_cases,'ordinary_ability_cases':ordinary_cases*4,'ability_exceptions':exceptions,'special_stat_cases':special_stats,'medicine_held_metadata':items,'gameplay_acceptance':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',required=True,type=Path)
    parser.add_argument('--save',required=True,type=Path)
    args=parser.parse_args()
    rp=profile._private_file(args.rom,'ROM',must_exist=True)
    sp=profile._private_file(args.save,'save',must_exist=True)
    rom,raw=rp.read_bytes(),sp.read_bytes()
    report=probe(raw,rom)
    if rom!=rp.read_bytes() or raw!=sp.read_bytes():
        raise ValueError('private source changed during exact probe')
    report['sources_immutable']=True
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
