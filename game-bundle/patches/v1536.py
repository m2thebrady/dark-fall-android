"""Renew Royal Haven's public well, bell court and notice stand."""
import re,json,base64,hashlib
from pathlib import Path

def apply(html):
    root=Path(__file__).parent;art=root/'art-v1536'
    meta=json.loads((art/'metadata.json').read_text())
    models={m['key']:m for m in meta['models']}
    def uri(m):
        b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode()
    def replace_assets(pattern,keys):
        nonlocal html
        m=re.search(pattern,html);assert m
        d=json.loads(m[1])
        for k in keys:
            assert k in d;d[k]=uri(models[k])
        html=html[:m.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[m.end(1):]
    replace_assets(rb'for\(const \[k,src\] of Object.entries\((\{"stall0"[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1475Images\[k\]=im;', ['well'])
    replace_assets(rb'for\(const \[k,src\] of Object.entries\((\{"rh1499bellCourt"[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;', ['rh1499bellCourt','rh1499notice'])
    m=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html);assert m
    data=json.loads(m[1])
    for t in meta['ground']:
        assert hashlib.sha256(base64.b64decode(data[t['key']].split(',')[1])).hexdigest()==t['sourceSha256']
        data[t['key']]=uri(t)
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    # Civic data drives both collision and the established audit, so update its
    # authored geometry, not a detached second collider.
    m=re.search(rb'const rh1499Civic=\(\(\)=>\{\n const data=(\{[^\n]+?\}),objects=\[data.bellCourt,data.notice,data.stoneSeat\];',html);assert m
    data=json.loads(m[1]);notice=data['notice']
    assert notice['x']==5145 and notice['y']==1291.026
    assert notice['polyParts']==[[[-32.167,-9.218],[23.051,0.0],[32.167,-12.835],[-23.051,-22.053]]]
    notice['dx']=notice['artDy']=0
    notice['poly']=[[-31,-16],[31,-16],[31,-2],[-31,-2]]
    notice['polyParts']=[notice['poly']]
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    def metadata(name,edit):
        nonlocal html
        m=re.search(rb'const '+name.encode()+rb'=(\{[^\n]+?\});',html);assert m
        d=json.loads(m[1]);edit(d)
        html=html[:m.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[m.end(1):]
    def update(m,k):
        m['file']='art-v1536/'+models[k]['file']
        m['sourceBounds']=models[k]['sourceBounds']
    metadata('rh1510MarketMeta',lambda d:update(d['well'],'well'))
    metadata('rh1515LayoutMeta',lambda d:update(d['civic']['rh1499bellCourt'],'rh1499bellCourt'))
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:80],html.count(old))
        html=html.replace(old,new,1)
    edit('function rh1457Shade(o){','const rh1536Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1536.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('wallRenewal:rh1535WallStatus,','publicRenewal:rh1536Status,reviewPublic:new URLSearchParams(location.search).has("graphicsAudit")?rh1536Review:undefined,wallRenewal:rh1535WallStatus,')
    return b''.join(p if i%2 else p.replace(b'V1535',b'V1536') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
