#!/usr/bin/env python3
import json
from pathlib import Path
from plan_animation_transitions import plan
profile=json.loads(Path("assets/profiles/warden.json").read_text())
sequence=[{"action":"idle"},{"action":"run","cycles":3},{"action":"attack"},{"action":"hit"},{"action":"death"}]
result=plan(profile,sequence)
assert [x["action"] for x in result]==["idle","run","attack","hit","death"]
assert result[1]["transition_from"]=="idle" and result[1]["cycles"]==3
assert result[2]["fps"]==profile["actions"]["attack"]["fps"]
for invalid in [[{"action":"unknown"}],[{"action":"idle","cycles":0}],[],[{"action":"run","cycles":1.5}]]:
    try:plan(profile,invalid)
    except ValueError:pass
    else:raise AssertionError(f"accepted {invalid}")
print("Animation transition planning tests passed")
