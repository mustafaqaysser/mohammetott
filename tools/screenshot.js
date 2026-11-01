// Screenshot every section of index.html at desktop (1440) and mobile (375).
//   node tools/screenshot.js [outDir]
// Uses reduced-motion so animations are captured in their final state.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const root = path.resolve(__dirname, '..');
const out = path.resolve(process.argv[2] || path.join(root, 'screenshots'));
const url = 'file://' + path.join(root, 'index.html');

const targets = [
  ['01-cover', '#cover'],
  ['02-brief', '#brief'],
  ['03-concept', '#concept'],
];
for (const [k, n] of [['a', 'codex'], ['b', 'model'], ['c', 'monolith']]) {
  const base = `#dir-${k}`;
  const i = { a: 4, b: 5, c: 6 }[k];
  targets.push([`0${i}-${k}-${n}-0-opener`, `${base} .dir-open`]);
  for (let b = 1; b <= 7; b++) {
    const name = ['construction', 'lockups', 'symbol', 'colour', 'typography', 'applications', 'rationale'][b - 1];
    targets.push([`0${i}-${k}-${n}-${b}-${name}`, `${base} .blk:nth-of-type(${b})`]);
  }
}
targets.push(['07-compare', '#compare'], ['08-next', '#next']);

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  for (const [label, width] of [['desktop', 1440], ['mobile', 375]]) {
    const dir = path.join(out, label);
    fs.mkdirSync(dir, { recursive: true });
    const page = await browser.newPage({
      viewport: { width, height: label === 'desktop' ? 900 : 812 },
      deviceScaleFactor: label === 'desktop' ? 1 : 2,
      reducedMotion: 'reduce',
    });
    page.on('console', m => { if (m.type() === 'error') errors.push(`${label}: ${m.text()}`); });
    page.on('pageerror', e => errors.push(`${label}: ${e.message}`));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    await page.addStyleTag({ content: '.nav{display:none!important}' });
    await page.waitForTimeout(100);
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    if (sw > width) errors.push(`${label}: horizontal overflow ${sw}px > ${width}px`);
    for (const [name, sel] of targets) {
      const el = await page.$(sel);
      if (!el) { errors.push(`missing ${sel}`); continue; }
      await el.screenshot({ path: path.join(dir, `${name}.png`) });
    }
    await page.close();
  }
  await browser.close();
  console.log(errors.length ? errors.join('\n') : 'no console errors, no overflow');
})();
