// Distinct merchant pavilions share the original lot geometry and existing
// depth-sort / building transparency. One reused cargo sprite gives the carts
// different goods without decoding a duplicate bitmap.
function rh1529MarketVariant(o){
 if(o.k==='stall0'&&o.x===5850&&o.y===1845)return 'produce';
 if(o.k==='stall1'&&o.x===6280&&o.y===1890)return 'cloth';
 if(o.k==='cart'&&o.x===5790&&o.y===1960)return 'grainCart';
 return null;
}
function rh1529MarketStatus(full=false){
 const models=Object.entries(rh1529MarketMeta.stalls).map(([key,m])=>{
  const o=rh1475Furniture.find(q=>rh1529MarketVariant(q)===key),im=o&&rh1512MarketImage(o);
  return {key,name:m.name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
   counterHeight:m.counterHeight,geometry:o?{x:o.x,y:o.y,w:o.w,h:o.h,rx:o.rx,ry:o.ry,flip:o.flip}:null,
   fit:!!o&&o.w===m.worldBounds[0]&&o.h===m.worldBounds[1]&&o.flip===m.flip&&o.x===m.center[0]&&o.y===m.center[1],
   solid:full?!!o&&blocked(o.x,o.y):null};
 });
 const carts=rh1475Furniture.filter(o=>o.k==='cart').map(o=>{
  const im=rh1512MarketImage(o);return {x:o.x,y:o.y,w:o.w,h:o.h,rx:o.rx,ry:o.ry,
   art:rh1529MarketVariant(o)||'produceCart',ready:!!im?.complete&&im.naturalWidth>1,
   reused:im===rh1417Art.cargo2,solid:full?blocked(o.x,o.y):null};
 });
 const stalls=rh1475Furniture.filter(o=>o.k.startsWith('stall')).map(o=>rh1512MarketVariant(o)||o.k);
 return {version:1529,models,carts,stallVariants:stalls,marketCount:rh1475Furniture.length,
  bakedTiles:rh1529MarketMeta.ground.map(o=>o.key),court:rh1529MarketMeta.court.name,
  newColliders:0,additionalGroundPasses:0,npcChanges:0};
}
function rh1529ReviewMarket(){if(!rh1512ReviewFort('market'))return false;rh199Reset();return true;}
