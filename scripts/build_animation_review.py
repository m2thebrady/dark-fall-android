#!/usr/bin/env python3
"""Export an offline animation review package with sheet, contact sheet and report."""
import argparse,json,shutil,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from build_animation_candidate import build

def make_review(profile,spec,rig,base,action,count,destination,reference_lock=None,reference_base=None):
    if destination.exists():raise FileExistsError("Review destination already exists")
    with tempfile.TemporaryDirectory() as temp:
        staging=Path(temp)/"review"
        staging.mkdir()
        candidate=staging/"candidate.png"
        report=build(profile,spec,rig,base,action,count,candidate,strict=False,reference_lock=reference_lock,reference_base=reference_base)
        w,h=profile["frame"]["width"],profile["frame"]["height"]
        source=Image.open(candidate).convert("RGBA")
        cols=min(5,count);rows=(count+cols-1)//cols
        padding=16;label_height=22
        sheet=Image.new("RGB",(cols*(w+padding)+padding,rows*(h+label_height+padding)+padding),(34,38,41))
        draw=ImageDraw.Draw(sheet)
        for i in range(count):
            x=padding+(i%cols)*(w+padding);y=padding+(i//cols)*(h+label_height+padding)
            tile=source.crop((i*w,0,(i+1)*w,h))
            sheet.paste(tile,(x,y),tile)
            draw.text((x,y+h+3),f"Frame {i:03d}",fill=(230,230,225))
        sheet.save(staging/"contact-sheet.png")
        report["review_status"]="pending_human_review"
        report["reference_lock_supplied"]=reference_lock is not None
        (staging/"diagnostics.json").write_text(json.dumps(report,indent=2)+"\n")
        (staging/"REVIEW.md").write_text(
            f"# {spec['character']} — {action} animation review\n\n"
            f"Frames: {count}. Diagnostic findings: {report['blocking_count']}.\n\n"
            "Review all frames for consistent identity, anatomy, armor, cloak, weapon grip, clipping, palette, and motion. "
            "Record approval separately. Automated checks cannot approve artwork.\n")
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(staging,destination)
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("profile","spec","rig","destination"):p.add_argument(name,type=Path)
    p.add_argument("--action",default="idle");p.add_argument("--frames",type=int,default=16)
    p.add_argument("--reference-lock",type=Path)
    a=p.parse_args()
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text());rig=json.loads(a.rig.read_text())
    lock=json.loads(a.reference_lock.read_text()) if a.reference_lock else None
    result=make_review(profile,spec,rig,a.rig.parent,a.action,a.frames,a.destination,lock,a.reference_lock.parent if a.reference_lock else None)
    print(json.dumps({"destination":str(a.destination),"findings":result["blocking_count"],"review_status":result["review_status"]},indent=2))
if __name__=="__main__":main()
