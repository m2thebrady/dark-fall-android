// Gardens are part of the master ground atlas. The old plot surfaces are
// restored before rebaking; no new decorations enter the sorted draw queue.
const rh1537ReviewPoints={...rh1526Gardens.review,merchant:[2450,2246]};
function rh1537GardenStatus(full=false){
 const roads=full?[...rh1521Plan.roads.map(r=>({points:r.points,half:r.width/2})),...rh1524Landscape.links.map(r=>({points:r.points,half:r.width/2}))]:[];
 const plots=rh1537Meta.plots.map(g=>{
  let samples=0,bad=0,margin=Infinity;
  if(full){
   for(let x=g.x-g.w/2+3;x<g.x+g.w/2;x+=7)for(let y=g.y-g.h/2+3;y<g.y+g.h/2;y+=7){samples++;if(blocked(x,y))bad++;}
   for(const x of [g.x-g.w/2,g.x,g.x+g.w/2])for(const y of [g.y-g.h/2,g.y,g.y+g.h/2])for(const r of roads)margin=Math.min(margin,rh1473Distance(x,y,r.points)-r.half);
  }
  return {name:g.name,variant:g.variant,position:[g.x,g.y],size:[g.w,g.h],old:g.old,
   expanded:g.w>g.old[2]||g.h>g.old[3],relocated:g.x!==g.old[0]||g.y!==g.old[1],
   samples:full?samples:null,bad:full?bad:null,clearance:full?Math.round(margin*10)/10:null,centerClear:full?!blocked(g.x,g.y):null};
 });
 return {version:1537,plots,variants:rh1537Meta.variants,expanded:plots.filter(g=>g.expanded).length,relocated:plots.filter(g=>g.relocated).length,
  bakedTiles:rh1537Meta.tiles.map(t=>t.key),visible:rh1521Status().tiles,
  routes:full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  links:full?rh1524Landscape.links.map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  review:Object.entries(rh1537ReviewPoints).map(([key,xy])=>({key,xy,clear:full?!blocked(...xy):null})),
  additionalDraws:0,newColliders:0,npcChanges:0};
}
function rh1537Review(key){
 const xy=rh1537ReviewPoints[key];if(!xy||blocked(...xy))return false;[p.x,p.y]=xy;rh199Reset();return true;
}
