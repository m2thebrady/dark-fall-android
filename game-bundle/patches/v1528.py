"""Royal Haven: remove 12 detached decorative walls and bake six open flagstone walks."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent
    art=root/'art-v1528'
    meta=json.loads((art/'metadata.json').read_text())
    a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)
    assert a
    data=json.loads(a[1])
    for t in meta['ground']:
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP' and t['key'] in data
        data[t['key']]='data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1528CourtMeta='+json.dumps(meta,separators=(',',':'))+';\n'
    edit('function rh1457Shade(o){',info+(root/'royal-haven-v1528.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('rh1520Install();rh1521MarketInstall();rh1522Install();rh1525Install();','rh1520Install();rh1521MarketInstall();rh1522Install();rh1525Install();rh1528Install();')
    edit('marketRenewal:rh1527MarketRenewal,','streetClearance:rh1528Status,reviewStreetClearance:new URLSearchParams(location.search).has("graphicsAudit")?rh1528Review:undefined,marketRenewal:rh1527MarketRenewal,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1527',b'V1528') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
