#!/usr/bin/env python3
"""Render pose landmark guides as a reviewable contact sheet; not finished sprite artwork."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
from validate_pose_spec import validate
def render(profile,spec,output,scale=2):
    errors=validate(spec,profile)
    if errors:raise ValueError("; ".join(errors))
    fw,fh=profile["frame"]["width"],profile["frame"]["height"]
    poses=[(action,pose) for action,frames in spec["poses"].items() for pose in frames]
    columns=min(4,len(poses));rows=math.ceil(len(poses)/columns)
    image=Image.new("RGB",(columns*fw*scale,rows*(fh*scale+24)),(29,34,37))
    draw=ImageDraw.Draw(image)
    for i,(action,pose) in enumerate(poses):
        ox=(i%columns)*fw*scale;oy=(i//columns)*(fh*scale+24)
        points={name:(ox+(xy[0]+pose.get("offsets",{}).get(name,[0,0])[0])*scale,oy+(xy[1]+pose.get("offsets",{}).get(name,[0,0])[1])*scale) for name,xy in spec["landmarks"].items()}
        for a,b in spec.get("links",[]):draw.line([points[a],points[b]],fill=(158,183,173),width=2)
        for name,pt in points.items():
            x,y=pt;draw.ellipse((x-3,y-3,x+3,y+3),fill=(238,191,107))
        draw.text((ox+5,oy+fh*scale+3),f"{action}  t={pose['t']:.2f}",fill=(235,237,227))
    if Path(output).exists():raise FileExistsError("Refusing to overwrite pose preview")
    image.save(output)
    return len(poses)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path);parser.add_argument("spec",type=Path);parser.add_argument("output",type=Path)
    a=parser.parse_args()
    print(f"Rendered {render(json.loads(a.profile.read_text()),json.loads(a.spec.read_text()),a.output)} pose guides")
if __name__=="__main__":main()
