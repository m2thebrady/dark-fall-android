#!/usr/bin/env python3
"""Bake the V1526 garden art into a verified V1525 HTML candidate.

This is an offline art-production step, not a runtime dependency. The stable
bundle manifest is not modified. Archive the baked assets and candidate
manifest after browser validation, so a future promotion needs no Pillow.
"""
import base64
from collections import deque
import hashlib
import io
import json
import math
from pathlib import Path
import re
import runpy
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "game-bundle"
ART = BUNDLE / "patches/art-v1526"
HTML = ROOT / "app/src/main/assets/index.html"
BAKED = ART / "baked"
REPORTS = ROOT / "browser-smoke-results"
BAKED.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)
manifest = json.loads((BUNDLE / "manifest.json").read_text())
html = HTML.read_bytes()
base_sha = hashlib.sha256(html).hexdigest()
assert manifest["version"] == 1525, "Candidate must be made from V1525"
assert base_sha == manifest["sha256"] and len(html) == manifest["bytes"]
meta = json.loads((ART / "layout.json").read_text())
layout = json.loads((BUNDLE / "patches/art-v1521/layout.json").read_text())
landscape = json.loads((BUNDLE / "patches/art-v1524/landscape.json").read_text())
north = json.loads((BUNDLE / "patches/art-v1525/metadata.json").read_text())
roads = layout["roads"] + [r for r in landscape["links"] if r["key"] not in ("Courtyard House Walk", "Cottage West Walk")] + north["links"]
assert len(meta["gardens"]) == len(landscape["gardens"]) == 15
assert {(g["x"], g["y"]) for g in meta["gardens"]} == {(g["x"], g["y"]) for g in landscape["gardens"]}
# Independent rectangle-to-path check protects the named pedestrian lanes.
def road_clearance(g):
    minimum = math.inf
    for road in roads:
        for a, b in zip(road["points"], road["points"][1:]):
            n = max(1, math.ceil(math.dist(a, b) / 2))
            for i in range(n+1):
                t = i/n
                x, y = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
                d = math.hypot(max(0,abs(x-g["x"])-g["w"]/2),max(0,abs(y-g["y"])-g["h"]/2)) - road["width"]/2
                minimum = min(minimum, d)
    return minimum

for g in meta["gardens"]:
    assert g["kind"] in meta["kinds"]
    assert road_clearance(g) >= 5, ("Garden too close to route",g)

m = re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages', html)
assert m, "Missing terrain data"
chunks = json.loads(m[1])
atlas = Image.open(ART / meta["sourceAtlas"]).convert("RGBA")
W,H = atlas.size
assert W >= 1200 and H >= 600
# Normalize the four independent transparent crops. Some PNG encoders retain
# pale matte at the edge; only remove pale BACKGROUND joined to a boundary,
# preserving pale flowers and stone details within the isolated plant patch.
def cutout(box):
    im = atlas.crop(box)
    w,h = im.size
    alpha = im.getchannel("A")
    corners = [alpha.getpixel((x,y)) for x,y in ((0,0),(0,h-1),(w-1,0),(w-1,h-1))]
    if max(corners) > 32:
        pixels = list(im.getdata())
        seen = bytearray(w*h)
        queue = deque([y*w+x for y in range(h) for x in (0,w-1)] + [y*w+x for y in (0,h-1) for x in range(w)])
        a = bytearray(alpha.tobytes())
        while queue:
            k = queue.popleft()
            if seen[k]:
                continue
            seen[k] = 1
            r,g,b,o = pixels[k]
            if not (o < 32 or (min(r,g,b) >= 185 and max(r,g,b)-min(r,g,b) <= 48)):
                continue
            a[k] = 0
            x,y = k%w,k//w
            for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0 <= xx < w and 0 <= yy < h and not seen[yy*w+xx]:
                    queue.append(yy*w+xx)
        alpha = Image.frombytes("L",(w,h),bytes(a))
        im.putalpha(alpha)
    crop = alpha.point(lambda a: 255 if a >= 24 else 0).getbbox()
    assert crop and crop[2]-crop[0] > w*.45 and crop[3]-crop[1] > h*.2, ("Empty cutout", box, crop)
    im = im.crop(crop)
    # Transparent areas stay transparent; no flat rectangle of background.
    assert im.getchannel("A").getextrema()[0] < 20 and im.getchannel("A").getextrema()[1] > 200
    return im

