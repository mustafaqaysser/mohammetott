#!/usr/bin/env python3
"""DAVINCI identity — logo builder.

Constructs the three symbol directions from explicit geometry (see PLAN.md),
sets the bilingual wordmarks in the specified Google Fonts, shapes Arabic with
HarfBuzz and converts every glyph to outlines, then writes:

  logos/<dir>/davinci-<x>-{symbol,horizontal,stacked}-{light,dark}.svg
  tools/build/sprite.svg      (CSS-variable coloured <symbol>s for index.html)
  tools/build/construction-*.svg (construction drawings for the presentation)

Requires: fonttools, uharfbuzz.  Fonts are fetched once from Google Fonts into
tools/.fonts (git-ignored).
"""
import json
import math
import os
import re
import urllib.request

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "tools", ".fonts")
BUILD_DIR = os.path.join(ROOT, "tools", "build")
LOGO_DIR = os.path.join(ROOT, "logos")

PHI = (1 + 5 ** 0.5) / 2


def f(x):
    """Compact number formatting for SVG."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------
def font_path(family, weight):
    os.makedirs(FONT_DIR, exist_ok=True)
    fn = os.path.join(FONT_DIR, f"{family.replace(' ', '')}-{weight}.ttf")
    if os.path.exists(fn):
        return fn
    url = ("https://fonts.googleapis.com/css2?family="
           f"{family.replace(' ', '+')}:wght@{weight}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/4.0"})
    css = urllib.request.urlopen(req).read().decode()
    srcs = re.findall(r"url\((https://[^)]+\.ttf)\)", css)
    # Arabic families come split in subsets: take the one that has Arabic,
    # css2 without text= returns a single static ttf for old UAs.
    data = urllib.request.urlopen(srcs[0]).read()
    with open(fn, "wb") as fh:
        fh.write(data)
    return fn


class Face:
    _cache = {}

    def __init__(self, family, weight):
        path = font_path(family, weight)
        self.tt = TTFont(path)
        blob = hb.Blob.from_file_path(path)
        self.hbfont = hb.Font(hb.Face(blob))
        self.upem = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    @classmethod
    def get(cls, family, weight):
        key = (family, weight)
        if key not in cls._cache:
            cls._cache[key] = Face(family, weight)
        return cls._cache[key]


def text_outline(face, text, size, tracking=0.0, x=0.0, baseline=0.0):
    """Shape `text` and return (path_d, advance_width, (xmin,ymin,xmax,ymax)).

    tracking is in em/1000 (like design tools). y grows downward (SVG)."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(face.hbfont, buf, {"kern": True, "liga": True})
    scale = size / face.upem
    track = tracking / 1000.0 * size
    svg = SVGPathPen(face.gs, ntos=f)
    bounds = BoundsPen(face.gs)
    cx = x
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = face.order[info.codepoint]
        gx = cx + pos.x_offset * scale
        gy = baseline - pos.y_offset * scale
        t = (scale, 0, 0, -scale, gx, gy)
        face.gs[name].draw(TransformPen(svg, t))
        face.gs[name].draw(TransformPen(bounds, t))
        cx += pos.x_advance * scale
        if i < n - 1:
            cx += track
    return svg.getCommands(), cx - x, bounds.bounds


def measure(face, text, size, tracking=0.0):
    _, w, b = text_outline(face, text, size, tracking)
    return w, b


# --------------------------------------------------------------------------
# Symbols — pure geometry
# --------------------------------------------------------------------------
# Each symbol returns (svg_inner, viewbox_w, viewbox_h). Colours come from a
# dict so the same geometry can be emitted with hex values or CSS variables.

