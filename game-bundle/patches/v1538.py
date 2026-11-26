"""Replace flat residential and observatory scenery with detailed cutouts."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent;art=root/'art-v1538'
    meta=json.loads((art/'metadata.json').read_text())
    models={m['key']:m for m in meta['models']}
    def uri(key):
        m=models[key];b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode()
    m=re.search(rb'const rh1423HouseArt=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1423HouseArt\[k\]=im;\}',html);assert m
    old=json.loads(m[1])
    assert len(old)==19
    keys=[k for k in old if k not in meta['aliases']]
    fresh={k:uri(k) for k in keys}
    assert len(fresh)==13 and len(meta['aliases'])==6
    decl='const rh1423HouseArt={};for(const [k,src] of Object.entries('+json.dumps(fresh,separators=(',',':'))+')){const im=rh1200Image();im.src=src;rh1423HouseArt[k]=im;}\n'
    for k,v in meta['aliases'].items():decl+=f'rh1423HouseArt.{k}=rh1423HouseArt.{v};'
    html=html[:m.start()]+decl.encode()+html[m.end():]
    m=re.search(rb'const rh1417Art=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)',html);assert m
    data=json.loads(m[1])
    for key in ('armillary','arcaneTable'):assert key in data;data[key]=uri(key)
    html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode();assert html.count(a)==1,(a[:120],html.count(a))
        html=html.replace(a,b,1)
    edit("const rack={x:4410,y:1930,w:81,h:45,rx:34,ry:10,k:'houseWood',flip:false,artisan1495:true};",
         "const rack={x:4410,y:1930,w:81,h:45,rx:34,ry:10,k:'houseWood',variant:2,phase:0,flip:false,artisan1495:true};")
    edit('function rh1457Shade(o){','const rh1538Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1538.js').read_text()+'\nfunction rh1457Shade(o){')
    edit('rh1534Install();\ntry{rh1434Grid=','rh1534Install();\nrh1538Install();\ntry{rh1434Grid=')
    edit('gardenRenewal:rh1537GardenStatus,','fixtureRenewal:rh1538FixtureStatus,reviewFixtures:new URLSearchParams(location.search).has("graphicsAudit")?rh1538Review:undefined,gardenRenewal:rh1537GardenStatus,')
    return b''.join(p if i%2 else p.replace(b'V1537',b'V1538') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
