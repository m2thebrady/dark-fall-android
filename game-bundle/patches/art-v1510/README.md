# Royal Haven exterior artwork, V1510

Sixteen original game facades were revised for one consistent dimensional medieval exterior style.
The art was generated in three original sprite atlases and extracted into transparent WebP sprites,
fitted to the established game-space entrance anchors and facade bounds. Older smithies, shops,
inn and cellar use distinct replacement architecture; the existing dimensional buildings retain their
roof planes, doors and footprints with revised texture, individually recognizable trade signs,
weathered wood, limewash, masonry, moss, hand-made roofing and storefront displays.

All files here are exterior-only assets. They do not change collision, entrances, room layouts or actors.
`metadata.json` records the normalized door, chimney, light and forge-fire positions for each facade.
The materializer embeds these WebP files into the verified HTML, and the renderer aligns the images
with existing world geometry. The ground contact treatment uses each sprite's actual lower alpha
contour to blend it into surrounding cobbles and soil. No added decorative ground pixels obstruct movement.

A subsequent graphics-only pass adds six residential sprites (townhouse, forward cottage,
deep stone house, left courtyard cottage, main court house, and court wing). These are
recorded separately in `home-metadata.json`. Their existing house geometry and door anchors
are retained; the contact-ground treatment now also follows estate, annex and courtyard buildings.

The existing map removed Wayfarer Inn in an earlier build; its replacement sprite remains
available for a future lot without altering the current layout. The relocated Storehouse
Cellar has a second fitted raster using its established 193/650 door anchor.

### Forest Gate and street integration

- `forest-gate-revised.webp`: the two outdated outer guard towers are replaced with original dimensionally shaded, weathered stone architecture. The original central arch, wooden gates, crest, banner anchors and flames are retained in the composite. Original world draw fit is unchanged. Built-in image generation prompt: “Edit only the old flat gray rectangular outer side towers; dimensional weathered sandstone guardhouse buttresses, irregular stone, recessed arched windows, iron-banded timber doors, ivy and damp moss, surrounding central gate style, preserve the original silhouette and transparent central passage.” The generated side sections were blended into the old gate sprite and encoded to WebP.
- `shoulder-{i}-{j}.webp`: four sparse, half-resolution world-aligned overlays from the existing baked terrain, built using `scripts/build_royal_haven_shoulders.py`. The overlays mix adjacent actual cobble and grass material along irregular weathered road margins; no collision changes, no changes to the mountain/forest. They load only as a corresponding decoded terrain chunk is drawn. Run the script with a materialized game HTML and the destination art directory to reproduce.
- Fitted foundations now sample the revised facade silhouettes, use a less prominent curb line and have ragged outer wear; landmark foundations receive matching irregular soil contact.

### Civic hall and service architecture

The following original generated transparent sprites replace their actual indexed legacy assets; all use the approved dimensional painted medieval style and retain ground footprints, collisions and gameplay. Built-in image generation used the original buildings as camera/style references. New images were re-fitted to the same base widths, with taller service-building elevations for believable human-sized doorways.

- `guild-hall-revised.webp`: prestigious civic stone hall with square stair tower, two-storey timber meeting chamber, large double oak entrance, crossed-key crest, weathered slate and individually dark/cool/warm leaded windows. Window polygons and two animated lantern anchors in `civic-metadata.json` align with the revised art and preserve the original entrance.
- `annex-storehouse-revised.webp`: merchant storehouse with off-center double oak loading doors, working hoist gable, tucked-in burlap sacks and patched masonry.
- `annex-supply-depot-revised.webp`: asymmetric depot with terracotta lean-to roof, half-open recessed loading doorway, ropes and stacked crates.
- `annex-herb-workshop-revised.webp`: herb drying workshop with aged slate, open upper shutters, recessed drying racks, limewashed timber and mossy stone.
- Ground contact and wear follow the existing exterior's silhouette and actual thresholds; originally larger rebuilt herb annex retains its separate asset. Door and light metadata are normalized to the sprite dimensions.
