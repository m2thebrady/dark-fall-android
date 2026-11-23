#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from build_transition_preview import build
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    profile=json.loads(Path("assets/profiles/wolf.json").read_text())
    actions={name:[i] for i,name in enumerate(profile["actions"])}
    w,h=profile["frame"]["width"],profile["frame"]["height"]
    image=Image.new("RGBA",(w*len(actions),h),(0,0,0,0))
    painter=ImageDraw.Draw(image)
    for i in range(len(actions)):painter.rectangle((i*w+30,30,i*w+110,100),fill=(142,151,154,255))
    image.save(root/"sheet.png")
    manifest={"name":"test-wolf","image":"sheet.png","frame_width":w,"frame_height":h,"columns":len(actions),"rows":1,"actions":actions}
    (root/"manifest.json").write_text(json.dumps(manifest))
    sequence=[{"action":"idle"},{"action":"run","cycles":2},{"action":"attack"},{"action":"death"}]
    (root/"sequence.json").write_text(json.dumps(sequence))
    output=root/"preview.html"
    result=build(Path("assets/profiles/wolf.json"),root/"manifest.json",root/"sequence.json",output)
    page=output.read_text()
    assert result["steps"]==4
    assert "data:image/png;base64," in page
    assert "test-wolf" in page
    assert "Restart" in page
    try:build(Path("assets/profiles/wolf.json"),root/"manifest.json",root/"sequence.json",output)
    except FileExistsError:pass
    else:raise AssertionError("preview overwritten")
print("Transition preview tests passed")
