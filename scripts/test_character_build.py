#!/usr/bin/env python3
"""End-to-end synthetic character pipeline regression."""
import json,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from build_character_asset import run
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    profile=json.loads(Path("assets/profiles/warden.json").read_text())
    actions={name:[i] for i,name in enumerate(profile["actions"])}
    width,height=profile["frame"]["width"],profile["frame"]["height"]
    sheet=Image.new("RGBA",(width*len(actions),height),(0,0,0,0))
    for i in range(len(actions)):
        ImageDraw.Draw(sheet).rectangle((i*width+60,40,i*width+100,150),fill=(85,69,55,255))
    sheet.save(root/"sheet.png")
    manifest={"name":"synthetic-warden","image":"sheet.png","frame_width":width,"frame_height":height,"columns":len(actions),"rows":1,"actions":actions}
    (root/"sheet.json").write_text(json.dumps(manifest))
    report=run(Path("assets/profiles/warden.json"),root/"sheet.json",root/"sheet.png",root/"report")
    assert report["sprite_validation"]=="passed"
    assert report["coverage_validation"]=="passed"
    assert report["palette"]["opaque_pixels"]>0
    assert (root/"report"/"report.json").exists()
    try:run(Path("assets/profiles/warden.json"),root/"sheet.json",root/"sheet.png",root/"report")
    except FileExistsError:pass
    else:raise AssertionError("overwrote existing report")
print("Character production pipeline tests passed")
