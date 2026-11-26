"""Royal Haven: straight gatehouse, recessed homes and a walkable west trade row."""
from pathlib import Path
import re, json, base64

def apply(html: bytes) -> bytes:
    root=Path(__file__).parent
    art=root/'art-v1514'
    meta=json.loads((art/'layout-metadata.json').read_text())
    shops,gate=meta['shops'],meta['gate']
    assert set(shops)=={'Herbalist','Enchanter','Fletcher'}
    def dump(o):return json.dumps(o,separators=(',',':')).encode()
    def url(o):return 'data:image/webp;base64,'+base64.b64encode((art/o['file']).read_bytes()).decode()
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode()
        if html.count(a)!=1:raise ValueError(f'V1514 anchor count {html.count(a)}: {a[:120]}')
        html=html.replace(a,b,1)
    def update(rx,fn):
        nonlocal html
        m=re.search(rx,html)
        if not m:raise ValueError(f'Missing anchor {rx}')
        data=json.loads(m[1]);fn(data)
        html=html[:m.start(1)]+dump(data)+html[m.end(1):]

    def shopmeta(data):
        for name,m in shops.items():
            data[name].update({f:m[f] for f in ['file','width','height','door','flues','lanterns']})
    update(rb'const rh1510ArtMeta=(\{[^\n]+?\});\n',shopmeta)
    update(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({k:url(m) for k,m in shops.items()}))
    for atlas,key,name,module in [
        (b'rh1501Art','herbal','Herbalist',b'rh1501Herbs'),
        (b'rh1502Art','enchant','Enchanter',b'rh1502District'),
        (b'rh1504Art','fletcher','Fletcher',b'rh1504Artisan')]:
        rx=rb'const '+atlas+rb'=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;'+atlas+rb'\[k\]=im;\}'
        m=re.search(rx,html);assert m
        data=json.loads(m[1]);data.pop(key);data.pop(key+'Night',None)
        new=m[0][:m.start(1)-m.start()]+dump(data)+m[0][m.end(1)-m.start():]
        new+=atlas+b'['+dump(key)+b']=rh1510Art['+dump(name)+b'];'
        html=html[:m.start()]+new+html[m.end():]
        start=html.index(b'var '+module+b'=(()=>{')
        end=html.index(b'\n})();',start)+6;block=html[start:end]
        m=re.search(rb'const data=(\{[^\n]+?\}),art=',block);assert m
        data=json.loads(m[1]);o=data[name];g=shops[name]['geometry']
        assert [o['x'],o['y']]==g['doorWorld']
        o.update({f:g[f] for f in ['left','top','w','h','bottom','parts','height','doorWidth']})
        o.update({f:shops[name][f] for f in ['flues','lanterns']})
        block=block[:m.start(1)]+dump(data)+block[m.end(1):]
        if module!=b'rh1504Artisan':
            a=b'rh1432FacadeDraw(a,b.left,b.top,b.w,b.h);const n=rh1433Day().night;'
            assert block.count(a)==1, module
            block=block.replace(a,b'rh1432FacadeDraw(a,b.left,b.top,b.w,b.h);if(rh1513RowBuilding(s))rh1513RowGlass(s,b);const n=rh1433Day().night;')
        if module in [b'rh1502District',b'rh1504Artisan']:
            # The Enchanter now extends toward the Fletcher; place the lane
            # in the physical opening between the two straight storefronts.
            block=block.replace(b'[985,',b'[1008,')
        if module==b'rh1502District':
            block=block.replace(b'{x:955,y:1840,k:\'lamp\'',b'{x:930,y:2039,k:\'lamp\'')
            # Bend the residence side path around the existing obstacle.
            block=block.replace(b'[4100,1380],[4100,1510],[3820,1530]',b'[4100,1380],[4330,1440],[4330,1580],[3870,1580],[3820,1530]')
        html=html[:start]+block+html[end:]
    edit('return !!rh1513LayoutMeta.shops[s.name];','return !!(rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name]);')
    edit('const m=rh1513LayoutMeta.shops[s.name];','const m=rh1513LayoutMeta.shops[s.name]||rh1514LayoutMeta.shops[s.name];')

    # Replace only gatehouse raster and associated geometry. Keep the passage
    # and its two connections, rather than creating a solid decorative arch.
    matches=list(re.finditer(rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;',html))
    found=0
    for m in reversed(matches):
        d=json.loads(m[1])
        if 'rh1494Gatehouse' not in d:continue
        d['rh1494Gatehouse']=url(gate);d.pop('rh1494GatehouseNight',None)
        html=html[:m.start(1)]+dump(d)+html[m.end(1):];found+=1
    assert found==1
    update(rb'const rh1511DistrictData=(\{[^\n]+?\});\n',lambda d:d.update({'rh1494Gatehouse':{f:gate[f] for f in ['file','width','height','sourceBounds','flues','windows','openings']}}))
    start=html.index(b'const rh1494Gatehouse=(()=>{')
    end=html.index(b'\n})();',start)+6;block=html[start:end]
    m=re.search(rb'const home=(\{[^\n]+?\});',block);assert m
    old=json.loads(m[1]);old.update(gate['geometry'])
    block=block[:m.start(1)]+dump(old)+block[m.end(1):]
    # The body is square to the street, with the same external approach.
    p=gate['passage'];a=gate['approaches']
    block=re.sub(rb'const passage=\[[^\n]+?\];',b'const passage='+dump(p)+b';',block,count=1)
    block=re.sub(rb'const approaches=\[\n.*?\n \];',b'const approaches='+dump(a)+b';',block,count=1,flags=re.S)
    block=re.sub(rb'const walkRoutes=\[\n.*?\n \];',b'const walkRoutes='+dump([p,a[0]+a[1][-2::-1]])+b';',block,count=1,flags=re.S)
    # Sample the actual revised polygon extents rather than the old slope.
    block=block.replace(b'for(let x=-216;x<=216;x+=2)for(let y=-121;y<=1;y+=2)',b'for(let x=-250;x<=250;x+=2)for(let y=-151;y<=6;y+=2)')
    block=block.replace(b'g.rotate(-.16);',b'g.rotate(0);')
    # No new bench on the gateway route; preserve other furniture.
    block=block.replace(b'if(!propFree(bench,bench.rx,bench.ry)||!propFree(planter,34,15))',b'if(!propFree(planter,34,15))')
    block=block.replace(b'rh194Props.push(bench);rh117Props.push(planter);',b'rh117Props.push(planter);')
    block=block.replace(b'rh194Props.pop();rh117Props.pop();',b'rh117Props.pop();')
    block=block.replace(b'props:3',b'props:2')
    html=html[:start]+block+html[end:]

    # Shift the entire neighboring compound, without distorting its architecture.
    shift=meta['homeShift']
    def homes(d):
        for o in d:
            if o['k'] in ['courtmain','courtwing']:
                o['y']=round(o['y']+shift,3)
                o['door'][1]=round(o['door'][1]+shift,3)
    update(rb'const rh1464Homes=(\[[^\n]+?\]);',homes)
    def courtyard(d):
        # Extend northern edges to the moved thresholds, retain southern exit.
        for i in [2,3]:d[i][1]=round(d[i][1]+shift,2)
    update(rb'const rh1472Court=(\[[^\n]+?\]);',courtyard)
    edit('[[3995,991],[3995,1018]]',f'[[3995,{991+shift}],[3995,1018]]')
    def paths(d):
        d.append([[[4177,round(921.26+shift+18,2)],[4177,966],[4150,1000]],14])
    update(rb'const rh1473Paths=(\[[^\n]+?\]);',paths)

    # Filter the real town object lists after all staged installations; the
    # same arrays feed rendering and the collision grid. Do not touch interior
    # benches, workbenches, shop racks or other functional objects.
    i=html.index(b'function rh1457Shade(')
    html=html[:i]+b'const rh1514LayoutMeta='+dump(meta)+b';\n'+(root/'royal-haven-v1514.js').read_bytes()+b'\n'+html[i:]
    edit('rh1504Artisan.init();rh1510PlaceAnnexes();','rh1504Artisan.init();rh1510PlaceAnnexes();rh1514RemoveStreetBenches();')
    edit('rh1513RowGround(cx,cy);rh1511ThresholdDraw(cx,cy);','rh1513RowGround(cx,cy);rh1514RowGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
    edit('function rh1510GroundReset(){rh1513RowSurface=null;','function rh1510GroundReset(){rh1514RowSurface=null;rh1513RowSurface=null;')
    edit('streetLayout:rh1513LayoutStatus,reviewLayout:','streetLayout:rh1513LayoutStatus,streetAlignment:rh1514AlignmentStatus,reviewAlignment:new URLSearchParams(location.search).has("graphicsAudit")?rh1514ReviewAlignment:undefined,reviewLayout:')
    assert html.count(b'V1513')>=108
    return html.replace(b'V1513',b'V1514')
