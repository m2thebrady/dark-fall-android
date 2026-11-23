#!/usr/bin/env python3
"""Validate scalable, engine-agnostic animation asset catalog entries."""
import argparse,json,re
from pathlib import Path

ID=re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
FAMILIES={"humanoid","quadruped","flying","serpentine","irregular","prop","environment","vfx"}
KINDS={"character","enemy","boss","prop","environment","effect"}
def validate(catalog):
    issues=[]
    if catalog.get("schema_version")!=1:issues.append("unsupported schema_version")
    assets=catalog.get("assets")
    if not isinstance(assets,list):return issues+["assets must be list"]
    seen=set()
    for i,asset in enumerate(assets):
        label=f"assets[{i}]"
        if not isinstance(asset,dict):issues.append(f"{label}: invalid entry");continue
        identifier=asset.get("id")
        if not isinstance(identifier,str) or not ID.fullmatch(identifier):issues.append(f"{label}: invalid id")
        elif identifier in seen:issues.append(f"{label}: duplicate id")
        seen.add(identifier)
        if asset.get("family") not in FAMILIES:issues.append(f"{label}: invalid family")
        if asset.get("kind") not in KINDS:issues.append(f"{label}: invalid kind")
        frame=asset.get("frame")
        if not isinstance(frame,dict) or any(type(frame.get(k)) is not int or not 1<=frame[k]<=2048 for k in ("width","height")):issues.append(f"{label}: invalid frame")
        actions=asset.get("actions")
        if not isinstance(actions,dict) or not actions:issues.append(f"{label}: missing actions");continue
        for name,action in actions.items():
            if not isinstance(name,str) or not ID.fullmatch(name):issues.append(f"{label}: invalid action name")
            if not isinstance(action,dict):issues.append(f"{label}.{name}: invalid action");continue
            if type(action.get("fps")) is not int or not 1<=action["fps"]<=60:issues.append(f"{label}.{name}: invalid fps")
            if type(action.get("frames")) is not int or not 1<=action["frames"]<=600:issues.append(f"{label}.{name}: invalid frame count")
            if type(action.get("loop")) is not bool:issues.append(f"{label}.{name}: invalid loop")
        if asset.get("status") not in ("planned","in_production","review","approved","retired"):issues.append(f"{label}: invalid status")
        if asset.get("status")=="approved" and not asset.get("approved_revision"):issues.append(f"{label}: approved asset missing revision")
    return issues

def main():
    p=argparse.ArgumentParser();p.add_argument("catalog",type=Path);a=p.parse_args()
    issues=validate(json.loads(a.catalog.read_text()))
    print(json.dumps({"valid":not issues,"issues":issues},indent=2))
    if issues:raise SystemExit(1)
if __name__=="__main__":main()
