import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root='game-bundle/patches/',meta=JSON.parse(readFileSync(root+'art-v1522/frontages.json'));
const art=readFileSync(root+'art-v1522/frontages.webp');
assert.equal(art.subarray(0,4).toString(),'RIFF');assert.equal(art.subarray(8,12).toString(),'WEBP');assert.ok(art.length<250000);
// All rectangles stay in the one texture and are on the known open forecourts.
assert.equal(meta.length,4);assert.equal(meta.flatMap(r=>r.doors).length,12);
assert.equal(new Set(meta.flatMap(r=>r.doors.map(d=>d.material))).size,12);
for(const r of meta){
 assert.ok(r.sx>=0&&r.sy>=0&&r.sx+r.w<=1792&&r.sy+r.h<=448);
 assert.ok(r.x>=0&&r.x+r.w<=6460&&r.y+r.h<=2600);
 assert.ok(r.doors.every(d=>d.x>=r.x&&d.x<=r.x+r.w&&d.y>=r.y&&d.y<=r.y+r.h));
}
const displays=['Weapon Smith','Armor Smith','Leatherworker','General Store','Item Shop','Herbalist','Bakery','Fletcher','Keep'].map((name,i)=>({name,x:200+i*150,y:1425}));
const prop={k:'crate',x:230,y:1395},hard={k:'crate',x:470,y:1395};
const furniture=[{x:6045,y:2015}],render=[];
const ctx=vm.createContext({rh1522Frontages:meta,rh1522ArtData:'data:image/webp;base64,'+art.toString('base64'),
 Image:class{complete=true;naturalWidth=1792;naturalHeight=448;},marketDisplays:displays,
 rh117Props:[prop,hard],rh1519Soft:new Set([prop]),rh1475Furniture:furniture,
 blocked:(x,y)=>displays.some(d=>Math.abs(x-d.x)<46&&Math.abs(y-d.y)<15)||furniture.some(o=>o.x===x&&o.y===y),
 rh1513PathCheck:()=>({samples:11,bad:0}),c:{drawImage:(...args)=>render.push(args)}});
vm.runInContext(readFileSync(root+'royal-haven-v1522.js','utf8'),ctx);
ctx.rh1522Install();let a=ctx.rh1522FrontageStatus(true);
assert.equal(a.removed.length,8);assert.ok(a.removed.every(o=>o.wasSolid&&o.clear));assert.equal(displays.length,1);
assert.equal(displays[0].name,'Keep');assert.equal(prop.y,1365);assert.equal(hard.y,1395);assert.ok(a.solidMarket);
ctx.rh1522Ground(0,1250,1000,500,false);assert.equal(render.length,0);
ctx.rh1522Ground(0,1250,1000,500,true);assert.equal(render.length,1);
ctx.rh1522Ground(2160,1250,1100,500,true);assert.equal(render.length,2);
ctx.rh1522Ground(0,0,1000,500,true);assert.equal(render.length,2);
assert.equal(ctx.rh1522FrontageStatus().stats.maxVisible,1);
console.log('V1522: four compact texture treatments, twelve distinct entrances, targeted kiosk removal, passable stock relocation, and viewport culling PASS');
