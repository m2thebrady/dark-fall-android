#!/usr/bin/env python3
"""Validate handcrafted Dark Fall map JSON without touching the game renderer."""
import argparse
import json
from pathlib import Path

TYPES={"tree","rock","ruin","bush","water","landmark","spawn","exit","decoration"}
SOLID={"tree","rock","ruin","water"}
def rect(obj):
    return (obj["x"],obj["y"],obj["width"],obj["height"])
def overlap(a,b):
    return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]
def validate(data):
    errors=[]
    if not isinstance(data,dict):return ["Map must be an object"]
    size=data.get("size",{})
    if not isinstance(size,dict):return ["size must be an object"]
    w,h=size.get("width"),size.get("height")
    if any(not isinstance(v,int) or isinstance(v,bool) or v<=0 for v in (w,h)):
        return ["size.width and size.height must be positive integers"]
    objects=data.get("objects",[])
    if not isinstance(objects,list):return ["objects must be an array"]
    ids=set()
    for i,o in enumerate(objects):
        p=f"objects[{i}]"
        if not isinstance(o,dict):errors.append(f"{p} must be an object");continue
        ident=o.get("id")
        if not isinstance(ident,str) or not ident.strip():errors.append(f"{p}.id missing")
        elif ident in ids:errors.append(f"{p}.id duplicate: {ident}")
        else:ids.add(ident)
        if o.get("type") not in TYPES:errors.append(f"{p}.type invalid")
        vals=[o.get(k) for k in ("x","y","width","height")]
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) for v in vals):
            errors.append(f"{p} coordinates and dimensions must be numeric");continue
        x,y,ow,oh=vals
        if ow<=0 or oh<=0:errors.append(f"{p} dimensions must be positive")
        if x<0 or y<0 or x+ow>w or y+oh>h:errors.append(f"{p} outside map bounds")
        if o.get("solid",False) not in (True,False):errors.append(f"{p}.solid must be boolean")
        if o.get("type")=="spawn" and o.get("solid",False):errors.append(f"{p} spawn cannot be solid")
    valid=[o for o in objects if isinstance(o,dict) and all(isinstance(o.get(k),(int,float)) and not isinstance(o.get(k),bool) for k in ("x","y","width","height"))]
    spawns=[o for o in valid if o.get("type")=="spawn"]
    exits=[o for o in valid if o.get("type")=="exit"]
    if not spawns:errors.append("Map needs at least one spawn")
    if not exits:errors.append("Map needs at least one exit")
    for i,a in enumerate(valid):
        if a.get("type") not in ("spawn","exit"):continue
        for b in valid:
            if b is a or not b.get("solid",b.get("type") in SOLID):continue
            if overlap(rect(a),rect(b)):errors.append(f"{a.get('id')} overlaps solid {b.get('id')}")
    return errors

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("maps",nargs="+",type=Path)
    args=parser.parse_args()
    failed=False
    for path in args.maps:
        try:errors=validate(json.loads(path.read_text()))
        except (ValueError,OSError) as exc:errors=[str(exc)]
        for error in errors:print(f"{path}: {error}")
        if errors:failed=True
        else:print(f"{path}: valid")
    raise SystemExit(1 if failed else 0)
if __name__=="__main__":main()
