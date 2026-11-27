"""Royal Haven: individual merchant stalls, watchtower art and wall foundations."""
from pathlib import Path
import base64
import json
import re


def apply(html: bytes) -> bytes:
    root=Path(__file__).parent
    art=root/"art-v1512"
    meta=json.loads((art/"fortification-metadata.json").read_text())
    if set(meta)!={"tower0","tower1","tower2","spice","pottery"}:
        raise ValueError("Incomplete V1512 art")
    def url(k):
        return "data:image/webp;base64,"+base64.b64encode((art/meta[k]["file"]).read_bytes()).decode()
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        n=html.count(old)
        if n!=1:
            raise ValueError(f"V1512 anchor count {n}: {old[:120]}")
        html=html.replace(old,new,1)

    match=re.search(rb'const rh1335TowerArt=(\[[^\n]+?\])\.map',html)
    if not match:
        raise ValueError("Missing tower image array")
    values=json.loads(match.group(1))
    if len(values)!=3:
        raise ValueError("Unexpected number of tower variants")
    html=html[:match.start(1)]+json.dumps([url("tower"+str(i)) for i in range(3)],separators=(",",":")).encode()+html[match.end(1):]
    code=("const rh1512FortMeta="+json.dumps(meta,separators=(",",":"))+";\n"
          "const rh1512MarketVariants={};for(const [k,src] of Object.entries("+json.dumps({k:url(k) for k in ["spice","pottery"]},separators=(",",":"))+")){const im=rh1200Image();im.src=src;rh1512MarketVariants[k]=im;}\n").encode()
    i=html.index(b"function rh1457Shade(")
    html=html[:i]+code+(root/"royal-haven-v1512.js").read_bytes()+b"\n"+html[i:]
    edit("function rh1475Draw(o,now,cx,cy){const im=rh1475Images[o.k];",
         "function rh1475Draw(o,now,cx,cy){const im=rh1512MarketImage(o);")
    edit("function rh1335SideWalls(cx,cy){for(const side of [-1,1])",
         "function rh1335SideWalls(cx,cy){rh1512WallBuilds=0;for(const side of [-1,1])")
    edit("c.drawImage(im,0,0,65,240);c.restore();} }}",
         "c.drawImage(rh1512WallSegment(im,side,y),0,0,65,240);c.restore();} }}")
    edit("function rh1335Curtain(cx,cy){if(cy+H<2340||cy>2550)return;for(let x=0;x<WORLD_W;x+=240){if(x+240<cx||x>cx+W)continue;const a=rh1215WallSection(x);if(!a)continue;for(const [l,r] of [[0,1450],[2150,WORLD_W]]){const start=Math.max(l,x),end=Math.min(r,x+240);if(end>start)c.drawImage(a,(start-x)*a.naturalWidth/240,0,(end-start)*a.naturalWidth/240,a.naturalHeight,start,2360,end-start,184);}}}",
         "function rh1335Curtain(cx,cy){if(cy+H<2340||cy>2550)return;for(let x=0;x<WORLD_W;x+=240){if(x+240<cx||x>cx+W)continue;const im=rh1215WallSection(x);if(!im)continue;const a=rh1512WallSegment(im,0,x);for(const [l,r] of [[0,1450],[2150,WORLD_W]]){const start=Math.max(l,x),end=Math.min(r,x+240);if(end>start)rh1457Facade({left:start,top:2360,w:end-start,h:184},2543,()=>c.drawImage(a,(start-x)*(a.naturalWidth||a.width)/240,0,(end-start)*(a.naturalWidth||a.width)/240,a.naturalHeight||a.height,start,2360,end-start,184));}}}")
    edit("rh117Push(o.y,()=>rh1457Facade({left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h},o.y,()=>rh1335Tower(o)));",
         "rh117Push(o.y,()=>rh1457Facade(rh1512TowerBounds(o),o.y,()=>rh1335Tower(o)));")
    edit("rh1511ThresholdDraw(cx,cy);rh1510MarketGround(cx,cy);rh1510Ground(cx,cy);",
         "rh1512WallFooting(cx,cy);rh1511ThresholdDraw(cx,cy);rh1510MarketGround(cx,cy);rh1510Ground(cx,cy);")
    edit("rh1510GroundBuilds=0;\n rh1510AnnexApproach(cx,cy);",
         "rh1510GroundBuilds=0;\n rh1512TowerContacts(cx,cy);rh1510AnnexApproach(cx,cy);")
    edit("function rh1510GroundReset(){rh1511ThresholdCache.clear();",
         "function rh1510GroundReset(){rh1512WallCache.clear();rh1512FootCache.clear();rh1512WallPixels=0;rh1512WallBuilds=0;rh1511ThresholdCache.clear();")
    edit("districtArt:rh1511DistrictStatus,reviewDistrict:", 
         "districtArt:rh1511DistrictStatus,fortificationArt:rh1512FortStatus,reviewFortifications:new URLSearchParams(location.search).has('graphicsAudit')?rh1512ReviewFort:undefined,reviewDistrict:")
    if html.count(b"V1511")<108:
        raise ValueError("Expected V1511 version labels")
    return html.replace(b"V1511",b"V1512")
