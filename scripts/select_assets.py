#!/usr/bin/env python3
"""Resolve asset revision selections without touching the bundled game."""
import argparse, hashlib, json
from pathlib import Path
from validate_asset import validate

def resolve_selection(config_path, staged_root):
    config=json.loads(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(config,dict) or not isinstance(config.get("assets"),dict):
        raise ValueError("Selection must contain an assets object")
    resolved={}
    for asset_id,revision in sorted(config["assets"].items()):
        if not isinstance(asset_id,str) or not asset_id or not all(c.isalnum() or c in "-_" for c in asset_id):
            raise ValueError("Invalid asset ID")
        if not isinstance(revision,str) or len(revision)!=16 or any(c not in "0123456789abcdef" for c in revision):
            raise ValueError(f"{asset_id}: revision must be a 16-digit SHA256 prefix")
        folder=Path(staged_root)/asset_id/revision
        if not folder.is_dir():
            raise ValueError(f"{asset_id}: staged revision missing")
        manifests=list(folder.glob("*.json"))
        if len(manifests)!=1:
            raise ValueError(f"{asset_id}: expected exactly one manifest")
        manifest_path=manifests[0]
        m=json.loads(manifest_path.read_text(encoding="utf-8"))
        if m.get("name",manifest_path.stem)!=asset_id:
            raise ValueError(f"{asset_id}: manifest name mismatch")
        image=folder/m["image"]
        if image.parent.resolve()!=folder.resolve() or not image.is_file():
            raise ValueError(f"{asset_id}: invalid image path")
        digest=hashlib.sha256(manifest_path.read_bytes()+image.read_bytes()).hexdigest()[:16]
        if digest!=revision:
            raise ValueError(f"{asset_id}: staged files changed after import")
        validate(manifest_path)
        resolved[asset_id]={"revision":revision,"manifest":str(manifest_path),"image":str(image)}
    return resolved

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("selection")
    parser.add_argument("--staged-root",default="assets/staged")
    parser.add_argument("--output")
    args=parser.parse_args()
    result=resolve_selection(args.selection,args.staged_root)
    report=json.dumps({"resolved":result},indent=2)
    if args.output:
        Path(args.output).write_text(report+"\n",encoding="utf-8")
    print(report)