def sym_codex(c, small=False):
    r_out = 40.0
    r_in = r_out / PHI                       # 24.72
    w = r_out - r_in                         # 15.28
    top_inner_y = 50 - r_in                  # 25.28
    head_x = 50 - r_in                       # 25.28  top-arm terminal
    head_tip = head_x + w * 0.62             # qalam cut: upper point
    base_top = 50 + r_in                     # 74.72
    stem_w = 6.4 if small else 3.2
    mass = (f"M{f(head_tip)} 10H50A{f(r_out)} {f(r_out)} 0 0 1 50 90H10"
            f"V{f(base_top)}H50A{f(r_in)} {f(r_in)} 0 0 0 50 {f(top_inner_y)}"
            f"H{f(head_x)}Z")
    stem = (f'<rect x="10" y="10" width="{f(stem_w)}" '
            f'height="{f(base_top - 10)}" fill="{c["accent"]}"/>')
    return (f'{stem}<path d="{mass}" fill="{c["ink"]}"/>', 100, 100)


def _hex(R=42.0, cx=50.0, cy=50.0, k=1.0):
    R = R * k
    a = R * math.cos(math.radians(30))
    return {
        "top": (cx, cy - R), "ur": (cx + a, cy - R / 2),
        "lr": (cx + a, cy + R / 2), "bot": (cx, cy + R),
        "ll": (cx - a, cy + R / 2), "ul": (cx - a, cy - R / 2),
        "c": (cx, cy),
    }


def model_counter(inset=11.0):
    H = _hex()
    s30 = math.tan(math.radians(30))
    dy = inset / math.cos(math.radians(30))
    x0, x1 = 50 + inset, H["ur"][0] - inset
    top = lambda x: H["top"][1] + (x - 50) * s30 + dy
    bot = lambda x: H["bot"][1] - (x - 50) * s30 - dy
    return [(x0, top(x0)), (x1, top(x1)), (x1, bot(x1)), (x0, bot(x0))]


def sym_model(c, small=False):
    H = _hex()
    sw = 7.0 if small else 3.2
    apo = 42 * math.cos(math.radians(30))
    k = (apo - sw / 2) / apo
    W = _hex(k=k)
    P = lambda p: f"{f(p[0])} {f(p[1])}"
    solid = (f"M{P(H['top'])}L{P(H['ur'])}L{P(H['lr'])}L{P(H['bot'])}Z")
    cnt = model_counter(9.0 if small else 11.0)
    solid += "M" + "L".join(P(p) for p in cnt) + "Z"
    wire = (f"M50 {f(W['top'][1])}L{P(W['ul'])}L{P(W['ll'])}L50 {f(W['bot'][1])}"
            f"M{P(W['ul'])}L50 50L50 {f(W['bot'][1])}")
    out = (f'<path d="{solid}" fill="{c["solid"]}" fill-rule="evenodd"/>'
           f'<path d="{wire}" fill="none" stroke="{c["wire"]}" '
           f'stroke-width="{f(sw)}" stroke-linejoin="miter" stroke-linecap="square"/>')
    if not small:
        out += (f'<path d="M50 50L{P(W["ll"])}" fill="none" stroke="{c["wire"]}" '
                f'stroke-width="1.6" stroke-dasharray="3.2 3.2"/>')
    return out, 100, 100


def sym_monolith(c, small=False):
    Wd, Ht = 100 * PHI, 100.0                # 161.8 × 100 golden block
    split = Wd - Ht                          # 61.8: left mass is a golden rect,
                                             # right mass is the square
    g = 3.6 if small else 2.4                # the joint — the only drawn line
    r = Ht / PHI ** 2                        # arc radius 38.2
    cy = Ht / 2
    xl, xr = split - g / 2, split + g / 2
    dy = math.sqrt(r * r - (g / 2) ** 2)
    left = f"M0 0H{f(xl)}V{f(Ht)}H0Z"
    right = (f"M{f(xr)} 0H{f(Wd)}V{f(Ht)}H{f(xr)}V{f(cy + dy)}"
             f"A{f(r)} {f(r)} 0 0 0 {f(xr)} {f(cy - dy)}Z")
    return (f'<path d="{left}" fill="{c["mass"]}"/>'
            f'<path d="{right}" fill="{c["mass2"]}"/>', Wd, Ht)


