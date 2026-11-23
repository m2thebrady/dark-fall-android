#!/usr/bin/env python3
"""Unified offline Warden animation candidate build; never modifies gameplay assets."""
import argparse,json,tempfile
from pathlib import Path
from interpolate_pose_guides import interpolate,diagnose
from audit_pose_motion import audit
from guide_equipment_and_cloth import attachment_drift,follow
from compose_articulated_parts import render,validate_rig
from audit_articulated_rig import analyze
from audit_sprite_margins import inspect
from audit_sprite_consistency import analyze as audit_consistency
from validate_art_reference_lock import validate as validate_reference_lock

def build(profile,spec,rig,base,action,count,output,strict=True,reference_lock=None,reference_base=None):
    if reference_lock is not None:
        issues=validate_reference_lock(reference_lock,reference_base or base,profile)
        if issues:raise ValueError('Invalid master reference lock: '+'; '.join(issues))
        if reference_lock.get('status')!='approved':raise ValueError('Master reference is not approved')
    errors=validate_rig(spec,rig,base)
    if errors:raise ValueError("; ".join(errors))
    if output.exists():raise FileExistsError("Refusing to overwrite candidate")
    frames=interpolate(profile,spec,action,count)
    report={"character":spec["character"],"action":action,"frames":count,
            "pose_displacement":diagnose(spec,frames),
            "body_motion":audit(spec,frames),
            "joint_motion":analyze(spec,rig,frames),
            "weapon_attachment":[],"cloth_guide":[],
            "sprite_margins":[],"sprite_consistency":[],"approved":False,
            "note":"Experimental candidate; approval requires visual review of actual artwork"}
    if "hand_r" in spec["landmarks"] and "club_tip" in spec["landmarks"]:
        import math
        ref=math.dist(spec["landmarks"]["hand_r"],spec["landmarks"]["club_tip"])
        report["weapon_attachment"]=attachment_drift(frames,"hand_r","club_tip",ref)
    if "hip" in spec["landmarks"]:
        report["cloth_guide"]=follow(frames,"hip")
    with tempfile.TemporaryDirectory() as tmp:
        sheet=Path(tmp)/"sheet.png"
        render(profile,spec,rig,base,action,count,sheet)
        margins=inspect(sheet,profile["frame"]["width"],profile["frame"]["height"])
        report["sprite_margins"]=margins["findings"]
        report["sprite_consistency"]=audit_consistency(sheet,profile["frame"]["width"],profile["frame"]["height"])["findings"]
        report["blocking_count"]=sum(len(report[k]) for k in ("pose_displacement","body_motion","joint_motion","weapon_attachment","sprite_margins","sprite_consistency"))
        if strict and report["blocking_count"]:
            raise ValueError(f"Candidate rejected: {report['blocking_count']} diagnostic findings")
        output.parent.mkdir(parents=True,exist_ok=True)
        sheet.replace(output)
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("profile","spec","rig","output"):p.add_argument(name,type=Path)
    p.add_argument("--action",default="run");p.add_argument("--frames",type=int,default=32)
    p.add_argument("--allow-warnings",action="store_true")
    p.add_argument("--report",type=Path)
    p.add_argument("--reference-lock",type=Path)
    a=p.parse_args()
    if a.report and a.report.exists():raise FileExistsError("Refusing to overwrite report")
    profile=json.loads(a.profile.read_text());spec=json.loads(a.spec.read_text());rig=json.loads(a.rig.read_text())
    lock=json.loads(a.reference_lock.read_text()) if a.reference_lock else None
    result=build(profile,spec,rig,a.rig.parent,a.action,a.frames,a.output,not a.allow_warnings,lock,a.reference_lock.parent if a.reference_lock else None)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
