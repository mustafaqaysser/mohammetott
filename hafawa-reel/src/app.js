/* «نسافر قبلك» — Instagram Reel, 1080x1920, 80 s, deterministic render(t). */
(() => {
'use strict';
const W = 1080, H = 1920, TM = window.TIMING || null, DUR = TM ? TM.D : 80;
const AN = TM ? TM.anchors : [[0, 0], [80, 80]];
const warp = T => { for (let i = 1; i < AN.length; i++) if (T <= AN[i][1]) { const [v0, o0] = AN[i - 1], [v1, o1] = AN[i]; return v0 + (v1 - v0) * (T - o0) / (o1 - o0); } return 80; };
const NS = 'http://www.w3.org/2000/svg';
const CAPTURE = /capture=1/.test(location.search);

/* ---------- math ---------- */
const clamp = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, t) => a + (b - a) * t;
function bez(p1x, p1y, p2x, p2y) {
  const cx = 3 * p1x, bx = 3 * (p2x - p1x) - cx, ax = 1 - cx - bx;
  const cy = 3 * p1y, by = 3 * (p2y - p1y) - cy, ay = 1 - cy - by;
  const sx = t => ((ax * t + bx) * t + cx) * t, sy = t => ((ay * t + by) * t + cy) * t;
  const dsx = t => (3 * ax * t + 2 * bx) * t + cx;
  return x => {
    if (x <= 0) return 0; if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 10; i++) { const d = sx(t) - x, dd = dsx(t); if (Math.abs(d) < 1e-6 || Math.abs(dd) < 1e-6) break; t -= d / dd; }
    return sy(clamp(t));
  };
}
const E = {
  out: bez(.16, 1, .3, 1), back: bez(.34, 1.56, .64, 1), inOut: bez(.65, 0, .35, 1),
  in: bez(.7, 0, .84, 0), soft: bez(.4, 0, .2, 1), lin: x => x,
};
const P = (t, a, d, e = E.out) => d <= 0 ? (t >= a ? 1 : 0) : e(clamp((t - a) / d));
const win = (t, a, b, fi = .4, fo = .35) => {
  if (t < a || t >= b) return 0;
  const i = fi <= 0 ? 1 : E.out(clamp((t - a) / fi));
  const o = fo <= 0 ? 1 : 1 - E.soft(clamp((t - (b - fo)) / fo));
  return Math.min(i, o);
};
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const nz = (x, seed = 0) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i + seed * 97.3), hash(i + 1 + seed * 97.3), u) * 2 - 1; };
const AR = n => String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);