# --------------------------------------------------------------------------
# Direction definitions
# --------------------------------------------------------------------------
DIRS = {
    "A": dict(
        slug="A-codex", name="codex", sym=sym_codex,
        light=dict(ink="#3B2A1E", accent="#A8432F", text="#3B2A1E", sub="#6E6A63"),
        dark=dict(ink="#F2EBDD", accent="#C8654E", text="#F2EBDD", sub="#B9AE9C"),
        var=dict(ink="var(--lg-ink,#3B2A1E)", accent="var(--lg-accent,#A8432F)",
                 text="var(--lg-text,#3B2A1E)", sub="var(--lg-sub,#6E6A63)"),
        ar=("Amiri", 700, 0.0), en=("Cormorant Garamond", 600, 180),
        dar=("Amiri", 400, 0.0), den=("IBM Plex Mono", 400, 60),
        ar_ink=0.56, en_cap=0.23, d_cap=0.07, dar_scale=1.18,
    ),
    "B": dict(
        slug="B-model", name="model", sym=sym_model,
        light=dict(solid="#2F6FED", wire="#0E1621", text="#0E1621", sub="#4A5566"),
        dark=dict(solid="#2F6FED", wire="#F7F8FA", text="#F7F8FA", sub="#C9CCCF"),
        var=dict(solid="var(--lg-solid,#2F6FED)", wire="var(--lg-wire,#0E1621)",
                 text="var(--lg-text,#0E1621)", sub="var(--lg-sub,#4A5566)"),
        ar=("IBM Plex Sans Arabic", 600, 0.0), en=("Space Grotesk", 700, 140),
        dar=("IBM Plex Sans Arabic", 400, 0.0), den=("IBM Plex Mono", 500, 80),
        ar_ink=0.52, en_cap=0.21, d_cap=0.068, dar_scale=1.0,
    ),
    "C": dict(
        slug="C-monolith", name="monolith", sym=sym_monolith,
        light=dict(mass="#141312", mass2="#141312", text="#141312", sub="#8A857D"),
        dark=dict(mass="#E4DCCF", mass2="#E4DCCF", text="#E4DCCF", sub="#9A7444"),
        var=dict(mass="var(--lg-mass,#141312)", mass2="var(--lg-mass2,#141312)",
                 text="var(--lg-text,#141312)", sub="var(--lg-sub,#8A857D)"),
        ar=("Alexandria", 600, 0.0), en=("Syne", 600, 320),
        dar=("Alexandria", 300, 0.0), den=("Syne", 600, 200),
        ar_ink=0.56, en_cap=0.2, d_cap=0.064, dar_scale=1.0,
    ),
}

AR_NAME = "دافنشي"
EN_NAME = "DAVINCI"
AR_DESC = ["هندسة", "إشراف", "نمذجة"]
EN_DESC = ["ENGINEERING", "SUPERVISION", "BIM"]


def cap_height(face):
    os2 = face.tt["OS/2"]
    ch = getattr(os2, "sCapHeight", 0) or 0
    if ch <= 0:
        _, b = measure(face, "H", face.upem)
        ch = -b[1] if b else face.upem * 0.7
    return ch / face.upem


def word_block(face, text, size, tracking, x, baseline):
    d, w, b = text_outline(face, text, size, tracking, x, baseline)
    return d, w, b


def desc_line(face, parts, size, tracking, x, baseline, rtl, dot_r):
    """Lay out descriptor segments separated by a drawn middle dot.
    Returns (path_d, width, dots[(cx,cy)]). x is the left edge."""
    # measure segments
    segs = [measure(face, p, size, tracking)[0] for p in parts]
    gap = size * 1.25
    total = sum(segs) + gap * (len(parts) - 1)
    order = list(range(len(parts)))
    if rtl:
        order = order[::-1]          # first Arabic word sits on the right
    cx = x
    ds, dots = [], []
    xh = size * 0.32
    for j, idx in enumerate(order):
        d, w, _ = text_outline(face, parts[idx], size, tracking, cx, baseline)
        ds.append(d)
        cx += w
        if j < len(order) - 1:
            dots.append((cx + gap / 2, baseline - xh))
            cx += gap
    return " ".join(ds), total, dots


