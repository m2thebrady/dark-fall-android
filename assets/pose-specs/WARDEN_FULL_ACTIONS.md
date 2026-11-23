# Warden full-action blockout

Generate all seven actions in one offline command:

```bash
python3 scripts/build_warden_action_blockout.py assets/profiles/warden.json assets/pose-specs/warden-guide.json /tmp/warden-motion-blockout
```

The tool produces per-action JSON landmark sequences, eight-frame contact sheets, and a summary with the action budget and diagnostic counts. It refuses to overwrite an existing output directory.

| Action | Frames | Intent |
|---|---:|---|
| Idle | 16 | Quiet breathing and grounded stance |
| Run | 32 | Restrained stride; stable club |
| Attack | 32 | Controlled heavy club arc |
| Cast | 24 | Measured healing gesture |
| Run-cast | 32 | Continue moving while healing |
| Hit | 16 | Small shoulder/torso recoil |
| Death | 24 | Restrained fall blockout |
| **Total** | **176** | Provisional motion budget |

These are **anatomical guides**, not finished character artwork. The current provisional landmark set does not depict a realistic full-body fall and should not be mistaken for approved poses. The next step is attaching actual approved painted character parts, revising any anatomical shortcomings with an artist, and inspecting complete animated action sets before gameplay integration. No changes to V994.
