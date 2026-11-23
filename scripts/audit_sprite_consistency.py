#!/usr/bin/env python3
"""Compare alpha silhouettes and palette drift between candidate animation frames."""
import argparse,json,math
from pathlib import Path
from PIL import Image

def analyze(path,width,height,max_occupancy_ratio=2.5,max_palette_colors=128):
    if width<=0 or height<=0 or max_occupancy_ratio<1 or max_palette_colors<1:raise ValueError("invalid thresholds")
    img=Image.open(path).convert("RGBA")
    if img.width%width or img.height%height:raise ValueError("sheet not divisible into frames")
    frames=[]
    for y in range(0,img.height,height):
        for x in range(0,img.width,width):
            pixels=img.crop((x,y,x+width,y+height))
            rgba=list(pixels.getdata())
            opaque=[p for p in rgba if p[3]>0]
            colors={p[:3] for p in opaque}
            frames.append({"frame":len(frames),"occupied_pixels":len(opaque),"palette_colors":len(colors)})
    nonempty=[f["occupied_pixels"] for f in frames if f["occupied_pixels"]]
    reference=sorted(nonempty)[len(nonempty)//2] if nonempty else 0
    issues=[]
    for f in frames:
        n=f["occupied_pixels"]
        if not n:issues.append({"frame":f["frame"],"type":"empty_silhouette"})
        elif reference and max(n/reference,reference/n)>max_occupancy_ratio:
            issues.append({"frame":f["frame"],"type":"silhouette_area_outlier","pixels":n,"median":reference})
        if f["palette_colors"]>max_palette_colors:
            issues.append({"frame":f["frame"],"type":"palette_color_count","colors":f["palette_colors"]})
    return {"frames":frames,"findings":issues,"note":"Diagnostics only: shape similarity and palette fidelity require visual review"}

def main():
    p=argparse.ArgumentParser();p.add_argument("image",type=Path);p.add_argument("width",type=int);p.add_argument("height",type=int)
    p.add_argument("--max-area-ratio",type=float,default=2.5);p.add_argument("--max-colors",type=int,default=128)
    a=p.parse_args()
    print(json.dumps(analyze(a.image,a.width,a.height,a.max_area_ratio,a.max_colors),indent=2))
if __name__=="__main__":main()