def build_lockup(key, colors, layout):
    D = DIRS[key]
    sym_inner, sw_, sh_ = D["sym"](colors)
    Hs = 100.0                                  # symbol height in lockup units
    s_scale = Hs / sh_
    sym_w = sw_ * s_scale

    far = Face.get(*D["ar"][:2])
    fen = Face.get(*D["en"][:2])
    fdar = Face.get(*D["dar"][:2])
    fden = Face.get(*D["den"][:2])

    # sizes: Arabic by ink height, English by cap height
    _, b = measure(far, AR_NAME, 100)
    ar_size = 100 * (D["ar_ink"] * Hs) / (b[3] - b[1])
    en_size = D["en_cap"] * Hs / cap_height(fen)
    d_size = D["d_cap"] * Hs / cap_height(fden)
    dar_size = d_size * D["dar_scale"] * 1.15

    tc, sc = colors["text"], colors["sub"]
    parts = []
    _, arb = measure(far, AR_NAME, ar_size)
    ar_w = arb[2] - arb[0]
    _, enb = measure(fen, EN_NAME, en_size, D["en"][2])
    en_w = enb[2] - enb[0]
    dar_w = desc_line(fdar, AR_DESC, dar_size, 0, 0, 0, True, 0)[1]
    den_w = desc_line(fden, EN_DESC, d_size, D["den"][2], 0, 0, False, 0)[1]
    dot_r = d_size * 0.055

    if layout == "horizontal":
        gap = Hs * 0.30
        # names share one baseline; descriptors share a second baseline that
        # clears the Arabic descender. The group is centred on the symbol.
        dgap = Hs * D.get("dgap", 0.17)
        group_top = arb[1]                       # relative to base = 0
        dbase_rel = arb[3] + dgap + d_size * 0.72
        group_h = dbase_rel - group_top
        base = Hs / 2 - group_h / 2 - group_top
        dbase = base + dbase_rel
        left_w = max(en_w, den_w)
        right_w = max(ar_w, dar_w)
        sx = left_w + gap
        rx = sx + sym_w + gap
        total_w = rx + right_w
        # English block: right aligned to symbol
        en_x = left_w - en_w - enb[0]
        d, _, _ = text_outline(fen, EN_NAME, en_size, D["en"][2], en_x, base)
        parts.append(f'<path d="{d}" fill="{tc}"/>')
        dd, _, dots = desc_line(fden, EN_DESC, d_size, D["den"][2],
                                left_w - den_w, dbase, False, dot_r)
        parts.append(f'<path d="{dd}" fill="{sc}"/>')
        parts += [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(dot_r * 2.2)}" fill="{sc}"/>'
                  for x, y in dots]
        # Arabic block: left aligned to symbol
        d, _, _ = text_outline(far, AR_NAME, ar_size, 0, rx - arb[0], base)
        parts.append(f'<path d="{d}" fill="{tc}"/>')
        dd, _, dots = desc_line(fdar, AR_DESC, dar_size, 0, rx, dbase, True, dot_r)
        parts.append(f'<path d="{dd}" fill="{sc}"/>')
        parts += [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(dot_r * 2.2)}" fill="{sc}"/>'
                  for x, y in dots]
        sym = (f'<g transform="translate({f(sx)} 0) scale({f(s_scale)})">'
               f'{sym_inner}</g>')
        # vertical bounds: include Arabic descender
        _, ab = text_outline(far, AR_NAME, ar_size, 0, 0, base)[1:]
        top = min(0, ab[1])
        bottom = max(Hs, dbase + d_size * 0.35, ab[3])
        pad = Hs * 0.0
        vb = (0 - pad, top - pad, total_w + 2 * pad, bottom - top + 2 * pad)
        return sym + "".join(parts), vb

    # stacked
    cx = 0.0
    width = max(sym_w, ar_w, en_w, dar_w, den_w)
    cx = width / 2
    y = 0.0
    sym = (f'<g transform="translate({f(cx - sym_w / 2)} 0) scale({f(s_scale)})">'
           f'{sym_inner}</g>')
    y = Hs + Hs * 0.30
    ar_base = y - arb[1]
    d, _, _ = text_outline(far, AR_NAME, ar_size, 0, cx - ar_w / 2 - arb[0], ar_base)
    parts.append(f'<path d="{d}" fill="{tc}"/>')
    y = ar_base + arb[3] + Hs * 0.18
    en_base = y - enb[1]
    d, _, _ = text_outline(fen, EN_NAME, en_size, D["en"][2],
                           cx - en_w / 2 - enb[0], en_base)
    parts.append(f'<path d="{d}" fill="{tc}"/>')
    y = en_base + Hs * 0.30
    dd, _, dots = desc_line(fdar, AR_DESC, dar_size, 0, cx - dar_w / 2, y, True, dot_r)
    parts.append(f'<path d="{dd}" fill="{sc}"/>')
    parts += [f'<circle cx="{f(x)}" cy="{f(yy)}" r="{f(dot_r * 2.2)}" fill="{sc}"/>'
              for x, yy in dots]
    y += Hs * 0.17
    dd, _, dots = desc_line(fden, EN_DESC, d_size, D["den"][2], cx - den_w / 2, y,
                            False, dot_r)
    parts.append(f'<path d="{dd}" fill="{sc}"/>')
    parts += [f'<circle cx="{f(x)}" cy="{f(yy)}" r="{f(dot_r * 2.2)}" fill="{sc}"/>'
              for x, yy in dots]
    bottom = y + d_size * 0.1
    return sym + "".join(parts), (0, 0, width, bottom)


