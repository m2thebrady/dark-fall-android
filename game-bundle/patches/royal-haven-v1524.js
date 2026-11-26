// All landscape details are baked into the existing 720x650 terrain tiles.
// Only the optional graphics audit invokes collision sampling.
function rh1524LandscapeStatus(full=false){
 const terrain=rh1521Status();
 return {version:rh1524Landscape.version,materials:rh1524Landscape.materials.slice(),tileCount:rh1524Landscape.tileCount,
  tiles:terrain.tiles,linkCount:rh1524Landscape.links.length,gardenCount:rh1524Landscape.gardens.length,
  routes:full?rh1524Landscape.links.map(r=>({key:r.key,width:r.width,...rh1513PathCheck(r.points,7)})):null,
  gardenCentersClear:full?rh1524Landscape.gardens.every(g=>!blocked(g.x,g.y)):null,
  geometry:'unchanged',additionalDraws:0};
}
function rh1524Review(key){
 const q={gatehouse:[4630,1270],longhouse:[5250,1280],residences:[5220,2075],south:[4630,2410],herbs:[3760,2340]}[key];
 if(!q)return false;[p.x,p.y]=q;rh199Reset();return true;
}
