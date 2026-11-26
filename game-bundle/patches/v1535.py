"""Renew the full perimeter wall kit with baked continuous modular artwork."""
from pathlib import Path
import json,re,base64,hashlib

def apply(html:bytes)->bytes:
    root=Path(__file__).parent;art=root/'art-v1535'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(t):
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    a=re.search(rb'const rh1335SideArt=(\[[^\n]+?\])\.map',html);assert a
    assert len(json.loads(a[1]))==3
    html=html[:a.start(1)]+json.dumps([uri(t) for t in meta['side']],separators=(',',':')).encode()+html[a.end(1):]
    a=re.search(rb'const rh1215WallArt=Object.values\((\{[^\n]+?\})\)\.map',html);assert a
    assert len(json.loads(a[1]))==4
    html=html[:a.start(1)]+json.dumps({t['key']:uri(t) for t in meta['curtain']},separators=(',',':')).encode()+html[a.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    def replace_function(start,end,new):
        nonlocal html
        l=html.index(start.encode());r=html.index(end.encode(),l+1)
        html=html[:l]+new.encode()+html[r:]
    edit('rh1335SideArt[Math.floor(y/240)%3]','rh1335SideArt[Math.floor(y/240)%rh1335SideArt.length]')
    # Replace on-demand per-segment canvas shading with shared decoded images.
    replace_function('function rh1512WallSegment(source,side,start){','// Narrow irregular foundation banks',
                     'function rh1512WallSegment(source,side,start){return rh1535WallRef(source,side,start);}\n')
    replace_function('function rh1512FootSegment(side,start){','function rh1512WallFooting(cx,cy){',
                     'function rh1512FootSegment(side,start){return rh1535FootRef(side,start);}\n')
    edit('const a=rh1512FootSegment(side,y);c.drawImage(a.can,a.x,a.y);',
         'const a=rh1512FootSegment(side,y);if(a)c.drawImage(a.can,a.x,a.y);')
    edit('const a=rh1512FootSegment(0,x);\n   // Retain','const a=rh1512FootSegment(0,x);if(!a)continue;\n   // Retain')
    # The unused legacy fallback also derives source clipping from the new
    # actual asset dimensions, rather than the old fixed 960x464 source.
    edit('c.drawImage(a,(start-x)*4,0,(end-start)*4,464,start,2428,end-start,116);',
         'c.drawImage(a,(start-x)*a.naturalWidth/240,0,(end-start)*a.naturalWidth/240,a.naturalHeight,start,2428,end-start,116);')
    old=b'c.drawImage(rh1215WallSection(y),0,0,960,280,y,0,240,70);'
    assert html.count(old)==2
    html=html.replace(old,b'c.drawImage(rh1215WallSection(y),0,0,rh1215WallSection(y).naturalWidth,rh1215WallSection(y).naturalHeight*.60,y,0,240,70);')
    info='const rh1535Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1535.js').read_text()+'\n'
    info+='const rh1535FootArt={south:[],west:[],east:[]};\n'
    for t in meta['foot']:
        item=f'rh1535FootArt.{t["kind"]}[{int(t["key"])}]'
        info+=f'{item}=rh1200Image();{item}.src="{uri(t)}";\n'
    edit('function rh1457Shade(o){',info+'function rh1457Shade(o){')
    edit('perimeterRenewal:rh1534TowerStatus,','wallRenewal:rh1535WallStatus,reviewWalls:new URLSearchParams(location.search).has("graphicsAudit")?rh1535Review:undefined,perimeterRenewal:rh1534TowerStatus,')
    parts=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1534',b'V1535') for i,part in enumerate(parts))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
