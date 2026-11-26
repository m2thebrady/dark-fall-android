"""Royal Haven: sharper residential assets and quality-first adaptive recovery."""
from pathlib import Path
import json,re,base64,hashlib

def apply(html:bytes)->bytes:
    root=Path(__file__).parent; art=root/'art-v1533'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(t,old):
        orig=base64.b64decode(old.split(',')[1])
        assert hashlib.sha256(orig).hexdigest()==t['sourceSha256'],t['key']
        b=(art/t['file']).read_bytes()
        assert len(b)==t['bytes'] and hashlib.sha256(b).hexdigest()==t['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    a=re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html);assert a
    data=json.loads(a[1])
    for t in meta['ground']:
        assert t['key'] in data
        data[t['key']]=uri(t,data[t['key']])
    html=html[:a.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[a.end(1):]
    for t in meta['facades']:
        a=list(re.finditer(re.escape(t['key'].encode())+rb'\.src="([^"]+)"',html))
        assert len(a)==1,t['key']
        m=a[0];html=html[:m.start(1)]+uri(t,m[1].decode()).encode()+html[m.end(1):]
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    edit('const rh1431Scales=[1,.85,.70];','const rh1431Scales=[1,.88,.70];')
    edit('const good=q.raf<19&&q.cost<(q.slow?10:8);',
         'const good=q.raf<19&&q.cost<(q.slow?(q.tier===2?12.5:q.tier===1?11:10):8);')
    edit('if(q.slow){q.slow=false;rh1523TimingStats.slowTransitions++;}\n   else if(q.tier>0){q.tier--;rh1523TimingStats.tierTransitions++;}',
         '// Recover image clarity at the existing 30 Hz target first.\n   if(q.tier>0){q.tier--;rh1523TimingStats.tierTransitions++;}\n   else if(q.slow){q.slow=false;rh1523TimingStats.slowTransitions++;}')
    info='const rh1533Meta='+json.dumps(meta,separators=(',',':'))+';\n'+(root/'royal-haven-v1533.js').read_text()+'\n'
    edit('function rh1457Shade(o){',info+'function rh1457Shade(o){')
    edit('northernPrecinct:rh1532Status,','clarity:rh1533Status,clarityProbe:new URLSearchParams(location.search).has("graphicsAudit")?rh1533ResolutionProbe:undefined,northernPrecinct:rh1532Status,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1532',b'V1533') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