def wordmark_symbols(key, colors):
    """Separate Arabic / English wordmarks for flexible page layouts."""
    D = DIRS[key]
    far = Face.get(*D["ar"][:2])
    fen = Face.get(*D["en"][:2])
    out = {}
    _, b = measure(far, AR_NAME, 100)
    d, _, b = text_outline(far, AR_NAME, 100, 0, -b[0], 0)
    out["ar"] = (f'<path d="{d}" fill="{colors["text"]}"/>', (0, b[1], b[2] - b[0], b[3] - b[1]))
    _, b = measure(fen, EN_NAME, 100, D["en"][2])
    d, _, b = text_outline(fen, EN_NAME, 100, D["en"][2], -b[0], 0)
    out["en"] = (f'<path d="{d}" fill="{colors["text"]}"/>', (0, b[1], b[2] - b[0], b[3] - b[1]))
    return out


def svg_doc(inner, vb, title, pad=0.0, w=None):
    x, y, ww, hh = vb
    x, y, ww, hh = x - pad, y - pad, ww + 2 * pad, hh + 2 * pad
    size = f' width="{f(w)}" height="{f(w * hh / ww)}"' if w else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{f(x)} {f(y)} {f(ww)} {f(hh)}"{size}>'
            f'<title>{title}</title>{inner}</svg>\n')


# --------------------------------------------------------------------------
# Construction drawings (for the presentation)
# --------------------------------------------------------------------------
def construction_codex():
    r, ri = 40, 40 / PHI
    L = []
    ln = 'stroke="var(--cs-line,#A8432F)" stroke-width=".35" fill="none"'
    lf = 'stroke="var(--cs-faint,#A8432F)" stroke-width=".25" fill="none" opacity=".55"'
    L.append(f'<rect x="10" y="10" width="80" height="80" {ln}/>')
    L.append(f'<circle cx="50" cy="50" r="{r}" {ln}/>')
    L.append(f'<circle cx="50" cy="50" r="{f(ri)}" {ln}/>')
    L.append(f'<path d="M50 4V96M4 50H96M10 10L90 90M90 10L10 90" {lf}/>')
    gx = 10 + 80 / PHI
    L.append(f'<path d="M{f(gx)} 6V94M6 {f(gx)}H94" {lf} stroke-dasharray="1 1"/>')
    L.append(f'<path d="M{f(50 - ri)} 6V30M10 74.72H96M10 25.28H96" {lf} stroke-dasharray="1 1"/>')
    # radius callouts
    L.append(f'<path d="M50 50L{f(50 + r * math.cos(-0.6))} {f(50 + r * math.sin(-0.6))}" {ln}/>')
    L.append(f'<path d="M50 50L{f(50 + ri * math.cos(0.9))} {f(50 + ri * math.sin(0.9))}" {ln}/>')
    for (x, y) in [(10, 10), (90, 10), (90, 90), (10, 90), (50, 50), (50, 10), (50, 90)]:
        L.append(f'<circle cx="{x}" cy="{y}" r=".9" fill="var(--cs-line,#A8432F)"/>')
    return "".join(L)


