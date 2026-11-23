#!/usr/bin/env python3
"""Interpolate landmark guides with optional motion limits; never generates finished sprites."""
import argparse,json,math
from pathlib import Path
from validate_pose_spec import validate

def interpolate(profile,spec,action,frame_count):
    errors=validate(spec,profile)
    if errors:raise ValueError("; ".join(errors))
    if action not in spec["poses"]:raise ValueError("action has no approved key poses")
    if type(frame_count) is not int or not 2<=frame_count<=500:raise ValueError("frame count must be 2..500")
    poses=spec["poses"][action]
    frames=[]
    for i in range(frame_count):
        t=i/(frame_count-1)
        right=next((j for j in range(1,len(poses)) if poses[j]["t"]>=t),len(poses)-1)
        left=right-1
        a,b=poses[left],poses[right]
        alpha=(t-a["t"])/(b["t"]-a["t"])
        positions={}
        for name,origin in spec["landmarks"].items():
            da=a.get("offsets",{}).get(name,[0,0]);db=b.get("offsets",{}).get(name,[0,0])
            positions[name]=[round(origin[k]+da[k]*(1-alpha)+db[k]*alpha,3) for k in (0,1)]
        frames.append({"frame":i,"t":round(t,5),"landmarks":positions})
    return frames

def diagnose(spec,frames):
    warnings=[]
    base=spec["landmarks"]
    for frame in frames:
        for name,limit in spec.get("limits",{}).items():
            if not name.startswith("max_") or not name.endswith("_displacement"):continue
            landmark=name[4:-13]
            if landmark not in base:continue
            xy=frame["landmarks"][landmark];origin=base[landmark]
            distance=math.dist(xy,origin)
            if distance>limit:warnings.append({"frame":frame["frame"],"landmark":landmark,"distance":round(distance,3),"limit":limit})
    return warnings

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path);parser.add_argument("spec",type=Path)
    parser.add_argument("action");parser.add_argument("frames",type=int);parser.add_argument("output",type=Path)
    args=parser.parse_args()
    profile=json.loads(args.profile.read_text());spec=json.loads(args.spec.read_text())
    frames=interpolate(profile,spec,args.action,args.frames)
    result={"character":spec["character"],"action":args.action,"frames":frames,"warnings":diagnose(spec,frames),"note":"Landmark guide data only; not sprite artwork"}
    if args.output.exists():raise FileExistsError("Refusing to overwrite interpolated guide")
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(f"Generated {len(frames)} guide frames; {len(result['warnings'])} motion warnings")
if __name__=="__main__":main()
