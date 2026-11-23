#!/usr/bin/env python3
from animation_state import choose_action,transition
actions={"idle":[0],"run":[1],"run_cast":[2],"cast":[3],"hit":[4],"death":[5]}
assert choose_action(actions,moving=True)=="run"
assert choose_action(actions,moving=True,casting=True)=="run_cast"
assert choose_action(actions,moving=True,casting=True,hit=True)=="hit"
assert choose_action(actions,moving=True,dead=True)=="death"
assert choose_action(actions,casting=True)=="cast"
assert choose_action(actions)=="idle"
assert transition(actions,"idle","run",[["idle","run"]])=="run"
assert transition(actions,"idle","cast",[["idle","run"]])=="idle"
try:
    transition(actions,"idle","missing")
    raise AssertionError("Unknown action accepted")
except ValueError:
    pass
print("Animation state transition tests passed")
