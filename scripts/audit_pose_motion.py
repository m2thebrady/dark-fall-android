#!/usr/bin/env python3
"""Measure segment rigidity and frame-to-frame landmark continuity in pose guides."""
import argparse,json,math
from pathlib import Path
from interpolate_pose_guides import interpolate

def audit(spec,frames,rigidity_tolerance=0.12,max_step=12):
    if not 0<=rigidity_tolerance<=1 or max_step<=0:raise ValueError("invalid audit tolerances")
    baseline={tuple(link):math.dist(spec["landmarks"][link[0]],spec["landmarks"][link[1]]) for link in spec["links"]}
    findings=[]
    for frame in frames:
        positions=frame["landmarks"]
        for (a,b),length in baseline.items():
            if length==0:continue
            actual=math.dist(positions[a],positions[b])
            ratio=abs(actual-length)/length
            if ratio>rigidity_tolerance:findings.append({"type":"segment_length","frame":frame["frame"],"segment":[a,b],"drift":round(ratio,4)})
    for before,after in zip(frames,frames[1:]):
        for name in spec["landmarks"]:
            distance=math.dist(before["landmarks"][name],after["landmarks"][name])
            if distance>max_step:findings.append({"type":"frame_jump","frame":after["frame"],"landmark":name,"pixels":round(distance,3)})
    return findings

def main():
    p=argparse.ArgumentParser()
    p.add_argument("profile",type=Path);p.add_argument("spec",type=Path);p.add_argument("action");p.add_argument("frames",type=int)
    p.add_argument("--rigidity-tolerance",type=float,default=0.12);p.add_argument("--max-step",type=float,default=12)
    a=p.parse_args()
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text())
    result=audit(spec,interpolate(profile,spec,a.action,a.frames),a.rigidity_tolerance,a.max_step)
    print(json.dumps({"action":a.action,"findings":result,"count":len(result)},indent=2))
if __name__=="__main__":main()
