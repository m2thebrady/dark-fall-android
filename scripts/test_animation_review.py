#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image
from build_animation_review import make_review
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
with tempfile.TemporaryDirectory() as temp:
    base=Path(temp)
    Image.new("RGBA",(12,12),(110,90,70,255)).save(base/"part.png")
    rig={"character":"warden","parts":[{"name":"head","image":"part.png","root":"head","tip":"neck","pivot":[6,6]}]}
    destination=base/"review"
    result=make_review(profile,spec,rig,base,"idle",8,destination)
    assert result["review_status"]=="pending_human_review"
    assert (destination/"candidate.png").is_file()
    assert (destination/"contact-sheet.png").is_file()
    assert (destination/"diagnostics.json").is_file()
    assert (destination/"REVIEW.md").is_file()
    assert Image.open(destination/"contact-sheet.png").width>profile["frame"]["width"]
    try:make_review(profile,spec,rig,base,"idle",8,destination)
    except FileExistsError:pass
    else:raise AssertionError("overwrote review package")
print("Animation review package tests passed")
