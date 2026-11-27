// V1512: independent merchant stalls and weathered fortifications.
// Geometry, collision footprint and authored route graph are not modified.
function rh1512MarketVariant(o){
 if(o.k==='stall1'&&o.x===5845&&o.y===2084)return 'spice';
 if(o.k==='stall0'&&o.x===6240&&o.y===2085)return 'pottery';
 return null;
}
function rh1512MarketImage(o){
 const k=rh1512MarketVariant(o),im=k?rh1512MarketVariants[k]:null;
 return im?.complete&&im.naturalWidth>1?im:rh1475Images[o.k];
}
function rh1512TowerBounds(o){return {left:o.x-o.w/2,top:o.y-o.h,w:o.w,h:o.h,primary:rh1335TowerArt[o.k],upgrade:rh1335TowerArt[o.k],style:{green:true}};}
function rh1512TowerContacts(cx,cy){
 for(const o of rh1335FortTowers){
  rh1510GroundEntry(o,rh1512TowerBounds(o),rh1335TowerArt[o.k],{name:'Watchtower',type:'home',doorX:NaN,doorY:NaN},cx,cy);
 }
}
const rh1512WallCache=new Map(),rh1512FootCache=new Map();
let rh1512WallBuilds=0,rh1512WallPixels=0;
// Value noise is sampled in continuous WORLD coordinates, not restarted at
// the tile edge. Wind/rain stains therefore cross joins without a square seam.
function rh1512Noise(x,y,sx,sy,seed){
 const a=Math.floor(x/sx),b=Math.floor(y/sy),dx=x/sx-a,dy=y/sy-b,u=dx*dx*(3-2*dx),v=dy*dy*(3-2*dy);
 const k=rh1510Hash(a,b,seed),l=rh1510Hash(a+1,b,seed),m=rh1510Hash(a,b+1,seed),n=rh1510Hash(a+1,b+1,seed);
 return (k+(l-k)*u)*(1-v)+(m+(n-m)*u)*v;
}
function rh1512WallSegment(source,side,start){
 // Preserve the painted battlements/stone joints and original transparent
 // silhouette; only the materials are reworked. Cache each visible segment.
 const key=side+':'+start;
 const old=rh1512WallCache.get(key);
 if(old?.source===source){rh1512WallCache.delete(key);rh1512WallCache.set(key,old);return old.can;}
 if(rh1512WallBuilds>=1)return source;
 rh1512WallBuilds++;
 if(old){rh1512WallPixels-=old.can.width*old.can.height;rh1512WallCache.delete(key);}
 const vertical=side!==0,w=vertical?130:480,h=vertical?480:368,can=rhSurface(w,h),g=can.getContext('2d',{willReadFrequently:true});
 g.drawImage(source,0,0,w,h);
 const data=g.getImageData(0,0,w,h),d=data.data;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const n=(y*w+x)*4;if(d[n+3]<32)continue;
  // Source right edge faces the inside of the city; the painter mirrors
  // the whole finished segment for its opposite side.
  const X=vertical?(side<0?x/2:WORLD_W-x/2):start+x/2,Y=vertical?start+y/2:2360+y/2;
  const broad=rh1512Noise(X,Y,52,84,1512),lichen=rh1512Noise(X,Y,8,11,1513),rain=rh1512Noise(X,Y,5,46,1514);
  const face=vertical?rh1510Clamp((x/w-.28)/.67):rh1510Clamp((y/h-.43)/.53);
  const l=d[n]*.299+d[n+1]*.587+d[n+2]*.114,stone=rh1510Clamp((l-25)/67),dark=rh1510Clamp((broad-.30)*1.14)*(.45+.55*rain);
  const green=Math.pow(rh1510Clamp((lichen-.47)*2.4),1.5)*(.15+face*.85)*stone;
  const grit=(rh1510Hash(Math.floor(X*2),Math.floor(Y*2),1515)-.5)*6.4+(broad-.5)*10;
  const shadow=1-dark*.17*stone,fade=green*.29;
  d[n]=d[n]*shadow*(1-fade)+78*fade+grit;
  d[n+1]=d[n+1]*shadow*(1-fade)+90*fade+grit;
  d[n+2]=d[n+2]*shadow*(1-fade)+52*fade+grit;
 }
 g.putImageData(data,0,0);
 while(rh1512WallPixels+w*h>2200000&&rh1512WallCache.size){
  const k=rh1512WallCache.keys().next().value,v=rh1512WallCache.get(k);
  rh1512WallCache.delete(k);rh1512WallPixels-=v.can.width*v.can.height;
 }
 rh1512WallCache.set(key,{source,can});rh1512WallPixels+=w*h;
 return can;
}
// Narrow irregular foundation banks, feathered out over the existing
// terrain. No new solids; scattered tiny rubble is only painted onto earth.
function rh1512FootSegment(side,start){
 const key=side+':'+start;
 if(rh1512FootCache.has(key))return rh1512FootCache.get(key);
 const vertical=side!==0,w=vertical?43:240,h=vertical?240:39,can=rhSurface(w,h),g=can.getContext('2d',{willReadFrequently:true});
 const ox=vertical?(side<0?65:WORLD_W-65-w):start,oy=vertical?start:2322;
 const im=g.createImageData(w,h),d=im.data;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const X=ox+x,Y=oy+y,q=vertical?(side<0?x:w-1-x):h-1-y;
  const broad=rh1512Noise(X,Y,16,22,1521),fine=rh1512Noise(X,Y,3,4,1522),grain=rh1510Hash(X,Y,1523);
  const span=12+24*broad+3*fine,raw=rh1510Clamp(1-q/span),f=raw*raw*(3-2*raw);
  const moss=rh1510Clamp((fine-.45)*2.25)*(.45+.55*broad),i=(y*w+x)*4;
  d[i]=64+grain*26+moss*8;d[i+1]=55+grain*23+moss*24;d[i+2]=39+grain*17+moss*7;
  // Fine stone chips emerge from the vegetation rather than floating.
  if(grain>.966&&fine>.52){d[i]+=37;d[i+1]+=35;d[i+2]+=28;}
  d[i+3]=Math.round(f*(38+76*broad+grain*24));
 }
 g.putImageData(im,0,0);
 const a={can,x:ox,y:oy};rh1512FootCache.set(key,a);return a;
}
function rh1512WallFooting(cx,cy){
 for(const side of [-1,1]){
  const e=side<0?65:WORLD_W-65;
  if(e+45<cx||e-45>cx+W)continue;
  for(let y=Math.max(0,Math.floor(cy/240)*240);y<WORLD_H&&y<cy+H;y+=240){
   const a=rh1512FootSegment(side,y);c.drawImage(a.can,a.x,a.y);
  }
 }
 if(cy+H>=2322&&cy<2361){
  for(let x=Math.max(0,Math.floor(cx/240)*240);x<WORLD_W&&x<cx+W;x+=240){
   const a=rh1512FootSegment(0,x);
   // Retain the existing broad gate approach in its entirety.
   for(const [l,r] of [[0,1450],[2150,WORLD_W]]){
    const from=Math.max(l,x),to=Math.min(r,x+240);if(to<=from)continue;
    c.drawImage(a.can,from-x,0,to-from,39,from,a.y,to-from,39);
   }
  }
 }
}
function rh1512FortStatus(){
 const towers=[0,1,2].map(i=>({key:'tower'+i,ready:rh1335TowerArt[i]?.complete&&rh1335TowerArt[i].naturalWidth===rh1512FortMeta['tower'+i].width&&rh1335TowerArt[i].naturalHeight===rh1512FortMeta['tower'+i].height,
  instances:rh1335FortTowers.filter(o=>o.k===i).map(o=>({x:o.x,y:o.y,w:o.w,h:o.h,rx:o.rx,ry:o.ry}))}));
 const market=rh1475Furniture.filter(o=>o.k.startsWith('stall')).map(o=>{
  const im=rh1512MarketImage(o),key=rh1512MarketVariant(o)||o.k,m=rh1512FortMeta[key];
  return {key,x:o.x,y:o.y,w:o.w,h:o.h,ready:!!im?.complete&&im.naturalWidth>1&&(!m||im.naturalWidth===m.width&&im.naturalHeight===m.height)};
 });
 return {towers,market,wallTiles:rh1512WallCache.size,sideTiles:[...rh1512WallCache.keys()].filter(k=>!k.startsWith('0:')).length,curtainTiles:[...rh1512WallCache.keys()].filter(k=>k.startsWith('0:')).length,footTiles:rh1512FootCache.size,towerContacts:rh1335FortTowers.filter(o=>rh1510GroundCache.has(o)).length};
}
function rh1512ReviewFort(key){
 const pos={market:[6100,1980],south:[4980,2395],west:[185,1500],east:[6320,2050],middle:[5550,1580]};
 if(!pos[key])return false;[p.x,p.y]=pos[key];return true;
}
