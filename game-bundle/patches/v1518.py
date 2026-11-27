"""Royal Haven: bound expensive render work and reuse fixed street layers."""
from pathlib import Path
import re

def apply(html:bytes)->bytes:
 root=Path(__file__).parent
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1518 anchor count {html.count(a)}: {a[:120]}')
  html=html.replace(a,b,1)
 def replace_function(name,source):
  nonlocal html
  # Explicit start/end anchors for multiline functions.
  a=html.index(('function '+name+'(').encode());b=html.index(b'\n}',a)+2
  html=html[:a]+source.encode()+html[b:]
 # Render helpers placed before drawTown, after V1517 metadata.
 i=html.index(b'function rh1457Shade(')
 html=html[:i]+(root/'royal-haven-v1518.js').read_bytes()+b'\n'+html[i:]
 # Keep the original full fallback for all non-opted-in facades.
 replace_function('rh1457Facade', '''function rh1457Facade(b,base,draw){
 const previous=rh1510FacadeContext;rh1510FacadeContext=b||null;
 try{if(!rh1457Overlap(b,base,p.x,p.y)){draw();return;}rh1518MaskFacade(b,draw);}
 finally{rh1510FacadeContext=previous;}
}''')
 edit('return {...b,primary:im,upgrade:rh1511DistrictArt(o)?im:rh1510HomeUpgrade(o),style:',
      'return {...b,rh1518LocalPad:8,primary:im,upgrade:rh1511DistrictArt(o)?im:rh1510HomeUpgrade(o),style:')
 edit('return {...fit,primary:rh1451SiteArt(s),upgrade:rh1510Upgrade(s),style:',
      'return {...fit,rh1518LocalPad:rh1504Shop?.ready(s)?64:undefined,primary:rh1451SiteArt(s),upgrade:rh1510Upgrade(s),style:')
 edit('rh1457Facade(b,o.y,()=>rh1432FacadeDraw(im,b.left,b.top,b.w,b.h));','rh1457Facade({...b,rh1518LocalPad:8},o.y,()=>rh1432FacadeDraw(im,b.left,b.top,b.w,b.h));')
 edit('h:o.h,primary:rh1335TowerArt[o.k],upgrade:','h:o.h,rh1518LocalPad:8,primary:rh1335TowerArt[o.k],upgrade:')
 edit('function rh1510MarketBounds(o){return {left:o.x-o.w/2,top:o.y-o.h+6,w:o.w,h:o.h};}', 'function rh1510MarketBounds(o){return {left:o.x-o.w/2,top:o.y-o.h+6,w:o.w,h:o.h,rh1518LocalPad:8};}')
 edit('rh1457Facade({...b,primary:im,upgrade:im,style:{green:true,flues:rh1513LayoutMeta.court[o.k].flues}}','rh1457Facade({...b,rh1518LocalPad:8,primary:im,upgrade:im,style:{green:true,flues:rh1513LayoutMeta.court[o.k].flues}}')
 # Lazy art must be retained only by its intended bounded maps.
 for a,b in [
  ('if(!im){im=rh1200Image();im.src=rh119ChunkData[key];','if(!im){im=rh1518LazyImage();im.src=rh119ChunkData[key];'),
  ('if(!missing.length&&prefetch.length){prefetch.sort','if(!missing.length&&prefetch.length&&rh1518PrefetchReady(performance.now())){prefetch.sort'),
  ('const {key}=prefetch[0],im=rh1200Image();im.src=rh119ChunkData[key];','const {key}=prefetch[0],im=rh1518LazyImage();im.src=rh119ChunkData[key];'),
  ('if(!im){im=rh1200Image();im.src=src;rh1510ShoulderImages.set(z.key,im);}','if(!im){im=rh1518LazyImage();im.src=src;rh1510ShoulderImages.set(z.key,im);}'),
  ('a=src.map(uri=>{const im=rh1200Image();im.src=uri;return im;});rh1419AwningCache.set(name,a);','a=src.map(uri=>{const im=rh1518LazyImage();im.src=uri;return im;});rh1419AwningCache.set(name,a);'),
  ('if(!im){im=rh1200Image();im.src=q[4];rh1376GlassImages.set(key,im);}','if(!im){im=rh1518LazyImage();im.src=q[4];rh1376GlassImages.set(key,im);}'),
  ('if(!im){im=rh1200Image();im.src=q[4];rh1410NightImages.set(key,im);}','if(!im){im=rh1518LazyImage();im.src=q[4];rh1410NightImages.set(key,im);}')
 ]:edit(a,b)
 # Coordinate a shared heavy raster budget, with direct-art/ground fallback.
 edit('function drawTown(){rh1432BeginFacades();','function drawTown(){rh1518Begin();rh1432BeginFacades();')
 edit("c.restore();rh1200Text(title,'DARK FALL · ROYAL HAVEN · V1517');}finally{rh1433End();}}", "c.restore();rh1200Text(title,'DARK FALL · ROYAL HAVEN · V1517');}finally{rh1433End();rh1518End();}}")
 edit('if(missing){const {key,x,y}=missing,a=rhSurface(rh1200TileW,rh1200TileH)', 'if(missing&&rh1518Claim("base-tile")){const {key,x,y}=missing,a=rhSurface(rh1200TileW,rh1200TileH)')
 edit('while(rh1200GroundCache.size>22)','while(rh1200GroundCache.size>14)')
 edit('if(rh1512WallBuilds>=1)return source;','if(rh1512WallBuilds>=1||!rh1518Claim("wall"))return source;')
 edit('else if(rh1510GroundBuilds<1){','else if(rh1510GroundBuilds<1&&rh1518Claim("contact")){')
 edit('else if(rh1432Builds<1){','else if(rh1432Builds<1&&rh1518Claim("facade")){')
 edit('else if(rh1433ActorBuilds<2){','else if(rh1433ActorBuilds<2&&rh1518Claim("actor")){')
 edit('if(blocked(dx,dy+21))continue;','if(blocked(dx,dy+21)||!rh1518Claim("threshold"))continue;')
 edit('if(!a&&built<1){a=rh1517BuildWear(b);','if(!a&&built<1&&rh1518Claim("residential-wear")){a=rh1517BuildWear(b);')
 edit('if(!a&&built<1){\n   a=rhSurface(b.w,b.h);','if(!a&&built<1&&rh1518Claim("foundry-wear")){\n   a=rhSurface(b.w,b.h);')
 # The fixed late ground pass retains the precise original ordering; the
 # animated day/gallery shadows and incremental newer surfaces stay live.
 a=html.index(b'rh1459WallContacts(cx,cy);rh1460StationContacts(cx,cy);')
 b=html.index(b'\nrh1512WallFooting(cx,cy);',a)
 block=html[a:b].decode()
 assert block.endswith('rh1474Contacts(cx,cy);')
 html=html[:a]+b'rh1518StreetLayer(cx,cy,rh1518StaticDistrictPass);'+html[b:]
 anchor=b'function drawTown(){'
 i=html.index(anchor);html=html[:i]+('function rh1518StaticDistrictPass(cx,cy){'+block+'}\n').encode()+html[i:]
 # Fast world-space noise lattice values, no per-pixel hash repetition.
 edit('const data=g.getImageData(0,0,w,h),d=data.data;\n for(let y=0;y<h;y++)for(let x=0;x<w;x++){\n  const n=(y*w+x)*4;if(d[n+3]<32)continue;',
      '''const data=g.getImageData(0,0,w,h),d=data.data;
 const ox=vertical?(side<0?0:WORLD_W):start,oy=vertical?start:2360,dx=vertical&&side>0?-.5:.5;
 const broadField=rh1518NoiseField(w,h,ox,oy,dx,.5,52,84,1512),lichenField=rh1518NoiseField(w,h,ox,oy,dx,.5,8,11,1513),rainField=rh1518NoiseField(w,h,ox,oy,dx,.5,5,46,1514);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const n=(y*w+x)*4;if(d[n+3]<32)continue;''')
 edit('const broad=rh1512Noise(X,Y,52,84,1512),lichen=rh1512Noise(X,Y,8,11,1513),rain=rh1512Noise(X,Y,5,46,1514);',
      'const broad=broadField[n/4],lichen=lichenField[n/4],rain=rainField[n/4];')
 # Footing generation uses the same original noise.
 edit('const im=g.createImageData(w,h),d=im.data;\n for(let y=0;y<h;y++)for(let x=0;x<w;x++){\n  const X=ox+x,Y=oy+y,q=vertical?',
      'const im=g.createImageData(w,h),d=im.data,broadField=rh1518NoiseField(w,h,ox,oy,1,1,16,22,1521),fineField=rh1518NoiseField(w,h,ox,oy,1,1,3,4,1522);\n for(let y=0;y<h;y++)for(let x=0;x<w;x++){\n  const X=ox+x,Y=oy+y,q=vertical?')
 edit('const broad=rh1512Noise(X,Y,16,22,1521),fine=rh1512Noise(X,Y,3,4,1522),grain=rh1510Hash(X,Y,1523);',
      'const broad=broadField[y*w+x],fine=fineField[y*w+x],grain=rh1510Hash(X,Y,1523);')
 # Reset the new atlas on the existing town exit / generated cache lifecycle.
 edit('function rh1432ClearFacades(){rh1510ShoulderReset();','function rh1432ClearFacades(){rh1518Reset();rh1510ShoulderReset();')
 edit('residentialDistrict:rh1517ResidentialStatus,reviewResidential:', 'residentialDistrict:rh1517ResidentialStatus,performance:new URLSearchParams(location.search).has("graphicsAudit")?rh1518Performance:undefined,reviewResidential:')
 assert html.count(b'V1517')>=108
 return html.replace(b'V1517',b'V1518')
