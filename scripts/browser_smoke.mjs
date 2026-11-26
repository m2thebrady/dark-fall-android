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
  await probe.addScriptTag({content:await readFile('game-bundle/patches/royal-haven-v1518.js','utf8')});
  const optimizedCutaway=await probe.evaluate(()=>{
    const main=c,b={left:86,top:65,w:108,h:140,rh1518LocalPad:8};
    const paint=()=>{c.fillStyle='#b2b5b9';c.fillRect(b.left,b.top,b.w,b.h);c.fillStyle='#544431';c.fillRect(108,90,40,60);};
    const reset=()=>{main.setTransform(1,0,0,1,0,0);main.fillStyle='#983027';main.fillRect(0,0,256,240);main.setTransform(.8,0,0,.8,12,16);p.x=140;p.y=140;};
    reset();rh1457Facade(b,205,paint);let old=main.getImageData(0,0,256,240).data;
    reset();rh1518MaskFacade(b,paint);let fresh=main.getImageData(0,0,256,240).data;
    let max=0,changed=0;for(let i=0;i<old.length;i++){const d=Math.abs(old[i]-fresh[i]);max=Math.max(max,d);if(d>1)changed++;}
    return {max,changed,local:rh1518Stats.localCutaways,pixels:rh1518Stats.cutawayPixels,fullPixels:rh1518Stats.fullEquivalentPixels};
  });
  if(optimizedCutaway.max>2||optimizedCutaway.changed>10||optimizedCutaway.local!==1||optimizedCutaway.pixels>=optimizedCutaway.fullPixels*.5)
    throw new Error('Optimized local cutaway differs from full compositing: '+JSON.stringify(optimizedCutaway));
  console.log('Local cutaway pixel equivalence and transfer reduction PASS',optimizedCutaway);
  await writeFile(resolve(out,'royal-haven-local-cutaway.json'),JSON.stringify(optimizedCutaway,null,2));
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
  if(['Dark Fall V1510','Dark Fall V1511','Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
    const masterGround=['Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title);
    // The built-in entry point is used for an exterior runtime smoke, not a modified game.
    await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven?.exteriorArt?.();return a?.length===16&&a.every(s=>s.ready&&(!s.active||s.bounds))&&window.DarkFallRoyalHaven.secondaryArt().every(s=>s.ready);},{},{timeout:45000});
    const art=await page.evaluate(()=>({stores:window.DarkFallRoyalHaven.exteriorArt(),homes:window.DarkFallRoyalHaven.secondaryArt()}));
    console.log('Royal Haven artwork readiness',JSON.stringify(art));
    const first=page.locator('.chooseCard').first();
    if(await first.isVisible())await first.click({timeout:15000});
    if(['Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      // Class selection automatically opens Royal Haven. Switch to the actual
      // forest through the supported API before testing its layout and controls.
      await page.waitForFunction(()=>window.DarkFallRoyalHaven?.active,{},{timeout:30000});
      await page.evaluate(()=>window.DarkFallRoyalHaven.close());
      await page.waitForFunction(()=>!window.dfTownActive&&!window.DarkFallRoyalHaven.active,{},{timeout:20000});
      const samples=[];
      const waitViewport=async()=>{
        await page.waitForFunction(()=>{
          const f=window.DarkFallForestViewport?.();
          return !!f&&!window.dfTownActive&&!window.DarkFallRoyalHaven.active&&Math.abs(f.wrap.x)<1&&Math.abs(f.wrap.y)<1&&Math.abs(f.wrap.width-innerWidth)<2&&Math.abs(f.wrap.height-innerHeight)<2&&
            Math.abs(f.css.x-f.stage.x)<1&&Math.abs(f.css.y-f.stage.y)<1&&Math.abs(f.css.width-f.stage.width)<1&&Math.abs(f.css.height-f.stage.height)<1&&
            Math.abs(f.css.x)<1&&Math.abs(f.css.width-innerWidth)<2&&Math.abs(f.css.y+f.css.height-innerHeight)<2&&f.scaleMismatch<.005&&f.pointerError<1e-7&&f.area<=f.cap&&
            f.logical[0]===f.backing[0]&&f.logical[1]===f.backing[1]&&f.camera&&f.player;
        },{},{timeout:20000});
        await page.waitForFunction(()=>{
          const c=document.getElementById('screen');
          return c.getContext('2d').getImageData(Math.floor(c.width/2),Math.floor(c.height/2),1,1).data[3]===255;
        },{},{timeout:20000});
        return await page.evaluate(()=>window.DarkFallForestViewport());
      };
      for(const [width,height] of [[2048,1080],[2560,1080],[780,390],[390,844],[1280,720]]){
        await page.setViewportSize({width,height});
        const sample=await waitViewport();samples.push(sample);
        if(width===2048||width===780)await page.screenshot({path:resolve(out,'forest-fill-'+width+'x'+height+'.png'),timeout:30000});
      }
      // Exercise the actual Fullscreen button; unsupported headless/browser modes
      // are recorded separately from the mandatory full-window geometry checks.
      let native='not supported';
      if(await page.evaluate(()=>!!document.fullscreenEnabled)){
        await page.locator('#fullscreenBtn').click({timeout:10000});
        try{await page.waitForFunction(()=>document.fullscreenElement?.id==='gameWrap',{},{timeout:5000});native='entered';}
        catch{native='browser denied fullscreen';}
        if(native==='entered'){
          samples.push(await waitViewport());
          await page.screenshot({path:resolve(out,'forest-native-fullscreen.png'),timeout:30000});
          await page.evaluate(()=>document.exitFullscreen());
          await page.waitForFunction(()=>!document.fullscreenElement);
          samples.push(await waitViewport());native='entered and exited';
        }
      }
      await writeFile(resolve(out,'forest-viewport-audit.json'),JSON.stringify({samples,native},null,2));
      console.log('Forest responsive canvas geometry and pixel budgets PASS',JSON.stringify({samples,native}));
    }
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
    await page.waitForFunction(master=>{const a=window.DarkFallRoyalHaven.marketArt();return a.assets.every(o=>o.ready)&&a.eastTiles===4&&a.eastReady.includes('8:3')&&(master||a.squareReady)&&a.contactCount>=7;},masterGround,{timeout:30000});
    await page.waitForTimeout(2500);
    const marketArt=await page.evaluate(()=>window.DarkFallRoyalHaven.marketArt());
    if(marketArt.assets.some(o=>!o.instances.length)||marketArt.assets.filter(o=>o.key.startsWith('stall')).reduce((n,o)=>n+o.instances.length,0)!==4)throw new Error('Market art instance audit failed: '+JSON.stringify(marketArt));
    console.log('Royal Haven market graphics readiness',JSON.stringify(marketArt));
    await page.screenshot({path:resolve(out,'royal-haven-market.png'),timeout:30000});
    await writeFile(resolve(out,'royal-haven-market-audit.json'),JSON.stringify(marketArt,null,2));
    let districtArt=null;
    if(['Dark Fall V1511','Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
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
    if(['Dark Fall V1512','Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
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
    if(['Dark Fall V1513','Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.streetLayout();return a.row.every(o=>o.ready)&&a.court.every(o=>o.ready);},{},{timeout:30000});
      for(const key of ['courtyard','row','tailor','bakery']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewLayout(k),key);
        await page.waitForTimeout(1800);
        await page.screenshot({path:resolve(out,'royal-haven-layout-'+key+'.png'),timeout:30000});
      }
      streetLayout=await page.evaluate(()=>window.DarkFallRoyalHaven.streetLayout(true));
      await writeFile(resolve(out,'royal-haven-layout-audit.json'),JSON.stringify(streetLayout,null,2));
      const {row,court,trades,artisan,courtRoutes,crossStreet,pavingReady}=streetLayout;
      if(row.length!==3||court.length!==3||(!masterGround&&!pavingReady)||!trades.installed||!artisan.installed||
         row.some(o=>!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>2||o.height<78||o.doorWidth<50||o.approach.bad)||
         row.some(o=>o.door[1]!==1963)||court.some(o=>o.door&&o.doorHeight<73)||
         trades.lanes.bad||trades.residents.bad||artisan.lanes.bad||artisan.residents.bad||crossStreet.bad||courtRoutes.some(o=>o.bad))
        throw new Error('Street alignment/courtyard placement audit failed: '+JSON.stringify(streetLayout));
      console.log('Royal Haven street alignment and inward courtyard audit PASS',JSON.stringify(streetLayout));
    }
    let streetAlignment=null;
    if(['Dark Fall V1514','Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.streetAlignment();return a.row.every(o=>o.ready)&&a.gate.ready;},{},{timeout:30000});
      for(const key of ['homes','row','herbalist','fletcher','gate']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewAlignment(k),key);
        await page.waitForTimeout(1200);
        await page.screenshot({path:resolve(out,'royal-haven-aligned-'+key+'.png'),timeout:30000});
      }
      streetAlignment=await page.evaluate(()=>window.DarkFallRoyalHaven.streetAlignment(true));
      await writeFile(resolve(out,'royal-haven-alignment-audit.json'),JSON.stringify(streetAlignment,null,2));
      const {row,homes,gate,benches,passage,herbalist,enchanter,fletcher,alleys,crossStreet,pavingReady}=streetAlignment;
      if((!masterGround&&!pavingReady)||benches.remaining!==0||benches.removed<10||benches.clearCenters<10||
         homes.length!==2||homes.some(o=>o.approach.bad)||gate.opening.some(x=>x<.9)||passage.arch.bad||
         row.some(o=>!o.ready||Math.hypot(o.door[0]-o.artDoor[0],o.door[1]-o.artDoor[1])>.01||o.height<78||o.doorWidth<50||o.approach.bad)||
         alleys.some(o=>o.bad)||crossStreet.bad||
         [herbalist,enchanter,fletcher].some(a=>!a.installed||a.lanes.bad||a.residents.bad||a.shops.some(s=>s.foot.bad||!s.entrance.every(Boolean))))
        throw new Error('Straight street / bench clearance audit failed: '+JSON.stringify(streetAlignment));
      console.log('Royal Haven straight shop and gatehouse layout PASS',JSON.stringify(streetAlignment));
    }
    let merchantQuarter=null;
    if(['Dark Fall V1515','Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
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
         (!masterGround&&(!surfaces.includes('merchants')||!surfaces.includes('vacantCourt')))||
         row.some(o=>!o.ready||!o.artDoor||Math.hypot(o.artDoor[0]-o.door[0],o.artDoor[1]-o.door[1])>.01||o.height<78||o.doorWidth<50||o.approach.bad)||
         civic.some(o=>!o.ready||o.opening?.some(x=>x<.9))||
         routes.some(o=>o.bad)||clearedLot.bad||!civicWalk.installed||civicWalk.passage.bad||civicWalk.routes.bad||civicWalk.people.bad||
         !residence.installed||residence.lanes.bad||residence.residents.bad||residence.shops.some(o=>o.foot.bad||!o.entrance.every(Boolean)))
        throw new Error('Merchant terrace and civic square audit failed: '+JSON.stringify(merchantQuarter));
      console.log('Royal Haven merchant terrace / civic square PASS',JSON.stringify(merchantQuarter));
    }
    let foundryDistrict=null;
    if(['Dark Fall V1516','Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
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
         (!masterGround&&!['forge','armor','leather'].every(k=>surfaces.includes(k)))||routes.some(o=>o.bad))
        throw new Error('Foundry district geometry and walkability audit failed: '+JSON.stringify(foundryDistrict));
      console.log('Royal Haven foundry district and open gallery PASS',JSON.stringify(foundryDistrict));
    }
    let residentialDistrict=null;
    if(['Dark Fall V1517','Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
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
         (!masterGround&&!['cottageCourt','stoneCourt','sideLane','foundryCrossing','foundryCorner'].every(k=>surfaces.includes(k)))||routes.some(o=>o.bad))
        throw new Error('Residential geometry, paving and walking audit failed: '+JSON.stringify(residentialDistrict));
      console.log('Royal Haven residential street integration PASS',JSON.stringify(residentialDistrict));
    }
    let landmarkRenewal=null;
    if(['Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>window.DarkFallRoyalHaven.landmarkRenewal().entries.every(e=>e.ready),{},{timeout:30000});
      for(const key of ['mage','cave','cellar']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewLandmark(k),key);
        await page.waitForTimeout(1800);
        await page.screenshot({path:resolve(out,'royal-haven-landmark-'+key+'.png'),timeout:30000});
      }
      landmarkRenewal=await page.evaluate(()=>window.DarkFallRoyalHaven.landmarkRenewal(true));
      await writeFile(resolve(out,'royal-haven-landmark-audit.json'),JSON.stringify(landmarkRenewal,null,2));
      if(landmarkRenewal.entries.length!==3||landmarkRenewal.entries.some(e=>!e.ready||!e.artDoor||Math.hypot(e.artDoor[0]-e.door[0],e.artDoor[1]-e.door[1])>.01||e.doorWidth<47||e.doorHeight<78||!e.solid||e.approach.bad)||!landmarkRenewal.seatRemoved||!landmarkRenewal.seatClear)
        throw new Error('Royal Haven landmark fit and walkability audit failed: '+JSON.stringify(landmarkRenewal));
      console.log('Royal Haven three new landmarks and seat removal PASS',JSON.stringify(landmarkRenewal));
    }
    let groundPlan=null;
    if(masterGround){
      for(const key of ['foundry','merchants','craft','royal','market','residential','gate']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewGround(k),key);
        await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.groundPlan();return a.tiles.length&&a.tiles.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1200);
        await page.screenshot({path:resolve(out,'royal-haven-ground-'+key+'.png'),timeout:30000});
      }
      groundPlan=await page.evaluate(()=>window.DarkFallRoyalHaven.groundPlan(true));
      await writeFile(resolve(out,'royal-haven-ground-audit.json'),JSON.stringify(groundPlan,null,2));
      if(groundPlan.roadCount<20||groundPlan.courtCount<15||groundPlan.stats.readyFrames===0||
        groundPlan.market.rejected||groundPlan.market.moved.length!==6||groundPlan.cleared.some(o=>!o.clear)||
        !groundPlan.solidMarket||!groundPlan.fountainSolid||groundPlan.routes.some(r=>r.bad))
        throw new Error('Royal Haven master street geometry audit failed: '+JSON.stringify(groundPlan));
      console.log('Royal Haven connected ground plan and spacious market PASS',JSON.stringify(groundPlan));
    }
    let frontageAudit=null;
    if(['Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.evaluate(()=>window.DarkFallRoyalHaven.reviewGround('merchants'));
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.frontage();return a.ready&&a.stats.draws>0;},{},{timeout:30000});
      frontageAudit=await page.evaluate(()=>window.DarkFallRoyalHaven.frontage(true));
      if(frontageAudit.rows!==4||frontageAudit.removed.length!==8||frontageAudit.remaining!==0||
         frontageAudit.removed.some(r=>!r.wasSolid||!r.clear||r.crossing.bad)||
         frontageAudit.entrances.length!==12||frontageAudit.entrances.some(r=>r.approach.bad)||
         frontageAudit.relocated.length<12||!frontageAudit.solidMarket||frontageAudit.marketCount!==7||frontageAudit.stats.maxVisible>4)
        throw new Error('Storefront renewal audit failed: '+JSON.stringify(frontageAudit));
      await writeFile(resolve(out,'royal-haven-frontage-audit.json'),JSON.stringify(frontageAudit,null,2));
      await page.screenshot({path:resolve(out,'royal-haven-frontage-merchants.png'),timeout:30000});
      console.log('Royal Haven unobstructed merchant frontage PASS',JSON.stringify(frontageAudit));
    }
    if(['Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['gatehouse','longhouse','residences','south','herbs']){
        await page.evaluate(k=>window.DarkFallRoyalHaven.reviewLandscape(k),key);
        await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.landscape();return a.tiles.length&&a.tiles.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1000);
        await page.screenshot({path:resolve(out,'royal-haven-landscape-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.landscape(true));
      await writeFile(resolve(out,'royal-haven-landscape-audit.json'),JSON.stringify(a,null,2));
      if(a.tileCount!==27||a.linkCount<8||a.materials.length!==4||a.gardenCount<10||!a.gardenCentersClear||a.routes.some(r=>r.bad)||a.additionalDraws!==0)
       throw new Error('Landscape audit failed: '+JSON.stringify(a));
      console.log('Royal Haven V1524 landscape PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.northcourt();return a.installed&&a.homes.every(h=>h.ready);},{},{timeout:30000});
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.northcourt(true));
      await writeFile(resolve(out,'royal-haven-northcourt-audit.json'),JSON.stringify(a,null,2));
      if(!a.installed||a.homes.length!==2||a.homes.some(h=>!h.ready||h.doorHeight!==84||h.doorWidth<40)||
         a.routes.length!==3||a.routes.some(r=>r.bad)||a.groundTiles!==2||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('Northcourt audit failed: '+JSON.stringify(a));
      if(!await page.evaluate(()=>window.DarkFallRoyalHaven.reviewNorthcourt()))throw new Error('Northcourt review could not position camera');
      await page.waitForTimeout(1600);
      await page.screenshot({path:resolve(out,'royal-haven-northcourt.png'),timeout:30000});
      console.log('Royal Haven V1525 Northcourt PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.gardens(true));
      if(a.version!==1526||a.gardenCount!==15||a.kinds.length!==4||a.tiles.length<5||
         !a.centersClear||a.gardens.some(g=>!g.clear||g.roadClearance<5)||
         a.additionalDraws!==0||a.newColliders!==0||a.npcChanges!==0)
        throw new Error('V1526 garden clearance audit failed: '+JSON.stringify(a));
      for(const key of ['north','gatehouse','east','south','west']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewGardens(k),key))throw new Error('Garden review missing '+key);
        await page.waitForFunction(()=>{const v=window.DarkFallRoyalHaven.gardens();return v.visibleTiles.length>0&&v.visibleTiles.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-gardens-'+key+'.png'),timeout:30000});
      }
      await writeFile(resolve(out,'royal-haven-garden-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1526 garden renewal PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.marketRenewal();return a.assets.length===2&&a.assets.every(o=>o.ready);},{},{timeout:30000});
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.marketRenewal(true));
      const expected={spice:{x:5820,y:2084,w:205,h:182,rx:59,ry:27,flip:false},pottery:{x:6280,y:2085,w:207,h:184,rx:60,ry:27,flip:true}};
      if(a.version!==1527||a.marketCount!==7||a.aprons!==2||a.bakedTiles.length!==2||
         a.assets.some(o=>!o.ready||!o.fit||!o.solid||o.counterHeight<42||o.counterHeight>68||Object.entries(expected[o.key]).some(([k,v])=>o.geometry[k]!==v))||
         a.newColliders!==0||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('V1527 permanent market audit failed: '+JSON.stringify(a));
      if(!await page.evaluate(()=>window.DarkFallRoyalHaven.reviewMarketRenewal()))throw new Error('Market renewal camera unavailable');
      await page.waitForFunction(()=>window.DarkFallRoyalHaven.groundPlan().tiles.every(t=>t.ready),{},{timeout:30000});
      await page.waitForTimeout(1500);
      await page.screenshot({path:resolve(out,'royal-haven-market-renewal.png'),timeout:30000});
      await writeFile(resolve(out,'royal-haven-market-renewal-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1527 market renewal PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.streetClearance(true));
      if(a.version!==1528||a.removed!==12||a.remaining!==0||a.clearCenters!==12||a.openCrossings!==12||
         a.courts.length!==6||a.bakedTiles.length!==6||a.marketCount!==7||a.structuralTowers!==8||
         a.cleared.some(o=>!o.wasBlocked||!o.free||o.crossing.bad)||
         a.newColliders!==0||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('V1528 open courtyard audit failed: '+JSON.stringify(a));
      for(const key of ['east','west']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewStreetClearance(k),key))throw new Error('Courtyard review camera unavailable: '+key);
        await page.waitForFunction(()=>window.DarkFallRoyalHaven.groundPlan().tiles.every(t=>t.ready),{},{timeout:30000});
        await page.waitForTimeout(1000);
        await page.screenshot({path:resolve(out,'royal-haven-open-courtyard-'+key+'.png'),timeout:30000});
      }
      await writeFile(resolve(out,'royal-haven-open-courtyard-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1528 open courtyard PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.marketCourt();return a.models.length===2&&a.models.every(o=>o.ready)&&a.carts.length===2&&a.carts.every(o=>o.ready);},{},{timeout:30000});
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.marketCourt(true));
      const expected={produce:{x:5850,y:1845,w:210,h:190,rx:62,ry:29,flip:false},cloth:{x:6280,y:1890,w:210,h:190,rx:62,ry:29,flip:true}};
      if(a.version!==1529||a.marketCount!==7||a.stallVariants.length!==4||new Set(a.stallVariants).size!==4||a.bakedTiles.length!==4||
         a.models.some(o=>!o.ready||!o.fit||!o.solid||o.counterHeight<42||o.counterHeight>68||Object.entries(expected[o.key]).some(([k,v])=>o.geometry[k]!==v))||
         a.carts.some(o=>!o.ready||!o.solid)||a.carts.filter(o=>o.reused&&o.art==='grainCart').length!==1||
         a.newColliders!==0||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('V1529 market court audit failed: '+JSON.stringify(a));
      if(!await page.evaluate(()=>window.DarkFallRoyalHaven.reviewMarketCourt()))throw new Error('Market court camera unavailable');
      await page.waitForFunction(()=>window.DarkFallRoyalHaven.groundPlan().tiles.every(t=>t.ready),{},{timeout:30000});
      await page.waitForTimeout(1300);
      await page.screenshot({path:resolve(out,'royal-haven-merchant-square.png'),timeout:30000});
      await writeFile(resolve(out,'royal-haven-merchant-square-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1529 merchant square PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.commercialPaving(true));
      if(a.version!==1530||a.regions.length!==6||a.bakedTiles.length!==12||Object.keys(a.materials).length!==3||
         a.regions.some(o=>!o.reviewClear||o.path.bad||!o.renderedTiles.length)||
         a.marketCount!==7||a.newColliders!==0||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('V1530 commercial paving audit failed: '+JSON.stringify(a));
      for(let i=0;i<a.regions.length;i++){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewCommercialPaving(k),i))throw new Error('Commercial paving review camera unavailable: '+i);
        await page.waitForFunction(()=>window.DarkFallRoyalHaven.commercialPaving().visible.every(t=>t.ready),{},{timeout:30000});
        await page.waitForTimeout(800);
        await page.screenshot({path:resolve(out,'royal-haven-commercial-paving-'+i+'.png'),timeout:30000});
      }
      await writeFile(resolve(out,'royal-haven-commercial-paving-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1530 commercial paving PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['castle','approach','fountain']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewRoyalPaving(k),key))throw new Error('Royal paving review unavailable: '+key);
        await page.waitForFunction(()=>{const r=window.DarkFallRoyalHaven.royalPaving();return r.overlay.ready&&r.castleReady&&r.visible.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-royal-paving-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.royalPaving(true));
      if(a.version!==1531||a.bakedTiles.length!==8||a.regions.length!==3||a.materials.length!==2||
         !a.overlay.ready||!a.overlay.alphaPreserved||a.overlay.width!==1120||a.overlay.height!==460||
         !a.castleReady||!a.castleSolid||!a.fountainSolid||a.castleApproach.bad||
         a.waterfallLoops!==2||!a.waterfallReady||a.royalGardens<4||a.regions.some(o=>o.path.bad||!o.reviewClear)||
         a.marketCount!==7||a.newColliders!==0||a.additionalGroundPasses!==0||a.npcChanges!==0)
        throw new Error('V1531 royal paving audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-royal-paving-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1531 royal paving PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['temple','observatory']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewNorthernPrecinct(k),key))throw new Error('Northern precinct review unavailable: '+key);
        await page.waitForFunction(()=>{const r=window.DarkFallRoyalHaven.northernPrecinct();return r.botanicalReady&&r.regions.every(t=>t.ready)&&r.visible.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-northern-precinct-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.northernPrecinct(true));
      if(a.version!==1532||a.regions.length!==2||a.bakedTiles.length!==8||!a.botanicalReady||
        a.regions.some(r=>!r.ready||r.path.bad||!r.reviewClear)||a.northAvenue.bad||
        a.terraces.length!==4||a.terraces.some(r=>!r.landing||!r.backSolid)||a.beds!==4||
        a.newColliders!==0||a.npcChanges!==0||a.additionalSurfaceDraws!==0)
        throw new Error('V1532 northern precinct audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-northern-precinct-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1532 northern precinct PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const proof=await page.evaluate(()=>window.DarkFallRoyalHaven.clarityProbe());
      if(proof.medium.tier!==1||!proof.medium.slow||proof.full.tier!==0||!proof.full.slow||
         proof.fast.tier!==0||proof.fast.slow||proof.emergency.tier!==2||!proof.emergency.slow)
        throw new Error('V1533 adaptive clarity recovery failed: '+JSON.stringify(proof));
      for(const key of ['north','south','east']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewGardens(k),key))throw new Error('Clarity review location unavailable: '+key);
        await page.waitForFunction(()=>{const q=window.DarkFallRoyalHaven.clarity();return q.facades.every(a=>a.ready)&&q.visible.every(a=>a.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-clarity-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.clarity(true));
      if(a.version!==1533||a.facades.length!==6||a.facades.some(r=>!r.ready||!r.alphaPreserved)||
         a.ground.length!==11||a.scales.join(',')!=='1,0.88,0.7'||!a.emergencyScalePreserved||
         a.zoom!==1.12||a.paths.some(r=>r.bad)||!a.gardenClear||a.extraFrameFilters||
         a.extraDraws||a.newColliders||a.npcChanges)
        throw new Error('V1533 clarity audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-clarity-audit.json'),JSON.stringify({a,proof},null,2));
      console.log('Royal Haven V1533 clarity and adaptive recovery PASS',JSON.stringify({a,proof}));
    }
    if(['Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['west','south','eastNorth','eastSouth','former']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewPerimeter(k),key))throw new Error('Tower review unavailable: '+key);
        await page.waitForFunction(()=>{const r=window.DarkFallRoyalHaven.perimeterRenewal();return r.models.every(m=>m.ready)&&r.visible.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-perimeter-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.perimeterRenewal(true));
      if(a.version!==1534||a.models.length!==3||a.models.some(t=>!t.ready)||a.towers.length!==8||
        a.towers.some(t=>!t.footprintPreserved||!t.baseFits||!t.naturalAspect||!t.solid||t.h<=t.previousH)||
        a.moved.length!==2||a.moved.some(t=>!t.oldCenterOpen||!t.newCenterSolid||t.crossing.bad||t.to[0]!==a.easternWallX)||
        a.review.some(p=>!p.clear)||a.paths.some(r=>r.bad)||a.changedCollisionCount||a.additionalDraws||a.npcChanges)
        throw new Error('V1534 perimeter watchtower audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-perimeter-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1534 perimeter watchtowers PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['west','east','south','gate']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewWalls(k),key))throw new Error('Wall review unavailable: '+key);
        await page.waitForFunction(()=>{const r=window.DarkFallRoyalHaven.wallRenewal();return r.curtain.every(t=>t.ready)&&r.sides.every(t=>t.ready)&&r.feet.every(t=>t.ready)&&r.visible.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-walls-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.wallRenewal(true));
      if(a.version!==1535||a.curtain.length!==8||a.sides.length!==4||a.feet.length!==12||
        [...a.curtain,...a.sides,...a.feet].some(t=>!t.ready)||a.seamAlphaMAE.some(e=>e>1)||
        !a.wallRefs||!a.footRefs||!a.sharedSources||a.runtimeWallBuilds||a.wallRasterPixels||
        !a.gateReady||!a.gateOpen||a.gatePath.bad||!a.curtainSolid||!a.sideSolid||
        a.review.some(r=>!r.clear)||a.newColliders||a.additionalDraws||a.npcChanges)
        throw new Error('V1535 connected fortifications audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-walls-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1535 connected fortifications and shared wall surfaces PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['well','bell','notice']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewPublic(k),key))throw new Error('Civic review unavailable: '+key);
        await page.waitForFunction(()=>window.DarkFallRoyalHaven.publicRenewal().assets.every(t=>t.ready),{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-civic-renewal-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.publicRenewal(true));
      if(a.version!==1536||a.assets.length!==3||a.assets.some(t=>!t.ready)||a.marketCount!==7||
        !a.wellSolid||!a.noticeStraight||!a.bellOpening||a.bellOpening.some(e=>e<.9)||
        a.passage.bad||a.civicRoutes.bad||a.civicFootprints.some(r=>r.foot.bad)||a.noticeApproach.bad||
        a.wellCirculation.bad||a.routes.length!==17||a.routes.some(r=>r.bad)||a.review.some(r=>!r.clear)||
        a.bakedTiles.length!==1||a.newColliders||a.additionalDraws||a.npcChanges)
        throw new Error('V1536 civic architecture audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-civic-renewal-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1536 civic architecture and walking paths PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['north','gatehouse','east','south','west','merchant']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewGardenRenewal(k),key))throw new Error('Garden renewal review unavailable: '+key);
        await page.waitForFunction(()=>{const v=window.DarkFallRoyalHaven.gardenRenewal();return v.visible.length>0&&v.visible.every(t=>t.ready);},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-living-gardens-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.gardenRenewal(true));
      if(a.version!==1537||a.plots.length!==15||a.variants.length!==6||
        a.expanded!==6||a.relocated!==5||a.bakedTiles.length!==12||
        a.plots.some(g=>!g.centerClear||!g.samples||g.bad||g.clearance<5)||
        a.routes.length!==17||a.routes.some(r=>r.bad)||a.links.some(r=>r.bad)||
        a.review.some(r=>!r.clear)||a.additionalDraws||a.newColliders||a.npcChanges)
        throw new Error('V1537 garden renewal clearance audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-living-gardens-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1537 renewed ground gardens and clear circulation PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      for(const key of ['observatory','east','craft','south']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewFixtures(k),key))throw new Error('Fixture review unavailable: '+key);
        await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.fixtureRenewal();return a.models.every(m=>m.ready)&&a.allFramesReady;},{},{timeout:30000});
        await page.waitForTimeout(1300);
        await page.screenshot({path:resolve(out,'royal-haven-street-craft-'+key+'.png'),timeout:30000});
      }
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.fixtureRenewal(true));
      if(a.version!==1538||!a.installed||a.models.length!==15||a.models.some(m=>!m.ready)||
        a.instances.length!==12||a.instances.some(o=>!o.ready||!o.soft||!o.centerClear||o.roadClearance<0)||
        a.frameSlots!==16||a.uniqueLaundryFrames!==10||!a.allFramesReady||!a.fixedArtisan||a.lanternCount!==40||
        a.moves.length!==3||a.moves.some(m=>!m.located||!m.soft||!m.oldClear||!m.samples||m.bad||m.clearance<12||m.gardenOverlap)||
        a.routes.length!==17||a.routes.some(r=>r.bad)||a.links.some(r=>r.bad)||a.review.some(r=>!r.clear)||
        a.additionalDrawLayers||a.newColliders||a.npcChanges||a.lanternChanges)
        throw new Error('V1538 street craft and fixture clearance audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-street-craft-audit.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1538 street craft and clear pedestrian space PASS',JSON.stringify(a));
    }
    if(['Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      await page.waitForFunction(()=>window.DarkFallRoyalHaven.landscapeRenewal().models.every(m=>m.ready),{},{timeout:30000});
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.landscapeRenewal());
      if(a.models.length!==4||a.models.some(m=>!m.ready)||a.newColliders||a.newDrawLayers||a.npcChanges)throw new Error('V1539 natural landscaping audit failed: '+JSON.stringify(a));
      await writeFile(resolve(out,'royal-haven-natural-landscaping.json'),JSON.stringify(a,null,2));
      console.log('Royal Haven V1539 natural landscaping PASS',JSON.stringify(a));
    }
    if(status.title==='Dark Fall V1540'){
      await page.waitForFunction(()=>{const a=window.DarkFallRoyalHaven.canopyRenewal();return a.models.every(m=>m.ready)&&a.retain.every(m=>m.ready);},{},{timeout:30000});
      const a=await page.evaluate(()=>window.DarkFallRoyalHaven.canopyRenewal(true));
      if(a.version!==1540||a.models.length!==8||a.models.some(m=>!m.ready||!m.instances||Math.abs(m.footOffset)>1||m.visibleHeight<.68)||
        a.retain.length!==4||a.retain.some(m=>!m.ready)||a.replacedInstances!==41||a.treeCount!==59||
        a.routes.length!==17||a.routes.some(r=>r.bad)||a.links.length!==12||a.links.some(r=>r.bad)||a.additionalDrawLayers||a.newColliders||a.npcChanges)
        throw new Error('V1540 tree variety and path audit failed: '+JSON.stringify(a));
      const interior=await page.evaluate(()=>window.DarkFallRoyalHaven.interiorReadiness(true));
      if(!interior.audited||interior.rows.length!==20||interior.bespoke!==8||interior.landmarks!==4||interior.approachIssues.length)
        throw new Error('V1540 exterior interior-readiness audit failed: '+JSON.stringify(interior));
      await writeFile(resolve(out,'royal-haven-canopy-audit.json'),JSON.stringify(a,null,2));
      await writeFile(resolve(out,'royal-haven-interior-readiness.json'),JSON.stringify(interior,null,2));
      console.log('Royal Haven V1540 tree silhouettes and interior entrance readiness PASS',JSON.stringify({canopy:a,interior}));
      for(const key of ['south','herbs']){
        if(!await page.evaluate(k=>window.DarkFallRoyalHaven.reviewLandscape(k),key))throw new Error('Canopy review point unavailable: '+key);
        await page.waitForTimeout(1400);
        await page.screenshot({path:resolve(out,'royal-haven-canopy-'+key+'.png'),timeout:30000});
      }
    }
    let navigationAudit=null;
    if(['Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const initial=await page.evaluate(()=>window.DarkFallRoyalHaven.navigation());
      if(initial.inside||initial.zoom!==1.12||initial.benches!==0||initial.removedSeats<10||initial.openDecor<10||
         !initial.solidFountain||initial.solidMarket!==initial.marketCount||initial.roundTrip>.001||
         Math.abs(initial.view[0]-1280/1.12)>.001)throw new Error('Exterior camera or pedestrian obstacle audit failed: '+JSON.stringify(initial));
      const crossing=await page.evaluate(()=>window.DarkFallRoyalHaven.reviewWalk());
      if(!crossing)throw new Error('No newly open street obstacle crossing');
      await page.waitForTimeout(500);
      const key=crossing.dir>0?'ArrowRight':'ArrowLeft';
      await page.keyboard.down(key);
      try{
        await page.waitForFunction(c=>{const n=window.DarkFallRoyalHaven.navigation();return !n.inside&&(n.x-c.x)*c.dir>16;},crossing,{timeout:8000});
      }finally{await page.keyboard.up(key);}
      const after=await page.evaluate(()=>window.DarkFallRoyalHaven.navigation());
      if(Math.abs(after.y-crossing.y)>3||after.roundTrip>.001)throw new Error('Former small obstacle does not allow straight movement: '+JSON.stringify({crossing,after}));
      navigationAudit={initial,crossing,after};
      await writeFile(resolve(out,'royal-haven-navigation-audit.json'),JSON.stringify(navigationAudit,null,2));
      await page.screenshot({path:resolve(out,'royal-haven-walk-clearance.png'),timeout:30000});
      console.log('Royal Haven closer zoom and real keyboard traversal of removed physics PASS',JSON.stringify(navigationAudit));
    }
    let performanceAudit=null;
    if(['Dark Fall V1518','Dark Fall V1519','Dark Fall V1520','Dark Fall V1521','Dark Fall V1522','Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
      const begin=await page.evaluate(()=>window.DarkFallRoyalHaven.performance());
      await page.setViewportSize({width:390,height:844});
      await page.evaluate(()=>{window.DarkFallRoyalHaven.close();window.DarkFallRoyalHaven.open();});
      await page.waitForTimeout(1600);
      const mobileBegin=await page.evaluate(()=>window.DarkFallRoyalHaven.performance());
      const readings=[];
      for(const [review,key] of [['reviewFoundry','corridor'],['reviewResidential','lane'],['reviewFoundry','forge'],['reviewResidential','cottage']]){
        await page.evaluate(([review,key])=>window.DarkFallRoyalHaven[review](key),[review,key]);
        await page.waitForTimeout(1800);
        readings.push(await page.evaluate(()=>window.DarkFallRoyalHaven.performance()));
      }
      await page.keyboard.down('ArrowRight');await page.waitForTimeout(750);await page.keyboard.up('ArrowRight');
      await page.waitForTimeout(2400);
      const end=await page.evaluate(()=>window.DarkFallRoyalHaven.performance());
      await page.screenshot({path:resolve(out,'royal-haven-performance-mobile.png'),timeout:30000});
      performanceAudit={begin,mobileBegin,readings,end};
      await writeFile(resolve(out,'royal-haven-performance-audit.json'),JSON.stringify(performanceAudit,null,2));
      if(end.registeredImages!==begin.registeredImages||end.maxBuilds>2||end.frames<=mobileBegin.frames||end.tileHits<=begin.tileHits||
         end.localCutaways<1||end.cutawayPixels>=end.fullEquivalentPixels||[...readings,end].some(x=>x.streetTiles>x.streetLimit||x.staticTiles>14||x.terrainImages>20||x.shoulderImages>4))
        throw new Error('Royal Haven resource and cache budget audit failed: '+JSON.stringify(performanceAudit));
      console.log('Royal Haven mobile viewport cache and render workload audit PASS',JSON.stringify(performanceAudit));
      if(['Dark Fall V1523','Dark Fall V1524','Dark Fall V1525','Dark Fall V1526','Dark Fall V1527','Dark Fall V1528','Dark Fall V1529','Dark Fall V1530','Dark Fall V1531','Dark Fall V1532','Dark Fall V1533','Dark Fall V1534','Dark Fall V1535','Dark Fall V1536','Dark Fall V1537','Dark Fall V1538','Dark Fall V1539','Dark Fall V1540'].includes(status.title)){
        const session=await page.context().newCDPSession(page);
        await session.send('Emulation.setCPUThrottlingRate',{rate:2});
        try{
          const crossing=await page.evaluate(()=>window.DarkFallRoyalHaven.reviewWalk());
          if(!crossing)throw new Error('No clear lane for throttled movement');
          await page.waitForTimeout(750);
          const before=await page.evaluate(()=>window.DarkFallRoyalHaven.performance());
          const started=Date.now();
          await page.keyboard.down(crossing.dir>0?'ArrowRight':'ArrowLeft');
          try{
            await page.waitForFunction(c=>{const n=window.DarkFallRoyalHaven.navigation();return !n.inside&&(n.x-c.x)*c.dir>16;},crossing,{timeout:12000});
          }finally{await page.keyboard.up(crossing.dir>0?'ArrowRight':'ArrowLeft');}
          await page.waitForTimeout(3000);
          const after=await page.evaluate(()=>window.DarkFallRoyalHaven.performance());
          const moved=await page.evaluate(()=>window.DarkFallRoyalHaven.navigation());
          const elapsedMs=Date.now()-started,updates=after.optimization.cadence.updates-before.optimization.cadence.updates,
            renders=after.optimization.cadence.presents-before.optimization.cadence.presents,
            sheetBuilds=after.optimization.actor.builds-before.optimization.actor.builds;
          const stress={elapsedMs,updates,renders,sheetBuilds,before,after,crossing,moved};
          if(updates<12||renders<4||after.optimization.actor.pixels>after.optimization.actor.budget||
             after.optimization.actor.pages>12||sheetBuilds>Math.ceil(elapsedMs/180)+2||
             (after.byKind.actor||0)!==0||Math.abs(moved.y-crossing.y)>4||moved.inside)
            throw new Error('V1523 animation cache and throttled-input stress audit failed: '+JSON.stringify(stress));
          await writeFile(resolve(out,'royal-haven-performance-stress.json'),JSON.stringify(stress,null,2));
          console.log('Royal Haven 2x CPU-throttled movement and bounded actor atlas PASS',JSON.stringify(stress));
        }finally{await session.send('Emulation.setCPUThrottlingRate',{rate:1});await session.detach();}
      }
      await page.setViewportSize({width:1280,height:720});
    }
    await writeFile(resolve(out,'royal-haven-runtime.json'),JSON.stringify({town,art,streetArt,civicArt,marketArt,districtArt,fortificationArt,streetLayout,streetAlignment,merchantQuarter,foundryDistrict,residentialDistrict,landmarkRenewal,groundPlan,frontageAudit,navigationAudit,performanceAudit,errors},null,2));
    if(errors.some(e=>/ReferenceError|SyntaxError|TypeError|InvalidStateError|not defined/i.test(e)))throw new Error('Fatal Royal Haven JavaScript error: '+errors.join('\n').slice(0,2000));
  }
  // Record pixel samples for diagnostics; some games draw via WebGL or a second canvas.
  // Do not fail on transparent samples until the active rendering canvas is identified.
  if (status.canvasDimensions.some(c => c.width <= 0 || c.height <= 0)) throw new Error('Invalid canvas pixel dimensions');
  if (errors.some(e => /ReferenceError|SyntaxError|not defined/i.test(e))) throw new Error('Fatal JavaScript error during startup');
} finally {
  await browser.close();
}

