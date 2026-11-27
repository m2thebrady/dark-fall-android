"""Align Royal Haven's trade row with its street and turn the east courtyard inward."""
from pathlib import Path
import base64
import json
import re


def apply(html: bytes) -> bytes:
    root=Path(__file__).parent
    art=root/"art-v1513"
    meta=json.loads((art/"layout-metadata.json").read_text())
    shops, court=meta["shops"],meta["court"]
    assert set(shops)=={"Tailor","Apothecary","Bakery"}
    assert set(court)=={"rh1474rear","rh1474tower","rh1474gallery"}
    def url(m):
        return "data:image/webp;base64,"+base64.b64encode((art/m["file"]).read_bytes()).decode()
    def dump(v):
        return json.dumps(v,separators=(",",":")).encode()
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        n=html.count(old)
        if n!=1:
            raise ValueError(f"V1513 anchor count {n}: {old[:100]}")
        html=html.replace(old,new,1)
    def object_after(prefix):
        start=html.index(prefix)+len(prefix)
        # Use end of complete JSON by finding exact suffix of statement; atlas
        # data is large but confined to a single line.
        return start

    m=re.search(rb'const rh1510ArtMeta=(\{[^\n]+?\});\n',html)
    assert m
    values=json.loads(m[1])
    for k,v in shops.items():
        for field in ["file","width","height","door","flues","lanterns"]:
            values[k][field]=v[field]
    html=html[:m.start(1)]+dump(values)+html[m.end(1):]
    m=re.search(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',html)
    assert m
    values=json.loads(m[1]);values.update({name:url(v) for name,v in shops.items()})
    html=html[:m.start(1)]+dump(values)+html[m.end(1):]

    # Both of the existing functional shop modules now reference those same
    # assets. Eliminate mismatched old day/night artwork, not shop mechanics.
    for atlas,names in [(b'rh1500Art',{"apoth":"Apothecary","bakery":"Bakery"}),(b'rh1504Art',{"tailor":"Tailor"})]:
        pattern=rb'const '+atlas+rb'=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;'+atlas+rb'\[k\]=im;\}'
        m=re.search(pattern,html)
        if not m:raise ValueError("Missing atlas "+str(atlas))
        values=json.loads(m[1])
        for k in names:
            values.pop(k);values.pop(k+"Night",None)
        new=m[0][:m.start(1)-m.start()]+dump(values)+m[0][m.end(1)-m.start():]
        new+=b''.join(atlas+b'['+dump(k)+b']=rh1510Art['+dump(name)+b'];' for k,name in names.items())
        html=html[:m.start()]+new+html[m.end():]

    # Data-driven fit and collision aligned to straight facade. Retain x/y,
    # routes, staff and all admission/interaction logic in original modules.
    for module,names in [(b'rh1500Trades',["Apothecary","Bakery"]),(b'rh1504Artisan',["Tailor"])]:
        start=html.index(b'var '+module+b'=(()=>{')
        end=html.index(b'\n})();',start)+6
        block=html[start:end]
        m=re.search(rb'const data=(\{[^\n]+?\}),art=',block)
        values=json.loads(m[1])
        for k in names:
            o=values[k];geom=shops[k]["geometry"]
            assert [o["x"],o["y"]]==geom["doorWorld"]
            o.update({f:geom[f] for f in ["left","top","w","h","bottom","parts","height","doorWidth"]})
            o["flues"]=shops[k]["flues"];o["lanterns"]=shops[k]["lanterns"]
        block=block[:m.start(1)]+dump(values)+block[m.end(1):]
        old=b'rh1432FacadeDraw(a,b.left,b.top,b.w,b.h);const n=rh1433Day().night;'
        assert block.count(old)==1
        block=block.replace(old,b'rh1432FacadeDraw(a,b.left,b.top,b.w,b.h);if(rh1513RowBuilding(s))rh1513RowGlass(s,b);const n=rh1433Day().night;')
        html=html[:start]+block+html[end:]

    m=re.search(rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1474Art\[k\]=im;\}',html)
    if not m:raise ValueError("Missing courtyard atlas")
    values=json.loads(m[1])
    for k,v in court.items():
        values[k]=url(v);values.pop(k+'Night',None)
    html=html[:m.start(1)]+dump(values)+html[m.end(1):]
    m=re.search(rb'const rh1474Parts=(\[[^\n]+?\]);\n',html)
    assert m
    values=json.loads(m[1])
    for o in values:
        k=o["k"];v=court[k]
        if k=="rh1474tower":
            # Reflect the polygon about the same X axis as the visual asset.
            o["dx"]=-o["dx"]
            o["poly"]=[[-x,y] for x,y in reversed(o["poly"])]
        if "door" in v:
            o["door"]=[round(o["x"]+o.get("dx",0)-o["w"]/2+o["w"]*v["door"][0],3),round(o["y"]+o.get("artDy",0)-o["h"]+o["h"]*v["door"][1],3)]
            o["doorHeight"]=round(o["h"]*v["doorHeight"],2)
            if v["flues"]:
                o["flue"],o["flueY"]=v["flues"][0]
        if k=="rh1474gallery" and "boxes" in v:
            o["boxes"]=v["boxes"]
    html=html[:m.start(1)]+dump(values)+html[m.end(1):]
    # A shared apron grows toward both facing doorways, not over the passage.
    geom=meta["courtyard"]
    m=re.search(rb'const rh1474Court=(\[[^\n]+?\]);',html);assert m
    html=html[:m.start(1)]+dump(geom["paving"])+html[m.end(1):]
    m=re.search(rb'const rh1474GalleryWalk=(\[[^\n]+?\]);',html);assert m
    html=html[:m.start(1)]+dump(geom["galleryWalk"])+html[m.end(1):]
    m=re.search(rb'const rh1474Routes=(\[\n.*?\n\]);',html,re.S);assert m
    html=html[:m.start(1)]+dump(geom["routes"])+html[m.end(1):]
    edit("rh1472Trace(g,rh1474Court,b.x,b.y);g.strokeStyle='#2f332c88';g.lineWidth=7;g.stroke();g.strokeStyle='#bdac9155';g.lineWidth=2;g.stroke();",
         "rh1511PavingEdge(g,b,rh1474Court,1513);")
    edit("rh1457Facade(b,o.y,()=>{\n rh1432FacadeDraw(im,b.left,b.top,b.w,b.h);\n const glow=rh1474Art[o.k+'Night']",
         "rh1457Facade({...b,primary:im,upgrade:im,style:{green:true,flues:rh1513LayoutMeta.court[o.k].flues}},o.y,()=>{\n rh1432FacadeDraw(im,b.left,b.top,b.w,b.h);rh1513CourtGlass(o,b);\n const glow=rh1474Art[o.k+'Night']")
    # Low depth details and the new street texture both preserve the existing
    # cached contact and adaptive graphics budget.
    i=html.index(b"function rh1457Shade(")
    html=html[:i]+b"const rh1513LayoutMeta="+dump(meta)+b";\n"+(root/"royal-haven-v1513.js").read_bytes()+b"\n"+html[i:]
    edit("rh1512WallFooting(cx,cy);rh1511ThresholdDraw(cx,cy);",
         "rh1512WallFooting(cx,cy);rh1513RowGround(cx,cy);rh1511ThresholdDraw(cx,cy);")
    edit("function rh1510GroundReset(){rh1512WallCache.clear();",
         "function rh1510GroundReset(){rh1513RowSurface=null;rh1512WallCache.clear();")
    edit("fortificationArt:rh1512FortStatus,reviewFortifications:",
         "fortificationArt:rh1512FortStatus,streetLayout:rh1513LayoutStatus,reviewLayout:new URLSearchParams(location.search).has('graphicsAudit')?rh1513ReviewLayout:undefined,reviewFortifications:")
    if html.count(b"V1512")<108:raise ValueError("Expected V1512 labels")
    return html.replace(b"V1512",b"V1513")