sources = {}
for kind,box in zip(meta["kinds"],((0,0,W//2,H//2),(W//2,0,W,H//2),(0,H//2,W//2,H),(W//2,H//2,W,H))):
    sources[kind] = cutout(box)

TW,TH = meta["tileWidth"],meta["tileHeight"]
tiles = {}
originals = {}
def gettile(tx,ty):
    key = f"{tx}:{ty}"
    if key not in tiles:
        uri = chunks[key]
        im = Image.open(io.BytesIO(base64.b64decode(uri.split(",",1)[1]))).convert("RGBA")
        assert im.size == (TW,TH)
        tiles[key] = im
        originals[key] = im.copy()
    return key,tiles[key]
def crop_world(rect, source):
    left,top,right,bottom = rect
    result = Image.new("RGB",(right-left,bottom-top))
    for ty in range(top//TH,(bottom-1)//TH+1):
        for tx in range(left//TW,(right-1)//TW+1):
            key,_ = gettile(tx,ty)
            xx,yy = tx*TW,ty*TH
            lo,tt,hi,bb = max(left,xx),max(top,yy),min(right,xx+TW),min(bottom,yy+TH)
            result.paste(source[key].crop((lo-xx,tt-yy,hi-xx,bb-yy)).convert("RGB"),(lo-left,tt-top))
    return result

patches = []
for i,g in enumerate(meta["gardens"]):
    src = sources[g["kind"]]
    if g["flip"]:
        src = ImageOps.mirror(src)
    # Fit the generated image proportionally inside a pre-audited footprint.
    # A source with dense planting receives subtle local darkening to match
    # the existing Royal Haven ground, avoiding the pasted-on sticker effect.
    scale = min(g["w"]/src.width,g["h"]/src.height)
    s = src.resize((max(1,round(src.width*scale)), max(1,round(src.height*scale))), Image.Resampling.LANCZOS)
    rgb = ImageEnhance.Color(s.convert("RGB")).enhance(.86)
    rgb = ImageEnhance.Brightness(rgb).enhance(g["tone"])
    alpha = s.getchannel("A").point(lambda a: 0 if a < 12 else min(255, round((a-12)*255/243)))
    rgb.putalpha(alpha)
    patch = rgb
    l,t = g["x"]-patch.width//2,g["y"]-patch.height//2
    r,b = l+patch.width,t+patch.height
    assert r <= meta["world"][0] and b <= meta["world"][1] and l >= 0 and t>=0
    for ty in range(t//TH,(b-1)//TH+1):
        for tx in range(l//TW,(r-1)//TW+1):
            _,tile = gettile(tx,ty)
            xx,yy = tx*TW,ty*TH
            lo,tt,hi,bb = max(l,xx),max(t,yy),min(r,xx+TW),min(b,yy+TH)
            tile.alpha_composite(patch.crop((lo-l,tt-t,hi-l,bb-t)),dest=(lo-xx,tt-yy))
    patches.append((g,(l,t,r,b)))

# Store exact, reusable assets; only tiles whose pixels changed are encoded.
# The rest of the city's images, architecture, geometry and map are untouched.
out = []
for key,tile in sorted(tiles.items()):
    if ImageChops.difference(tile.convert("RGB"), originals[key].convert("RGB")).getbbox() is None:
        continue
    file = "ground-" + key.replace(":","-") + ".webp"
    dst = BAKED / file
    tile.convert("RGB").save(dst, "WEBP", quality=92, method=6)
    data = dst.read_bytes()
    assert len(data) > 10000 and Image.open(dst).size == (TW,TH)
    out.append({"key":key,"file":file,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
assert len(out) >= 5
baked = {"version":1526,"base_sha256":base_sha,"tiles":out}
(BAKED/"manifest.json").write_text(json.dumps(baked,indent=2)+"\n")
# A before/after contact sheet gives a reproducible review at world-pixel scale.
# It is not a live gameplay screenshot; the separate browser audit supplies that.
sheet = Image.new("RGB",(720,15*140),(35,37,31))
draw = ImageDraw.Draw(sheet)
draw.text((10,4),"V1525 BEFORE / V1526 AFTER - terrain crop review",fill=(225,226,217))
for i,(g,_) in enumerate(patches):
    cy=25+i*139
    l,t=g["x"]-104,g["y"]-50
    box=(l,t,l+208,t+100)
    a=crop_world(box,originals)
    z=crop_world(box,tiles)
    sheet.paste(a.resize((300,110),Image.Resampling.LANCZOS),(10,cy+18))
    sheet.paste(z.resize((300,110),Image.Resampling.LANCZOS),(330,cy+18))
    draw.text((10,cy),g["name"]+" | "+g["kind"],fill=(224,222,205))
sheet.save(REPORTS/"v1526-garden-bake-preview.png")
# Rebuild from the exact baked assets, using the normal patch contract.
new = runpy.run_path(str(BUNDLE/"patches/v1526.py"))["apply"](html)
assert b"<title>Dark Fall V1526</title>" in new
digest = hashlib.sha256(new).hexdigest()
candidate = {**manifest,"version":1526,"bytes":len(new),"sha256":digest,
             "patches":manifest["patches"]+["patches/v1526.py"]}
(REPORTS/"candidate-manifest.json").write_text(json.dumps(candidate,indent=2)+"\n")
HTML.write_bytes(new)
print("V1526_CANDIDATE_MANIFEST",json.dumps({"version":1526,"bytes":len(new),"sha256":digest,"baked_tiles":len(out),"gardens":len(patches)}))
print("V1526 offline terrain bake complete; verified V1525 base unchanged in repository.")
