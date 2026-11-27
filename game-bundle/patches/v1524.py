"""Royal Haven terrain and residential connections, baked into existing terrain chunks."""
from pathlib import Path
import base64,json,re
def apply(html:bytes)->bytes:
 root=Path(__file__).parent;art=root/'art-v1524'
 meta=json.loads((art/'landscape.json').read_text())
 def uri(file):
  return 'data:image/webp;base64,'+base64.b64encode((art/file).read_bytes()).decode('ascii')
 a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)
 if not a:raise ValueError('V1524 terrain missing')
 d=json.loads(a[1])
 for tile in meta['tiles']:
  assert tile['key'] in d
  d[tile['key']]=uri(tile['file'])
 html=html[:a.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[a.end(1):]
 for name,file in [('rh1368MapArtData','map.webp'),('rh1522ArtData','frontages.webp')]:
  html,n=re.subn(('const '+name+'="[^"]+";').encode(),('const '+name+'="'+uri(file)+'";').encode(),html,count=1)
  assert n==1,name
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode();assert html.count(a)==1,a
  html=html.replace(a,b,1)
 info={k:v for k,v in meta.items() if k!='tiles'};info['tileCount']=len(meta['tiles'])
 edit('function rh1457Shade(o){','const rh1524Landscape='+json.dumps(info,separators=(',',':'))+';\n'+(root/'royal-haven-v1524.js').read_text()+'\nfunction rh1457Shade(o){')
 edit('frontage:rh1522FrontageStatus,','landscape:rh1524LandscapeStatus,reviewLandscape:new URLSearchParams(location.search).has("graphicsAudit")?rh1524Review:undefined,frontage:rh1522FrontageStatus,')
 assert html.count(b'V1523')>=108
 return html.replace(b'V1523',b'V1524')
