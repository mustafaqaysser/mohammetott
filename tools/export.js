// Renders every export asset for the identity package.
//   node tools/export.js <outDir>
// - book/      : one high-res JPEG per presentation section (→ PDF in package.py)
// - mockups/   : each application mockup at 2.5x, per direction
// - logos/     : every SVG → vector PDF + transparent PNGs (512/1024/2048)
// - favicons/  : symbol small master at 16/32/48/64/180/512 px
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const root = path.resolve(__dirname, '..');
const out = path.resolve(process.argv[2] || path.join(root, 'export'));
const url = 'file://' + path.join(root, 'index.html');
const DIRS = [['a', 'codex', 'A-codex'], ['b', 'model', 'B-model'], ['c', 'monolith', 'C-monolith']];
const BLOCKS = ['construction', 'lockups', 'symbol', 'colour', 'typography', 'applications', 'rationale'];
const MOCKS = ['hoarding', 'business-card', 'payment-report', 'instagram', 'letterhead', 'helmet-vest'];

const mk = d => { fs.mkdirSync(d, { recursive: true }); return d; };

(async () => {
  const browser = await chromium.launch();

  // ---- presentation pages -------------------------------------------------
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.addStyleTag({ content: '.nav{display:none!important}' });
  await page.waitForTimeout(500);
  const book = mk(path.join(out, 'book'));
  const targets = [['01-cover', '#cover'], ['02-brief', '#brief'], ['03-concept', '#concept']];
  DIRS.forEach(([k, n], i) => {
    targets.push([`0${4 + i}-${k}-${n}-0-opener`, `#dir-${k} .dir-open`]);
    BLOCKS.forEach((b, j) => targets.push([`0${4 + i}-${k}-${n}-${j + 1}-${b}`, `#dir-${k} .blk:nth-of-type(${j + 1})`]));
  });
  targets.push(['07-compare', '#compare'], ['08-next', '#next']);
  for (const [name, sel] of targets) {
    const el = await page.$(sel);
    await el.screenshot({ path: path.join(book, `${name}.jpg`), type: 'jpeg', quality: 90 });
  }
  await page.close();

  // ---- mockups ------------------------------------------------------------
  const mp = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2.5, reducedMotion: 'reduce' });
  await mp.goto(url, { waitUntil: 'networkidle' });
  await mp.evaluate(() => document.fonts.ready);
  await mp.addStyleTag({ content: '.nav{display:none!important}' });
  await mp.waitForTimeout(500);
  for (const [k, n, slug] of DIRS) {
    const dir = mk(path.join(out, 'mockups', slug));
    const figs = await mp.$$(`#dir-${k} .mk-fig`);
    for (let i = 0; i < figs.length; i++) {
      await figs[i].screenshot({ path: path.join(dir, `davinci-${k}-${n}-mockup-${String(i + 1).padStart(2, '0')}-${MOCKS[i]}.png`) });
    }
  }
  const cmp = mk(path.join(out, 'mockups', 'comparison'));
  await (await mp.$('#compare .cmp-grid')).screenshot({ path: path.join(cmp, 'davinci-comparison-hoarding-and-card.png') });
  await mp.close();

  // ---- logos: SVG → PDF (vector) + PNG -------------------------------------
  const lp = await browser.newPage();
  for (const [, , slug] of DIRS) {
    const src = path.join(root, 'logos', slug);
    const pdfDir = mk(path.join(out, 'logos', slug, 'PDF'));
    const pngDir = mk(path.join(out, 'logos', slug, 'PNG'));
    for (const f of fs.readdirSync(src).filter(f => f.endsWith('.svg'))) {
      const svg = fs.readFileSync(path.join(src, f), 'utf8');
      const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
      const ratio = vb[3] / vb[2];
      const base = f.replace(/\.svg$/, '');
      // vector PDF, 200 mm wide (dark versions get a dark page so they are visible)
      const dark = /-dark/.test(f);
      const bg = dark ? ({ 'A-codex': '#3B2A1E', 'B-model': '#0E1621', 'C-monolith': '#141312' })[slug] : 'transparent';
      const wmm = 200, hmm = +(wmm * ratio).toFixed(2);
      await lp.setContent(`<html><head><style>@page{size:${wmm}mm ${hmm}mm;margin:0}html,body{margin:0;background:${bg}}
        svg{display:block;width:${wmm}mm;height:${hmm}mm}</style></head><body>${svg}</body></html>`);
      await lp.pdf({ path: path.join(pdfDir, `${base}.pdf`), width: `${wmm}mm`, height: `${hmm}mm`, printBackground: true, pageRanges: '1' });
      // transparent PNGs
      for (const w of [512, 1024, 2048]) {
        const h = Math.round(w * ratio);
        await lp.setViewportSize({ width: w, height: h });
        await lp.setContent(`<html><head><style>html,body{margin:0;background:transparent}svg{display:block;width:${w}px;height:${h}px}</style></head><body>${svg}</body></html>`);
        await lp.screenshot({ path: path.join(pngDir, `${base}-${w}.png`), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
      }
    }
    // favicons / app icons from the small-size master, on brand ground
    const fav = mk(path.join(out, 'logos', slug, 'favicon'));
    const smallSvg = fs.readFileSync(path.join(src, fs.readdirSync(src).find(f => /symbol-small-light/.test(f))), 'utf8');
    for (const s of [16, 32, 48, 64, 180, 512]) {
      await lp.setViewportSize({ width: s, height: s });
      await lp.setContent(`<html><head><style>html,body{margin:0;background:transparent}
        div{width:${s}px;height:${s}px;display:grid;place-items:center}svg{width:${s}px;height:${s}px}</style></head>
        <body><div>${smallSvg}</div></body></html>`);
      await lp.screenshot({ path: path.join(fav, `favicon-${s}.png`), omitBackground: true, clip: { x: 0, y: 0, width: s, height: s } });
    }
  }
  await lp.close();
  await browser.close();
  console.log('exported to', out);
})();
