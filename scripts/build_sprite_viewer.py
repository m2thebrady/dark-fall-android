#!/usr/bin/env python3
"""Create a standalone HTML animation preview for an asset overlay.

This viewer is intentionally independent of Dark Fall's production renderer.
It cannot change the bundled game and does not claim runtime integration.
"""
import argparse,html,json,shutil
from pathlib import Path
from check_asset_overlay import check_overlay

VIEWER="""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dark Fall — Experimental Sprite Viewer</title>
<style>body{font:16px system-ui;background:#181b1c;color:#f2f2ec;margin:20px}
canvas{background:#303438;image-rendering:pixelated;border:1px solid #707b7b;max-width:100%}
label{display:block;margin:12px 0}select,button{font:inherit;padding:7px}
small{color:#b8c3c2}</style></head><body>
<h1>Dark Fall — Experimental Sprite Viewer</h1>
<p><small>Isolated asset preview. Does not replace sprites in the game.</small></p>
<label>Asset <select id="asset"></select></label>
<label>Action <select id="action"></select></label>\n<label>Playback <button id="pause">Pause</button> <button id="step">Next frame</button></label>\n<label>Simulated state <select id="state"><option value="manual">Manual</option><option value="idle">Idle</option><option value="run">Moving</option><option value="cast">Casting</option><option value="run_cast">Moving + Casting</option><option value="attack">Attacking</option><option value="run_attack">Moving + Attacking</option><option value="hit">Taking damage</option><option value="death">Death</option></select></label>\n<label>Speed <select id="speed"><option value="4">4 fps</option><option value="8">8 fps</option><option value="10" selected>10 fps</option><option value="15">15 fps</option><option value="24">24 fps</option></select></label>
<canvas id="stage" width="320" height="320"></canvas>\n<label><input id="guides" type="checkbox" checked> Show frame bounds and feet anchor</label>\n<label><input id="onion" type="checkbox"> Show previous frame ghost</label>
<p id="status" role="status"></p>
<script>
(async()=>{
const registry=await (await fetch('./registry.json')).json();
const assetSelect=document.getElementById('asset');
const actionSelect=document.getElementById('action');
const canvas=document.getElementById('stage');
const ctx=canvas.getContext('2d');
ctx.imageSmoothingEnabled=false;
let manifest,image,action='idle',start=performance.now(),paused=false,pausedIndex=0,fps=10;
for(const id of Object.keys(registry.assets)){const option=document.createElement('option');option.value=id;option.textContent=id;assetSelect.append(option)}
async function loadAsset(){
 const entry=registry.assets[assetSelect.value];
 if(!entry){document.getElementById('status').textContent='No assets selected';return}
 manifest=await (await fetch(entry.manifest)).json();
 image=new Image();image.src=entry.image;await image.decode();
 actionSelect.replaceChildren();
 for(const name of Object.keys(manifest.actions)){const option=document.createElement('option');option.value=name;option.textContent=name;actionSelect.append(option)}
 action=actionSelect.value;start=performance.now();pausedIndex=0;pausedIndex=0;
}
assetSelect.addEventListener('change',()=>loadAsset().catch(showError));
actionSelect.addEventListener('change',()=>{action=actionSelect.value;start=performance.now()});
document.getElementById('pause').addEventListener('click',()=>{
 paused=!paused;
 document.getElementById('pause').textContent=paused?'Resume':'Pause';
 if(!paused){start=performance.now()-pausedIndex*1000/fps}
});
document.getElementById('step').addEventListener('click',()=>{
 paused=true;document.getElementById('pause').textContent='Resume';
 const frames=manifest?.actions[action];
 if(frames?.length)pausedIndex=(pausedIndex+1)%frames.length;
});
document.getElementById('speed').addEventListener('change',event=>{
 fps=Number(event.target.value);start=performance.now()-pausedIndex*1000/fps;
});
document.getElementById('state').addEventListener('change',event=>{
 if(!manifest)return;
 const requested=event.target.value;
 if(requested==='manual')return;
 const actions=manifest.actions;
 const fallback={run_cast:['run_cast','cast','run','idle'],run_attack:['run_attack','attack','run','idle'],run:['run','idle'],cast:['cast','idle'],attack:['attack','idle'],hit:['hit','idle'],death:['death','idle'],idle:['idle']};
 const chosen=(fallback[requested]||['idle']).find(name=>actions[name]);
 if(chosen){actionSelect.value=chosen;action=chosen;pausedIndex=0;start=performance.now()}
});
function showError(error){document.getElementById('status').textContent=String(error)}
function draw(now){
 requestAnimationFrame(draw);
 if(!manifest||!image)return;
 const frames=manifest.actions[action];
 if(!frames||!frames.length)return;
 const fps=10;
 const position=paused?pausedIndex:Math.floor((now-start)*fps/1000)%frames.length;
 if(!paused)pausedIndex=position;
 const index=frames[position];
 const w=manifest.frame_width,h=manifest.frame_height;
 const sx=(index%manifest.columns)*w,sy=Math.floor(index/manifest.columns)*h;
 ctx.clearRect(0,0,canvas.width,canvas.height);
 const scale=Math.min(4,Math.floor(Math.min(canvas.width/w,canvas.height/h)));
 const dx=(canvas.width-w*scale)/2,dy=(canvas.height-h*scale)/2;
 if(document.getElementById('onion').checked&&frames.length>1){
   const prev=frames[(position+frames.length-1)%frames.length];
   const px=(prev%manifest.columns)*w,py=Math.floor(prev/manifest.columns)*h;
   ctx.globalAlpha=0.25;ctx.drawImage(image,px,py,w,h,dx,dy,w*scale,h*scale);ctx.globalAlpha=1;
 }
 ctx.drawImage(image,sx,sy,w,h,dx,dy,w*scale,h*scale);
 if(document.getElementById('guides').checked){
   ctx.strokeStyle='#f3d36b';ctx.lineWidth=1;ctx.strokeRect(dx,dy,w*scale,h*scale);
   const anchor=manifest.anchors?.[String(index)]?.feet;
   if(Array.isArray(anchor)&&anchor.length===2){
     const ax=dx+anchor[0]*scale,ay=dy+anchor[1]*scale;
     ctx.strokeStyle='#50e8a4';ctx.beginPath();ctx.moveTo(ax-6,ay);ctx.lineTo(ax+6,ay);ctx.moveTo(ax,ay-6);ctx.lineTo(ax,ay+6);ctx.stroke();
   }
 }
 document.getElementById('status').textContent=assetSelect.value+' / '+action+' / frame '+index;
}
await loadAsset();requestAnimationFrame(draw);
})().catch(error=>document.getElementById('status').textContent=String(error));
</script></body></html>"""

def build(overlay,output):
    overlay=Path(overlay).resolve()
    check_overlay(overlay)
    output=Path(output).resolve()
    if output==overlay or overlay in output.parents or output in overlay.parents:
        raise ValueError("Output and source must be separate")
    if output.exists():
        raise ValueError("Output directory already exists")
    shutil.copytree(overlay,output)
    (output/"index.html").write_text(VIEWER,encoding="utf-8")
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("overlay")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    print(build(args.overlay,args.output))
