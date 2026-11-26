"""Royal Haven Northcourt: two measured angular residences and a baked flagstone court."""
from pathlib import Path
import base64,json,re

def apply(html:bytes)->bytes:
 root=Path(__file__).parent;art=root/'art-v1525'
 meta=json.loads((art/'metadata.json').read_text())
 def uri(file):
  p=art/file
  if p.exists(): payload=base64.b64encode(p.read_bytes()).decode('ascii')
  else:
   payload=(art/(file+'.b64')).read_text().strip()
   base64.b64decode(payload,validate=True)
  return 'data:image/webp;base64,'+payload
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  assert html.count(a)==1,(a,html.count(a))
  html=html.replace(a,b,1)
 a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)
 assert a,'V1524 terrain missing'
 d=json.loads(a[1])
 for tile in meta['ground']:
  assert tile['key'] in d
  d[tile['key']]=uri(tile['file'])
 html=html[:a.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[a.end(1):]
 html,n=re.subn(rb'const rh1368MapArtData="[^"]+";',('const rh1368MapArtData="'+uri('map.webp')+'";').encode(),html,count=1)
 assert n==1
 info='const rh1525Meta='+json.dumps(meta,separators=(',',':'))+';\n'
 info+='const rh1525Art={};for(const [key,src] of Object.entries('+json.dumps({k:uri(v['file']) for k,v in meta['homes'].items()},separators=(',',':'))+')){const im=rh1200Image();im.src=src;rh1525Art[key]=im;}\n'
 edit('function rh1457Shade(o){',info+(root/'royal-haven-v1525.js').read_text()+'\nfunction rh1457Shade(o){')
 edit("const glow=rh1510MarketBuilding(o)||rh1511DistrictArt(o)?null:rh1464Art[o.k+'Night'];","const revised=rh1525Applied&&rh1525Meta.homes[o.k];const glow=revised||rh1510MarketBuilding(o)||rh1511DistrictArt(o)?null:rh1464Art[o.k+'Night'];")
 edit('if(rh1511DistrictArt(o))rh1511WindowGlass(o,b);const a=rh1433Day().night;','if(rh1511DistrictArt(o))rh1511WindowGlass(o,b);if(revised)rh1510WindowTint(revised.windows,b.left,b.top,b.w,b.h);const a=rh1433Day().night;')
 edit('rh1520Install();rh1521MarketInstall();rh1522Install();','rh1520Install();rh1521MarketInstall();rh1522Install();rh1525Install();')
 edit('landscape:rh1524LandscapeStatus,','northcourt:rh1525Status,reviewNorthcourt:new URLSearchParams(location.search).has("graphicsAudit")?rh1525Review:undefined,landscape:rh1524LandscapeStatus,')
 # Do not change version-looking byte sequences inside embedded images.
 chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
 return b''.join(part if i%2 else part.replace(b'V1524',b'V1525') for i,part in enumerate(chunks))

if __name__=='__main__':
 import sys
 Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
