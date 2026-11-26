# Royal Haven V1526: lived-in gardens

Four original, realistic garden and yard cutouts renew fifteen already established garden sites. Each bounding rectangle was checked against all named roads and residential approaches; the plants are low, decorative surfaces, not new collision objects. Terrain dimensions, architecture, zoom, and NPCs are unchanged.

The checked and reproducible V1525 bundle remains the stable manifest until the new browser candidate has passed. `scripts/build_v1526_candidate.py` starts with verified V1525 HTML, produces only changed WebP terrain tiles, archives their byte counts and checksums plus the candidate bundle manifest, and applies `patches/v1526.py`. Full browser smoke covers V1525's existing regressions and five garden locations. No APK release is produced.

After successful QA, promote the exact archived `baked/` directory and candidate manifest, increment Android version metadata, and remove the temporary candidate build step. The regular materializer can then apply V1526 with the standard library alone.
