#!/usr/bin/env python3
"""Compile approved asset manifests into runtime-safe metadata without changing the game."""
import argparse,json
from pathlib import Path
from validate_asset_catalog import validate

def compile_catalog(catalog):
    issues=validate(catalog)
    if issues:raise ValueError("; ".join(issues))
    result={"schema_version":1,"assets":{},"excluded":{}}
    for asset in catalog["assets"]:
        if asset["status"]!="approved":
            result["excluded"][asset["id"]]=f"not approved ({asset['status']})"
            continue
        result["assets"][asset["id"]]={"family":asset["family"],"kind":asset["kind"],"frame":asset["frame"],"actions":asset["actions"],"revision":asset["approved_revision"]}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("catalog",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Refusing to overwrite runtime manifest")
    data=compile_catalog(json.loads(a.catalog.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2)+"\n")
    print(f"Compiled {len(data['assets'])} approved assets; excluded {len(data['excluded'])}")
if __name__=="__main__":main()
