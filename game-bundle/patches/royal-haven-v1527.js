// Two bespoke permanent stalls occupy the exact existing market lots.
// The only ground changes are baked texture replacements, not solid props.
function rh1527MarketRenewal(full=false){
 const assets=Object.entries(rh1527MarketMeta.stalls).map(([key,m])=>{
  const o=rh1475Furniture.find(q=>rh1512MarketVariant(q)===key),im=o&&rh1512MarketImage(o);
  const geometry=o&&{x:o.x,y:o.y,w:o.w,h:o.h,rx:o.rx,ry:o.ry,flip:o.flip};
  return {key,name:m.name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
   counterHeight:m.counterHeight,geometry,fit:!!o&&o.w===m.worldBounds[0]&&o.h===m.worldBounds[1],
   solid:full?!!o&&blocked(o.x,o.y):null};
 });
 return {version:1527,assets,marketCount:rh1475Furniture.length,aprons:rh1527MarketMeta.aprons.length,
   bakedTiles:rh1527MarketMeta.ground.map(t=>t.key),newColliders:0,additionalGroundPasses:0,npcChanges:0};
}
function rh1527ReviewMarket(){const ok=rh1512ReviewFort('market');if(ok)rh199Reset();return ok;}
