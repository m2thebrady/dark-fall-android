#!/usr/bin/env python3
"""Validate a reproducible art-reference lock without treating it as approval."""
import argparse,hashlib,json,re
from pathlib import Path

SHA=re.compile(r"^[0-9a-f]{64}$")
def validate(lock,base,profile):
    issues=[]
    if lock.get("character")!=profile.get("id"):issues.append("character mismatch")
    if lock.get("status") not in ("draft","approved"):issues.append("invalid approval status")
    if lock.get("status")=="approved" and not lock.get("approved_by"):issues.append("approved lock requires approver")
    if lock.get("frame")!=profile.get("frame"):issues.append("frame size mismatch")
    files=lock.get("references")
    if not isinstance(files,list) or not files:return issues+["references must be a nonempty list"]
    seen=set()
    for entry in files:
        if not isinstance(entry,dict):issues.append("invalid reference");continue
        name=entry.get("path");digest=entry.get("sha256")
        if not isinstance(name,str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:issues.append("unsafe reference path");continue
        if name in seen:issues.append("duplicate reference")
        seen.add(name)
        if not isinstance(digest,str) or not SHA.fullmatch(digest):issues.append(f"{name}: invalid SHA256");continue
        file=base/name
        if not file.is_file():issues.append(f"{name}: missing reference");continue
        actual=hashlib.sha256(file.read_bytes()).hexdigest()
        if actual!=digest:issues.append(f"{name}: reference hash changed")
    return issues

def main():
    p=argparse.ArgumentParser();p.add_argument("profile",type=Path);p.add_argument("lock",type=Path)
    a=p.parse_args()
    issues=validate(json.loads(a.lock.read_text()),a.lock.parent,json.loads(a.profile.read_text()))
    print(json.dumps({"valid":not issues,"issues":issues},indent=2))
    if issues:raise SystemExit(1)
if __name__=="__main__":main()
