#!/usr/bin/env python3
"""Experimental articulated sprite compositor using two-landmark bone orientation.

Each painted part is a rigid PNG rotated around a declared pivot. No deformation.
"""
import argparse,json,math
from pathlib import Path
from PIL import Image
from interpolate_pose_guides import interpolate

def validate_rig(spec,layout,base):
    errors=[]
    if layout.get("character")!=spec.get("character"):errors.append("character mismatch")
    parts=layout.get("parts")
    if not isinstance(parts,list) or not parts:return errors+["parts must be nonempty list"]
    names=set()
    for part in parts:
        if not isinstance(part,dict):errors.append("invalid part");continue
        name=part.get("name")
        if not isinstance(name,str) or not name or name in names:errors.append("duplicate or missing part name")
        names.add(name)
        for key in ("root","tip"):
            if part.get(key) not in spec["landmarks"]:errors.append(f"{name}: invalid {key}")
        filename=part.get("image")
        if not isinstance(filename,str) or Path(filename).is_absolute() or ".." in Path(filename).parts or Path(filename).suffix.lower()!=".png":errors.append(f"{name}: unsafe PNG path")
        elif not (base/filename).is_file():errors.append(f"{name}: missing PNG")
        pivot=part.get("pivot")
        if not isinstance(pivot,list) or len(pivot)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pivot):errors.append(f"{name}: invalid pivot")
        if part.get("root")==part.get("tip"):errors.append(f"{name}: root and tip must differ")
    return errors

def render(profile,spec,layout,base,action,count,output):
    errors=validate_rig(spec,layout,base)
    if errors:raise ValueError("; ".join(errors))
    if Path(output).exists():raise FileExistsError("Refusing to overwrite articulated output")
    frames=interpolate(profile,spec,action,count)
    w,h=profile["frame"]["width"],profile["frame"]["height"]
    sheet=Image.new("RGBA",(w*count,h),(0,0,0,0))
    parts=[(p,Image.open(base/p["image"]).convert("RGBA")) for p in layout["parts"]]
    for i,frame in enumerate(frames):
        canvas=Image.new("RGBA",(w,h),(0,0,0,0))
        for part,image in parts:
            root=frame["landmarks"][part["root"]];tip=frame["landmarks"][part["tip"]]
            refroot=spec["landmarks"][part["root"]];reftip=spec["landmarks"][part["tip"]]
            angle=math.atan2(tip[1]-root[1],tip[0]-root[0])-math.atan2(reftip[1]-refroot[1],reftip[0]-refroot[0])
            degrees=math.degrees(angle)
            pivot=part["pivot"]
            # Rotate the artwork around its authored pivot, preserving transparent padding.
            px,py=pivot
            margin=math.ceil(math.hypot(*image.size))+2
            size=margin*2+max(image.size)
            pad=Image.new("RGBA",(size,size))
            cx=cy=size//2
            pad.alpha_composite(image,(round(cx-px),round(cy-py)))
            rotated=pad.rotate(-degrees,resample=Image.Resampling.BICUBIC)
            canvas.alpha_composite(rotated,(round(root[0]-cx),round(root[1]-cy)))
        sheet.alpha_composite(canvas,(i*w,0))
    sheet.save(output)
    return {"frames":count,"parts":len(parts),"warning":"Rigid joint rotation only; manually review overlap, clipped pixels, anatomy and visual fidelity"}

def main():
    p=argparse.ArgumentParser()
    for name in ("profile","spec","rig","output"):p.add_argument(name,type=Path)
    p.add_argument("--action",default="run");p.add_argument("--frames",type=int,default=16)
    a=p.parse_args()
    print(json.dumps(render(json.loads(a.profile.read_text()),json.loads(a.spec.read_text()),json.loads(a.rig.read_text()),a.rig.parent,a.action,a.frames,a.output),indent=2))
if __name__=="__main__":main()
