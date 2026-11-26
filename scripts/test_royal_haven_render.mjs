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

const westDir='game-bundle/patches/art-v1514/';
const west=JSON.parse(readFileSync(westDir+'layout-metadata.json','utf8'));
assert.deepEqual(Object.keys(west.shops).sort(),['Enchanter','Fletcher','Herbalist']);
assert.equal(west.homeShift,-36);
for(const [name,m] of Object.entries({...west.shops,gate:west.gate})){
 const bytes=readFileSync(westDir+m.file);
 assert.equal(bytes.toString('ascii',8,12),'WEBP');
 assert.ok(bytes.length>25000&&bytes.length<500000,name+' compact transparent art');
 assert.ok(m.width>300&&m.height>300);
}
for(const [name,m] of Object.entries(west.shops)){
 const g=m.geometry;
 assert.equal(g.doorWorld[1],1963);
 assert.ok(Math.abs(g.left+g.w*m.door[0])<.002);
 assert.ok(Math.abs(g.top+g.h*m.door[1])<.002);
 assert.ok(g.height>=78&&g.doorWidth>=50,name+' human-scale entrance');
 assert.ok(g.parts.every(p=>p.every((v,i)=>{const u=p[(i+1)%p.length];return v[0]===u[0]||v[1]===u[1]})));
}
assert.ok(west.gate.geometry.archWidth>=100&&west.gate.geometry.archHeight>=118);
assert.equal(west.gate.geometry.polyParts.length,2);
assert.ok(west.gate.geometry.walk.every(p=>p[0]===west.gate.geometry.walk[0][0]),'straight open passage');
console.log('Four front-facing sprites, recessed homes, preserved shop doors and square passage PASS');

const merchantDir='game-bundle/patches/art-v1515/';
const quarter=JSON.parse(readFileSync(merchantDir+'layout-metadata.json','utf8'));
assert.deepEqual(Object.keys(quarter.shops).sort(),['General Store','Item Shop','Town Residence']);
assert.deepEqual(Object.keys(quarter.civic).sort(),['rh1499bellCourt','rh1499stoneSeat']);
for(const [name,m] of Object.entries({...quarter.shops,...quarter.civic})){
 const asset=readFileSync(merchantDir+m.file);
 assert.equal(asset.toString('ascii',8,12),'WEBP');
 assert.ok(asset.length>25000&&asset.length<500000,name+' compact alpha art');
 assert.ok(m.width>300&&m.height>300);
}
const square=parts=>parts.every(p=>p.every((v,i)=>{const u=p[(i+1)%p.length];return v[0]===u[0]||v[1]===u[1]}));
for(const [name,m] of Object.entries(quarter.shops)){
 const g=m.geometry;
 assert.ok(Math.abs(g.left+g.w*m.door[0])<.002&&Math.abs(g.top+g.h*m.door[1])<.002);
 assert.ok(g.height>=78&&g.doorWidth>=50,name+' human-scale entrance');
 assert.ok(square(g.parts),name+' squared footprint');
}
const general=quarter.shops['General Store'].geometry,item=quarter.shops['Item Shop'].geometry;
assert.deepEqual(general.doorWorld,[2385,1333]);assert.deepEqual(item.doorWorld,[2865,1333]);assert.deepEqual(quarter.shops['Town Residence'].geometry.doorWorld,[3820,1360]);
const maxX=g=>g.doorWorld[0]+Math.max(...g.parts.flat().map(p=>p[0]));
const minX=g=>g.doorWorld[0]+Math.min(...g.parts.flat().map(p=>p[0]));
assert.ok(maxX(general)>=quarter.seam&&minX(item)<=quarter.seam&&maxX(general)-minX(item)<1,'continuous shared wall');
const gap=item.doorWorld[0]+item.left-general.doorWorld[0]-general.left-general.w;
assert.ok(gap>=-30&&gap<=5,'connected merchant silhouettes');
const bell=quarter.civic.rh1499bellCourt.geometry,seat=quarter.civic.rh1499stoneSeat.geometry;
assert.equal(bell.polyParts.length,4);assert.ok(square(bell.polyParts)&&square(seat.polyParts));assert.ok(bell.archWidth>=100&&bell.archHeight>=80);
assert.ok(bell.walk.every(p=>p[0]===bell.walk[0][0]),'straight bell passage');
console.log('Five individualized buildings and civic assets, shared merchant wall, level seat and straight bell passage PASS');

