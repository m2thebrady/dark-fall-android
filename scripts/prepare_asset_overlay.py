#!/usr/bin/env python3
"""Prepare an isolated asset overlay directory; NEVER modify bundled game HTML.

This is a packaging adapter, not a runtime renderer. A later runtime bridge
will opt in to loading these files. Original game assets stay untouched.
"""
import argparse, json, shutil
from pathlib import Path
from select_assets import resolve_selection

def prepare(selection, staged_root, output):
    resolved=resolve_selection(selection,staged_root)
    destination=Path(output).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Output must be empty to avoid overwriting a previous build")
    destination.mkdir(parents=True,exist_ok=True)
    registry={"schema_version":1,"assets":{}}
    for asset_id, info in resolved.items():
        target=destination/asset_id
        target.mkdir()
        manifest=Path(info["manifest"])
        image=Path(info["image"])
        shutil.copy2(manifest,target/"manifest.json")
        shutil.copy2(image,target/image.name)
        registry["assets"][asset_id]={"revision":info["revision"],"manifest":f"{asset_id}/manifest.json","image":f"{asset_id}/{image.name}"}
    (destination/"registry.json").write_text(json.dumps(registry,indent=2)+"\n",encoding="utf-8")
    return registry

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("selection")
    p.add_argument("--staged-root",default="assets/staged")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(prepare(args.selection,args.staged_root,args.output),indent=2))
