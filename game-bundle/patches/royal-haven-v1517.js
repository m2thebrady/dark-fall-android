// Residential infill: original sprite art, collision-subset footprint, and
// world-seeded ground-only material variations. No new furniture or NPCs.
const rh1517WearCache=new Map();
function rh1517PrepareStreet(){
 for(const r of rh1517Meta.routes){
  const {points,half}=r,pad=half+7,x=Math.min(...points.map(p=>p[0]))-pad,y=Math.min(...points.map(p=>p[1]))-pad;
  rh1467Frontages.push({points,half,x,y,w:Math.ceil(Math.max(...points.map(p=>p[0]))-x+pad),h:Math.ceil(Math.max(...points.map(p=>p[1]))-y+pad),walk1517:true});
 }
}
// An irregular patch of genuinely textured stone. Offset the source tile
// phase so the new surface is not another copy of the road below it, then
// transition through chipped, damp and mossy margins, not rectangle edges.
function rh1517BuildWear(b){
 const a=rhSurface(b.w,b.h),g=a.getContext('2d',{willReadFrequently:true});
 const scale=b.kind==='threshold'?.53:b.kind==='lane'?.44:.48;
 rh1406Pave(g,rh191PaveArt,b.x+157+b.seed%41,b.y-113,b.w,b.h,scale);
 g.globalCompositeOperation='destination-in';rh1472Trace(g,b.shape,b.x,b.y);g.fillStyle='#fff';g.fill();
 g.globalCompositeOperation='source-atop';
 rh1511PavingEdge(g,b,b.shape,b.seed);
 const pixels=g.getImageData(0,0,b.w,b.h),d=pixels.data;
 const broad=rh1510Field(b.w,b.h,42,31,b.seed+3),patch=rh1510Field(b.w,b.h,17,13,b.seed+57),fine=rh1510Field(b.w,b.h,4,3,b.seed+121);
 for(let y=0;y<b.h;y++)for(let x=0;x<b.w;x++){
  const n=y*b.w+x,i=n*4;if(!d[i+3])continue;
  const rough=patch[n],micro=fine[n],v=broad[n],l=.299*d[i]+.587*d[i+1]+.114*d[i+2];
  // Protected corners retain green mortar; foot-worn centers reveal warmer
  // aggregate. Some stones remain untouched instead of uniformly recolored.
  const moss=rh1510Clamp((rough-.49)*2.9)*rh1510Clamp((v-.24)*1.7)*rh1510Clamp((110-l)/67)*(b.kind==='damp'?1:.64);
  const grime=(v-.5)*18+(micro-.5)*7-(b.kind==='damp'?9:3);
  const wear=rh1510Clamp((.54-rough)*2.3)*Math.max(0,l-64)*.10;
  d[i]+=grime+wear-moss*13;d[i+1]+=grime+wear*.68+moss*14;d[i+2]+=grime+wear*.23-moss*11;
  // Irregular fractional alpha reveals some underlying stones across the
  // full patch as well as feathering its boundary.
  d[i+3]*=(.35+.36*v+.22*rough)*(b.kind==='lane'?.8:1);
 }
 g.putImageData(pixels,0,0);return a;
}
function rh1517StreetGround(cx,cy){
 if(!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 let built=0;
 for(const b of rh1517Meta.ground){
  if(b.x+b.w<cx||b.x>cx+W||b.y+b.h<cy||b.y>cy+H)continue;
  let a=rh1517WearCache.get(b.key);
  if(!a&&built<1){a=rh1517BuildWear(b);rh1517WearCache.set(b.key,a);built++;}
  if(a)c.drawImage(a,b.x,b.y);
 }
}
function rh1517ResidentialStatus(full=false){
 const homes=Object.entries(rh1517Meta.homes).map(([key,m])=>{
  const o=rh1464Homes.find(h=>h.k===key),im=rh1464Art[key],b=o&&rh1464Bounds(o),door=o&&rh1511DoorRows(o)[0];
  let footprint=null;
  if(full&&o){let samples=0,bad=0;for(const [l,t,r,z] of o.boxes)for(let x=l+1;x<r;x+=5)for(let y=t+1;y<z;y+=5){samples++;if(!blocked(o.x+x,o.y+y))bad++;}footprint={samples,bad};}
  return {key,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,lot:o&&[o.x,o.y],door,artDoor:b&&[b.left+b.w*m.door[0],b.top+b.h*m.door[1]],doorHeight:b&&b.h*m.doorHeight,doorWidth:b&&b.w*m.doorWidth,bounds:b,footprint,approach:full&&door?rh1513PathCheck([[door[0],door[1]+15],[door[0],door[1]+22]],7):null};
 });
 return {homes,surfaces:[...rh1517WearCache.keys()],routes:full?rh1517Meta.routes.map(r=>({key:r.key,...rh1513PathCheck(r.points,r.half)})):null};
}
function rh1517ReviewResidential(key){
 const pts={cottage:[4565,2410],stone:[4864,2325],lane:[4770,2200],court:[4660,2359]};
 if(!pts[key])return false;[p.x,p.y]=pts[key];return true;
}