/* ---------- dom ---------- */
function S(tag, attrs, parent) { const e = document.createElementNS(NS, tag); if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function D(cls, parent, html) { const e = document.createElement('div'); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
const st = (e, o) => { for (const k in o) e.style[k] = o[k]; };
const fullSvg = parent => S('svg', { class: 'full', viewBox: `0 0 ${W} ${H}`, width: W, height: H }, parent);

const stage = document.getElementById('stage');
const shakeEl = document.getElementById('shake');

/* ---------- shared defs ---------- */
const defsSvg = S('svg', { width: 0, height: 0, style: 'position:absolute' }, document.body);
defsSvg.innerHTML = `<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fde7a8"/><stop offset=".35" stop-color="#e3b04f"/><stop offset=".72" stop-color="#a8741f"/><stop offset="1" stop-color="#5e3c10"/></linearGradient>
  <linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#7a5418"/><stop offset=".3" stop-color="#e9bd62"/><stop offset=".5" stop-color="#fff0c4"/><stop offset=".7" stop-color="#d7a346"/><stop offset="1" stop-color="#6b4512"/></linearGradient>
  <linearGradient id="goldText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffefc2"/><stop offset=".55" stop-color="#e3b04f"/><stop offset="1" stop-color="#a06a1c"/></linearGradient>
  <linearGradient id="stream" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f1d27e"/><stop offset="1" stop-color="#b8892f"/></linearGradient>
  <linearGradient id="porc" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#bdb29c"/><stop offset=".32" stop-color="#f7f0e0"/><stop offset=".5" stop-color="#fffaf0"/><stop offset=".78" stop-color="#e2d8c4"/><stop offset="1" stop-color="#a99d86"/></linearGradient>
  <radialGradient id="coffee" cx=".45" cy=".4" r=".7">
    <stop offset="0" stop-color="#f6dc92"/><stop offset=".6" stop-color="#d1a449"/><stop offset="1" stop-color="#8f6420"/></radialGradient>
  <radialGradient id="bloomGold" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#f3c66b" stop-opacity=".55"/><stop offset=".45" stop-color="#c98a2c" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
  <radialGradient id="bloomCold" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#9fb8e0" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
  <radialGradient id="brass" cx=".5" cy=".35" r=".7">
    <stop offset="0" stop-color="#f0c56a"/><stop offset=".7" stop-color="#9b6a22"/><stop offset="1" stop-color="#4a300c"/></radialGradient>
  <filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="b8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>`;

/* ---------- reusable art ---------- */
function makeDallah(parent) {
  const g = S('g', null, parent);
  // spout (left)
  S('path', { d: 'M -108 -92 C -168 -108 -204 -170 -224 -240 C -234 -276 -250 -300 -272 -320 C -240 -312 -214 -287 -204 -256 C -189 -206 -160 -156 -104 -142 Z', fill: 'url(#gold)' }, g);
  // handle (right)
  S('path', { d: 'M 58 -258 C 150 -272 178 -200 152 -128 C 138 -90 122 -62 104 -44', fill: 'none', stroke: '#8a5d1a', 'stroke-width': 17, 'stroke-linecap': 'round' }, g);
  S('path', { d: 'M 58 -258 C 150 -272 178 -200 152 -128', fill: 'none', stroke: '#f2cf7e', 'stroke-width': 4, 'stroke-linecap': 'round', opacity: .55 }, g);
  // body
  S('path', { d: 'M -72 0 C -112 -10 -137 -60 -122 -110 C -107 -160 -56 -190 -46 -230 C -41 -256 -61 -276 -76 -292 L 76 -292 C 61 -276 41 -256 46 -230 C 56 -190 107 -160 122 -110 C 137 -60 112 -10 72 0 Z', fill: 'url(#goldH)' }, g);
  // belly highlight
  S('path', { d: 'M -88 -40 C -112 -80 -104 -128 -72 -160', fill: 'none', stroke: '#fff6d6', 'stroke-width': 9, 'stroke-linecap': 'round', opacity: .55, filter: 'url(#b3)' }, g);
  // bands
  S('path', { d: 'M -47 -228 Q 0 -218 47 -228', fill: 'none', stroke: '#6b4512', 'stroke-width': 4 }, g);
  S('path', { d: 'M -118 -96 Q 0 -70 118 -96', fill: 'none', stroke: '#6b4512', 'stroke-width': 3, opacity: .7 }, g);
  S('path', { d: 'M -110 -86 Q 0 -60 110 -86', fill: 'none', stroke: '#ffe9b0', 'stroke-width': 2, opacity: .5 }, g);
  // lid
  S('rect', { x: -80, y: -304, width: 160, height: 14, rx: 7, fill: '#9c6b21' }, g);
  S('path', { d: 'M -74 -300 C -68 -334 -30 -354 0 -358 C 30 -354 68 -334 74 -300 Z', fill: 'url(#goldH)' }, g);
  S('path', { d: 'M -11 -354 C -6 -380 -3 -396 0 -424 C 3 -396 6 -380 11 -354 Z', fill: '#c8902e' }, g);
  S('circle', { cx: 0, cy: -372, r: 10, fill: 'url(#gold)' }, g);
  // foot
  S('ellipse', { cx: 0, cy: 0, rx: 80, ry: 12, fill: '#7b5317' }, g);
  S('rect', { x: -76, y: -12, width: 152, height: 10, rx: 5, fill: '#b4822c' }, g);
  return g;
}
function makeCup(parent) {
  const g = S('g', null, parent);
  S('ellipse', { cx: 0, cy: 0, rx: 125, ry: 26, fill: '#d6ccb7' }, g);
  const coffee = S('ellipse', { cx: 0, cy: 5, rx: 112, ry: 20, fill: 'url(#coffee)' }, g);
  S('path', { d: 'M -125 0 C -120 80 -85 150 -70 158 Q 0 172 70 158 C 85 150 120 80 125 0 A 125 26 0 0 1 -125 0 Z', fill: 'url(#porc)' }, g);
  S('path', { d: 'M -122 30 C -60 60 60 60 122 30', fill: 'none', stroke: 'url(#goldH)', 'stroke-width': 7 }, g);
  for (let i = -4; i <= 4; i++) {
    const x = i * 22, y = 72 + Math.abs(i) * -1.5 + (16 - i * i) * .6;
    S('path', { d: `M ${x} ${y - 9} L ${x + 7} ${y} L ${x} ${y + 9} L ${x - 7} ${y} Z`, fill: '#c8902e', opacity: .85 }, g);
  }
  S('path', { d: 'M -100 150 Q 0 166 100 150', fill: 'none', stroke: 'url(#goldH)', 'stroke-width': 4, opacity: .8 }, g);
  S('ellipse', { cx: 0, cy: 0, rx: 125, ry: 26, fill: 'none', stroke: '#fffaf0', 'stroke-width': 3.5, opacity: .9 }, g);
  S('path', { d: 'M -104 22 C -98 74 -78 122 -62 140', fill: 'none', stroke: '#fff', 'stroke-width': 8, opacity: .45, filter: 'url(#b3)', 'stroke-linecap': 'round' }, g);
  return { g, coffee };
}
function makePerson(parent, o = {}) {
  const g = S('g', null, parent);
  const fill = o.fill || '#111824', rim = o.rim || null;
  const body = 'M -96 -362 Q -100 -384 -60 -388 L 60 -388 Q 100 -384 96 -362 L 112 -120 Q 112 -110 100 -110 L -100 -110 Q -112 -110 -112 -120 Z';
  S('rect', { x: -72, y: -122, width: 58, height: 124, rx: 14, fill }, g);
  S('rect', { x: 14, y: -122, width: 58, height: 124, rx: 14, fill }, g);
  S('path', { d: body, fill }, g);
  S('rect', { x: -20, y: -418, width: 40, height: 40, rx: 10, fill }, g);
  S('circle', { cx: 0, cy: -448, r: 44, fill }, g);
  if (rim) {
    S('path', { d: 'M 96 -362 L 112 -120', stroke: rim, 'stroke-width': 3, opacity: .6, fill: 'none' }, g);
    S('path', { d: 'M 30 -486 A 44 44 0 0 1 44 -440', stroke: rim, 'stroke-width': 3, opacity: .6, fill: 'none' }, g);
  }
  if (o.sign) {
    const sg = S('g', { transform: `translate(0 -300) rotate(${o.rot || 0})` }, g);
    S('rect', { x: -122, y: -70, width: 244, height: 140, rx: 8, fill: o.signFill || '#f2f0ea' }, sg);
    const tx = S('text', { x: 0, y: 14, 'text-anchor': 'middle', 'font-family': 'Permanent Marker', 'font-size': o.fs || 38, fill: '#15151a' }, sg);
    tx.textContent = o.sign;
    S('path', { d: 'M -92 -350 L -128 -250 L -112 -236', stroke: fill, 'stroke-width': 30, 'stroke-linecap': 'round', fill: 'none' }, g);
    S('path', { d: 'M 92 -350 L 128 -250 L 112 -236', stroke: fill, 'stroke-width': 30, 'stroke-linecap': 'round', fill: 'none' }, g);
  }
  return g;
}

/* ---------- map ---------- */
const MAP = window.MAP;
const proj = (lon, lat) => [(lon - MAP.lon0) * MAP.kx, (MAP.lat0 - lat) * MAP.ky];
function makeMap(parent, color, top) {
  const wrap = D('layer', parent);
  st(wrap, { top: top + 'px', height: MAP.H + 'px', bottom: 'auto', transformOrigin: '50% 50%' });
  const cv = document.createElement('canvas'); cv.width = W; cv.height = MAP.H; wrap.appendChild(cv);
  st(cv, { position: 'absolute', left: 0, top: 0 });
  const c = cv.getContext('2d'); c.fillStyle = color;
  for (const [x, y] of MAP.dots) { c.beginPath(); c.arc(x, y, 2.7, 0, Math.PI * 2); c.fill(); }
  const svg = S('svg', { width: W, height: MAP.H, viewBox: `0 0 ${W} ${MAP.H}`, style: 'position:absolute;left:0;top:0;overflow:visible' }, wrap);
  return { wrap, cv, svg };
}
function arcPath(a, b, lift = .32) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
  const len = Math.hypot(dx, dy), nx = -dy / len, ny = dx / len;
  const s = ny > 0 ? -1 : 1;
  return `M ${a[0]} ${a[1]} Q ${mx + nx * len * lift * s} ${my + ny * len * lift * s} ${b[0]} ${b[1]}`;
}
function makePin(parent, color = '#e2483d') {
  const g = S('g', null, parent);
  S('ellipse', { cx: 0, cy: 2, rx: 14, ry: 5, fill: '#000', opacity: .45 }, g);
  const head = S('g', null, g);
  S('path', { d: 'M 0 0 C -6 -14 -22 -28 -22 -46 A 22 22 0 1 1 22 -46 C 22 -28 6 -14 0 0 Z', fill: color }, head);
  S('circle', { cx: 0, cy: -46, r: 8, fill: '#fff', opacity: .9 }, head);
  return { g, head };
}

/* ---------- scenes ---------- */
const scenes = [];
function scene(a, b, build, draw, env) {
  const root = D('scene', shakeEl);
  const sc = { a, b, root, env: env || ((t) => win(t, a, b, .35, .35)) };
  Object.assign(sc, build(root) || {});
  sc.draw = draw;
  scenes.push(sc);
  return sc;
}

/* S1/S10 — coffee (pour clock c) */
function buildCoffee(root, withNumber) {
  const bg = D('layer', root);
  st(bg, { background: 'radial-gradient(ellipse 90% 60% at 50% 52%, #3b250c 0%, #160d05 55%, #070402 100%)' });
  const svg = fullSvg(root);
  const bloom = S('circle', { cx: 540, cy: 920, r: 620, fill: 'url(#bloomGold)' }, svg);
  let num = null;
  if (withNumber) {
    num = S('text', { x: 540, y: 700, 'text-anchor': 'middle', 'font-family': 'Amiri', 'font-weight': 700, 'font-size': 640, fill: 'none', stroke: 'url(#goldText)', 'stroke-width': 3, direction: 'rtl', opacity: 0 }, svg);
    num.textContent = '٢١';
  }
  // table + reflection
  S('ellipse', { cx: 540, cy: 1132, rx: 330, ry: 40, fill: '#000', opacity: .55, filter: 'url(#b20)' }, svg);
  S('rect', { x: 0, y: 1128, width: W, height: 2, fill: '#e3b04f', opacity: .18 }, svg);
  const dallahWrap = S('g', null, svg);
  const dallah = makeDallah(dallahWrap);
  const stream = S('path', { d: 'M 547 684 C 548 760 541 860 540 955', fill: 'none', stroke: 'url(#stream)', 'stroke-width': 10, 'stroke-linecap': 'round' }, svg);
  const shine = S('path', { d: 'M 545 690 C 546 760 540 860 539 950', fill: 'none', stroke: '#fff8e0', 'stroke-width': 2.5, 'stroke-dasharray': '18 34', opacity: .55 }, svg);
  const cupG = S('g', { transform: 'translate(540 950)' }, svg);
  const cup = makeCup(cupG);
  const ripples = [0, 1, 2].map(() => S('ellipse', { cx: 0, cy: 6, rx: 10, ry: 3, fill: 'none', stroke: '#fff3c8', 'stroke-width': 2 }, cupG));
  const steam = [[-62, 0], [64, 1.3], [-10, 2.6]].map(([x, ph]) => {
    const p = S('path', { d: 'M 0 0 C -24 -60 24 -110 0 -170 C -24 -230 22 -280 0 -340', fill: 'none', stroke: '#fff', 'stroke-width': 16, 'stroke-linecap': 'round', opacity: 0, filter: 'url(#b8)' }, cupG);
    return { p, x, ph };
  });
  return { bloom, num, dallah, dallahWrap, stream, shine, cup, ripples, steam, svg };
}
function drawCoffee(s, c, tNum) {
  // c: continuous pour clock; loops at c=0
  const breathe = Math.sin(c * 1.1) * .5 + .5;
  s.bloom.setAttribute('r', 600 + breathe * 40);
  s.bloom.setAttribute('opacity', .85 + breathe * .15);
  const tilt = -42 + Math.sin(c * .9) * 1.2;
  s.dallahWrap.setAttribute('transform', `translate(${960 + Math.sin(c * .7) * 3} ${740 + Math.cos(c * .9) * 2}) rotate(${tilt})`);
  const wob = Math.sin(c * 7) * 1.4;
  s.stream.setAttribute('d', `M 547 684 C ${548 + wob} 760 ${541 - wob} 860 540 955`);
  s.shine.setAttribute('stroke-dashoffset', -c * 260);
  s.ripples.forEach((r, i) => {
    const ph = ((c * .9 + i / 3) % 1 + 1) % 1;
    r.setAttribute('rx', 8 + ph * 104); r.setAttribute('ry', 2 + ph * 18); r.setAttribute('opacity', (1 - ph) * .55);
  });
  s.steam.forEach(({ p, x, ph }) => {
    const k = (((c * .38 + ph / 3) % 1) + 1) % 1;
    p.setAttribute('transform', `translate(${x + Math.sin(c * 1.3 + ph) * 10} ${-20 - k * 120}) scale(${.8 + k * .5} ${.7 + k * .4})`);
    p.setAttribute('opacity', Math.sin(k * Math.PI) * .2);
  });
  if (s.num) {
    const o = tNum == null ? 0 : P(tNum, 1.35, 1.2, E.out);
    s.num.setAttribute('opacity', o * .32);
    s.num.setAttribute('transform', `translate(540 700) scale(${1.08 - o * .08}) translate(-540 -700)`);
    s.num.setAttribute('stroke-dasharray', '4000');
    s.num.setAttribute('stroke-dashoffset', 4000 * (1 - o));
  }
}
const S1 = scene(0, 3.2, r => buildCoffee(r, true), (t, s) => {
  drawCoffee(s, t, t);
  s.root.style.transform = `scale(${1 + t * .006})`;
}, t => (t >= 0 && t < 3.2) ? 1 : 0);

/* S2 — arrivals, nobody waiting */
const NAMES = ['MR. HANSEN', 'A. KOVAC', 'DR. LIN', 'HOTEL RIVA', 'M. DUBOIS', 'J. PEREIRA', 'SATO', 'K. WEBER', 'MS. ROSSI', 'T. MÜLLER', 'P. NOVAK', 'L. GARCIA'];
function buildHall(root, warm) {
  const bg = D('layer', root);
  st(bg, { background: warm ? 'linear-gradient(#24170b 0%, #120b05 45%, #0a0603 100%)' : 'linear-gradient(#0d1626 0%, #070c16 48%, #04060b 100%)' });
  const svg = fullSvg(root);
  const lc = warm ? '#ffd38a' : '#bcd3ff';
  const lights = [];
  [[110, 900, 14], [220, 760, 12], [310, 640, 10], [380, 540, 8], [432, 460, 6]].forEach(([y, w, h]) => {
    lights.push(S('rect', { x: 540 - w / 2, y, width: w, height: h, rx: h / 2, fill: lc, opacity: .55, filter: 'url(#b3)' }, svg));
  });
  S('rect', { x: 0, y: 1250, width: W, height: 670, fill: warm ? '#0e0905' : '#060a12' }, svg);
  S('rect', { x: 0, y: 1250, width: W, height: 3, fill: lc, opacity: .15 }, svg);
  const back = S('g', { opacity: .22, filter: 'url(#b3)' }, svg);
  const front = S('g', null, svg);
  const backRow = [], frontRow = [];
  for (let i = 0; i < 12; i++) {
    const g = S('g', null, back);
    makePerson(g, { fill: warm ? '#1b130b' : '#141c2b', sign: NAMES[(i + 5) % 12], rot: (hash(i) - .5) * 8, fs: 34 });
    backRow.push(g);
  }
  for (let i = 0; i < 9; i++) {
    const g = S('g', null, front);
    makePerson(g, { fill: warm ? '#160f08' : '#0f1520', sign: NAMES[i], rot: (hash(i + 20) - .5) * 9, rim: lc });
    frontRow.push(g);
  }
  return { svg, back, front, backRow, frontRow, lights };
}
function drawHall(s, k) {
  s.backRow.forEach((g, i) => g.setAttribute('transform', `translate(${i * 200 - 260 - k * 150} 1090) scale(.62)`));
  s.frontRow.forEach((g, i) => g.setAttribute('transform', `translate(${i * 300 - 220 - k * 380} 1270) scale(.88)`));
  s.lights.forEach((l, i) => l.setAttribute('opacity', .45 + Math.sin(k * 6 + i) * .05));
}
const S2 = scene(3.2, 10.2, root => {
  const h = buildHall(root, false);
  const trav = S('g', null, h.svg);
  const p = makePerson(trav, { fill: '#03050a', rim: '#9fb8e0' });
  const suit = S('g', null, trav);
  S('rect', { x: 140, y: -230, width: 130, height: 200, rx: 18, fill: '#0b1220', stroke: '#9fb8e0', 'stroke-opacity': .35, 'stroke-width': 2 }, suit);
  S('path', { d: 'M 180 -230 V -330 H 230 V -230', fill: 'none', stroke: '#0b1220', 'stroke-width': 10 }, suit);
  S('circle', { cx: 160, cy: -22, r: 12, fill: '#05080e' }, suit); S('circle', { cx: 250, cy: -22, r: 12, fill: '#05080e' }, suit);
  const bat = S('g', { opacity: 0 }, h.svg);
  S('rect', { x: -95, y: -40, width: 170, height: 80, rx: 16, fill: 'none', stroke: '#f4ead7', 'stroke-width': 6 }, bat);
  S('rect', { x: 80, y: -16, width: 14, height: 32, rx: 4, fill: '#f4ead7' }, bat);
  const lvl = S('rect', { x: -84, y: -29, width: 10, height: 58, rx: 6, fill: '#ff3b30' }, bat);
  const bt = S('text', { x: -10, y: 120, 'text-anchor': 'middle', 'font-family': 'Cairo', 'font-weight': 900, 'font-size': 64, fill: '#ff3b30' }, bat);
  bt.textContent = '3%';
  const cold = S('circle', { cx: 540, cy: 900, r: 700, fill: 'url(#bloomCold)' }, h.svg);
  h.svg.insertBefore(cold, h.svg.firstChild);
  return { ...h, trav, bat, lvl };
}, (t, s) => {
  const lt = t - 3.2, k = lt / 7;
  drawHall(s, k);
  const walk = clamp(lt / 4.5);
  const bob = walk < 1 ? Math.abs(Math.sin(lt * 5.2)) * 8 : 0;
  s.trav.setAttribute('transform', `translate(${470 + Math.sin(lt * .4) * 6} ${1790 - bob}) scale(${1.62 + walk * .1})`);
  const bo = P(t, 7.9, .45, E.back);
  const blink = t > 8.6 ? (Math.sin((t - 8.6) * 9) > -.2 ? 1 : .25) : 1;
  s.bat.setAttribute('opacity', bo * blink);
  s.bat.setAttribute('transform', `translate(540 360) scale(${.7 + bo * .3})`);
  s.root.style.transform = `scale(${1.04 - k * .04})`;
}, t => win(t, 3.2, 10.2, 0, .35));

/* S3 — map journey + the problem (10.2 – 22.0) */
const HOME = proj(45, 24);
const S3 = scene(10.2, 22.0, root => {
  const bg = D('layer', root);
  st(bg, { background: 'radial-gradient(ellipse 100% 70% at 50% 45%, #2a1a0c 0%, #0f0904 70%, #070402 100%)' });
  const cold = D('layer', root); st(cold, { background: 'linear-gradient(#0b1424, #04070d)', opacity: 0 });
  const m = makeMap(root, '#cdb487', 486);
  const pin = makePin(m.svg);
  const arcs = [['shanghai', 12.7, 'شنغهاي', 1, -40], ['marbella', 13.9, 'ماربيا', -1, -40]].map(([city, at, name, side, dy]) => {
    const to = MAP.cities[city];
    const d = arcPath(HOME, to, .28);
    const glowP = S('path', { d, fill: 'none', stroke: '#e3b04f', 'stroke-width': 9, opacity: .35, filter: 'url(#b8)' }, m.svg);
    const p = S('path', { d, fill: 'none', stroke: '#f6d48a', 'stroke-width': 3.5, 'stroke-linecap': 'round' }, m.svg);
    const dot = S('circle', { r: 9, fill: '#fff3cf', filter: 'url(#glow)' }, m.svg);
    const ring = S('circle', { cx: to[0], cy: to[1], r: 10, fill: 'none', stroke: '#f6d48a', 'stroke-width': 3 }, m.svg);
    const cdot = S('circle', { cx: to[0], cy: to[1], r: 9, fill: '#f6d48a' }, m.svg);
    const lab = D('label', m.wrap, name);
    st(lab, { top: (to[1] + dy - 30) + 'px', fontSize: '50px' });
    if (side > 0) st(lab, { right: (W - to[0] + 6) + 'px' }); else st(lab, { left: (to[0] - 30) + 'px' });
    return { p, glowP, dot, ring, cdot, lab, at, len: p.getTotalLength() };
  });
  // problem layer
  const prob = D('layer', root);
  const ps = fullSvg(prob);
  const tabs = [];
  for (let i = 0; i < 17; i++) {
    const g = S('g', { opacity: 0 }, ps);
    S('path', { d: 'M 0 60 L 14 8 Q 16 0 26 0 L 214 0 Q 224 0 226 8 L 240 60 Z', fill: '#1a2436', stroke: '#7f9cc4', 'stroke-opacity': .35 }, g);
    S('circle', { cx: 40, cy: 30, r: 9, fill: '#7f9cc4', opacity: .7 }, g);
    S('rect', { x: 60, y: 24, width: 120 - (i % 4) * 18, height: 12, rx: 6, fill: '#7f9cc4', opacity: .5 }, g);
    tabs.push({ g, x: 40 + hash(i * 3.1) * 780, y: 300 + hash(i * 7.7) * 1050, a: 17.3 + i * .14, r: (hash(i) - .5) * 14 });
  }
  const prices = ['€480', 'SAR 1,950', '$315', '€129', 'SAR 2,400', '€689'].map((txt, i) => {
    const g = S('g', { opacity: 0 }, ps);
    S('rect', { x: -110, y: -38, width: 220, height: 76, rx: 38, fill: '#c0392b' }, g);
    const tx = S('text', { x: 0, y: 16, 'text-anchor': 'middle', 'font-family': 'Cairo', 'font-weight': 800, 'font-size': 40, fill: '#fff' }, g);
    tx.textContent = txt;
    return { g, x: 160 + hash(i * 5.3) * 760, y: 420 + hash(i * 9.1) * 900, a: 17.6 + i * .32 };
  });
  const clock = S('g', { opacity: 0 }, ps);
  S('circle', { r: 128, fill: 'rgba(10,16,28,.75)', stroke: '#e8eef8', 'stroke-width': 6 }, clock);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; S('line', { x1: Math.sin(a) * 104, y1: -Math.cos(a) * 104, x2: Math.sin(a) * 118, y2: -Math.cos(a) * 118, stroke: '#e8eef8', 'stroke-width': i % 3 ? 3 : 7 }, clock); }
  const hh = S('line', { x1: 0, y1: 0, x2: 0, y2: -62, stroke: '#e8eef8', 'stroke-width': 10, 'stroke-linecap': 'round' }, clock);
  const mh = S('line', { x1: 0, y1: 0, x2: 0, y2: -96, stroke: '#e8eef8', 'stroke-width': 6, 'stroke-linecap': 'round' }, clock);
  const sh = S('line', { x1: 0, y1: 18, x2: 0, y2: -108, stroke: '#ff5a4e', 'stroke-width': 3, 'stroke-linecap': 'round' }, clock);
  S('circle', { r: 9, fill: '#ff5a4e' }, clock);
  const words = [['فنادق؟', 17.4, 790], ['أسعار؟', 18.2, 960], ['مواصلات؟', 19.0, 1130]].map(([w, a, y]) => {
    const e = D('', prob, w);
    st(e, { position: 'absolute', left: 0, right: 0, top: y + 'px', textAlign: 'center', font: "900 150px/1 'Cairo'", color: '#fff', direction: 'rtl', transform: 'translateY(-50%)', opacity: 0 });
    return { e, a };
  });
  return { cold, m, pin, arcs, prob, tabs, prices, clock, hh, mh, sh, words };
}, (t, s) => {
  // journey (10.2–15.6)
  const lt = t - 10.2;
  const reveal = P(t, 10.25, 2.2, E.out);
  const r = 40 + reveal * 1400;
  const mask = `radial-gradient(circle at ${HOME[0]}px ${HOME[1]}px, #000 ${r}px, transparent ${r + 260}px)`;
  s.m.cv.style.webkitMaskImage = mask; s.m.cv.style.maskImage = mask;
  const pd = P(t, 10.6, .7, E.back);
  s.pin.g.setAttribute('transform', `translate(${HOME[0]} ${HOME[1]})`);
  s.pin.head.setAttribute('transform', `translate(0 ${-(1 - pd) * 260}) scale(${pd ? 1 : 0})`);
  s.pin.g.setAttribute('opacity', t > 10.6 ? 1 : 0);
  s.arcs.forEach(a => {
    const k = P(t, a.at, 1.0, E.inOut);
    a.p.setAttribute('stroke-dasharray', a.len); a.p.setAttribute('stroke-dashoffset', a.len * (1 - k));
    a.glowP.setAttribute('stroke-dasharray', a.len); a.glowP.setAttribute('stroke-dashoffset', a.len * (1 - k));
    const pt = a.p.getPointAtLength(a.len * k);
    a.dot.setAttribute('cx', pt.x); a.dot.setAttribute('cy', pt.y); a.dot.setAttribute('opacity', k > 0 && k < 1 ? 1 : 0);
    const arr = P(t, a.at + .95, .5, E.back);
    a.cdot.setAttribute('r', 9 * arr);
    const rp = ((t - a.at - .95) % 1.6) / 1.6;
    a.ring.setAttribute('r', 10 + rp * 34); a.ring.setAttribute('opacity', t > a.at + .95 ? (1 - rp) * .8 : 0);
    st(a.lab, { opacity: P(t, a.at + .9, .5), transform: `translateY(${(1 - P(t, a.at + .9, .5)) * 20}px)` });
  });
  // problem (15.6–22)
  const pk = P(t, 15.6, 1.0, E.inOut);
  s.cold.style.opacity = pk;
  st(s.m.wrap, { filter: `blur(${pk * 7}px) saturate(${1 - pk * .8})`, opacity: 1 - pk * .55, transform: `scale(${1 + lt * .006 + pk * .12})` });
  const co = P(t, 15.9, .6, E.back);
  s.clock.setAttribute('opacity', co);
  s.clock.setAttribute('transform', `translate(540 420) scale(${.6 + co * .4})`);
  const ct = Math.max(0, t - 15.6);
  s.hh.setAttribute('transform', `rotate(${67 + ct * 10})`);
  s.mh.setAttribute('transform', `rotate(${84 + ct * ct * 26})`);
  const ticks = Math.floor(ct * (1 + ct * .55) * 2);
  s.sh.setAttribute('transform', `rotate(${ticks * 6})`);
  const glitch = t > 19.8 && t < 21.8;
  s.tabs.forEach(o => {
    const k = P(t, o.a, .45, E.back);
    const fl = glitch && hash(Math.floor(t * 20) + o.x) > .7 ? .2 : 1;
    o.g.setAttribute('opacity', k * .75 * fl * (t > 21.7 ? 0 : 1));
    o.g.setAttribute('transform', `translate(${o.x + nz(t * .7, o.x) * 14} ${o.y - (t - o.a) * 10}) rotate(${o.r}) scale(${.6 + k * .4})`);
  });
  s.prices.forEach(o => {
    const k = P(t, o.a, .35, E.back);
    const fl = hash(Math.floor(t * 12) + o.x) > .82 ? .35 : 1;
    o.g.setAttribute('opacity', k * fl * (t > 21.7 ? 0 : 1));
    o.g.setAttribute('transform', `translate(${o.x} ${o.y}) scale(${.5 + k * .5}) rotate(${(hash(o.y) - .5) * 16})`);
  });
  s.words.forEach(w => {
    const k = P(t, w.a, .38, E.out);
    let tx = 0, sh = '0 10px 40px rgba(0,0,0,.6)';
    if (glitch) { const g = nz(t * 30, w.a) * 14; tx = g; sh = `${-g * .8}px 0 rgba(255,40,60,.7), ${g * .8}px 0 rgba(40,200,255,.7)`; }
    const op = k * (t > 21.7 ? 0 : 1) * (glitch && hash(Math.floor(t * 24) + w.a) > .85 ? .3 : 1);
    st(w.e, { opacity: op, transform: `translate(${tx}px,-50%) scale(${1.7 - k * .7})`, filter: `blur(${(1 - k) * 14}px)`, textShadow: sh });
  });
  s.root.style.transform = '';
}, t => win(t, 10.2, 21.75, .45, 0));

