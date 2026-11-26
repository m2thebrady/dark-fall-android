# Royal Haven — interior production plan (V1540)

The V1540 exterior pass preserves the existing building anchors, collision footprints, character scale and entrance triggers. The readiness survey uses the real 105-unit interaction radius, a 7-unit clearance probe and the existing collision-aware room-exit algorithm. It does not create rooms or alter transitions.

All 20 active exterior sites have a clear sampled approach and a clear exterior exit point. Eight have the newer bespoke room renderer; four use the landmark renderer, seven use older shop rooms, and one is the future guild hall. This is an exterior geometry check, not an interior traversal test.

## Recommended next production sequence

1. **Royal Castle** — grand audience hall, council and archive/armory transitions, monumental angular stonework and realistic furniture at character scale. Preserve the existing wings and castle story functions.
2. **Temple of Light** — vaulted nave, side chapels, sanctuary and quiet open axial walking space; natural stone, warm candles and varied window light.
3. **Caster Guild** — arcane library and lecture / ritual halls, architectural depth and distinct furniture, with restrained effects.
4. **Future Guild Hall** — a civic guild interior with meeting/training areas and wide circulation; keep gameplay hooks explicit.
5. **Legacy commercial interiors** — general and item stores, apothecary, alchemist, herbalist, bakery and cellar; emphasize believable stocked workstations, custom room identity and unobstructed paths. Dark Guild Cave receives its own rugged monumental treatment.
6. **Review existing bespoke interiors** — weaponsmith, armorer, leatherworker, enchanter, fletcher, tailor, residence and Iron Hearth Tavern. Keep their existing interaction and traversal logic; revise art only when there is a clear quality improvement.

## Acceptance criteria

- Distinct architecture that reflects exterior building scale; no identical generic rooms.
- Consistent overhead perspective, dark medieval materials, realistic angular geometry, readable entry and exit.
- Existing owner, dialogue, inventory and story interaction anchors remain functional; avoid new NPC redesigns.
- Test character/companion spawn footprints, all exits, shopkeeper interactions and path clearance; no trapping behind furnishings.
- Reuse bounded static caches and cull offscreen art; evaluate on desktop and mobile before broad replacement.

## V1540 exterior entrance survey

| Structure | Interior type | Approach point | Exit point |
|---|---|---|---|
| Royal Castle | landmark | 1800.0, 623.0 | 1800.0, 655.0 |
| Temple of Light | landmark | 565.0, 726.0 | 565.0, 758.0 |
| Caster Guild | landmark | 3090.0, 712.0 | 3090.0, 744.0 |
| Weapon Smith | bespoke | 350.0, 1413.0 | 350.0, 1415.0 |
| Armor Smith | bespoke | 805.0, 1413.0 | 805.0, 1415.0 |
| Leatherworker | bespoke | 1275.0, 1413.0 | 1275.0, 1415.0 |
| General Store | legacy-shop | 2385.0, 1413.0 | 2385.0, 1415.0 |
| Item Shop | legacy-shop | 2865.0, 1413.0 | 2865.0, 1415.0 |
| Alchemist | legacy-shop | 3345.0, 1413.0 | 3345.0, 1415.0 |
| Herbalist | legacy-shop | 335.0, 2043.0 | 335.0, 2045.0 |
| Enchanter | bespoke | 865.0, 2043.0 | 865.0, 2045.0 |
| Fletcher | bespoke | 1275.0, 2043.0 | 1275.0, 2045.0 |
| Tailor | bespoke | 2325.0, 2043.0 | 2325.0, 2045.0 |
| Apothecary | legacy-shop | 2865.0, 2043.0 | 2865.0, 2045.0 |
| Bakery | legacy-shop | 3345.0, 2043.0 | 3345.0, 2045.0 |
| Future Guild Hall | future | 1740.0, 2118.0 | 1740.0, 2120.0 |
| Dark Guild Cave | landmark | 4980.0, 610.0 | 4980.0, 612.0 |
| Town Residence | bespoke | 3820.0, 1440.0 | 3820.0, 1442.0 |
| The Iron Hearth Tavern | bespoke | 1205.0, 858.0 | 1205.0, 860.0 |
| Storehouse Cellar | legacy-shop | 765.6, 2380.0 | 765.6, 2382.0 |