const foundryDir='game-bundle/patches/art-v1516/';
const foundry=JSON.parse(readFileSync(foundryDir+'layout-metadata.json','utf8'));
assert.deepEqual(Object.keys(foundry.shops).sort(),['Armor Smith','Leatherworker','Weapon Smith']);
for(const [name,m] of Object.entries({...foundry.shops,townhouse:foundry.home,gallery:foundry.gallery})){
 const asset=readFileSync(foundryDir+m.file);
 assert.equal(asset.toString('ascii',8,12),'WEBP');
 assert.ok(asset.length>25000&&asset.length<500000,name+' compact detailed alpha art');
 assert.ok(m.width>300&&m.height>300);
}
for(const [name,m] of Object.entries(foundry.shops)){
 const g=m.geometry;
 assert.equal(g.doorWorld[1],1333);
 assert.ok(Math.abs(g.left+g.w*m.door[0])<.01&&Math.abs(g.top+g.h*m.door[1])<.01,name+' aligned threshold');
 assert.ok(g.height>=78&&g.doorWidth>=50,name+' human-scale doors');
 assert.ok(square(g.parts),name+' squared collision shape');
}
assert.deepEqual(foundry.shops['Weapon Smith'].geometry.doorWorld,[350,1333]);
assert.deepEqual(foundry.shops['Armor Smith'].geometry.doorWorld,[805,1333]);
assert.deepEqual(foundry.shops['Leatherworker'].geometry.doorWorld,[1275,1333]);
const flame=foundry.shops['Weapon Smith'].fire;
assert.ok(flame[0]>flame[2]&&flame[0]<flame[2]+flame[4]&&flame[1]>flame[3]&&flame[1]<flame[3]+flame[5],'forge animation anchor inside its furnace clip');
assert.ok(foundry.home.geometry.doorHeight>=80&&foundry.home.geometry.w*foundry.home.doorWidth>=50);
const covered=foundry.gallery.geometry;
assert.equal(covered.polyParts.length,2);assert.ok(square(covered.polyParts)&&covered.openingWidth>=60&&covered.openingHeight>=80);
assert.ok(covered.polyParts.every(q=>q.every(p=>Math.abs(p[0])>=30)),'central gallery passage has no solid footprint');
console.log('Three straight craft facades, townhouse, clear timber gallery and clipped forge fire PASS');
// Execute the forge paint branch in isolation. The animation must use an
// available clock and stay in the defined furnace clip even when cut away.
const flameCalls=[],foundryCtx=vm.createContext({
 rh1516Meta:foundry,rh1444Enabled:true,rh1510Art:Object.fromEntries(Object.entries(foundry.shops).map(([k,m])=>[k,{complete:true,naturalWidth:m.width,naturalHeight:m.height}])),
 c:{save(){},restore(){},beginPath(){},rect(){},clip(){}},performance:{now:()=>12345},p:{x:5000,y:5000},
 rh1432FacadeDraw(){},rh1510WindowTint(){},rh1273Fire:(x,y,w,h,t)=>flameCalls.push(t),rh1273Embers:(x,y,w,h,t)=>flameCalls.push(t),txt(){}
});
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1516.js','utf8'),foundryCtx);
assert.equal(vm.runInContext("rh1516Foundry.draw({name:'Weapon Smith',doorX:350,doorY:1333})",foundryCtx),true);
assert.deepEqual(flameCalls,[12.345,12.345],'animated furnace and embers use the real render clock');
console.log('Foundry furnace paint and time source PASS');
// The replacement home footprints must stay inside previously solid ground.
// This protects established citizen routes and other district collision.
const residentialDir='game-bundle/patches/art-v1517/';
const residential=JSON.parse(readFileSync(residentialDir+'layout-metadata.json','utf8'));
const oldHomeBoxes={
 forward:{y:2393,boxes:[[-145,-78,145,-36],[-86,-37,25,4]]},
 deepstone:{y:2034,boxes:[[-140.6,-64.66,107.06,3.97]]}
};
for(const [key,m] of Object.entries(residential.homes)){
 const g=m.geometry,old=oldHomeBoxes[key],y=g.y??old.y;
 assert.ok(g.h*m.doorHeight>=78&&g.w*m.doorWidth>=47,key+' human-scaled doorway');
 assert.ok(Math.abs(g.dx-g.w/2+g.w*m.door[0]-g.doorWorldOffset)<.001,key+' aligned horizontal entrance');
 assert.ok(Math.abs(g.artDy-g.h+g.h*m.door[1])<.001,key+' aligned vertical entrance');
 assert.ok(m.windows.some(x=>x.lit)&&m.windows.some(x=>!x.lit),key+' non-uniform glass lighting');
 for(const [l,t,r,b] of g.boxes)for(let x=l+.5;x<r;x+=1)for(let yy=t+.5;yy<b;yy+=1)
   assert.ok(old.boxes.some(([ol,ot,or,ob])=>x>ol&&x<or&&y+yy>old.y+ot&&y+yy<old.y+ob),key+' footprint must not consume new walkable land');
 assert.ok(readFileSync(residentialDir+m.file).length>10000);
}
assert.equal(residential.homes.forward.geometry.y,2360);
for(const b of residential.ground){
 assert.ok(b.w*b.h<45000,'bounded cache allocation');
 assert.ok(b.shape.every(([x,y])=>x>=b.x&&x<=b.x+b.w&&y>=b.y&&y<=b.y+b.h));
}
console.log('Two distinct human-scale homes, non-expanding footprints, and bounded organic paving overlays PASS');
// The optimized world-noise grid must reproduce the previous scalar noise
// at every sampled position, including mirrored sides and nonzero origins.
const perfCtx=vm.createContext({});vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1510.js','utf8'),perfCtx);
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1518.js','utf8'),perfCtx);
const prevNoise=(x,y,sx,sy,seed)=>{let a=Math.floor(x/sx),b=Math.floor(y/sy),dx=x/sx-a,dy=y/sy-b,u=dx*dx*(3-2*dx),v=dy*dy*(3-2*dy);let k=perfCtx.rh1510Hash(a,b,seed),l=perfCtx.rh1510Hash(a+1,b,seed),m=perfCtx.rh1510Hash(a,b+1,seed),n=perfCtx.rh1510Hash(a+1,b+1,seed);return (k+(l-k)*u)*(1-v)+(m+(n-m)*u)*v;};
for(const [ox,oy,dx,dy] of [[0,2360,.5,.5],[6460,1200,-.5,.5],[480,2322,1,1],[-28,-14,1,1]]){
 const grid=perfCtx.rh1518NoiseField(130,96,ox,oy,dx,dy,8,11,1513);
 for(let y=0;y<96;y++)for(let x=0;x<130;x++)assert.ok(Math.abs(grid[y*130+x]-prevNoise(ox+x*dx,oy+y*dy,8,11,1513))<1e-7);
}
let q=perfCtx.rh1518CutawayRect({left:200,top:200,w:250,h:300,rh1518LocalPad:8},{a:.7,b:0,c:0,d:.7,e:-70,f:-70},896,504);
assert.ok(q.w*q.h<896*504*.3&&q.x>=0&&q.y>=0&&q.x+q.w<=896&&q.y+q.h<=504);
perfCtx.rh1431InitialTier=()=>1;perfCtx.rh1431Perf={tier:1};perfCtx.rh176Moving=true;
perfCtx.rh1518Begin();assert.equal(perfCtx.rh1518Claim('terrain'),true);assert.equal(perfCtx.rh1518Claim('facade'),false);perfCtx.rh1518End();
perfCtx.rh1431InitialTier=()=>0;perfCtx.rh1431Perf={tier:0};perfCtx.rh176Moving=false;
perfCtx.rh1518Begin();assert.equal(perfCtx.rh1518Claim('terrain'),true);assert.equal(perfCtx.rh1518Claim('facade'),true);assert.equal(perfCtx.rh1518Claim('contact'),false);perfCtx.rh1518End();
perfCtx.W=1280;perfCtx.H=720;
assert.equal(perfCtx.rh1518StreetTiles(0,0).length,4);
assert.equal(perfCtx.rh1518StreetTiles(1,1).length,9);
assert.equal(perfCtx.rh1518StreetTiles(640,360).length,4);
console.log('Optimized world noise, bounded cutaway rectangle, raster budget, and tile coverage PASS');

