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
