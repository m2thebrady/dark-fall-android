"""Exact V1556 merchant scene and navigation patch from verified V1555."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='7ccc95ab1767a78fc36834b570eb2f05d28a1374adc8a4478fcc5c80d5c3bdfc'
MODULE='3ecf86a7f9c14c6b783943d218b956125ed87b4ef8ba87cda0381ec7257aa931'
TARGET='d5a12324a37976000394585fbd4c0f2f375d6bacc325f0347e367489ded3a673'
def apply(html):
    if len(html)!=224672897 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1555 source mismatch')
    root=Path(__file__).parent/'v1556-merchants'
    raw=b''.join((root/f'v1556-{i:03}.gzpart').read_bytes() for i in range(7))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1556 merchant module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    old=b'const bounds=cv.getBoundingClientRect(),x=(e.clientX-bounds.left)*W/bounds.width,y=(e.clientY-bounds.top)*H/bounds.height;\n const d=rh1554PortalAt(name,p.x,p.y);'
    new=b'const bounds=cv.getBoundingClientRect(),screenX=(e.clientX-bounds.left)*W/bounds.width,screenY=(e.clientY-bounds.top)*H/bounds.height;\n const [x,y]=rh1556PointerInside(name,screenX,screenY);\n const d=rh1554PortalAt(name,p.x,p.y);'
    if html.count(anchor)!=1 or html.count(old)!=1:
        raise ValueError('V1556 module or pointer insertion anchor mismatch')
    html=html.replace(old,new,1).replace(anchor,mod+b'\n'+anchor,1)
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1555(?![A-Za-z0-9+/_=])',b'V1556',html)
    if len(html)!=227701530 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1556 final output mismatch')
    return html
