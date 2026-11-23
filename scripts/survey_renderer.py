#!/usr/bin/env python3
"""Read-only survey of legacy game renderer source and sprite references.

Produces bounded line-context excerpts without modifying the huge HTML.
"""
import argparse, json, re
from pathlib import Path
PATTERNS={
    "sprite_drawing":r"drawImage\s*\(",
    "canvas_context":r"getContext\s*\(",
    "frame_indexing":r"frameIndex|animFrame|spriteFrame|frameCount",
    "animation_state":r"animationState|animState|currentAnim|\.animation\b",
    "sprite_loading":r"new\s+Image\s*\(|\.src\s*=\s*['\x22]data:image",
    "class_names":r"\b(?:Warden|Caster|Fighter)\b",
}
def survey(source, limit=12):
    content=Path(source).read_text(encoding="utf-8")
    lines=content.splitlines()
    results={}
    for name,pattern in PATTERNS.items():
        regex=re.compile(pattern,re.I)
        hits=[]
        total=0
        for i,line in enumerate(lines,1):
            matches=list(regex.finditer(line))
            total+=len(matches)
            if matches and len(hits)<limit:
                excerpt=line[:240] if len(line)<240 else line[max(0,matches[0].start()-70):matches[0].start()+170]
                hits.append({"line":i,"excerpt":excerpt})
        results[name]={"occurrences":total,"examples":hits}
    return {"source":str(source),"lines":len(lines),"categories":results}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="app/src/main/assets/index.html")
    p.add_argument("--output",default="browser-smoke-results/renderer-survey.json")
    args=p.parse_args()
    result=survey(args.source)
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v["occurrences"] for k,v in result["categories"].items()},indent=2))
