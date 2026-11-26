"""Exact, fail-closed transformations from the original V1509 HTML."""
from pathlib import Path

def apply(html: bytes) -> bytes:
    def edit(old: str, new: str):
        nonlocal html
        a,b=old.encode(),new.encode()
        count=html.count(a)
        if count != 1:
            raise ValueError(f"V1510 patch anchor count {count}: {old[:100]}")
        html=html.replace(a,b,1)

    # The old cutaway had a lane whitelist and painted the building three times.
    start=html.index(b"function rh1457Overlap(")
    end=html.index(b"function rh1457Shade(",start)
    js=Path(__file__).with_name("royal-haven-v1510.js").read_bytes()
    html=html[:start]+js+b"\n"+html[end:]

    edit("if(landmarkNames.has(s.name)||s.type==='future')facade();else rh1457Facade(b,rh1504Shop?.depth(s)??s.doorY,facade);",
         "rh1457Facade(rh1510SiteBounds(b,s),rh1504Shop?.depth(s)??s.doorY,facade);")
    edit("rh117Push(o.y,()=>rh187Draw(o));}", "rh117Push(o.y,()=>rh1457Facade(b,o.y,()=>rh187Draw(o)));}")
    edit("c.drawImage(im,o.x-o.w/2,o.y-h,o.w,h);if(o.rebuilt1340)", "rh1432FacadeDraw(im,o.x-o.w/2,o.y-h,o.w,h);if(o.rebuilt1340)")
    edit("rh1457Facade(b,o.y,()=>c.drawImage(im,b.left,b.top,b.w,b.h));",
         "rh1457Facade(b,o.y,()=>rh1432FacadeDraw(im,b.left,b.top,b.w,b.h));")
    edit("rh117Push(o.y,()=>rh1335Tower(o));",
         "rh117Push(o.y,()=>rh1457Facade({left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h},o.y,()=>rh1335Tower(o)));")
    edit("function rh1335Tower(o){const im=rh1335TowerArt[o.k];if(!im?.complete||!im.naturalWidth)return;c.drawImage(im,o.x-o.w/2,o.y-o.h,o.w,o.h);}",
         "function rh1335Tower(o){const im=rh1335TowerArt[o.k];if(!im?.complete||!im.naturalWidth)return;rh1432FacadeDraw(im,o.x-o.w/2,o.y-o.h,o.w,o.h);}")
    edit("rh117Push(o.y,()=>rh191Tower(o));",
         "rh117Push(o.y,()=>rh1457Facade({left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h},o.y,()=>rh191Tower(o)));")
    edit("c.drawImage(im,-o.w/2,-o.h,o.w,o.h);rh1281Cloth", "rh1432FacadeDraw(im,-o.w/2,-o.h,o.w,o.h);rh1281Cloth")
    edit("rh117Push(o.y,()=>rh190Arch(o,now));",
         "rh117Push(o.y,()=>rh1457Facade({left:o.x-105,top:o.y-185,w:210,h:190},o.y,()=>rh190Arch(o,now)));")
    edit("c.drawImage(rh190ArchArt,o.x-w/2,o.y-h+5,w,h);", "rh1432FacadeDraw(rh190ArchArt,o.x-w/2,o.y-h+5,w,h);")
    edit("rh117Push(2470,()=>rh118Gate(cx,cy));",
         "rh117Push(2470,()=>rh1457Facade({left:rh1407Gate.x,top:rh1407Gate.y,w:rh1407Gate.w,h:rh1407Gate.h},2470,()=>rh118Gate(cx,cy)));")
    edit("rh118Sprite('gate',a.x+a.w/2,a.base,a.w,a.h);","rh1432FacadeDraw(rh118Images.gate,a.x,a.y,a.w,a.h);")
    # Respect the existing capped LRU and single raster build per frame.
    edit("const dw=Math.ceil(w),dh=Math.ceil(h),n=dw*dh;\n if(!im?.complete", "const dw=Math.ceil(w),dh=Math.ceil(h),n=dw*dh,wear=rh1510WeatherKey(w,h);\n if(!im?.complete")
    edit("(!filtered&&im.naturalWidth<=dw*1.35&&im.naturalHeight<=dh*1.35)", "(wear===null&&!filtered&&im.naturalWidth<=dw*1.35&&im.naturalHeight<=dh*1.35)")
    edit("const key=rh1432FacadeIds.get(im)+':'+dw+':'+dh+':'+filter;", "const key=rh1432FacadeIds.get(im)+':'+dw+':'+dh+':'+filter+':'+wear;")
    edit("g.drawImage(im,0,0,dw,dh);while(rh1432FacadePixels+n>", "g.drawImage(im,0,0,dw,dh);rh1510WeatherRaster(g,dw,dh,wear);while(rh1432FacadePixels+n>")
    edit("function rh1432ClearFacades(){rh1432FacadeCache.clear();","function rh1432ClearFacades(){rh1510CutawayCanvas=null;rh1432FacadeCache.clear();")
    # Preserve existing draw order and special northern citadel (painted behind the party).
    # Every occurrence was checked against the text-only source (no embedded image bytes).
    if html.count(b"V1509")!=108:
        raise ValueError("V1510 version replacement count changed")
    return html.replace(b"V1509",b"V1510")
