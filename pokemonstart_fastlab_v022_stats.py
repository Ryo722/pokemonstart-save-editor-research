"""Exact-profile stat calculations used only by the Fast Lab v0.22 editors."""
from __future__ import annotations

from dataclasses import replace

import pokemonstart_save_verifier as v
import pokemonstart_transaction as tx


def stats(mon: v.PartyRecord, *, level: int | None = None) -> tuple[int, ...]:
    """Calculate the evidenced Modest Bulbasaur/Ivysaur level 5/6 profile."""
    stat_level = mon.level if level is None else level
    if (mon.species not in (1, 2) or stat_level not in (5, 6)
            or mon.hyper_training != 0 or mon.nature_mint != 0
            or mon.personality % 25 != 15):
        raise tx.TransactionError("unsupported Fast Lab v0.22 stat profile")
    if any(iv < 0 or iv > 31 for iv in mon.ivs):
        raise tx.TransactionError("IV out of range")
    if any(ev < 0 or ev > 252 for ev in mon.evs) or sum(mon.evs) > 510:
        raise tx.TransactionError("EV allocation out of range")
    hp_base = 45 if mon.species == 1 else 60
    hp_max = ((2 * hp_base + mon.ivs[0] + mon.evs[0] // 4) * stat_level) // 100 + stat_level + 10
    bases = (49, 49, 45, 65, 65) if mon.species == 1 else (62, 63, 60, 80, 80)
    values = [((2 * base + mon.ivs[i] + mon.evs[i] // 4) * stat_level) // 100 + stat_level
              for i, base in enumerate(bases, 1)]
    # The only live-confirmed native nature is Modest (15): +Sp. Attack, -Attack.
    values[0] = values[0] * 90 // 100
    values[3] = values[3] * 110 // 100
    if hp_max < mon.max_hp:
        raise tx.TransactionError("HP-decreasing transformation is outside this proof")
    hp = mon.hp + hp_max - mon.max_hp if mon.hp else 0
    return (min(hp, hp_max), hp_max, *values)


def after_attack_iv(mon: v.PartyRecord) -> v.PartyRecord:
    if mon.species != 1 or mon.level != 5 or mon.ivs[1] != 29:
        raise tx.TransactionError("Attack IV edit is outside the live-confirmed baseline")
    interim = replace(mon, ivs=(mon.ivs[0], 0, *mon.ivs[2:]))
    hp, max_hp, attack, defense, speed, sp_attack, sp_defense = stats(interim)
    return replace(interim, hp=hp, max_hp=max_hp, attack=attack, defense=defense,
                   speed=speed, sp_attack=sp_attack, sp_defense=sp_defense)
