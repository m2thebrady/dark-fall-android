// Northern landmarks use painted surfaces and real botanical material without
// adding world entities. All placement, stair geometry and collisions remain.
const rh1532CourtImages=Object.create(null);
function rh1532ImageReady(im){return !!(im?.complete&&im.naturalWidth>1)}
function rh1532IsTerrace(o){return o.seed>=31&&o.seed<=34}
function rh1532PlantFill(g,o,x,y,w,h,variant=0){
 if(!rh1532ImageReady(rh1532PlantArt)||w<=0||h<=0)return false;
 const im=rh1532PlantArt,sw=Math.min(im.naturalWidth,Math.round(w*4.2)),sh=Math.min(im.naturalHeight,Math.round(h*4.2));
 const seed=o.seed*47+variant*173;
 const sx=(seed*13)%(im.naturalWidth-sw+1),sy=(seed*31)%(im.naturalHeight-sh+1);
 g.drawImage(im,sx,sy,sw,sh,x,y,w,h);
 return true;
}
function rh1532TerraceStone(g,o,x,y,w,h){
 if(!rh1532IsTerrace(o))return false;
 const im=rh1532CourtImages[o.seed<=32?13471:13472];
 if(!rh1532ImageReady(im))return false;
 // Crop a different side field per terrace; no baked inlaid lines in the landing.
 const sx=o.seed%2?50:im.naturalWidth-50-w;
 g.drawImage(im,sx,60,w,h,x,y,w,h);
 return true;
}
function rh1532Status(full=false){
 const ground=rh1521Status(false);
 return {version:1532,regions:rh1532Meta.regions.map(r=>({key:r.key,name:r.name,review:r.review,tiles:r.tiles,
  ready:rh1532ImageReady(rh1532CourtImages[r.overlay.seed]),material:r.material,
  path:full?rh1513PathCheck(r.path,7):null,reviewClear:full?!blocked(r.review[0],r.review[1]):null})),
  botanicalReady:rh1532ImageReady(rh1532PlantArt),terraces:rh1325Terraces.filter(rh1532IsTerrace).map(o=>({seed:o.seed,x:o.x,y:o.y,w:o.w,h:o.h,
   landing:full?!blocked(o.x,o.y+o.h/2-4):null,backSolid:full?blocked(o.x,o.y-o.h/2+2):null})),
  beds:rh189Greens.filter(o=>o.landmark1347).length,
  northAvenue:full?rh1513PathCheck(rh1521Plan.roads.find(r=>r.key==='North Avenue').points,7):null,
  bakedTiles:rh1532Meta.ground.map(t=>t.key),visible:ground.tiles,
  newColliders:0,npcChanges:0,additionalSurfaceDraws:0};
}
function rh1532Review(key){
 const r=rh1532Meta.regions.find(o=>o.key===key);if(!r)return false;
 [p.x,p.y]=r.review;rh199Reset();return true;
}
