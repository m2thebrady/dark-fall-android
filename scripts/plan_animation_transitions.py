#!/usr/bin/env python3
"""Plan and validate explicit animation state changes without touching game runtime."""
import argparse,json
from pathlib import Path
def plan(profile,sequence):
    actions=profile["actions"]
    if not isinstance(sequence,list) or not sequence:raise ValueError("sequence must be nonempty array")
    result=[]
    for i,entry in enumerate(sequence):
        if not isinstance(entry,dict):raise ValueError(f"step {i} must be object")
        action=entry.get("action")
        if action not in actions:raise ValueError(f"step {i}: unknown action {action}")
        cycles=entry.get("cycles",1)
        if type(cycles) is not int or not 1<=cycles<=20:raise ValueError(f"step {i}: cycles out of range")
        fps=actions[action]["fps"]
        result.append({"action":action,"fps":fps,"cycles":cycles,"loop":actions[action]["loop"],"transition_from":sequence[i-1]["action"] if i else None})
    return result
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path)
    parser.add_argument("sequence",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        result=plan(json.loads(args.profile.read_text()),json.loads(args.sequence.read_text()))
        payload=json.dumps({"character":args.profile.stem,"transitions":result},indent=2)+"\n"
        if args.output:
            if args.output.exists():raise FileExistsError("refusing to overwrite output")
            args.output.write_text(payload)
        else:print(payload)
    except (ValueError,OSError) as exc:parser.error(str(exc))
if __name__=="__main__":main()
