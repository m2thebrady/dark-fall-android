"""Royal Haven: attached merchant row and more individual civic architecture."""
from pathlib import Path
import base64,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent;art=root/'art-v1515';meta=json.loads((art/'layout-metadata.json').read_text())
    shops=meta['shops'];civic=meta['civic'];assert set(shops)=={'General Store','Item Shop','Town Residence'}
    def dump(o):return json.dumps(o,separators=(',',':')).encode()
    def url(m):return 'data:image/webp;base64,'+base64.b64encode((art/m['file']).read_bytes()).decode()
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode()
        if html.count(a)!=1:raise ValueError(f'V1515 anchor count {html.count(a)}: {a[:120]}')
        html=html.replace(a,b,1)
    def update(rx,fn):
        nonlocal html
        m=re.search(rx,html)
        if not m:raise ValueError(f'Missing anchor {rx}')
        d=json.loads(m[1]);fn(d)
        html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    def shopmeta(d):
        for k,m in shops.items():d[k].update({f:m[f] for f in ['file','width','height','door','flues','lanterns']})
        d.pop('home:leftcourt',None)
    update(rb'const rh1510ArtMeta=(\{[^\n]+?\});\n',shopmeta)
    def shopart(d):
        d.update({k:url(m) for k,m in shops.items()});d.pop('home:leftcourt',None)
    update(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',shopart)
    # Retire the removed house art and its collision object; leave unrelated
    # residential homes, doors and interiors untouched.
    update(rb'const rh1464Homes=(\[[^\n]+?\]);',lambda d:d.__setitem__(slice(None),[o for o in d if o['k']!='leftcourt']))
    matches=list(re.finditer(rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;',html))
    found=set()
    for m in reversed(matches):
        d=json.loads(m[1]);changed=False
        for k in ['leftcourt','leftcourtNight']:
            if k in d:d.pop(k);changed=True
        for k,m0 in civic.items():
            if k in d:d[k]=url(m0);d.pop(k+'Night',None);found.add(k);changed=True
        if changed:html=html[:m.start(1)]+dump(d)+html[m.end(1):]
    assert found==set(civic)
    bell=civic['rh1499bellCourt'];seat=civic['rh1499stoneSeat']
    update(rb'const rh1511DistrictData=(\{[^\n]+?\});\n',lambda d:d.update({'rh1499bellCourt':{f:bell[f] for f in ['file','width','height','sourceBounds','flues','windows','openings']}}))
    # Room and name interaction anchors remain unchanged. Town Residence
    # is now a square-to-street front with a physically unobstructed entrance.
    m=re.search(rb'const rh1502Art=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1502Art\[k\]=im;\}',html);assert m
    d=json.loads(m[1]);d.pop('townres');d.pop('townresNight',None)
    new=m[0][:m.start(1)-m.start()]+dump(d)+m[0][m.end(1)-m.start():]+b'rh1502Art["townres"]=rh1510Art["Town Residence"];'
    html=html[:m.start()]+new+html[m.end():]
    start=html.index(b'var rh1502District=(()=>{');end=html.index(b'\n})();',start)+6;block=html[start:end]
    m=re.search(rb'const data=(\{[^\n]+?\}),art=',block);assert m
    d=json.loads(m[1]);m0=shops['Town Residence'];o=d['Town Residence'];g=m0['geometry'];assert [o['x'],o['y']]==g['doorWorld']
    o.update({k:g[k] for k in ['left','top','w','h','bottom','parts','height','doorWidth']});o.update({k:m0[k] for k in ['flues','lanterns']})
    block=block[:m.start(1)]+dump(d)+block[m.end(1):];html=html[:start]+block+html[end:]
    edit('return !!(rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name]);','return !!(rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name]||rh1515LayoutMeta.shops[s.name]);')
    edit('const m=rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name];','const m=rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name]||rh1515LayoutMeta.shops[s.name];')
    # Refit each civic pavilion support, retaining the open passage.
    start=html.index(b'const rh1499Civic=(()=>{');end=html.index(b'\n})();',start)+6;block=html[start:end]
    m=re.search(rb'const data=(\{[^\n]+?\}),objects=',block);d=json.loads(m[1]);d['bellCourt'].update(bell['geometry']);d['stoneSeat'].update(seat['geometry'])
    block=block[:m.start(1)]+dump(d)+block[m.end(1):]
    block=block.replace(b'[5358.4,1287.92]',dump(bell['geometry']['walk'][0]))
    html=html[:start]+block+html[end:]

    # The former between-shop gallery and lane no longer lead through a
    # solid party wall. Keep the rear service lane but end at the rear path.
    edit("{x:2635,y:1301,w:124,k:'stone'}","") # remove trailing comma too below
    edit("const rh1462Galleries=[{x:580,y:1301,w:112,k:'timber'},];","const rh1462Galleries=[{x:580,y:1301,w:112,k:'timber'}];")
    edit("{x:2618,y:925,w:34,h:415,vertical:true,seed:145601,kind:'service'}","{x:2618,y:925,w:34,h:219,vertical:true,seed:145601,kind:'service'}")
    edit('[[3560,1696],[3560,1720]]', '[[3410,1695],[3555,1695],[3660,1710],[3750,1710]]')
    # Early procedural placement uses the new party-wall bounds too. It
    # does not reserve a phantom passage through the now-attached stores.
    def foot(d):
        for name in ['General Store','Item Shop']:
            p=shops[name]['geometry']['parts'];xs=[x for q in p for x,y in q];d[name]=[min(xs),max(xs)]
    update(rb'const rh1328Foot=(\{[^\n]+?\});',foot)

    # Dedicated facade and real-footprint implementation joins the same
    # render/collision/depth/map hooks as all earlier trade models.
    i=html.index(b'function rh1457Shade(')
    html=html[:i]+b'const rh1515LayoutMeta='+dump(meta)+b';\n'+(root/'royal-haven-v1515.js').read_bytes()+b'\n'+html[i:]
    edit('const choose=s=>rh1504Artisan.handles(s)?rh1504Artisan:rh1503Shop;', 'const choose=s=>rh1515Commerce.handles(s)?rh1515Commerce:rh1504Artisan.handles(s)?rh1504Artisan:rh1503Shop;')
    edit('return {handles:s=>rh1504Artisan.handles(s)||rh1503Shop.handles(s),','return {handles:s=>rh1515Commerce.handles(s)||rh1504Artisan.handles(s)||rh1503Shop.handles(s),')
    edit('rh1504Artisan.init();rh1510PlaceAnnexes();','rh1504Artisan.init();rh1515PrepareStreet();rh1510PlaceAnnexes();')
    edit('rh1514RowGround(cx,cy);rh1511ThresholdDraw(cx,cy);','rh1514RowGround(cx,cy);rh1515StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
    edit('function rh1510GroundReset(){rh1514RowSurface=null;', 'function rh1510GroundReset(){rh1515StreetSurfaces.clear();rh1514RowSurface=null;')
    edit('streetAlignment:rh1514AlignmentStatus,reviewAlignment:', 'streetAlignment:rh1514AlignmentStatus,merchantQuarter:rh1515QuarterStatus,reviewQuarter:new URLSearchParams(location.search).has("graphicsAudit")?rh1515ReviewQuarter:undefined,reviewAlignment:')
    assert html.count(b'V1514')>=108
    return html.replace(b'V1514',b'V1515')
