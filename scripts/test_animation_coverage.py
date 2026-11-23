#!/usr/bin/env python3
import copy,json
from pathlib import Path
from check_animation_coverage import check
p=json.loads(Path("assets/profiles/warden.json").read_text())
manifest={"frame_width":p["frame"]["width"],"frame_height":p["frame"]["height"],"actions":{k:[0] for k in p["actions"]}}
assert not check(p,manifest)
m=copy.deepcopy(manifest);del m["actions"]["run"]
assert "missing action: run" in check(p,m)
m=copy.deepcopy(manifest);m["actions"]["attack"]=[]
assert "empty action: attack" in check(p,m)
m=copy.deepcopy(manifest);m["frame_width"]+=1
assert "frame width mismatch" in check(p,m)
m=copy.deepcopy(manifest);m["actions"]["unknown"]=[0]
assert "unexpected action: unknown" in check(p,m)
print("Animation coverage tests passed")
