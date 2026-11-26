"""Exact, fail-closed transformations from the original V1509 HTML."""
from pathlib import Path
import json
import base64
import re

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
    patch_dir=Path(__file__).parent
    metadata=json.loads((patch_dir/"art-v1510/metadata.json").read_text())
    metadata.update(json.loads((patch_dir/"art-v1510/home-metadata.json").read_text()))
    metadata.update(json.loads((patch_dir/"art-v1510/variant-metadata.json").read_text()))
    assets={name:"data:image/webp;base64,"+base64.b64encode((patch_dir/"art-v1510"/item["file"]).read_bytes()).decode() for name,item in metadata.items()}
    art=("const rh1510ArtMeta="+json.dumps(metadata,separators=(",",":"))+";\nconst rh1510Art={};for(const [name,src] of Object.entries("+json.dumps(assets,separators=(",",":"))+")){const im=rh1200Image();im.src=src;rh1510Art[name]=im;}\n").encode()
    # Replace only the gate sprite's artwork; original world geometry, animated
    # banner/flame anchors and cutaway remain unchanged.
    gate=re.search(rb'const rh118Images=\{\};for\(const \[k,v\] of Object.entries\((\{[^\n]+?\})\)',html)
    if not gate:
        raise ValueError("Gate image dictionary not found")
    old_gate=json.loads(gate.group(1))["gate"]
    revised_gate="data:image/webp;base64,"+base64.b64encode((patch_dir/"art-v1510/forest-gate-revised.webp").read_bytes()).decode()
    # Gate dictionary is located earlier than the cutaway anchors. Apply after
    # their indexed splice to avoid shifting the original source positions.
    shoulders={f"{i}-{j}":"data:image/webp;base64,"+base64.b64encode((patch_dir/f"art-v1510/shoulder-{i}-{j}.webp").read_bytes()).decode() for i in range(2) for j in range(2)}
    art+=("const rh1510ShoulderData="+json.dumps(shoulders,separators=(",",":"))+";\n").encode()
    civic_meta=json.loads((patch_dir/"art-v1510/civic-metadata.json").read_text())
    art+=("const rh1510CivicMeta="+json.dumps(civic_meta,separators=(",",":"))+";\n").encode()
    js=art+patch_dir.joinpath("royal-haven-v1510.js").read_bytes()
    html=html[:start]+js+b"\n"+html[end:]
    edit(old_gate,revised_gate)
    # Replace the actual indexed artwork in-place, so every existing projection,
    # foundation, bounds query and visible instance uses the same revised sprite.
    def civic_group(symbol, files):
        nonlocal html
        rx=rb'const '+symbol.encode()+rb'=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)'
        match=re.search(rx,html)
        if not match:
            raise ValueError("Missing civic art dictionary: "+symbol)
        values=json.loads(match.group(1))
        for key,file in files.items():
            if key not in values:
                raise ValueError("Missing civic art key: "+key)
            values[key]="data:image/webp;base64,"+base64.b64encode((patch_dir/"art-v1510"/file).read_bytes()).decode()
        html=html[:match.start(1)]+json.dumps(values,separators=(",",":")).encode()+html[match.end(1):]
    civic_group("rh193Art",{"hall":civic_meta["hall"]["file"]})
    civic_group("rh187Art",{k:m["file"] for k,m in civic_meta.items() if k!="hall"})
    edit("function rh1269Landmark(s,im){const academy=", "function rh1269Landmark(s,im){if(s.type==='future'&&im===rh193Art.hall)return rh1510HallFit(s,im);const academy=")
    edit("if(k==='mage'||k==='hall')rh1376DrawGlass('landmark:'+k,left,base-h,w,h);",
         "if(k==='mage')rh1376DrawGlass('landmark:'+k,left,base-h,w,h);if(k==='hall')rh1510HallGlass(left,base-h,w,h);")
    edit("return [[166,340,11,18],[100,243,18,27]].map(([u,v,w,h],i)=>({x:fit.left+fit.w*u/850,y:fit.top+fit.h*v/499,w:fit.w*w/850,h:fit.h*h/499,base:s.doorY,i,seed:1416+i*19,site:s.name}));",
         "return rh1510CivicMeta.hall.flames.map(([u,v,w,h],i)=>({x:fit.left+fit.w*u,y:fit.top+fit.h*v,w:fit.w*w,h:fit.h*h,base:s.doorY,i,seed:1416+i*19,site:s.name}));")
    edit("for(const o of ready)c.drawImage(o.im,o.x,o.y,720,650);",
         "for(const o of ready){c.drawImage(o.im,o.x,o.y,720,650);rh1510ShoulderDraw(c,o.x,o.y);}")
    edit("const im=s.type==='future'?rh193Art.hall:rh1451SiteArt(s),fit=rh1365SiteBounds(s);",
         "const im=rh1510Upgrade(s)||(s.type==='future'?rh193Art.hall:rh1451SiteArt(s)),fit=rh1365SiteBounds(s);")
    edit("g.strokeStyle='#34372c85';g.lineWidth=3;shape(g);g.stroke();g.strokeStyle='#b3a89066';g.lineWidth=1;shape(g);g.stroke();for(const p of runs)rh1422Weather(g,p,top,depth,seed);g.restore();",
         "g.strokeStyle='#34372c66';g.lineWidth=2.5;shape(g);g.stroke();g.strokeStyle='#b3a89044';g.lineWidth=1;shape(g);g.stroke();for(const p of runs)rh1422Weather(g,p,top,depth,seed);g.restore();rh1510FoundationWear(g,runs,top,depth,seed);")

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
    # Only the primary image is replaced; original world-space fit and collision remain unchanged.
    edit("function rh1432FacadeDraw(im,x,y,w,h){", "function rh1432FacadeDraw(im,x,y,w,h){\n if(rh1510FacadeContext?.upgrade&&rh1510FacadeContext.primary===im)im=rh1510FacadeContext.upgrade;")
    edit("rh1451SiteGlass(s,left,base-h,w,h);rh1424ShopFabric(s,left,base-h,w,h,performance.now()/1000);","if(!rh1510Upgrade(s)){rh1451SiteGlass(s,left,base-h,w,h);rh1424ShopFabric(s,left,base-h,w,h,performance.now()/1000);}")
    edit("function rh1451SiteFlues(s){const q=", "function rh1451SiteFlues(s){const revised=rh1510ArtPoints(s,'flues');if(revised)return revised;const q=")
    edit("function rh1451SiteLanterns(s){const q=", "function rh1451SiteLanterns(s){const revised=rh1510ArtPoints(s,'lanterns');if(revised)return revised;const q=")
    edit("function rh1454FireGeometry(s){return rh1454ForgeReady(s)?rh1454ForgeFire:rh1454OldFire;}", "function rh1454FireGeometry(s){return rh1510ArtPoints(s,'fire')||(rh1454ForgeReady(s)?rh1454ForgeFire:rh1454OldFire);}")
    edit("rh1430PuddleDraw(cx,cy,townTime);", "rh1510Ground(cx,cy);rh1430PuddleDraw(cx,cy,townTime);")
    edit("function rh1432ClearFacades(){rh1510CutawayCanvas=null;", "function rh1432ClearFacades(){rh1510ShoulderReset();rh1510GroundReset();rh1510CutawayCanvas=null;")
    edit("sites:sites.map(s=>s.name)};", "sites:sites.map(s=>s.name),exteriorArt:()=>Object.keys(rh1510ArtMeta).filter(name=>!name.includes(':')).map(name=>{const s=sites.find(o=>o.name===name),im=s?rh1510Upgrade(s):rh1510Art[name];return {name,active:!!s,ready:!!im?.complete&&im.naturalWidth>1,bounds:s?!!rh1365SiteBounds(s):null,legacy:rh1510ArtMeta[name].legacy};}),streetArt:rh1510StreetArtStatus,civicArt:rh1510CivicArtStatus,secondaryArt:()=>Object.keys(rh1510ArtMeta).filter(k=>k.startsWith('home:')).map(name=>({name,ready:!!rh1510Art[name]?.complete&&rh1510Art[name].naturalWidth>1}))};")
    edit("rh1457Facade(b,o.y,()=>{rh1432FacadeDraw(im,b.left,b.top,b.w,b.h);const a=rh1433Day().night;", "rh1457Facade(rh1510HomeContext(b,o,im),o.y,()=>{rh1432FacadeDraw(im,b.left,b.top,b.w,b.h);const a=rh1433Day().night;")
    edit("if(Number.isFinite(o.flue)&&rh1246SmokeArt.every(a=>a.complete&&a.naturalWidth>1))rh1424Plume(b.left+b.w*o.flue,b.top+(o.flueY===undefined?3:b.h*o.flueY),now,cx,cy,o.x+o.y,'house');", "const updatedFlue=rh1510HomeFlues(o)?.[0];if((updatedFlue||Number.isFinite(o.flue))&&rh1246SmokeArt.every(a=>a.complete&&a.naturalWidth>1))rh1424Plume(b.left+b.w*(updatedFlue?.[0]??o.flue),b.top+(updatedFlue?b.h*updatedFlue[1]:(o.flueY===undefined?3:b.h*o.flueY)),now,cx,cy,o.x+o.y,'house');")
    # Preserve existing draw order and special northern citadel (painted behind the party).
    # Every occurrence was checked against the text-only source (no embedded image bytes).
    if html.count(b"V1509")!=108:
        raise ValueError("V1510 version replacement count changed")
    return html.replace(b"V1509",b"V1510")
