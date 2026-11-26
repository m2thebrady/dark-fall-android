// Reposition only the three old decorative racks that intersected the master
// street corridors. All existing soft-object references and physics survive.
let rh1538Installed=false;
const rh1538ReviewPoints={observatory:[3092,870],east:[5220,2075],craft:[4196,1920],south:[3500,2350]};
function rh1538Install(){
 const items=rh1538Meta.moves.map(m=>rh194Props.find(o=>o.k===m.k&&o.x===m.old[0]&&o.y===m.old[1]));
 if(items.some(o=>!o||!rh1519Soft.has(o)))return false;
 for(let i=0;i<items.length;i++){
  const o=items[i],m=rh1538Meta.moves[i],d=rh1519Decor.find(v=>v.k===o.k&&v.x===o.x&&v.y===o.y);
  [o.x,o.y]=m.new;
  if(d)[d.x,d.y]=m.new;
 }
 // The observatory tabletop has a deeper silhouette than the former flat
 // table. Height is adjusted to preserve legible object scale, not its physics.
 const table=rh194Props.find(o=>o.k==='arcaneTable');
 if(table)table.h=65;
 // The artisan's old wood rack never supplied a variant index. The restored
 // rack now renders with the correct pre-existing contact and projection logic.
 const artisan=rh194Props.find(o=>o.artisan1495&&o.k==='houseWood');
 if(artisan&&!rh1423HouseProps.includes(artisan))rh1423HouseProps.push(artisan);
 rh1538Installed=true;return true;
}
function rh1538FixtureStatus(full=false){
 const local=[...rh194Props,...rh1465Props].filter(o=>['houseWood','houseRack','armillary','arcaneTable'].includes(o.k));
 const image=o=>o.k==='houseWood'||o.k==='houseRack'?rh1423HouseImage(o,0,false):rh1417Art[o.k];
 const roads=full?[...rh1521Plan.roads.map(r=>({points:r.points,half:r.width/2})),...rh1524Landscape.links.map(r=>({points:r.points,half:r.width/2}))]:[];
 function clearance(o,foot=false){let d=Infinity;for(const x of (foot?[o.x-o.rx,o.x,o.x+o.rx]:[o.x]))for(const y of (foot?[o.y-o.ry,o.y,o.y+o.ry]:[o.y]))for(const r of roads)d=Math.min(d,rh1473Distance(x,y,r.points)-r.half);return Math.round(d*10)/10;}
 const instances=local.map(o=>({k:o.k,position:[o.x,o.y],variant:o.variant,soft:rh1519Soft.has(o),ready:!!image(o)?.complete&&image(o).naturalWidth>0,
  roadClearance:full?clearance(o):null,centerClear:full?!blocked(o.x,o.y):null}));
 const models=rh1538Meta.models.map(m=>{const im=rh1423HouseArt[m.key]||rh1417Art[m.key];return {key:m.key,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height};});
 const frames=Array.from({length:2},(_,v)=>Array.from({length:8},(_,f)=>rh1423HouseArt['rack'+v+'_'+f])).flat();
 const moves=rh1538Meta.moves.map(m=>{
  const o=local.find(q=>q.k===m.k&&q.x===m.new[0]&&q.y===m.new[1]);
  let samples=0,bad=0;
  if(full&&o)for(let x=o.x-o.rx-5;x<=o.x+o.rx+5;x+=7)for(let y=o.y-o.ry-5;y<=o.y+o.ry+5;y+=7){samples++;if(blocked(x,y))bad++;}
  return {...m,located:!!o,soft:!!o&&rh1519Soft.has(o),oldClear:full?!blocked(...m.old):null,
   clearance:full&&o?clearance(o,true):null,samples:full?samples:null,bad:full?bad:null,
   gardenOverlap:!!o&&rh1537Meta.plots.some(g=>Math.abs(g.x-o.x)<g.w/2+o.rx&&Math.abs(g.y-o.y)<g.h/2+o.ry)};
 });
 const artisan=local.find(o=>o.artisan1495&&o.k==='houseWood');
 return {version:1538,installed:rh1538Installed,models,instances,moves,
  frameSlots:frames.length,uniqueLaundryFrames:new Set(frames).size,allFramesReady:frames.every(im=>!!im?.complete&&im.naturalWidth>0),
  fixedArtisan:!!artisan&&artisan.variant===2,lanternCount:rh117Props.filter(o=>o.k==='lamp').length,
  routes:full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  links:full?rh1524Landscape.links.map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  review:Object.entries(rh1538ReviewPoints).map(([key,xy])=>({key,xy,clear:full?!blocked(...xy):null})),
  additionalDrawLayers:0,newColliders:0,npcChanges:0,lanternChanges:0};
}
function rh1538Review(key){const xy=rh1538ReviewPoints[key];if(!xy||blocked(...xy))return false;[p.x,p.y]=xy;rh199Reset();return true;}
