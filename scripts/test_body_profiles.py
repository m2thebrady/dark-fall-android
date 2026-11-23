#!/usr/bin/env python3
import copy,json
from pathlib import Path
from validate_body_profile import validate
paths=list(Path("assets/profiles").glob("*.json"))
assert len(paths)>=3
profiles=[json.loads(p.read_text()) for p in paths]
assert {p["family"] for p in profiles}>={"humanoid","quadruped","avian"}
assert len({p["id"] for p in profiles})==len(profiles)
for p in profiles:assert not validate(p),(p["id"],validate(p))
p=copy.deepcopy(profiles[0]);p["palette"]["armor"]="#badhex"
assert any("invalid hex" in x for x in validate(p))
p=copy.deepcopy(profiles[0]);p["anchors"]["feet"]=[99999,0]
assert any("out of frame" in x for x in validate(p))
p=copy.deepcopy(profiles[0]);p["actions"]["idle"]["fps"]=0
assert any("fps invalid" in x for x in validate(p))
avian=next(p for p in profiles if p["family"]=="avian")
avian=copy.deepcopy(avian);del avian["actions"]["fly"]
assert any("requires fly" in e for e in validate(avian))
quadruped=next(p for p in profiles if p["family"]=="quadruped")
quadruped=copy.deepcopy(quadruped)
quadruped["actions"].pop("run",None);quadruped["actions"].pop("walk",None)
assert any("requires locomotion" in e for e in validate(quadruped))
print("Body profile tests passed")