def construction_model():
    H = _hex()
    P = lambda p: f"{f(p[0])} {f(p[1])}"
    L = []
    ln = 'stroke="var(--cs-line,#2F6FED)" stroke-width=".3" fill="none"'
    lf = 'stroke="var(--cs-faint,#2F6FED)" stroke-width=".2" fill="none" opacity=".5"'
    # isometric grid
    s = 42 / 6
    lines = []
    for i in range(-12, 13):
        off = i * s
        lines.append(f"M{f(50 + off * 0.866 - 60 * 0.866)} {f(50 + off * 0.5 + 60 * 0.5 - 60)}"
                     f"l{f(120 * 0.866)} {f(-120 * 0.5) if False else f(0)}")
    # simpler: 3 families of lines clipped by a rect
    fam = []
    for i in range(-20, 21):
        y0 = 50 + i * s
        fam.append(f"M-20 {f(y0 + 70 * 0.57735)}L120 {f(y0 - 70 * 0.57735)}")
        fam.append(f"M-20 {f(y0 - 70 * 0.57735)}L120 {f(y0 + 70 * 0.57735)}")
    for i in range(-10, 11):
        x0 = 50 + i * s * 0.866
        fam.append(f"M{f(x0)} -10V110")
    L.append(f'<g clip-path="url(#cm-clip)"><path d="{"".join(fam)}" {lf}/></g>')
    L.append(f'<path d="M{P(H["top"])}L{P(H["ur"])}L{P(H["lr"])}L{P(H["bot"])}'
             f'L{P(H["ll"])}L{P(H["ul"])}ZM{P(H["ul"])}L50 50L{P(H["ur"])}M50 50V92" {ln}/>')
    L.append(f'<path d="M50 2V98" stroke="var(--cs-signal,#FF6A1A)" stroke-width=".4" '
             f'stroke-dasharray="2 1.2"/>')
    cnt = model_counter()
    L.append('<path d="M' + "L".join(P(p) for p in cnt) + f'Z" {ln} stroke-dasharray="1 .8"/>')
    for k in ("top", "ur", "lr", "bot", "ll", "ul", "c"):
        x, y = H[k]
        L.append(f'<rect x="{f(x - .9)}" y="{f(y - .9)}" width="1.8" height="1.8" '
                 f'fill="var(--bg,#fff)" stroke="var(--cs-line,#2F6FED)" stroke-width=".3"/>')
    defs = '<defs><clipPath id="cm-clip"><rect x="0" y="0" width="100" height="100"/></clipPath></defs>'
    return defs + "".join(L)


