// Prepainted walls and foundation banks. Static images are shared across all
// segments. There is no per-coordinate Canvas2D readback or weather raster.
function rh1535WallRef(source,side,start){
 const key=side+':'+start;
 const old=rh1512WallCache.get(key);
 if(old?.source===source){rh1512WallCache.delete(key);rh1512WallCache.set(key,old);return source;}
 rh1512WallCache.set(key,{source,can:source});
 while(rh1512WallCache.size>64)rh1512WallCache.delete(rh1512WallCache.keys().next().value);
 return source;
}
function rh1535FootRef(side,start){
 const kind=side===0?'south':side<0?'west':'east';
 const im=rh1535FootArt[kind][Math.abs(Math.floor(start/240))%4];
 if(!im?.complete||!im.naturalWidth)return null;
 const key=side+':'+start,old=rh1512FootCache.get(key);
 if(old?.can===im)return old;
 const x=side===0?start:side<0?65:WORLD_W-108,y=side===0?2322:start;
 const a={can:im,x,y};rh1512FootCache.set(key,a);return a;
}
const rh1535ReviewPoints={west:[205,855],east:[6220,1660],south:[4980,2395],gate:[1800,2395]};
function rh1535WallStatus(full=false){
 const a=rh1521Status(false);
 const ready=(m,im)=>({key:m.key,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,width:m.width,height:m.height});
 return {version:1535,curtain:rh1535Meta.curtain.map((m,i)=>ready(m,rh1215WallArt[i])),
  sides:rh1535Meta.side.map((m,i)=>ready(m,rh1335SideArt[i])),
  feet:rh1535Meta.foot.map(m=>({...ready(m,rh1535FootArt[m.kind][Number(m.key)]),kind:m.kind})),
  seamAlphaMAE:[...rh1535Meta.curtainSeamAlphaMAE,...rh1535Meta.sideSeamAlphaMAE],
  wallRefs:rh1512WallCache.size,footRefs:rh1512FootCache.size,
  sharedSources:[...rh1512WallCache.values()].every(q=>q.can===q.source),
  runtimeWallBuilds:rh1518Stats.byKind.wall||0,wallRasterPixels:rh1512WallPixels,
  gateReady:rh1510StreetArtStatus().gateReady,gateClip:rh1535Meta.gateClip,
  gatePath:full?rh1513PathCheck(rh1521Plan.roads.find(r=>r.key==='Forest Gate Walk').points,7):null,
  gateOpen:full?!blocked(1800,2510):null,curtainSolid:full?blocked(1000,2520):null,
  sideSolid:full?blocked(32,1200)&&blocked(WORLD_W-32,1200):null,
  review:Object.entries(rh1535ReviewPoints).map(([key,xy])=>({key,xy,clear:full?!blocked(...xy):null})),
  visible:a.tiles,newColliders:0,additionalDraws:0,npcChanges:0};
}
function rh1535Review(key){
 const xy=rh1535ReviewPoints[key];if(!xy||blocked(...xy))return false;[p.x,p.y]=xy;rh199Reset();return true;
}
