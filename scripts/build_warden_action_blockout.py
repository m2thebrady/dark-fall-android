#!/usr/bin/env python3
"""Produce a complete seven-action Warden landmark motion proof, without claiming sprite artwork."""
import argparse,json,shutil,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from interpolate_pose_guides import interpolate,diagnose
from audit_pose_motion import audit
from guide_equipment_and_cloth import attachment_drift
from validate_pose_spec import validate
import math

BUDGET={"idle":16,"run":32,"attack":32,"cast":24,"run_cast":32,"hit":16,"death":24}

def produce(profile,spec,destination):
    if destination.exists():raise FileExistsError("Output directory already exists")
    errors=validate(spec,profile)
    if errors:raise ValueError("; ".join(errors))
    missing=set(profile["actions"])-set(spec["poses"])
    if missing:raise ValueError("Missing actions: "+", ".join(sorted(missing)))
    if set(BUDGET)!=set(profile["actions"]):raise ValueError("Production budget and profile actions differ")
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp)/"proof";out.mkdir()
        summary={"character":spec["character"],"type":"anatomical_motion_blockout","approved":False,"actions":{}}
        w,h=profile["frame"]["width"],profile["frame"]["height"]
        for action,count in BUDGET.items():
            frames=interpolate(profile,spec,action,count)
            issues=diagnose(spec,frames)+audit(spec,frames)
            ref=math.dist(spec["landmarks"]["hand_r"],spec["landmarks"]["club_tip"])
            issues+=attachment_drift(frames,"hand_r","club_tip",ref)
            (out/f"{action}.json").write_text(json.dumps({"action":action,"frames":frames,"diagnostics":issues},indent=2)+"\n")
            # Sparse frame contact sheet is a guide for art direction, not finished art.
            indices=sorted(set(round(i*(count-1)/7) for i in range(8)))
            board=Image.new("RGB",(w*4,h*2),(31,34,37))
            d=ImageDraw.Draw(board)
            for j,index in enumerate(indices):
                ox=(j%4)*w;oy=(j//4)*h
                points={name:(round(x)+ox,round(y)+oy) for name,(x,y) in frames[index]["landmarks"].items()}
                for a,b in spec["links"]:d.line((points[a],points[b]),fill=(166,183,164),width=3)
                for x,y in points.values():d.ellipse((x-3,y-3,x+3,y+3),fill=(225,179,95))
                d.text((ox+5,oy+5),f"{action} {index:02d}",fill=(235,235,235))
            board.save(out/f"{action}-contact.png")
            summary["actions"][action]={"frames":count,"fps":profile["actions"][action]["fps"],"loop":profile["actions"][action]["loop"],"diagnostic_findings":len(issues)}
        summary["total_frames"]=sum(BUDGET.values())
        (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
        (out/"README.md").write_text("# Warden full-action motion blockout\n\nThese are anatomical landmark guides, **not finished pixel-art frames**. Each action requires reference-constrained artwork, cleanup, visual review and gameplay testing. The 176-frame budget is provisional.\n")
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(out,destination)
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("profile",type=Path);p.add_argument("spec",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args()
    result=produce(json.loads(a.profile.read_text()),json.loads(a.spec.read_text()),a.output)
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
