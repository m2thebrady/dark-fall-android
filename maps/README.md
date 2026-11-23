# Dark Fall handcrafted map data (experimental)

This is a standalone, versioned layout description for future handcrafted levels. It **does not alter the V994 runtime map**.

Run `python3 scripts/validate_map.py maps/woodland-approach.json` and `python3 scripts/test_map_validation.py`.

Coordinates are abstract world units; objects have unique IDs, types, positions, sizes, and optional solidity. The validator checks boundaries, dimensions, duplicate IDs, spawn and exit presence, and spawn/exit collision with solid objects. It is deliberately not a pathfinding or playability guarantee.

The example evokes the existing woodland-to-castle progression but is **not an extraction of production coordinates**. Do not substitute it into the game without renderer and collision-system integration tests.
