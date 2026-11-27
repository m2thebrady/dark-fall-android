"""Three original landmark sprites with precise entrance, glass, smoke, flame and ground alignment."""
from pathlib import Path
import base64,json,re

def apply(html:bytes)->bytes:
 root=Path(__file__).parent;art=root/'art-v1520';meta=json.loads((art/'metadata.json').read_text())
 assert set(meta)=={'mage','cave','cellar'}
 def dump(x):return json.dumps(x,separators=(',',':')).encode()
 def url(k):return 'data:image/webp;base64,'+base64.b64encode((art/meta[k]['file']).read_bytes()).decode()
 def edit(a,b):
  nonlocal html
  a,b=a.encode(),b.encode()
  if html.count(a)!=1:raise ValueError(f'V1520 anchor {html.count(a)}: {a[:120]}')
  html=html.replace(a,b,1)
 def update(rx,fn):
  nonlocal html
  m=re.search(rx,html)
  if not m:raise ValueError(f'Missing V1520 anchor {rx}')
  x=json.loads(m[1]);fn(x);html=html[:m.start(1)]+dump(x)+html[m.end(1):]
 update(rb'const rh193Art=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({k:url(k) for k in ['mage','cave']}))
 def cell_meta(d):
  for k in ['Storehouse Cellar','variant:cellar-relocated']:
   d[k].update({x:meta['cellar'][x] for x in ['file','width','height','door','flues','lanterns']});d[k]['legacy']=False
 update(rb'const rh1510ArtMeta=(\{[^\n]+?\});',cell_meta)
 update(rb'const rh1510Art=\{\};for\(const \[name,src\] of Object.entries\((\{[^\n]+?\})\)',lambda d:d.update({k:url('cellar') for k in ['Storehouse Cellar','variant:cellar-relocated']}))
 # In the new source dimensions, every light, animated cloth and entrance is
 # measured independently. Do not reuse the previous landmark's pixel overlays.
 i=html.index(b'function rh1457Shade(')
 html=html[:i]+b'const rh1520Meta='+dump(meta)+b';\n'+(root/'royal-haven-v1520.js').read_bytes()+b'\n'+html[i:]
 edit('const a=academy?[.438,.976]:rh1269Anchors[s.type];','const a=academy?rh1520Meta.mage.door:s.type===\'cave\'&&im===rh193Art.cave?rh1520Meta.cave.door:rh1269Anchors[s.type];')
 edit("if(k==='mage')rh1376DrawGlass('landmark:'+k,left,base-h,w,h);","if(k==='mage')rh1510WindowTint(rh1520Meta.mage.windows,left,base-h,w,h);")
 edit('[[0.35802,0.59552,0.02400,0.08300],[0.68930,0.59552,0.02400,0.08300]]','rh1520Meta.cave.flames')
 edit('anchors=[[.35802,.57444],[.68930,.57444]];','anchors=rh1520Meta.cave.lamps;')
 edit('"mage": [[0.349, 0.779], [0.525, 0.779]]','"mage": rh1520Meta.mage.lamps.map(a=>a.slice(0,2))')
 # Rewrite the complete old mage set only; temple remains unchanged.
 edit('mage:{lamps:[[.349,.779,.007,.016],[.525,.779,.007,.016]],cloth:[[[.280,.622],[.314,.622],[.314,.757],[.297,.798],[.280,.759]],[[.575,.614],[.610,.614],[.610,.756],[.592,.798],[.576,.756]]],flues:[[.234,.273],[.260,.278]]}', 
      'mage:{lamps:rh1520Meta.mage.lamps,cloth:rh1520Meta.mage.cloth,flues:rh1520Meta.mage.flues}')
 edit('function rh180Facade(s){if(rh1504Shop?.draw(s))return true;', 'function rh180Facade(s){if(rh1504Shop?.draw(s)||rh1520CellarDraw(s))return true;')
 edit('function rh1365SiteBounds(s){const q=rh1504Shop?.fit(s);', 'function rh1365SiteBounds(s){const q=rh1520CellarFit(s)||rh1504Shop?.fit(s);')
 edit('function rh1451SiteArt(s){const q=rh1504Shop?.image(s);', 'function rh1451SiteArt(s){if(rh1520CellarReady(s))return rh1510Upgrade(s);const q=rh1504Shop?.image(s);')
 edit('const fit=rh1504Shop?.fit(s),w=fit?.w??s.w*.99,h=fit?.h??w*im.naturalHeight/im.naturalWidth,left=fit?.left??s.doorX-w*st[4],top=fit?.top??s.doorY+4-h;',
      'const fit=rh1520CellarFit(s)||rh1504Shop?.fit(s),w=fit?.w??s.w*.99,h=fit?.h??w*im.naturalHeight/im.naturalWidth,left=fit?.left??s.doorX-w*st[4],top=fit?.top??s.doorY+4-h;')
 edit('const fit=rh1504Shop?.fit(b),w=fit?.w??b.w*.99,h=fit?.h??w*im.naturalHeight/im.naturalWidth,left=fit?.left??b.doorX-w*st[4],top=fit?.top??b.doorY+4-h;',
      'const fit=rh1520CellarFit(b)||rh1504Shop?.fit(b),w=fit?.w??b.w*.99,h=fit?.h??w*im.naturalHeight/im.naturalWidth,left=fit?.left??b.doorX-w*st[4],top=fit?.top??b.doorY+4-h;')
 edit('return {...fit,rh1518LocalPad:rh1504Shop?.ready(s)?64:undefined,','return {...fit,rh1518LocalPad:rh1520MetaFor(s)||rh1504Shop?.ready(s)?64:undefined,')
 edit('rh1514RemoveStreetBenches();rh1519ClearStreet();','rh1514RemoveStreetBenches();rh1519ClearStreet();rh1520Install();')
 edit('function rh1510GroundReset(){rh1517WearCache.clear();','function rh1510GroundReset(){rh1520ApproachCache.clear();rh1517WearCache.clear();')
 edit('rh1517StreetGround(cx,cy);rh1511ThresholdDraw(cx,cy);','rh1517StreetGround(cx,cy);rh1520ApproachGround(cx,cy);rh1511ThresholdDraw(cx,cy);')
 # Previous civic audit should measure only installed solids, not the removed seat.
 edit('objects:objects.map(o=>({k:o.k,foot:footprint(o,true)}))','objects:objects.filter(o=>rh1464Homes.includes(o)).map(o=>({k:o.k,foot:footprint(o,true)}))')
 edit('const civic=Object.entries(rh1515LayoutMeta.civic).map(', 'const civic=Object.entries(rh1515LayoutMeta.civic).filter(([key])=>key!==\'rh1499stoneSeat\').map(')
 edit('residentialDistrict:rh1517ResidentialStatus,navigation:', 'residentialDistrict:rh1517ResidentialStatus,landmarkRenewal:rh1520LandmarkStatus,reviewLandmark:new URLSearchParams(location.search).has("graphicsAudit")?rh1520ReviewLandmark:undefined,navigation:')
 assert html.count(b'V1519')>=108
 return html.replace(b'V1519',b'V1520')