/* S4 — the wish (22–28) */
const S4 = scene(22.0, 28.0, root => {
  const bg = D('layer', root); st(bg, { background: 'linear-gradient(#070a12, #030407)' });
  const svg = fullSvg(root);
  const win_ = S('g', null, svg);
  S('rect', { x: 300, y: 150, width: 480, height: 560, rx: 6, fill: '#0b1426' }, win_);
  const bokeh = [];
  for (let i = 0; i < 26; i++) {
    const c = hash(i * 4.4) > .5 ? '#ffcf7a' : '#8fb4ff';
    bokeh.push({ e: S('circle', { r: 8 + hash(i) * 26, fill: c, opacity: .25 + hash(i * 2) * .35, filter: 'url(#b8)' }, win_), x: 320 + hash(i * 1.7) * 440, y: 380 + hash(i * 3.3) * 300, sp: .2 + hash(i * 9) * .6 });
  }
  S('rect', { x: 300, y: 150, width: 480, height: 560, rx: 6, fill: 'none', stroke: '#1b2233', 'stroke-width': 18 }, win_);
  S('rect', { x: 532, y: 150, width: 16, height: 560, fill: '#1b2233' }, win_);
  S('path', { d: 'M 300 710 L 780 710 L 980 1700 L 100 1700 Z', fill: '#cfe0ff', opacity: .05, filter: 'url(#b20)' }, svg);
  const motes = [];
  for (let i = 0; i < 40; i++) motes.push({ e: S('circle', { r: 1.5 + hash(i * 5) * 2.5, fill: '#e8eefc', opacity: 0 }, svg), x: 250 + hash(i * 1.3) * 600, y: 760 + hash(i * 2.9) * 900, ph: hash(i * 7) });
  const room = S('g', null, svg);
  S('rect', { x: 120, y: 1380, width: 760, height: 160, rx: 20, fill: '#0a0d14' }, room);
  S('rect', { x: 120, y: 1360, width: 760, height: 40, rx: 14, fill: '#121827' }, room);
  const man = S('g', { transform: 'translate(470 1380)' }, room);
  S('path', { d: 'M -70 0 C -80 -120 -60 -230 -10 -270 C 30 -290 70 -270 80 -220 C 92 -150 90 -60 80 0 Z', fill: '#05070c', stroke: '#8fa6d0', 'stroke-opacity': .35, 'stroke-width': 2 }, man);
  S('circle', { cx: 30, cy: -310, r: 46, fill: '#05070c', stroke: '#8fa6d0', 'stroke-opacity': .35, 'stroke-width': 2 }, man);
  S('path', { d: 'M -60 -10 L -150 20 L -160 150 L -120 150 L -110 60 L 40 40 Z', fill: '#05070c' }, man);
  const suit = S('g', { transform: 'translate(760 1500)' }, room);
  S('rect', { x: -70, y: -220, width: 140, height: 220, rx: 18, fill: '#0b101a', stroke: '#8fa6d0', 'stroke-opacity': .3, 'stroke-width': 2 }, suit);
  S('rect', { x: -26, y: -250, width: 52, height: 34, rx: 8, fill: 'none', stroke: '#0b101a', 'stroke-width': 9 }, suit);
  return { bokeh, motes };
}, (t, s) => {
  const lt = t - 22;
  s.bokeh.forEach(b => { b.e.setAttribute('cx', b.x + Math.sin(lt * b.sp + b.y) * 12); b.e.setAttribute('cy', b.y + Math.cos(lt * b.sp) * 6); });
  s.motes.forEach(m => {
    const y = m.y - ((lt * 18 + m.ph * 900) % 900) + 0;
    m.e.setAttribute('cx', m.x + Math.sin(lt * .6 + m.ph * 9) * 20); m.e.setAttribute('cy', y);
    m.e.setAttribute('opacity', (.25 + Math.sin(lt + m.ph * 20) * .2) * clamp(1 - Math.abs(y - 1200) / 600));
  });
  s.root.style.transform = `scale(${1 + lt * .012})`;
}, t => win(t, 22.0, 28.0, .9, .5));

