"""Distinct merchant booths and a realistic paved market court."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html:bytes)->bytes:
    root=Path(__file__).parent
    art=root/'art-v1529'
    meta=json.loads((art/'metadata.json').read_text())
    def uri(item):
        b=(art/item['file']).read_bytes()
        assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
        assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode('ascii')
    def update(pattern,fn):
        nonlocal html
        a=re.search(pattern,html);assert a,pattern
        d=json.loads(a[1]);fn(d)
        html=html[:a.start(1)]+json.dumps(d,separators=(',',':')).encode()+html[a.end(1):]
    def terrain(d):
        for t in meta['ground']:
            assert t['key'] in d
            d[t['key']]=uri(t)
    update(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',terrain)
    def models(d):
        for k,m in meta['stalls'].items():
            assert k not in d
            d[k]=uri(m)
    update(rb'const rh1512MarketVariants=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',models)
    def measures(d):
        for k,m in meta['stalls'].items():
            assert k not in d
            d[k]={x:m[x] for x in ('file','width','height','sourceBounds','name','counterHeight')}
    update(rb'const rh1512FortMeta=(\{[^\n]+?\});',measures)
    def edit(old,new):
        nonlocal html
        old,new=old.encode(),new.encode()
        assert html.count(old)==1,(old[:100],html.count(old))
        html=html.replace(old,new,1)
    info='const rh1529MarketMeta='+json.dumps(meta,separators=(',',':'))+';\n'
    edit('function rh1457Shade(o){',info+(root/'royal-haven-v1529.js').read_text()+'\nfunction rh1457Shade(o){')
    edit(" if(o.k==='stall1'&&(o.x===5845||o.x===5820)&&o.y===2084)return 'spice';"," const newer=rh1529MarketVariant(o);if(newer)return newer;\n if(o.k==='stall1'&&(o.x===5845||o.x===5820)&&o.y===2084)return 'spice';")
    edit('const k=rh1512MarketVariant(o),im=k?rh1512MarketVariants[k]:null;', "const k=rh1512MarketVariant(o),im=k==='grainCart'?rh1417Art.cargo2:k?rh1512MarketVariants[k]:null;")
    edit('streetClearance:rh1528Status,','marketCourt:rh1529MarketStatus,reviewMarketCourt:new URLSearchParams(location.search).has("graphicsAudit")?rh1529ReviewMarket:undefined,streetClearance:rh1528Status,')
    chunks=re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)
    return b''.join(part if i%2 else part.replace(b'V1528',b'V1529') for i,part in enumerate(chunks))

if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
