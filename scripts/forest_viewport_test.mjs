import vm from 'node:vm';
import fs from 'node:fs';
import assert from 'node:assert/strict';
let rect={left:0,top:44,x:0,y:44,width:2048,height:1036},callbacks=[],writes=0;
const canvas={_w:1280,_h:720,get width(){return this._w},set width(v){this._w=v;writes++},get height(){return this._h},set height(v){this._h=v;writes++},getBoundingClientRect:()=>rect,parentElement:{getBoundingClientRect:()=>rect}};
const wrap={getBoundingClientRect:()=>({x:0,y:0,width:rect.width,height:rect.height+rect.top}),style:{setProperty(){}}};
const ctx={canvas,thornMobileLite:false,innerWidth:2048,innerHeight:1080,started:false,matchMedia:()=>({matches:rect.width<=800}),document:{getElementById:()=>wrap,addEventListener(){}},requestAnimationFrame:f=>callbacks.push(f),addEventListener(){}};
ctx.window=ctx;vm.createContext(ctx);vm.runInContext(fs.readFileSync('game-bundle/patches/forest-v1539.js','utf8'),ctx);
const sizes=[[2048,1036],[1920,1036],[1280,676],[2560,1036],[3440,1396],[3840,2116],[780,390],[390,844],[360,780],[1024,768],[800,450],[1024,600],[2732,2048]];
for(const [w,h] of sizes){
 rect={x:0,y:0,left:0,top:0,width:w,height:h};
 ctx.df1539Resize();
 const a=ctx.DarkFallForestViewport();
 assert(a.logical[0]===a.backing[0]&&a.logical[1]===a.backing[1]);
 assert(a.area<=a.cap);assert(a.logical[0]<=2400&&a.logical[1]<=1900);
 assert(a.scaleMismatch<.005);assert(a.pointerError<1e-8);
 const before=writes;ctx.df1539Resize();assert(writes===before);
 ctx.df1539Schedule();ctx.df1539Schedule();assert(callbacks.length===1);callbacks.shift()();
 console.log(w+'x'+h,'=>',a.logical.join('x'),'pixels',a.area,'scale error',a.scaleMismatch.toFixed(5));
}
console.log('Viewport geometry/pointer/deduplicated resize PASS, '+sizes.length+' cases');
