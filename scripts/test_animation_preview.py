#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from preview_animation import export
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    image=Image.new("RGBA",(64,32),(0,0,0,0))
    draw=ImageDraw.Draw(image)
    draw.rectangle((8,8,22,22),fill="red")
    draw.rectangle((32+8,8,32+22,22),fill="blue")
    image.save(root/"sprite.png")
    manifest={"image":"sprite.png","frame_width":32,"frame_height":32,"columns":2,"rows":1,"actions":{"run":[0,1]}}
    path=root/"sprite.json"
    path.write_text(json.dumps(manifest))
    results=export(path,root/"previews",fps=8)
    assert len(results)==1
    with Image.open(results[0]) as gif:
        assert gif.format=="GIF"
        assert gif.n_frames==2
    try:
        export(path,root/"previews")
        raise AssertionError("Preview overwrite accepted")
    except ValueError:
        pass
print("Animated preview tests passed")
