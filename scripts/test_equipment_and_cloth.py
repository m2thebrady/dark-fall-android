#!/usr/bin/env python3
import copy,json,math
from pathlib import Path
from interpolate_pose_guides import interpolate
from guide_equipment_and_cloth import follow,attachment_drift
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
frames=interpolate(profile,spec,"run",32)
cloth=follow(frames,"hip",lag=0.4,max_offset=3)
assert len(cloth)==32
assert all(math.dist(item["position"],frames[i]["landmarks"]["hip"])<=3.001 for i,item in enumerate(cloth))
for lag in (-0.1,1.0):
    try:follow(frames,"hip",lag)
    except ValueError:pass
    else:raise AssertionError("accepted invalid lag")
ref=math.dist(spec["landmarks"]["hand_r"],spec["landmarks"]["club_tip"])
assert isinstance(attachment_drift(frames,"hand_r","club_tip",ref),list)
bad=copy.deepcopy(frames);bad[3]["landmarks"]["club_tip"][0]+=100
assert any(x["frame"]==3 for x in attachment_drift(bad,"hand_r","club_tip",ref))
print("Cloth follow and weapon attachment tests passed")
