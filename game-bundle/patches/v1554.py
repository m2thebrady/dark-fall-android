"""Consolidate verified V1548 with recovered Temple, Castle and Caster Guild artwork.
Fail closed on missing, changed or misordered input. All binary instructions are
copy ranges or literal bytes; the reconstructed result is hash-checked.
"""
from pathlib import Path
import gzip
import hashlib
import struct

SOURCE = 'ff0273b79a05f5daff90b127035f750518af064485775d02d3a05b91bb3c7ce1'
DELTA = 'cb188acdfd294e8ac6537aa661bd529349bf7e3a9600f6edb277aab7dca6f4a7'
TARGET = '1c23b8edfa60f294a651eb9a9355de5d9f9383b133cf983260d6addfa0144dc3'

def apply(html):
    if len(html) != 208050903 or hashlib.sha256(html).hexdigest() != SOURCE:
        raise ValueError('Incorrect V1542 base for consolidated V1554')
    directory = Path(__file__).parent / 'v1554-delta'
    raw = b''.join((directory / f'v1554-{i:03}.gzpart').read_bytes() for i in range(32))
    if hashlib.sha256(raw).hexdigest() != DELTA:
        raise ValueError('Invalid V1554 delta')
    delta = gzip.decompress(raw)
    out = bytearray()
    at = 0
    while at < len(delta):
        kind = delta[at:at+1]
        at += 1
        if kind == b'C':
            start, size = struct.unpack_from('>QQ', delta, at)
            at += 16
            if start + size > len(html):
                raise ValueError('Copy exceeds verified base')
            out.extend(html[start:start+size])
        elif kind == b'I':
            size, = struct.unpack_from('>Q', delta, at)
            at += 8
            if at + size > len(delta):
                raise ValueError('Truncated literal')
            out.extend(delta[at:at+size])
            at += size
        else:
            raise ValueError('Invalid delta operation')
        if len(out) > 222552795:
            raise ValueError('Unexpected output size')
    if len(out) != 222552795 or hashlib.sha256(out).hexdigest() != TARGET:
        raise ValueError('V1554 integrity check failed')
    return bytes(out)
