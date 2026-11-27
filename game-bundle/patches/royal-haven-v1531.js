// Visual-only, world-aligned royal paving. The replacement overlay uses
// the existing castle court render and exact same alpha silhouette.
function rh1531RoyalStatus(full=false){
 const ground=rh1521Status(false),m=rh1531RoyalMeta.overlay;
 return {version:1531,overlay:{width:m.width,height:m.height,alphaPreserved:m.alphaPreserved,
  ready:!!rh1315CourtArt.complete&&rh1315CourtArt.naturalWidth===m.width&&rh1315CourtArt.naturalHeight===m.height},
  regions:rh1531RoyalMeta.regions.map(r=>({key:r.key,name:r.name,review:r.review,tiles:r.tiles,
   path:full?rh1513PathCheck(r.path,7):null,reviewClear:full?!blocked(r.review[0],r.review[1]):null})),
  materials:rh1531RoyalMeta.materials,bakedTiles:rh1531RoyalMeta.ground.map(t=>t.key),visible:ground.tiles,
  castleReady:rh1313CitadelReady(),castleSolid:full?blocked(1800,465):null,
  fountainSolid:full?blocked(1795,1245):null,castleApproach:full?rh1513PathCheck([[1800,575],[1800,1015]],7):null,
  waterfallLoops:rh1314WaterArt.length,
  waterfallReady:rh1314WaterArt.every(im=>im.complete&&im.naturalWidth>1),
  royalGardens:rh189Greens.filter(o=>o.royal1346).length,
  marketCount:rh1475Furniture.length,newColliders:0,additionalGroundPasses:0,npcChanges:0};
}
function rh1531ReviewRoyal(key){
 const r=rh1531RoyalMeta.regions.find(o=>o.key===key);if(!r)return false;
 [p.x,p.y]=r.review;rh199Reset();return true;
}
