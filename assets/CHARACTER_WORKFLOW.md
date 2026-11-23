# Character production workflow

The production sequence is:

1. Approve a master reference for character shape, clothing, equipment, palette and lighting. Reference colors in `assets/profiles/` are provisional.
2. Create a character-specific body profile. Humanoids, quadrupeds, birds and irregular monsters do **not** share a rig or dimensions.
3. Draw key poses and animation frames, keeping the frame size and anchors consistent for that individual character.
4. Create a sprite-sheet manifest using the existing validated asset format.
5. Run `python3 scripts/build_character_asset.py PROFILE MANIFEST SHEET.png OUTPUT_DIR` to check profile, animation coverage, sheet validity, and palette drift. The output directory must not exist; a report is written there.
6. Preview animations with `scripts/preview_animation.py` and the standalone viewer, inspect transitions, feet anchors, weapon anchors, silhouette and palette. Revise artwork until satisfactory.
7. Stage revisions with `scripts/stage_asset.py`, then use the selected-asset overlay tools to prepare a reversible test. Do **not** overwrite the production game bundle.
8. Only integrate after a renderer adapter and screenshot regression tests are implemented and passed.

This workflow currently **validates user-provided artwork; it does not generate finished character drawings or automatically install them into the game**. The pipeline is deliberately conservative to avoid repeating earlier visual regressions.

## Action-transition planning

Before animation production, use `python3 scripts/plan_animation_transitions.py assets/profiles/warden.json assets/profiles/warden-transition-demo.json` to inspect a planned sequence of actions, loops and per-action FPS. Equivalent sample sequences exist for the wolf and raven. This validates action availability and emits a transition plan; it does **not** yet render an animated preview or alter the in-game animation state machine.

## Offline transition preview

After preparing an approved sprite sheet and manifest, generate a self-contained HTML preview with `python3 scripts/build_transition_preview.py PROFILE MANIFEST SEQUENCE OUTPUT.html`. The preview embeds the sheet and plays the planned action sequence at the profile's per-action FPS, with pause/restart controls. The final action holds on its last frame. This is a standalone browser visualization, **not** game-runtime integration. The output path must not already exist.
