// Paving improvements are wholly baked into the existing world-space terrain.
// No geometry, objects, draw calls, character art, or animation is changed.
function rh1530CommercialStatus(full=false){
 const terrain=rh1521Status(false);
 return {version:1530,regions:rh1530CommercialMeta.regions.map(r=>({
  name:r.name,court:r.court,kind:r.kind,road:r.road,points:r.points,renderedTiles:r.tiles,
  path:full?rh1513PathCheck(r.points,7):null,review:r.review,reviewClear:full?!blocked(r.review[0],r.review[1]):null
 })),
 materials:rh1530CommercialMeta.materials,bakedTiles:rh1530CommercialMeta.ground.map(q=>q.key),
 visible:terrain.tiles,roadCount:terrain.roadCount,marketCount:rh1475Furniture.length,
 newColliders:0,additionalGroundPasses:0,npcChanges:0};
}
function rh1530ReviewCommercial(index){
 const r=rh1530CommercialMeta.regions[index];if(!r)return false;
 [p.x,p.y]=r.review;rh199Reset();return true;
}
