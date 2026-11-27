"""Refine Royal Haven's oversized paving and retire intrusive lane planters."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent;art=root/'art-v1542'
    meta=json.loads((art/'metadata.json').read_text())
    assert len(meta['regions'])==5 and len(meta['ground'])==12 and len(meta['models'])==6 and len(meta['removed'])==12 and len(meta['placements'])==10
    def load(m):
        b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode()
    terrain=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html);assert terrain
    data=json.loads(terrain[1])
    for m in meta['ground']:
        key=m['key'];assert key in data
        old=base64.b64decode(data[key].split(',')[1]);assert hashlib.sha256(old).hexdigest()==m['oldSHA256']
        data[key]=load(m)
    html=html[:terrain.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[terrain.end(1):]
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode();assert html.count(a)==1,(a[:120],html.count(a));html=html.replace(a,b,1)
    models={m['key']:load(m) for m in meta['models']}
    declaration='const rh1542Meta='+json.dumps(meta,separators=(',',':'))+';\nconst rh1542Art={};for(const [k,src] of Object.entries('+json.dumps(models,separators=(',',':'))+')){const im=rh1200Image();im.src=src;rh1542Art[k]=im;}\n'
    edit('function rh174Garden(o){',declaration+(root/'royal-haven-v1542.js').read_text()+'\nfunction rh174Garden(o){')
    edit('const im=rh1418GardenImage(o)||(o.temple?', 'const im=rh1542GardenImage(o)||rh1418GardenImage(o)||(o.temple?')
    edit('rh1541Install();\ntry{rh1434Grid=', 'rh1541Install();\nrh1542Install();\ntry{rh1434Grid=')
    edit('tradeRenewal:rh1541Status,','pavingRefinement:rh1542Status,reviewPavingRefinement:new URLSearchParams(location.search).has("graphicsAudit")?rh1542Review:undefined,tradeRenewal:rh1541Status,')
    return b''.join(p if i%2 else p.replace(b'V1541',b'V1542') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))
if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
