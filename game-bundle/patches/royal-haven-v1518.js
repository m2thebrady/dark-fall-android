// V1518: rendering work budgets, bounded lazy resources and local compositing.
// No changes to collision, sprite art, camera position, controls or animation clocks.
const rh1518Stats={frames:0,builds:0,defers:0,maxBuilds:0,byKind:{},tileHits:0,tileMisses:0,cutawayPixels:0,fullEquivalentPixels:0,localCutaways:0};
let rh1518InFrame=false,rh1518FrameBuilds=0,rh1518FrameLimit=1,rh1518PrefetchAt=-Infinity;
function rh1518Begin(){
 rh1518InFrame=true;rh1518FrameBuilds=0;
 rh1518FrameLimit=rh1431InitialTier()>0||rh1431Perf.tier>0||rh176Moving?1:2;
}
function rh1518End(){
 if(!rh1518InFrame)return;
 rh1518Stats.frames++;rh1518Stats.maxBuilds=Math.max(rh1518Stats.maxBuilds,rh1518FrameBuilds);rh1518InFrame=false;
}
function rh1518Claim(kind){
 if(!rh1518InFrame)return true;
 if(rh1518FrameBuilds>=rh1518FrameLimit){rh1518Stats.defers++;return false;}
 rh1518FrameBuilds++;rh1518Stats.builds++;rh1518Stats.byKind[kind]=(rh1518Stats.byKind[kind]||0)+1;return true;
}
// Lazy terrain is not part of the eagerly loaded art registry. Map eviction
// must be able to release the image rather than leave an invisible strong ref.
function rh1518LazyImage(){return new Image();}
function rh1518PrefetchReady(t){if(t-rh1518PrefetchAt<170)return false;rh1518PrefetchAt=t;return true;}
// Same interpolated world-space noise, with each lattice hash computed once.
// Negative step supports mirrored eastern sidewalls without a seam.
function rh1518NoiseField(w,h,ox,oy,dx,dy,sx,sy,seed){
 const xi=new Int32Array(w),yi=new Int32Array(h),xf=new Float64Array(w),yf=new Float64Array(h);
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
 for(let x=0;x<w;x++){const z=(ox+x*dx)/sx,a=Math.floor(z),f=z-a;xi[x]=a;xf[x]=f*f*(3-2*f);minX=Math.min(minX,a);maxX=Math.max(maxX,a);}
 for(let y=0;y<h;y++){const z=(oy+y*dy)/sy,a=Math.floor(z),f=z-a;yi[y]=a;yf[y]=f*f*(3-2*f);minY=Math.min(minY,a);maxY=Math.max(maxY,a);}
 const cols=maxX-minX+2,rows=maxY-minY+2,grid=new Float64Array(cols*rows);
 for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)grid[y*cols+x]=rh1510Hash(x+minX,y+minY,seed);
 const out=new Float32Array(w*h);
 for(let y=0;y<h;y++){const row=(yi[y]-minY)*cols,v=yf[y];for(let x=0;x<w;x++){const j=row+xi[x]-minX,u=xf[x],k=grid[j],l=grid[j+1],m=grid[j+cols],n=grid[j+cols+1];out[y*w+x]=(k+(l-k)*u)*(1-v)+(m+(n-m)*u)*v;}}
 return out;
}
// A small device-space layer is sufficient for known, precisely bounded
// modern sprites. Older callbacks still use the conservative full canvas.
let rh1518CutawayCanvas=null;
function rh1518CutawayRect(b,m,w,h){
 if(!b||!Number.isFinite(b.left+b.top+b.w+b.h)||m.b!==0||m.c!==0||m.a<=0||m.d<=0)return {x:0,y:0,w,h};
 const pad=b.rh1518LocalPad??96;
 const l=Math.max(0,Math.floor((b.left-pad)*m.a+m.e)),t=Math.max(0,Math.floor((b.top-pad)*m.d+m.f));
 const r=Math.min(w,Math.ceil((b.left+b.w+pad)*m.a+m.e)),bt=Math.min(h,Math.ceil((b.top+b.h+pad)*m.d+m.f));
 if(r<=l||bt<=t)return {x:0,y:0,w,h};
 return {x:l,y:t,w:r-l,h:bt-t};
}
function rh1518MaskFacade(b,draw){
 const main=c,fullW=main.canvas.width,fullH=main.canvas.height,transform=main.getTransform();
 const q=Number.isFinite(b?.rh1518LocalPad)?rh1518CutawayRect(b,transform,fullW,fullH):{x:0,y:0,w:fullW,h:fullH};
 const local=q.w*q.h<fullW*fullH;
 let layer;
 if(local){
  const w=Math.min(fullW,Math.ceil(q.w/64)*64),h=Math.min(fullH,Math.ceil(q.h/64)*64);
  layer=rh1518CutawayCanvas;
  if(!layer||layer.width<w||layer.height<h){layer=rhSurface(Math.max(w,Math.min(layer?.width||0,fullW)),Math.max(h,Math.min(layer?.height||0,fullH)));rh1518CutawayCanvas=layer;}
 }else{
  layer=rh1510CutawayCanvas;
  if(!layer||layer.width!==fullW||layer.height!==fullH)layer=rh1510CutawayCanvas=rhSurface(fullW,fullH);
 }
 const g=layer.getContext('2d');
 g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,q.w,q.h);
 g.save();
 try{
  g.beginPath();g.rect(0,0,q.w,q.h);g.clip();
  g.setTransform(transform.a,transform.b,transform.c,transform.d,transform.e-q.x,transform.f-q.y);
  g.imageSmoothingEnabled=main.imageSmoothingEnabled;g.imageSmoothingQuality=main.imageSmoothingQuality;
  g.globalAlpha=1;g.globalCompositeOperation='source-over';c=g;
  try{draw();}finally{c=main;}
  rh1510Mask(g,p.x,p.y);
 }finally{g.restore();c=main;}
 main.save();try{main.setTransform(1,0,0,1,0,0);main.drawImage(layer,0,0,q.w,q.h,q.x,q.y,q.w,q.h);}finally{main.restore();}
 rh1518Stats.fullEquivalentPixels+=fullW*fullH;rh1518Stats.cutawayPixels+=q.w*q.h;if(local)rh1518Stats.localCutaways++;
}
// Fixed district paving, drains, thresholds and contacts are composited in
// their original order into a bounded atlas. Animated surfaces and day/night
// shadow layers stay outside this pass. Missing tiles are drawn directly.
const rh1518StreetCache=new Map(),rh1518TileW=640,rh1518TileH=360,rh1518Bleed=2;
let rh1518StreetPrimed=false;
function rh1518StreetLimit(){return rh1431InitialTier()>0?10:12;}
function rh1518StreetTiles(cx,cy){
 const wanted=[];
 for(let iy=Math.floor(cy/rh1518TileH);iy<=Math.floor((cy+H-.001)/rh1518TileH);iy++)
  for(let ix=Math.floor(cx/rh1518TileW);ix<=Math.floor((cx+W-.001)/rh1518TileW);ix++)
   wanted.push({key:ix+':'+iy,x:ix*rh1518TileW,y:iy*rh1518TileH});
 return wanted;
}
function rh1518BuildStreetTile(o,pass){
 const pad=rh1518Bleed,a=rhSurface(rh1518TileW+pad*2,rh1518TileH+pad*2),main=c,prior=rh1436GroundView;
 try{
  c=a.getContext('2d');c.imageSmoothingEnabled=true;c.imageSmoothingQuality='medium';
  c.translate(pad-o.x,pad-o.y);
  rh1436GroundView={x:o.x-pad,y:o.y-pad,w:rh1518TileW+pad*2,h:rh1518TileH+pad*2};
  // Original culling methods assume a full logical viewport. A padded,
  // conservative origin retains every mark touching a tile boundary.
  pass(o.x-96,o.y-96);
 }finally{c=main;rh1436GroundView=prior;}
 return a;
}
function rh1518StreetLayer(cx,cy,pass){
 if(!rh1200StaticReady||!rh1518StreetPrimed){
  pass(cx,cy);if(rh1200StaticReady)rh1518StreetPrimed=true;return;
 }
 const wanted=rh1518StreetTiles(cx,cy),missing=[];let built=false;
 for(const o of wanted){
  let a=rh1518StreetCache.get(o.key);
  if(a){rh1518StreetCache.delete(o.key);rh1518StreetCache.set(o.key,a);rh1518Stats.tileHits++;}
  else{
   rh1518Stats.tileMisses++;
   if(!built&&rh1518Claim('district-tile')){
    a=rh1518BuildStreetTile(o,pass);rh1518StreetCache.set(o.key,a);built=true;
   }
  }
  if(a)c.drawImage(a,rh1518Bleed,rh1518Bleed,rh1518TileW,rh1518TileH,o.x,o.y,rh1518TileW,rh1518TileH);
  else missing.push(o);
 }
 // One draw of the original pass, clipped to all currently missing tile
 // rectangles. Never show holes or a simplified stand-in pavement.
 if(missing.length){
  c.save();try{c.beginPath();for(const o of missing)c.rect(o.x,o.y,rh1518TileW,rh1518TileH);c.clip();pass(cx,cy);}finally{c.restore();}
 }
 const keep=new Set(wanted.map(o=>o.key));
 while(rh1518StreetCache.size>rh1518StreetLimit()){
  const key=[...rh1518StreetCache.keys()].find(k=>!keep.has(k));if(key===undefined)break;
  rh1518StreetCache.delete(key);
 }
}
function rh1518Reset(){
 rh1518StreetCache.clear();rh1518StreetPrimed=false;rh1518CutawayCanvas=null;rh1518PrefetchAt=-Infinity;rh1518InFrame=false;rh1518FrameBuilds=0;
}
function rh1518Performance(){
 return {...rh1518Stats,byKind:{...rh1518Stats.byKind},streetTiles:rh1518StreetCache.size,streetLimit:rh1518StreetLimit(),terrainImages:rh119ChunkImages.size,registeredImages:rh1200Images.length,shoulderImages:rh1510ShoulderImages.size,staticTiles:rh1200GroundCache.size,tier:rh1431Perf.tier,slow:rh1431Perf.slow,renderCost:rh1431Perf.cost,raf:rh1431Perf.raf,backing:[cv.width,cv.height]};
}
