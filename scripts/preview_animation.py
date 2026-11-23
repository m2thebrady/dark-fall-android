#!/usr/bin/env python3
"""Export per-action GIF previews for review, without changing game sprites."""
import argparse,json
from pathlib import Path
from PIL import Image
def export(manifest_path,output,fps=10):
    path=Path(manifest_path)
    m=json.loads(path.read_text(encoding="utf-8"))
    sheet=Image.open(path.parent/m["image"]).convert("RGBA")
    w,h=m["frame_width"],m["frame_height"]
    cols=m["columns"]
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    created=[]
    for name,indices in m["actions"].items():
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in name):
            raise ValueError("Unsafe animation action name")
        frames=[]
        for idx in indices:
            x=(idx%cols)*w
            y=(idx//cols)*h
            frame=sheet.crop((x,y,x+w,y+h))
            backdrop=Image.new("RGBA",(w,h),(48,48,48,255))
            backdrop.alpha_composite(frame)
            frames.append(backdrop.convert("RGB"))
        if not frames:
            raise ValueError("Empty action")
        dest=output/(name+".gif")
        if dest.exists():
            raise ValueError("Refusing to overwrite existing preview")
        frames[0].save(dest,save_all=True,append_images=frames[1:],duration=round(1000/fps),loop=0,optimize=False)
        created.append(str(dest))
    return created
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("manifest")
    p.add_argument("--output",required=True)
    p.add_argument("--fps",type=int,default=10)
    args=p.parse_args()
    if not 1<=args.fps<=30:
        p.error("--fps must be 1-30")
    print("\n".join(export(args.manifest,args.output,args.fps)))
