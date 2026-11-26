// V1510 Royal Haven: material wear at the existing display-art cache resolution
// and a local, depth-aware cutaway. No footprint, door or collision changes.
let rh1510FacadeContext=null,rh1510CutawayCanvas=null;
function rh1510Clamp(v){return Math.min(1,Math.max(0,v));}
function rh1510Hash(x,y,seed){
 let n=Math.imul(x+1,374761393)^Math.imul(y+1,668265263)^Math.imul(seed,1274126177);
 n=Math.imul(n^(n>>>13),1274126177);return ((n^(n>>>16))>>>0)/4294967295;
}
function rh1510Seed(b){return ((Math.round(b.left)*73856093)^(Math.round(b.top)*19349663))>>>0;}
function rh1510Field(w,h,sx,sy,seed){
 const cols=Math.ceil(w/sx)+2,rows=Math.ceil(h/sy)+2,grid=new Float32Array(cols*rows);
 for(let j=0;j<rows;j++)for(let i=0;i<cols;i++)grid[j*cols+i]=rh1510Hash(i,j,seed);
 const ix=new Int32Array(w),fx=new Float32Array(w);
 for(let x=0;x<w;x++){ix[x]=Math.floor(x/sx);const f=x/sx-ix[x];fx[x]=f*f*(3-2*f);}
 const out=new Float32Array(w*h);
 for(let y=0;y<h;y++){
  const j=Math.floor(y/sy),f=y/sy-j,t=f*f*(3-2*f),o=j*cols;
  for(let x=0;x<w;x++){const k=o+ix[x],u=fx[x],a=grid[k]+(grid[k+1]-grid[k])*u,b=grid[k+cols]+(grid[k+cols+1]-grid[k+cols])*u;out[y*w+x]=a+(b-a)*t;}
 }
 return out;
}
// Preserve source silhouettes and details. Wear follows material colour, rather than
// stamping identical decals over windows, signs, roof tiles and timber.
function rh1510WeatherPixels(data,w,h,seed,style={}){
 const broad=rh1510Field(w,h,46,39,seed+11),patch=rh1510Field(w,h,13,11,seed+41),
       rain=rh1510Field(w,h,4,62,seed+83),fine=rh1510Field(w,h,2.8,3.6,seed+107);
 const bottom=new Int32Array(w);bottom.fill(-1);
 for(let x=0;x<w;x++)for(let y=h-1;y>=0;y--)if(data[(y*w+x)*4+3]>224){bottom[x]=y;break;}
 const profile=rh1510Hash(2,5,seed),damp=(.8+profile*.65)*(style.green?1.30:1);
 const flues=(style.flues||[]).filter(q=>Array.isArray(q)&&q.length>=2&&q.every(Number.isFinite));
 const sootStrength=style.hearth?1.0:.55;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const j=y*w+x,i=j*4,a=data[i+3];if(a<225)continue;
  const r=data[i],g=data[i+1],b=data[i+2],l=.299*r+.587*g+.114*b,span=Math.max(r,g,b)-Math.min(r,g,b);
  // Lit windows, fabric, sign paint and cool glass retain their original contrast.
  const vivid=rh1510Clamp((span-35)/48),light=rh1510Clamp((l-158)/62),guard=(1-vivid*.88)*(1-light*.58);
  const plaster=rh1510Clamp((l-89)/59)*rh1510Clamp((38-span)/29);
  const timber=rh1510Clamp((r-b-12)/35)*rh1510Clamp((141-l)/60);
  const stone=rh1510Clamp((l-43)/47)*(1-vivid*.74);
  const ground=rh1510Clamp(1-(bottom[x]-y)/(22+profile*22))*rh1510Clamp((y/h-.51)/.33);
  const stain=rh1510Clamp((broad[j]-.45)*2.3)*(.42+.58*patch[j]);
  const drip=rh1510Clamp((rain[j]-.57)*3.1)*rh1510Clamp((broad[j]-.21)*1.6);
  const chip=rh1510Clamp((patch[j]-.57)*3.1)*rh1510Clamp((fine[j]-.28)*1.42);
  const lichen=rh1510Clamp((patch[j]-.54)*3.3)*rh1510Clamp((fine[j]-.23)*1.6)*(ground*.80+stain*.20);
  // Broken patches of limewash expose the darker foundation, with ragged pale edges.
  const peel=plaster*rh1510Clamp((broad[j]-.57)*4.8)*rh1510Clamp((patch[j]-.40)*3.6);
  const wearEdge=peel*rh1510Clamp((fine[j]-.56)*3.1);
  let soot=0;
  for(const [u,v] of flues){const dx=(x-u*w)/(11+w*.013),dy=(y-v*h)/(24+h*.035);
   if(dy>-.15&&dy<1.7&&Math.abs(dx)<1.6)soot=Math.max(soot,Math.exp(-dx*dx*2)*rh1510Clamp(1-dy/1.7)*(.5+.5*rain[j]));}
  const grit=(fine[j]-.5)*(7+plaster*12+stone*4)+(rh1510Hash(x,y,seed+179)-.5)*3.2;
  const weather=guard*(grit+plaster*(chip*24-stain*39-drip*22)+stone*((patch[j]-.5)*17-stain*19-drip*12)
                       +timber*(chip*12-stain*10-drip*6)-ground*(10+patch[j]*17)*damp
                       -peel*24+wearEdge*16-soot*40*sootStrength);
  const moss=guard*stone*lichen*damp;
  data[i]=r+weather-moss*13+peel*5;data[i+1]=g+weather+moss*11;data[i+2]=b+weather-moss*18-peel*5;
 }
}
function rh1510WeatherKey(w,h){
 const b=rh1510FacadeContext;if(!b||w<48||h<48||Math.abs(w-b.w)>Math.max(5,b.w*.035)||Math.abs(h-b.h)>Math.max(5,b.h*.035))return null;
 return rh1510Seed(b);
}
function rh1510WeatherRaster(g,w,h,seed){
 if(seed===null)return;
 // Cached once at world display resolution, never read back from the live game canvas.
 try{const im=g.getImageData(0,0,w,h);const style=rh1510FacadeContext?.style||{};
 if(rh1510FacadeContext?.upgrade){
  const original=im.data.slice();rh1510WeatherPixels(im.data,w,h,seed,style);
  for(let i=0;i<im.data.length;i+=4)for(let k=0;k<3;k++)im.data[i+k]=original[i+k]+(im.data[i+k]-original[i+k])*.35;
 }else rh1510WeatherPixels(im.data,w,h,seed,style);g.putImageData(im,0,0);}catch(_){}
}
function rh1510Upgrade(s){const a=rh1510Art[s.name];return a?.complete&&a.naturalWidth>1?a:null;}
function rh1510Legacy(s){return !!rh1510Upgrade(s)&&!!rh1510ArtMeta[s.name]?.legacy;}
function rh1510ArtPoints(s,key){return rh1510Upgrade(s)?rh1510ArtMeta[s.name]?.[key]:null;}
function rh1510SiteBounds(b,s){
 const fit=b||{left:s.x,top:s.y,w:s.w,h:s.h};
 return {...fit,primary:rh1451SiteArt(s),upgrade:rh1510Upgrade(s),style:{hearth:s.type==='forge'||s.type==='tavern'||s.type==='inn'||s.name==='Bakery',
  green:s.name==='Herbalist'||s.name==='Apothecary'||s.type==='home',flues:rh1451SiteFlues(s)}};
}
function rh1457Overlap(b,base,x,y){
 // This includes the feather around the 68-unit player, not just the centre.
 return !!b&&base>y+.5&&b.left<x+54&&b.left+b.w>x-54&&b.top<y+20&&b.top+b.h>y-94;
}
function rh1510Mask(g,x,y){
 // The centre exposes the whole sprite; the outer edge blends into the untouched roof.
 g.save();g.translate(x,y-31);g.scale(54,63);
 const gradient=g.createRadialGradient(0,0,0,0,0,1);
 gradient.addColorStop(0,'rgba(0,0,0,.94)');gradient.addColorStop(.56,'rgba(0,0,0,.92)');
 gradient.addColorStop(.76,'rgba(0,0,0,.53)');gradient.addColorStop(1,'rgba(0,0,0,0)');
 g.globalCompositeOperation='destination-out';g.globalAlpha=1;g.fillStyle=gradient;g.fillRect(-1,-1,2,2);g.restore();
}
function rh1457Facade(b,base,draw){
 const previous=rh1510FacadeContext;rh1510FacadeContext=b||null;
 try{
  if(!rh1457Overlap(b,base,p.x,p.y)){draw();return;}
  const main=c,w=main.canvas.width,h=main.canvas.height;
  // One reusable layer at the adaptive backing resolution; only allocated for an occluder.
  // Punching a hole into this isolated layer never erases the street or the player.
  let layer=rh1510CutawayCanvas;
  if(!layer||layer.width!==w||layer.height!==h)layer=rh1510CutawayCanvas=rhSurface(w,h);
  const g=layer.getContext('2d'),transform=main.getTransform();
  g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,w,h);
  g.save();
  try{
   g.setTransform(transform);g.imageSmoothingEnabled=main.imageSmoothingEnabled;g.imageSmoothingQuality=main.imageSmoothingQuality;
   g.globalAlpha=1;g.globalCompositeOperation='source-over';
   c=g;try{draw();}finally{c=main;}
   rh1510Mask(g,p.x,p.y);
  }finally{g.restore();c=main;}
  main.save();try{main.setTransform(1,0,0,1,0,0);main.drawImage(layer,0,0);}finally{main.restore();}
 }finally{rh1510FacadeContext=previous;}
}

