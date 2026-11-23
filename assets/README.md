# Dark Fall asset validation (experimental)

New character/enemy sprites should be authored as standalone **RGBA PNG sprite sheets** with a neighboring JSON manifest before integration into the 45 MB legacy HTML. Run `python3 -m pip install Pillow` then `python3 scripts/validate_asset.py assets/examples/warden.json` after adding the referenced PNG.

The example manifest is a **schema example only**: the PNG does not exist yet, so do not run the example in CI until a real sheet is added.

Each action lists zero-based row-major frame indices. Every frame has the same width/height and a configurable transparent safe margin. The validator rejects missing images, wrong dimensions, non-RGBA sheets, invalid indices, empty actions and artwork touching the frame edge. This prevents a class of sprite clipping and accidental transparent-frame bugs; it cannot guarantee anatomy, motion quality, or alignment.

Preview a real sheet with `python3 scripts/preview_asset.py path/to/asset.json --output /tmp/asset-preview.png`. The preview labels every action frame, shows transparency on a checkerboard, and draws the safe margin.\n\nNext: track per-frame feet/weapon anchors, check animation transition states, and integrate validated assets through a reversible build step. Keep existing sprites untouched until replacement art passes visual review.

## Safe staging (not yet game integration)

After validation, run `python3 scripts/stage_asset.py path/to/asset.json`. This creates an immutable-style, content-hashed revision under `assets/staged/<asset-name>/<hash>/`. Old revisions remain available for rollback. The staging tool does **not** change the game or select a live revision. Never delete the existing bundled character until a new one passes phone testing.

Animation manifests may include `anchors` keyed by frame number with `feet` and `weapon` coordinates, `anchor_tolerance`, and `transitions` as pairs of valid action names. These checks validate structure and positioning; they do not guarantee good motion.

## Select revisions for a future build

Copy `assets/selection.example.json` to a private selection file, then populate `assets` with asset IDs mapped to their 16-character revision hashes. Run `python3 scripts/select_assets.py path/to/selection.json` to verify that every selected revision exists, matches its original hash, and still passes sprite validation. This does **not** inject the artwork into the game yet; the integration adapter will be built and tested separately.

## Isolated overlay packaging (experimental)

After selecting validated revisions, run `python3 scripts/prepare_asset_overlay.py path/to/selection.json --output /tmp/dark-fall-overlay`. This creates an isolated folder with a registry and asset files. It refuses to overwrite an existing nonempty output. **No current game renderer reads this registry yet**, and it is deliberately not included in the Android publishing workflow. The next step is a test-only runtime bridge with an explicit opt-in switch and a legacy fallback.

## Legacy renderer investigation

Run `python3 scripts/survey_renderer.py` to create `browser-smoke-results/renderer-survey.json`, a read-only inventory of sprite drawing, image loading, animation state, and class references. The survey reports approximate source locations; it does not imply these are safe injection points. Review actual render functions and frame timing before implementing a replacement adapter.

## Animation silhouette diagnostics

Run `python3 scripts/inspect_animation.py path/to/character.json --output /tmp/animation-report.json` to inspect opaque artwork bounds for every animation frame. It warns when a frame is fully transparent or an action's silhouette width/height varies beyond the configurable ratio (default 1.5x). Use `--fail-on-warning` for strict experiments. These warnings are review aids: deliberate attacks, falls, and perspective changes may legitimately change silhouette dimensions. This does not yet render an animated GIF or test in-game transitions.

## Animated GIF previews

Run `python3 scripts/preview_animation.py path/to/character.json --output /tmp/dark-fall-gifs --fps 10` to generate one looping GIF for each action, including idle, run, attack and death when present. Previews show actual sheet frames on a neutral background, preserving frame dimensions and ordering. Use a fresh output directory: existing GIF files are not overwritten. These previews are for visual review only; the game's renderer may use different timing, scaling and interpolation.

## Browser-based sprite viewer (isolated)

Prepare an overlay, then run `python3 scripts/build_sprite_viewer.py /tmp/dark-fall-overlay --output /tmp/dark-fall-viewer`. Serve the viewer directory with `python3 -m http.server 8000 --directory /tmp/dark-fall-viewer`, then open `http://localhost:8000`. Select a character and action to preview frames on a canvas at a fixed 10 fps. Pause, resume, or step forward one frame at a time to inspect sprite clipping and proportions. This standalone viewer intentionally does **not** modify or hook the production game renderer, and does not yet support custom per-action timing, anchors or game effects. It is a safe intermediate stage before a test-only in-game bridge.
