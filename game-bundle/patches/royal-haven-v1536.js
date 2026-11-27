// Three static replacements share the established facade and market draw paths.
// The notice board is straightened inside its previous collision envelope.
const rh1536ReviewPoints={well:[6100,1980],bell:[5380,1410],notice:[5160,1321]};
function rh1536Status(full=false){
 const well=rh1475Furniture.find(o=>o.k==='well'),bell=rh1464Homes.find(o=>o.k==='rh1499bellCourt'),notice=rh1464Homes.find(o=>o.k==='rh1499notice');
 const objects={well,rh1499bellCourt:bell,rh1499notice:notice};
 const assets=rh1536Meta.models.map(m=>{
  const o=objects[m.key],im=m.key==='well'?o&&rh1512MarketImage(o):rh1464Art[m.key];
  return {key:m.key,ready:!!o&&!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
   position:o&&[o.x,o.y],size:o&&[o.w,o.h]};
 });
 const civic=full?rh1499Civic.audit():null;
 return {version:1536,assets,marketCount:rh1475Furniture.length,
  wellSolid:full?!!well&&blocked(well.x,well.y):null,
  bellOpening:full?rh1511OpeningClear(rh1464Art.rh1499bellCourt,[[.27,.695,.72,.79]]):null,
  passage:full?civic.passage:null,civicRoutes:full?civic.routes:null,
  civicFootprints:full?civic.objects:null,
  noticeApproach:full?rh1513PathCheck([[5200,1318],[5160,1321]],7):null,
  noticeStraight:!!notice&&notice.dx===0&&notice.artDy===0&&notice.polyParts[0].every((a,i,ps)=>a[0]===ps[(i+1)%ps.length][0]||a[1]===ps[(i+1)%ps.length][1]),
  wellCirculation:full?rh1513PathCheck([[6100,1955],[6100,1980],[6100,2058],[6045,2058],[5990,2058],[5990,1980]],7):null,
  routes:full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  review:Object.entries(rh1536ReviewPoints).map(([key,xy])=>({key,xy,clear:full?!blocked(...xy):null})),
  bakedTiles:rh1536Meta.ground.map(m=>m.key),additionalDraws:0,newColliders:0,npcChanges:0};
}
function rh1536Review(key){
 const xy=rh1536ReviewPoints[key];if(!xy||blocked(...xy))return false;[p.x,p.y]=xy;rh199Reset();return true;
}
