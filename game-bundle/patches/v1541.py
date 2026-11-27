"""Upgrade relocated trade stock; explicit first-party town entry; narrow legacy ground caching."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent;art=root/'assets'/'v1541'
    meta=json.loads((art/'metadata.json').read_text());models=meta['models']
    assert len(models)==15 and len({m['key'] for m in models})==15
    data={}
    for m in models:
        b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        data[m['key']]='data:image/webp;base64,'+base64.b64encode(b).decode()
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode();assert html.count(a)==1,(a[:120],html.count(a));html=html.replace(a,b,1)
    declaration='const rh1541Meta='+json.dumps(meta,separators=(',',':'))+';\nconst rh1541Art={};for(const [k,src] of Object.entries('+json.dumps(data,separators=(',',':'))+')){const im=rh1200Image();im.src=src;rh1541Art[k]=im;}\n'
    edit('function rh1389SupplyGeometry(o){const newSupply=',declaration+(root/'royal-haven-v1541.js').read_text()+'\nfunction rh1389SupplyGeometry(o){const renewed=rh1541Geometry(o);if(renewed)return renewed;const newSupply=')
    edit('rh1538Install();\ntry{rh1434Grid=', 'rh1538Install();\nrh1541Install();\ntry{rh1434Grid=')
    edit('canopyRenewal:rh1540CanopyStatus,','tradeRenewal:rh1541Status,partyArrival:rh1541PartyArrival,startParty:rh1200StartTown,canopyRenewal:rh1540CanopyStatus,')
    edit("document.getElementById('classSelect').hidden=true}","document.getElementById('classSelect').hidden=true;window.DarkFallRoyalHaven?.startParty?.()}")
    edit('let rh1200FirstArrival=false;', '''let rh1200FirstArrival=false;
const rh1541Spawn={x:1800,y:2260};let rh1541FirstParty=null;
function rh1541PartyArrival(){return {defaultZone:'Royal Haven',spawn:[rh1541Spawn.x,rh1541Spawn.y],first:rh1541FirstParty,active:active,arrived:rh1200FirstArrival};}''')
    edit("function rh1200StartTown(){if(rh1200FirstArrival||typeof started==='undefined'||!started)return;const selection=document.getElementById('classSelect');if(selection&&!selection.hidden)return;rh1200FirstArrival=true;thornApplyStats();pForestArrival1208();if(!active)open();}",'''function rh1200StartTown(){if(rh1200FirstArrival||typeof started==='undefined'||!started)return false;const selection=document.getElementById('classSelect');if(selection&&!selection.hidden)return false;rh1200FirstArrival=true;thornApplyStats();pForestArrival1208();if(!active){
 p.x=rh1541Spawn.x;p.y=rh1541Spawn.y;rh1204FromCamp=true;open();
 }rh1541FirstParty={zone:'Royal Haven',leader:[p.x,p.y],clear:!blocked(p.x,p.y),actors:rh199Party.actors.map(a=>({kind:a.kind,x:a.x,y:a.y,hidden:a.hidden,clear:!blocked(a.x,a.y)})),active};return true;}''')
    edit('function rh1200GroundOverlays(cx,cy){','function rh1200GroundOverlays(cx,cy,vw=W/rh1519Zoom,vh=H/rh1519Zoom,ready=false){')
    edit('for(let y=Math.floor(cy/rh1200TileH);y<=Math.floor((cy+H-.001)/rh1200TileH);y++)for(let x=Math.floor(cx/rh1200TileW);x<=Math.floor((cx+W-.001)/rh1200TileW);x++){','const window=rh1541GroundWindow(cx,cy,vw,vh,ready);\n for(let y=window.y0;y<=window.y1;y++)for(let x=window.x0;x<=window.x1;x++){')
    edit('()=>rh1200GroundOverlays(cx,cy));','()=>rh1200GroundOverlays(cx,cy,view.w,view.h,groundReady));')
    edit('optimization:rh1523Stats(),byKind:', 'optimization:{...rh1523Stats(),legacyGround:{...rh1541GroundStats}},byKind:')
    return b''.join(p if i%2 else p.replace(b'V1540',b'V1541') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))
if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
