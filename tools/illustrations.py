"""Hand-built SVG illustrations for the DAVINCI presentation.

- iso_building(): one isometric residential massing, rendered in five styles:
    'codex'  — sepia line drawing with red-chalk overshoot construction lines
    'model'  — section plane: left half wireframe, right half solid
    'mono'   — monolithic shaded mass with cast shadow
    'draft'  — pure wireframe (the "before")
    'built'  — finished, shaded and glazed (the "after")
- qr_path(): a real QR code as one SVG path.
- mirror_script(): abstract mirror-writing texture (not real text).
"""
import math
import random

import qrcode

COS30 = math.cos(math.radians(30))
SIN30 = 0.5


def f(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- geometry
BOXES = [
    # (x0, y0, z0, x1, y1, z1)
    (0.0, 0.0, 0.0, 8.0, 5.0, 1.3),     # podium
    (0.7, 0.6, 1.3, 7.3, 4.4, 6.1),     # main block (5 floors)
    (1.6, 1.2, 6.1, 5.2, 3.8, 6.9),     # rooftop pavilion
]
FLOORS = [1.3 + 0.96 * i for i in range(1, 5)]


def proj(p, s=10.0):
    x, y, z = p
    return ((x - y) * COS30 * s, (x + y) * SIN30 * s - z * s)


def faces(box):
    x0, y0, z0, x1, y1, z1 = box
    return {
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "left": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
    }


def edges(box, hidden=False):
    x0, y0, z0, x1, y1, z1 = box
    vis = [
        ((x0, y0, z1), (x1, y0, z1)), ((x1, y0, z1), (x1, y1, z1)),
        ((x1, y1, z1), (x0, y1, z1)), ((x0, y1, z1), (x0, y0, z1)),
        ((x1, y0, z0), (x1, y0, z1)), ((x1, y1, z0), (x1, y1, z1)),
        ((x0, y1, z0), (x0, y1, z1)),
        ((x1, y0, z0), (x1, y1, z0)), ((x1, y1, z0), (x0, y1, z0)),
    ]
    hid = [
        ((x0, y0, z0), (x0, y0, z1)), ((x0, y0, z0), (x1, y0, z0)),
        ((x0, y0, z0), (x0, y1, z0)),
    ]
    return hid if hidden else vis


def facade_lines(box_i):
    """Floor lines + window mullions on the main block's two visible faces."""
    x0, y0, z0, x1, y1, z1 = BOXES[box_i]
    L = []
    for z in FLOORS:
        L.append(((x1, y0, z), (x1, y1, z)))
        L.append(((x0, y1, z), (x1, y1, z)))
    for i in range(1, 6):
        y = y0 + (y1 - y0) * i / 6
        L.append(((x1, y, z0), (x1, y, z1)))
    for i in range(1, 9):
        x = x0 + (x1 - x0) * i / 9
        L.append(((x, y1, z0), (x, y1, z1)))
    return L


def _pts(poly, ox, oy, s):
    return " ".join(f"{f(proj(p, s)[0] + ox)},{f(proj(p, s)[1] + oy)}" for p in poly)


def _line(a, b, ox, oy, s, ext=0.0):
    (ax, ay), (bx, by) = proj(a, s), proj(b, s)
    if ext:
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy) or 1
        ax, ay = ax - dx / n * ext, ay - dy / n * ext
        bx, by = bx + dx / n * ext, by + dy / n * ext
    return f"M{f(ax + ox)} {f(ay + oy)}L{f(bx + ox)} {f(by + oy)}"


