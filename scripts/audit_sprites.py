#!/usr/bin/env python3
"""Non-destructive static guardrails for sprite data and animation source.
This is an audit, not a substitute for runtime visual tests.
"""
from pathlib import Path
import re, json, hashlib
root = Path(__file__).resolve().parents[1]
html = (root / "app/src/main/assets/index.html").read_text(encoding="utf-8")
# Extract data URI image payload declarations and report basic integrity.
data_images = re.findall(r'data:image/(?:png|webp|jpeg);base64,([A-Za-z0-9+/=]+)', html)
bad = [i for i, value in enumerate(data_images) if len(value) < 32 or len(value) % 4 != 0]
if bad:
    raise SystemExit(f"Invalid embedded sprite image payloads at indices {bad[:20]}")
# Report suspicious source-level patterns without failing legacy content.
checks = {
    "embedded_image_payloads": len(data_images),
    "sprite_mentions": len(re.findall(r"sprite", html, re.I)),
    "animation_mentions": len(re.findall(r"animation|animFrame|frameIndex", html, re.I)),
    "canvas_mentions": len(re.findall(r"<canvas|\.getContext\(", html, re.I)),
    "source_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
}
print("Sprite audit:", json.dumps(checks, indent=2))
if checks["sprite_mentions"] == 0 or checks["canvas_mentions"] == 0:
    raise SystemExit("Expected game sprite/canvas infrastructure missing")
