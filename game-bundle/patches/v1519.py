"""Royal Haven: closer camera, remove leftover seating, forgiving street collision."""
from pathlib import Path

def apply(html:bytes)->bytes:
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1519 anchor {html.count(a)}: {a[:120]}')
  html=html.replace(a,b,1)
 root=Path(__file__).parent
 # Must precede the early collision-grid creation and all temporary placement audits.
 i=html.index(b'let rh1434Grid=null;')
 html=html[:i]+(root/'royal-haven-v1519.js').read_bytes()+b'\n'+html[i:]
 # Preserve the placement-time checks; objects are marked only after all scenery is installed.
 edit('const sym=(o,rx,ry)=>add(o,o.x-rx,o.x+rx,o.y-ry,o.y+ry,(x,y)=>Math.abs(x-o.x)<rx&&Math.abs(y-o.y)<ry);',
      'const sym=(o,rx,ry)=>{if(!rh1519Soft.has(o))add(o,o.x-rx,o.x+rx,o.y-ry,o.y+ry,(x,y)=>Math.abs(x-o.x)<rx&&Math.abs(y-o.y)<ry);};')
 edit('for(const o of rh117Props){const [w,h]=rh1387SupplyFoot(o);if(Math.abs(x-o.x)<w&&Math.abs(y-o.y)<h)return true;}',
      'for(const o of rh117Props){if(rh1519Soft.has(o))continue;const [w,h]=rh1387SupplyFoot(o);if(Math.abs(x-o.x)<w&&Math.abs(y-o.y)<h)return true;}')
 edit('rh118Props.some(o=>Math.abs(x-o.x)<o.r&&Math.abs(y-o.y)<17)', 'rh118Props.some(o=>!rh1519Soft.has(o)&&Math.abs(x-o.x)<o.r&&Math.abs(y-o.y)<17)')
 edit("rh119Garden.some(o=>o.k==='rock'&&Math.abs(x-o.x)<o.w*.35&&Math.abs(y-o.y)<13)", "rh119Garden.some(o=>!rh1519Soft.has(o)&&o.k==='rock'&&Math.abs(x-o.x)<o.w*.35&&Math.abs(y-o.y)<13)")
 for name in ['rh171Furnishings','rh175Objects','rh176Props','rh192Edges','rh194Props']:
  edit(f'{name}.some(o=>Math.abs(x-o.x)<o.rx&&Math.abs(y-o.y)<o.ry)',f'{name}.some(o=>!rh1519Soft.has(o)&&Math.abs(x-o.x)<o.rx&&Math.abs(y-o.y)<o.ry)')
 for name in ['rh1460Stations','rh1465Props']:
  edit(f'{name}.some(o=>Math.abs(x-o.x)<o.rx&&y>o.y-o.ry&&y<o.y+4)',f'{name}.some(o=>!rh1519Soft.has(o)&&Math.abs(x-o.x)<o.rx&&y>o.y-o.ry&&y<o.y+4)')
 edit('(Math.abs(x-1690)<9&&Math.abs(y-2320)<9)||rhObstacle(x,y)', 'rhObstacle(x,y)')
 edit('rh1514RemoveStreetBenches();\n', 'rh1514RemoveStreetBenches();rh1519ClearStreet();\n')
 # Apply one uniform world transform, preserve room canvas and HTML UI.
 edit('const cx=Math.max(0,Math.min(WORLD_W-W,p.x-W/2)),cy=Math.max(Math.min(WORLD_H-H,p.y-(H-96)),-royalView*92,Math.min(WORLD_H-H,p.y-H/2-northBias-royalView*38));camX=cx;camY=cy;c.save();c.translate(-cx,-cy);',
      'const view=rh1519Camera(p.x,p.y,royalView,northBias),cx=view.x,cy=view.y;camX=cx;camY=cy;c.save();c.scale(view.zoom,view.zoom);c.translate(-cx,-cy);')
 edit('const vis=(x,y,r=180)=>x>cx-r&&x<cx+W+r&&y>cy-r&&y<cy+H+r;', 'const vis=(x,y,r=180)=>x>cx-r&&x<cx+view.w+r&&y>cy-r&&y<cy+view.h+r;')
 edit('const xx=s.doorX-camX,yy=s.doorY-camY;if(Math.hypot(xx-x,yy-y)<48', 'const hit=rh1519WorldPoint(x,y,camX,camY);if(Math.hypot(s.doorX-hit.x,s.doorY-hit.y)<48')
 # Keep interior movement as-is and preserve automatic entrances.
 edit('const speed=inside?220:270;const steps=Math.max(1,Math.ceil(speed*dt/9));for(let i=0;i<steps;i++){const x=p.x+dx*speed*dt/steps,y=p.y+dy*speed*dt/steps;if(!blocked(x,p.y))p.x=x;if(!blocked(p.x,y))p.y=y}', 
      'const speed=inside?220:270;if(!inside)rh1519Walk(p,dx*speed*dt,dy*speed*dt,blocked);else{const steps=Math.max(1,Math.ceil(speed*dt/9));for(let i=0;i<steps;i++){const x=p.x+dx*speed*dt/steps,y=p.y+dy*speed*dt/steps;if(!blocked(x,p.y))p.x=x;if(!blocked(p.x,y))p.y=y}}')
 # Cache only the actually visible atlas tiles; fixed tile generation still uses
 # its original conservative culling footprint (so edge marks are not lost).
 edit('function rh1518StreetTiles(cx,cy){','function rh1518StreetTiles(cx,cy,vw=W,vh=H){')
 edit('(cy+H-.001)/rh1518TileH','(cy+vh-.001)/rh1518TileH')
 edit('(cx+W-.001)/rh1518TileW','(cx+vw-.001)/rh1518TileW')
 edit('function rh1518StreetLayer(cx,cy,pass){','function rh1518StreetLayer(cx,cy,pass,vw=W,vh=H){')
 edit('const wanted=rh1518StreetTiles(cx,cy),missing=[];','const wanted=rh1518StreetTiles(cx,cy,vw,vh),missing=[];')
 edit('rh1518StreetLayer(cx,cy,rh1518StaticDistrictPass);','rh1518StreetLayer(cx,cy,rh1518StaticDistrictPass,view.w,view.h);')
 # Zoom-aware terrain residency and all existing map/room controls unchanged.
 a=html.index(b'function rh119Ground(cx,cy){')
 b=html.index(b'\n}',a)+2
 ground=html[a:b].decode()
 ground=ground.replace('const wanted=new Set()','const vw=W/rh1519Zoom,vh=H/rh1519Zoom,wanted=new Set()').replace('cy+H','cy+vh').replace('cx+W','cx+vw').replace('cx-W/2','cx-vw/2').replace('cy-H/2','cy-vh/2')
 html=html[:a]+ground.encode()+html[b:]
 edit('residentialDistrict:rh1517ResidentialStatus,performance:', 'residentialDistrict:rh1517ResidentialStatus,navigation:new URLSearchParams(location.search).has("graphicsAudit")?rh1519Navigation:undefined,reviewWalk:new URLSearchParams(location.search).has("graphicsAudit")?rh1519ReviewWalk:undefined,performance:')
 assert html.count(b'V1518')>=108
 return html.replace(b'V1518',b'V1519')
