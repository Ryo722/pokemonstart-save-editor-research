"""Candidate reusable observed regular-items prefix; no inferred bag capacity."""
from __future__ import annotations
import struct
import pokemonstart_save_verifier as v
import pokemonstart_fl2_core as profile
import pokemonstart_fastlab_v022_creation as canonical_creation

NAMES = {13:'Potion',14:'Antidote',533:'Preserved item #533'}
OFFSET = 0xADC


def _observed_antidote_state(raw, rom_sha256, present):
    """Qualify only the captured three-record bag shape and zero tail."""
    profile._require_rom_hash(rom_sha256)
    result = v.verify_bytes(raw)
    section = result.slots[result.active_slot].section(13)
    prefix = [struct.unpack_from('<HH', section.data, OFFSET + 4*i) for i in range(3)]
    expected = (13, 3), (533, 1), ((14, 1) if present else (0, 0))
    if tuple(prefix) != expected or any(section.data[OFFSET + 12:0xFF4]):
        raise ValueError('requires the observed ordered Potion / item #533 / Antidote state with zero tail')
    return result, section


def remove_observed_antidote(raw, rom_sha256):
    """Zero the observed Antidote record in place; no compaction or checksum edit."""
    result, section = _observed_antidote_state(raw, rom_sha256, True)
    base = section.physical_sector * v.SECTOR_SIZE + OFFSET + 8
    output = bytearray(raw)
    output[base:base + 4] = b'\0' * 4
    candidate = bytes(output)
    v.verify_bytes(candidate)
    if struct.unpack_from('<HH', candidate, base) != (0, 0):
        raise ValueError('Antidote deletion postcondition failed')
    return candidate, {'slot': 2, 'item_id': 14, 'quantity': 1,
                       'removed_in_place': True, 'compacted': False,
                       'checksum_changed': False, 'verifier_accepted': True}


def insert_observed_antidote(raw, rom_sha256):
    """Restore the observed Antidote record into its captured empty slot."""
    _, section = _observed_antidote_state(raw, rom_sha256, False)
    base = section.physical_sector * v.SECTOR_SIZE + OFFSET + 8
    output = bytearray(raw)
    struct.pack_into('<HH', output, base, 14, 1)
    candidate = bytes(output)
    v.verify_bytes(candidate)
    if struct.unpack_from('<HH', candidate, base) != (14, 1):
        raise ValueError('Antidote insertion postcondition failed')
    return candidate, {'slot': 2, 'item_id': 14, 'quantity': 1,
                       'restored_observed_position': True,
                       'checksum_changed': False, 'verifier_accepted': True}


def inspect(raw, rom_sha256):
    profile._require_rom_hash(rom_sha256)
    result=v.verify_bytes(raw)
    active=result.slots[result.active_slot]
    if struct.unpack_from('<I',active.section(0).data,0xF20)[0]!=0:
        raise ValueError('Items supports observed key0 only')
    section=active.section(13)
    prefix=[struct.unpack_from('<HH',section.data,OFFSET+i*4) for i in range(3)]
    # An observed three-record window, explicitly NOT inferred pocket capacity.
    if (prefix[0][0]!=13 or not 1<=prefix[0][1]<=3 or prefix[1]!=(533,1)
            or prefix[2] not in ((0,0),(14,1)) or any(section.data[OFFSET+12:])):
        raise ValueError('Items requires observed Potion x1..3 / preserved #533 x1 / optional Antidote x1 prefix and zero tail')
    return {'entries':[{'slot':i,'item_id':item,'name':NAMES[item],'quantity':qty,
                        'editable':item==13,'removable':False}
                       for i,(item,qty) in enumerate(prefix) if item],
            'can_insert_antidote':prefix[2]==(0,0) and profile.sha(raw)==canonical_creation.INVENTORY_SOURCE_SHA256,'window_slots':3,
            'capacity':'unqualified beyond observed three-record window',
            'insertion':'exact canonical pre-purchase root only; reusable whole-pocket uniqueness unqualified',
            'removal':'unsupported: exact-build removal/compaction behavior not established',
            'checksum_covered':False}


def derive(raw, rom_sha256, changes):
    before=inspect(raw,rom_sha256)
    if not isinstance(changes,dict) or not changes or set(changes)-{'potion_quantity','insert_antidote'}:
        raise ValueError('unsupported Items operation; removal/capacity remain unqualified')
    result=v.verify_bytes(raw)
    section=result.slots[result.active_slot].section(13)
    base=section.physical_sector*4096+OFFSET
    output=bytearray(raw);allowed=set()
    if 'potion_quantity' in changes:
        quantity=changes['potion_quantity']
        if type(quantity) is not int or not 1<=quantity<=3:
            raise ValueError('Potion quantity must be an integer in observed range 1..3')
        struct.pack_into('<H',output,base+2,quantity)
        allowed.update((base+2,base+3))
    if 'insert_antidote' in changes:
        if changes['insert_antidote'] is not True or not before['can_insert_antidote']:
            raise ValueError('Antidote insertion requires exact canonical root; full-pocket uniqueness remains unqualified')
        proven,_=canonical_creation.insert_inventory(raw,rom_sha256)
        output[base+8:base+12]=proven[base+8:base+12]
        allowed.update(range(base+8,base+12))
    candidate=bytes(output)
    after=inspect(candidate,rom_sha256)
    diffs=[i for i,(a,b) in enumerate(zip(raw,candidate)) if a!=b]
    if not diffs:raise ValueError('Items unchanged; no output')
    if not set(diffs)<=allowed:raise ValueError('Items byte envelope mismatch')
    verified=v.verify_bytes(candidate)
    if verified.slots[verified.active_slot].section(13).checksum_stored!=section.checksum_stored:
        raise ValueError('unchecked Items edit unexpectedly changed checksum')
    if 'potion_quantity' in changes and after['entries'][0]['quantity']!=changes['potion_quantity']:
        raise ValueError('Potion quantity postcondition failed')
    if 'insert_antidote' in changes and after['can_insert_antidote']:
        raise ValueError('Antidote insertion postcondition failed')
    return candidate,{'before':before,'after':after,'changed_offsets':diffs,'verifier_accepted':True}