def _hull(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def shadow_poly(box, ld=(0.95, -0.35)):
    x0, y0, z0, x1, y1, z1 = box
    pts = []
    for x in (x0, x1):
        for y in (y0, y1):
            pts.append((x, y))
            pts.append((x + ld[0] * z1, y + ld[1] * z1))
    return [(x, y, 0) for x, y in _hull(pts)]


# viewBox for the building (s=10): computed once
def _bounds(s=10.0):
    xs, ys = [], []
    for b in BOXES:
        for fc in faces(b).values():
            for p in fc:
                X, Y = proj(p, s)
                xs.append(X)
                ys.append(Y)
    return min(xs), min(ys), max(xs), max(ys)


def iso_building(style, c, s=10.0, pad=14, uid="b", ground=True):
    """Return a complete <svg> element string.  c = colour dict."""
    x0, y0, x1, y1 = _bounds(s)
    ox, oy = -x0 + pad, -y0 + pad
    W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    if style in ("mono", "built"):
        W += 34
    out = []
    sw = c.get("sw", 0.7)

    def polys(fill_map, stroke=None, stroke_w=0.0, extra=""):
        r = []
        for b in BOXES:
            for k in ("left", "right", "top"):
                fill = fill_map[k]
                st = f' stroke="{stroke}" stroke-width="{f(stroke_w)}" stroke-linejoin="round"' if stroke else ""
                r.append(f'<polygon points="{_pts(faces(b)[k], ox, oy, s)}" fill="{fill}"{st}{extra}/>')
        return "".join(r)

    def solid(fill_map, mull, mull_w, mull_op, edge=None, edge_w=0.0):
        r = []
        for bi, b in enumerate(BOXES):
            for k in ("left", "right", "top"):
                r.append(f'<polygon points="{_pts(faces(b)[k], ox, oy, s)}" fill="{fill_map[k]}"/>')
            if bi == 1:
                r.append(facade(mull, mull_w, mull_op))
            if edge:
                d = "".join(_line(a, bb, ox, oy, s) for a, bb in edges(b))
                r.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{f(edge_w)}" '
                         f'stroke-linejoin="round"/>')
        return "".join(r)

    def wire(color, w, hidden_color=None, ext=0.0, cls=""):
        d = "".join(_line(a, b, ox, oy, s, ext) for bx in BOXES for a, b in edges(bx))
        r = f'<path class="{cls}" d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" stroke-linecap="round" pathLength="1"/>' if cls else \
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" stroke-linecap="round"/>'
        if hidden_color:
            dh = "".join(_line(a, b, ox, oy, s) for bx in BOXES for a, b in edges(bx, True))
            r += (f'<path d="{dh}" fill="none" stroke="{hidden_color}" stroke-width="{f(w * .7)}" '
                  f'stroke-dasharray="1.6 1.6"/>')
        return r

    def facade(color, w, op=1.0):
        d = "".join(_line(a, b, ox, oy, s) for a, b in facade_lines(1))
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" opacity="{op}"/>'

    if ground and style in ("mono", "built"):
        sh = "".join(f'<polygon points="{_pts(shadow_poly(b), ox, oy, s)}"/>' for b in BOXES)
        out.append(f'<g fill="{c.get("shadow", "#000")}" opacity="{c.get("shadow_op", .22)}">{sh}</g>')
    if ground:
        gx = [proj((-2, 7, 0), s), proj((10.5, 7, 0), s), proj((10.5, -2, 0), s)]
        out.append(f'<path d="M{f(gx[0][0] + ox)} {f(gx[0][1] + oy)}L{f(gx[1][0] + ox)} {f(gx[1][1] + oy)}'
                   f'L{f(gx[2][0] + ox)} {f(gx[2][1] + oy)}" fill="none" stroke="{c.get("ground", c.get("line", "#999"))}" '
                   f'stroke-width="{f(sw * .6)}" opacity=".5"/>')

    if style == "codex":
        # red-chalk construction overshoot, then a light wash, then sepia ink
        out.append(f'<g opacity=".55">{wire(c["chalk"], sw * .55, ext=7)}</g>')
        out.append(polys({"left": c["wash"], "right": c["wash2"], "top": c["paper"]}))
        out.append(facade(c["ink"], sw * .45, .7))
        out.append(wire(c["ink"], sw * 1.1, hidden_color=c["chalk"]))
    elif style == "draft":
        out.append(wire(c["line"], sw, hidden_color=c["line"]))
        out.append(facade(c["line"], sw * .5, .6))
    elif style == "built":
        out.append(solid({"left": c["left"], "right": c["right"], "top": c["top"]},
                         c["mull"], sw * .7, .9, c["edge"], sw * .5))
    elif style == "mono":
        out.append(solid({"left": c["left"], "right": c["right"], "top": c["top"]},
                         c["mull"], sw * .35, .55))
    elif style == "model":
        mid = W / 2
        out.append(f'<defs><clipPath id="{uid}-L"><rect x="0" y="0" width="{f(mid)}" height="{f(H)}"/></clipPath>'
                   f'<clipPath id="{uid}-R"><rect x="{f(mid)}" y="0" width="{f(W - mid)}" height="{f(H)}"/></clipPath></defs>')
        out.append(f'<g clip-path="url(#{uid}-R)">'
                   + solid({"left": c["left"], "right": c["right"], "top": c["top"]},
                           c["mull"], sw * .6, .8) + '</g>')
        out.append(f'<g clip-path="url(#{uid}-L)">' + wire(c["line"], sw, hidden_color=c["line"])
                   + facade(c["line"], sw * .45, .7) + '</g>')
        out.append(f'<path d="M{f(mid)} 2V{f(H - 2)}" stroke="{c["plane"]}" stroke-width="{f(sw * .9)}" '
                   f'stroke-dasharray="4 2.5"/>')
    return (f'<svg class="iso iso-{style}" viewBox="0 0 {f(W)} {f(H)}" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{"".join(out)}</svg>')


