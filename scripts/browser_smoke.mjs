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
  await page.goto('file://' + resolve('app/src/main/assets/index.html'), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  const status = await page.evaluate(() => ({
    title: document.title,
    canvases: document.querySelectorAll('canvas').length,
    canvasDimensions: [...document.querySelectorAll('canvas')].map(c => ({ width: c.width, height: c.height, cssWidth: c.getBoundingClientRect().width, cssHeight: c.getBoundingClientRect().height })),
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
  if (status.canvasDimensions.some(c => c.width <= 0 || c.height <= 0)) throw new Error('Invalid canvas pixel dimensions');
  if (errors.some(e => /ReferenceError|SyntaxError|not defined/i.test(e))) throw new Error('Fatal JavaScript error during startup');
} finally {
  await browser.close();
}
