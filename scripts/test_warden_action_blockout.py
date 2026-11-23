#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from PIL import Image
from build_warden_action_blockout import produce,BUDGET
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
with tempfile.TemporaryDirectory() as temp:
    output=Path(temp)/"blockout"
    summary=produce(profile,spec,output)
    assert set(summary["actions"])==set(profile["actions"])
    assert summary["total_frames"]==sum(BUDGET.values())
    assert summary["approved"] is False
    for action,count in BUDGET.items():
        data=json.loads((output/f"{action}.json").read_text())
        assert len(data["frames"])==count
        assert Image.open(output/f"{action}-contact.png").size==(profile["frame"]["width"]*4,profile["frame"]["height"]*2)
    try:produce(profile,spec,output)
    except FileExistsError:pass
    else:raise AssertionError("overwrote blockout")
print("Full Warden action blockout tests passed")
