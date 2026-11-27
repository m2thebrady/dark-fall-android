"""Royal Haven permanent spice and pottery kiosks, plus baked flagstone aprons."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent
    art=root/'art-v1527'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(m):
        b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    def update(pattern,fn):
        nonlocal html
        a=re.search(pattern,html)
        assert a,pattern
        d=json.loads(a[1]);fn(d)
        html=html[:a.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[a.end(1):]
    def tiles(d):
        for t in meta['ground']:
            assert t['key'] in d
            d[t['key']]=uri(t)
    update(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',tiles)
    def models(d):
        for key,m in meta['stalls'].items():
            assert key in d
            d[key]=uri(m)
    update(rb'const rh1512MarketVariants=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',models)
    def measurements(d):
        for key,m in meta['stalls'].items():
            assert key in d
            d[key]={**d[key],**{k:m[k] for k in ('file','width','height','sourceBounds','name','counterHeight')}}
    update(rb'const rh1512FortMeta=(\{[^\n]+?\});',measurements)
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1527MarketMeta='+json.dumps(meta,separators=(',',':'))+';\n'
    edit('function rh1457Shade(o){',info+(root/'royal-haven-v1527.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('gardens:rh1526GardenStatus,','marketRenewal:rh1527MarketRenewal,reviewMarketRenewal:new URLSearchParams(location.search).has("graphicsAudit")?rh1527ReviewMarket:undefined,gardens:rh1526GardenStatus,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1526',b'V1527') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
