// node render.mjs preview <outdir> t1 t2 ...   |   node render.mjs frames <outdir> [fps] [workers]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), url = require('url');
(async () => {
const [mode, out, ...rest] = process.argv.slice(2);
const here = __dirname;
const page_url = url.pathToFileURL(path.join(here, 'index.html')).href + '?capture=1';
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-gpu-vsync'] });
async function newPage() {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(page_url); await p.evaluate(() => window.__ready);
  if (errs.length) console.error('PAGE ERRORS:', errs);
  return p;
}
if (mode === 'preview') {
  const p = await newPage();
  for (const t of rest.map(Number)) {
    await p.evaluate(t => window.__render(t), t);
    await p.screenshot({ path: path.join(out, `t${t.toFixed(2)}.png`) });
  }
} else {
  const fps = Number(rest[0] || 30), W = Number(rest[1] || 4);
  const dur = await (await newPage()).evaluate(() => window.__DUR);
  const N = Math.round(dur * fps);
  const t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: W }, async (_, w) => {
    const p = await newPage();
    for (let i = w; i < N; i += W) {
      await p.evaluate(t => window.__render(t), i / fps);
      await p.screenshot({ path: path.join(out, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93 });
      if (++done % 200 === 0) console.log(`${done}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
  }));
  console.log('frames', N);
}
await browser.close();
})();
