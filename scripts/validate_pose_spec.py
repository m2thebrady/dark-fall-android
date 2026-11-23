#!/usr/bin/env python3
"""Validate character-specific key-pose and rig specifications; no game runtime changes."""
import argparse,json,math
from pathlib import Path
def validate(spec,profile):
    errors=[]
    if not isinstance(spec,dict):return ["pose specification must be an object"]
    if spec.get("character")!=profile.get("id"):errors.append("character does not match body profile")
    landmarks=spec.get("landmarks")
    if not isinstance(landmarks,dict) or not landmarks:return errors+["landmarks must be nonempty object"]
    width,height=profile["frame"]["width"],profile["frame"]["height"]
    for name,xy in landmarks.items():
        if not isinstance(xy,list) or len(xy)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in xy) or not (0<=xy[0]<width and 0<=xy[1]<height):errors.append(f"invalid landmark: {name}")
    links=spec.get("links",[])
    if not isinstance(links,list):errors.append("links must be list");links=[]
    for link in links:
        if not isinstance(link,list) or len(link)!=2 or any(x not in landmarks for x in link):errors.append(f"invalid link: {link}")
    limits=spec.get("limits",{})
    if not isinstance(limits,dict):errors.append("limits must be object");limits={}
    for name,value in limits.items():
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value<0:errors.append(f"invalid limit: {name}")
    poses=spec.get("poses",{})
    if not isinstance(poses,dict) or not poses:return errors+["poses must be nonempty object"]
    for action,frames in poses.items():
        if action not in profile["actions"]:errors.append(f"unknown action: {action}")
        if not isinstance(frames,list) or len(frames)<2:errors.append(f"{action}: at least two key poses required");continue
        prev=-1
        for pose in frames:
            if not isinstance(pose,dict):errors.append(f"{action}: invalid pose");continue
            t=pose.get("t")
            if not isinstance(t,(int,float)) or isinstance(t,bool) or not math.isfinite(t) or not 0<=t<=1 or t<=prev:errors.append(f"{action}: pose times must strictly increase in [0,1]")
            else:prev=t
            offsets=pose.get("offsets",{})
            if not isinstance(offsets,dict):errors.append(f"{action}: offsets must be object");continue
            for name,delta in offsets.items():
                if name not in landmarks or not isinstance(delta,list) or len(delta)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in delta):errors.append(f"{action}: invalid offset for {name}")
        if frames[0].get("t")!=0 or frames[-1].get("t")!=1:errors.append(f"{action}: must start at 0 and end at 1")
    return errors
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path)
    parser.add_argument("spec",type=Path)
    a=parser.parse_args()
    errors=validate(json.loads(a.spec.read_text()),json.loads(a.profile.read_text()))
    if errors:
        for e in errors:print(e)
        raise SystemExit(1)
    print("Pose specification valid")
if __name__=="__main__":main()
