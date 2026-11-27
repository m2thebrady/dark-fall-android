// V1542: retire legacy raised beds from the commercial lanes. Their
// furniture/physics entries are removed together; keep all civic and verge gardens.
const rh1542Retired=[],rh1542GardenBindings=new WeakMap(),rh1542GardenPlacements=[];
function rh1542Install(){
 const objects=rh1542Meta.removed.map(m=>rh170Gardens.find(o=>o.x===m.x&&o.y===m.y&&o.w===m.w&&o.h===m.h));
 if(objects.some(o=>!o)||new Set(objects).size!==rh1542Meta.removed.length)return false;
 for(const o of objects)rh1542Retired.push({x:o.x,y:o.y,w:o.w,h:o.h,wasBlocked:blocked(o.x,o.y)});
 for(const o of objects)rh170Gardens.splice(rh170Gardens.indexOf(o),1);
 for(const m of rh1542Meta.placements){
  const o=rh170Gardens.find(o=>o.x===m.x&&o.y===m.y);
  if(o&&rh1542Art[m.key]){rh1542GardenBindings.set(o,m.key);rh1542GardenPlacements.push({o,key:m.key});}
 }
 return true;
}
function rh1542GardenImage(o){
 const key=rh1542GardenBindings.get(o),im=key&&rh1542Art[key];
 return im?.complete&&im.naturalWidth>0?im:null;
}
function rh1542ReviewPoint(r){
 const [x,y]=r.review;
 for(const d of [0,12,24,36,48,60,72,90]){
  for(const [dx,dy] of [[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]]){
   const a=x+dx*d,b=y+dy*d;
   if([-7,0,7].every(u=>[-7,0,7].every(v=>!blocked(a+u,b+v))))return [a,b];
  }
 }
 return null;
}
function rh1542Status(full=false){
 const models=rh1542Meta.models.map(m=>({...m,ready:rh1542Art[m.key].complete&&rh1542Art[m.key].naturalWidth===m.width&&rh1542Art[m.key].naturalHeight===m.height,
  instances:rh1542GardenPlacements.filter(a=>a.key===m.key).length}));
 const gardens=rh1542GardenPlacements.map(({o,key})=>({key,x:o.x,y:o.y,w:o.w,h:o.h,solid:full?blocked(o.x,o.y):null,ready:rh1542GardenImage(o)===rh1542Art[key],visualH:rh1542GardenImage(o)?o.w*rh1542Art[key].naturalHeight/rh1542Art[key].naturalWidth:null}));
 const retired=rh1542Retired.map(o=>{
  let samples=0,bad=0;
  if(full){
   for(let x=o.x-o.w/2+4;x<=o.x+o.w/2-4;x+=7)for(let y=o.y-o.h/2+4;y<=o.y+o.h/2-4;y+=7){samples++;if(blocked(x,y))bad++;}
  }
  return {...o,centerClear:full?!blocked(o.x,o.y):null,samples,bad,
   horizontal:full?rh1513PathCheck([[o.x-o.w/2,o.y],[o.x+o.w/2,o.y]],7):null,
   vertical:full?rh1513PathCheck([[o.x,o.y-o.h/2],[o.x,o.y+o.h/2]],7):null};
 });
 return {version:1542,models,gardens,retired,remainingGardens:rh170Gardens.length,
  regions:rh1542Meta.regions.map(r=>({name:r.name,tiles:r.tileKeys,surfacePixels:r.surfacePixels,nonRepeatingQuilt:r.nonRepeatingQuilt,review:full?rh1542ReviewPoint(r):r.review})),
  bakedTiles:rh1542Meta.ground.map(m=>m.key),
  routes:full?rh1521Plan.roads.filter(o=>o.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  links:full?rh1524Landscape.links.map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  sortedDrawObjectsRemoved:retired.length,additionalDrawLayers:0,newColliders:0,npcChanges:0};
}
function rh1542Review(index){
 const r=rh1542Meta.regions[index],xy=r&&rh1542ReviewPoint(r);if(!xy)return false;[p.x,p.y]=xy;rh199Reset();return true;
}
