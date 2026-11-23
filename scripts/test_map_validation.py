#!/usr/bin/env python3
import copy
import json
from pathlib import Path
from validate_map import validate
base=json.loads(Path("maps/woodland-approach.json").read_text())
assert not validate(base),validate(base)
def bad(modifier,term):
    sample=copy.deepcopy(base)
    modifier(sample)
    errors=validate(sample)
    assert any(term in e for e in errors),(term,errors)
bad(lambda x:x["objects"].append(copy.deepcopy(x["objects"][0])),"duplicate")
bad(lambda x:x["objects"][0].update(x=-10),"outside map")
bad(lambda x:x["objects"][0].update(x=500,y=200),"overlaps solid")
bad(lambda x:x["objects"].pop(),"at least one exit")
bad(lambda x:x["objects"][0].update(width=0),"dimensions must be positive")
bad(lambda x:x["objects"][0].update(type="dragon"),"type invalid")
print("Map validation tests passed")
