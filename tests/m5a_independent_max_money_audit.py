#!/usr/bin/env python3
"""Independent audit for the one exact M5A max-money candidate.
Does not import the proof writer.
"""
from pathlib import Path
import hashlib, struct, json, sys
FLASH=0x20000; SECTOR=0x1000; SLOTS=14; SIG=0x08012025
LENS=(0xF24,0xFF0,0xFF0,0xFF0,0xD98,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0xFF0,0x450)
IN_SHA='fcbdef7ac3e629ec3884def5df1894f108a267f639692791796bb5389783fe0b'
OUT_SHA='e949a584c9a260030c0773bc34b117975e4e15f84ae589fa668812979f32ec69'
DIFF={0x10290:(0xB8,0x7F),0x10291:(0x0B,0x96),0x10292:(0x00,0x98),0x10FF6:(0x62,0xC1),0x10FF7:(0x91,0x1C)}
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def csum(data):
    t=0
    for o in range(0,len(data),4): t=(t+u32(data,o))&0xffffffff
    return ((t>>16)+(t&0xffff))&0xffff
def parse_slot(raw,idx):
    flash=raw[:FLASH]; base=idx*SLOTS; secs=[]
    for i in range(SLOTS): secs.append(flash[(base+i)*SECTOR:(base+i+1)*SECTOR])
    if all(s==b'\xff'*SECTOR for s in secs): return {'state':'empty'}
    if any(s==b'\xff'*SECTOR for s in secs): raise AssertionError('partial erased')
    byid={}; counters=set(); order=[]
    for i,s in enumerate(secs):
        sid=u16(s,0xff4); order.append(sid)
        assert 0<=sid<14 and sid not in byid
        assert u32(s,0xff8)==SIG
        assert u16(s,0xff6)==csum(s[:LENS[sid]])
        counters.add(u32(s,0xffc)); byid[sid]=(base+i,s)
    assert set(byid)==set(range(14)); assert len(counters)==1
    return {'state':'valid','counter':next(iter(counters)),'byid':byid,'order':order}
def audit(srcp,outp):
    src=Path(srcp).read_bytes(); out=Path(outp).read_bytes()
    assert hashlib.sha256(src).hexdigest()==IN_SHA
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    assert len(src)==len(out)==0x20010
    diffs={i:(a,b) for i,(a,b) in enumerate(zip(src,out)) if a!=b}
    assert diffs==DIFF, diffs
    ss=[parse_slot(src,0),parse_slot(src,1)]; oslots=[parse_slot(out,0),parse_slot(out,1)]
    assert ss[0]['state']==oslots[0]['state']=='empty'
    assert ss[1]['counter']==oslots[1]['counter']==1
    assert ss[1]['order']==oslots[1]['order']==[13,0,1,2,3,4,5,6,7,8,9,10,11,12]
    s0p,s0=oslots[1]['byid'][0]; s1p,s1=oslots[1]['byid'][1]
    assert s0p==15 and s1p==16
    key=u32(s0,0xf20); stored=u32(s1,0x290); money=key^stored
    assert key==0 and money==9_999_999
    assert src[FLASH:]==out[FLASH:]
    for sec in (28,29,30,31):
        a=sec*SECTOR; b=a+SECTOR; assert src[a:b]==out[a:b]
    return {'status':'PASS','input_sha256':IN_SHA,'output_sha256':OUT_SHA,'money':money,'key':key,
            'changed_offsets':[f'0x{x:05X}' for x in sorted(diffs)],'all_section_checksums_valid':True,
            'source_footer_preserved':True,'sectors28_31_preserved':True}
if __name__=='__main__':
    print(json.dumps(audit(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
