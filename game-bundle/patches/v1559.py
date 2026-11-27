"""Exact V1559 residential interiors and exterior door registration patch from verified V1558."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='365f636a85780174929d74a17eb54d01bc9d577d00e44f50588967ec85a1bfee'
MODULE='c8a5dca604d7b8501c331d13e311029fa6f56e17d9200a9fd3fdce7259593c78'
TARGET='669b309f8950dce2869c4494dd04027e5db7ef0d0883cce864120b9357842202'
def apply(html):
    if len(html)!=235259045 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1558 source mismatch')
    root=Path(__file__).parent/'v1559-residences'
    raw=b''.join((root/f'v1559-{i:03}.gzpart').read_bytes() for i in range(9))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1559 residential module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    if html.count(anchor)!=1:
        raise ValueError('V1559 module insertion anchor mismatch')
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1558(?![A-Za-z0-9+/_=])',b'V1559',html)
    html=html.replace(anchor,mod+b'\n'+anchor,1)
    for old,new in [(b'for(const s of sites){if(Math.hypot(p.x-s.doorX,p.y-s.doorY)<35&&performance.now()>doorLock){interact();break}}}else if(rh1554Plan(inside.name))', b'if(!rh1559ExteriorAuto(dx,dy))for(const s of sites){if(Math.hypot(p.x-s.doorX,p.y-s.doorY)<35&&performance.now()>doorLock){interact();break}}}else if(rh1554Plan(inside.name))'), (b'window.DarkFallRoyalHaven={compactMerchants:', b'window.DarkFallRoyalHaven={residentialInteriors:rh1559HomeStatus,compactMerchants:')]:
        if html.count(old)!=1: raise ValueError('V1559 exact anchor mismatch')
        html=html.replace(old,new,1)
    if len(html)!=239164697 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1559 final output mismatch')
    return html