# ---------------------------------------------------------------- concept
def concept_svg():
    """Large animated 'drawing → model → mass' stage for section 03.

    Uses classes animated by CSS: .cg (grid), .ce (edges, pathLength=1),
    .cf (faces), .cs (shadow), .cl (labels)."""
    s = 15.0
    x0, y0, x1, y1 = _bounds(s)
    pad = 40
    ox, oy = -x0 + pad + 30, -y0 + pad + 10
    W, H = x1 - x0 + 2 * pad + 90, y1 - y0 + 2 * pad + 40
    out = []
    # iso grid on the ground plane
    g = []
    for i in range(-3, 13):
        g.append(_line((i, -3, 0), (i, 9, 0), ox, oy, s))
    for j in range(-3, 10):
        g.append(_line((-3, j, 0), (13, j, 0), ox, oy, s))
    out.append(f'<path class="cg" d="{"".join(g)}" fill="none" stroke="currentColor" stroke-width=".5"/>')
    sh = "".join(f'<polygon points="{_pts(shadow_poly(b), ox, oy, s)}"/>' for b in BOXES)
    out.append(f'<g class="cs" fill="currentColor">{sh}</g>')
    fills = {"left": "var(--cf-left)", "right": "var(--cf-right)", "top": "var(--cf-top)"}
    fp = []
    for bi, b in enumerate(BOXES):
        for k in ("left", "right", "top"):
            fp.append(f'<polygon class="cf cf-{bi}" points="{_pts(faces(b)[k], ox, oy, s)}" fill="{fills[k]}"/>')
    out.append("".join(fp))
    fl = "".join(_line(a, b, ox, oy, s) for a, b in facade_lines(1))
    out.append(f'<path class="cfl" d="{fl}" fill="none" stroke="var(--cf-mull)" stroke-width=".6"/>')
    # edges: one path per box so they can be staggered
    for bi, b in enumerate(BOXES):
        d = "".join(_line(a, bb, ox, oy, s, 6) for a, bb in edges(b))
        out.append(f'<path class="ce ce-{bi}" d="{d}" pathLength="1" fill="none" stroke="currentColor" '
                   f'stroke-width="1.1" stroke-linecap="round"/>')
    return (f'<svg class="concept-svg" viewBox="0 0 {f(W)} {f(H)}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="A construction line draws a building, which becomes a solid mass">'
            f'{"".join(out)}</svg>')


# ---------------------------------------------------------------- QR
def qr_path(data, color="currentColor", quiet=0):
    q = qrcode.QRCode(border=quiet, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(data)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    d = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                start = x
                while x < n and row[x]:
                    x += 1
                d.append(f"M{start} {y}h{x - start}v1h{start - x}z")
            else:
                x += 1
    return (f'<svg class="qr" viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" '
            f'shape-rendering="crispEdges" aria-label="QR code"><path d="{"".join(d)}" fill="{color}"/></svg>')


# ---------------------------------------------------------------- textures
def mirror_script(seed=7, lines=7, w=300, color="currentColor", op=0.18):
    """Abstract, mirror-written looking strokes — loops and ligatures that
    evoke Leonardo's hand without being legible text."""
    rnd = random.Random(seed)
    out = []
    y = 12
    for _ in range(lines):
        x = 4
        d = [f"M{x} {y}"]
        while x < w - 20:
            step = rnd.uniform(5, 11)
            amp = rnd.uniform(2.5, 6.5)
            if rnd.random() < 0.18:      # word gap
                x += rnd.uniform(6, 12)
                d.append(f"M{f(x)} {f(y)}")
                continue
            if rnd.random() < 0.25:      # loop (like l / b ascender)
                d.append(f"c{f(step * .2)} {f(-amp * 2.4)} {f(step * .9)} {f(-amp * 2.4)} {f(step * .6)} 0")
            else:
                d.append(f"q{f(step / 2)} {f(-amp * rnd.choice([1, -0.6]))} {f(step)} 0")
            x += step * (0.6 if d[-1].startswith("c") else 1)
        out.append(f'<path d="{"".join(d)}"/>')
        y += 16
    return (f'<svg class="mirror" viewBox="0 0 {w} {y}" preserveAspectRatio="none" aria-hidden="true">'
            f'<g transform="translate({w} 0) scale(-1 1)" fill="none" stroke="{color}" stroke-width=".7" '
            f'stroke-linecap="round" opacity="{op}">{"".join(out)}</g></svg>')
