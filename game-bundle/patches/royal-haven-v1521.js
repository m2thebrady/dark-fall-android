// A single authored exterior ground plan. World-space tile positions, actor
// sizes, shop entrances, existing building footprints and mountain remain.
const rh1521GroundStats={frames:0,tiles:0,readyFrames:0,fallbackFrames:0,legacyCalls:0};
let rh1521MarketMoveResult={moved:[],rejected:null};
function rh1521MarketInstall(){
 const original=rh1475Furniture.slice(),poses=original.map(o=>[o.x,o.y]);
 const moved=[];
 for(const m of rh1521Plan.marketMoves){
  const o=original.find(o=>o.k===m.k&&o.x===m.old[0]&&o.y===m.old[1]);
  if(!o){rh1521MarketMoveResult.rejected='missing '+m.k;return;}
  moved.push({o,m});
 }
 // Check each new footing against the actual city without any old market
 // furniture. Commit only if every new position remains safe.
 rh1475Furniture.length=0;
 let failed=null;
 for(const {o,m} of moved){
  const [x,y]=m.new;
  outer:for(let dx=-o.rx-4;dx<=o.rx+4;dx+=8)for(let dy=-o.ry-4;dy<=o.ry+4;dy+=8)
   if(blocked(x+dx,y+dy)){failed={k:o.k,x,y,conflict:[x+dx,y+dy]};break outer;}
  if(failed)break;
 }
 if(!failed){
  for(const {o,m} of moved){[o.x,o.y]=m.new;}
  for(let i=0;i<original.length;i++)for(let j=i+1;j<original.length;j++){
   const a=original[i],b=original[j];
   if(Math.abs(a.x-b.x)<a.rx+b.rx+8&&Math.abs(a.y-b.y)<a.ry+b.ry+8)
    failed={k:a.k,other:b.k,conflict:[a.x,a.y]};
  }
 }
 if(failed){original.forEach((o,i)=>{[o.x,o.y]=poses[i]});rh1521MarketMoveResult.rejected=failed;}
 else rh1521MarketMoveResult.moved=moved.map(({m})=>m);
 rh1475Furniture.push(...original);
}
function rh1521VisibleTiles(cx,cy,vw,vh){
 const list=[];
 for(let yy=Math.max(0,Math.floor(cy/650));yy<=Math.min(3,Math.floor((cy+vh-.001)/650));yy++)
 for(let xx=Math.max(0,Math.floor(cx/720));xx<=Math.min(8,Math.floor((cx+vw-.001)/720));xx++){
  const key=xx+':'+yy,im=rh119ChunkImages.get(key);list.push({key,x:xx*720,y:yy*650,im,ready:!!im?.complete&&im.naturalWidth===720&&im.naturalHeight===650});
 }
 return list;
}
function rh1521Ready(cx,cy,vw,vh){const a=rh1521VisibleTiles(cx,cy,vw,vh);return !!a.length&&a.every(o=>o.ready);}
function rh1521LegacyGround(cx,cy,vw,vh,ready,draw){
 if(!ready){rh1521GroundStats.legacyCalls++;draw();return;}
 // The master atlas already contains the streets. Keep original northern
 // mountain terraces and the narrow outer strip at the Forest Gate only.
 if(cy>=865&&cy+vh<=2460)return;
 c.save();try{
  c.beginPath();if(cy<865)c.rect(0,0,WORLD_W,865);
  if(cy+vh>2460)c.rect(0,2460,WORLD_W,140);
  c.clip();rh1521GroundStats.legacyCalls++;draw();
 }finally{c.restore();}
}
function rh1521BlendTransitions(cx,cy,vw,vh,ready){
 rh1521GroundStats.frames++;
 if(!ready){rh1521GroundStats.fallbackFrames++;return;}
 rh1521GroundStats.readyFrames++;
 const a=rh1521VisibleTiles(cx,cy,vw,vh);rh1521GroundStats.tiles+=a.length;
 // Only the transition strips are redrawn. The main city ground was already
 // drawn by rh119Ground; no second full-screen ground buffer is allocated.
 for(const q of a){
  if(!q.ready)continue;
  for(const [from,to,reverse] of [[700,865,false],[2460,2490,true]]){
   if(q.y>=to||q.y+650<=from||cy>=to||cy+vh<=from)continue;
   const n=reverse?4:12;
   for(let i=0;i<n;i++){
    const lo=Math.max(q.y,from+(to-from)*i/n),hi=Math.min(q.y+650,from+(to-from)*(i+1)/n);if(hi<=lo)continue;
    let alpha=(i+.5)/n;if(reverse)alpha=1-alpha;
    alpha=alpha*alpha*(3-2*alpha);
    c.save();c.globalAlpha=alpha;c.drawImage(q.im,0,lo-q.y,720,hi-lo,q.x,lo,720,hi-lo);c.restore();
   }
  }
 }
}
function rh1521StaticContacts(cx,cy){
 const vis=(x,y,r=180)=>x>cx-r&&x<cx+W+r&&y>cy-r&&y<cy+H+r;
 rh1219TreeGround(vis);rh1218FoundationShadows(vis);rh170StreetShadows(cx,cy);
 rh1459WallContacts(cx,cy);rh1460StationContacts(cx,cy);
 rh1464Contacts(cx,cy);rh1465Contacts(cx,cy);rh1474Contacts(cx,cy);
}
function rh1521Review(key){
 const q=rh1521Plan.review[key];if(!q)return false;[p.x,p.y]=q;rh199Reset();return true;
}
function rh1521Status(full=false){
 const v=rh1519Camera(p.x,p.y),tiles=rh1521VisibleTiles(v.x,v.y,v.w,v.h);
 const routes=full?rh1521Plan.roads.filter(r=>r.audit).map(r=>({key:r.key,width:r.width,...rh1513PathCheck(r.points,7)})):null;
 // Test the formerly obstructed cart locations, plus the existing well and
 // all current market furniture. No part of the paving enters collision.
 const cleared=full?rh1521MarketMoveResult.moved.filter(m=>m.k==='cart').map(m=>({x:m.old[0],y:m.old[1],clear:!blocked(m.old[0],m.old[1])})):null;
 return {tiles:tiles.map(q=>({key:q.key,ready:q.ready})),roadCount:rh1521Plan.roads.length,courtCount:rh1521Plan.courts.length,
  stats:{...rh1521GroundStats},market:rh1521MarketMoveResult,cleared,routes,
  solidMarket:rh1475Furniture.every(o=>blocked(o.x,o.y)),fountainSolid:blocked(1795,1245)};
}
