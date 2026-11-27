"""Exact V1555 cave scene and gameplay-layout patch from verified V1554."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='1c23b8edfa60f294a651eb9a9355de5d9f9383b133cf983260d6addfa0144dc3'
MODULE='8922de1d7683ef6c95ea0754999d6b2e64bc8b805e53f67fb039d70e8d37358a'
TARGET='7ccc95ab1767a78fc36834b570eb2f05d28a1374adc8a4478fcc5c80d5c3bdfc'
def apply(html):
    if len(html)!=222552795 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1554 source mismatch')
    root=Path(__file__).parent/'v1555-cave'
    raw=b''.join((root/f'v1555-{i:03}.gzpart').read_bytes() for i in range(5))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1555 cave module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    if html.count(anchor)!=1:
        raise ValueError('V1555 module insertion anchor mismatch')
    html=html.replace(anchor,mod+b'\n'+anchor,1)
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1554(?![A-Za-z0-9+/_=])',b'V1555',html)
    if len(html)!=224672897 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1555 final output mismatch')
    return html
