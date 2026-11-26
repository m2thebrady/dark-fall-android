// Shared, grounded western shopping street. Keep two cross alleys and
// retain all original interaction points. No collision from cosmetic paving.
const rh1514RowPolygon=[[187,1967],[335,1965],[505,1966],[592,1967],[713,1966],[865,1965],[985,1967],[1110,1966],[1275,1965],[1420,1969],[1423,2025],[1270,2035],[1108,2032],[985,2033],[865,2037],[710,2034],[592,2032],[490,2035],[332,2034],[188,2026]];
const rh1514RowBounds={x:178,y:1958,w:1255,h:88};
let rh1514RowSurface=null;
function rh1514RowGround(cx,cy){
 const b=rh1514RowBounds;
 if(b.x+b.w<cx||b.x>cx+W||b.y+b.h<cy||b.y>cy+H||!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 if(!rh1514RowSurface){
  const a=rhSurface(b.w,b.h),g=a.getContext('2d',{willReadFrequently:true});
  rh1406Pave(g,rh191PaveArt,b.x,b.y,b.w,b.h,.44);
  g.globalCompositeOperation='source-atop';
  const grad=g.createLinearGradient(0,0,0,b.h);grad.addColorStop(0,'#38332c40');grad.addColorStop(.6,'#82755c18');grad.addColorStop(1,'#59604428');g.fillStyle=grad;g.fillRect(0,0,b.w,b.h);
  g.globalCompositeOperation='destination-in';rh1472Trace(g,rh1514RowPolygon,b.x,b.y);g.fillStyle='#fff';g.fill();
  g.globalCompositeOperation='source-atop';rh1511PavingEdge(g,b,rh1514RowPolygon,1514);
  g.globalCompositeOperation='source-over';rh1514RowSurface=a;
 }
 c.drawImage(rh1514RowSurface,b.x,b.y);
}
const rh1514RemovedBenches=[];
function rh1514RemoveStreetBenches(){
 for(const list of [rh194Props,rh1465Props]){
  for(let i=list.length-1;i>=0;i--){
   const o=list[i];if(o.k!=='plazaBench'&&o.k!=='bench')continue;
   rh1514RemovedBenches.push({x:o.x,y:o.y,k:o.k});list.splice(i,1);
  }
 }
 rh1473Furniture.benches.length=0;rh1474Bench.length=0;
 rh1434Grid=rh1434BuildGrid();
}
function rh1514AlignmentStatus(full=false){
 const row=Object.entries(rh1514LayoutMeta.shops).map(([name,m])=>{
  const s=sites.find(o=>o.name===name),b=s&&rh1365SiteBounds(s),im=s&&rh1510Upgrade(s);
  return {name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,door:[s.doorX,s.doorY],artDoor:b?[b.left+b.w*m.door[0],b.top+b.h*m.door[1]]:null,height:b?b.h*m.doorHeight:0,doorWidth:b?b.w*m.doorWidth:0,bounds:b,approach:full?rh1513PathCheck([[s.doorX,s.doorY+19],[s.doorX,s.doorY+42]],8):null};
 });
 const g=rh1464Homes.find(o=>o.k==='rh1494Gatehouse'),gm=rh1514LayoutMeta.gate,im=rh1464Art.rh1494Gatehouse;
 const homes=rh1464Homes.filter(o=>['courtmain','courtwing'].includes(o.k)).map(o=>({key:o.k,x:o.x,y:o.y,door:o.door,bounds:rh1464Bounds(o),approach:full?rh1513PathCheck([[o.door[0],o.door[1]+20],[o.door[0],o.door[1]+42]],7):null}));
 return {row,homes,homeShift:rh1514LayoutMeta.homeShift,gate:{ready:!!g&&!!im?.complete&&im.naturalWidth===gm.width&&im.naturalHeight===gm.height,geometry:g,opening:full?rh1511OpeningClear(im,gm.openings):null},benches:{removed:rh1514RemovedBenches.length,remaining:[...rh194Props,...rh1465Props].filter(o=>o.k==='plazaBench'||o.k==='bench').length,clearCenters:full?rh1514RemovedBenches.filter(o=>!blocked(o.x,o.y)).length:null},pavingReady:!!rh1514RowSurface,...(full?{herbalist:rh1501Herbs.audit(),enchanter:rh1502District.audit(),fletcher:rh1504Artisan.audit(),passage:rh1494Gatehouse.audit(),alleys:[592,1008].map(x=>rh1513PathCheck([[x,1745],[x,1965],[x,1987]],10)),crossStreet:rh1513PathCheck([[170,1995],[335,1995],[592,1995],[865,1995],[1008,1987],[1275,1996],[1444,1999]],9)}:{})};
}
function rh1514ReviewAlignment(key){
 const points={homes:[4320,1115],row:[800,2040],herbalist:[380,2030],fletcher:[1050,2027],gate:[4580,1164]};
 if(!points[key])return false;[p.x,p.y]=points[key];return true;
}
