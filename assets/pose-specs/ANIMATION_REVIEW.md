# Animation review package

Use the approved character artwork split into transparent parts, and a reviewed joint rig. Run:

```bash
python3 scripts/build_animation_review.py assets/profiles/warden.json assets/pose-specs/warden-guide.json PATH/TO/rig.json PATH/TO/warden-idle-review --action idle --frames 16 --reference-lock PATH/TO/reference-lock.json
```

Output is a new directory containing:

- `candidate.png`: horizontal sprite sheet
- `contact-sheet.png`: labeled per-frame inspection layout
- `diagnostics.json`: movement, clipping, color, silhouette and reference-gate results
- `REVIEW.md`: checklist for human review

Review output is **always pending human review**. Do not interpret a zero-warning report as approval. This tool refuses to overwrite an existing review directory and does not install anything into the game. Without an approved master reference, synthetic tooling tests may omit `--reference-lock`, but real character-art production must include it.
