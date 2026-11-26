"""Realistic tree silhouettes and a read-only interior readiness survey."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent;art=root/'art-v1540'
    meta=json.loads((art/'metadata.json').read_text());models={m['key']:m for m in meta['models']}
    assert len(models)==8
    m=re.search(rb'const rh117Images=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',html);assert m
    data=json.loads(m[1])
    for key,model in models.items():
        assert key in data and model['visibleHeight']>=.68 and abs(model['footOffset'])<=1
        b=(art/model['file']).read_bytes()
        assert len(b)==model['bytes'] and hashlib.sha256(b).hexdigest()==model['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        data[key]='data:image/webp;base64,'+base64.b64encode(b).decode()
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode();assert html.count(a)==1,(a[:120],html.count(a));html=html.replace(a,b,1)
    edit('function rh1457Shade(o){','const rh1540Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1540.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('fixtureRenewal:rh1538FixtureStatus,','canopyRenewal:rh1540CanopyStatus,interiorReadiness:new URLSearchParams(location.search).has("graphicsAudit")?rh1540InteriorReadiness:undefined,fixtureRenewal:rh1538FixtureStatus,')
    # Only version labels, not base64 asset data.
    return b''.join(p if i%2 else p.replace(b'V1539',b'V1540') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))
if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
