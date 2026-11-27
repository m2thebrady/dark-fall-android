// V1540: genuine species silhouettes replace same-image color variants.
// Preserve the existing object placement, world physics, wind, tree cache,
// projected shadow and depth-sorting systems. No added layers or objects.
function rh1540CanopyStatus(full=false){
 const counts={};
 for(const o of rh117Trees)counts[o.k]=(counts[o.k]||0)+1;
 const models=rh1540Meta.models.map(m=>{
  const im=rh117Images[m.key];
  return {...m,ready:!!im?.complete&&im.naturalWidth===m.width&&im.naturalHeight===m.height,instances:counts[m.key]||0};
 });
 const retain=rh1540Meta.unchangedKeys.map(key=>({key,instances:counts[key]||0,ready:rh117Ready(key)}));
 return {version:1540,models,retain,treeCount:rh117Trees.length,replacedInstances:models.reduce((n,m)=>n+m.instances,0),
  speciesCounts:counts,rootAnchorsUnchanged:true,additionalDrawLayers:0,newColliders:0,npcChanges:0,
  routes:full?rh1521Plan.roads.filter(o=>o.audit).map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null,
  links:full?rh1524Landscape.links.map(r=>({key:r.key,...rh1513PathCheck(r.points,7)})):null};
}
// A geometry-only manifest for the next interior phase, no new transitions.
// Reuse real door positions, trigger radius and exit-position algorithm.
const rh1540InteriorPriority={
 'Royal Castle':1,'Temple of Light':1,'Caster Guild':1,
 'Future Guild Hall':1,'Dark Guild Cave':2,'General Store':2,'Item Shop':2,
 'Alchemist':2,'Apothecary':2,'Herbalist':2,'Bakery':2,'Storehouse Cellar':2,
 'The Iron Hearth Tavern':3,'Town Residence':3,'Weapon Smith':3,'Armor Smith':3,
 'Leatherworker':3,'Enchanter':3,'Fletcher':3,'Tailor':3,'Wayfarer Inn':3
};
function rh1540InteriorReadiness(full=false){
 const audit=full&&!inside;
 const clear=(x,y)=>[-7,0,7].every(dx=>[-7,0,7].every(dy=>!blocked(x+dx,y+dy)));
 const rows=sites.map(s=>{
  let room=Object.prototype.hasOwnProperty.call(rh1505Rooms.rooms,s.name)?'bespoke':landmarkNames.has(s.name)?'landmark':rebuiltRooms.has(s.name)?'legacy-shop':s.type==='future'?'future':'other';
  let approach=null,exit=null;
  if(audit){
   for(const dy of [80,90,70,95,60,50,40,30,20,10,0,-10,-20]){
    for(const dx of [0,-12,12,-24,24,-36,36,-48,48,-60,60]){
     if(Math.hypot(dx,dy)>=105)continue;
     const x=s.doorX+dx,y=s.doorY+dy;
     if(clear(x,y)&&sites.find(q=>Math.hypot(x-q.doorX,y-q.doorY)<105)===s){approach={x,y};break;}
    }
    if(approach)break;
   }
   if(approach)exit=rh1285ExitPoint(s,approach);
  }
  return {name:s.name,type:s.type,priority:rh1540InteriorPriority[s.name]||3,room,door:[s.doorX,s.doorY],
   approach:audit?approach:null,exit:audit?exit:null,approachClear:audit?!!approach:null,exitClear:audit?!!exit&&clear(exit.x,exit.y):null};
 });
 return {version:1540,exteriorOnly:true,audited:audit,rows,bespoke:rows.filter(r=>r.room==='bespoke').length,
  landmarks:rows.filter(r=>r.room==='landmark').length,approachIssues:audit?rows.filter(r=>!r.approachClear||!r.exitClear).map(r=>r.name):null};
}
