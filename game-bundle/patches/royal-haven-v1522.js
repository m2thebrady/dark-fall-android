// Shop frontage renewal: built-in counters already show all trade goods.
// Remove the eight detached, redundant kiosks; leave the independent east
// market stalls, carts, fountain, shop buildings and interaction anchors alone.
const rh1522Removed=[],rh1522Relocated=[];
const rh1522Stats={frames:0,draws:0,maxVisible:0};
const rh1522Image=new Image();rh1522Image.src=rh1522ArtData;
function rh1522Install(){
 const names=new Set(['Weapon Smith','Armor Smith','Leatherworker','General Store','Item Shop','Herbalist','Bakery','Fletcher']);
 for(let i=marketDisplays.length-1;i>=0;i--){
  const d=marketDisplays[i];if(!names.has(d.name))continue;
  rh1522Removed.push({name:d.name,x:d.x,y:d.y,wasSolid:blocked(d.x,d.y)});
  marketDisplays.splice(i,1);
 }
 // Recess the little already-passable stock piles toward their shops.
 // Do not overwrite streets, remove interactables, or create new collision.
 for(const row of rh1522Frontages)for(const door of row.doors){
  for(const o of rh117Props){
   if(!rh1519Soft.has(o)||!['crate','barrel','basket','goods','plant'].includes(o.k)||
      Math.abs(o.x-door.x)!==120||o.y!==door.y+62)continue;
   for(const off of [32,38,44]){
    const ny=door.y+off;
    if([-10,0,10].some(dx=>[-8,0,8].some(dy=>blocked(o.x+dx,ny+dy))))continue;
    rh1522Relocated.push({k:o.k,x:o.x,from:o.y,to:ny});o.y=ny;break;
   }
  }
 }
}
function rh1522Ground(cx,cy,vw,vh,groundReady){
 if(!groundReady||!rh1522Image.complete||rh1522Image.naturalWidth!==1792)return;
 let drawn=0;
 for(const r of rh1522Frontages){
  if(r.x+r.w<=cx||r.x>=cx+vw||r.y+r.h<=cy||r.y>=cy+vh)continue;
  c.drawImage(rh1522Image,r.sx,r.sy,r.w,r.h,r.x,r.y,r.w,r.h);drawn++;
 }
 rh1522Stats.frames++;rh1522Stats.draws+=drawn;rh1522Stats.maxVisible=Math.max(rh1522Stats.maxVisible,drawn);
}
function rh1522FrontageStatus(full=false){
 const removed=rh1522Removed.map(o=>({...o,clear:!blocked(o.x,o.y),
  crossing:full?rh1513PathCheck([[o.x-25,o.y],[o.x+25,o.y]],7):null}));
 const entrances=full?rh1522Frontages.flatMap(row=>row.doors.map(d=>({x:d.x,y:d.y,material:d.material,
  approach:rh1513PathCheck([[d.x,d.y+20],[d.x,d.y+47]],7)}))):null;
 return {ready:rh1522Image.complete&&rh1522Image.naturalWidth===1792&&rh1522Image.naturalHeight===448,
  rows:rh1522Frontages.length,entrances,removed,relocated:rh1522Relocated.slice(),remaining:marketDisplays.length,
  marketCount:rh1475Furniture.length,solidMarket:rh1475Furniture.every(o=>blocked(o.x,o.y)),stats:{...rh1522Stats}};
}
