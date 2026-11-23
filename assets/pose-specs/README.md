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
