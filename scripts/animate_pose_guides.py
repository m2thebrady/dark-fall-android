#!/usr/bin/env python3
"""Export an animated GIF of interpolated landmark guides for motion review."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
from interpolate_pose_guides import interpolate,diagnose

def render(profile,spec,action,count,output,fps=12):
    if not 1<=fps<=60:raise ValueError("fps must be 1..60")
    frames=interpolate(profile,spec,action,count)
    w,h=profile["frame"]["width"],profile["frame"]["height"]
    scale=3
    images=[]
    for frame in frames:
        img=Image.new("RGB",(w*scale,h*scale),(29,34,37))
        d=ImageDraw.Draw(img)
        points={name:(int(x*scale),int(y*scale)) for name,(x,y) in frame["landmarks"].items()}
        for a,b in spec["links"]:d.line([points[a],points[b]],fill=(159,184,173),width=4)
        for name,(x,y) in points.items():d.ellipse((x-5,y-5,x+5,y+5),fill=(241,193,103))
        images.append(img)
    if Path(output).exists():raise FileExistsError("Refusing to overwrite animation preview")
    images[0].save(output,save_all=True,append_images=images[1:],duration=round(1000/fps),loop=0,optimize=False)
    return {"frames":len(frames),"warnings":diagnose(spec,frames)}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path);parser.add_argument("spec",type=Path);parser.add_argument("action")
    parser.add_argument("frames",type=int);parser.add_argument("output",type=Path);parser.add_argument("--fps",type=int,default=12)
    a=parser.parse_args()
    print(json.dumps(render(json.loads(a.profile.read_text()),json.loads(a.spec.read_text()),a.action,a.frames,a.output,a.fps),indent=2))
if __name__=="__main__":main()
