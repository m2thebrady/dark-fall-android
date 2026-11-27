"""Renew the northern temple and guild courts and existing planted terraces."""
from pathlib import Path
import json,re,base64,hashlib

def apply(html:bytes)->bytes:
    root=Path(__file__).parent; art=root/'art-v1532'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(t):
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html);assert a
    data=json.loads(a[1])
    for t in meta['ground']:
        assert t['key'] in data
        data[t['key']]=uri(t)
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1532Meta='+json.dumps(meta,separators=(',',':'))+';\n'
    info+=(root/'royal-haven-v1532.js').read_text()+'\n'
    info+='const rh1532PlantArt=rh1200Image();rh1532PlantArt.src="'+uri(meta['plant'])+'";\n'
    for r in meta['regions']:
        seed=r['overlay']['seed']
        info+=f'rh1532CourtImages[{seed}]=rh1200Image();rh1532CourtImages[{seed}].src="{uri(r["overlay"])}";\n'
    edit('function rh1457Shade(o){',info+'function rh1457Shade(o){')
    edit('function rh1347CourtArt(o){','function rh1347CourtArt(o){\n const painted=rh1532CourtImages[o.seed];if(rh1532ImageReady(painted))return painted;')
    edit('c.globalAlpha=.83;c.drawImage(a,o.x-o.w/2,o.y-o.h/2);','c.globalAlpha=a===rh1532CourtImages[o.seed]?1:.83;c.drawImage(a,o.x-o.w/2,o.y-o.h/2);')
    # Existing garden meshes and collision stay intact; replace grass/fern material
    # only in sacred and observatory gardens. Cache only the finished surfaces.
    edit('const ready=rh191PaveArt.complete&&rh191PaveArt.naturalWidth&&rh189Grass.complete&&rh189Grass.naturalWidth&&rh178Art.fern?.complete&&rh178Art.fern.naturalWidth;',
         'const ready=rh191PaveArt.complete&&rh191PaveArt.naturalWidth&&rh189Grass.complete&&rh189Grass.naturalWidth&&rh178Art.fern?.complete&&rh178Art.fern.naturalWidth&&(!rh1532IsTerrace(o)||(rh1532PlantArt.complete&&rh1532CourtImages[o.seed<=32?13471:13472].complete));')
    edit("g.save();poly(top,'#777365');g.clip();if(rh191PaveArt.complete&&rh191PaveArt.naturalWidth)g.drawImage(rh191PaveArt,x,y,w,h);else masonry(x,y,w,h,82,18,9);r(x,y,w,h,'#525b4932');g.restore();",
         "g.save();poly(top,'#777365');g.clip();if(!rh1532TerraceStone(g,o,x,y,w,h)){if(rh191PaveArt.complete&&rh191PaveArt.naturalWidth)g.drawImage(rh191PaveArt,x,y,w,h);else masonry(x,y,w,h,82,18,9);}r(x,y,w,h,'#525b4932');g.restore();")
    edit("g.restore();if(rh189Grass.complete&&rh189Grass.naturalWidth)g.drawImage(rh189Grass,bx+4,by+4,bw-8,bh-9);",
         "g.restore();if(!(rh1532IsTerrace(o)&&rh1532PlantFill(g,o,bx+3,by+3,bw-6,bh-7,bx>mid?1:0))){if(rh189Grass.complete&&rh189Grass.naturalWidth)g.drawImage(rh189Grass,bx+4,by+4,bw-8,bh-9);")
    edit("g.globalAlpha=1;ln(bx,by+bh,bx+bw,by+bh,'#383c32',2);}}",
         "g.globalAlpha=1;}ln(bx,by+bh,bx+bw,by+bh,'#383c32',2);}}")
    edit('function rh1346RoyalGardenArt(o){','function rh1346RoyalGardenArt(o){\n if(o.landmark1347&&!rh1532PlantArt.complete)return null;')
    edit("g.save();poly(inner,'#33392b');g.clip();g.drawImage(rh189Grass,", "g.save();poly(inner,'#33392b');g.clip();if(!(o.landmark1347&&rh1532PlantFill(g,o,x+9,y+7,w-18,h-14))){g.drawImage(rh189Grass,")
    edit('g.globalAlpha=1;g.restore();\n // Low front face','g.globalAlpha=1;}g.restore();\n // Low front face')
    # Render the renewed northern objects after the atlas transition so the
    # foliage and cut-stone edges are not faded into the old terrain.
    edit('function rh1325TerraceGround(cx,cy){for(const o of rh1325Terraces){','function rh1325TerraceGround(cx,cy,north=false){for(const o of rh1325Terraces){if(rh1532IsTerrace(o)!==north)continue;')
    edit('function rh1346RoyalGardenGround(cx,cy){for(const o of rh189Greens){','function rh1346RoyalGardenGround(cx,cy,north=false){for(const o of rh189Greens){if(!!o.landmark1347!==north)continue;')
    edit('rh1347CourtGround(cx,cy);\nrh1346RoyalGardenGround(cx,cy);','rh1346RoyalGardenGround(cx,cy);')
    edit('rh1521BlendTransitions(cx,cy,view.w,view.h,groundReady);rh1522Ground',
         'rh1521BlendTransitions(cx,cy,view.w,view.h,groundReady);rh1347CourtGround(cx,cy);rh1346RoyalGardenGround(cx,cy,true);rh1325TerraceGround(cx,cy,true);rh1522Ground')
    edit('royalPaving:rh1531RoyalStatus,','northernPrecinct:rh1532Status,reviewNorthernPrecinct:new URLSearchParams(location.search).has("graphicsAudit")?rh1532Review:undefined,royalPaving:rh1531RoyalStatus,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1531',b'V1532') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