/* S5 — majlis (28–40) */
const S5 = scene(28.0, 40.0, root => {
  const back = D('layer', root);
  st(back, { background: 'radial-gradient(ellipse 120% 80% at 30% 20%, #6a3e14 0%, #2f1a08 45%, #120903 100%)', transformOrigin: '50% 60%' });
  const bsvg = fullSvg(back);
  S('path', { d: 'M -100 -100 L 420 -100 L 1180 1500 L 520 1500 Z', fill: '#ffd08a', opacity: .12, filter: 'url(#b20)' }, bsvg);
  const front = D('layer', root); st(front, { transformOrigin: '50% 60%' });
  const svg = fullSvg(front);
  const motes = [];
  for (let i = 0; i < 46; i++) motes.push({ e: S('circle', { r: 1.5 + hash(i * 3) * 3, fill: '#ffe2a8' }, svg), x: hash(i * 1.9) * 1000 + 40, y: 200 + hash(i * 4.1) * 1300, ph: hash(i * 8) });
  // cushion band
  S('rect', { x: -20, y: 1530, width: 1120, height: 160, rx: 30, fill: '#5a1d14' }, svg);
  for (let i = 0; i < 3; i++) S('rect', { x: -20, y: 1556 + i * 40, width: 1120, height: 6, fill: '#d9a547', opacity: .5 }, svg);
  // mabkhara + smoke
  const mab = S('g', { transform: 'translate(190 1500)' }, svg);
  S('path', { d: 'M -60 0 L 60 0 L 46 -40 L 70 -60 L 70 -110 L -70 -110 L -70 -60 L -46 -40 Z', fill: 'url(#gold)' }, mab);
  S('path', { d: 'M -50 -110 Q 0 -170 50 -110 Z', fill: '#b4822c' }, mab);
  const smoke = [0, 1, 2, 3].map(i => S('path', { d: 'M 0 0 C -40 -120 40 -220 0 -340 C -40 -460 40 -560 0 -700', fill: 'none', stroke: '#fff4dc', 'stroke-width': 22, 'stroke-linecap': 'round', opacity: .1, filter: 'url(#b8)' }, mab));
  // tray
  const tray = S('g', null, svg);
  S('ellipse', { cx: 640, cy: 1470, rx: 300, ry: 56, fill: '#000', opacity: .5, filter: 'url(#b20)' }, tray);
  S('ellipse', { cx: 640, cy: 1455, rx: 290, ry: 52, fill: 'url(#brass)' }, tray);
  S('ellipse', { cx: 640, cy: 1449, rx: 262, ry: 42, fill: 'none', stroke: '#ffe0a0', 'stroke-width': 2, opacity: .45 }, tray);
  const dg = S('g', { transform: 'translate(780 1450) scale(.6)' }, tray); makeDallah(dg);
  const c1 = S('g', { transform: 'translate(520 1400) scale(.42)' }, tray); makeCup(c1);
  const c2 = S('g', { transform: 'translate(620 1420) scale(.42)' }, tray); makeCup(c2);
  // uncle label + quote marks
  const lab = D('', front, 'قريب الوالد');
  st(lab, { position: 'absolute', left: 0, right: 0, top: '470px', textAlign: 'center', font: "700 40px 'Cairo'", color: '#e3b04f', letterSpacing: '0', direction: 'rtl', opacity: 0 });
  const qm = D('', front, '«');
  st(qm, { position: 'absolute', right: '70px', top: '470px', font: "700 220px/1 'Amiri'", color: '#e3b04f', opacity: 0 });
  // realization: spotlight + falling cup
  const dark = D('layer', root); st(dark, { background: 'radial-gradient(circle at 540px 1280px, rgba(0,0,0,0) 0px, rgba(0,0,0,.25) 220px, rgba(0,0,0,.94) 560px)', opacity: 0 });
  const spot = fullSvg(root);
  const sc = S('g', { opacity: 0 }, spot);
  S('ellipse', { cx: 540, cy: 1450, rx: 300, ry: 52, fill: 'url(#brass)' }, sc);
  const scShadow = S('ellipse', { cx: 540, cy: 1452, rx: 90, ry: 14, fill: '#000', opacity: .5, filter: 'url(#b8)' }, sc);
  const cupFall = S('g', null, sc); makeCup(cupFall);
  return { back, front, motes, smoke, lab, qm, dark, sc, cupFall, scShadow };
}, (t, s) => {
  const lt = t - 28;
  s.motes.forEach(m => {
    const y = m.y - ((lt * 14 + m.ph * 1200) % 1200);
    m.e.setAttribute('cx', m.x + Math.sin(lt * .5 + m.ph * 12) * 26); m.e.setAttribute('cy', y + 200);
    m.e.setAttribute('opacity', .35 + Math.sin(lt * 1.3 + m.ph * 30) * .25);
  });
  s.smoke.forEach((p, i) => {
    const k = ((lt * .22 + i / 4) % 1);
    p.setAttribute('transform', `translate(${Math.sin(lt * .8 + i) * 18 + (i - 1.5) * 10} ${-k * 120}) scale(${1 + k * .3})`);
    p.setAttribute('opacity', Math.sin(k * Math.PI) * .14);
  });
  const lo = win(t, 28.3, 35.6, .6, .4);
  s.lab.style.opacity = lo; s.qm.style.opacity = lo * .35;
  // dolly zoom on "على طول"
  const dz = P(t, 33.6, 1.9, E.inOut);
  s.front.style.transform = `scale(${1 + lt * .004 + dz * .16})`;
  s.back.style.transform = `scale(${1.05 - dz * .1})`;
  s.back.style.filter = `blur(${dz * 5}px)`;
  // realization
  const rk = P(t, 35.4, .9, E.inOut);
  s.dark.style.opacity = rk;
  s.front.style.opacity = 1 - rk * .9;
  const ck = P(t, 35.6, .8, E.out);
  s.sc.setAttribute('opacity', ck);
  const fall = P(t, 38.95, .4, E.in);
  const land = t >= 39.35;
  const sq = land ? 1 - Math.exp(-(t - 39.35) * 18) * Math.cos((t - 39.35) * 40) * .08 : 1;
  const y = land ? 1300 : lerp(1180 + Math.sin(t * 1.2) * 6, 1300, fall);
  s.cupFall.setAttribute('transform', `translate(540 ${y}) scale(${.92 * (land ? 2 - sq : 1)} ${.92 * sq})`);
  s.scShadow.setAttribute('rx', 60 + fall * 40); s.scShadow.setAttribute('opacity', .2 + fall * .4);
}, t => win(t, 28.0, 39.5, .6, 0));

