# Dark Fall V1511 — eastern Royal Haven graphics

This graphics-only patch follows the V1510 painted market upgrade. The
existing map, actor dimensions, original structure coordinates, door anchors,
collision footprints, access routes and interiors remain unchanged.

## Building cutouts

Each asset was created with built-in image generation, using the corresponding
V1509 original isolated building sprite as an editing reference. Common prompt:
"Preserve the exact camera orientation, exterior silhouette, roof pitch,
height/width proportions, footprint, visible facade axes, position and size
of every major entrance, windows and chimney, and especially the feet and
ground contact line. Replace artificial low-poly rendered surfaces with
convincingly dimensional hand-crafted, heavily weathered architectural surfaces.
Rough stone, natural mortar, stains and repairs, overlapping irregular
slates, authentic iron and wood, variable aged leaded windowpanes some dark
some reflected sky or muted warm, realistic soft daylight from upper left.
Full object isolated on true transparent background."

| Asset | Specific art direction |
| --- | --- |
| district-rh1478East.webp | Frontal narrow stone house, irregular slate, deeply recessed windows, old shutters and a soot-stained tall chimney. |
| district-rh1478West.webp | Three-storey corner half-timber home, patched limewash, aged oak framework and authentic glass with varied lighting. |
| district-rh1478Rear.webp | Lower stone rear house, natural mortar, rough oak door canopy, restrained moss and differing leaded glass. |
| district-rh1493Longhouse.webp | Long merchant's estate with original asymmetric gable, recessed double entrances, balcony, dormer and chimneys. |
| district-rh1494Gatehouse.webp | Tall tower over a walkable OPEN stone passage, adjoining low dwelling, original door positions, weathered masonry and roof. |
| district-rh1495workshop.webp | Working artisan outbuilding with red-brown roof and lean-to, functional freight doors, timbers and contained supplies. |
| district-rh1495stepHouse.webp | Tall narrow stepped-gable stone house, human-scale door, chipped gable stones, slate, varied windows. |
| district-rh1496herbCourt.webp | Green-roof herb courtyard, asymmetric paired doors, weathered stone, dried herb details near original entrance. |
| district-rh1499bellCourt.webp | Open stone bell pavilion with transparent central passage, patinated finial, appropriate bell and masonry support feet. |

The transparent cutouts are fitted to the established normalized alpha
extents and encoded in WebP. Metadata records dimensions, chimney positions
and individual glass polygons. Obsolete full-building night silhouettes are
removed; smoke and window tints use the revised art coordinates.

## Terrain integration

The actual courtyard flagstone masks are retained, but a deterministic
world-space erosion field softens their edges into adjacent grass. Footpaths
retain their authored width and routing; only the visible margins and
weathering vary. Individual existing door coordinates drive cached small
worn stone thresholds, including multi-entrance structures. Nothing added
to the ground graphics changes collision.

The browser audit visits the original market-adjacent homes, civic ward,
gatehouse, artisan district and herb courtyard. It checks loaded assets,
existing installed structures, their preserved geometry and traversable
paths (including the gatehouse and bell-pavilion openings).
