#!/usr/bin/env python3
"""Synthetic tests of palette distance, alpha handling and threshold behavior."""
import json,tempfile
from pathlib import Path
from PIL import Image
from inspect_palette import inspect
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    profile=root/"profile.json"
    profile.write_text(json.dumps({"palette":{"base":"#112233"}}))
    image=root/"sprite.png"
    pixels=Image.new("RGBA",(4,1),(17,34,51,255))
    pixels.putpixel((1,0),(250,0,0,255))
    pixels.putpixel((2,0),(255,255,255,0))
    pixels.save(image)
    report=inspect(image,profile)
    assert report["opaque_pixels"]==3,report
    assert report["unique_colors"]==2,report
    assert report["outside_reference_tolerance"]==1,report
    assert report["outside_fraction"]==0.3333,report
    pixels=Image.new("RGBA",(2,1),(0,0,0,0))
    pixels.save(image)
    report=inspect(image,profile)
    assert report["opaque_pixels"]==0 and report["outside_fraction"]==0,report
print("Palette diagnostic tests passed")
