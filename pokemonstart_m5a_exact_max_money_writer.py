#!/usr/bin/env python3
"""Exact M5A proof writer: one retained input, 3000 -> 9,999,999 money only.

This is deliberately not a reusable money editor. It accepts one exact SHA-256,
requires the expected starting semantic value, writes only to a new path, and
requires the complete output byte diff to match the sealed proof contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path

FLASH_SIZE = 0x20000
RTC_FOOTER_SIZE = 0x10
SECTOR_SIZE = 0x1000
SLOT_SECTORS = 14
FILE_SIGNATURE = 0x08012025
SECTION_ID_OFFSET = 0xFF4
SECTION_CHECKSUM_OFFSET = 0xFF6
SECTION_SIGNATURE_OFFSET = 0xFF8
SECTION_COUNTER_OFFSET = 0xFFC
SECTION_LENGTHS = (0xF24,0xFF0,0xFF0,0xFF0,0xD98,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0x450)
MONEY_SECTION_ID = 1
MONEY_OFFSET = 0x0290
KEY_SECTION_ID = 0
KEY_OFFSET = 0x0F20

EXPECTED_INPUT_SHA256 = "fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b"
EXPECTED_START_MONEY = 3000
TARGET_MONEY = 9_999_999
EXPECTED_ACTIVE_SLOT = 1
EXPECTED_COUNTER = 1
EXPECTED_SECTION0_PHYSICAL = 15
EXPECTED_SECTION1_PHYSICAL = 16
EXPECTED_KEY = 0x00000000
# Sealed after independent in-memory derivation; None during pre-seal computation.
EXPECTED_OUTPUT_SHA256: str | None = "e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69"
EXPECTED_DIFFS = {
    0x10290: (0xB8, 0x7F),
    0x10291: (0x0B, 0x96),
    0x10292: (0x00, 0x98),
    0x10FF6: (0x62, 0xC1),
    0x10FF7: (0x91, 0x1C),
}

class ProofError(ValueError):
    pass

def u16(b: bytes|bytearray, off: int) -> int:
    return struct.unpack_from('<H', b, off)[0]

def u32(b: bytes|bytearray, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]

def checksum(data: bytes|bytearray) -> int:
    if len(data) % 4:
        raise ProofError('checksum length is not divisible by 4')
    total = 0
    for off in range(0, len(data), 4):
        total = (total + u32(data, off)) & 0xFFFFFFFF
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF

def parse_slot(flash: bytes|bytearray, slot_index: int):
    base_sector = slot_index * SLOT_SECTORS
    raw = [bytes(flash[(base_sector+i)*SECTOR_SIZE:(base_sector+i+1)*SECTOR_SIZE]) for i in range(SLOT_SECTORS)]
    erased = [s == b'\xFF'*SECTOR_SIZE for s in raw]
    if all(erased):
        return {'state':'empty','counter':None,'sections':{}}
    if any(erased):
        raise ProofError(f'slot {slot_index} partially erased')
    sections = {}
    counters = set()
    for i, sec in enumerate(raw):
        physical = base_sector+i
        sid = u16(sec, SECTION_ID_OFFSET)
        if sid >= SLOT_SECTORS or sid in sections:
            raise ProofError(f'slot {slot_index} invalid/duplicate section id {sid}')
        sig = u32(sec, SECTION_SIGNATURE_OFFSET)
        if sig != FILE_SIGNATURE:
            raise ProofError(f'slot {slot_index} section {sid} bad signature')
        stored = u16(sec, SECTION_CHECKSUM_OFFSET)
        calc = checksum(sec[:SECTION_LENGTHS[sid]])
        if stored != calc:
            raise ProofError(f'slot {slot_index} section {sid} checksum mismatch')
        ctr = u32(sec, SECTION_COUNTER_OFFSET)
        counters.add(ctr)
        sections[sid] = {'physical':physical,'sector':sec,'counter':ctr}
    if set(sections) != set(range(SLOT_SECTORS)):
        raise ProofError(f'slot {slot_index} missing section ids')
    if len(counters) != 1:
        raise ProofError(f'slot {slot_index} inconsistent counters')
    return {'state':'valid','counter':next(iter(counters)),'sections':sections}

def signed32(v:int)->int:
    return v if v < 0x80000000 else v-0x100000000

def active_slot(slots):
    a,b=slots
    if a['state']=='empty' and b['state']=='valid': return 1
    if a['state']=='valid' and b['state']=='empty': return 0
    if a['state']!='valid' or b['state']!='valid': raise ProofError('cannot choose active slot')
    ca,cb=a['counter'],b['counter']
    if ca==cb: raise ProofError('equal counters')
    if {ca,cb}=={0xFFFFFFFF,0}: return 0 if ca==0 else 1
    return 1 if signed32(ca)<signed32(cb) else 0

def inspect(raw: bytes|bytearray):
    if len(raw) not in (FLASH_SIZE, FLASH_SIZE+RTC_FOOTER_SIZE):
        raise ProofError('unsupported save size')
    flash = raw[:FLASH_SIZE]
    slots=(parse_slot(flash,0),parse_slot(flash,1))
    active=active_slot(slots)
    s=slots[active]
    sec0=s['sections'][KEY_SECTION_ID]
    sec1=s['sections'][MONEY_SECTION_ID]
    key=u32(sec0['sector'],KEY_OFFSET)
    stored=u32(sec1['sector'],MONEY_OFFSET)
    money=stored ^ key
    return {
        'slots':slots,'active_slot':active,'counter':s['counter'],
        'section0_physical':sec0['physical'],'section1_physical':sec1['physical'],
        'key':key,'stored':stored,'money':money,
        'footer':bytes(raw[FLASH_SIZE:]),
        'sector28':bytes(flash[28*SECTOR_SIZE:29*SECTOR_SIZE]),
        'sector29':bytes(flash[29*SECTOR_SIZE:30*SECTOR_SIZE]),
        'sector30':bytes(flash[30*SECTOR_SIZE:31*SECTOR_SIZE]),
        'sector31':bytes(flash[31*SECTOR_SIZE:32*SECTOR_SIZE]),
    }

def exact_diffs(before: bytes, after: bytes):
    if len(before)!=len(after): raise ProofError('length changed')
    return {i:(a,b) for i,(a,b) in enumerate(zip(before,after)) if a!=b}

def derive_candidate(raw: bytes) -> tuple[bytes, dict]:
    source_sha=hashlib.sha256(raw).hexdigest()
    if source_sha != EXPECTED_INPUT_SHA256:
        raise ProofError(f'unrecognized input SHA-256 {source_sha}')
    pre=inspect(raw)
    required={
        'active_slot':EXPECTED_ACTIVE_SLOT,'counter':EXPECTED_COUNTER,
        'section0_physical':EXPECTED_SECTION0_PHYSICAL,
        'section1_physical':EXPECTED_SECTION1_PHYSICAL,'key':EXPECTED_KEY,
        'money':EXPECTED_START_MONEY,
    }
    for k,v in required.items():
        if pre[k]!=v: raise ProofError(f'{k} mismatch: got {pre[k]!r}, expected {v!r}')

    out=bytearray(raw)
    money_abs=pre['section1_physical']*SECTOR_SIZE + MONEY_OFFSET
    struct.pack_into('<I',out,money_abs,TARGET_MONEY ^ pre['key'])
    sec_base=pre['section1_physical']*SECTOR_SIZE
    new_checksum=checksum(out[sec_base:sec_base+SECTION_LENGTHS[MONEY_SECTION_ID]])
    struct.pack_into('<H',out,sec_base+SECTION_CHECKSUM_OFFSET,new_checksum)
    candidate=bytes(out)

    diffs=exact_diffs(raw,candidate)
    if diffs != EXPECTED_DIFFS:
        raise ProofError(f'complete diff mismatch: {diffs!r}')
    post=inspect(candidate)
    if post['money'] != TARGET_MONEY:
        raise ProofError(f'post money mismatch {post["money"]}')
    for k in ('active_slot','counter','section0_physical','section1_physical','key'):
        if post[k] != pre[k]: raise ProofError(f'post invariant changed: {k}')
    for k in ('footer','sector28','sector29','sector30','sector31'):
        if post[k] != pre[k]: raise ProofError(f'preserved region changed: {k}')
    output_sha=hashlib.sha256(candidate).hexdigest()
    if EXPECTED_OUTPUT_SHA256 is not None and output_sha != EXPECTED_OUTPUT_SHA256:
        raise ProofError(f'output SHA-256 mismatch: {output_sha}')
    return candidate, {
        'input_sha256':source_sha,'output_sha256':output_sha,
        'active_slot':pre['active_slot'],'counter':pre['counter'],
        'encryption_key':pre['key'],'starting_money':pre['money'],'target_money':post['money'],
        'section1_physical':pre['section1_physical'],'new_section1_checksum':new_checksum,
        'diffs':{f'0x{k:05X}':[f'0x{v[0]:02X}',f'0x{v[1]:02X}'] for k,v in sorted(diffs.items())},
    }

def write_new(input_path: Path, output_path: Path):
    if input_path.resolve() == output_path.resolve(): raise ProofError('output aliases input')
    if output_path.exists(): raise ProofError('output already exists')
    raw=input_path.read_bytes()
    before_sha=hashlib.sha256(raw).hexdigest()
    candidate,receipt=derive_candidate(raw)
    if hashlib.sha256(input_path.read_bytes()).hexdigest()!=before_sha:
        raise ProofError('source changed before publication')
    fd=os.open(output_path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(candidate); f.flush(); os.fsync(f.fileno())
    except Exception:
        try: output_path.unlink()
        except OSError: pass
        raise
    reread=output_path.read_bytes()
    if reread != candidate:
        output_path.unlink(missing_ok=True); raise ProofError('published bytes differ')
    if exact_diffs(raw,reread) != EXPECTED_DIFFS:
        output_path.unlink(missing_ok=True); raise ProofError('persisted diff mismatch')
    post=inspect(reread)
    if post['money'] != TARGET_MONEY:
        output_path.unlink(missing_ok=True); raise ProofError('persisted semantic mismatch')
    if hashlib.sha256(input_path.read_bytes()).hexdigest()!=before_sha:
        output_path.unlink(missing_ok=True); raise ProofError('source changed during publication')
    receipt['source_immutable']=True
    receipt['output_path']=str(output_path)
    return receipt

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    a=p.parse_args(argv)
    try: receipt=write_new(a.input,a.output)
    except (OSError,ProofError) as e:
        print(json.dumps({'status':'REJECTED','reason':str(e)},indent=2)); return 2
    print(json.dumps({'status':'EXACT_CANARY_CREATED',**receipt},indent=2,sort_keys=True)); return 0

if __name__=='__main__':
    raise SystemExit(main())
