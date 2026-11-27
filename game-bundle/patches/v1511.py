"""Eastern Royal Haven art pass, applied after verified V1510."""
from pathlib import Path
import base64
import json
import re


def apply(html: bytes) -> bytes:
    def edit(old: str, new: str):
        nonlocal html
        a,b=old.encode(),new.encode()
        count=html.count(a)
        if count!=1:
            raise ValueError(f"V1511 anchor count {count}: {old[:120]}")
        html=html.replace(a,b,1)

    root=Path(__file__).parent
    art=root/"art-v1511"
    meta=json.loads((art/"district-metadata.json").read_text())
    if set(meta)!={"rh1478East","rh1478West","rh1478Rear","rh1493Longhouse","rh1494Gatehouse",
                   "rh1495workshop","rh1495stepHouse","rh1496herbCourt","rh1499bellCourt"}:
        raise ValueError("Incomplete eastern district sprite set")
    # Update the primary indexed assets in-place. All world-space object
    # positions, bounds, doors, walking corridors and depth order are retained.
    rx=rb'for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)\)\{const im=rh1200Image\(\);im.src=src;rh1464Art\[k\]=im;'
    found=set()
    for match in reversed(list(re.finditer(rx,html))):
        values=json.loads(match.group(1))
        keys=values.keys() & meta.keys()
        if not keys:
            continue
        for k in keys:
            values[k]="data:image/webp;base64,"+base64.b64encode((art/meta[k]["file"]).read_bytes()).decode()
            # New window tints are aligned to the revised glass, not old
            # full-building night overlays that could ghost over roof/walls.
            # Retire the now unused old night raster from the bundled atlas.
            values.pop(k+"Night",None)
            found.add(k)
        html=html[:match.start(1)]+json.dumps(values,separators=(",",":")).encode()+html[match.end(1):]
    if found!=set(meta):
        raise ValueError("Missing active district art: "+str(set(meta)-found))
    anchor=b"function rh1457Shade("
    i=html.index(anchor)
    code=("const rh1511DistrictData="+json.dumps(meta,separators=(",",":"))+";\n").encode()+(root/"royal-haven-v1511.js").read_bytes()
    html=html[:i]+code+b"\n"+html[i:]

    edit("const glow=rh1510MarketBuilding(o)?null:rh1464Art[o.k+'Night'];",
         "const glow=rh1510MarketBuilding(o)||rh1511DistrictArt(o)?null:rh1464Art[o.k+'Night'];")
    edit("if(rh1510MarketBuilding(o))rh1510MarketGlass(o,b);const a=rh1433Day().night;",
         "if(rh1510MarketBuilding(o))rh1510MarketGlass(o,b);if(rh1511DistrictArt(o))rh1511WindowGlass(o,b);const a=rh1433Day().night;")
    edit("function rh1510HomeContext(b,o,im){return {...b,primary:im,upgrade:rh1510HomeUpgrade(o),style:{green:true,flues:rh1510HomeFlues(o)||[]}};}",
         "function rh1510HomeContext(b,o,im){return {...b,primary:im,upgrade:rh1511DistrictArt(o)?im:rh1510HomeUpgrade(o),style:{green:true,flues:rh1511DistrictFlues(o)||rh1510HomeFlues(o)||[]}};}")
    edit("const updatedFlue=rh1510MarketMeta[o.k]?.flue||rh1510HomeFlues(o)?.[0];",
         "const updatedFlue=rh1511DistrictFlues(o)?.[0]||rh1510MarketMeta[o.k]?.flue||rh1510HomeFlues(o)?.[0];")
    edit("if(Number.isFinite(o.flue2)&&rh1246SmokeArt.every(a=>a.complete&&a.naturalWidth>1))rh1424Plume(b.left+b.w*o.flue2,b.top+b.h*o.flueY2,now,cx,cy,o.x+o.y+67,'house');",
         "const f2=rh1511DistrictFlues(o)?.[1];if((f2||Number.isFinite(o.flue2))&&rh1246SmokeArt.every(a=>a.complete&&a.naturalWidth>1))rh1424Plume(b.left+b.w*(f2?.[0]??o.flue2),b.top+b.h*(f2?.[1]??o.flueY2),now,cx,cy,o.x+o.y+67,'house');")

    # The broad paving borders used identical smooth linework. Keep original
    # polygon masks, then weather the actual alpha and stone at their margins.
    for old,new in [
        ("rh1472Trace(g,court,b.x,b.y);g.strokeStyle='#9a997360';g.lineWidth=6;g.stroke();g.strokeStyle='#b2b19455';g.lineWidth=1.4;g.stroke();",
         "rh1511PavingEdge(g,b,court,1496);"),
        ("rh1472Trace(g,yard,b.x,b.y);g.strokeStyle='#8c806a70';g.lineWidth=6;g.stroke();g.strokeStyle='#b8aa8655';g.lineWidth=1.4;g.stroke();",
         "rh1511PavingEdge(g,b,yard,1495);"),
        ("rh1472Trace(g,apron,x,y);g.lineWidth=8;g.strokeStyle='#3a393064';g.stroke();g.lineWidth=2;g.strokeStyle='#b6aa8970';g.stroke();",
         "rh1511PavingEdge(g,{x,y,w,h},apron,1493);"),
        ("rh1472Trace(g,shape,x,y);g.strokeStyle='#33362b88';g.lineWidth=6;g.stroke();g.strokeStyle='#b8aa8866';g.lineWidth=1.5;g.stroke();",
         "rh1511PavingEdge(g,{x,y,w,h},shape,1492);"),
        ("rh1472Trace(g,polygon,b.x,b.y);g.strokeStyle='#332f2580';g.lineWidth=8;g.stroke();g.strokeStyle='#b6a48a55';g.lineWidth=2;g.stroke();",
         "rh1511PavingEdge(g,b,polygon,1499);"),
    ]:
        edit(old,new)

    edit("g.drawImage(mask,0,0);g.globalCompositeOperation='source-over';rh1467FrontCache.set(o,a);return a;",
         "g.drawImage(mask,0,0);rh1511FrontWear(g,o);g.globalCompositeOperation='source-over';rh1467FrontCache.set(o,a);return a;")
    edit("rh1510MarketGround(cx,cy);rh1510Ground(cx,cy);rh1430PuddleDraw(cx,cy,townTime);",
         "rh1511ThresholdDraw(cx,cy);rh1510MarketGround(cx,cy);rh1510Ground(cx,cy);rh1430PuddleDraw(cx,cy,townTime);")
    edit("function rh1510GroundReset(){rh1510MarketContacts.clear();",
         "function rh1510GroundReset(){rh1511ThresholdCache.clear();rh1510MarketContacts.clear();")
    edit("marketArt:rh1510MarketArtStatus,reviewMarket:", 
         "marketArt:rh1510MarketArtStatus,districtArt:rh1511DistrictStatus,reviewDistrict:new URLSearchParams(location.search).has('graphicsAudit')?rh1511ReviewDistrict:undefined,reviewMarket:")
    if html.count(b"V1510")<108:
        raise ValueError("Expected V1510 version labels")
    return html.replace(b"V1510",b"V1511")