// V1510 street integration: use each facade's true lower alpha contour, not
// a rectangular lot. Contact shadows, damp edges, stone fragments and worn
// thresholds are ground-only, cached and independent of collision or doors.
const rh1510GroundCache=new Map();
let rh1510GroundBuilds=0,rh1510GroundPixels=0;
function rh1510GroundReset(){rh1510GroundCache.clear();rh1510GroundPixels=0;rh1510GroundBuilds=0;}
function rh1510GroundBuild(b,im,site){
 const seed=rh1510Seed(b),sw=Math.max(8,Math.ceil(b.w/3)),sh=Math.max(8,Math.ceil(b.h/3));
 const silhouette=rhSurface(sw,sh),sg=silhouette.getContext('2d',{willReadFrequently:true});
 sg.drawImage(im,0,0,sw,sh);
 const pixels=sg.getImageData(0,0,sw,sh).data;
 const pad=28,top=Math.floor(b.top+b.h-Math.min(142,b.h*.34)),left=Math.floor(b.left-pad);
 const w=Math.ceil(b.w+2*pad),h=Math.ceil(b.top+b.h+39-top);
 const canvas=rhSurface(w,h),g=canvas.getContext('2d');
 const type=site.type,green=site.name==='Herbalist'||site.name==='Apothecary'||type==='home',soot=type==='forge'||site.name==='Bakery';
 const pale=site.name==='Bakery',wood=site.name==='Fletcher'||site.name==='Leatherworker';
 const groundY=[];
 function spot(x,y,rx,ry,color){
  g.save();g.translate(x,y);g.scale(rx,ry);
  const r=g.createRadialGradient(0,0,.10,0,0,1);r.addColorStop(0,color);r.addColorStop(.62,color);r.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=r;g.fillRect(-1,-1,2,2);g.restore();
 }
 for(let xx=0;xx<sw;xx+=2){
  let yy=sh-1;while(yy>sh*.66&&pixels[(yy*sw+xx)*4+3]<155)yy--;
  if(yy<=sh*.66)continue;
  const x=b.left+xx*b.w/sw-left,y=b.top+(yy+.5)*b.h/sh-top,k=rh1510Hash(xx,0,seed);
  if(y<8||y>h-18)continue;
  groundY.push([x,y]);
  // Uneven soil/cobble boundary, tight dark contact and broad natural grime.
  spot(x,y+3,13+k*13,5+k*5,'rgba(26,29,23,.115)');
  spot(x,y+9,19+k*14,7+k*9,soot?'rgba(39,34,29,.082)':'rgba(62,57,44,.070)');
  if(k>.43)spot(x+2,y+7,9+k*8,4+k*4,green?'rgba(64,75,43,.13)':'rgba(77,72,55,.09)');
 }
 // A few irregularly scattered chips, moss, timber shavings or ash hug
 // the actual footing. No generated objects enter the collision grid.
 for(let i=0;i<groundY.length;i++){
  const [x,y]=groundY[i],q=rh1510Hash(i,7,seed);
  if(q<.38)continue;
  const u=x+(rh1510Hash(i,13,seed)-.5)*8,v=y+3+rh1510Hash(i,17,seed)*12;
  const s=1.1+rh1510Hash(i,19,seed)*2.7;
  g.fillStyle=green&&q>.63?'rgba(86,99,58,.30)':pale&&q>.60?'rgba(161,150,121,.19)':wood&&q>.57?'rgba(138,111,74,.23)':'rgba(92,86,72,.27)';
  g.beginPath();g.moveTo(u-s,v);g.lineTo(u-.4*s,v-s*.48);g.lineTo(u+s,v-.15*s);g.lineTo(u+s*.55,v+s*.54);g.closePath();g.fill();
  if(green&&q>.79){g.fillStyle='rgba(113,129,72,.33)';g.fillRect(u-1,v-1,1.4,2);}
 }
 // Worn entry apron: low, irregular paving sheen and softly worn approach.
 // It is at the existing entrance, with no added step collision or height.
 const dx=site.doorX-left,dy=site.doorY-top+5;
 if(dx>12&&dx<w-12&&dy>0&&dy<h-8){
  const wide=Math.min(27,Math.max(17,b.w*.056));
  spot(dx,dy+10,wide+13,11,'rgba(35,38,32,.12)');
  spot(dx,dy+12,wide+9,7,'rgba(151,142,115,.075)');
  for(let n=-2;n<=2;n++){
   const k=rh1510Hash(n+6,11,seed),x=dx+n*wide*.41,y=dy+5+k*3;
   g.fillStyle='rgba(120,112,91,.19)';g.beginPath();
   g.moveTo(x-5,y-2);g.lineTo(x+4,y-2.8);g.lineTo(x+4.8,y+2.5);g.lineTo(x-4.8,y+2);g.closePath();g.fill();
   g.strokeStyle='rgba(44,45,36,.18)';g.lineWidth=.8;g.stroke();
  }
 }
 return {canvas,left,top,n:w*h,im};
}
function rh1510Ground(cx,cy){
 rh1510GroundBuilds=0;
 for(const s of sites){
  if(!rhPainted[s.name])continue;
  const b=rh1365SiteBounds(s);if(!b||!rh1365Intersects(b,cx,cy,45))continue;
  const im=rh1510Upgrade(s)||rh1451SiteArt(s);
  if(!im?.complete||!im.naturalWidth)continue;
  let a=rh1510GroundCache.get(s);
  if(a&&a.im!==im){rh1510GroundPixels-=a.n;rh1510GroundCache.delete(s);a=null;}
  if(a){rh1510GroundCache.delete(s);rh1510GroundCache.set(s,a);}
  else if(rh1510GroundBuilds<1){
   rh1510GroundBuilds++;
   try{
    a=rh1510GroundBuild(b,im,s);
    while(rh1510GroundPixels+a.n>1600000&&rh1510GroundCache.size){const key=rh1510GroundCache.keys().next().value;rh1510GroundPixels-=rh1510GroundCache.get(key).n;rh1510GroundCache.delete(key);}
    rh1510GroundCache.set(s,a);rh1510GroundPixels+=a.n;
   }catch(_){}
  }
  if(a)c.drawImage(a.canvas,a.left,a.top);
 }
}
