#!/usr/bin/env python3
"""Check an asset overlay registry and file paths before runtime use."""
import argparse, hashlib, json
from pathlib import Path
from validate_asset import validate

def check_overlay(folder):
    root=Path(folder).resolve()
    registry=json.loads((root/"registry.json").read_text(encoding="utf-8"))
    if registry.get("schema_version")!=1 or not isinstance(registry.get("assets"),dict):
        raise ValueError("Unsupported overlay registry")
    for asset_id, info in registry["assets"].items():
        if not isinstance(asset_id,str) or not asset_id or any(not (c.isalnum() or c in "-_") for c in asset_id):
            raise ValueError("Invalid asset ID")
        expected=f"{asset_id}/manifest.json"
        if info.get("manifest")!=expected:
            raise ValueError(f"{asset_id}: unexpected manifest location")
        manifest_path=(root/expected).resolve()
        if not manifest_path.is_relative_to(root):
            raise ValueError("Manifest escapes overlay")
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        image_name=manifest["image"]
        if Path(image_name).name!=image_name or info.get("image")!=f"{asset_id}/{image_name}":
            raise ValueError(f"{asset_id}: invalid image path")
        image_path=(manifest_path.parent/image_name).resolve()
        if not image_path.is_relative_to(root):
            raise ValueError("Image escapes overlay")
        digest=hashlib.sha256(manifest_path.read_bytes()+image_path.read_bytes()).hexdigest()[:16]
        if digest!=info.get("revision"):
            raise ValueError(f"{asset_id}: image/manifest integrity mismatch")
        validate(manifest_path)
    print(f"Overlay validation passed: {len(registry['assets'])} assets")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("folder")
    args=p.parse_args()
    check_overlay(args.folder)
