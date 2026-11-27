"""V1526 garden renewal: replace only pre-baked, dimension-preserving terrain tiles."""
from pathlib import Path
import base64
import hashlib
import json
import re

def apply(html: bytes) -> bytes:
    root = Path(__file__).parent
    art = root / "art-v1526"
    meta = json.loads((art / "layout.json").read_text(encoding="utf-8"))
    baked = json.loads((art / "baked" / "manifest.json").read_text(encoding="utf-8"))
    assert baked["version"] == 1526 and baked["base_sha256"] == hashlib.sha256(html).hexdigest()
    assert len(baked["tiles"]) >= 5
    keys = [tile["key"] for tile in baked["tiles"]]
    assert len(set(keys)) == len(keys)
    a = re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages', html)
    assert a, "V1525 ground tile atlas missing"
    d = json.loads(a[1])
    for tile in baked["tiles"]:
        payload = (art / "baked" / tile["file"]).read_bytes()
        assert tile["key"] in d and len(payload) == tile["bytes"]
        assert hashlib.sha256(payload).hexdigest() == tile["sha256"]
        assert payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
        d[tile["key"]] = "data:image/webp;base64," + base64.b64encode(payload).decode("ascii")
    html = html[:a.start(1)] + json.dumps(d, separators=(",", ":")).encode() + html[a.end(1):]
    def edit(old, new):
        nonlocal html
        old, new = old.encode(), new.encode()
        assert html.count(old) == 1, (old[:100], html.count(old))
        html = html.replace(old, new, 1)
    meta["bakedTiles"] = keys
    info = "const rh1526Gardens=" + json.dumps(meta, separators=(",", ":")) + ";\n"
    edit("function rh1457Shade(o){", info + (root / "royal-haven-v1526.js").read_text() + "\nfunction rh1457Shade(o){")
    edit("northcourt:rh1525Status,", 'gardens:rh1526GardenStatus,reviewGardens:new URLSearchParams(location.search).has("graphicsAudit")?rh1526GardenReview:undefined,northcourt:rh1525Status,')
    # Preserve all base64 image payloads while changing the game's visible version.
    chunks = re.split(rb'(data:[^;,"\s]+;base64,[A-Za-z0-9+/=]+)', html)
    return b"".join(part if i % 2 else part.replace(b"V1525", b"V1526") for i, part in enumerate(chunks))
