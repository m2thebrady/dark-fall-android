#!/usr/bin/env python3
import copy,json,tempfile
from pathlib import Path
from validate_asset_catalog import validate
from compile_asset_manifest import compile_catalog
catalog=json.loads(Path("assets/catalog.json").read_text())
assert validate(catalog)==[]
assert len(catalog["assets"])>=8
compiled=compile_catalog(catalog)
assert not compiled["assets"]
assert len(compiled["excluded"])==len(catalog["assets"])
test=copy.deepcopy(catalog)
test["assets"][0]["status"]="approved"
test["assets"][0]["approved_revision"]="sha256:test-fixture-only"
assert validate(test)==[]
compiled=compile_catalog(test)
assert "fighter" in compiled["assets"]
bad=copy.deepcopy(catalog);bad["assets"][1]["id"]=bad["assets"][0]["id"]
assert any("duplicate id" in x for x in validate(bad))
bad=copy.deepcopy(catalog);bad["assets"][0]["actions"]["idle"]["frames"]=0
assert any("invalid frame count" in x for x in validate(bad))
print("Universal asset catalog tests passed")
