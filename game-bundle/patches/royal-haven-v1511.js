// V1511: physically supported eastern homes, courtyard approaches and civic openings.
// The original V1509 geometry, routes, collision and actor scale are untouched.
function rh1511DistrictMeta(o){return rh1511DistrictData[o.k]||null;}
function rh1511DistrictArt(o){return !!rh1511DistrictMeta(o);}
function rh1511WindowGlass(o,b){
 const m=rh1511DistrictMeta(o);
 if(m?.windows?.length)rh1510WindowTint(m.windows,b.left,b.top,b.w,b.h);
}
function rh1511DistrictFlues(o){return rh1511DistrictMeta(o)?.flues||null;}
function rh1511DoorRows(o){
 if(o.doors?.length)return o.doors;
 if(o.door?.length)return [[o.door[0],o.door[1],o.doorHeight||70]];
 return Number.isFinite(o.doorWorldOffset)?[[o.x+o.doorWorldOffset,o.y,o.doorHeight||70]]:[];
}
// Rust, moss, chips and irregular wear use world-space seeds. All cached
// surfaces remain on the ground layer, without invisible or raised obstacles.
function rh1511PavingEdge(g,b,poly,seed){
 const w=g.canvas.width,h=g.canvas.height,im=g.getImageData(0,0,w,h),d=im.data;
 const broad=rh1510Field(w,h,21,17,seed),fine=rh1510Field(w,h,5,5,seed+71);
 const edges=poly.map((a,i)=>{const z=poly[(i+1)%poly.length],dx=z[0]-a[0],dy=z[1]-a[1];return [a[0]-b.x,a[1]-b.y,dx,dy,Math.max(.01,dx*dx+dy*dy)];});
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const n=y*w+x,i=n*4;if(!d[i+3])continue;
  let dist=Infinity;
  for(const [ax,ay,dx,dy,l] of edges){
   const t=rh1510Clamp(((x-ax)*dx+(y-ay)*dy)/l);
   dist=Math.min(dist,Math.hypot(x-ax-t*dx,y-ay-t*dy));
  }
  const width=5+broad[n]*12+fine[n]*4,edge=rh1510Clamp((dist-.5)/width);
  const phase=edge*edge*(3-2*edge),soil=(1-phase)*(.32+broad[n]*.68),wear=(broad[n]-.5)*9;
  d[i]=d[i]*(1-soil*.26)+87*soil*.26+wear;
  d[i+1]=d[i+1]*(1-soil*.2)+91*soil*.2+wear;
  d[i+2]=d[i+2]*(1-soil*.25)+57*soil*.25+wear;
  d[i+3]*=phase;
 }
 g.putImageData(im,0,0);
}
// All authored frontage paths and gutter centerlines retain their width. Only
// the outer stones are feathered irregularly so path and grass meet naturally.
function rh1511FrontWear(g,o){
 const w=g.canvas.width,h=g.canvas.height;
 if(w<3||h<3||w*h>310000)return;
 const im=g.getImageData(0,0,w,h),d=im.data,seed=(Math.imul(Math.round(o.x),73856093)^Math.imul(Math.round(o.y),19349663))>>>0;
 const broad=rh1510Field(w,h,17,15,seed),fine=rh1510Field(w,h,4,4,seed+55);
 const span=Math.min(8,Math.max(3,o.half*.28)),edges=[];
 for(let i=1;i<o.points.length;i++){
  const a=o.points[i-1],z=o.points[i],dx=z[0]-a[0],dy=z[1]-a[1];
  edges.push([a[0]-o.x,a[1]-o.y,dx,dy,Math.max(.01,dx*dx+dy*dy)]);
 }
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const n=y*w+x,j=n*4;if(!d[j+3])continue;
  let dist=Infinity;
  for(const [ax,ay,dx,dy,l] of edges){const t=rh1510Clamp(((x-ax)*dx+(y-ay)*dy)/l);dist=Math.min(dist,Math.hypot(x-ax-t*dx,y-ay-t*dy));}
  const q=rh1510Clamp((o.half-dist)/Math.max(1,span*(.53+.77*broad[n]+.36*fine[n])));
  const fade=q*q*(3-2*q),m=(1-fade)*(.28+.72*fine[n]),scuff=(broad[n]-.5)*7;
  d[j]=d[j]*(1-m*.15)+85*m*.15+scuff;d[j+1]=d[j+1]*(1-m*.12)+91*m*.12+scuff;d[j+2]=d[j+2]*(1-m*.17)+61*m*.17+scuff;
  d[j+3]*=fade;
 }
 g.putImageData(im,0,0);
}
const rh1511ThresholdCache=new Map();
function rh1511ThresholdBuild(o,door){
 const [dx,dy,height]=door,wide=Math.round(Math.min(46,Math.max(26,height*.47))),w=wide*2+24,h=44,x=Math.round(dx-w/2),y=Math.round(dy-2);
 const a=rhSurface(w,h),g=a.getContext('2d'),seed=Math.round(o.x*17+o.y*31+dx),b={x,y,w,h};
 rh1406Pave(g,rh191PaveArt,x,y,w,h,.43);
 // Custom worn entry geometry: widest at the sill, then a softly rounded,
 // asymmetric worn route extending into existing paving. Purely visual.
 const shape=[[dx-wide*.72,dy],[dx+wide*.76,dy+1],[dx+wide*.85,dy+12],[dx+wide*.65,dy+28],[dx+wide*.21,dy+39],[dx-wide*.26,dy+36],[dx-wide*.86,dy+22]];
 g.globalCompositeOperation='destination-in';rh1472Trace(g,shape,x,y);g.fillStyle='#fff';g.fill();
 g.globalCompositeOperation='source-atop';
 const gr=g.createLinearGradient(0,0,0,h);
 gr.addColorStop(0,'#29291e66');gr.addColorStop(.31,'#51493329');gr.addColorStop(.83,'#b1a4831d');gr.addColorStop(1,'#6e745b18');
 g.fillStyle=gr;g.fillRect(0,0,w,h);
 for(let i=0;i<16;i++){
  const u=8+rh1510Hash(i,1,seed)*(w-16),v=4+rh1510Hash(i,2,seed)*(h-8);
  g.fillStyle=i%3?'#534a382c':'#bdb08b2a';g.beginPath();g.ellipse(u,v,1+rh1510Hash(i,3,seed)*1.9,.65,rh1510Hash(i,4,seed)*3,0,Math.PI*2);g.fill();
 }
 rh1511PavingEdge(g,b,shape,seed);g.globalCompositeOperation='source-over';
 return {a,x,y};
}
function rh1511ThresholdDraw(cx,cy){
 if(!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 let builds=0;
 for(const o of rh1464Homes){
  if(!rh1511DistrictArt(o)&&!rh1510MarketBuilding(o))continue;
  for(const [i,door] of rh1511DoorRows(o).entries()){
   const [dx,dy]=door;
   if(!Number.isFinite(dx)||!Number.isFinite(dy)||dx+70<cx||dx-70>cx+W||dy+50<cy||dy-8>cy+H)continue;
   const key=o.k+':'+i+':'+dx+':'+dy;
   let a=rh1511ThresholdCache.get(key);
   if(!a&&builds<2){
    // Do not place a decorative entrance apron on a blocked/corner location.
    if(blocked(dx,dy+21))continue;
    a=rh1511ThresholdBuild(o,door);rh1511ThresholdCache.set(key,a);builds++;
   }
   if(a){c.save();c.globalAlpha=.67;c.drawImage(a.a,a.x,a.y);c.restore();}
  }
 }
}
// Diagnostics are read-only. Camera review exists solely with the explicit
// graphicsAudit URL parameter (normal game cannot teleport).
function rh1511OpeningClear(im,regions){
 if(!regions?.length||!im?.complete||im.naturalWidth<2)return null;
 const n=240,a=rhSurface(n,n),g=a.getContext('2d',{willReadFrequently:true});
 g.drawImage(im,0,0,n,n);
 return regions.map(region=>{
  const [x,y,X,Y]=region.map(q=>Math.round(q*n)),d=g.getImageData(x,y,X-x,Y-y).data;
  let clear=0;for(let i=3;i<d.length;i+=4)if(d[i]<35)clear++;
  return clear/(d.length/4);
 });
}
function rh1511DistrictStatus(full=false){
 const assets=Object.entries(rh1511DistrictData).map(([key,m])=>{
  const im=rh1464Art[key],homes=rh1464Homes.filter(o=>o.k===key);
  return {key,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
   openings:full?rh1511OpeningClear(im,m.openings):null,
   instances:homes.map(o=>({x:o.x,y:o.y,w:o.w,h:o.h,doors:rh1511DoorRows(o),archWidth:o.archWidth??null,archHeight:o.archHeight??null}))};
 });
 return {assets,thresholds:rh1511ThresholdCache.size,...(full?{
  court:rh1492Court.audit(),estate:rh1493Estate.audit(),gate:rh1494Gatehouse.audit(),artisan:rh1495District.audit(),herb:rh1496HerbAnnex.audit(),civic:rh1499Civic.audit()}: {})};
}
function rh1511ReviewDistrict(key){
 const points={market:[5510,1958],civic:[5220,1250],artisan:[4575,2012],herb:[3765,2420],gate:[4605,1164]};
 const at=points[key];if(!at)return false;
 [p.x,p.y]=at;return true;
}
