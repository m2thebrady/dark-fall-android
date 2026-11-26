import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
let now=0,draws=[],rasterBuilds=0,claims=[];
const sprite=()=>({complete:true,naturalWidth:2048,naturalHeight:1536});
const sources=Array.from({length:4},sprite);
const canvas=(w,h)=>({width:w,height:h,getContext(){return {drawImage(...args){rasterBuilds++;assert.ok(args[3]<=4096&&args[4]<=4096);}}}});
const ctx=vm.createContext({performance:{now:()=>now},rhSurface:canvas,rh1433InExterior:true,rh1431Perf:{tier:1,cost:10,slow:true},
 rh176Moving:true,rh1518Claim:k=>{claims.push(k);return true;},c:{filter:'none',drawImage(...args){draws.push(args);}},rh1436GroundView:null,camX:0,camY:0,W:1280,H:720,rh1519Zoom:1.12});
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1523.js','utf8'),ctx);
const initial=ctx.rh1523ActorPlan(sources[0],256,512,256,256,72,72);
assert.equal(initial.cw,96);assert.equal(initial.ch,96);assert.equal(initial.sx,96);assert.equal(initial.sy,192);
assert.equal(ctx.rh1523ActorPlan(sources[0],5,512,256,256,72,72),null);
assert.equal(ctx.rh1523ActorPlan(sources[0],256,0,256,256,225,225),null);
for(let frame=0;frame<600;frame++){
 now=frame*1000/60;
 for(let i=0;i<24;i++){
  const f=(frame+i)%48,source=sources[i%4],sx=f%8*256,sy=Math.floor(f/8)*256,w=66+i%9,h=w;
  ctx.rh1523ActorDraw(source,sx,sy,256,256,-w/2,-h,w,h);
  const a=draws.at(-1);
  assert.deepEqual(a.slice(5),[-w/2,-h,w,h]);
  if(a[0]!==source)assert.deepEqual(a.slice(1,5),[f%8*96,Math.floor(f/8)*96,96,96]);
 }
}
const stats=ctx.rh1523Stats().actor;
assert.equal(stats.requests,14400);
assert.equal(stats.builds,4,'one reduced sheet per source, not one per animation frame or citizen');
assert.equal(rasterBuilds,4);assert.ok(stats.hits>13500);
assert.equal(stats.evictions,0);assert.ok(stats.pixels<=stats.budget);
assert.deepEqual(claims,['actor-sheet','actor-sheet','actor-sheet','actor-sheet']);
// A full cache must not discard hot pages to admit other sheets.
for(let frame=0;frame<120;frame++){
 now+=1000/60;
 for(const source of sources)ctx.rh1523ActorDraw(source,0,0,256,256,-36,-72,72,72);
 const extra=sprite();ctx.rh1523ActorDraw(extra,0,0,256,256,-36,-72,72,72);
}
assert.equal(ctx.rh1523Stats().actor.builds,4);
ctx.rh1523ClearActors();assert.equal(ctx.rh1523Stats().actor.pixels,0);
// A mobile renderer starts at a stable 30 Hz while logic observes every rAF.
const q=ctx.rh1523State(1);let presented=0;
for(let n=0;n<120;n++){const t=100+n*1000/60;ctx.rh1523Observe(q,t,14);if(ctx.rh1523Due(q,t))presented++;}
assert.equal(presented,60);assert.equal(q.slow,true);assert.equal(q.tier,1);
// Long gaps which defeated the previous controller now trigger an early fallback.
const desktop=ctx.rh1523State(0);
for(let i=1;i<=9;i++)ctx.rh1523Observe(desktop,i*180,38);
assert.equal(desktop.slow,true);assert.ok(desktop.tier>0);
const healthy=ctx.rh1523State(0);
for(let i=1;i<=800;i++)ctx.rh1523Observe(healthy,i*1000/60,7);
assert.equal(healthy.slow,false);assert.equal(healthy.tier,0);
assert.equal(ctx.rh1523Intersects({left:1180,top:50,w:25,h:25},0,0),false);
ctx.rh1436GroundView={x:0,y:0,w:640,h:360};assert.equal(ctx.rh1523Intersects({left:1180,top:50,w:25,h:25},0,0),true);
console.log('V1523 PASS: 14,400 animated draws with four reusable sheets, stable 30 Hz presentation, responsive long-frame fallback and close-camera culling');
