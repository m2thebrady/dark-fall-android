"""Exact V1557 artisan workshop and navigation patch from verified V1556."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='d5a12324a37976000394585fbd4c0f2f375d6bacc325f0347e367489ded3a673'
MODULE='8edd0cb18e2e87d3a69ba23da757a744b5e1065c534d332ddc100375a479fb93'
TARGET='214b7b8dfca36528e1cbebe88f858d076dce485fe08f3512d9f51c57afb4ad3c'
def apply(html):
    if len(html)!=227701530 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1556 source mismatch')
    root=Path(__file__).parent/'v1557-workshops'
    raw=b''.join((root/f'v1557-{i:03}.gzpart').read_bytes() for i in range(8))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1557 workshop module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    if html.count(anchor)!=1:
        raise ValueError('V1557 module insertion anchor mismatch')
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1556(?![A-Za-z0-9+/_=])',b'V1557',html)
    html=html.replace(anchor,mod+b'\n'+anchor,1)
    if len(html)!=231375473 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1557 final output mismatch')
    return html
