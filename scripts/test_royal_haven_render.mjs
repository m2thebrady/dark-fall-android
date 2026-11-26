import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const scope=vm.createContext({});
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1510.js','utf8'),scope);
const {rh1457Overlap:overlap,rh1510WeatherPixels:wear}=scope;
const bounds={left:50,top:20,w:100,h:180};
assert.equal(overlap(bounds,200,100,130),true,'behind a building anywhere, not just a marked lane');
assert.equal(overlap(bounds,200,100,205),false,'in front of a building');
assert.equal(overlap(bounds,200,300,130),false,'beside a distant building');
assert.equal(overlap(bounds,200,100,-120),false,'above its roof');
assert.equal(overlap(null,200,100,130),false);
const w=160,h=170,original=new Uint8ClampedArray(w*h*4);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){
 const i=(y*w+x)*4;original.set(x<18?[20,20,20,0]:x<35?[235,174,33,255]:[139,132,117,255],i);
}
const a=original.slice(),b=original.slice(),different=original.slice();
wear(a,w,h,47390,{hearth:true,flues:[[.5,.15]]});
wear(b,w,h,47390,{hearth:true,flues:[[.5,.15]]});
wear(different,w,h,47391,{green:true});
assert.deepEqual(a,b,'deterministic weathering across frames');
assert.notDeepEqual(a,original,'weathering changes visible masonry');
assert.notDeepEqual(a,different,'separate buildings have distinct patina');
let material=0,window=0,n=0;
for(let i=0;i<a.length;i+=4){
 assert.equal(a[i+3],original[i+3],'alpha/silhouette preserved');
 if(original[i+3]===0)assert.deepEqual(a.slice(i,i+4),original.slice(i,i+4),'transparent edges preserved');
 if(original[i]===139){material+=Math.abs(a[i]-original[i]);n++;}
 if(original[i]===235)window+=Math.abs(a[i]-original[i]);
}
assert.ok(material/n>2,'masonry wear is visible');
assert.ok(window/(17*h)<material/n,'bright shop glass and signage relatively protected');
console.log('Royal Haven geometry, deterministic weathering, colour protection and silhouette tests PASS');

const folder='game-bundle/patches/art-v1510/';
const art=JSON.parse(readFileSync(folder+'metadata.json','utf8'));
const expected=['Weapon Smith','Armor Smith','Leatherworker','General Store','Item Shop','Wayfarer Inn','Apothecary','Bakery','Herbalist','Alchemist','Fletcher','Tailor','Storehouse Cellar','Enchanter','Town Residence','The Iron Hearth Tavern'];
assert.deepEqual(Object.keys(art).sort(),expected.sort(),'every named commercial/residential facade has a revised asset');
for(const [name,m] of Object.entries(art)){
 const b=readFileSync(folder+m.file);
 assert.equal(b.toString('ascii',0,4),'RIFF',name);assert.equal(b.toString('ascii',8,12),'WEBP',name);
 assert.ok(b.length>10000&&m.width>100&&m.height>100,name);
 assert.ok(m.door[0]>.25&&m.door[0]<.75&&m.door[1]>.65&&m.door[1]<1.02,name+' entrance alignment');
 for(const p of [...m.flues,...m.lanterns])assert.ok(p.every(v=>v>=0&&v<=1),name+' light/smoke anchor');
}
console.log('All 16 revised exterior sprites and entrance/smoke/light metadata PASS');
const homes=JSON.parse(readFileSync(folder+'home-metadata.json','utf8'));
assert.equal(Object.keys(homes).length,6);
for(const [name,m] of Object.entries(homes)){
 const b=readFileSync(folder+m.file);
 assert.equal(b.toString('ascii',0,4),'RIFF',name);assert.equal(b.toString('ascii',8,12),'WEBP',name);
 assert.ok(m.width>100&&m.height>100&&m.door[0]>.2&&m.door[0]<.8&&m.door[1]>.8&&m.door[1]<=1,name);
}
console.log('Six residential facade upgrades PASS');

const variant=JSON.parse(readFileSync(folder+'variant-metadata.json','utf8'))['variant:cellar-relocated'];
assert.ok(Math.abs(variant.door[0]-193/650)<.003,'relocated cellar artwork uses its actual door anchor');
assert.equal(readFileSync(folder+variant.file).toString('ascii',8,12),'WEBP');
console.log('Relocated cellar entrance variant PASS');

const shoulder=scope.rh1510ShoulderTile;
assert.equal(shoulder(0,0).key,'0-0');
assert.equal(shoulder(2160,650).sx,1080);
assert.equal(shoulder(2160,650).sy,325);
assert.equal(shoulder(2880,650).key,'1-0');
assert.equal(shoulder(2880,1300).sx,0);
assert.equal(shoulder(2880,1300).sy,0);
assert.equal(shoulder(5760,1300),null,'new overlays never touch fallback terrain beyond the original painted town');
for(let i=0;i<2;i++)for(let j=0;j<2;j++){
 const p=readFileSync(folder+'shoulder-'+i+'-'+j+'.webp');
 assert.equal(p.toString('ascii',8,12),'WEBP');
 assert.ok(p.length>5000&&p.length<120000,'sparse shoulder overlay stays small');
}
const gate=readFileSync(folder+'forest-gate-revised.webp');
assert.equal(gate.toString('ascii',8,12),'WEBP');
assert.ok(gate.length>30000&&gate.length<400000);
console.log('Gate artwork and seamless world-aligned shoulder atlas PASS');