/* S6 — founding (40–47) */
const S6 = scene(40.0, 47.0, root => {
  const bg = D('layer', root); st(bg, { background: 'radial-gradient(ellipse 90% 70% at 50% 40%, #2a1c11 0%, #120c07 70%, #070503 100%)' });
  const wrap = D('layer', root); st(wrap, { transformOrigin: '50% 45%' });
  const paper = D('paper', wrap);
  const pg = document.createElement('canvas'); pg.width = 380; pg.height = 430; paper.appendChild(pg);
  st(pg, { position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: .5, mixBlendMode: 'multiply', borderRadius: '6px' });
  const pc = pg.getContext('2d'); const id = pc.createImageData(380, 430);
  for (let i = 0; i < id.data.length; i += 4) { const v = 200 + hash(i * .37) * 55; id.data[i] = v; id.data[i + 1] = v * .97; id.data[i + 2] = v * .9; id.data[i + 3] = 60; }
  pc.putImageData(id, 0, 0);
  const svg = fullSvg(wrap);
  const word = S('text', { x: 540, y: 800, 'text-anchor': 'middle', 'font-family': 'Amiri', 'font-weight': 700, 'font-size': 290, fill: '#1d1712', 'fill-opacity': 0, stroke: '#1d1712', 'stroke-width': 2.2, direction: 'rtl', 'stroke-dasharray': 3200, 'stroke-dashoffset': 3200 }, svg);
  word.textContent = 'حفاوة';
  const rule = S('line', { x1: 300, y1: 905, x2: 780, y2: 905, stroke: '#b98a33', 'stroke-width': 4, 'stroke-dasharray': 480, 'stroke-dashoffset': 480 }, svg);
  const def1 = S('text', { x: 540, y: 990, 'text-anchor': 'middle', 'font-family': 'Amiri', 'font-weight': 700, 'font-size': 50, fill: '#3a2a19', direction: 'rtl', opacity: 0 }, svg);
  def1.textContent = 'حَفَاوَة (اسم)';
  const def2 = S('text', { x: 540, y: 1066, 'text-anchor': 'middle', 'font-family': 'Amiri', 'font-size': 44, fill: '#4a3824', direction: 'rtl', opacity: 0 }, svg);
  def2.textContent = 'المبالغة في الإكرام، والسؤال عن الحال';
  const seal = S('g', { opacity: 0 }, svg);
  S('circle', { cx: 0, cy: 0, r: 70, fill: '#8e2a1e' }, seal);
  S('circle', { cx: 0, cy: 0, r: 58, fill: 'none', stroke: '#e3b04f', 'stroke-width': 2 }, seal);
  const sw = S('text', { x: 0, y: 14, 'text-anchor': 'middle', 'font-family': 'Amiri', 'font-weight': 700, 'font-size': 40, fill: '#f6d48a', direction: 'rtl' }, seal);
  sw.textContent = 'حفاوة';
  const nib = S('circle', { r: 7, fill: '#e3b04f', filter: 'url(#glow)', opacity: 0 }, svg);
  return { wrap, word, rule, def1, def2, seal, nib, paper };
}, (t, s) => {
  const lt = t - 40;
  const pk = P(t, 40.0, .9, E.out);
  s.paper.style.transform = `translateY(${(1 - pk) * 80}px) rotate(${-2.2 + (1 - pk) * 3}deg)`;
  const wk = P(t, 40.4, 2.0, E.inOut);
  s.word.setAttribute('stroke-dashoffset', 3200 * (1 - wk));
  s.word.setAttribute('fill-opacity', P(t, 41.9, .8, E.soft));
  s.nib.setAttribute('opacity', wk > 0 && wk < 1 ? 1 : 0);
  s.nib.setAttribute('cx', 760 - wk * 470 + Math.sin(lt * 23) * 30); s.nib.setAttribute('cy', 760 + Math.cos(lt * 17) * 50);
  s.rule.setAttribute('stroke-dashoffset', 480 * (1 - P(t, 42.6, .6, E.inOut)));
  s.def1.setAttribute('opacity', P(t, 43.0, .6)); s.def2.setAttribute('opacity', P(t, 43.4, .7));
  const sk = P(t, 44.6, .45, E.back);
  s.seal.setAttribute('opacity', sk); s.seal.setAttribute('transform', `translate(790 1170) scale(${1.6 - sk * .6}) rotate(-12)`);
  s.wrap.style.transform = `scale(${1 + lt * .01}) rotate(${-lt * .15}deg)`;
}, t => win(t, 40.0, 47.0, .5, .3));

