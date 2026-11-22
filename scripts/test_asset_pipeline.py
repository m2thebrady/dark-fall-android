#!/usr/bin/env python3
"""Generate a tiny synthetic asset and exercise validation/preview in CI."""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    folder=Path(tmp)
    sheet=Image.new("RGBA",(64,32),(0,0,0,0))
    draw=ImageDraw.Draw(sheet)
    for x in (0,32):
        draw.rectangle((x+9,8,x+22,26),fill=(180,100,90,255))
    sheet.save(folder/"test.png")
    manifest={"name":"test","image":"test.png","frame_width":32,"frame_height":32,"columns":2,"rows":1,"safe_margin":3,"actions":{"idle":[0,1]},"anchors":{"0":{"feet":[16,27]},"1":{"feet":[16,27]}}}
    path=folder/"test.json"
    path.write_text(json.dumps(manifest))
    subprocess.run([sys.executable,str(root/"scripts/validate_asset.py"),str(path)],check=True)
    subprocess.run([sys.executable,str(root/"scripts/preview_asset.py"),str(path)],check=True)
    assert (folder/"test-contact-sheet.png").stat().st_size>100
    manifest["transitions"]=[["idle","missing"]]
    path.write_text(json.dumps(manifest))
    bad_transition=subprocess.run([sys.executable,str(root/"scripts/validate_asset.py"),str(path)],capture_output=True)
    assert bad_transition.returncode!=0,"Expected unknown transition to be rejected"
    manifest.pop("transitions")
    manifest["anchors"]["1"]["feet"]=[31,27]
    path.write_text(json.dumps(manifest))
    bad=subprocess.run([sys.executable,str(root/"scripts/validate_asset.py"),str(path)],capture_output=True)
    assert bad.returncode!=0,"Expected drifting anchor to be rejected"
print("Asset pipeline synthetic self-test passed")
