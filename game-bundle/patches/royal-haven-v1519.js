// Royal Haven V1519: a slightly closer exterior camera and unobstructed foot traffic.
// Logical canvas/UI, world coordinates, buildings, actor sizes and room cameras stay unchanged.
const rh1519Zoom=1.12;
const rh1519Soft=new WeakSet();
const rh1519Removed=[],rh1519Decor=[];
const rh1519IsBench=o=>/bench|seat/i.test(String(o.k||''));
function rh1519Camera(x,y,royalView=0,northBias=0){
 const w=W/rh1519Zoom,h=H/rh1519Zoom;
 return {x:Math.max(0,Math.min(WORLD_W-w,x-w/2)),
  y:Math.max(Math.min(WORLD_H-h,y-(h-96/rh1519Zoom)),-royalView*92,
             Math.min(WORLD_H-h,y-h/2-(northBias+royalView*38)/rh1519Zoom)),
  w,h,zoom:rh1519Zoom};
}
function rh1519WorldPoint(x,y,cx,cy){return {x:cx+x/rh1519Zoom,y:cy+y/rh1519Zoom};}
// Swept foot movement, with gentle corner assistance only for near-cardinal input.
// Never teleport through a wall or steer along an extended solid facade.
function rh1519Walk(actor,dx,dy,solid){
 const n=Math.max(1,Math.ceil(Math.hypot(dx,dy)/4)),sx=dx/n,sy=dy/n;
 for(let i=0;i<n;i++){
  const ox=actor.x,oy=actor.y;
  if(sx&&!solid(ox+sx,oy))actor.x=ox+sx;
  if(sy&&!solid(actor.x,oy+sy))actor.y=oy+sy;
  const alongX=Math.abs(sx)>Math.abs(sy)*4,alongY=Math.abs(sy)>Math.abs(sx)*4;
  if(!alongX&&!alongY)continue;
  if((alongX&&actor.x!==ox)||(alongY&&actor.y!==oy))continue;
  // Look at most 14 world units around a short protruding corner. Follow
  // only a clear lateral segment, with a clear forward step at its far end.
  const step=alongX?sx:sy,dir=Math.sign(step),x=actor.x,y=actor.y;
  let shift=0,available=[true,true];
  for(let offset=2;offset<=14&&!shift;offset+=2){
   for(let j=0;j<2;j++){
    if(!available[j])continue;
    const side=j===0?-1:1,d=side*offset,a=x+(alongY?d:0),b=y+(alongX?d:0);
    if(solid(a,b)){available[j]=false;continue;}
    if(!solid(a+(alongX?dir*4:0),b+(alongY?dir*4:0))){shift=d;break;}
   }
  }
  if(!shift)continue;
  const drift=Math.sign(shift)*Math.min(Math.abs(shift),Math.abs(step)*.9);
  const a=x+(alongY?drift:0),b=y+(alongX?drift:0);
  if(!solid(a,b)){actor.x=a;actor.y=b;}
 }
}
function rh1519ClearStreet(){
 // Remove legacy hospitality seating and decorative rail fragments in
 // addition to the plaza/gallery seats already removed in V1514.
 for(const list of [rh194Props,rh176Props,rh1465Props,rh192Edges,rh175Objects]){
  for(let i=list.length-1;i>=0;i--){
   const o=list[i],seat=rh1519IsBench(o),rail=o.k==='rail';
   if(!seat&&!rail)continue;
   rh1519Removed.push({k:o.k,x:o.x,y:o.y});if(seat)rh1514RemovedBenches.push({k:o.k,x:o.x,y:o.y});
   list.splice(i,1);
  }
 }
 // Keep the artwork of little goods, planters, signage, lamps and tools.
 // They are decorative, not pathfinding obstacles. LARGE objects (buildings,
 // raised beds, mature trees, carts, wells, stalls, masonry) remain solid.
 const groups=[
  [rh117Props,()=>true],
  [rh118Props,o=>o.k==='plant'],
  [rh119Garden,o=>o.k==='rock'&&o.w<=100],
  [rh171Furnishings,o=>o.k==='goods'],
  [rh175Objects,o=>o.k==='brazier'],
  [rh176Props,o=>o.k==='barrel'],
  [rh194Props,o=>['armillary','arcaneTable','mossRock','houseWood','houseRack'].includes(o.k)],
  [rh1465Props,()=>true],[rh1460Stations,()=>true]
 ];
 for(const [list,eligible] of groups)for(const o of list)if(eligible(o)){
  rh1519Decor.push({k:o.k,x:o.x,y:o.y,wasBlocked:blocked(o.x,o.y)});
  rh1519Soft.add(o);
 }
}
function rh1519Navigation(){
 const a=rh1519Camera(p.x,p.y),projected={x:(p.x-camX)*rh1519Zoom,y:(p.y-camY)*rh1519Zoom};
 const back=rh1519WorldPoint(projected.x,projected.y,camX,camY);
 const benchCount=[...rh194Props,...rh1465Props,...rh176Props].filter(rh1519IsBench).length;
 return {x:p.x,y:p.y,inside:inside?.name||null,zoom:rh1519Zoom,view:[a.w,a.h],camera:[camX,camY],
  projected,roundTrip:Math.hypot(back.x-p.x,back.y-p.y),benches:benchCount,
  removedSeats:rh1514RemovedBenches.length,removedRails:rh1519Removed.filter(o=>o.k==='rail').length,
  decorCount:rh1519Decor.length,openDecor:rh1519Decor.filter(o=>o.wasBlocked&&!blocked(o.x,o.y)).length,
  solidFountain:blocked(1795,1245),solidMarket:rh1475Furniture.filter(o=>blocked(o.x,o.y)).length,
  marketCount:rh1475Furniture.length};
}
// Only exposed through the explicit graphics-audit option. Choose an actual
// newly opened obstacle with a clear lane across it, for real input testing.
function rh1519ReviewWalk(){
 for(const o of rh1519Decor){
  const {x,y}=o;if(!o.wasBlocked||blocked(x,y)||sites.some(s=>Math.hypot(s.doorX-x,s.doorY-y)<125)||y>2350)continue;
  for(const dir of [1,-1]){
   let free=true;
   for(let d=-45;d<=160&&free;d+=3)if(blocked(x+d*dir,y)||sites.some(s=>Math.hypot(s.doorX-x-d*dir,s.doorY-y)<38))free=false;
   if(!free)continue;
   p.x=x-45*dir;p.y=y;rh199Reset();return {x,y,start:p.x,dir,k:o.k};
  }
 }
 return null;
}
