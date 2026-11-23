#!/usr/bin/env python3
"""Schema checks for independent Dark Fall character body and animation profiles."""
import argparse,json
from pathlib import Path
FAMILIES={"humanoid","quadruped","avian","irregular"}
ACTIONS={"idle","run","walk","attack","run_attack","cast","run_cast","hit","death","fly","dive","heal","kneel"}
def validate(p):
    errors=[]
    if not isinstance(p,dict):return ["profile must be an object"]
    if not isinstance(p.get("id"),str) or not p["id"].strip():errors.append("id required")
    if p.get("family") not in FAMILIES:errors.append("family invalid")
    dimensions=p.get("frame",{})
    if not isinstance(dimensions,dict):return errors+["frame must be object"]
    for key in ("width","height"):
        v=dimensions.get(key)
        if not isinstance(v,int) or isinstance(v,bool) or v<=0:errors.append(f"frame.{key} must be positive integer")
    palette=p.get("palette",{})
    if not isinstance(palette,dict) or not palette:errors.append("palette must be nonempty object")
    else:
        for key,value in palette.items():
            if not isinstance(value,str) or len(value)!=7 or value[0]!="#" or any(c not in "0123456789abcdefABCDEF" for c in value[1:]):errors.append(f"palette.{key} invalid hex color")
    anchors=p.get("anchors",{})
    if not isinstance(anchors,dict):errors.append("anchors must be object")
    else:
        for key,value in anchors.items():
            if not isinstance(value,list) or len(value)!=2 or any(not isinstance(v,(int,float)) or isinstance(v,bool) for v in value):errors.append(f"anchor {key} invalid")
            elif all(isinstance(dimensions.get(k),int) for k in ("width","height")) and not (0<=value[0]<=dimensions["width"] and 0<=value[1]<=dimensions["height"]):errors.append(f"anchor {key} out of frame")
    actions=p.get("actions")
    if not isinstance(actions,dict) or not actions:errors.append("actions must be nonempty object")
    else:
        for name,settings in actions.items():
            if name not in ACTIONS:errors.append(f"action {name} unknown")
            if not isinstance(settings,dict):errors.append(f"action {name} must be object");continue
            fps=settings.get("fps")
            if not isinstance(fps,(int,float)) or isinstance(fps,bool) or not 1<=fps<=60:errors.append(f"action {name} fps invalid")
            if not isinstance(settings.get("loop"),bool):errors.append(f"action {name} loop invalid")
        if "idle" not in actions:errors.append("idle action required")
        if p.get("family")=="avian" and "fly" not in actions:errors.append("avian profile requires fly action")
        if p.get("family")=="quadruped" and not ("run" in actions or "walk" in actions):errors.append("quadruped profile requires locomotion")
    return errors
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profiles",nargs="+",type=Path)
    args=parser.parse_args()
    fail=False
    for path in args.profiles:
        try:errors=validate(json.loads(path.read_text()))
        except (ValueError,OSError) as e:errors=[str(e)]
        for e in errors:print(f"{path}: {e}")
        if errors:fail=True
        else:print(f"{path}: valid")
    raise SystemExit(int(fail))
if __name__=="__main__":main()
