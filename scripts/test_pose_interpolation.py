#!/usr/bin/env python3
import copy,json,tempfile
from pathlib import Path
from PIL import Image
from interpolate_pose_guides import interpolate,diagnose
from animate_pose_guides import render
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
frames=interpolate(profile,spec,"run",17)
assert len(frames)==17
assert frames[0]["landmarks"]["foot_l"]==frames[-1]["landmarks"]["foot_l"]
assert frames[8]["landmarks"]["foot_l"]!=frames[0]["landmarks"]["foot_l"]
assert diagnose(spec,frames)==[]
for n in (0,1,501,1.5):
    try:interpolate(profile,spec,"run",n)
    except ValueError:pass
    else:raise AssertionError(f"accepted invalid count {n}")
bad=copy.deepcopy(spec)
bad["limits"]["max_head_displacement"]=0
assert diagnose(bad,interpolate(profile,bad,"idle",5))
with tempfile.TemporaryDirectory() as temp:
    path=Path(temp)/"run.gif"
    result=render(profile,spec,"run",17,path,12)
    assert result["frames"]==17
    gif=Image.open(path)
    assert gif.n_frames==17
    try:render(profile,spec,"run",17,path)
    except FileExistsError:pass
    else:raise AssertionError("overwrote existing preview")
print("Interpolated pose animation tests passed")