def construction_monolith():
    W, Ht = 100 * PHI, 100.0
    split = W - Ht
    r = Ht / PHI ** 2
    L = []
    ln = 'stroke="var(--cs-line,#9A7444)" stroke-width=".35" fill="none"'
    lf = 'stroke="var(--cs-faint,#9A7444)" stroke-width=".25" fill="none" opacity=".6"'
    L.append(f'<rect x="0" y="0" width="{f(W)}" height="{f(Ht)}" {ln}/>')
    # golden subdivision: square | golden rectangle | ...
    s2 = split - split / PHI
    L.append(f'<path d="M{f(split)} -8V{f(Ht + 8)}M0 {f(split)}H{f(split)}'
             f'M{f(s2)} {f(split)}V{f(Ht)}M-8 50H{f(W + 8)}" {lf}/>')
    # golden spiral quarter-arcs
    L.append(f'<path d="M{f(split)} 0A{f(Ht)} {f(Ht)} 0 0 1 {f(W)} {f(Ht)}" {lf}/>')
    L.append(f'<path d="M{f(split)} 0A{f(split)} {f(split)} 0 0 0 0 {f(split)}" {lf}/>')
    L.append(f'<path d="M0 {f(split)}A{f(Ht - split)} {f(Ht - split)} 0 0 0 {f(Ht - split)} {f(Ht)}" {lf}/>')
    L.append(f'<circle cx="{f(split)}" cy="50" r="{f(r)}" {ln}/>')
    L.append(f'<path d="M{f(split)} 50L{f(split + r * .8)} {f(50 - r * .6)}" {ln}/>')
    for (x, y) in [(split, 50), (split, 50 - r), (split, 50 + r), (split + r, 50),
                   (0, 0), (W, Ht), (split, 0), (split, Ht)]:
        L.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.1" fill="var(--cs-line,#9A7444)"/>')
    return "".join(L)


# --------------------------------------------------------------------------
def main():
    os.makedirs(BUILD_DIR, exist_ok=True)
    sprite = []
    meta = {}
    for key, D in DIRS.items():
        out_dir = os.path.join(LOGO_DIR, D["slug"])
        os.makedirs(out_dir, exist_ok=True)
        base = f"davinci-{key.lower()}-{D['name']}"
        for mode in ("light", "dark"):
            c = D[mode]
            inner, w, h = D["sym"](c)
            pad = 8 if key != "C" else 10
            with open(os.path.join(out_dir, f"{base}-symbol-{mode}.svg"), "w") as fh:
                fh.write(svg_doc(inner, (0, 0, w, h), f"DAVINCI {key} symbol", pad))
            inner, w, h = D["sym"](c, small=True)
            with open(os.path.join(out_dir, f"{base}-symbol-small-{mode}.svg"), "w") as fh:
                fh.write(svg_doc(inner, (0, 0, w, h), f"DAVINCI {key} symbol (≤32px master)", pad))
            for layout in ("horizontal", "stacked"):
                inner, vb = build_lockup(key, c, layout)
                p = vb[3] * 0.12
                with open(os.path.join(out_dir, f"{base}-{layout}-{mode}.svg"), "w") as fh:
                    fh.write(svg_doc(inner, vb, f"DAVINCI {key} {layout} lockup", p))
        # sprite for the page (CSS variable colours)
        c = D["var"]
        inner, w, h = D["sym"](c)
        sprite.append(f'<symbol id="{key}-sym" viewBox="0 0 {f(w)} {f(h)}">{inner}</symbol>')
        inner, w, h = D["sym"](c, small=True)
        sprite.append(f'<symbol id="{key}-sym-s" viewBox="0 0 {f(w)} {f(h)}">{inner}</symbol>')
        meta[key] = {"sym": [w, h]}
        for layout in ("horizontal", "stacked"):
            inner, vb = build_lockup(key, c, layout)
            sprite.append(f'<symbol id="{key}-{layout}" viewBox="{" ".join(f(v) for v in vb)}">'
                          f'{inner}</symbol>')
            meta[key][layout] = [round(v, 2) for v in vb]
        for wk, (inner, vb) in wordmark_symbols(key, c).items():
            sprite.append(f'<symbol id="{key}-wm-{wk}" viewBox="{" ".join(f(v) for v in vb)}">'
                          f'{inner}</symbol>')
            meta[key][f"wm-{wk}"] = [round(v, 2) for v in vb]
    cons = {"A": (construction_codex(), "0 0 100 100"),
            "B": (construction_model(), "0 0 100 100"),
            "C": (construction_monolith(), f"0 0 {f(100 * PHI)} 100")}
    for k, (inner, vb) in cons.items():
        sprite.append(f'<symbol id="{k}-cons" viewBox="{vb}" overflow="visible">{inner}</symbol>')
    with open(os.path.join(BUILD_DIR, "sprite.svg"), "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" '
                 'style="position:absolute" aria-hidden="true">' + "".join(sprite) + "</svg>")
    with open(os.path.join(BUILD_DIR, "meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print("logos built:", json.dumps(meta))


if __name__ == "__main__":
    main()
