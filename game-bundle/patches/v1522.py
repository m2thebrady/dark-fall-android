"""Recess frontage clutter and add four texture-based ground treatments."""
from pathlib import Path
import base64,json
def apply(html:bytes)->bytes:
 root=Path(__file__).parent;art=root/'art-v1522'
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1522 anchor {html.count(a)}: {a[:120]}')
  html=html.replace(a,b,1)
 plan=json.loads((art/'frontages.json').read_text())
 data='data:image/webp;base64,'+base64.b64encode((art/'frontages.webp').read_bytes()).decode()
 snippet='const rh1522Frontages='+json.dumps(plan,separators=(',',':'))+';\nconst rh1522ArtData='+json.dumps(data)+';\n'+(root/'royal-haven-v1522.js').read_text()+'\n'
 edit('function rh1457Shade(o){',snippet+'function rh1457Shade(o){')
 edit('rh1520Install();rh1521MarketInstall();','rh1520Install();rh1521MarketInstall();rh1522Install();')
 edit('rh1521BlendTransitions(cx,cy,view.w,view.h,groundReady);rh1457LaneShadows','rh1521BlendTransitions(cx,cy,view.w,view.h,groundReady);rh1522Ground(cx,cy,view.w,view.h,groundReady);rh1457LaneShadows')
 edit('groundPlan:rh1521Status,','frontage:rh1522FrontageStatus,groundPlan:rh1521Status,')
 assert html.count(b'V1521')>=108
 return html.replace(b'V1521',b'V1522')
