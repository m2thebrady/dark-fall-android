"""A continuous road and courtyard ground atlas, reconciled to the installed city."""
from pathlib import Path
import json,re,base64
def apply(html:bytes)->bytes:
 root=Path(__file__).parent;art=root/'art-v1521';plan=json.loads((art/'layout.json').read_text())
 def data(name):return 'data:image/webp;base64,'+base64.b64encode((art/name).read_bytes()).decode()
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1521 anchor {html.count(a)}: {a[:120]}')
  html=html.replace(a,b,1)
 def update(rx,fn):
  nonlocal html
  m=re.search(rx,html)
  if not m:raise ValueError(f'V1521 missing {rx}')
  d=json.loads(m[1]);fn(d);html=html[:m.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[m.end(1):]
 def chunks(d):
  for iy in range(1,4):
   for ix in range(9):d[f'{ix}:{iy}']=data(f'ground-{ix}-{iy}.webp')
 update(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',chunks)
 i=html.index(b'function rh1457Shade(')
 html=html[:i]+b'const rh1521Plan='+json.dumps(plan,separators=(',',':')).encode()+b';\n'+(root/'royal-haven-v1521.js').read_bytes()+b'\n'+html[i:]
 edit('rh1519ClearStreet();rh1520Install();','rh1519ClearStreet();rh1520Install();rh1521MarketInstall();')
 edit("if(o.k==='stall1'&&o.x===5845&&o.y===2084)","if(o.k==='stall1'&&(o.x===5845||o.x===5820)&&o.y===2084)")
 edit("if(o.k==='stall0'&&o.x===6240&&o.y===2085)","if(o.k==='stall0'&&(o.x===6240||o.x===6280)&&o.y===2085)")
 # Use the same lazy source tiles already drawn by the existing terrain pass.
 edit("rect(cx,cy,W,H,'#292e2a');rh119Ground(cx,cy);","rect(cx,cy,W,H,'#292e2a');rh119Ground(cx,cy);const groundReady=rh1521Ready(cx,cy,view.w,view.h);")
 edit('rh1200GroundOverlays(cx,cy);\n// Animated understory contacts','rh1521LegacyGround(cx,cy,view.w,view.h,groundReady,()=>rh1200GroundOverlays(cx,cy));\n// Animated understory contacts')
 edit('rh1325TerraceGround(cx,cy);\nrh1459CourtGround(cx,cy);','rh1325TerraceGround(cx,cy);\nrh1521LegacyGround(cx,cy,view.w,view.h,groundReady,()=>{rh1459CourtGround(cx,cy);')
 edit('rh1457LaneShadows(cx,cy);rh1462Ground(cx,cy);\nrh1518StreetLayer(cx,cy,rh1518StaticDistrictPass,view.w,view.h);\nrh1512WallFooting(cx,cy);rh1513RowGround(cx,cy);rh1514RowGround(cx,cy);rh1515StreetGround(cx,cy);rh1516StreetGround(cx,cy);rh1517StreetGround(cx,cy);rh1520ApproachGround(cx,cy);rh1511ThresholdDraw(cx,cy);',
      'rh1462Ground(cx,cy);if(!groundReady){rh1518StaticDistrictPass(cx,cy);rh1513RowGround(cx,cy);rh1514RowGround(cx,cy);rh1515StreetGround(cx,cy);rh1516StreetGround(cx,cy);rh1517StreetGround(cx,cy);}});\nrh1521BlendTransitions(cx,cy,view.w,view.h,groundReady);rh1457LaneShadows(cx,cy);if(!rh1200StaticReady)rh1200StaticReady=rh1200Images.every(im=>im.complete);rh1518StreetLayer(cx,cy,rh1521StaticContacts,view.w,view.h);rh1512WallFooting(cx,cy);rh1520ApproachGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
 # New map is generated from exactly the same worldwide artwork.
 old=re.search(rb'function rh1368DrawMapTerrain\(\)\{[^\n]+\}',html)
 assert old
 m=re.search(rb'const rh1368MapArtData="[^"]+";',html);assert m
 html=html[:m.start()]+b'const rh1368MapArtData="'+data('town-map.webp').encode()+b'";'+html[m.end():]
 old=re.search(rb'function rh1368DrawMapTerrain\(\)\{[^\n]+\}',html);assert old
 new="function rh1368DrawMapTerrain(){if(!rh1368MapArt){rh1368MapArt=new Image();rh1368MapArt.src=rh1368MapArtData;}if(!rh1368MapArt.complete||rh1368MapArt.naturalWidth!==1292)return false;mc.drawImage(rh1368MapArt,0,0,646,260);return true;}"
 html=html[:old.start()]+new.encode()+html[old.end():]
 # The separate old map lane overlay did not reflect the rebuilt streets.
 edit('rh1455LaneMap();rh1462Map();','rh1462Map();')
 edit('rh1475SquareMap();rh1467FrontMap();rh1468Map();','rh1475SquareMap();rh1468Map();')
 edit("rh1459CourtMap();rh1462Map();rh1463Map();rh1465Map();rh1472CourtMap();rh1492Court.map();rh1493Estate.map();rh1495District.map();rh1496HerbAnnex.map();rh1498Yard.map();rh1499Civic.map();rh1464Map();","rh1462Map();for(const w of rh1459Walls.concat(rh1463Walls,rh1465Walls)){mc.fillStyle='#6f6d60';mc.fillRect((w.x-w.w/2)/10,(w.y-10)/10,w.w/10,1.7);}rh1464Map();")
 edit("rh1472Trace(mc,rh1474Court,0,0,.1);mc.fillStyle='#a99c80';mc.fill();mc.fillStyle='#786d5d';","mc.fillStyle='#786d5d';")
 edit("mc.fillStyle='#676658';for(const o of rh194Courts)mc.fillRect((o.x-o.w/2)/10,o.y/10,o.w/10,o.h/10);mc.fillStyle='#938b75';","mc.fillStyle='#938b75';")
 edit("rh1472Trace(mc,rh1475Square,0,0,.1);mc.fillStyle='#ae9b7d';mc.fill();for(const o of rh1475Furniture)","for(const o of rh1475Furniture)")
 # Ground atlas replaces the old plaza-specific raster. Report the active
 # master ground rather than making browser tests wait for an unused surface.
 edit('landmarkRenewal:rh1520LandmarkStatus,','groundPlan:rh1521Status,reviewGround:new URLSearchParams(location.search).has("graphicsAudit")?rh1521Review:undefined,landmarkRenewal:rh1520LandmarkStatus,')
 assert html.count(b'V1520')>=108
 return html.replace(b'V1520',b'V1521')
