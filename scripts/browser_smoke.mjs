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
    const behindDraws=draws,restored=c===main&&main.getTransform().a===.8;
    p.y=220;rh1457Facade(bounds,205,facade);
    const front=pixel(140,109);
    return {center,feet,feather,roof,street,front,behindDraws,draws,restored};
  });
  await probe.close();
  if(cutaway.center[1]>75||cutaway.feet[1]>85||cutaway.feather[1]<=cutaway.center[1]||
     cutaway.roof[1]<170||cutaway.front[1]<170||cutaway.street[1]!==48||
     cutaway.behindDraws!==1||cutaway.draws!==2||!cutaway.restored||
     [cutaway.center,cutaway.feet,cutaway.street,cutaway.roof].some(p=>p[3]!==255))
    throw new Error('Royal Haven cutaway pixel test failed: '+JSON.stringify(cutaway));
  await writeFile(resolve(out,'royal-haven-cutaway.json'),JSON.stringify(cutaway,null,2));
  console.log('Royal Haven cutaway pixel test PASS',cutaway);
  await page.goto('file://' + resolve('app/src/main/assets/index.html'), { waitUntil: 'domcontentloaded', timeout: 60000 });
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
  if(status.title==='Dark Fall V1510'){
    // The built-in entry point is used for an exterior runtime smoke, not a modified game.
    const town=await page.evaluate(()=>{const api=window.DarkFallRoyalHaven;if(!api)return false;api.open();return api.active;});
    if(!town)throw new Error('Royal Haven failed to open');
    await page.waitForTimeout(4000);
    await page.screenshot({path:resolve(out,'royal-haven-exterior.png'),timeout:30000});
    await writeFile(resolve(out,'royal-haven-runtime.json'),JSON.stringify({town,errors},null,2));
    if(errors.some(e=>/ReferenceError|SyntaxError|TypeError|InvalidStateError|not defined/i.test(e)))throw new Error('Fatal Royal Haven JavaScript error: '+errors.join('\n').slice(0,2000));
  }
  // Record pixel samples for diagnostics; some games draw via WebGL or a second canvas.
  // Do not fail on transparent samples until the active rendering canvas is identified.
  if (status.canvasDimensions.some(c => c.width <= 0 || c.height <= 0)) throw new Error('Invalid canvas pixel dimensions');
  if (errors.some(e => /ReferenceError|SyntaxError|not defined/i.test(e))) throw new Error('Fatal JavaScript error during startup');
} finally {
  await browser.close();
}
