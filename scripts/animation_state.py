"""Pure animation-state transition logic for standalone preview tooling.

A runtime adapter can later reuse this policy; no game logic is modified.
"""
def transition(actions, current, requested, allowed=None):
    if requested not in actions:
        raise ValueError(f"Unknown action: {requested}")
    if current is None:
        return requested
    if current not in actions:
        raise ValueError(f"Unknown current action: {current}")
    if current==requested:
        return current
    if allowed is not None and [current,requested] not in allowed:
        return current
    return requested

def choose_action(actions, moving=False, attacking=False, casting=False, hit=False, dead=False):
    priorities=(
        (dead, "death"),
        (hit, "hit"),
        (attacking and moving, "run_attack"),
        (casting and moving, "run_cast"),
        (attacking, "attack"),
        (casting, "cast"),
        (moving, "run"),
    )
    for active,action in priorities:
        if active and action in actions:
            return action
    return "idle" if "idle" in actions else next(iter(actions))
