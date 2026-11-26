import { chromium } from 'playwright';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
const out = resolve('browser-smoke-results');
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', err => errors.push(String(err)));
page.on('console', msg => { if (msg.type() === 'error') errors.push('console: ' + msg.text()); });
try {
  // Real Canvas2D compositing regression, including scaled/translated camera transforms.
  const probe=await browser.newPage();
  await probe.setContent('<canvas id="scene" width="256" height="240"></canvas>');
  await probe.addScriptTag({content:`
    let c=document.getElementById('scene').getContext('2d'),p={x:140,y:140};
    function rhSurface(w,h){const a=document.createElement('canvas');a.width=w;a.height=h;return a;}
  `});
  await probe.addScriptTag({content:await readFile('game-bundle/patches/royal-haven-v1510.js','utf8')});
  await probe.addScriptTag({content:await readFile('game-bundle/patches/royal-haven-v1511.js','utf8')});
  const cutaway=await probe.evaluate(()=>{
    const main=c;
    c.fillStyle='#983027';c.fillRect(0,0,256,240);
    c.setTransform(.8,0,0,.8,12,16);
    const bounds={left:20,top:10,w:240,h:195};
    let draws=0;
    const facade=()=>{draws++;c.fillStyle='#b2b5b9';c.fillRect(bounds.left,bounds.top,bounds.w,bounds.h);};
    rh1457Facade(bounds,205,facade);
    const pixel=(x,y)=>Array.from(main.getImageData(Math.floor(x*.8+12),Math.floor(y*.8+16),1,1).data);
    const center=pixel(140,109),feet=pixel(140,140),feather=pixel(179,109),roof=pixel(70,60),street=pixel(10,10);
    const behindDraws=draws,restored=c===main&&Math.abs(main.getTransform().a-.8)<1e-6;
    p.y=220;rh1457Facade(bounds,205,facade);
    const front=pixel(140,109);
    const sprite=rhSurface(140,180),sc=sprite.getContext('2d');sc.fillStyle='#777';sc.fillRect(24,20,98,148);
    const blend=rh1510GroundBuild({left:100,top:30,w:140,h:180},sprite,{name:'Herbalist',type:'shop',doorX:170,doorY:198});
    const bg=blend.canvas.getContext('2d'),contact=bg.getImageData(170-blend.left,204-blend.top,1,1).data[3],
      far=bg.getImageData(92-blend.left,160-blend.top,1,1).data[3];
    const apron=rhSurface(120,100),ag=apron.getContext('2d');
    ag.fillStyle='#9b8771';ag.fillRect(0,0,120,100);
    rh1511PavingEdge(ag,{x:0,y:0,w:120,h:100},[[0,0],[119,0],[119,99],[0,99]],1493);
    const pavingEdge=ag.getImageData(2,2,1,1).data[3],pavingCore=ag.getImageData(60,50,1,1).data[3];
    return {center,feet,feather,roof,street,front,behindDraws,draws,restored,contact,far,pavingEdge,pavingCore};
  });
  await probe.close();
  if(cutaway.center[1]>75||cutaway.feet[1]>85||cutaway.feather[1]<=cutaway.center[1]||
     cutaway.roof[1]<170||cutaway.front[1]<170||cutaway.street[1]!==48||
     cutaway.behindDraws!==1||cutaway.draws!==2||!cutaway.restored||cutaway.contact<=0||cutaway.far!==0||cutaway.pavingEdge>=40||cutaway.pavingCore!==255||
     [cutaway.center,cutaway.feet,cutaway.street,cutaway.roof].some(p=>p[3]!==255))
    throw new Error('Royal Haven cutaway pixel test failed: '+JSON.stringify(cutaway));
  await writeFile(resolve(out,'royal-haven-cutaway.json'),JSON.stringify(cutaway,null,2));
  console.log('Royal Haven cutaway pixel test PASS',cutaway);
  await page.goto('file://' + resolve('app/src/main/assets/index.html') + '?graphicsAudit=1', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  const status = await page.evaluate(() => ({
    title: document.title,
    canvases: document.querySelectorAll('canvas').length,
    canvasDimensions: [...document.querySelectorAll('canvas')].map(c => ({ width: c.width, height: c.height, cssWidth: c.getBoundingClientRect().width, cssHeight: c.getBoundingClientRect().height })),
    canvasPixelSamples: [...document.querySelectorAll('canvas')].map(c => { try { const ctx = c.getContext('2d', { willReadFrequently: true }); if (!ctx || c.width < 2 || c.height < 2) return { available: false }; const w = Math.min(24, c.width), h = Math.min(24, c.height); const data = ctx.getImageData(Math.floor((c.width-w)/2), Math.floor((c.height-h)/2), w, h).data; let opaque=0, nonzero=0; for (let i=0;i<data.length;i+=4) { if (data[i+3]>0) opaque++; if (data[i]||data[i+1]||data[i+2]||data[i+3]) nonzero++; } return { available:true, sampledPixels:w*h, opaque, nonzero }; } catch(e) { return { available:false, reason:String(e).slice(0,100) }; } }),
    visibleButtons: [...document.querySelectorAll('button, [role="button"]')].filter(el => { const r = el.getBoundingClientRect(); const st = getComputedStyle(el); return r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none'; }).map(el => (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 60)).slice(0, 30),
    bodyText: document.body?.innerText?.slice(0, 500) ?? '',
    width: innerWidth,
    height: innerHeight,
  }));
  await page.screenshot({ path: resolve(out, 'startup.png'), fullPage: false, timeout: 20000 });
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(500);
  await page.screenshot({ path: resolve(out, 'keyboard-probe.png'), fullPage: false, timeout: 20000 });
  await page.keyboard.up('ArrowRight');
  const startupPng = await readFile(resolve(out, 'startup.png'));
  const probePng = await readFile(resolve(out, 'keyboard-probe.png'));
  const startupHash = createHash('sha256').update(startupPng).digest('hex');
  const probeHash = createHash('sha256').update(probePng).digest('hex');
  const screenshotAudit = { startupHash, probeHash, startupBytes: startupPng.length, probeBytes: probePng.length, screenshotsDiffer: startupHash !== probeHash };
  // Pixel-level comparisons require a deterministic scene and are intentionally not enforced yet.
  await writeFile(resolve(out, 'screenshot-audit.json'), JSON.stringify(screenshotAudit, null, 2));
  console.log('Screenshot audit:', screenshotAudit);
  if (startupPng.length < 1000 || probePng.length < 1000) throw new Error('Screenshot unexpectedly empty');
  await writeFile(resolve(out, 'report.json'), JSON.stringify({ status, errors }, null, 2));
  console.log(JSON.stringify({ status, errors: errors.slice(0, 12) }, null, 2));
  if (!status.canvases) throw new Error('Game canvas not found');
  if(['Dark Fall V1510','Dark Fall V1511','Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
    // The built-in entry point is used for an exterior runtime smoke, not a modified game.
    await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven?.exteriorArt?.();return a?.length===16&&a.every(s=>s.ready&&(!s.active||s.bounds))&&window.DarkFallRoyalHaven.secondaryArt().every(s=>s.ready);},{},{timeout:45000});
    const art=await page.evaluate(()=>({stores:window.DarkFallRoyalHaven.exteriorArt(),homes:window.DarkFallRoyalHaven.secondaryArt()}));
    console.log('Royal Haven artwork readiness',JSON.stringify(art));
    const first=page.locator('.chooseCard').first();
    if(await first.isVisible())await first.click({timeout:15000});
    const town=await page.evaluate(()=>{const api=window.DarkFallRoyalHaven;if(!api)return false;api.open();return api.active;});
    if(!town)throw new Error('Royal Haven failed to open');
    await page.waitForFunction(()=>{const k=window.DarkFallRoyalHaven.streetArt();return k.gateReady&&k.shoulderTiles===4&&k.loadedShoulders>0&&k.shoulderDraws>0;},{},{timeout:30000});
    await page.waitForTimeout(4000);
    const streetArt=await page.evaluate(()=>window.DarkFallRoyalHaven.streetArt());
    await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.civicArt();return a.hallReady&&a.annexes.length===3&&a.annexes.every(o=>o.ready);},{},{timeout:30000});
    const civicArt=await page.evaluate(()=>window.DarkFallRoyalHaven.civicArt());
    await writeFile(resolve(out,'royal-haven-civic-audit.json'),JSON.stringify(civicArt,null,2));
    if(!civicArt.hallDoorAligned||civicArt.hallDoorHeight<95||!civicArt.annexes.every(o=>o.instances.length)||civicArt.placements.length!==2||
       civicArt.annexes.some(o=>o.instances.some(o=>o.doorHeight<54)))throw new Error('Revised civic building geometry audit failed: '+JSON.stringify(civicArt));
    console.log('Royal Haven civic building readiness',JSON.stringify(civicArt));
    console.log('Royal Haven gate / ground readiness',streetArt);
    await page.screenshot({path:resolve(out,'royal-haven-exterior.png'),timeout:30000});
    // Walk north toward the civic hall to review the complete building at play scale.
    await page.keyboard.down('ArrowUp');
    await page.waitForTimeout(1000);
    await page.keyboard.up('ArrowUp');
    await page.waitForTimeout(1200);
    await page.screenshot({path:resolve(out,'royal-haven-civic-hall.png'),timeout:30000});
    // Graphics-only camera audit uses the explicit query opt-in, not a normal
    // player's save or route. Render the exact market court at play scale.
    await page.evaluate(()=>window.DarkFallRoyalHaven.reviewMarket());
    await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.marketArt();return a.assets.every(o=>o.ready)&&a.eastTiles===4&&a.eastReady.includes('8:3')&&a.squareReady&&a.contactCount>=7;},{},{timeout:30000});
    await page.waitForTimeout(2500);
    const marketArt=await page.evaluate(()=>window.DarkFallRoyalHaven.marketArt());
    if(marketArt.assets.some(o=>!o.instances.length)||marketArt.assets.filter(o=>o.key.startsWith('stall')).reduce((n,o)=>n+o.instances.length,0)!==4)throw new Error('Market art instance audit failed: '+JSON.stringify(marketArt));
    console.log('Royal Haven market graphics readiness',JSON.stringify(marketArt));
    await page.screenshot({path:resolve(out,'royal-haven-market.png'),timeout:30000});
    await writeFile(resolve(out,'royal-haven-market-audit.json'),JSON.stringify(marketArt,null,2));
    let districtArt=null;
    if(['Dark Fall V1511','Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.districtArt();return a.assets.length===9&&a.assets.every(o=>o.ready);},{},{timeout:30000});
      // Review each revised neighborhood in the real game, while the explicit
      // audit-only camera option keeps test positioning out of normal gameplay.
      for(const key of ['market','civic','gate','artisan','herb']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewDistrict(k),key);
        await page.waitForTimeout(1600);
        await page.screenshot({path:resolve(out,'royal-haven-district-'+key+'.png'),timeout:30000});
      }
      districtArt=await page.evaluate(()=>window.DarkFallRoyalHaven.districtArt(true));
      await writeFile(resolve(out,'royal-haven-district-audit.json'),JSON.stringify(districtArt,null,2));
      const {court,estate,gate,artisan,herb,civic}=districtArt;
      if(districtArt.assets.some(o=>o.instances.length!==1||o.openings?.some(x=>x<.9))||districtArt.thresholds<7||
         ![court,estate,gate,artisan,herb,civic].every(o=>o.installed)||
         court.route.badCount||court.footprintErrors||court.npcErrors||
         estate.paths.bad||estate.footprint.bad||estate.npcs.bad||
         gate.arch.bad||gate.footprint.bad||gate.doors.bad||gate.citizens.bad||
         artisan.main.bad||artisan.approaches.bad||artisan.residents.bad||
         herb.lanes.bad||herb.residents.bad||herb.foot.bad||
         civic.passage.bad||civic.routes.bad||civic.people.bad)
        throw new Error('Eastern district placement/walkway audit failed: '+JSON.stringify(districtArt));
      console.log('Royal Haven eastern district audit PASS',JSON.stringify(districtArt));
    }
    let fortificationArt=null;
    if(['Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.fortificationArt();return a.towers.every(o=>o.ready)&&a.market.every(o=>o.ready);},{},{timeout:30000});
      for(const key of ['market','south','west','east','middle']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewFortifications(k),key);
        await page.waitForTimeout(1700);
        await page.screenshot({path:resolve(out,'royal-haven-fortification-'+key+'.png'),timeout:30000});
      }
      fortificationArt=await page.evaluate(()=>window.DarkFallRoyalHaven.fortificationArt());
      await writeFile(resolve(out,'royal-haven-fortification-audit.json'),JSON.stringify(fortificationArt,null,2));
      if(fortificationArt.towers.length!==3||fortificationArt.towers.reduce((n,o)=>n+o.instances.length,0)!==8||
         new Set(fortificationArt.market.map(o=>o.key)).size!==4||fortificationArt.market.length!==4||
         !fortificationArt.sideTiles||!fortificationArt.curtainTiles||!fortificationArt.footTiles||!fortificationArt.towerContacts)
        throw new Error('Fortification and market audit failed: '+JSON.stringify(fortificationArt));
      console.log('Royal Haven fortification & market diversity audit PASS',JSON.stringify(fortificationArt));
    }
    let streetLayout=null;
    if(['Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.streetLayout();return a.row.every(o=>o.ready)&&a.court.every(o=>o.ready);},{},{timeout:30000});
      for(const key of ['courtyard','row','tailor','bakery']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewLayout(k),key);
        await page.waitForTimeout(1800);
        await page.screenshot({path:resolve(out,'royal-haven-layout-'+key+'.png'),timeout:30000});
      }
      streetLayout=await page.evaluate(()=>window.DarkFallRoyalHaven.streetLayout(true));
      await writeFile(resolve(out,'royal-haven-layout-audit.json'),JSON.stringify(streetLayout,null,2));
      const {row,court,trades,artisan,courtRoutes,crossStreet,pavingReady}=streetLayout;
      if(row.length!==3||court.length!==3||!pavingReady||!trades.installed||!artisan.installed||
         row.some(o=>!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>2||o.height<78||o.doorWidth<50||o.approach.bad)||
         row.some(o=>o.door[1]!==1963)||court.some(o=>o.door&&o.doorHeight<73)||
         trades.lanes.bad||trades.residents.bad||artisan.lanes.bad||artisan.residents.bad||crossStreet.bad||courtRoutes.some(o=>o.bad))
        throw new Error('Street alignment/courtyard placement audit failed: '+JSON.stringify(streetLayout));
      console.log('Royal Haven street alignment and inward courtyard audit PASS',JSON.stringify(streetLayout));
    }
    let streetAlignment=null;
    if(['Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.streetAlignment();return a.row.every(o=>o.ready)&&a.gate.ready;},{},{timeout:30000});
      for(const key of ['homes','row','herbalist','fletcher','gate']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewAlignment(k),key);
        await page.waitForTimeout(1200);
        await page.screenshot({path:resolve(out,'royal-haven-aligned-'+key+'.png'),timeout:30000});
      }
      streetAlignment=await page.evaluate(()=>window.DarkFallRoyalHaven.streetAlignment(true));
      await writeFile(resolve(out,'royal-haven-alignment-audit.json'),JSON.stringify(streetAlignment,null,2));
      const {row,homes,gate,benches,passage,herbalist,enchanter,fletcher,alleys,crossStreet,pavingReady}=streetAlignment;
      if(!pavingReady||benches.remaining!==0||benches.removed<10||benches.clearCenters<10||
         homes.length!==2||homes.some(o=>o.approach.bad)||gate.opening.some(x=>x<.9)||passage.arch.bad||
         row.some(o=>!o.ready||Math.hypot(o.door[0]-o.artDoor[0],o.door[1]-o.artDoor[1])>.01||o.height<78||o.doorWidth<50||o.approach.bad)||
         alleys.some(o=>o.bad)||crossStreet.bad||
         [herbalist,enchanter,fletcher].some(a=>!a.installed||a.lanes.bad||a.residents.bad||a.shops.some(s=>s.foot.bad||!s.entrance.every(Boolean))))
        throw new Error('Straight street / bench clearance audit failed: '+JSON.stringify(streetAlignment));
      console.log('Royal Haven straight shop and gatehouse layout PASS',JSON.stringify(streetAlignment));
    }
    let merchantQuarter=null;
    if(['Dark Fall V1515','Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.merchantQuarter();return a.row.every(o=>o.ready)&&a.civic.every(o=>o.ready);},{},{timeout:30000});
      for(const key of ['merchants','residence','vacant','bell']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewQuarter(k),key);
        await page.waitForTimeout(1600);
        await page.screenshot({path:resolve(out,'royal-haven-quarter-'+key+'.png'),timeout:30000});
      }
      merchantQuarter=await page.evaluate(()=>window.DarkFallRoyalHaven.merchantQuarter(true));
      await writeFile(resolve(out,'royal-haven-quarter-audit.json'),JSON.stringify(merchantQuarter,null,2));
      const {row,civic,removedHouse,removedGallery,visualGap,seam,surfaces,routes,clearedLot,civicWalk,residence}=merchantQuarter;
      if(!removedHouse||!removedGallery||!seam.solid||visualGap< -30||visualGap>5||
         !surfaces.includes('merchants')||!surfaces.includes('vacantCourt')||
         row.some(o=>!o.ready||!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>.01||o.height<78||o.doorWidth<50||o.approach.bad)||
         civic.some(o=>!o.ready||o.opening?.some(x=>x<.9))||
         routes.some(o=>o.bad)||clearedLot.bad||!civicWalk.installed||civicWalk.passage.bad||civicWalk.routes.bad||civicWalk.people.bad||
         !residence.installed||residence.lanes.bad||residence.residents.bad||residence.shops.some(o=>o.foot.bad||!o.entrance.every(Boolean)))
        throw new Error('Merchant terrace and civic square audit failed: '+JSON.stringify(merchantQuarter));
      console.log('Royal Haven merchant terrace / civic square PASS',JSON.stringify(merchantQuarter));
    }
    let foundryDistrict=null;
    if(['Dark Fall V1516','Dark Fall V1517'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.foundryDistrict();return a.shops.every(o=>o.ready)&&a.gallery.ready&&a.townhouse.ready;},{},{timeout:30000});
      for(const key of ['forge','armor','leather','corridor','townhouse']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewFoundry(k),key);
        await page.waitForTimeout(1400);
        await page.screenshot({path:resolve(out,'royal-haven-foundry-'+key+'.png'),timeout:30000});
      }
      foundryDistrict=await page.evaluate(()=>window.DarkFallRoyalHaven.foundryDistrict(true));
      await writeFile(resolve(out,'royal-haven-foundry-audit.json'),JSON.stringify(foundryDistrict,null,2));
      const {shops,gallery,townhouse,surfaces,routes}=foundryDistrict;
      if(shops.length!==3||shops.some(o=>!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>.01||o.doorHeight<78||o.doorWidth<50||o.footprint.bad||o.approach.bad)||
         !gallery.opening?.length||gallery.opening.some(x=>x<.9)||gallery.walk.bad||!gallery.piers.every(Boolean)||
         !townhouse.artDoor||Math.hypot(townhouse.artDoor[0]-townhouse.door[0],townhouse.artDoor[1]-townhouse.door[1])>.01||townhouse.approach.bad||
         !['forge','armor','leather'].every(k=>surfaces.includes(k))||routes.some(o=>o.bad))
        throw new Error('Foundry district geometry and walkability audit failed: '+JSON.stringify(foundryDistrict));
      console.log('Royal Haven foundry district and open gallery PASS',JSON.stringify(foundryDistrict));
    }
    let residentialDistrict=null;
    if(status.title==='Dark Fall V1517'){
      await page.waitForFunction(()=>window.DarkFallRoyalHaven.residentialDistrict().homes.every(o=>o.ready),{},{timeout:30000});
      for(const key of ['cottage','stone','lane','court']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewResidential(k),key);
        await page.waitForTimeout(1500);
        await page.screenshot({path:resolve(out,'royal-haven-residential-'+key+'.png'),timeout:30000});
      }
      residentialDistrict=await page.evaluate(()=>window.DarkFallRoyalHaven.residentialDistrict(true));
      await writeFile(resolve(out,'royal-haven-residential-audit.json'),JSON.stringify(residentialDistrict,null,2));
      const {homes,surfaces,routes}=residentialDistrict;
      if(homes.length!==2||homes.some(o=>!o.door||!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>.01||o.doorHeight<78||o.doorWidth<47||o.footprint.bad||o.approach.bad)||
         !['cottageCourt','stoneCourt','sideLane','foundryCrossing','foundryCorner'].every(k=>surfaces.includes(k))||routes.some(o=>o.bad))
        throw new Error('Residential geometry, paving and walking audit failed: '+JSON.stringify(residentialDistrict));
      console.log('Royal Haven residential street integration PASS',JSON.stringify(residentialDistrict));
    }
    await writeFile(resolve(out,'royal-haven-runtime.json'),JSON.stringify({town,art,streetArt,civicArt,marketArt,districtArt,fortificationArt,streetLayout,streetAlignment,merchantQuarter,foundryDistrict,residentialDistrict,errors},null,2));
    if(errors.some(e=>/ReferenceError|SyntaxError|TypeError|InvalidStateError|not defined/i.test(e)))throw new Error('Fatal Royal Haven JavaScript error: '+errors.join('\n').slice(0,2000));
  }
  // Record pixel samples for diagnostics; some games draw via WebGL or a second canvas.
  // Do not fail on transparent samples until the active rendering canvas is identified.
  if (status.canvasDimensions.some(c => c.width <= 0 || c.height <= 0)) throw new Error('Invalid canvas pixel dimensions');
  if (errors.some(e => /ReferenceError|SyntaxError|not defined/i.test(e))) throw new Error('Fatal JavaScript error during startup');
} finally {
  await browser.close();
}
