#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image
from build_animation_candidate import build
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    Image.new("RGBA",(8,8),(180,130,70,255)).save(base/"head.png")
    rig={"character":"warden","parts":[{"name":"head","image":"head.png","root":"head","tip":"neck","pivot":[4,4]}]}
    output=base/"candidate.png"
    report=build(profile,spec,rig,base,"idle",9,output,strict=False)
    assert output.is_file()
    assert report["frames"]==9
    assert report["approved"] is False
    assert isinstance(report["blocking_count"],int)
    try:build(profile,spec,rig,base,"idle",9,output,strict=False)
    except FileExistsError:pass
    else:raise AssertionError("overwrote existing candidate")
    bad=base/"invalid.png"
    invalid={"character":"warden","parts":[{"name":"bad","image":"../head.png","root":"head","tip":"neck","pivot":[4,4]}]}
    try:build(profile,spec,invalid,base,"idle",9,bad)
    except ValueError:pass
    else:raise AssertionError("accepted unsafe artwork")
print("Unified candidate builder tests passed")
