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
