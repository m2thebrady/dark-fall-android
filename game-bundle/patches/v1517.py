"""Royal Haven residential infill and less uniform pedestrian street material."""
from pathlib import Path
import base64,json,re
def apply(html:bytes)->bytes:
    root=Path(__file__).parent;art=root/'art-v1517';meta=json.loads((art/'layout-metadata.json').read_text());homes=meta['homes']
    assert set(homes)=={'forward','deepstone'}
    def dump(obj):return json.dumps(obj,separators=(',',':')).encode()
    def url(m):return 'data:image/webp;base64,'+base64.b64encode((art/m['file']).read_bytes()).decode()
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode()
        if html.count(a)!=1:raise ValueError(f'V1517 anchor count {html.count(a)}: {a[:100]}')
        html=html.replace(a,b,1)
    def update(rx,fn):
        nonlocal html
        m=re.search(rx,html)
        if not m:raise ValueError(f'Missing V1517 anchor {rx}')
        d=json.loads(m[1]);fn(d)
        html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    def artmeta(d):
        for k,m in homes.items():
            d['home:'+k].update({f:m[f] for f in ('file','width','height','door','flues','lanterns')})
    update(rb'const rh1510ArtMeta=(\{[^\n]+?\});\n',artmeta)
    update(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({'home:'+k:url(m) for k,m in homes.items()}))
    def geometry(d):
        for o in d:
            if o['k'] in homes:
                # The cottage is set back into its original main body; the
                # stone home keeps the old relative door used by relocation.
                for key in ['door','doors','flue2','flueY2','doorX','poly','polyParts']:o.pop(key,None)
                o.update(homes[o['k']]['geometry'])
    update(rb'const rh1464Homes=(\[[^\n]+?\]);',geometry)
    found=set()
    for m in reversed(list(re.finditer(rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;',html))):
        d=json.loads(m[1]);keys=d.keys()&homes.keys()
        if not keys:continue
        for k in keys:
            d[k]=url(homes[k]);d.pop(k+'Night',None);found.add(k)
        html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    assert found==set(homes)
    i=html.index(b'function rh1457Shade(')
    html=html[:i]+b'const rh1517Meta='+dump(meta)+b';\n'+(root/'royal-haven-v1517.js').read_bytes()+b'\n'+html[i:]
    edit('function rh1511DistrictMeta(o){return rh1511DistrictData[o.k]||(o.k==="townhouse"?rh1516Meta.home:null);}',
         'function rh1511DistrictMeta(o){return rh1517Meta.homes[o.k]||rh1511DistrictData[o.k]||(o.k==="townhouse"?rh1516Meta.home:null);}')
    edit('rh1516PrepareStreet();rh1510PlaceAnnexes();','rh1516PrepareStreet();rh1517PrepareStreet();rh1510PlaceAnnexes();')
    edit('rh1516StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);','rh1516StreetGround(cx,cy);rh1517StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
    edit('function rh1510GroundReset(){rh1516StreetSurfaces.clear();','function rh1510GroundReset(){rh1517WearCache.clear();rh1516StreetSurfaces.clear();')
    edit('foundryDistrict:rh1516DistrictStatus,reviewFoundry:', 'foundryDistrict:rh1516DistrictStatus,residentialDistrict:rh1517ResidentialStatus,reviewResidential:new URLSearchParams(location.search).has("graphicsAudit")?rh1517ReviewResidential:undefined,reviewFoundry:')
    assert html.count(b'V1516')>=108
    return html.replace(b'V1516',b'V1517')
