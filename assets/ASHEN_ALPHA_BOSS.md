# Ashen Alpha — boss asset production specification

## Design lock

Approved visual direction: **Revised Concept 1**. Muscular charcoal-gray wolf, shorter natural fur without an oversized mane, amber eyes, dark claws, scars. Keep the silhouette and eye color stable across all actions. The original approved image and preliminary alpha-cutout are in the separately exported asset pack, not in GitHub's text-only catalog.

## Motion contract

| Action | Target frames | Playback | Key requirement |
|---|---:|---:|---|
| Idle | 16 | 8 fps loop | Quiet breathing and subtle head motion; planted paws |
| Walk | 24 | 12 fps loop | Four-beat gait; no paw sliding |
| Run | 24 | 14 fps loop | Extended stride and suspension; correct rear/front foot timing |
| Attack | 32 | 16 fps | Anticipation, bite/claw, impact, recovery |
| Run-attack | 32 | 16 fps | Keep locomotion and attack synchronized |
| Hit | 16 | 12 fps | Brief restrained recoil, no scale jumps |
| Death | 32 | 12 fps | Legs give way, shoulder/torso contact, head settles |
| Corpse | 1 | static | Same final silhouette as death, no twitching |

Total planned: **177** artwork frames. This is a production target, not a claim that the frames exist.

## Implementation gates

- Alpha edges clean, all interior body pixels opaque; no white checkerboard pixels or color holes.
- Same facing direction, character identity, frame size, visual scale and ground anchor.
- Each limb has coherent foot-contact phases; independent front and hind leg motion.
- Motion loops close smoothly, attacks return to locomotion, death settles to exactly the corpse image.
- Frames padded and visually reviewed in isolation at game display scale.
- Keep boss independent from existing wolves. **After** art approval, spawn near first-zone entry and protect existing regular-wolf behavior.
- Preserve playable V994 until isolated boss test and rollback are ready.

**State:** concept approved, preliminary master-art extraction prepared externally, animation frames not yet produced, gameplay integration not started.
