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

const civic=JSON.parse(readFileSync(folder+'civic-metadata.json','utf8'));
assert.deepEqual(Object.keys(civic).sort(),['activeHerb','hall','herb','store','supply']);
scope.rh1510CivicMeta=civic;
const f=scope.rh1510HallFit({w:550,h:320,doorX:1740,doorY:2038},{naturalWidth:civic.hall.width,naturalHeight:civic.hall.height});
assert.ok(Math.abs(f.left+f.w*civic.hall.door[0]-1740)<.0001,'redesigned guild door preserves interaction X');
assert.ok(Math.abs(f.top+f.h*civic.hall.door[1]-2044)<.0001,'guild door sill follows original entrance');
assert.ok(f.h*civic.hall.doorHeight>=95,'guild entrance is taller than the player silhouette');
assert.ok(civic.hall.windows.some(p=>p.lit)&&civic.hall.windows.some(p=>!p.lit),'varied window illumination');
assert.equal(civic.hall.flames.length,2);
for(const [k,m] of Object.entries(civic)){
 const a=readFileSync(folder+m.file);
 assert.equal(a.toString('ascii',8,12),'WEBP');
 assert.ok(a.length>40000&&a.length<400000,k+' compact alpha sprite');
 assert.ok(m.door[0]>.3&&m.door[0]<.85&&m.door[1]>.85&&m.door[1]<1);
 if(k!=='hall') assert.ok((k==='activeHerb'?350:198)*m.height/m.width*m.doorHeight>=54,k+' doorway human scale');
}
console.log('Civic hall entrance alignment, lighting metadata and proportioned service annexes PASS');

const pathCross=scope.rh1510PathCross;
assert.equal(pathCross({l:50,t:50,r:150,b:90},[[0,70],[200,70]],10),true,'protected route crosses new foundation');
assert.equal(pathCross({l:50,t:50,r:150,b:90},[[0,115],[200,115]],10),false,'open route beside foundation');
assert.equal(pathCross({l:50,t:50,r:150,b:90},[[100,0],[100,40]],12),true,'walking margin protected');
console.log('Vacant-lot path clearance tests PASS');

const market=JSON.parse(readFileSync(folder+'market-metadata.json','utf8'));
assert.deepEqual(Object.keys(market).sort(),['cart','rh1498shelter','rh1498warehouse','stall0','stall1','well']);
for(const [k,m] of Object.entries(market)){
 const a=readFileSync(folder+m.file);
 assert.equal(a.toString('ascii',0,4),'RIFF');
 assert.equal(a.toString('ascii',8,12),'WEBP');
 assert.ok(a.length>10000&&a.length<450000,k+' compact textured alpha art');
 assert.ok(m.width>200&&m.height>200);
}
for(let j=0;j<4;j++){
 const a=readFileSync(folder+'east-ground-'+j+'.webp');
 assert.equal(a.toString('ascii',8,12),'WEBP');
 assert.ok(a.length>30000&&a.length<180000);
}
console.log('Market artwork and 4 additional seamless east terrain chunks PASS');
const districtDir='game-bundle/patches/art-v1511/';
const district=JSON.parse(readFileSync(districtDir+'district-metadata.json','utf8'));
assert.deepEqual(Object.keys(district).sort(),['rh1478East','rh1478Rear','rh1478West','rh1493Longhouse','rh1494Gatehouse','rh1495stepHouse','rh1495workshop','rh1496herbCourt','rh1499bellCourt']);
for(const [k,m] of Object.entries(district)){
 const a=readFileSync(districtDir+m.file);
 assert.equal(a.toString('ascii',0,4),'RIFF');
 assert.equal(a.toString('ascii',8,12),'WEBP');
 assert.ok(a.length>30000&&a.length<500000,k+' compact art');
 assert.ok(m.width>240&&m.height>240);
 for(const p of m.flues)assert.ok(p.length===2&&p.every(x=>x>=0&&x<=1),k+' chimney anchor');
 for(const w of m.windows)assert.ok(w.points.length>=3&&w.points.every(p=>p.every(x=>x>=0&&x<=1)),k+' window coordinates');
}
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1511.js','utf8'),scope);
const doorRows=scope.rh1511DoorRows;
assert.equal(doorRows({x:200,y:130,doorWorldOffset:15,doorHeight:80})[0][0],215);
assert.equal(doorRows({doors:[[210,110,85],[245,115,73]]}).length,2);
assert.equal(doorRows({archWidth:100,archHeight:120}).length,0,'open arch and bell court do not fabricate thresholds');
console.log('Nine eastern district assets and preserved multi-door geometry PASS');

