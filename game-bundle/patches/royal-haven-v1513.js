// V1513: street-facing shop row and inward-facing courtyard.
// Store door interaction coordinates and the surrounding route graph stay intact.
function rh1513RowBuilding(s){return !!rh1513LayoutMeta.shops[s.name];}
function rh1513RowGlass(s,b){
 const m=rh1513LayoutMeta.shops[s.name];
 if(m?.windows?.length)rh1510WindowTint(m.windows,b.left,b.top,b.w,b.h);
}
function rh1513CourtGlass(o,b){
 const m=rh1513LayoutMeta.court[o.k];
 if(m?.windows?.length)rh1510WindowTint(m.windows,b.left,b.top,b.w,b.h);
}
// One continuous commercial pavement, with cross-street entrances left open.
// Use the existing painted paving sampled in world coordinates, not a new
// rectangular platform. All material applied here is ground-only.
const rh1513RowPolygon=[[2144,1968],[2313,1966],[2500,1967],[2630,1968],[2814,1966],[3000,1968],[3150,1967],[3330,1967],[3520,1969],[3612,1973],[3610,2025],[3518,2033],[3326,2038],[3140,2036],[2940,2030],[2790,2032],[2570,2036],[2338,2034],[2150,2028]];
const rh1513RowBounds={x:2136,y:1958,w:1488,h:88};
let rh1513RowSurface=null;
function rh1513RowGround(cx,cy){
 const b=rh1513RowBounds;
 if(b.x+b.w<cx||b.x>cx+W||b.y+b.h<cy||b.y>cy+H||!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 if(!rh1513RowSurface){
  const a=rhSurface(b.w,b.h),g=a.getContext('2d',{willReadFrequently:true});
  rh1406Pave(g,rh191PaveArt,b.x,b.y,b.w,b.h,.44);
  g.globalCompositeOperation='source-atop';
  const shade=g.createLinearGradient(0,0,0,b.h);shade.addColorStop(0,'#37362c44');shade.addColorStop(.30,'#5f544025');shade.addColorStop(.65,'#a59a7c10');shade.addColorStop(1,'#5d62452b');
  g.fillStyle=shade;g.fillRect(0,0,b.w,b.h);
  g.globalCompositeOperation='destination-in';rh1472Trace(g,rh1513RowPolygon,b.x,b.y);g.fillStyle='#fff';g.fill();
  g.globalCompositeOperation='source-atop';rh1511PavingEdge(g,b,rh1513RowPolygon,1513);
  // Longitudinal worn centre line only; no uniform boxed border or raised curb.
  const seed=1513;for(let i=0;i<180;i++){
   const x=22+rh1510Hash(i,0,seed)*(b.w-44),y=20+rh1510Hash(i,1,seed)*47;
   g.fillStyle=i%3?'#6a5f4936':'#b8a88b30';g.beginPath();g.ellipse(x,y,1+rh1510Hash(i,2,seed)*2,.55+rh1510Hash(i,3,seed)*.6,rh1510Hash(i,4,seed)*3,0,Math.PI*2);g.fill();
  }
  g.globalCompositeOperation='source-over';rh1513RowSurface=a;
 }
 c.drawImage(rh1513RowSurface,b.x,b.y);
}
function rh1513PathCheck(points,r=9){
 let samples=0,bad=0,examples=[];
 for(let i=1;i<points.length;i++){
  const a=points[i-1],b=points[i],n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/5));
  for(let j=0;j<=n;j++){
   const t=j/n,x=a[0]+(b[0]-a[0])*t,y=a[1]+(b[1]-a[1])*t;samples++;
   let clear=true;for(const dx of [-r,0,r])for(const dy of [-r,0,r])if(blocked(x+dx,y+dy))clear=false;
   if(!clear){bad++;if(examples.length<8)examples.push([Math.round(x),Math.round(y)]);}
  }
 }
 return {samples,bad,examples};
}
function rh1513LayoutStatus(full=false){
 const row=Object.entries(rh1513LayoutMeta.shops).map(([name,m])=>{
  const s=sites.find(o=>o.name===name),b=s&&rh1365SiteBounds(s),im=s&&rh1510Upgrade(s),ready=!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height;
  return {name,ready,door:s?[s.doorX,s.doorY]:null,artDoor:b?[b.left+b.w*m.door[0],b.top+b.h*m.door[1]]:null,
   height:b?b.h*m.doorHeight:0,doorWidth:b?b.w*m.doorWidth:0,fit:b,
   approach:full&&s?rh1513PathCheck([[s.doorX,s.doorY+19],[s.doorX,s.doorY+41]],8):null};
 });
 const court=rh1474Parts.map(o=>{
  const m=rh1513LayoutMeta.court[o.k],im=rh1474Art[o.k],b=rh1474Bounds(o);
  return {key:o.k,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
   bounds:b,door:o.door||null,artDoor:m.door?[b.left+b.w*m.door[0],b.top+b.h*m.door[1]]:null,doorHeight:o.doorHeight||null,poly:o.poly||null};
 });
 return {row,court,pavingReady:!!rh1513RowSurface,...(full?{
  trades:rh1500Trades.audit(),artisan:rh1504Artisan.audit(),
  courtRoutes:rh1474Routes.map(o=>rh1513PathCheck(o.points,Math.min(10,o.half-3))),
  crossStreet:rh1513PathCheck([[2325,1987],[2550,1987],[2600,1994],[2865,1994],[2970,1994],[3090,1994],[3200,1994],[3345,1990]],9)
 }: {})};
}
function rh1513ReviewLayout(key){
 const points={courtyard:[6010,1416],row:[2840,2025],tailor:[2490,2020],bakery:[3100,2020]};
 if(!points[key])return false;[p.x,p.y]=points[key];return true;
}
