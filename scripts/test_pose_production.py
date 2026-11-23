#!/usr/bin/env python3
import copy,json,tempfile
from pathlib import Path
from PIL import Image
from validate_pose_spec import validate
from preview_pose_spec import render
p=json.loads(Path("assets/profiles/warden.json").read_text())
s=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
assert not validate(s,p),validate(s,p)
with tempfile.TemporaryDirectory() as tmp:
    out=Path(tmp)/"poses.png"
    assert render(p,s,out)>3
    assert Image.open(out).size[0]>0
    try:render(p,s,out)
    except FileExistsError:pass
    else:raise AssertionError("overwrote preview")
bad=copy.deepcopy(s);bad["poses"]["run"][1]["offsets"]["foot_l"]=[float("nan"),0]
assert any("invalid offset" in x for x in validate(bad,p))
bad=copy.deepcopy(s);bad["poses"]["run"][1]["t"]=0
assert any("strictly increase" in x for x in validate(bad,p))
print("Pose production tests passed")
