// A visual reconstruction of the old perimeter watchtowers. Installation
// follows the existing town layout generation, so unrelated lots and trees
// are not re-rolled when the expanded eastern boundary is corrected.
const rh1534OriginalTowers=[];
const rh1534ReviewPoints={west:[205,855],south:[4980,2395],eastNorth:[6200,850],eastSouth:[6220,1660],former:[5676,1630]};
function rh1534Install(){
 for(const o of rh1335FortTowers){
  rh1534OriginalTowers.push({x:o.x,y:o.y,w:o.w,h:o.h,rx:o.rx,ry:o.ry,k:o.k});
  const m=rh1534Meta.towers[o.k],move=rh1534Meta.moves.find(a=>a.fromX===o.x&&a.y===o.y);
  // Uniform scaling at the existing base width, not squashing the new roof.
  o.h=Math.round(o.w*m.height/m.width);
  if(move)o.x=move.toX;
 }
}
function rh1534TowerStatus(full=false){
 const a=rh1521Status(false);
 return {version:1534,models:rh1534Meta.towers.map((m,i)=>({key:m.key,name:m.name,width:m.width,height:m.height,
  ready:!!rh1335TowerArt[i]?.complete&&rh1335TowerArt[i].naturalWidth===m.width&&rh1335TowerArt[i].naturalHeight===m.height})),
  towers:rh1335FortTowers.map((o,i)=>{const prior=rh1534OriginalTowers[i],m=rh1534Meta.towers[o.k];return {
   x:o.x,y:o.y,w:o.w,h:o.h,k:o.k,previousX:prior.x,previousH:prior.h,rx:o.rx,ry:o.ry,
   footprintPreserved:o.w===prior.w&&o.rx===prior.rx&&o.ry===prior.ry,baseFits:m.baseWidthFraction*o.w>=2*o.rx,
   naturalAspect:Math.abs(o.h-o.w*m.height/m.width)<=.51,solid:full?blocked(o.x,o.y-20):null};}),
  moved:rh1534Meta.moves.map(m=>({from:[m.fromX,m.y],to:[m.toX,m.y],oldCenterOpen:full?!blocked(m.fromX,m.y-20):null,
   newCenterSolid:full?blocked(m.toX,m.y-20):null,
   crossing:full?rh1513PathCheck([[m.fromX-35,m.y-20],[m.fromX+35,m.y-20]],7):null})),
  review:Object.entries(rh1534ReviewPoints).map(([key,xy])=>({key,xy,clear:full?!blocked(...xy):null})),
  easternWallX:WORLD_W-84,visible:a.tiles,paths:full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  changedCollisionCount:0,additionalDraws:0,npcChanges:0};
}
function rh1534Review(key){
 const xy=rh1534ReviewPoints[key];if(!xy||blocked(...xy))return false;[p.x,p.y]=xy;rh199Reset();return true;
}
