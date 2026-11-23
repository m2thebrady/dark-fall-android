# Dark Fall — universal asset production roadmap

The asset pipeline is **body-family and asset-kind driven**, not tied to the Warden. `assets/catalog.json` is the planning registry for playable heroes, humanoid enemies, quadrupeds, flying enemies, irregular bosses, props, environments and effects. Frame sizes, animation names, rates and target frame counts are provisional production specifications, **not descriptions of finished sprites**.

## Asset lifecycle

1. **Register** a unique asset ID, kind, family, action list, and frame budget.
2. **Reference** approved master artwork and lock its content hash.
3. **Produce** action-specific pose guides or effect timelines and actual art frames.
4. **Validate** dimensions, frame boundaries, palette, consistency, motion and transitions as applicable.
5. **Review** labeled contact sheets and in-motion previews with a human.
6. **Approve** a specific immutable revision, never a vague filename.
7. **Compile** an approved-only runtime manifest, with unapproved assets excluded.
8. **Integrate** through an adapter into the existing game renderer, then test on desktop and Android.
9. **Roll back** an asset revision independently if it causes clipping, invisibility or performance regressions.

## Priorities

**Phase A:** Shared registry, approval gates, versioned manifest and body-family schemas. (Registry prototype implemented.)

**Phase B:** Generic production recipes for humanoid, quadruped, flying, irregular, environment and VFX. Different body families require different rigging and diagnostics; do not force a humanoid skeleton onto ravens or wolves.

**Phase C:** Actual image production and refinement: canonical reference constraints, pose-conditioned artwork, manually correctable layers, palette and silhouette checks, transitions and high-resolution review. This remains the main unsolved technical challenge.

**Phase D:** Engine asset loader and action-state playback adapter, with per-asset fallback to existing sprites. Guard against missing assets, incorrect anchors, inconsistent sheet layout and mobile performance regressions.

**Phase E:** Bulk asset batches and level/map asset packs with build-time validation, dependency tracking, packaging and rollback.

## Safety

The current manifest compiler emits metadata only. It does **not** wire assets into the live renderer, and does not claim to have produced finished character art. No V994 gameplay changes are made by this branch.
