#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from inspect_animation import inspect
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    img=Image.new("RGBA",(96,32),(0,0,0,0))
    d=ImageDraw.Draw(img)
    d.rectangle((8,8,23,23),fill="white")
    d.rectangle((32+8,8,32+23,23),fill="white")
    d.rectangle((64+14,14,64+17,17),fill="white")
    img.save(root/"test.png")
    manifest={"image":"test.png","frame_width":32,"frame_height":32,"columns":3,"rows":1,"actions":{"run":[0,1,2]}}
    (root/"test.json").write_text(json.dumps(manifest))
    result=inspect(root/"test.json")
    assert len(result["actions"]["run"])==3
    assert any("silhouette height" in w for w in result["warnings"])
    assert any("silhouette width" in w for w in result["warnings"])
    manifest["actions"]["run"]=[0,1]
    (root/"test.json").write_text(json.dumps(manifest))
    assert not inspect(root/"test.json")["warnings"]
print("Animation silhouette diagnostics passed")
