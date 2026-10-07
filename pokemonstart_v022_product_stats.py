"""Source-backed candidate calculator, independent of legacy +level canary code.

Pinned CFRU-JP e24a16fe src/build_pokemon.c CALC_STAT adds 5 to non-HP
stats. Exact-build byte storage and species bases come from canonical v0.22
proofs. No claim of new target normal-SAVE acceptance is made here.
"""
import pokemonstart_transaction as tx


def stats(mon):
    if mon.level == 6:
        raise tx.TransactionError('Level 6 stat formula is unqualified for this exact build')
    if (mon.species not in (1,2) or mon.level != 5
            or mon.hyper_training!=0 or mon.nature_mint!=0
            or mon.personality%25 not in (12,15)):
        raise tx.TransactionError('source-backed stats require Bulbasaur/Ivysaur level5, neutral Serious or Modest, no mint/hyper-training')
    if any(not 0<=x<=31 for x in mon.ivs) or any(not 0<=x<=252 for x in mon.evs) or sum(mon.evs)>510:
        raise tx.TransactionError('IV/EV allocation invalid')
    bases=(45,49,49,45,65,65) if mon.species==1 else (60,62,63,60,80,80)
    hp=((2*bases[0]+mon.ivs[0]+mon.evs[0]//4)*mon.level)//100+mon.level+10
    values=[((2*base+mon.ivs[i]+mon.evs[i]//4)*mon.level)//100+5 for i,base in enumerate(bases[1:],1)]
    if mon.personality%25==15:
        values[0]=values[0]*90//100;values[3]=values[3]*110//100
    if hp<mon.max_hp:raise tx.TransactionError('HP-decreasing transformation is unqualified')
    current=min(hp,mon.hp+hp-mon.max_hp) if mon.hp else 0
    return (current,hp,*values)
