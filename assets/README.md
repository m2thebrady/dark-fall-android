# Dark Fall asset validation (experimental)

New character/enemy sprites should be authored as standalone **RGBA PNG sprite sheets** with a neighboring JSON manifest before integration into the 45 MB legacy HTML. Run `python3 -m pip install Pillow` then `python3 scripts/validate_asset.py assets/examples/warden.json` after adding the referenced PNG.

The example manifest is a **schema example only**: the PNG does not exist yet, so do not run the example in CI until a real sheet is added.

Each action lists zero-based row-major frame indices. Every frame has the same width/height and a configurable transparent safe margin. The validator rejects missing images, wrong dimensions, non-RGBA sheets, invalid indices, empty actions and artwork touching the frame edge. This prevents a class of sprite clipping and accidental transparent-frame bugs; it cannot guarantee anatomy, motion quality, or alignment.

Next: render a contact sheet with frame labels, track per-frame feet/weapon anchors, check animation transition states, and integrate validated assets through a reversible build step. Keep existing sprites untouched until replacement art passes visual review.
