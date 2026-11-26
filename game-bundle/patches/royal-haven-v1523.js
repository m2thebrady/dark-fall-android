// V1523: bounded whole-atlas animation cache and stable adaptive presentation.
// Gameplay still updates at requestAnimationFrame cadence, independently of
// the presentation budget. Artwork, frame selection and world dimensions are unchanged.
const rh1523ActorStats={requests:0,hits:0,direct:0,builds:0,rejected:0,evictions:0,maxPixels:0};
const rh1523ActorBudget=2200000,rh1523ActorLimit=12;
const rh1523ActorAtlases=new Map(),rh1523ActorSeen=new Map(),rh1523ActorIds=new WeakMap();
let rh1523ActorId=0,rh1523ActorPixels=0,rh1523ActorLast=-Infinity;
function rh1523ActorPlan(im,sx,sy,sw,sh,w,h){
 if(!im?.complete||!im.naturalWidth||!im.naturalHeight||![sx,sy,sw,sh,w,h].every(Number.isFinite)||
    sw<=0||sh<=0||w<=0||h<=0||sx<0||sy<0||sx+sw>im.naturalWidth||sy+sh>im.naturalHeight)return null;
 // Only complete, regularly gridded sprite sheets. Arbitrary crops stay direct.
 if(![sx/sw,sy/sh,im.naturalWidth/sw,im.naturalHeight/sh].every(Number.isInteger))return null;
 const ratio=Math.max(w/sw,h/sh);
 if(ratio>=.68)return null;
 // Quantization shares pages across NPCs of slightly different sizes. Every
 // cached frame has at least its world-display resolution, never an upscaled thumbnail.
 const scale=ratio<=.33?.375:ratio<=.45?.50:.75;
 const cw=Math.ceil(sw*scale),ch=Math.ceil(sh*scale),aw=im.naturalWidth/sw*cw,ah=im.naturalHeight/sh*ch,n=aw*ah;
 if(aw>4096||ah>4096||n>rh1523ActorBudget*.48)return null;
 return {cw,ch,aw,ah,n,sx:sx/sw*cw,sy:sy/sh*ch};
}
function rh1523ActorDraw(im,sx,sy,sw,sh,x,y,w,h){
 rh1523ActorStats.requests++;
 function direct(){rh1523ActorStats.direct++;c.drawImage(im,sx,sy,sw,sh,x,y,w,h);}
 if(!rh1433InExterior||rh1431Perf.tier===0||c.filter&&c.filter!=='none')return direct();
 const plan=rh1523ActorPlan(im,sx,sy,sw,sh,w,h);if(!plan)return direct();
 if(!rh1523ActorIds.has(im))rh1523ActorIds.set(im,++rh1523ActorId);
 const key=[rh1523ActorIds.get(im),sw,sh,plan.cw,plan.ch].join(':');
 const now=performance.now();let a=rh1523ActorAtlases.get(key);
 if(a){a.used=now;rh1523ActorStats.hits++;c.drawImage(a.canvas,plan.sx,plan.sy,plan.cw,plan.ch,x,y,w,h);return;}
 let seen=rh1523ActorSeen.get(key);
 if(!seen){seen={uses:0,last:-Infinity};rh1523ActorSeen.set(key,seen);}
 if(now-seen.last>1800)seen.uses=0;
 if(now-seen.last>=8)seen.uses++;seen.last=now;
 while(rh1523ActorSeen.size>128)rh1523ActorSeen.delete(rh1523ActorSeen.keys().next().value);
 // Never evict a page that is in current use. If all pages are busy, draw
 // directly rather than spending every frame rebuilding and discarding them.
 if(seen.uses<2||now-rh1523ActorLast<(rh176Moving?300:180)||rh1431Perf.cost>25){
  rh1523ActorStats.rejected++;return direct();
 }
 let room=rh1523ActorPixels+plan.n<=rh1523ActorBudget&&rh1523ActorAtlases.size<rh1523ActorLimit;
 if(!room){
  const cold=[...rh1523ActorAtlases.entries()].filter(([,q])=>now-q.used>5000).sort((a,b)=>a[1].used-b[1].used);
  for(const [k,q] of cold){rh1523ActorAtlases.delete(k);rh1523ActorPixels-=q.n;rh1523ActorStats.evictions++;
   if(rh1523ActorPixels+plan.n<=rh1523ActorBudget&&rh1523ActorAtlases.size<rh1523ActorLimit){room=true;break;}}
 }
 if(!room||!rh1518Claim('actor-sheet')){rh1523ActorStats.rejected++;return direct();}
 rh1523ActorLast=now;
 try{
  // Exact integer cell boundaries preserve animation cropping and anchors.
  const canvas=rhSurface(plan.aw,plan.ah),g=canvas.getContext('2d');
  g.imageSmoothingEnabled=true;g.imageSmoothingQuality='medium';
  g.drawImage(im,0,0,plan.aw,plan.ah);
  a={canvas,n:plan.n,used:now};rh1523ActorAtlases.set(key,a);rh1523ActorPixels+=plan.n;
  rh1523ActorStats.builds++;rh1523ActorStats.maxPixels=Math.max(rh1523ActorStats.maxPixels,rh1523ActorPixels);
 }catch(_){return direct();}
 c.drawImage(a.canvas,plan.sx,plan.sy,plan.cw,plan.ch,x,y,w,h);
}
function rh1523ClearActors(){
 rh1523ActorAtlases.clear();rh1523ActorSeen.clear();rh1523ActorPixels=0;rh1523ActorLast=-Infinity;
}
// The old controller reset its history after >150ms, so severe stutters
// could continuously prevent fallback. Explicit long-frame tracking and
// asymmetric recovery leave the input/simulation running at native cadence.
const rh1523TimingStats={updates:0,presents:0,longGaps:0,slowTransitions:0,tierTransitions:0,skipped:0};
function rh1523State(tier=0){return {tier,slow:tier>0,raf:16.67,cost:0,last:0,count:0,start:0,good:0,next:-Infinity,pressure:0,lastChange:0};}
function rh1523Observe(q,t,cost){
 const gap=q.last?t-q.last:0;q.last=t;rh1523TimingStats.updates++;
 if(gap>0&&gap<1000){q.raf=q.raf*.88+gap*.12;q.count++;if(gap>45)rh1523TimingStats.longGaps++;}
 else if(gap>=1000){q.count=0;q.start=t;q.good=0;q.pressure=0;return;}
 if(Number.isFinite(cost)&&cost>=0)q.cost=q.cost?q.cost*.90+cost*.10:cost;
 if(!q.start)q.start=t;
 const threshold=q.slow?27:17;
 const bad=(gap>42&&gap<1000)||q.cost>threshold||q.raf>24;
 q.pressure=bad?Math.min(12,(q.pressure||0)+1):Math.max(0,(q.pressure||0)-1);
 // A drop in frame cadence is cheaper than a canvas resize; first pace the
 // renderer, then reduce resolution only if 30 Hz still cannot keep up.
 if(q.pressure>=4&&t-(q.lastChange||0)>450){
  if(!q.slow){q.slow=true;rh1523TimingStats.slowTransitions++;}
  else if(q.tier<2){q.tier++;rh1523TimingStats.tierTransitions++;}
  else{q.pressure=0;return;}
  q.pressure=0;q.good=0;q.count=0;q.start=t;q.lastChange=t;q.next=-Infinity;return;
 }
 if(t-q.start<1200||q.count<12)return;
 q.start=t;q.count=0;
 const good=q.raf<19&&q.cost<(q.slow?10:8);
 if(good){
  if(++q.good>=5){
   if(q.slow){q.slow=false;rh1523TimingStats.slowTransitions++;}
   else if(q.tier>0){q.tier--;rh1523TimingStats.tierTransitions++;}
   q.good=0;q.pressure=0;q.lastChange=t;q.next=-Infinity;
  }
 }else q.good=0;
}
function rh1523Due(q,t,changed=false,room=false){
 const step=room||!q.slow?1000/60:1000/30;
 if(changed||!Number.isFinite(q.next)){q.next=t+step;rh1523TimingStats.presents++;return true;}
 if(t+1.4<q.next){rh1523TimingStats.skipped++;return false;}
 q.next+=step;if(q.next<t-1.4)q.next=t+step;rh1523TimingStats.presents++;return true;
}
function rh1523Stats(){
 return {actor:{...rh1523ActorStats,pages:rh1523ActorAtlases.size,pixels:rh1523ActorPixels,budget:rh1523ActorBudget},
  cadence:{...rh1523TimingStats,target:rh1431Perf.slow?30:60}};
}
// Use actual close-camera viewport for ordinary sprite selection. Tiled
// ground passes and map/geometry audits keep their conservative culling.
function rh1523Intersects(b,cx,cy,pad=0){
 const live=rh1433InExterior&&!rh1436GroundView&&cx===camX&&cy===camY;
 const w=live?W/rh1519Zoom:W,h=live?H/rh1519Zoom:H;
 return b.left+b.w+pad>cx&&b.left-pad<cx+w&&b.top+b.h+pad>cy&&b.top-pad<cy+h;
}
