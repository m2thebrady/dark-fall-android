# Body profiles (experimental)

Each character uses a distinct body family and frame dimensions. These are **planning profiles, not finished sprite sheets**, and the proposed color values are **initial reference colors, not sampled from the production game**. They require visual approval before becoming authoritative.

Run `python3 scripts/validate_body_profile.py assets/profiles/*.json` and `python3 scripts/test_body_profiles.py`.

The optional `scripts/inspect_palette.py IMAGE PROFILE` prints a histogram and the fraction of visible pixels farther than an RGB-distance threshold of 80 from any reference color. This is a diagnostic, not proof of visual quality; highlights, lighting, anti-aliasing and gradients can legitimately differ. Set `--max-outside-fraction 0.5` to make it a gate once an approved palette exists.

Body families are humanoid, quadruped, avian and irregular. Each character controls its own frame dimensions, anchors and action timing. Profiles do not alter game runtime or require different characters to share a skeleton.

## Animation coverage check

After creating a sprite-sheet manifest, run `python3 scripts/check_animation_coverage.py assets/profiles/warden.json PATH/TO/manifest.json`. This checks whether the manifest supplies every action declared in the body profile, has no undeclared actions, and uses matching frame dimensions. The check intentionally does **not** certify artwork smoothness, gameplay integration, or frame-level quality.

Synthetic regression tests: `python3 scripts/test_palette_diagnostics.py` and `python3 scripts/test_animation_coverage.py`.
