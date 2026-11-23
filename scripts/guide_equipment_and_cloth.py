#!/usr/bin/env python3
"""Prototype restrained cloth-tail follow-through and weapon attachment diagnostics.

Generates procedural guide landmarks only; does not deform finished artwork.
"""
import argparse,json,math
from pathlib import Path
from interpolate_pose_guides import interpolate

def follow(frames,anchor,lag=0.35,max_offset=6):
    if not 0<=lag<1 or max_offset<0:raise ValueError("invalid follow-through settings")
    if not frames or anchor not in frames[0]["landmarks"]:raise ValueError("unknown anchor")
    previous=None
    result=[]
    for frame in frames:
        target=frame["landmarks"][anchor]
        if previous is None:position=list(target)
        else:
            position=[previous[k]+(target[k]-previous[k])*(1-lag) for k in (0,1)]
            distance=math.dist(position,target)
            if distance>max_offset and distance:
                position=[target[k]+(position[k]-target[k])*max_offset/distance for k in (0,1)]
        previous=position
        result.append({"frame":frame["frame"],"position":[round(v,3) for v in position],"anchor":anchor})
    return result

def attachment_drift(frames,hand,weapon,reference_distance,tolerance=3):
    if tolerance<0:raise ValueError("negative tolerance")
    findings=[]
    for frame in frames:
        positions=frame["landmarks"]
        distance=math.dist(positions[hand],positions[weapon])
        if abs(distance-reference_distance)>tolerance:
            findings.append({"frame":frame["frame"],"distance":round(distance,3),"expected":reference_distance})
    return findings

def main():
    p=argparse.ArgumentParser()
    p.add_argument("profile",type=Path);p.add_argument("spec",type=Path);p.add_argument("action")
    p.add_argument("frames",type=int);p.add_argument("anchor");p.add_argument("--lag",type=float,default=0.35)
    p.add_argument("--max-offset",type=float,default=6)
    a=p.parse_args()
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text())
    frames=interpolate(profile,spec,a.action,a.frames)
    print(json.dumps({"follow_through":follow(frames,a.anchor,a.lag,a.max_offset)},indent=2))
if __name__=="__main__":main()
