#!/usr/bin/env python3
"""Report per-frame sprite silhouette bounds and suspicious scale changes."""
import argparse,json
from pathlib import Path
from PIL import Image

def inspect(manifest_path, ratio_limit=1.5):
    path=Path(manifest_path)
    m=json.loads(path.read_text(encoding="utf-8"))
    image=Image.open(path.parent/m["image"]).convert("RGBA")
    w,h=m["frame_width"],m["frame_height"]
    cols=m["columns"]
    report={"actions":{},"warnings":[]}
    for action,frames in m["actions"].items():
        entries=[]
        for index in frames:
            x=(index%cols)*w
            y=(index//cols)*h
            crop=image.crop((x,y,x+w,y+h))
            bounds=crop.getchannel("A").getbbox()
            entry={"frame":index,"bounds":bounds,"width":bounds[2]-bounds[0] if bounds else 0,"height":bounds[3]-bounds[1] if bounds else 0}
            entries.append(entry)
            if bounds is None:
                report["warnings"].append(f"{action} frame {index}: fully transparent")
        heights=[e["height"] for e in entries if e["height"]]
        if heights and max(heights)/min(heights)>ratio_limit:
            report["warnings"].append(f"{action}: silhouette height varies by {max(heights)/min(heights):.2f}x")
        widths=[e["width"] for e in entries if e["width"]]
        if widths and max(widths)/min(widths)>ratio_limit:
            report["warnings"].append(f"{action}: silhouette width varies by {max(widths)/min(widths):.2f}x")
        report["actions"][action]=entries
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("manifest")
    p.add_argument("--ratio-limit",type=float,default=1.5)
    p.add_argument("--output")
    p.add_argument("--fail-on-warning",action="store_true")
    args=p.parse_args()
    if args.ratio_limit<=1:
        p.error("--ratio-limit must exceed 1")
    result=inspect(args.manifest,args.ratio_limit)
    output=json.dumps(result,indent=2)
    if args.output:
        Path(args.output).write_text(output+"\n",encoding="utf-8")
    print(output)
    if args.fail_on_warning and result["warnings"]:
        raise SystemExit(1)
