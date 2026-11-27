// The foundry district: level, distinct trade facades and real pedestrian alleys.
// Game interaction anchors and the party's scale are deliberately unchanged.
const rh1516Foundry=(()=>{
 const names=new Set(Object.keys(rh1516Meta.shops));
 const model=s=>rh1516Meta.shops[s.name];
 const handles=s=>rh1444Enabled&&names.has(s.name);
 const ready=s=>{const a=rh1510Art[s.name];return handles(s)&&a?.complete&&a.naturalWidth===model(s).width&&a.naturalHeight===model(s).height;};
 const image=s=>ready(s)?rh1510Art[s.name]:null;
 const fit=s=>{if(!ready(s))return null;const g=model(s).geometry;return {left:s.doorX+g.left,top:s.doorY+g.top,w:g.w,h:g.h};};
 const collides=(s,x,y)=>handles(s)&&model(s).geometry.parts.some(poly=>rh1472Poly(poly,x-s.doorX,y-s.doorY));
 const depth=s=>s.doorY;
 const flues=s=>ready(s)?model(s).flues:null;
 const lanterns=s=>ready(s)?model(s).lanterns:null;
 function flame(s,b){
  const f=model(s).fire;if(!f)return;
  const [fx,fy,l,t,w,h]=f,x=b.left+b.w*fx,y=b.top+b.h*fy,now=performance.now()/1000;
  c.save();try{
   c.beginPath();c.rect(b.left+b.w*l,b.top+b.h*t,b.w*w,b.h*h);c.clip();
   rh1273Fire(x,y,b.w*w*.83,b.h*h*.92,now,5);
   rh1273Embers(x,y,b.w*w*.66,b.h*h*.68,now,5);
  }finally{c.restore();}
 }
 function draw(s){const b=fit(s);if(!b)return false;rh1432FacadeDraw(image(s),b.left,b.top,b.w,b.h);rh1510WindowTint(model(s).windows,b.left,b.top,b.w,b.h);flame(s,b);if(Math.hypot(p.x-s.doorX,p.y-s.doorY)<280)txt(s.name,s.doorX,b.top-8,13,'#d8c5a0');return true;}
 function mapSite(s){if(!handles(s))return false;mc.fillStyle='#85867c';for(const q of model(s).geometry.parts){rh1472Trace(mc,q,-s.doorX,-s.doorY,.1);mc.fill();}return true;}
 return {handles,ready,image,fit,collides,depth,flues,lanterns,draw,mapSite};
})();
const rh1516Routes=[
 {points:[[90,1354],[90,1135],[580,1135],[1040,1135],[1530,1135],[1530,1354]],half:11},
 {points:[[90,1354],[350,1354],[580,1354],[805,1354],[1040,1354],[1275,1354],[1530,1354]],half:13},
 {points:[[580,1135],[580,1301],[580,1354]],half:12},
 {points:[[1040,1135],[1040,1354]],half:12},
 {points:[[3910,1714],[4075,1714],[4230,1714]],half:6}
];
function rh1516PrepareStreet(){
 for(const r of rh1516Routes){const {points,half}=r,pad=half+7,x=Math.min(...points.map(p=>p[0]))-pad,y=Math.min(...points.map(p=>p[1]))-pad;rh1467Frontages.push({points,half,x,y,w:Math.ceil(Math.max(...points.map(p=>p[0]))-x+pad),h:Math.ceil(Math.max(...points.map(p=>p[1]))-y+pad),walk1516:true});}
}
// Ground-only, world-seeded worn threshold apron. Organic edges follow the
// old road rather than introducing platform-like square slabs or obstacles.
const rh1516StreetShapes=[
 {key:'forge',x:102,y:1319,w:495,h:75,poly:[[113,1329],[200,1325],[350,1327],[469,1328],[534,1324],[584,1327],[584,1368],[525,1382],[402,1384],[293,1381],[206,1378],[113,1373]],seed:15161,kind:'soot'},
 {key:'armor',x:579,y:1319,w:488,h:75,poly:[[584,1327],[620,1328],[760,1330],[947,1328],[1051,1337],[1052,1370],[976,1377],[835,1381],[701,1384],[584,1372]],seed:15162,kind:'metal'},
 {key:'leather',x:1042,y:1324,w:470,h:72,poly:[[1051,1337],[1110,1330],[1240,1331],[1380,1328],[1499,1334],[1504,1369],[1399,1380],[1260,1382],[1125,1384],[1052,1370]],seed:15163,kind:'dust'}
];
const rh1516StreetSurfaces=new Map();
function rh1516StreetGround(cx,cy){
 if(!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 let built=0;
 for(const b of rh1516StreetShapes){
  if(b.x+b.w<cx||b.x>cx+W||b.y+b.h<cy||b.y>cy+H)continue;
  let a=rh1516StreetSurfaces.get(b.key);
  if(!a&&built<1){
   a=rhSurface(b.w,b.h);const g=a.getContext('2d',{willReadFrequently:true});rh1406Pave(g,rh191PaveArt,b.x,b.y,b.w,b.h,.48);
   g.globalCompositeOperation='source-atop';
   const tone=g.createLinearGradient(0,0,0,b.h);tone.addColorStop(0,b.kind==='soot'?'#24251e86':'#302e253c');tone.addColorStop(.5,b.kind==='dust'?'#8c775031':'#50493924');tone.addColorStop(1,'#41523836');g.fillStyle=tone;g.fillRect(0,0,b.w,b.h);
   // A little quieter surface wear at ground level: small dark pits, grit,
   // intermittent moss near the sides, never a new collision object.
   for(let i=0;i<Math.ceil(b.w*.5);i++){
    const z=rh1510Hash(i,4,b.seed),x=4+rh1510Hash(i,1,b.seed)*(b.w-8),y=4+rh1510Hash(i,3,b.seed)*(b.h-8);
    g.fillStyle=z<.26?'#2b272650':z>.7?'#ae98723c':'#4a513c42';
    g.beginPath();g.ellipse(x,y,1+z*3,.5+z*.9,z*3,0,Math.PI*2);g.fill();
   }
   g.globalCompositeOperation='destination-in';rh1472Trace(g,b.poly,b.x,b.y);g.fillStyle='#fff';g.fill();
   g.globalCompositeOperation='source-atop';rh1511PavingEdge(g,b,b.poly,b.seed);
   g.globalCompositeOperation='source-over';rh1516StreetSurfaces.set(b.key,a);built++;
  }
  if(a)c.drawImage(a,b.x,b.y);
 }
}
function rh1516DistrictStatus(full=false){
 const shops=Object.entries(rh1516Meta.shops).map(([name,m])=>{
  const s=sites.find(o=>o.name===name),b=rh1365SiteBounds(s),im=rh1510Art[name],g=m.geometry;
  let footprint=null;
  if(full){let samples=0,bad=0;for(const poly of g.parts){const l=Math.min(...poly.map(p=>p[0])),r=Math.max(...poly.map(p=>p[0])),t=Math.min(...poly.map(p=>p[1])),bottom=Math.max(...poly.map(p=>p[1]));for(let x=l+1;x<r;x+=7)for(let y=t+1;y<bottom;y+=7){samples++;if(!blocked(s.doorX+x,s.doorY+y))bad++;}}footprint={samples,bad};}
  return {name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,door:[s.doorX,s.doorY],artDoor:b?[b.left+b.w*m.door[0],b.top+b.h*m.door[1]]:null,doorHeight:b?b.h*m.doorHeight:0,doorWidth:b?b.w*m.doorWidth:0,bounds:b,flues:m.flues,fire:name==='Weapon Smith'?m.fire:null,footprint,approach:full?rh1513PathCheck([[s.doorX,s.doorY+15],[s.doorX,s.doorY+32]],8):null};
 });
 const g=rh1462Galleries.find(o=>o.x===580&&o.y===1301),im=rh1462Art.timber,m=rh1516Meta.gallery,b=g&&rh1462Bounds(g),h=rh1464Homes.find(o=>o.k==='townhouse'),hi=rh1464Art.townhouse,hm=rh1516Meta.home,hb=h&&rh1464Bounds(h);
 return {shops,gallery:{ready:!!g&&!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,bounds:b,opening:full?rh1511OpeningClear(im,m.openings):null,walk:full?rh1513PathCheck([[580,1160],[580,1354]],12):null,piers:full&&g?g.polyParts.map(poly=>{const x=poly.reduce((v,p)=>v+p[0],0)/poly.length,y=poly.reduce((v,p)=>v+p[1],0)/poly.length;return blocked(g.x+x,g.y+y);}):null},townhouse:{ready:!!h&&!!hi?.complete&&hi.naturalWidth===hm.width&&hi.naturalHeight===hm.height,bounds:hb,door:h?rh1511DoorRows(h)[0]:null,artDoor:hb?[hb.left+hb.w*hm.door[0],hb.top+hb.h*hm.door[1]]:null,approach:full&&h?rh1513PathCheck([[h.door[0],h.door[1]+14],[h.door[0],h.door[1]+19]],6):null},surfaces:[...rh1516StreetSurfaces.keys()],routes:full?rh1516Routes.map(r=>rh1513PathCheck(r.points,Math.min(10,r.half))):null};
}
function rh1516ReviewDistrict(key){const pts={forge:[350,1370],armor:[805,1380],leather:[1275,1390],corridor:[580,1255],townhouse:[4230,1535]};if(!pts[key])return false;[p.x,p.y]=pts[key];return true;}
