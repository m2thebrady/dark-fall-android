# Master model and key-pose development

The Warden guide is **an approximate landmark schematic**, not a traced version of the approved Warden blueprint or finished artwork. It intentionally contains only a small number of poses. It demonstrates independent landmark locations, links, action timelines, and motion constraints.

Run `python3 scripts/validate_pose_spec.py assets/profiles/warden.json assets/pose-specs/warden-guide.json`.
Run `python3 scripts/preview_pose_spec.py assets/profiles/warden.json assets/pose-specs/warden-guide.json warden-pose-guide.png`.

## Planned art-production stages

1. Obtain and lock an approved full-resolution character reference.
2. Annotate anatomy and equipment attachment points on the **actual** reference; replace provisional landmarks.
3. Approve key poses for every action before interpolating.
4. Generate intermediary guide poses while preserving fixed body proportions.
5. Refine pixel artwork, fabric, weapon and silhouette by hand or with a reference-constrained image process.
6. Run palette, padding, anchor, continuity, and transition checks.
7. Approve sprite sheets, then test with a reversible runtime adapter.

The current implementation covers schema validation and static guide previews. It **does not** generate polished artwork, enforce anatomical rigidity during interpolation, or replace the game renderer.

## Animated motion guides

Run `python3 scripts/interpolate_pose_guides.py assets/profiles/warden.json assets/pose-specs/warden-guide.json run 32 warden-run-guide.json` to generate per-frame landmark coordinates and displacement-limit warnings.

Run `python3 scripts/animate_pose_guides.py assets/profiles/warden.json assets/pose-specs/warden-guide.json run 32 warden-run-guide.gif --fps 12` to inspect an animated anatomical guide. Both commands refuse to overwrite existing outputs. The guide is a moving stick figure and does **not** synthesize polished pixel-art sprite frames or guarantee physically correct motion. Motion limits are diagnostics only; inspect their warnings before approving a pose sequence.

## Experimental artwork-layer attachment

The `compose_artwork_layers.py` tool accepts a JSON layout containing `character` and a list of `layers`, each with a unique `name`, relative transparent PNG `image`, known `anchor`, and optional `offset` [x,y]. The layout file lives beside its PNG layers. Example:

```json
{"character":"warden","layers":[{"name":"helmet","image":"helmet.png","anchor":"head","offset":[-12,-10]},{"name":"club","image":"club.png","anchor":"hand_r","offset":[-4,-20]}]}
```

Run `python3 scripts/compose_artwork_layers.py assets/profiles/warden.json assets/pose-specs/warden-guide.json PATH/TO/layers.json PATH/TO/output.png --action run --frames 16`.

**Important:** This is a rigid-translation compositor for separately prepared transparent pieces. It does not rotate arms, bend joints, synthesize occluded surfaces, resolve layer overlap, or automatically produce finished polished character art. A real approved Warden reference and manually prepared transparent artwork parts are required. Preview output must undergo visual review before any game integration.

## Experimental joint rotation

`compose_articulated_parts.py` rotates independently painted PNG parts around an authored image-space pivot using a pair of landmarks (root and tip). The reference root-to-tip angle is compared with the interpolated frame angle. Each part remains rigid, with no skeletal skinning, cloth simulation, occlusion correction or automatic cleanup.

Example rig JSON:

```json
{"character":"warden","parts":[{"name":"left_leg","image":"left-leg.png","root":"hip","tip":"foot_l","pivot":[12,4]}]}
```

Run `python3 scripts/compose_articulated_parts.py assets/profiles/warden.json assets/pose-specs/warden-guide.json PATH/TO/rig.json PATH/TO/articulated.png --action run --frames 16`.

The master Warden blueprint must first be separated into correctly aligned transparent parts. Joint pivot and reference anatomy must be approved before using this output in gameplay. Rotated artwork can look blurry at subpixel angles; manual pixel-art cleanup remains necessary.

## Unified candidate build (experimental)

`python3 scripts/build_animation_candidate.py assets/profiles/warden.json assets/pose-specs/warden-guide.json PATH/TO/rig.json PATH/TO/warden-idle-candidate.png --action idle --frames 16 --report PATH/TO/report.json`

This command interpolates poses, renders a candidate sprite sheet from separately painted articulated PNG parts, and audits body proportions, angular motion, club-to-hand attachment, and frame margins. By default any diagnostic finding **blocks** the output. `--allow-warnings` exports a diagnostic candidate despite findings, never an approved asset. No candidate is automatically installed into the game. The report includes an unapproved status; visual inspection and explicit approval remain mandatory. The cloth-follow guide is exported as numerical positions, not automatically applied to painted cloth.
