"""Responsive forest view and Royal Haven natural-landscaping asset refresh."""
from pathlib import Path
import base64,hashlib,json,re

def apply(html):
    root=Path(__file__).parent
    def edit(a,b):
        nonlocal html
        a,b=a.encode(),b.encode()
        assert html.count(a)==1,(a[:120],html.count(a))
        html=html.replace(a,b,1)
    css=(root/'forest-v1539.css').read_text()
    edit('</style></head><body>','</style><style id="df1539-forest-viewport">'+css+'</style></head><body>')
    edit('const canvas=document.getElementById(\'screen\'),ctx=canvas.getContext(\'2d\');const W=1280,H=720;', 
         "const canvas=document.getElementById('screen'),ctx=canvas.getContext('2d');\n"+(root/'forest-v1539.js').read_text())
    edit('window.darkFallPerformance=darkFallV873Perf;\nrequestAnimationFrame(loop);','window.darkFallPerformance=darkFallV873Perf;\ndf1539Install();\nrequestAnimationFrame(loop);')
    edit('let rect=canvas.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width*W,y=(e.clientY-rect.top)/rect.height*H,c=cam();',
         'let rect=canvas.getBoundingClientRect(),{x,y}=df1539Pointer(e.clientX,e.clientY,rect),c=cam();')
    for a,b in [('Math.max(W,H)*1.3','Math.max(DF1539_BASE_W,DF1539_BASE_H)*1.3'),
      ('Math.max(W,H)*1.05','Math.max(DF1539_BASE_W,DF1539_BASE_H)*1.05'),
      ('4*W*W','4*DF1539_BASE_W*DF1539_BASE_W'),
      ('Math.min(W,H)*.72','Math.min(DF1539_BASE_W,DF1539_BASE_H)*.72'),
      ('Math.abs(p.x-v339StayAnchor.x)>W*.375||Math.abs(p.y-v339StayAnchor.y)>H*.375',
       'Math.abs(p.x-v339StayAnchor.x)>DF1539_BASE_W*.375||Math.abs(p.y-v339StayAnchor.y)>DF1539_BASE_H*.375'),
      ('darkFallMireActivationRange=W*.60','darkFallMireActivationRange=DF1539_BASE_W*.60'),
      ('LICH_SPELL_RANGE=W*1.15','LICH_SPELL_RANGE=DF1539_BASE_W*1.15')]:
        edit(a,b)
    art=root/'art-v1539';meta=json.loads((art/'metadata.json').read_text())
    models={m['key']:m for m in meta['models']}
    def uri(key):
        m=models[key];b=(art/m['file']).read_bytes()
        assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'] and b[:4]==b'RIFF' and b[8:12]==b'WEBP'
        return 'data:image/webp;base64,'+base64.b64encode(b).decode()
    for dictionary,keys in [('rh1418Art',('rock0','rock1','rock2')),('rh119Images',('fern',))]:
        m=re.search(rb'const '+dictionary.encode()+rb'=\{\};for\(const \[k,src\] of Object.entries\((\{[^\n]+?\})\)',html);assert m
        data=json.loads(m[1])
        for key in keys:
            assert key in data;data[key]=uri(key)
        html=html[:m.start(1)]+json.dumps(data,separators=(',',':')).encode()+html[m.end(1):]
    edit('fixtureRenewal:rh1538FixtureStatus,','landscapeRenewal:()=>({version:1539,models:'+json.dumps(meta['models'],separators=(',',':'))+'.map(m=>{const im=m.key==="fern"?rh119Images.fern:rh1418Art[m.key];return {...m,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height}}),newColliders:0,newDrawLayers:0,npcChanges:0}),fixtureRenewal:rh1538FixtureStatus,')
    return b''.join(p if i%2 else p.replace(b'V1538',b'V1539') for i,p in enumerate(re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)',html)))
if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes(apply(Path(sys.argv[1]).read_bytes()))
