"""Reduce Royal Haven render-time cache churn and keep the player simulation responsive."""
from pathlib import Path
import re
def apply(html:bytes)->bytes:
 root=Path(__file__).parent
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1523 anchor {html.count(a)} {a[:100]}')
  html=html.replace(a,b,1)
 def replace_block(name,body):
  nonlocal html
  a=html.index(('function '+name+'(').encode());b=html.index(b'\n}',a)+2
  html=html[:a]+body.encode()+html[b:]
 # Install pure helpers before the rendering loop; all late references are
 # resolved only during the draw calls after the town is fully initialized.
 edit('function rh1457Shade(o){',(root/'royal-haven-v1523.js').read_text()+'\nfunction rh1457Shade(o){')
 replace_block('rh1433ActorFrame','function rh1433ActorFrame(im,sx,sy,sw,sh,x,y,w,h){\n return rh1523ActorDraw(im,sx,sy,sw,sh,x,y,w,h);\n}')
 edit('function rh1433ClearActors(){rh1433ActorCache.clear();rh1433ActorPixels=0;rh1433ActorBuilds=0;}','function rh1433ClearActors(){rh1523ClearActors();rh1433ActorCache.clear();rh1433ActorPixels=0;rh1433ActorBuilds=0;}')
 edit('function rh1431State(tier=0){return {tier,slow:false,raf:16.67,cost:0,last:0,count:0,start:0,good:0,next:-Infinity};}','function rh1431State(tier=0){return rh1523State(tier);}')
 replace_block('rh1431Observe','function rh1431Observe(q,t,cost){\n return rh1523Observe(q,t,cost);\n}')
 a=re.search(rb'function rh1431Due\(q,t,changed=false\)\{[^\n]+\}',html);assert a
 html=html[:a.start()]+b'function rh1431Due(q,t,changed=false,room=false){return rh1523Due(q,t,changed,room);}'+html[a.end():]
 edit('rh1431Due(rh1431Perf,t,room!==rh1200Room)','rh1431Due(rh1431Perf,t,room!==rh1200Room,!!room)')
 # Local, conservative device-space transparency bounds for actual art
 # callbacks. Unknown/undecoded fallback models retain the full-buffer path.
 edit('rh1457Facade({left:start,top:2360,w:end-start,h:184},2543','rh1457Facade({left:start,top:2360,w:end-start,h:184,rh1518LocalPad:4},2543')
 edit('rh1457Facade({left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h},o.y,()=>rh191Tower(o))','rh1457Facade({left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h,rh1518LocalPad:32},o.y,()=>rh191Tower(o))')
 edit('rh1457Facade({left:o.x-105,top:o.y-185,w:210,h:190},o.y,()=>rh190Arch(o,now))','rh1457Facade({left:o.x-105,top:o.y-185,w:210,h:190,rh1518LocalPad:32},o.y,()=>rh190Arch(o,now))')
 edit('rh1457Facade(b,o.y,()=>rh189House(o));','rh1457Facade(b?{...b,rh1518LocalPad:16}:b,o.y,()=>rh189House(o));')
 edit('rh1457Facade(b,o.y,()=>rh187Draw(o));','rh1457Facade(b?{...b,rh1518LocalPad:16}:b,o.y,()=>rh187Draw(o));')
 edit('rh1518LocalPad:rh1520MetaFor(s)||rh1504Shop?.ready(s)?64:undefined,','rh1518LocalPad:rh1520MetaFor(s)||rh1504Shop?.ready(s)?64:b&&rh1510Upgrade(s)?128:undefined,')
 edit('w:rh1407Gate.w,h:rh1407Gate.h},2470,()=>rh118Gate(cx,cy))','w:rh1407Gate.w,h:rh1407Gate.h,rh1518LocalPad:rh118Ready(\'gate\')?64:undefined},2470,()=>rh118Gate(cx,cy))')
 edit('function rh1365Intersects(b,cx,cy,pad=0){return b.left+b.w+pad>cx&&b.left-pad<cx+W&&b.top+b.h+pad>cy&&b.top-pad<cy+H;}','function rh1365Intersects(b,cx,cy,pad=0){return rh1523Intersects(b,cx,cy,pad);}')
 edit('rh1431LightVisible(x,y,r,camX,camY)','rh1431LightVisible(x,y,r,camX,camY,W/rh1519Zoom,H/rh1519Zoom)')
 # Protect initial scene transitions against a burst of expensive projected
 # shadow raster allocations. Existing static footing and contact shading
 # remain while newly encountered silhouette projections are populated.
 edit(' // Use the actual source alpha, compressed onto the ground and projected eastward.',' if(rh1433InExterior&&!rh1518Claim("shadow"))return null;\n // Use the actual source alpha, compressed onto the ground and projected eastward.')
 # Sample only the bottom band for silhouette-aligned contact masks, not an
 # entire building-sized temporary canvas. The sampled source is identical.
 edit('const w=Math.ceil(f.w),h=Math.ceil(f.h),sample=rhSurface(w,h),g=sample.getContext(\'2d\');g.drawImage(im,0,0,w,h);\n const band=Math.min(h,Math.ceil(h*.28)),a=g.getImageData(0,h-band,w,band).data,pad=18,mask=rhSurface(w+pad*2,band+pad*2+20),mg=mask.getContext(\'2d\');',
      'const w=Math.ceil(f.w),h=Math.ceil(f.h),band=Math.min(h,Math.ceil(h*.28)),sample=rhSurface(w,band),g=sample.getContext(\'2d\',{willReadFrequently:true});g.drawImage(im,0,band-h,w,h);\n const a=g.getImageData(0,0,w,band).data,pad=18,mask=rhSurface(w+pad*2,band+pad*2+20),mg=mask.getContext(\'2d\');')
 edit('if(count<8)return null;\n const soft=rhSurface(mask.width,mask.height)','if(count<8){rh1372Contacts.set(key,null);return null;}\n const soft=rhSurface(mask.width,mask.height)')
 # Include diagnostic counters in existing graphics-audit-only status.
 edit('return {...rh1518Stats,byKind:{...rh1518Stats.byKind},streetTiles:','return {...rh1518Stats,optimization:rh1523Stats(),byKind:{...rh1518Stats.byKind},streetTiles:')
 assert html.count(b'V1522')>=108
 return html.replace(b'V1522',b'V1523')
