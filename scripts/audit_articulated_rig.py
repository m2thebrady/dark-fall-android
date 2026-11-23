#!/usr/bin/env python3
"""Check articulated character rigs for excessive joint rotation and equipment drift."""
import argparse,json,math
from pathlib import Path
from interpolate_pose_guides import interpolate
from compose_articulated_parts import validate_rig

def analyze(spec,rig,frames,max_angle=25,max_delta=15):
    if max_angle<=0 or max_delta<=0:raise ValueError("thresholds must be positive")
    issues=[]
    for part in rig["parts"]:
        a,b=part["root"],part["tip"]
        baseline=spec["landmarks"]
        ref=math.atan2(baseline[b][1]-baseline[a][1],baseline[b][0]-baseline[a][0])
        previous=None
        for frame in frames:
            positions=frame["landmarks"]
            angle=math.atan2(positions[b][1]-positions[a][1],positions[b][0]-positions[a][0])
            degrees=math.degrees(math.atan2(math.sin(angle-ref),math.cos(angle-ref)))
            if abs(degrees)>max_angle:issues.append({"type":"rotation_limit","part":part["name"],"frame":frame["frame"],"degrees":round(degrees,2)})
            if previous is not None:
                jump=abs(math.degrees(math.atan2(math.sin(angle-previous),math.cos(angle-previous))))
                if jump>max_delta:issues.append({"type":"angular_jump","part":part["name"],"frame":frame["frame"],"degrees":round(jump,2)})
            previous=angle
    return issues

def main():
    p=argparse.ArgumentParser()
    p.add_argument("profile",type=Path);p.add_argument("spec",type=Path);p.add_argument("rig",type=Path)
    p.add_argument("action");p.add_argument("frames",type=int)
    p.add_argument("--max-angle",type=float,default=25);p.add_argument("--max-delta",type=float,default=15)
    a=p.parse_args()
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text());rig=json.loads(a.rig.read_text())
    errors=validate_rig(spec,rig,a.rig.parent)
    if errors:raise ValueError("; ".join(errors))
    findings=analyze(spec,rig,interpolate(profile,spec,a.action,a.frames),a.max_angle,a.max_delta)
    print(json.dumps({"action":a.action,"count":len(findings),"findings":findings},indent=2))
if __name__=="__main__":main()
