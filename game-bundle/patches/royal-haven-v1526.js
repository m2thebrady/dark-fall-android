// V1526: ground-level garden and yard detail baked into the same terrain atlas.
// No extra rendering calls, animation, solid objects, NPC changes or camera changes.
function rh1526GardenStatus(full=false){
 const a=rh1521Status();
 return {version:1526,gardenCount:rh1526Gardens.gardens.length,kinds:rh1526Gardens.kinds.slice(),
  tiles:rh1526Gardens.bakedTiles.slice(),visibleTiles:a.tiles,
  gardens:rh1526Gardens.gardens.map(g=>({name:g.name,kind:g.kind,x:g.x,y:g.y,w:g.w,h:g.h,roadClearance:g.roadClearance,clear:full?!blocked(g.x,g.y):null})),
  centersClear:full?rh1526Gardens.gardens.every(g=>!blocked(g.x,g.y)):null,
  additionalDraws:0,newColliders:0,npcChanges:0};
}
function rh1526GardenReview(key){
 const q=rh1526Gardens.review[key];if(!q)return false;
 [p.x,p.y]=q;rh199Reset();return true;
}