/* S7 — the principle + "سافر قبلك" (47–62) */
const ICONS = {
  bed: 'M 12 72 V 30 M 12 58 H 88 V 72 M 88 58 V 50 Q 88 42 80 42 H 42 V 58 M 18 50 Q 18 42 26 42 H 34 V 52 H 18 Z',
  car: 'M 10 64 L 20 42 Q 24 34 34 34 H 66 Q 76 34 80 42 L 90 64 V 74 H 10 Z M 26 42 L 32 50 H 68 L 74 42 M 28 74 V 80 M 72 74 V 80 M 16 56 H 26 M 74 56 H 84',
  wheel: 'M 50 14 A 36 36 0 1 1 49.9 14 Z M 50 42 A 8 8 0 1 1 49.9 42 Z M 14 50 H 42 M 58 50 H 86 M 50 58 V 86',
  doc: 'M 24 10 H 64 L 78 24 V 90 H 24 Z M 64 10 V 24 H 78 M 34 34 H 66 M 34 46 H 66 M 34 58 H 54 M 66 66 A 13 13 0 1 1 65.9 66 Z',
  shield: 'M 50 10 L 84 22 V 48 C 84 70 68 84 50 92 C 32 84 16 70 16 48 V 22 Z M 34 50 L 46 62 L 68 38',
};
const S7 = scene(47.0, 62.0, root => {
  const bg = D('layer', root); st(bg, { background: 'radial-gradient(ellipse 90% 60% at 50% 20%, #3a2810 0%, #120d07 55%, #080604 100%)' });
  const grid = D('layer', root);
  const defs = [['bed', 'الفندق', 300, 470, 440, 330, 51.8], ['car', 'السيارة', 780, 470, 440, 330, 52.7],
    ['wheel', 'السوّاق', 300, 840, 440, 330, 53.6], ['doc', 'التراخيص', 780, 840, 440, 330, 54.6], ['shield', 'الضمانات', 540, 1170, 920, 230, 55.6]];
  const cards = defs.map(([ic, lbl, cx, cy, w, h, a]) => {
    const c = D('card', grid);
    st(c, { left: (cx - w / 2) + 'px', top: (cy - h / 2) + 'px', width: w + 'px', height: h + 'px', opacity: 0 });
    const wide = w > 600;
    const sv = S('svg', { width: 130, height: 130, viewBox: '0 0 100 100' }, c);
    if (wide) st(sv, { left: 'auto', right: '90px', top: '50%', transform: 'translateY(-50%)' });
    S('path', { d: ICONS[ic], fill: 'none', stroke: '#e3b04f', 'stroke-width': 4.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, sv);
    const l = D('lbl', c, lbl);
    if (wide) st(l, { bottom: 'auto', top: '50%', transform: 'translateY(-50%)', fontSize: '64px' });
    const ck = S('svg', { width: 76, height: 76, viewBox: '0 0 76 76' }, c);
    st(ck, { left: '28px', top: '26px', transform: 'none' });
    S('circle', { cx: 38, cy: 38, r: 34, fill: '#e3b04f' }, ck);
    const cp = S('path', { d: 'M 22 39 L 33 50 L 55 27', fill: 'none', stroke: '#140e05', 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': 60, 'stroke-dashoffset': 60 }, ck);
    return { c, a, cp, ck };
  });
  // hero
  const hero = D('layer', root);
  const rays = D('layer', hero);
  st(rays, { background: 'conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba(243,198,107,.16) 10deg, transparent 22deg, transparent 40deg, rgba(243,198,107,.12) 52deg, transparent 64deg, transparent 90deg, rgba(243,198,107,.14) 100deg, transparent 114deg, transparent 150deg, rgba(243,198,107,.1) 160deg, transparent 172deg, transparent 200deg, rgba(243,198,107,.14) 212deg, transparent 226deg, transparent 260deg, rgba(243,198,107,.12) 270deg, transparent 284deg, transparent 320deg, rgba(243,198,107,.14) 332deg, transparent 346deg)', opacity: 0,
    WebkitMaskImage: 'radial-gradient(circle at 50% 50%, #000 0px, transparent 800px)', maskImage: 'radial-gradient(circle at 50% 50%, #000 0px, transparent 800px)' });
  const whisper = D('', hero, 'سافر قبلك.');
  st(whisper, { position: 'absolute', left: 0, right: 0, top: '930px', textAlign: 'center', font: "700 150px/1 'Amiri'", color: '#f4ead7', direction: 'rtl', transform: 'translateY(-50%)', opacity: 0 });
  const big = D('', hero, 'نسافر قبلك');
  st(big, { position: 'absolute', left: 0, right: 0, top: '930px', textAlign: 'center', font: "700 190px/1 'Amiri'", direction: 'rtl', transform: 'translateY(-50%)', opacity: 0,
    background: 'linear-gradient(#fff2c8, #e3b04f 55%, #9a651a)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 0 40px rgba(227,176,79,.45))' });
  const ps = fullSvg(hero);
  const parts = [];
  for (let i = 0; i < 60; i++) parts.push({ e: S('circle', { r: 2 + hash(i * 3) * 4, fill: '#ffe1a0', opacity: 0 }, ps), ang: hash(i * 1.7) * Math.PI * 2, sp: 300 + hash(i * 5.5) * 700 });
  return { grid, cards, hero, rays, whisper, big, parts, bg };
}, (t, s) => {
  const lt = t - 47;
  const gOn = t < 59.0;
  s.grid.style.display = gOn ? '' : 'none';
  s.bg.style.opacity = gOn ? 1 : 0;
  if (gOn) {
    s.cards.forEach(c => {
      const k = P(t, c.a, .42, E.out);
      const dim = P(t, 56.8, .8, E.soft);
      st(c.c, { opacity: k * (1 - dim * .7), transform: `scale(${(1.35 - k * .35) * (1 - dim * .04)}) rotate(${(1 - k) * -4}deg)` });
      c.cp.setAttribute('stroke-dashoffset', 60 * (1 - P(t, c.a + .22, .3, E.out)));
    });
    s.grid.style.transform = `scale(${1 + lt * .004})`;
  }
  // hero
  const wk = win(t, 59.85, 60.75, .5, .15);
  st(s.whisper, { opacity: wk, filter: `blur(${(1 - P(t, 59.85, .7)) * 12}px)` });
  const bk = P(t, 60.6, .7, E.out);
  st(s.big, { opacity: t >= 60.6 ? bk : 0, transform: `translateY(-50%) scale(${1.12 - bk * .12 + Math.max(0, t - 61.3) * .02})` });
  st(s.rays, { opacity: P(t, 60.6, 1.0) * .9, transform: `rotate(${(t - 60) * 8}deg) scale(1.6)` });
  s.parts.forEach(p => {
    const k = clamp((t - 60.6) / 1.4);
    const d = E.out(k) * p.sp;
    p.e.setAttribute('cx', 540 + Math.cos(p.ang) * d); p.e.setAttribute('cy', 930 + Math.sin(p.ang) * d * .8);
    p.e.setAttribute('opacity', t >= 60.6 ? (1 - k) * .9 : 0);
  });
}, t => win(t, 47.0, 62.0, .3, .3));

/* S8 — growth (62–70) */
const DEST = [[29, 41], [44.8, 41.7], [49.9, 40.4], [31.2, 30], [-8, 31.6], [-3.7, 40.4], [2.35, 48.85], [12.5, 41.9], [8.5, 47.4], [16.4, 48.2], [11.6, 48.1], [-0.13, 51.5], [18.4, 43.9], [55.3, 25.2], [101.7, 3.1], [115.2, -8.6], [100.5, 13.75], [73.5, 4.2], [121.5, 31.2], [69.2, 41.3], [76.9, 43.2]].map(([a, b]) => proj(a, b));
const S8 = scene(62.0, 70.0, root => {
  const bg = D('layer', root); st(bg, { background: 'radial-gradient(ellipse 100% 70% at 50% 45%, #2c1c0b 0%, #0f0904 70%, #060402 100%)' });
  const m = makeMap(root, '#7d6a48', 560);
  const pin = makePin(m.svg, '#e3b04f');
  const arcs = DEST.map((to, i) => {
    const d = arcPath(HOME, to, .25 + hash(i) * .12);
    const p = S('path', { d, fill: 'none', stroke: '#f2cf7e', 'stroke-width': 2.5, opacity: .9 }, m.svg);
    const dot = S('circle', { cx: to[0], cy: to[1], r: 0, fill: '#ffe3a1', filter: 'url(#glow)' }, m.svg);
    return { p, dot, len: p.getTotalLength(), a: 62.45 + i * .13 };
  });
  const br = [['jeddah', 'جدة', 65.2], ['trabzon', 'طرابزون', 67.4]].map(([c, n, a]) => {
    const to = MAP.cities[c];
    const ring = S('circle', { cx: to[0], cy: to[1], r: 0, fill: 'none', stroke: '#ffe3a1', 'stroke-width': 4 }, m.svg);
    const core = S('circle', { cx: to[0], cy: to[1], r: 0, fill: '#ffe3a1' }, m.svg);
    const lab = D('label', m.wrap, `<span class="chip">فرع</span>${n}`);
    st(lab, { right: (W - to[0] + 26) + 'px', top: (to[1] - 32) + 'px', fontSize: '52px', opacity: 0 });
    return { ring, core, lab, a };
  });
  const cnt = D('counter', root);
  st(cnt, { top: '130px' });
  cnt.innerHTML = `<div style="font:700 56px/1.2 'Amiri';color:#e3b04f;direction:rtl">أكثر من</div><div style="font:900 230px/1 'Cairo';background:linear-gradient(#fff2c8,#e3b04f 60%,#9a651a);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 30px rgba(227,176,79,.35))"></div><div style="font:700 70px/1.2 'Amiri';color:#f4ead7">دولة حول العالم</div>`;
  return { m, pin, arcs, br, cnt, num: cnt.children[1], sub: cnt.lastChild };
}, (t, s) => {
  const lt = t - 62;
  s.pin.g.setAttribute('transform', `translate(${HOME[0]} ${HOME[1]})`);
  s.pin.head.setAttribute('transform', `scale(${P(t, 62.1, .5, E.back)})`);
  let n = 0;
  s.arcs.forEach(a => {
    const k = P(t, a.a, .55, E.inOut);
    a.p.setAttribute('stroke-dasharray', a.len); a.p.setAttribute('stroke-dashoffset', a.len * (1 - k));
    const pop = P(t, a.a + .5, .35, E.back);
    a.dot.setAttribute('r', 6.5 * pop);
    if (t >= a.a + .5) n++;
  });
  s.num.textContent = AR(Math.max(1, n));
  st(s.cnt, { opacity: P(t, 62.2, .5), transform: `scale(${1 + (n >= 21 ? Math.exp(-(t - 65.3) * 6) * .08 : 0)})` });
  s.br.forEach(b => {
    const k = P(t, b.a, .5, E.back);
    const rp = ((t - b.a) % 1.4) / 1.4;
    b.core.setAttribute('r', 11 * k);
    b.ring.setAttribute('r', t > b.a ? 14 + rp * 46 : 0); b.ring.setAttribute('opacity', (1 - rp));
    st(b.lab, { opacity: P(t, b.a + .1, .45), transform: `translateX(${(1 - P(t, b.a + .1, .45)) * -20}px)` });
  });
  const z = P(t, 64.8, 3.2, E.inOut);
  st(s.m.wrap, { transformOrigin: '40% 45%', transform: `scale(${1 + lt * .008 + z * .28})` });
}, t => win(t, 62.0, 70.0, .45, .4));

/* S9 — the sign (70–76.9) */
const S9 = scene(70.0, 76.9, root => {
  const h = buildHall(root, true);
  h.front.setAttribute('opacity', .55); h.front.setAttribute('filter', 'url(#b3)');
  const bloom = S('circle', { cx: 540, cy: 960, r: 0, fill: 'url(#bloomGold)' }, h.svg);
  const drv = S('g', null, h.svg);
  const sign = D('', root);
  st(sign, { position: 'absolute', left: '170px', width: '740px', top: '690px', height: '380px', borderRadius: '18px', direction: 'rtl', textAlign: 'center',
    background: 'linear-gradient(160deg,#17130d,#050403)', border: '3px solid #e3b04f', boxShadow: '0 40px 90px rgba(0,0,0,.7), 0 0 60px rgba(227,176,79,.25)' });
  sign.innerHTML = `<div style="font:700 92px/1.2 'Amiri';margin-top:48px;background:linear-gradient(#fff2c8,#e3b04f 60%,#a06a1c);-webkit-background-clip:text;background-clip:text;color:transparent">حفاوة المسافرون</div>
    <div style="width:420px;height:2px;margin:18px auto;background:linear-gradient(90deg,transparent,#e3b04f,transparent)"></div>
    <div style="font:800 64px/1.3 'Cairo';color:#f4ead7">مرحبًا أ. عبدالله</div>`;
  const hands = fullSvg(root);
  const hg = S('g', null, hands);
  [[178, 1], [902, -1]].forEach(([x, d]) => {
    const g = S('g', { transform: `translate(${x} 0)` }, hg);
    S('path', { d: `M ${-d * 40} 1100 C ${-d * 30} 1000 ${-d * 10} 930 ${d * 10} 900`, fill: 'none', stroke: '#120c06', 'stroke-width': 70, 'stroke-linecap': 'round' }, g);
    S('rect', { x: -26, y: 850, width: 52, height: 100, rx: 26, fill: '#1a120a', stroke: '#ffd38a', 'stroke-opacity': .35, 'stroke-width': 2 }, g);
  });
  const parts = [];
  for (let i = 0; i < 40; i++) parts.push({ e: S('circle', { r: 1.5 + hash(i * 3.3) * 3, fill: '#ffe1a0' }, h.svg), x: hash(i * 2.2) * 1080, y: hash(i * 6.1) * 1900, ph: hash(i * 9.9) });
  return { ...h, bloom, drv, sign, parts, hg };
}, (t, s) => {
  const lt = t - 70;
  drawHall(s, .3 + lt * .03);
  const k = P(t, 70.2, .9, E.back);
  st(s.sign, { transform: `translateY(${(1 - k) * 420}px) rotate(${(1 - k) * 3 + Math.sin(lt * 1.1) * .4}deg)`, opacity: P(t, 70.2, .4) });
  s.hg.setAttribute('transform', `translate(0 ${(1 - k) * 420 + Math.sin(lt * 1.1) * 3})`);
  s.hg.setAttribute('opacity', P(t, 70.2, .4));
  s.bloom.setAttribute('r', 200 + P(t, 70.3, 1.5) * 650 + Math.sin(lt * 2) * 20);
  s.parts.forEach(p => {
    const y = ((p.y - lt * 40 * (1 + p.ph)) % 1900 + 1900) % 1900;
    p.e.setAttribute('cx', p.x + Math.sin(lt + p.ph * 10) * 20); p.e.setAttribute('cy', y);
    p.e.setAttribute('opacity', (.3 + Math.sin(lt * 2 + p.ph * 40) * .3) * P(t, 70.4, 1));
  });
  s.root.style.transform = `scale(${1.02 + lt * .006})`;
}, t => win(t, 70.0, 76.9, .4, 0));

/* S10 — back to the cup (76.4–80), clock c = t-80 */
const S10 = scene(76.4, 80.0, r => buildCoffee(r, false), (t, s) => {
  drawCoffee(s, t - 80, null);
  s.root.style.transform = `scale(${1 + 0 * t})`;
}, t => (t >= 76.4 && t < 80) ? E.soft(clamp((t - 76.4) / .5)) : 0);

/* ---------- captions ---------- */
const CUES = [
  [0.25, 3.0, 'هذا الفنجان… وراه واحد وعشرين دولة', ['واحد', 'وعشرين', 'دولة']],
  [3.6, 5.6, 'تعرف هالشعور؟'],
  [5.6, 7.7, 'توصل بلد ما تعرف فيه أحد…'],
  [7.7, 10.0, 'الكل فيه أحد ينتظرهم… إلا أنت.', ['إلا', 'أنت.']],
  [10.4, 12.6, 'من صغري وأنا أحب السفر…', ['السفر…']],
  [12.6, 15.4, 'من شنغهاي… لماربيا.', ['شنغهاي…', 'لماربيا.']],
  [15.8, 17.3, 'بس ترتيبات السفر؟'],
  [19.8, 21.7, 'وهل كل شي بيمشي صح؟'],
  [22.4, 24.6, 'وكنت أقول لنفسي…', [], 'hero'],
  [24.6, 27.7, 'يا ليت فيه أحد أثق فيه… يرتّب لي كل شي.', ['أثق'], 'hero'],
  [28.4, 35.5, 'يا وليدي… أنا أسافر على طول.', [], 'quote', 640],
  [31.2, 35.5, 'لو تقدر توفّر لي سوّاق… وفنادق زينة…', [], 'quote', 800],
  [33.6, 35.5, 'أنا معك على طول.', ['أنا', 'معك', 'على', 'طول.'], 'quote', 980],
  [35.8, 37.3, 'وهنا انتبهت…', [], 'hero'],
  [37.3, 39.2, 'هو يطلب بالضبط… اللي كنت أتمناه لنفسي.', ['أتمناه'], 'hero'],
  [40.6, 42.6, 'فأسسنا… حَفاوة المسافرون.', ['حَفاوة', 'المسافرون.']],
  [42.8, 46.6, 'لأن المسافر يستاهل استقبال… مو بس حجز.', ['استقبال…']],
  [47.2, 49.5, 'ومبدأنا من أول يوم:', [], 'hero'],
  [49.6, 51.7, 'ما نقدّم لك خدمة… ما جرّبناها.', ['جرّبناها.'], 'hero'],
  [51.8, 54.6, 'نجرّب الفندق… السيارة… السوّاق…'],
  [54.6, 56.8, 'ونتأكد من التراخيص والضمانات…'],
  [56.8, 58.9, 'عشان لما تسافر… يكون فيه أحد…', ['أحد…']],
  [62.4, 65.2, 'واليوم… أكثر من واحد وعشرين دولة…', ['واحد', 'وعشرين', 'دولة…']],
  [65.2, 67.4, 'وفرع في جدة…', ['جدة…']],
  [67.4, 69.6, 'وفرع في طرابزون.', ['طرابزون.']],
  [70.6, 72.6, 'حَفاوة المسافرون…', ['حَفاوة', 'المسافرون…']],
  [72.6, 75.8, 'نسافر قبلك… عشان ترتاح في سفرك.', ['نسافر', 'قبلك…']],
  [76.8, 79.7, 'وكل هذا… بدأ من هالفنجان.', ['هالفنجان.']],
];
const capRoot = document.getElementById('captions');
const CUE_SRC = TM ? TM.cues : CUES.map(([a, b, text, hl = [], style = 'cap', y]) => ({ a, b, e: b - .4, text, hl, style, y }));
const cues = CUE_SRC.map(({ a, b, e: se, text, hl = [], style = 'cap', y }) => {
  const e = D('cue ' + style, capRoot);
  if (y) e.style.top = y + 'px';
  const words = text.split(' ').map(w => { const s = document.createElement('span'); s.className = 'w' + (hl.includes(w) ? ' hl' : ''); s.textContent = w; e.appendChild(s); return s; });
  const lens = words.map(w => w.textContent.replace(/[\u064B-\u0652…\.؟:،]/g, '').length + 1);
  const tot = lens.reduce((x, y) => x + y, 0); let acc = 0;
  const offs = lens.map(l => { const o = acc / tot; acc += l; return o; });
  return { a, b, se, e, words, style, offs };
});
function drawCaptions(t) {
  for (const c of cues) {
    const on = t >= c.a - .01 && t < c.b;
    c.e.style.display = on ? 'block' : 'none';
    if (!on) continue;
    const span = Math.max(.2, (c.se - c.a) * .9);
    const out = 1 - P(t, c.b - .22, .22, E.soft);
    const dur = c.style === 'cap' ? .26 : .55;
    c.words.forEach((w, i) => {
      const k = P(t, c.a + span * c.offs[i], dur, E.out);
      w.style.opacity = k * out;
      w.style.transform = c.style === 'cap' ? `translateY(${(1 - k) * 26}px) scale(${1.15 - k * .15})` : `translateY(${(1 - k) * 14}px)`;
      w.style.filter = c.style === 'cap' ? '' : `blur(${(1 - k) * 8}px)`;
    });
  }
}

/* ---------- global fx ---------- */
const grain = document.getElementById('grain');
const gctx = grain.getContext('2d');
const grainFrames = [];
for (let f = 0; f < 8; f++) {
  const id = gctx.createImageData(grain.width, grain.height);
  for (let i = 0; i < id.data.length; i += 4) { const v = hash(i * .13 + f * 1000.7) * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  grainFrames.push(id);
}
const flash = document.getElementById('flash'), black = document.getElementById('black');
const FLASH = [[3.2, .45, '#fff', .55], [39.35, .18, '#fff', .22], [60.6, .5, '#ffe3a1', .4]];
const BLACKS = [[21.75, 22.0, 0, 0], [39.5, 40.0, 0, .45], [59.0, 59.85, 0, 0], [9.95, 10.45, .25, .25]];
const SHAKES = [[3.2, .5, 14], [17.4, .35, 10], [18.2, .35, 10], [19.0, .35, 12], [19.8, 1.9, 6], [39.35, .3, 6], [51.8, .3, 9], [52.7, .3, 9], [53.6, .3, 9], [54.6, .3, 9], [55.6, .35, 11], [60.6, .5, 12]];

function render(T) {
  T = ((T % DUR) + DUR) % DUR;
  const t = warp(T);
  for (const s of scenes) {
    const o = s.env(t);
    if (o <= 0) { s.root.style.display = 'none'; continue; }
    s.root.style.display = 'block'; s.root.style.opacity = o;
    s.draw(t, s);
  }
  drawCaptions(T);
  // flash
  let fo = 0, fc = '#fff';
  for (const [a, d, c, m] of FLASH) if (t >= a && t < a + d) { fo = Math.max(fo, (1 - (t - a) / d) * m); fc = c; }
  flash.style.background = fc; flash.style.opacity = fo;
  let bo = 0;
  for (const [a, b, fi, fo2] of BLACKS) if (t >= a && t < b) bo = Math.max(bo, win(t, a, b, fi, fo2));
  black.style.opacity = bo;
  // shake
  let sx = 0, sy = 0;
  for (const [a, d, amp] of SHAKES) if (t >= a && t < a + d) { const k = 1 - (t - a) / d; sx += nz(t * 38, a) * amp * k; sy += nz(t * 41, a + 9) * amp * k; }
  shakeEl.style.transform = `translate(${sx}px,${sy}px)`;
  gctx.putImageData(grainFrames[Math.floor(T * 24) % 8], 0, 0);
}
window.__render = render;
window.__DUR = DUR;
window.__CUES = CUES;
window.__ready = document.fonts.ready.then(() => { render(0); return true; });

/* ---------- live mode ---------- */
if (CAPTURE) { document.body.classList.add('capture'); return; }
const vp = document.getElementById('viewport');
const fit = () => { const s = Math.min(innerWidth / W, innerHeight / H); vp.style.transform = `scale(${s})`; };
addEventListener('resize', fit); fit();
const snd = document.getElementById('snd');
let start = performance.now();
const restart = () => { start = performance.now(); if (snd && !snd.paused) snd.currentTime = 0; };
addEventListener('keydown', e => {
  if (e.key === 'r' || e.key === 'R') restart();
  if (e.key === 'f' || e.key === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
  if (e.code === 'Space' && snd) { e.preventDefault(); if (snd.paused) { restart(); snd.currentTime = 0; snd.play(); } else snd.pause(); }
});
const hint = document.getElementById('hint');
setTimeout(() => hint.style.opacity = 0, 4000);
let idle;
addEventListener('mousemove', () => { document.body.classList.remove('nocursor'); clearTimeout(idle); idle = setTimeout(() => document.body.classList.add('nocursor'), 3000); });
idle = setTimeout(() => document.body.classList.add('nocursor'), 3000);
const loop = now => {
  const t = (snd && !snd.paused) ? snd.currentTime : ((now - start) / 1000);
  render(t);
  requestAnimationFrame(loop);
};
window.__ready.then(() => requestAnimationFrame(loop));
})();
