import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
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
    bodyText: document.body?.innerText?.slice(0, 500) ?? '',
    width: innerWidth,
    height: innerHeight,
  }));
  await page.screenshot({ path: resolve(out, 'startup.png'), fullPage: false, timeout: 20000 });
  await writeFile(resolve(out, 'report.json'), JSON.stringify({ status, errors }, null, 2));
  console.log(JSON.stringify({ status, errors: errors.slice(0, 12) }, null, 2));
  if (!status.canvases) throw new Error('Game canvas not found');
  if (errors.some(e => /ReferenceError|SyntaxError|not defined/i.test(e))) throw new Error('Fatal JavaScript error during startup');
} finally {
  await browser.close();
}
