#!/usr/bin/env python3
import tempfile
from pathlib import Path
from PIL import Image
from audit_sprite_consistency import analyze
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/"frames.png"
    img=Image.new("RGBA",(96,32))
    for offset,side in ((0,12),(32,12),(64,2)):
        for x in range(offset+4,offset+4+side):
            for y in range(4,4+side):img.putpixel((x,y),(50,80,120,255))
    img.save(path)
    report=analyze(path,32,32)
    assert len(report["frames"])==3
    assert any(x["type"]=="silhouette_area_outlier" and x["frame"]==2 for x in report["findings"])
    report=analyze(path,32,32,max_palette_colors=0) if False else report
    try:analyze(path,32,32,max_palette_colors=0)
    except ValueError:pass
    else:raise AssertionError("accepted invalid color limit")
    try:analyze(path,31,32)
    except ValueError:pass
    else:raise AssertionError("accepted invalid dimensions")
print("Sprite consistency tests passed")
