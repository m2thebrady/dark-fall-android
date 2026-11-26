"""Renew the Royal Castle forecourt, processional axis and fountain square."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent
    art=root/'art-v1531'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(t):
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)
    assert a
    data=json.loads(a[1])
    for t in meta['ground']:
        assert t['key'] in data
        data[t['key']]=uri(t)
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    matches=list(re.finditer(rb'rh1315CourtArt\.src="([^"]+)"',html))
    assert len(matches)==1
    a=matches[0]
    html=html[:a.start(1)]+uri(meta['overlay']).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1531RoyalMeta='+json.dumps(meta,separators=(',',':'))+';\n'
    edit('function rh1457Shade(o){',info+(root/'royal-haven-v1531.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('commercialPaving:rh1530CommercialStatus,','royalPaving:rh1531RoyalStatus,reviewRoyalPaving:new URLSearchParams(location.search).has("graphicsAudit")?rh1531ReviewRoyal:undefined,commercialPaving:rh1530CommercialStatus,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1530',b'V1531') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
