"""Exact V1558 specialist interior and navigation patch from verified V1557."""
from pathlib import Path
import gzip, hashlib, re
SOURCE='214b7b8dfca36528e1cbebe88f858d076dce485fe08f3512d9f51c57afb4ad3c'
MODULE='78b5b90e289dcaf281af7c191e06ba186518e198efe643ee1ce1efe27027d007'
TARGET='365f636a85780174929d74a17eb54d01bc9d577d00e44f50588967ec85a1bfee'
def apply(html):
    if len(html)!=231375473 or hashlib.sha256(html).hexdigest()!=SOURCE:
        raise ValueError('V1557 source mismatch')
    root=Path(__file__).parent/'v1558-specialists'
    raw=b''.join((root/f'v1558-{i:03}.gzpart').read_bytes() for i in range(9))
    if hashlib.sha256(raw).hexdigest()!=MODULE:
        raise ValueError('V1558 specialist module checksum mismatch')
    mod=gzip.decompress(raw)
    anchor=b'try{rh1434Grid='
    if html.count(anchor)!=1:
        raise ValueError('V1558 module insertion anchor mismatch')
    html=re.sub(rb'(?<![A-Za-z0-9+/_=])V1557(?![A-Za-z0-9+/_=])',b'V1558',html)
    html=html.replace(anchor,mod+b'\n'+anchor,1)
    if len(html)!=235259045 or hashlib.sha256(html).hexdigest()!=TARGET:
        raise ValueError('V1558 final output mismatch')
    return html
