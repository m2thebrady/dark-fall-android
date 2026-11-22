#!/usr/bin/env python3
"""Stage a validated asset in a versioned directory without editing the game.

Each revision is content-addressed, making rollback a pointer change later.
"""
import argparse, hashlib, json, shutil
from pathlib import Path
from validate_asset import validate

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--destination",default="assets/staged")
    args=parser.parse_args()
    source=Path(args.manifest).resolve()
    manifest=json.loads(source.read_text(encoding="utf-8"))
    validate(source)
    image=(source.parent/manifest["image"]).resolve()
    asset_id=manifest.get("name",source.stem)
    if not asset_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in asset_id):
        raise ValueError("Asset name must contain only letters, digits, dash, underscore")
    digest=hashlib.sha256(source.read_bytes()+image.read_bytes()).hexdigest()[:16]
    dest=Path(args.destination).resolve()/asset_id/digest
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(image,dest/image.name)
    shutil.copy2(source,dest/source.name)
    print(json.dumps({"asset":asset_id,"revision":digest,"staged":str(dest)},indent=2))

if __name__=="__main__":
    main()
