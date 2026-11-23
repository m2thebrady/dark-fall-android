#!/usr/bin/env python3
"""Report color distribution and distance from a character's reference palette."""
import argparse,json
from collections import Counter
from pathlib import Path
from PIL import Image
def inspect(image_path,profile_path):
    p=json.loads(Path(profile_path).read_text())
    image=Image.open(image_path).convert("RGBA")
    colors=Counter(rgb for r,g,b,a in image.getdata() if a>=128 for rgb in [(r,g,b)])
    palette=[tuple(int(v[i:i+2],16) for i in (1,3,5)) for v in p["palette"].values()]
    if not palette:raise ValueError("No palette colors")
    def distance(rgb):
        return min(sum((x-y)**2 for x,y in zip(rgb,reference))**0.5 for reference in palette)
    total=sum(colors.values())
    outside=sum(n for rgb,n in colors.items() if distance(rgb)>80)
    return {"opaque_pixels":total,"unique_colors":len(colors),"outside_reference_tolerance":outside,"outside_fraction":round(outside/total,4) if total else 0,"most_common":[{"rgb":"#%02X%02X%02X"%rgb,"pixels":n} for rgb,n in colors.most_common(12)]}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("image",type=Path)
    parser.add_argument("profile",type=Path)
    parser.add_argument("--max-outside-fraction",type=float,default=None)
    a=parser.parse_args()
    result=inspect(a.image,a.profile)
    print(json.dumps(result,indent=2))
    if a.max_outside_fraction is not None and result["outside_fraction"]>a.max_outside_fraction:raise SystemExit(1)
if __name__=="__main__":main()
