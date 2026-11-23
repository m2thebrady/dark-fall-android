#!/usr/bin/env python3
"""Detect alpha pixels clipped by sprite frame bounds, and inconsistent per-frame occupancy."""
import argparse,json
from pathlib import Path
from PIL import Image

def inspect(path,width,height,edge=2):
    if width<=0 or height<=0 or edge<0 or edge*2>=min(width,height):raise ValueError("invalid frame dimensions or margin")
    image=Image.open(path).convert("RGBA")
    if image.height%height or image.width%width:raise ValueError("sheet dimensions not divisible by frame dimensions")
    findings=[]
    cols=image.width//width;rows=image.height//height
    for i in range(cols*rows):
        x=(i%cols)*width;y=(i//cols)*height
        frame=image.crop((x,y,x+width,y+height))
        alpha=frame.getchannel("A")
        bbox=alpha.getbbox()
        if bbox is None:findings.append({"frame":i,"type":"empty_frame"});continue
        if bbox[0]<edge or bbox[1]<edge or bbox[2]>width-edge or bbox[3]>height-edge:
            findings.append({"frame":i,"type":"unsafe_margin","bbox":bbox})
    return {"frames":cols*rows,"findings":findings}

def main():
    p=argparse.ArgumentParser();p.add_argument("image",type=Path);p.add_argument("width",type=int);p.add_argument("height",type=int);p.add_argument("--margin",type=int,default=2)
    a=p.parse_args();print(json.dumps(inspect(a.image,a.width,a.height,a.margin),indent=2))
if __name__=="__main__":main()
