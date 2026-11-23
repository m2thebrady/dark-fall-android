#!/usr/bin/env python3
"""Compare an animation manifest's actions to its intended body profile."""
import argparse,json
from pathlib import Path
def check(profile,manifest):
    errors=[]
    actions=manifest.get("actions")
    if not isinstance(actions,dict):return ["manifest actions must be an object"]
    for action in profile["actions"]:
        if action not in actions:errors.append(f"missing action: {action}")
        elif not isinstance(actions[action],list) or not actions[action]:errors.append(f"empty action: {action}")
    for action in actions:
        if action not in profile["actions"]:errors.append(f"unexpected action: {action}")
    if manifest.get("frame_width")!=profile["frame"]["width"]:errors.append("frame width mismatch")
    if manifest.get("frame_height")!=profile["frame"]["height"]:errors.append("frame height mismatch")
    return errors
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path)
    parser.add_argument("manifest",type=Path)
    a=parser.parse_args()
    errors=check(json.loads(a.profile.read_text()),json.loads(a.manifest.read_text()))
    for error in errors:print(error)
    if errors:raise SystemExit(1)
    print("Animation coverage passed")
if __name__=="__main__":main()
