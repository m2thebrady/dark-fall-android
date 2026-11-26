"""Renew and reposition garden ground decals while preserving existing terrain dimensions."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent;art=root/'art-v1537'
    meta=json.loads((art/'metadata.json').read_text())
    assert len(meta['plots'])==15 and len(meta['variants'])==6
    m=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html);assert m
    data=json.loads(m[1])
    for t in meta['tiles']:
        assert t['key'] in data
        assert hashlib.sha256(base64.b64decode(data[t['key']].split(',')[1])).hexdigest()==t['sourceSha256']
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        data[t['key']]='data:image/webp;base64,'+base64.b64encode(b).decode()
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    # Keep the older diagnostic in sync with the current real plot positions.
    m=re.search(rb'const rh1526Gardens=(\{[^\n]+?\});',html);assert m
    data=json.loads(m[1]);assert len(data['gardens'])==len(meta['plots'])
    for g,q in zip(data['gardens'],meta['plots']):
        assert g['name']==q['name'] and [g['x'],g['y'],g['w'],g['h']]==q['old']
        for k in ('x','y','w','h','roadClearance'):g[k]=q[k]
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode();assert html.count(a)==1,(a,html.count(a))
        html=html.replace(a,b,1)
    edit('function rh1457Shade(o){','const rh1537Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1537.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('publicRenewal:rh1536Status,','gardenRenewal:rh1537GardenStatus,reviewGardenRenewal:new URLSearchParams(location.search).has("graphicsAudit")?rh1537Review:undefined,publicRenewal:rh1536Status,')
    return b''.join(p if i%2 else p.replace(b'V1536',b'V1537') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