// Exterior-only 12% zoom and exact inverse cursor projection.
const nav=vm.createContext({W:1280,H:720,WORLD_W:6460,WORLD_H:2600});
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1519.js','utf8'),nav);
const q19=nav.rh1519Camera(3100,1750);
assert.equal(q19.zoom,1.12);assert.ok(Math.abs(q19.w-1280/1.12)<1e-9);
assert.ok(Math.abs((3100-q19.x)*q19.zoom-640)<1e-9);
assert.ok(Math.abs((1750-q19.y)*q19.zoom-360)<1e-9);
const click19=nav.rh1519WorldPoint(640,360,q19.x,q19.y);
assert.ok(Math.hypot(click19.x-3100,click19.y-1750)<1e-9);
const edge19=nav.rh1519Camera(6440,2535);
assert.ok(Math.abs(edge19.x+edge19.w-6460)<1e-9&&edge19.y+edge19.h<=2600+1e-9);
assert.equal(vm.runInContext('rh1519IsBench',nav)({k:'woodbench'}),true);assert.equal(vm.runInContext('rh1519IsBench',nav)({k:'plazaBench'}),true);assert.equal(vm.runInContext('rh1519IsBench',nav)({k:'barrel'}),false);
const walk19=nav.rh1519Walk;
const v19={x:0,y:0};walk19(v19,100,0,()=>false);assert.ok(Math.abs(v19.x-100)<.001&&v19.y===0);
const wall19={x:0,y:0};walk19(wall19,100,0,(x,y)=>x>=20&&x<=38&&Math.abs(y)<100);assert.ok(wall19.x<20&&wall19.y===0);
const corner19={x:0,y:0};for(let i=0;i<14;i++)walk19(corner19,8,0,(x,y)=>x>=20&&x<=38&&Math.abs(y)<8);
assert.ok(corner19.x>38&&Math.abs(corner19.y)>=8,'short corner is bypassed without entering solid footprint');
const diagonal19={x:0,y:0};walk19(diagonal19,50,50,(x,y)=>x>=20&&x<=38&&Math.abs(y)<100);assert.ok(diagonal19.x<20&&diagonal19.y>45);
console.log('Exterior camera projection, viewport edges, no wall tunneling, short-corner assistance and diagonal sliding PASS');
