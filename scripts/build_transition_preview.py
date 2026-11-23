#!/usr/bin/env python3
"""Generate a standalone, offline animation-transition preview from validated assets."""
import argparse,base64,html,json
from pathlib import Path
from plan_animation_transitions import plan
from validate_asset import validate

def build(profile_path,manifest_path,sequence_path,output):
    profile=json.loads(Path(profile_path).read_text())
    manifest=json.loads(Path(manifest_path).read_text())
    transitions=plan(profile,json.loads(Path(sequence_path).read_text()))
    validate(manifest_path)
    image_path=(Path(manifest_path).resolve().parent/manifest["image"]).resolve()
    if Path(output).exists():raise FileExistsError("Refusing to overwrite preview")
    mime="image/png" if image_path.suffix.lower()==".png" else "image/webp"
    data="data:"+mime+";base64,"+base64.b64encode(image_path.read_bytes()).decode()
    payload=json.dumps({"manifest":manifest,"transitions":transitions,"image":data}).replace("<","\\u003c")
    page="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dark Fall — Action Sequence Preview</title><style>body{font:16px system-ui;background:#1d2124;color:#e6e6df;margin:20px}canvas{background:#333a3e;image-rendering:pixelated;max-width:100%;border:1px solid #666}button{padding:8px;margin:5px}</style>
<h1>Dark Fall — Action Sequence Preview</h1><p>Offline sprite-sheet preview. Not integrated into the game.</p>
<canvas id="stage" width="400" height="300"></canvas><p id="status"></p><button id="toggle">Pause</button><button id="restart">Restart</button>
<script id="payload" type="application/json">PAYLOAD</script>
<script>
const data=JSON.parse(document.getElementById('payload').textContent);
const m=data.manifest,steps=data.transitions,canvas=document.getElementById('stage'),ctx=canvas.getContext('2d');
ctx.imageSmoothingEnabled=false;const img=new Image();img.src=data.image;
let step=0,frame=0,cycles=0,last=0,paused=false,finished=false;
function draw(){
ctx.clearRect(0,0,canvas.width,canvas.height);
const state=steps[step],indices=m.actions[state.action],index=indices[frame];
const sx=(index%m.columns)*m.frame_width,sy=Math.floor(index/m.columns)*m.frame_height;
const scale=Math.min(2,canvas.width/m.frame_width,canvas.height/m.frame_height);
ctx.drawImage(img,sx,sy,m.frame_width,m.frame_height,(canvas.width-m.frame_width*scale)/2,(canvas.height-m.frame_height*scale)/2,m.frame_width*scale,m.frame_height*scale);
document.getElementById('status').textContent=state.action+' — frame '+(frame+1)+'/'+indices.length+' — step '+(step+1)+'/'+steps.length+(finished?' (finished)':'');
}
function tick(time){
if(img.complete&&img.naturalWidth){
 if(!paused&&!finished&&time-last>=1000/steps[step].fps){
 last=time;frame++;
 if(frame>=m.actions[steps[step].action].length){frame=0;cycles++;if(cycles>=steps[step].cycles){cycles=0;step++;if(step>=steps.length){step=steps.length-1;frame=m.actions[steps[step].action].length-1;finished=true}}}
 }
 draw();
}
requestAnimationFrame(tick)}
document.getElementById('toggle').onclick=()=>{paused=!paused;document.getElementById('toggle').textContent=paused?'Resume':'Pause'};
document.getElementById('restart').onclick=()=>{step=0;frame=0;cycles=0;finished=false;last=performance.now()};
img.onload=()=>requestAnimationFrame(tick);
</script></html>""".replace("PAYLOAD",payload)
    Path(output).write_text(page)
    return {"steps":len(transitions),"output":str(output)}
def main():
    parser=argparse.ArgumentParser()
    for name in ("profile","manifest","sequence","output"):parser.add_argument(name,type=Path)
    a=parser.parse_args()
    print(json.dumps(build(a.profile,a.manifest,a.sequence,a.output),indent=2))
if __name__=="__main__":main()
