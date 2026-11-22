#!/usr/bin/env python3
"""Render a contact sheet of all animation frames with labels and safe margins."""
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--output")
    args = parser.parse_args()
    p = Path(args.manifest).resolve()
    m = json.loads(p.read_text(encoding="utf-8"))
    src = Image.open(p.parent / m["image"]).convert("RGBA")
    fw, fh, cols = int(m["frame_width"]), int(m["frame_height"]), int(m["columns"])
    margin = int(m.get("safe_margin", 2))
    entries = [(name, index) for name, frames in m["actions"].items() for index in frames]
    if not entries:
        raise ValueError("No frames to preview")
    label_h, gap = 30, 12
    cell_w, cell_h = fw + 2*gap, fh + label_h + 2*gap
    across = min(6, max(1, math.ceil(math.sqrt(len(entries)))))
    down = math.ceil(len(entries)/across)
    preview = Image.new("RGB", (across*cell_w, down*cell_h), (38, 39, 44))
    draw = ImageDraw.Draw(preview)
    for position, (action, index) in enumerate(entries):
        x = (position % across)*cell_w + gap
        y = (position // across)*cell_h + gap
        # Checkerboard reveals transparency rather than silently flattening it.
        for cy in range(0, fh, 16):
            for cx in range(0, fw, 16):
                shade = 92 if (cx//16+cy//16)%2 else 119
                draw.rectangle((x+cx,y+cy,x+min(fw,cx+16)-1,y+min(fh,cy+16)-1),fill=(shade,shade,shade))
        frame = src.crop(((index%cols)*fw,(index//cols)*fh,(index%cols+1)*fw,(index//cols+1)*fh))
        preview.paste(frame, (x,y), frame)
        if margin:
            draw.rectangle((x+margin,y+margin,x+fw-margin-1,y+fh-margin-1),outline=(245,181,65),width=1)
        draw.text((x,y+fh+5),f"{action}  #{index}",fill=(255,255,255))
    dest = Path(args.output).resolve() if args.output else p.with_name(p.stem+"-contact-sheet.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    preview.save(dest)
    print(f"Saved {dest} ({len(entries)} labeled frames)")

if __name__ == "__main__":
    main()
