# Dark Fall V1512 — Royal Haven fortifications and market stalls

All render geometry, collision, character scale, authored door and store
interaction locations are retained. Three existing perimeter watchtower
sprites serve eight original world instances. Two existing market furniture
instances now select independent new artwork, without changing their
placement, classification, flip or dimensions.

## Asset art direction

Built-in image generation, using the existing transparent sprites as edit
references. Preserve the silhouette, footprint, camera, door size and
position, post and beam positions, and original perspective. Weathered,
realistic hand-crafted 3D medieval materials, muted palette and diffuse
upper-left daylight; isolated sprite with authentic alpha, no people or
ground outside silhouette.

| New asset | Art direction |
| --- | --- |
| tower0.webp | Rugged warm gray stone, uneven battlements, slight ivy and oak/iron door. |
| tower1.webp | Cold blue-gray garrison masonry, revised crenel stones, muted pennant, deeply recessed windows. |
| tower2.webp | Warm mixed rubble, coarse lime mortar, corner quoins, weathered lintel and moss. |
| spice.webp | Olive and linen canopy, herb bundles, pots, spice jars, scales, woven textiles and baskets. |
| pottery.webp | Patched natural linen, earthenware, ceramic jugs, bowls, reed mat and wrapped wares. |

New transparent images are fitted to the original alpha extents and encoded
as compact WebP. Differentiated market goods, weathering and authentic
cloth are baked into the art, not generated at runtime.

## Perimeter integration

The original painted wall topology, openings, battlements, alpha and stone
joints are preserved. World-space rain, damp, grain, lichen and stone color
modulation cross repeating tile boundaries smoothly. New foundation stains
fade out irregularly over the existing soil, and individual tower contacts
follow the new lower alpha contours. The south wall uses the existing local
player-centered cutaway around the actual visible curtain sections. The
cache limits material stamping to one new wall tile per frame and 2.2
million active wall pixels.
