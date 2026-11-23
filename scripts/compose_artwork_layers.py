#!/usr/bin/env python3
"""Attach independently painted transparent artwork layers to interpolated landmarks.

Rigid translations only: no limb deformation, rotation, or sprite synthesis.
"""
import argparse,json,math
from pathlib import Path
from PIL import Image
from interpolate_pose_guides import interpolate

def validate_layers(spec,layout,base):
    errors=[]
    if layout.get("character")!=spec.get("character"):errors.append("character mismatch")
    layers=layout.get("layers")
    if not isinstance(layers,list) or not layers:return errors+["layers must be nonempty list"]
    seen=set()
    for item in layers:
        if not isinstance(item,dict):errors.append("invalid layer");continue
        name=item.get("name");anchor=item.get("anchor");filename=item.get("image")
        if not isinstance(name,str) or not name or name in seen:errors.append("invalid or duplicate layer name")
        seen.add(name)
        if anchor not in spec["landmarks"]:errors.append(f"{name}: unknown anchor")
        if not isinstance(filename,str) or not filename.endswith(".png") or Path(filename).is_absolute() or ".." in Path(filename).parts:errors.append(f"{name}: unsafe PNG path")
        elif not (base/filename).is_file():errors.append(f"{name}: PNG missing")
        offset=item.get("offset",[0,0])
        if not isinstance(offset,list) or len(offset)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in offset):errors.append(f"{name}: invalid offset")
    return errors

def compose(profile,spec,layout,base,action,count,output):
    errors=validate_layers(spec,layout,base)
    if errors:raise ValueError("; ".join(errors))
    if Path(output).exists():raise FileExistsError("Refusing to overwrite sprite sheet")
    frames=interpolate(profile,spec,action,count)
    w,h=profile["frame"]["width"],profile["frame"]["height"]
    sheet=Image.new("RGBA",(w*count,h),(0,0,0,0))
    layers=[(entry,Image.open(base/entry["image"]).convert("RGBA")) for entry in layout["layers"]]
    for i,frame in enumerate(frames):
        canvas=Image.new("RGBA",(w,h),(0,0,0,0))
        for entry,image in layers:
            anchor=entry["anchor"]
            origin=spec["landmarks"][anchor];current=frame["landmarks"][anchor]
            offset=entry.get("offset",[0,0])
            x=round(origin[0]+offset[0]+current[0]-origin[0]);y=round(origin[1]+offset[1]+current[1]-origin[1])
            canvas.alpha_composite(image,(x,y))
        sheet.alpha_composite(canvas,(i*w,0))
    sheet.save(output)
    return {"frames":count,"width":w,"height":h,"layers":len(layers),"warning":"Rigid translations only; artistic refinement and alpha/clipping review required"}
def main():
    p=argparse.ArgumentParser()
    for name in ("profile","spec","layout","output"):p.add_argument(name,type=Path)
    p.add_argument("--action",default="run");p.add_argument("--frames",type=int,default=16)
    a=p.parse_args()
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text());layout=json.loads(a.layout.read_text())
    print(json.dumps(compose(profile,spec,layout,a.layout.parent,a.action,a.frames,a.output),indent=2))
if __name__=="__main__":main()
