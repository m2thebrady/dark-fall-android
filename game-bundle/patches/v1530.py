"""Re-pave the western and central commercial terraces and main streets."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent
    art=root/'art-v1530'
    meta=json.loads((art/'metadata.json').read_text())
    a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)
    assert a
    data=json.loads(a[1])
    for t in meta['ground']:
        payload=(art/t['file']).read_bytes()
        assert len(payload)==t['bytes'] and hashlib.sha256(payload).hexdigest()==t['sha256']
        assert payload[:4]==b'RIFF' and payload[8:12]==b'WEBP' and t['key'] in data
        data[t['key']]='data:image/webp;base64,'+base64.b64encode(payload).decode('ascii')
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1530CommercialMeta='+json.dumps(meta,separators=(',',':'))+';\n'
    edit('function rh1457Shade(o){',info+(root/'royal-haven-v1530.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('marketCourt:rh1529MarketStatus,','commercialPaving:rh1530CommercialStatus,reviewCommercialPaving:new URLSearchParams(location.search).has("graphicsAudit")?rh1530ReviewCommercial:undefined,marketCourt:rh1529MarketStatus,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1529',b'V1530') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
