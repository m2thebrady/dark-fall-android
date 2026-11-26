"""Replace the 3 repeating perimeter tower models; reconnect east wall."""
from pathlib import Path
import json,re,base64,hashlib

def apply(html:bytes)->bytes:
    root=Path(__file__).parent;art=root/'art-v1534'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(t):
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    a=re.search(rb'const rh1335TowerArt=(\[[^\n]+?\])\.map',html);assert a
    prev=json.loads(a[1]);assert len(prev)==3
    data=[uri(t) for t in meta['towers']]
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    a=re.search(rb'const rh1512FortMeta=(\{[^\n]+?\});',html);assert a
    old=json.loads(a[1])
    for t in meta['towers']:
        assert t['key'] in old
        old[t['key']].update({k:t[k] for k in ['width','height','sourceBounds','file']})
    html=html[:a.start(1)]+json.dumps(old,separators=(',',':')).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1534Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1534.js').read_text()+'\n'
    edit('function rh1457Shade(o){',info+'function rh1457Shade(o){')
    edit('try{rh1434Grid=rh1434BuildGrid();}catch(error){rh1434Grid=null;}','rh1534Install();\ntry{rh1434Grid=rh1434BuildGrid();}catch(error){rh1434Grid=null;}')
    # Taller structures require true visual bounds; avoid pop-in and
    # avoid rendering towers outside the closer camera.
    edit('for(const o of rh1335FortTowers)if(vis(o.x,o.y,360))rh117Push(o.y,()=>rh1457Facade(rh1512TowerBounds(o),o.y,()=>rh1335Tower(o)));',
         'for(const o of rh1335FortTowers){const b=rh1512TowerBounds(o);if(rh1365Intersects(b,cx,cy,18))rh117Push(o.y,()=>rh1457Facade(b,o.y,()=>rh1335Tower(o)));}')
    edit('clarity:rh1533Status,','perimeterRenewal:rh1534TowerStatus,reviewPerimeter:new URLSearchParams(location.search).has("graphicsAudit")?rh1534Review:undefined,clarity:rh1533Status,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1533',b'V1534') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
