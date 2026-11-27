"""Exact V1560 human-scale room props, residential expansion, and market clearance patch from verified V1559."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='669b309f8950dce2869c4494dd04027e5db7ef0d0883cce864120b9357842202'
MODULE='7070cbe99666fe4fd52b2e4e7c0c52c794ddf829e5849c42c73f5dd3a46a2ca5'
TARGET='f262141741b5c15f72a7163a3e256ed3f37d2776b416ed15a3c16222fcb00aac'
def apply(html):
    if len(html)!=239164697 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1559 source mismatch')
    root=Path(__file__).parent/'v1560-proportions'
    raw=b''.join((root/f'v1560-{i:03}.gzpart').read_bytes() for i in range(4))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1560 proportion module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    if html.count(anchor)!=1:
        raise ValueError('V1560 module insertion anchor mismatch')
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1559(?![A-Za-z0-9+/_=])',b'V1560',html)
    html=html.replace(anchor,mod+b'\n'+anchor,1)
    for old,new in [(b'window.DarkFallRoyalHaven={residentialInteriors:', b'window.DarkFallRoyalHaven={assetScale:rh1560ScaleStatus,residentialInteriors:')]:
        if html.count(old)!=1: raise ValueError('V1560 exact anchor mismatch')
        html=html.replace(old,new,1)
    if len(html)!=240928991 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1560 final output mismatch')
    return html
