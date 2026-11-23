#!/usr/bin/env python3
"""Verify revision selection, tamper detection and missing revision handling."""
import hashlib,json,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from select_assets import resolve_selection
from validate_asset import validate

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    src=root/"source"
    src.mkdir()
    Image.new("RGBA",(32,32),(0,0,0,0)).save(src/"hero.png")
    image=Image.open(src/"hero.png")
    draw=ImageDraw.Draw(image)
    draw.rectangle((8,8,23,23),fill=(255,100,30,255))
    image.save(src/"hero.png")
    manifest={"name":"hero","image":"hero.png","frame_width":32,"frame_height":32,"columns":1,"rows":1,"actions":{"idle":[0]},"safe_margin":2}
    (src/"hero.json").write_text(json.dumps(manifest))
    validate(src/"hero.json")
    digest=hashlib.sha256((src/"hero.json").read_bytes()+(src/"hero.png").read_bytes()).hexdigest()[:16]
    staged=root/"staged"/"hero"/digest
    staged.mkdir(parents=True)
    (staged/"hero.json").write_bytes((src/"hero.json").read_bytes())
    (staged/"hero.png").write_bytes((src/"hero.png").read_bytes())
    selection=root/"selection.json"
    selection.write_text(json.dumps({"assets":{"hero":digest}}))
    assert resolve_selection(selection,root/"staged")["hero"]["revision"]==digest
    selection.write_text(json.dumps({"assets":{"hero":"0"*16}}))
    try:
        resolve_selection(selection,root/"staged")
        raise AssertionError("Missing revision accepted")
    except ValueError:
        pass
    selection.write_text(json.dumps({"assets":{"hero":digest}}))
    (staged/"hero.json").write_text(json.dumps({**manifest,"safe_margin":3}))
    try:
        resolve_selection(selection,root/"staged")
        raise AssertionError("Modified revision accepted")
    except ValueError:
        pass
print("Asset selection and integrity tests passed")
