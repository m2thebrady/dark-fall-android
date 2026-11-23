#!/usr/bin/env python3
"""Test limb-length and motion-continuity diagnostics with deliberately broken poses."""
import copy,json
from pathlib import Path
from interpolate_pose_guides import interpolate
from audit_pose_motion import audit
profile=json.loads(Path("assets/profiles/warden.json").read_text())
spec=json.loads(Path("assets/pose-specs/warden-guide.json").read_text())
frames=interpolate(profile,spec,"run",32)
assert isinstance(audit(spec,frames),list)
bad=copy.deepcopy(frames)
bad[7]["landmarks"]["foot_l"][0]+=80
findings=audit(spec,bad)
assert any(f["type"]=="frame_jump" and f["landmark"]=="foot_l" for f in findings)
assert any(f["type"]=="segment_length" and "foot_l" in f["segment"] for f in findings)
try:audit(spec,frames,-1)
except ValueError:pass
else:raise AssertionError("accepted invalid tolerance")
print("Motion audit tests passed")
