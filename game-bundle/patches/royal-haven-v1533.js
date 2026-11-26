// Mild clarity correction is already baked into the asset bytes. The only
// runtime change is the existing adaptive canvas size and its recovery order.
function rh1533Status(full=false){
 const a=rh1521Status(false),images={rh1444Art,rh1446Art,rh1447Art,rh1448Art,rh1449Art,rh1450Art};
 return {version:1533,facades:rh1533Meta.facades.map(o=>({key:o.key,width:o.width,height:o.height,
  alphaPreserved:o.alphaPreserved,ready:!!images[o.key]?.complete&&images[o.key].naturalWidth===o.width&&images[o.key].naturalHeight===o.height})),
  ground:rh1533Meta.ground.map(o=>o.key),visible:a.tiles,scales:rh1431Scales.slice(),
  tier:rh1431Perf.tier,slow:rh1431Perf.slow,target:rh1431Perf.slow?30:60,backing:[cv.width,cv.height],zoom:rh1519Zoom,
  emergencyScalePreserved:rh1431Scales[2]===.70,extraFrameFilters:0,extraDraws:0,
  newColliders:0,npcChanges:0,
  paths:full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  gardenClear:full?rh1526Gardens.gardens.every(g=>!blocked(g.x,g.y)):null};
}
function rh1533ResolutionProbe(){
 const snapshot={...rh1523TimingStats},q=rh1523State(2);let t=1;
 function phase(ms,step,cost){for(let elapsed=0;elapsed<ms;elapsed+=step){t+=step;rh1523Observe(q,t,cost);}return {tier:q.tier,slow:q.slow,cost:q.cost,raf:q.raf};}
 try{
  // Moderate 30-Hz render cost with 60-Hz input cadence permits clearer
  // medium resolution, but not higher frame rate or full resolution yet.
  const medium=phase(7200,1000/60,12);
  const full=phase(7200,1000/60,7);
  const fast=phase(7200,1000/60,7);
  const emergency=phase(3200,50,38);
  return {medium,full,fast,emergency};
 }finally{Object.assign(rh1523TimingStats,snapshot);}
}
