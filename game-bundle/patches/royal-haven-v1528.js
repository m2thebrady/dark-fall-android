// Retire disconnected fragments, not the city's structural walls.
// Paving is incorporated into the existing terrain chunks and costs no draw passes.
const rh1528Cleared=[];
function rh1528Groups(){return [
 ['artisan',rh1459Walls],['residential',rh1463Walls],['court',rh1465Walls],['lantern',rh1468Walls]
];}
function rh1528Install(){
 for(const [group,list] of rh1528Groups()){
  for(const o of list){
   const approved=rh1528CourtMeta.removedWalls.some(m=>m.group===group&&m.x===o.x&&m.y===o.y&&m.w===o.w&&m.k===o.k);
   if(approved)rh1528Cleared.push({group,x:o.x,y:o.y,w:o.w,wasBlocked:blocked(o.x,o.y)});
  }
  for(let i=list.length-1;i>=0;i--)if(rh1528Cleared.some(o=>o.group===group&&o.x===list[i].x&&o.y===list[i].y))list.splice(i,1);
 }
}
function rh1528Status(full=false){
 const cleared=rh1528Cleared.map(o=>({...o,free:full?!blocked(o.x,o.y):null,crossing:full?rh1513PathCheck([[o.x,o.y-16],[o.x,o.y+16]],5):null}));
 return {version:1528,removed:cleared.length,remaining:rh1528Groups().reduce((n,[,list])=>n+list.length,0),
  clearCenters:full?cleared.filter(o=>o.free).length:null,openCrossings:full?cleared.filter(o=>o.crossing.bad===0).length:null,
  cleared,courts:rh1528CourtMeta.courts.map(q=>q.name),bakedTiles:rh1528CourtMeta.ground.map(q=>q.key),
  marketCount:rh1475Furniture.length,structuralTowers:rh1335FortTowers.length,newColliders:0,additionalGroundPasses:0,npcChanges:0};
}
function rh1528Review(key){
 const q={east:[4055,1900],west:[575,900]}[key];if(!q)return false;
 p.x=q[0];p.y=q[1];rh199Reset();return true;
}
