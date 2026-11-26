// V1541: permanent shop identity after the V1522 frontage relocation.
// One raster per existing prop, without extra objects or extra rendering passes.
const rh1541TradeKinds={
 'Weapon Smith':['weapon'],'Armor Smith':['armor'],'Leatherworker':['leather'],
 'General Store':['general'],'Item Shop':['item'],'Alchemist':['alchemy','alchemyDelivery'],
 'Herbalist':['herbalist'],'Enchanter':['enchanter','enchantDelivery'],
 'Fletcher':['fletcher'],'Tailor':['tailor','clothDelivery'],'Apothecary':['apothecary'],'Bakery':['bakery']
};
const rh1541TradeWidths={weapon:49,armor:48,leather:49,general:49,item:47,alchemy:48,herbalist:49,enchanter:47,fletcher:52,tailor:47,apothecary:47,bakery:48,alchemyDelivery:43,enchantDelivery:43,clothDelivery:43};
const rh1541Bindings=new WeakMap(),rh1541Stock=[];
function rh1541Install(){
 for(const m of rh1522Relocated){
  const s=sites.find(s=>s.doorY+62===m.from&&Math.abs(s.doorX-m.x)===120&&rh1541TradeKinds[s.name]);
  const key=s&&rh1541TradeKinds[s.name][m.k==='barrel'?1:0];
  const o=rh117Props.find(o=>o.k===m.k&&o.x===m.x&&o.y===m.to);
  if(!key||!o||!rh1541Art[key]||rh1541Bindings.has(o))continue;
  const entry={o,key,shop:s.name,original:[m.x,m.from],anchor:[m.x,m.to],geometry:null};
  rh1541Bindings.set(o,entry);rh1541Stock.push(entry);
 }
}
function rh1541Geometry(o){
 const a=rh1541Bindings.get(o);if(!a)return null;
 const im=rh1541Art[a.key];if(!im.complete||!im.naturalWidth)return null;
 if(a.geometry&&a.geometry.base===o.y&&a.geometry.x+a.geometry.w/2===o.x)return a.geometry;
 const scale=Math.min(rh1541TradeWidths[a.key]/im.naturalWidth,53/im.naturalHeight),w=im.naturalWidth*scale,h=im.naturalHeight*scale;
 return a.geometry={im,w,h,x:o.x-w/2,y:o.y-h,base:o.y,visibleW:w,flip:false,trade:'v1541-'+a.key};
}
function rh1541Status(full=false){
 const models=rh1541Meta.models.map(m=>({...m,ready:rh1541Art[m.key].complete&&rh1541Art[m.key].naturalWidth===m.width&&rh1541Art[m.key].naturalHeight===m.height,instances:rh1541Stock.filter(a=>a.key===m.key).length}));
 const stock=rh1541Stock.map(a=>{
  const o=a.o,g=rh1541Geometry(o);
  return {shop:a.shop,kind:o.k,key:a.key,original:a.original,anchor:a.anchor,
   unchanged:o.x===a.anchor[0]&&o.y===a.anchor[1],soft:rh1519Soft.has(o),clear:!blocked(o.x,o.y),
   active:!!g&&rh1389SupplyGeometry(o)===g,base:g?.base??null,width:g?.w??null,height:g?.h??null};
 });
 return {version:1541,models,stock,relocated:rh1522Relocated.length,fixed:stock.length,newColliders:0,additionalDrawLayers:0,npcChanges:0,
  routes:full?rh1521Plan.roads.filter(o=>o.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  links:full?rh1524Landscape.links.map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null};
}
// Reduce legacy tile candidates to the closer camera and uncovered transition strips.
// Pixel composition and original tile size are unchanged.
const rh1541GroundStats={queries:0,oldCandidates:0,neededCandidates:0,avoidedCandidates:0};
function rh1541GroundWindow(cx,cy,vw,vh,ready){
 let top=cy,bottom=cy+vh;
 if(ready){
  if(cy<865&&bottom<=2460)bottom=Math.min(bottom,865);
  else if(cy>=865&&bottom>2460)top=Math.max(top,2460);
 }
 const x0=Math.floor(cx/rh1200TileW),x1=Math.floor((cx+vw-.001)/rh1200TileW);
 const y0=Math.floor(top/rh1200TileH),y1=Math.floor((bottom-.001)/rh1200TileH);
 const old=(Math.floor((cx+W-.001)/rh1200TileW)-x0+1)*(Math.floor((cy+H-.001)/rh1200TileH)-Math.floor(cy/rh1200TileH)+1);
 const needed=Math.max(0,x1-x0+1)*Math.max(0,y1-y0+1);
 rh1541GroundStats.queries++;rh1541GroundStats.oldCandidates+=old;rh1541GroundStats.neededCandidates+=needed;rh1541GroundStats.avoidedCandidates+=Math.max(0,old-needed);
 return {x0,x1,y0,y1};
}
