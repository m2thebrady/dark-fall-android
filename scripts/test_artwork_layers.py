#!/usr/bin/env python3
import copy,json,tempfile
from pathlib import Path
from PIL import Image
from compose_artwork_layers import validate_layers,compose
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    Image.new("RGBA",(9,9),(200,90,30,255)).save(base/"head.png")
    Image.new("RGBA",(9,9),(20,140,90,255)).save(base/"club.png")
    layout={"character":"warden","layers":[{"name":"head","anchor":"head","image":"head.png","offset":[0,0]},{"name":"club","anchor":"club_tip","image":"club.png","offset":[0,0]}]}
    assert not validate_layers(spec,layout,base)
    out=base/"sheet.png"
    result=compose(profile,spec,layout,base,"run",9,out)
    assert result["frames"]==9
    sheet=Image.open(out)
    assert sheet.size==(profile["frame"]["width"]*9,profile["frame"]["height"])
    assert sheet.getbbox() is not None
    bad=copy.deepcopy(layout);bad["layers"][0]["image"]="../head.png"
    assert validate_layers(spec,bad,base)
    try:compose(profile,spec,layout,base,"run",9,out)
    except FileExistsError:pass
    else:raise AssertionError("overwrote sheet")
print("Layered artwork attachment tests passed")
