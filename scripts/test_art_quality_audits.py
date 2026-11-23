#!/usr/bin/env python3
import copy,tempfile
from pathlib import Path
from PIL import Image
from audit_articulated_rig import analyze
from audit_sprite_margins import inspect
spec={"landmarks":{"hip":[0,0],"foot":[0,10]}}
rig={"parts":[{"name":"leg","root":"hip","tip":"foot"}]}
frames=[{"frame":0,"landmarks":{"hip":[0,0],"foot":[0,10]}},{"frame":1,"landmarks":{"hip":[0,0],"foot":[10,0]}}]
assert any(f["type"]=="rotation_limit" for f in analyze(spec,rig,frames))
assert any(f["type"]=="angular_jump" for f in analyze(spec,rig,frames))
assert not analyze(spec,rig,frames,180,180)
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/"frames.png"
    image=Image.new("RGBA",(64,32),(0,0,0,0))
    for x in range(7,25):
        for y in range(7,25):image.putpixel((x,y),(255,255,255,255))
    image.putpixel((32,16),(255,255,255,255))
    image.save(path)
    result=inspect(path,32,32)
    assert result["frames"]==2
    assert any(f["frame"]==1 and f["type"]=="unsafe_margin" for f in result["findings"])
    assert not any(f["frame"]==0 for f in result["findings"])
print("Articulated rig and sprite margin audit tests passed")
