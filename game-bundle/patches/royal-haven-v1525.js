// Two unique residences, fitted to measured doors and baked-in terrain.
// No additional ground layers, props, NPCs, or animation loops.
let rh1525Applied=false,rh1525Rejection=null;
function rh1525Install(){
 const keys=Object.keys(rh1525Meta.homes);
 const indices=keys.map(k=>rh1464Homes.findIndex(o=>o.k===k));
 if(indices.some(i=>i<0)){rh1525Rejection='Original residences missing';return;}
 const originals=indices.map(i=>rh1464Homes[i]);
 const replacements=originals.map((o,i)=>({...o,...rh1525Meta.homes[keys[i]].geometry}));
 // Fit only the replacement footprints; the rest of the street geometry is preserved.
 // Temporarily remove the original residences while checking local ground.
 const saved=rh1464Homes.slice();
 rh1464Homes.splice(0,rh1464Homes.length,...saved.filter(o=>!keys.includes(o.k)));
 try{
  for(const o of replacements){
   const xs=o.poly.map(a=>a[0]),ys=o.poly.map(a=>a[1]);
   for(let y=Math.min(...ys)+5;y<Math.max(...ys);y+=10)
    for(let x=Math.min(...xs)+5;x<Math.max(...xs);x+=10)
     if(rh1472Poly(o.poly,x,y)&&blocked(o.x+x,o.y+y)){
      rh1525Rejection={home:o.k,reason:'Footprint intersects existing geometry',at:[o.x+x,o.y+y]};return;
     }
   rh1464Homes.push(o);
  }
  for(const route of rh1525Meta.links){
   const check=rh1513PathCheck(route.points,7);
   if(check.bad){rh1525Rejection={route:route.key,...check};return;}
  }
  rh1525Applied=true;
 }finally{
  rh1464Homes.splice(0,rh1464Homes.length,...saved);
  if(rh1525Applied)indices.forEach((i,j)=>rh1464Homes[i]=replacements[j]);
 }
 if(!rh1525Applied)return;
 for(const k of keys){
  const m=rh1525Meta.homes[k];
  // Release references to superseded sprites from the preload roster.
  const obsolete=new Set([rh1464Art[k],rh1464Art[k+'Night'],rh1510Art['home:'+k]]);
  for(let i=rh1200Images.length-1;i>=0;i--)if(obsolete.has(rh1200Images[i]))rh1200Images.splice(i,1);
  delete rh1464Art[k+'Night'];
  rh1464Art[k]=rh1525Art[k];
  rh1510Art['home:'+k]=rh1525Art[k];
  rh1510ArtMeta['home:'+k]={...rh1510ArtMeta['home:'+k],...m,legacy:false};
 }
 rh1524Landscape.links=rh1524Landscape.links.filter(r=>!['Courtyard House Walk','Cottage West Walk'].includes(r.key)).concat(rh1525Meta.links);
}
function rh1525Status(full=false){
 return {version:1525,installed:rh1525Applied,rejection:rh1525Rejection,
  homes:Object.entries(rh1525Meta.homes).map(([key,m])=>{
   const o=rh1464Homes.find(h=>h.k===key),b=o&&rh1464Bounds(o),im=rh1525Art[key];
   return {key,name:m.name,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,
    bounds:b,door:o?.door,doorHeight:o?.doorHeight,doorWidth:m.doorWidth};
  }),routes:full?rh1525Meta.links.map(r=>({key:r.key,width:r.width,...rh1513PathCheck(r.points,7)})):null,
  groundTiles:rh1525Meta.ground.length,additionalGroundPasses:0,npcChanges:0};
}
function rh1525Review(){if(!rh1525Applied)return false;p.x=4070;p.y=984;rh199Reset();return true;}
