# DAVINCI · دافنشي — Brand Identity Exploration

Three identity directions for **مكتب دافنشي للاستشارات الهندسية**, presented as a
single scrolling page for the client to choose one.

| | Direction | Best for |
|---|---|---|
| A | **Codex · الدفتر** — Leonardo's notebook: sepia ink, red chalk, ivory | Villas, luxury homes, architecture |
| B | **Model · النموذج** — section plane: half wireframe, half solid *(recommended)* | Developers, contractors, government, BIM |
| C | **Monolith · الكتلة** — one golden block, split once; light through a D-shaped void | High-end real-estate developers |

## Deliverables

- `index.html` — the presentation. Self-contained (inline CSS, JS, SVG); only Google Fonts load remotely. Open it in any browser.
- `logos/<A-codex|B-model|C-monolith>/` — symbol, horizontal and stacked lockups, light and dark, as SVG with all type converted to outlines. `symbol-small` is the ≤ 32 px master. `-dark` files are for dark backgrounds (transparent, light-coloured artwork).
- `screenshots/desktop` (1440 px) and `screenshots/mobile` (375 px) — every section.
- `PLAN.md` — the geometry of each symbol.

## Rebuilding

```sh
pip install fonttools uharfbuzz qrcode
python3 tools/build_logos.py   # geometry + outlined wordmarks → logos/ and tools/build/
python3 tools/build_page.py    # → index.html
node tools/screenshot.js       # → screenshots/ (needs Playwright)
```

Contact details in the mockups are placeholders (phone `0770 000 0000`, domain `davinci-eng.iq`, names and project).
