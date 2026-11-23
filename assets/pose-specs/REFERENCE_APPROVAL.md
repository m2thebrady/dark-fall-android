# Visual reference approval gate

The Warden's existing approved blueprint must be supplied as an actual image before its identity can be locked. **No placeholder is an approved reference.**

A lock file lives beside the artwork it references:

```json
{
  "character": "warden",
  "status": "draft",
  "frame": {"width": 160, "height": 192},
  "references": [
    {"path": "warden-master.png", "sha256": "REPLACE_WITH_REAL_64_CHARACTER_SHA256"}
  ]
}
```

Run `python3 scripts/validate_art_reference_lock.py assets/profiles/warden.json PATH/TO/reference-lock.json`. The validator checks character identity, dimensions, safe relative file paths, SHA256 integrity, and human approval metadata. An approved lock must include `"approved_by"` identifying the reviewer. A passing hash check does **not** establish artistic quality, animation fidelity, or human approval. Do not change a locked reference silently; make a new revision with a new hash and review.

Future work: integrate the lock into the unified candidate builder, compare palette and silhouette across all action frames, then require an explicit approved revision before renderer integration. Current V994 gameplay assets remain unchanged.

## Candidate builder integration

Pass `--reference-lock PATH/TO/reference-lock.json` to `scripts/build_animation_candidate.py` to require a valid SHA-verified **approved** master reference before exporting a candidate. The lock is optional for synthetic development tests, but must be supplied when preparing actual character artwork for review. A reference lock approval does **not** approve the generated animation candidate. Sprite silhouette occupancy and palette color-count outliers are now reported alongside the existing motion diagnostics.
