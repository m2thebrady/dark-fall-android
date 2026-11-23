#!/usr/bin/env python3
"""Create an immutable production checklist for each character action."""
import argparse,json
from pathlib import Path
STAGES=("master_reference","anatomical_landmarks","key_poses","interpolation","artwork_refinement","palette_and_clipping","motion_audit","transition_preview","runtime_smoke","approval")
def make(profile,spec):
    return {"character":spec["character"],"body_family":profile["family"],"production_status":"planning","note":"Approval statuses must be confirmed by human visual review; generated checks do not imply approved artwork.","actions":{name:{"stage":{stage:"pending" for stage in STAGES},"target_frames":None,"approved_revision":None} for name in profile["actions"]}}
def main():
    p=argparse.ArgumentParser();p.add_argument("profile",type=Path);p.add_argument("spec",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Refusing to overwrite checklist")
    a.output.write_text(json.dumps(make(json.loads(a.profile.read_text()),json.loads(a.spec.read_text())),indent=2)+"\n")
    print(f"Wrote {a.output}")
if __name__=="__main__":main()
