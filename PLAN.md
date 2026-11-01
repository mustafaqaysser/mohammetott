# DAVINCI · دافنشي — Identity Exploration Plan

Central idea for all three directions: **from drawing to reality** — a thin
construction line that becomes a solid mass. Every symbol below is built so
that part of it is still *drawing* (hairline, wireframe, joint) and part of it
is already *mass*. All geometry is hand-constructed in SVG (`tools/build_logos.py`);
wordmarks are set in the specified Google Fonts and converted to outlines for
the exported files.

Golden ratio φ = 1.618034. 1/φ = 0.618034. 1/φ² = 0.381966.

---

## A — CODEX «الدفتر»

**Metaphor.** A page from Leonardo's notebook: a square, a circle, a few
compass-free construction lines in red chalk, and one confident stroke of ink.

**Grid.** 100 × 100 unit field. Construction square `(10,10)–(90,90)`.
Inscribed circle `O(50,50) r = 40`. Second circle `r = 40/φ = 24.72`.

**Symbol geometry.**
- *Mass (sepia ink)* — the letter **د**: a heavy bowl that is the right half
  of the ring between `r = 40` and `r = 24.72` (stroke weight `15.28 = 40 − 40/φ`).
  - Top arm: from the vertical axis `x = 50` back to `x = 25.28` (= 50 − 24.72),
    cut on a qalam-like slant so the terminal is calligraphic, not mechanical.
  - Base: runs all the way left to the square's edge `x = 10` — the long
    baseline of a written dal, which is longer than its head.
- *Drawing (sanguine red)* — a hairline stem on the square's left edge
  `x = 10`, from the top of the square down into the base. With the stem the
  form reads as Latin **D**; without it (or at 16 px, where hairlines vanish)
  it reads as Arabic **د**. The open corner at top-left is the line the hand
  has not yet closed.
- Construction layer (shown in the presentation, not in the clean mark):
  square, both circles, axes, diagonals, φ-division marks, radius callouts.

**Wordmark.** دافنشي in Amiri Bold; DAVINCI in Cormorant Garamond SemiBold,
tracked +180; descriptor in Amiri / IBM Plex Mono.

---

## B — MODEL «النموذج» (recommended)

**Metaphor.** A BIM viewer with a section plane: one half of the object is
still a wireframe drawing, the other half is already a solid model.

**Grid.** 100 × 100. Isometric cube, circumradius `R = 42`, centred at `(50,50)`.
Vertices: top `(50, 8)`, UR `(86.37, 29)`, LR `(86.37, 71)`, bottom `(50, 92)`,
LL `(13.63, 71)`, UL `(13.63, 29)`, front-top `(50, 50)`.

**Symbol geometry.**
- *Section plane* — the vertical line `x = 50` cuts the cube in two.
- *Drawing half (left)* — wireframe in ink-navy: top→UL→LL→bottom, UL→centre,
  centre→bottom. At large sizes one hidden edge (centre→LL) is dashed.
- *Mass half (right)* — solid blueprint blue: polygon top, UR, LR, bottom.
  Its outline is already an angular **D**: tall straight stem on the section
  plane, bowl made of the cube's right edges.
- *Negative space* — the counter of that D is an inset of the half-hexagon by
  11 units: `(61, 27.05) (75.37, 35.35) (75.37, 64.65) (61, 72.95)`. The ring
  that remains — right wall plus sloped floor — is also the shape of a Kufic
  **د** (upright, turning into a base).
- *Small-size master (≤ 32 px)* — wire strokes thickened from 3.2 to 7 units,
  dashed edge removed, counter kept. Tested at 16 px.

**Wordmark.** دافنشي in IBM Plex Sans Arabic SemiBold; DAVINCI in Space
Grotesk Bold tracked +140; descriptors in IBM Plex Mono / Plex Sans Arabic.
Signal orange `#FF6A1A` is never in the logo — it is reserved for “clash
detected” moments (≤ 5 % of any layout).

---

## C — MONOLITH «الكتلة»

**Metaphor.** A single block of stone, split once. Light enters through the
cut.

**Grid.** Portrait golden rectangle `100 × 161.8`.

**Symbol geometry.**
- *Two masses* — left mass width `100/φ² = 38.2`, right mass width
  `100/φ = 61.8`, separated by a 2.4-unit joint (the only “drawn line”).
- *One arc* — a semicircle `r = 38.2`, centred on the joint at golden height
  `y = 161.8/φ = 100`, bites into the right mass.
- *Void* — the space between the straight face of the left mass and the arc is
  a **D** (flat stem + round bowl); its bowl, read alone, is **د**. Above and
  below the void the joint continues as a hairline of light.
- Proportions: void height 76.4 (= 2 × 38.2), right-mass wall at the void 23.6
  (= 100/φ³).

**Wordmark.** دافنشي in Alexandria SemiBold; DAVINCI in Syne SemiBold
tracked +320 (wide, quiet, architectural); descriptors Alexandria Light / Syne.

---

## Lockups (all directions)

- **Horizontal** — bilingual axis: `DAVINCI + English descriptor | symbol |
  دافنشي + Arabic descriptor`. Each text block aligns toward the symbol; the
  Arabic block sits on the right because Arabic is read first.
- **Stacked** — symbol, دافنشي, DAVINCI, Arabic descriptor, English descriptor,
  centred.
- Exports: `logos/<dir>/` → symbol, horizontal, stacked, each light + dark,
  all text outlined.

## Review checklist

1. Render each symbol at 16 / 32 / 64 / 512 px. Is it still a D/د at 16 px?
2. Could it be mistaken for an existing mark (e.g. generic cube logos)? The
   section-plane split in B is the ownable part — keep it obvious.
3. Arabic spelling is exactly «دافنشي»; never tracked; always RTL.
