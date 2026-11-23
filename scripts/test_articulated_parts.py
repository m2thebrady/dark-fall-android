#!/usr/bin/env python3
import copy,json,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from compose_articulated_parts import validate_rig,render
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    image=Image.new("RGBA",(18,50));draw=ImageDraw.Draw(image);draw.rectangle((7,1,12,45),fill=(175,115,63,255))
    image.save(base/"leg.png")
    rig={"character":"warden","parts":[{"name":"left_leg","image":"leg.png","root":"hip","tip":"foot_l","pivot":[9,2]}]}
    assert not validate_rig(spec,rig,base)
    output=base/"articulated.png"
    result=render(profile,spec,rig,base,"run",9,output)
    assert result["frames"]==9
    sheet=Image.open(output)
    assert sheet.size==(profile["frame"]["width"]*9,profile["frame"]["height"])
    assert sheet.getbbox() is not None
    first=sheet.crop((0,0,profile["frame"]["width"],profile["frame"]["height"]))
    middle=sheet.crop((4*profile["frame"]["width"],0,5*profile["frame"]["width"],profile["frame"]["height"]))
    assert first.tobytes()!=middle.tobytes(),"articulation did not move"
    bad=copy.deepcopy(rig);bad["parts"][0]["pivot"]=[float("nan"),2]
    assert validate_rig(spec,bad,base)
    try:render(profile,spec,rig,base,"run",9,output)
    except FileExistsError:pass
    else:raise AssertionError("overwrote articulated output")
print("Articulated part tests passed")
