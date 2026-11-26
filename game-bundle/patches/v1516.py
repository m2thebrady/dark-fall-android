"""Royal Haven's western foundry district: unique trade buildings, street access and older gallery replacement."""
from pathlib import Path
import base64,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent;art=root/'art-v1516';meta=json.loads((art/'layout-metadata.json').read_text())
    shops=meta['shops'];home=meta['home'];gallery=meta['gallery']
    assert set(shops)=={'Weapon Smith','Armor Smith','Leatherworker'}
    def dump(o):return json.dumps(o,separators=(',',':')).encode()
    def url(m):return 'data:image/webp;base64,'+base64.b64encode((art/m['file']).read_bytes()).decode()
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode()
        if html.count(a)!=1:raise ValueError(f'V1516 anchor count {html.count(a)}: {a[:120]}')
        html=html.replace(a,b,1)
    def update(rx,fn):
        nonlocal html
        m=re.search(rx,html)
        if not m:raise ValueError(f'Missing anchor {rx}')
        d=json.loads(m[1]);fn(d)
        html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    def artmeta(d):
        for k,m in {**shops,'home:townhouse':home}.items():
            fields=['file','width','height','door','flues','lanterns']+(['fire'] if k=='Weapon Smith' else [])
            d[k].update({f:m[f] for f in fields})
    update(rb'const rh1510ArtMeta=(\{[^\n]+?\});\n',artmeta)
    update(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({k:url(m) for k,m in {**shops,'home:townhouse':home}.items()}))
    # Retire the old angled townhouse sprite and its old night overlay; maintain
    # the same world lot and home collision extents while aligning its doorstep.
    update(rb'const rh1464Homes=(\[[^\n]+?\]);',lambda d:next(o for o in d if o['k']=='townhouse').update(home['geometry']))
    found=False
    matches=list(re.finditer(rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;',html))
    for m in reversed(matches):
        d=json.loads(m[1])
        if 'townhouse' not in d:continue
        d['townhouse']=url(home);d.pop('townhouseNight',None);found=True
        html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    assert found
    # Gallery fits its two actual supports; the middle is genuine alpha, not
    # a painted brown wall. The two side supports become collidable.
    update(rb'const rh1462Art=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({'timber':url(gallery)}))
    edit("const rh1462Galleries=[{x:580,y:1301,w:112,k:'timber'}];","const rh1462Galleries="+json.dumps([gallery['geometry']],separators=(',',':'))+";")
    edit('function rh1462Bounds(o){const h=o.w*132/104;', 'function rh1462Bounds(o){const h=o.h??o.w*132/104;')
    edit('function rh1464Blocked(x,y){return rh1464Homes.some(o=>','function rh1464Blocked(x,y){return rh1462Galleries.some(o=>o.polyParts?.some(poly=>rh1472Poly(poly,x-o.x,y-o.y)))||rh1464Homes.some(o=>')
    # Townhouse uses the same subtle day/night glass and threshold blending as
    # the district assets, without changing the existing nine-asset audit.
    edit('function rh1511DistrictMeta(o){return rh1511DistrictData[o.k]||null;}','function rh1511DistrictMeta(o){return rh1511DistrictData[o.k]||(o.k==="townhouse"?rh1516Meta.home:null);}')
    # Early placement keeps precise street-front offsets instead of the
    # original generic shop footprint.
    def foot(d):
        for name,m in shops.items():
            xs=[x for q in m['geometry']['parts'] for x,y in q];d[name]=[min(xs),max(xs)]
    update(rb'const rh1328Foot=(\{[^\n]+?\});',foot)
    i=html.index(b'function rh1457Shade(')
    html=html[:i]+b'const rh1516Meta='+dump(meta)+b';\n'+(root/'royal-haven-v1516.js').read_bytes()+b'\n'+html[i:]
    edit('const choose=s=>rh1515Commerce.handles(s)?rh1515Commerce:', 'const choose=s=>rh1516Foundry.handles(s)?rh1516Foundry:rh1515Commerce.handles(s)?rh1515Commerce:')
    edit('return {handles:s=>rh1515Commerce.handles(s)||','return {handles:s=>rh1516Foundry.handles(s)||rh1515Commerce.handles(s)||')
    # The clipped animated fire is drawn inside the cutaway facade, not at
    # stale screen coordinates from a previous model.
    edit("function rh1273BuildingFire(s,t){if(s.name==='Weapon Smith'){","function rh1273BuildingFire(s,t){if(rh1516Foundry.ready(s))return;if(s.name==='Weapon Smith'){")
    edit('rh1515PrepareStreet();rh1510PlaceAnnexes();','rh1515PrepareStreet();rh1516PrepareStreet();rh1510PlaceAnnexes();')
    edit('rh1515StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);','rh1515StreetGround(cx,cy);rh1516StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
    edit('function rh1510GroundReset(){rh1515StreetSurfaces.clear();','function rh1510GroundReset(){rh1516StreetSurfaces.clear();rh1515StreetSurfaces.clear();')
    edit('merchantQuarter:rh1515QuarterStatus,reviewQuarter:','merchantQuarter:rh1515QuarterStatus,foundryDistrict:rh1516DistrictStatus,reviewFoundry:new URLSearchParams(location.search).has("graphicsAudit")?rh1516ReviewDistrict:undefined,reviewQuarter:')
    assert html.count(b'V1515')>=108
    return html.replace(b'V1515',b'V1516')
