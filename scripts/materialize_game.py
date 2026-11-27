#!/usr/bin/env python3
"""Reconstruct and verify the original game HTML from Git-safe gzip parts."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "game-bundle"
DEST = ROOT / "app/src/main/assets/index.html"


def materialize():
    manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    total = 0
    fd, name = tempfile.mkstemp(prefix="game-", suffix=".tmp", dir=DEST.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            for part in manifest["parts"]:
                path = BUNDLE / part["name"]
                if path.stat().st_size != part["bytes"]:
                    raise ValueError(f"Incorrect size: {path.name}")
                with path.open("rb") as src:
                    if hashlib.file_digest(src, "sha256").hexdigest() != part["sha256"]:
                        raise ValueError(f"Incorrect checksum: {path.name}")
                with gzip.open(path, "rb") as src:
                    while chunk := src.read(1024 * 1024):
                        digest.update(chunk)
                        total += len(chunk)
                        out.write(chunk)
        base = manifest.get("base", manifest)
        if digest.hexdigest() != base["sha256"] or total != base["bytes"]:
            raise ValueError("Reconstructed base HTML does not match manifest")
        if manifest.get("patches"):
            content = Path(name).read_bytes()
            for patch in manifest["patches"]:
                path = BUNDLE / patch
                content = runpy.run_path(str(path))["apply"](content)
            Path(name).write_bytes(content)
            total = len(content)
            digest = hashlib.sha256(content)
        if digest.hexdigest() != manifest["sha256"] or total != manifest["bytes"]:
            raise ValueError("Patched HTML does not match manifest")
        os.replace(name, DEST)
    finally:
        Path(name).unlink(missing_ok=True)
    print(f"Materialized Dark Fall V{manifest['version']}: {total} bytes, SHA256 {digest.hexdigest()}")


if __name__ == "__main__":
    materialize()