const fortDir='game-bundle/patches/art-v1512/';
const fort=JSON.parse(readFileSync(fortDir+'fortification-metadata.json','utf8'));
assert.deepEqual(Object.keys(fort).sort(),['pottery','spice','tower0','tower1','tower2']);
for(const [k,m] of Object.entries(fort)){
 const a=readFileSync(fortDir+m.file);
 assert.equal(a.toString('ascii',8,12),'WEBP');
 assert.ok(a.length>15000&&a.length<500000,k+' compact alpha art');
 assert.ok(m.width>240&&m.height>240);
}
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1512.js','utf8'),scope);
assert.equal(scope.rh1512MarketVariant({k:'stall1',x:5845,y:2084}),'spice');
assert.equal(scope.rh1512MarketVariant({k:'stall0',x:6240,y:2085}),'pottery');
assert.equal(scope.rh1512MarketVariant({k:'stall0',x:5925,y:1845}),null);
assert.equal(scope.rh1512MarketVariant({k:'stall1',x:6240,y:1890}),null);
const fn=scope.rh1512Noise;
assert.ok(Math.abs(fn(240-.01,240,52,84,1512)-fn(240+.01,240,52,84,1512))<.001,'continuous material noise across tile seam');
assert.notEqual(fn(120,220,52,84,1512),fn(120,460,52,84,1512),'weathering varies across repeated source tiles');
console.log('Five new architectural/merchant assets, four distinct market variants and continuous wall wear PASS');

const rowDir='game-bundle/patches/art-v1513/';
const layout=JSON.parse(readFileSync(rowDir+'layout-metadata.json','utf8'));
assert.deepEqual(Object.keys(layout.shops).sort(),['Apothecary','Bakery','Tailor']);
assert.deepEqual(Object.keys(layout.court).sort(),['rh1474gallery','rh1474rear','rh1474tower']);
for(const [name,m] of Object.entries({...layout.shops,...layout.court})){
 const bytes=readFileSync(rowDir+m.file);
 assert.equal(bytes.toString('ascii',8,12),'WEBP');
 assert.ok(bytes.length>25000&&bytes.length<500000,name+' compact alpha art');
 for(const p of m.flues)assert.ok(p.every(v=>v>=0&&v<=1));
}
for(const [name,m] of Object.entries(layout.shops)){
 const g=m.geometry;
 assert.equal(g.doorWorld[1],1963,'shared straight street entrance line');
 assert.ok(Math.abs(g.left+g.w*m.door[0])<.002);
 assert.ok(Math.abs(g.top+g.h*m.door[1])<.002);
 assert.ok(g.height>=78&&g.doorWidth>=50,name+' believable door scale');
 assert.ok(g.parts.every(p=>p.every((v,i)=>{const u=p[(i+1)%p.length];return v[0]===u[0]||v[1]===u[1]})),name+' square street-aligned footprint');
}
assert.ok(layout.court.rh1474tower.door[0]<.4&&layout.court.rh1474rear.door[0]>.55,'both courtyard houses face each other');
assert.equal(layout.courtyard.routes.length,3,'two outward connections plus shared courtyard crossing');
console.log('Six new aligned assets, street-aligned geometry, original interaction coordinates and inward courtyard PASS');
