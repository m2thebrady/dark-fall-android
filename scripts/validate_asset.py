#!/usr/bin/env python3
"""Validate standalone sprite sheets before integrating them into Dark Fall.

Usage: python3 scripts/validate_asset.py path/to/asset.json
Manifest includes image, frame_width, frame_height, columns, rows, actions.
Requires Pillow. Read-only; does not modify game HTML.
"""
import argparse, json
from pathlib import Path
from PIL import Image

def validate(manifest_path):
    p = Path(manifest_path).resolve()
    m = json.loads(p.read_text(encoding="utf-8"))
    image_path = (p.parent / m["image"]).resolve()
    with Image.open(image_path) as image:
        image.load()
        if image.mode != "RGBA":
            raise ValueError("Sprite sheet must use RGBA transparency")
        fw, fh = int(m["frame_width"]), int(m["frame_height"])
        cols, rows = int(m["columns"]), int(m["rows"])
        if min(fw, fh, cols, rows) <= 0:
            raise ValueError("Frame dimensions and grid counts must be positive")
        if image.size != (fw * cols, fh * rows):
            raise ValueError(f"Sheet {image.size} does not match grid {(fw*cols, fh*rows)}")
        actions = m["actions"]
        if not isinstance(actions, dict) or not actions:
            raise ValueError("Provide named actions with frame indices")
        used = set()
        for name, indices in actions.items():
            if not isinstance(indices, list) or not indices:
                raise ValueError(f"{name}: empty action")
            for i in indices:
                if type(i) is not int or not 0 <= i < cols * rows:
                    raise ValueError(f"{name}: invalid frame index {i}")
                used.add(i)
        margin = int(m.get("safe_margin", 2))
        if margin < 0 or margin * 2 >= min(fw, fh):
            raise ValueError("Invalid safe_margin")
        warnings = []
        for i in sorted(used):
            x, y = (i % cols) * fw, (i // cols) * fh
            frame = image.crop((x, y, x + fw, y + fh))
            bbox = frame.getchannel("A").getbbox()
            if bbox is None:
                warnings.append(f"Frame {i}: fully transparent")
                continue
            left, top, right, bottom = bbox
            if left < margin or top < margin or right > fw - margin or bottom > fh - margin:
                warnings.append(f"Frame {i}: artwork reaches frame safety margin")
        result = {"asset": m.get("name", p.stem), "frames": len(used), "actions": list(actions), "warnings": warnings}
        print(json.dumps(result, indent=2))
        if warnings and not m.get("allow_margin_warnings", False):
            raise ValueError("Sprite safety validation failed; adjust padding or review manifest")
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    validate(args.manifest)
