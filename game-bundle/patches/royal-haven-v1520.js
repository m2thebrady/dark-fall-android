// Landmark renewal: measured doorway positions, natural footing and light anchors.
// The new art replaces the old bitmap source, not the gameplay site.
const rh1520ApproachCache=new Map();
let rh1520SeatRemoved=null;
var rh1520Installed=false,rh1520CellarLot=null;
function rh1520MetaFor(s){return s.name==='Caster Guild'?rh1520Meta.mage:s.type==='cave'?rh1520Meta.cave:s.name==='Storehouse Cellar'?rh1520Meta.cellar:null;}
function rh1520CellarReady(s){return rh1520Installed&&s.name==='Storehouse Cellar'&&!!rh1510Upgrade(s);}
function rh1520CellarGeometry(s){
 if(rh1520CellarLot?.site===s)return rh1520CellarLot.b;
 const m=rh1520Meta.cellar,old=rh1328Foot[s.name],right=old?.[1]??s.w*.99*(1-m.door[0]);
 // A slightly narrower footprint keeps the recessed loading bay within its
 // old lot, while the original interactive doorway remains fixed.
 const w=Math.min(s.w*.99,(right+2)/(1-m.door[0])),h=w*m.height/m.width;
 return {left:s.doorX-w*m.door[0],top:s.doorY+4-h*m.door[1],w,h,base:s.doorY+4+h*(1-m.door[1])};
}
function rh1520CellarFit(s){return rh1520CellarReady(s)?rh1520CellarGeometry(s):null;}
function rh1520CellarDraw(s){
 const b=rh1520CellarFit(s);if(!b)return false;
 rh1432FacadeDraw(rh1510Upgrade(s),b.left,b.top,b.w,b.h);
 rh1510WindowTint(rh1520Meta.cellar.windows,b.left,b.top,b.w,b.h);
 if(Math.hypot(p.x-s.doorX,p.y-s.doorY)<280)txt(s.name,s.doorX,b.top-8,13,'#d8c5a0');
 return true;
}
function rh1520Install(){
 const site=sites.find(s=>s.name==='Storehouse Cellar');
 if(site&&rh1328Foot[site.name]){
  const old=rh1328Foot[site.name],b=rh1520CellarGeometry(site);
  rh1520CellarLot={site,b};
  rh1328Foot[site.name]=[Math.max(old[0],b.left-site.doorX+4),Math.min(old[1],b.left+b.w-site.doorX-4)];
 }
 rh1520Installed=true;
 // The old stone seat was implemented as a miniature building and survived
 // the prior furniture cleanup. Remove both its sprite and its footprint.
 const i=rh1464Homes.findIndex(o=>o.k==='rh1499stoneSeat');
 if(i>=0){const [o]=rh1464Homes.splice(i,1);rh1520SeatRemoved={x:o.x,y:o.y-10};rh1514RemovedBenches.push({k:'stoneSeat',x:o.x,y:o.y-10});}
}
function rh1520ApproachSpec(s){
 const key=s.name,x=s.doorX,y=s.doorY,wide=s.name==='Caster Guild'?116:s.type==='cave'?78:65,depth=s.type==='cave'?104:82;
 // Only surface shading; sparse broken outer edges blend into the old paving.
 const shape=[[x-wide*.81,y-9],[x+wide*.74,y-8],[x+wide*.92,y+18],[x+wide*.74,y+depth*.54],
  [x+wide*.39,y+depth],[x-wide*.47,y+depth-7],[x-wide*.77,y+depth*.7],[x-wide,y+depth*.25]];
 const l=Math.floor(Math.min(...shape.map(p=>p[0])))-5,t=Math.floor(Math.min(...shape.map(p=>p[1])))-5;
 return {key,x:l,y:t,w:Math.ceil(Math.max(...shape.map(p=>p[0])))-l+5,h:Math.ceil(Math.max(...shape.map(p=>p[1])))-t+5,shape,
  kind:s.type==='cave'?'damp':'threshold',seed:s.type==='cave'?15203:s.name==='Caster Guild'?15201:15202};
}
function rh1520ApproachGround(cx,cy){
 if(!rh191PaveArt?.complete||rh191PaveArt.naturalWidth<2)return;
 for(const s of sites){
  if(!rh1520MetaFor(s))continue;
  const b=rh1520ApproachSpec(s);if(b.x+b.w<cx||b.x>cx+W||b.y+b.h<cy||b.y>cy+H)continue;
  let a=rh1520ApproachCache.get(b.key);
  if(!a&&rh1518Claim('landmark-approach')){a=rh1517BuildWear(b);rh1520ApproachCache.set(b.key,a);}
  if(a){c.save();c.globalAlpha=s.type==='cave'?.76:.82;c.drawImage(a,b.x,b.y);c.restore();}
 }
}
function rh1520LandmarkStatus(full=false){
 const entries=sites.filter(s=>rh1520MetaFor(s)).map(s=>{
  const m=rh1520MetaFor(s),im=s.type==='cave'?rh193Art.cave:s.name==='Caster Guild'?rh193Art.mage:rh1510Upgrade(s);
  const b=rh1365SiteBounds(s),door=[s.doorX,s.doorY+4];
  let approach=null,solid=null;
  if(full){
   // The existing interaction remains at the same world position; sample its
   // actual approach, with the old guild and cave floor collision unchanged.
   approach=rh1513PathCheck([[s.doorX,s.doorY+17],[s.doorX,s.doorY+40],[s.doorX,s.doorY+68]],8);
   solid=blocked(s.doorX,s.doorY-55);
  }
  return {name:s.name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,bounds:b,door,
   artDoor:b?[b.left+b.w*m.door[0],b.top+b.h*m.door[1]]:null,
   doorWidth:b?b.w*m.doorWidth:0,doorHeight:b?b.h*m.doorHeight:0,approach,solid};
 });
 return {entries,surfaces:[...rh1520ApproachCache.keys()],seatRemoved:!!rh1520SeatRemoved,seatClear:full&&rh1520SeatRemoved?!blocked(rh1520SeatRemoved.x,rh1520SeatRemoved.y):null};
}
function rh1520ReviewLandmark(key){
 const name={mage:'Caster Guild',cave:'Dark Guild Cave',cellar:'Storehouse Cellar'}[key],s=sites.find(o=>o.name===name);
 if(!s)return false;
 // A little south of each entrance: exact review only via graphicsAudit.
 p.x=s.doorX+(key==='cellar'?83:0);p.y=s.doorY+(key==='cellar'?66:90);rh199Reset();return true;
}
