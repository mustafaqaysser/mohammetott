#!/usr/bin/env python3
"""Assembles the complete DAVINCI identity package into one ZIP.

  node tools/export.js <tmp>/export
  python3 tools/package.py <tmp>/export <outDir>
"""
import io
import json
import os
import shutil
import sys
import zipfile

import img2pdf
from PIL import Image
from pypdf import PdfReader, PdfWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_page import DIRS, cmyk, rgb  # noqa: E402

EXPORT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "dist"))
NAME = "DAVINCI-Brand-Identity"
PKG = os.path.join(OUT, NAME)
SLUG = {"A": "A-codex", "B": "B-model", "C": "C-monolith"}

SECTIONS = {
    "01-cover": "الغلاف · Cover", "02-brief": "الموجز · Brief", "03-concept": "الفكرة · Concept",
    "07-compare": "مقارنة وتوصية · Comparison & recommendation", "08-next": "الخطوات التالية · Next steps",
}
BLOCK_T = ["الافتتاحية · Opener", "بناء الشعار · Logo construction", "الشعار الرئيسي · Primary lockup",
           "الرمز والأحجام · Symbol & sizes", "الألوان · Colour", "الخطوط · Typography",
           "التطبيقات · Applications", "الخلاصة · Rationale"]


def section_title(stem):
    if stem in SECTIONS:
        return None, SECTIONS[stem]
    parts = stem.split("-")              # 04-a-codex-3-symbol
    k = parts[1].upper()
    D = DIRS[k]
    return f"{k} — {D['en']} · {D['ar']}", BLOCK_T[int(parts[3])]


def build_pdf(dst):
    book = os.path.join(EXPORT, "book")
    files = sorted(f for f in os.listdir(book) if f.endswith(".jpg"))
    layout = img2pdf.get_fixed_dpi_layout_fun((192, 192))
    raw = img2pdf.convert([os.path.join(book, f) for f in files], layout_fun=layout)
    reader = PdfReader(io.BytesIO(raw))
    w = PdfWriter()
    for p in reader.pages:
        w.add_page(p)
    parents = {}
    for i, f in enumerate(files):
        chapter, title = section_title(f[:-4])
        if chapter:
            if chapter not in parents:
                parents[chapter] = w.add_outline_item(chapter, i)
            w.add_outline_item(title, i, parent=parents[chapter])
        else:
            w.add_outline_item(title, i)
    w.add_metadata({"/Title": "DAVINCI · دافنشي — Brand Identity", "/Author": "DAVINCI Engineering Consultancy",
                    "/Subject": "Brand identity exploration — three directions"})
    w.page_mode = "/UseOutlines"
    with open(dst, "wb") as fh:
        w.write(fh)
    return len(files)


def palettes(dst):
    os.makedirs(dst, exist_ok=True)
    data, css, txt = {}, [":root {"], []
    for k, D in DIRS.items():
        data[k] = {"direction": f"{D['en']} / {D['ar']}", "colours": []}
        txt.append(f"{k} — {D['en']} · {D['ar']}\n" + "-" * 48)
        css.append(f"  /* {k} — {D['en']} */")
        for n, a, h, p, role in D["palette"]:
            R, G, B = rgb(h)
            C, M, Y, K = cmyk(h)
            data[k]["colours"].append({"name": n, "name_ar": a, "hex": h.upper(), "rgb": [R, G, B],
                                       "cmyk": [C, M, Y, K], "usage_percent": p, "role": role})
            var = n.lower().replace(" ", "-")
            css.append(f"  --{k.lower()}-{var}: {h.upper()};")
            txt.append(f"{n:<15} {a:<16} HEX {h.upper()}  RGB {R:>3} {G:>3} {B:>3}  "
                       f"CMYK {C:>3} {M:>3} {Y:>3} {K:>3}  {p:>2}%  {role}")
        txt.append("")
    css.append("}")
    json.dump(data, open(os.path.join(dst, "davinci-palettes.json"), "w"), ensure_ascii=False, indent=2)
    open(os.path.join(dst, "davinci-palettes.css"), "w").write("\n".join(css) + "\n")
    open(os.path.join(dst, "davinci-palettes.txt"), "w").write(
        "DAVINCI · دافنشي — Colour palettes\nCMYK values are starting points for coated stock; confirm with a press proof.\n\n"
        + "\n".join(txt))
    # swatch sheets
    for k, D in DIRS.items():
        pal = D["palette"]
        W, H = 2400, 900
        img = Image.new("RGB", (W, H), "#FFFFFF")
        x = 0
        for n, a, h, p, role in pal:
            w_ = round(W * p / 100) if (n, a, h, p, role) != pal[-1] else W - x
            img.paste(Image.new("RGB", (w_, H), h), (x, 0))
            x += w_
        img.save(os.path.join(dst, f"davinci-{k.lower()}-{D['en'].lower()}-palette-proportions.png"))


def fonts_doc(dst):
    os.makedirs(dst, exist_ok=True)
    lines = ["# الخطوط · Typography", "",
             "جميع الخطوط من Google Fonts وبرخصة SIL Open Font License — مجانية للاستخدام التجاري.",
             "All typefaces are Google Fonts under the SIL Open Font License — free for commercial use.", ""]
    for k, D in DIRS.items():
        lines.append(f"## {k} — {D['en']} · {D['ar']}")
        for fam, role in D["type"]:
            lines.append(f"- **{fam}** — {role} — https://fonts.google.com/specimen/{fam.replace(' ', '+')}")
        lines.append("")
    lines += ["## Frame of the presentation", "- IBM Plex Sans / IBM Plex Sans Arabic / IBM Plex Mono", "",
              "قواعد: العربية دائماً من اليمين لليسار، ولا تُباعد حروفها أبداً. الاسم يُكتب «دافنشي» فقط.",
              "Rules: Arabic is always right-to-left and never letter-spaced. The name is spelled «دافنشي» only."]
    open(os.path.join(dst, "fonts.md"), "w").write("\n".join(lines) + "\n")


def readme(dst, pages):
    t = f"""# DAVINCI · دافنشي — الهوية البصرية الكاملة / Complete brand identity

مكتب دافنشي للاستشارات الهندسية — استكشاف الهوية البصرية بثلاثة اتجاهات كاملة.
DAVINCI Engineering Consultancy — brand identity exploration, three complete directions.

| | الاتجاه · Direction | الأنسب لـ · Best for |
|---|---|---|
| A | الدفتر · Codex | الفلل والمنازل الفاخرة والتصميم المعماري · Villas, luxury homes, architecture |
| B | النموذج · Model — **موصى به · recommended** | المطوّرون والمقاولون والجهات الحكومية وBIM · Developers, contractors, government, BIM |
| C | الكتلة · Monolith | مطوّرو العقارات الراقية · High-end real-estate developers |

## محتويات الحزمة · Contents

| المجلد · Folder | المحتوى · What's inside |
|---|---|
| `01_Identity-Book/DAVINCI-Identity-Book.pdf` | كتاب الهوية كاملاً ({pages} صفحة) مع فهرس — Full identity book ({pages} pages) with bookmarks |
| `01_Identity-Book/DAVINCI-Presentation.html` | العرض التفاعلي (يُفتح في المتصفح، يحتاج إنترنت للخطوط) — Interactive presentation (open in a browser; needs internet for fonts) |
| `02_Logos/<A,B,C>/SVG` | الشعارات بصيغة متجهة، النصوص محوّلة لمسارات — Vector logos, type outlined |
| `02_Logos/<A,B,C>/PDF` | للطباعة والمطابع — For print shops (vector) |
| `02_Logos/<A,B,C>/PNG` | خلفية شفافة 512 / 1024 / 2048 — Transparent PNG |
| `02_Logos/<A,B,C>/favicon` | أيقونات الموقع والتطبيق 16–512 + favicon.ico — Web & app icons |
| `03_Colours` | الألوان HEX / RGB / CMYK بصيغ JSON و CSS و TXT + لوحات النسب — Palettes + proportion sheets |
| `04_Typography/fonts.md` | الخطوط وروابطها وقواعد الاستخدام — Typefaces, links, rules |
| `05_Mockups` | التطبيقات بدقة عالية: لوحة الموقع، بطاقة العمل، تقرير الدفعة، إنستغرام، الورق الرسمي، الخوذة والسترة + المقارنة — High-res application mockups + comparison |
| `06_Screenshots` | لقطات كل الأقسام: سطح المكتب 1440 والجوال 375 — Every section, desktop & mobile |
| `PLAN.md` | الهندسة الدقيقة لبناء كل رمز — Exact geometry of each symbol |

## أنواع الشعار · Logo versions

- **symbol** — الرمز وحده · symbol only
- **symbol-small** — نسخة الأحجام الصغيرة (32 بكسل وأقل) · small-size master (≤ 32 px)
- **horizontal** — أفقي: DAVINCI | الرمز | دافنشي · bilingual horizontal lockup
- **stacked** — عمودي · stacked lockup
- **light** — للخلفيات الفاتحة · for light backgrounds
- **dark** — للخلفيات الداكنة (شفاف بألوان فاتحة؛ ملف PDF بخلفية داكنة للمعاينة) · for dark backgrounds

## ملاحظات · Notes

- بيانات الاتصال والأسماء والمشروع في النماذج افتراضية (0770 000 0000 ، davinci-eng.iq) — Contact details, names and project in the mockups are placeholders.
- قيم CMYK نقطة بداية؛ تُعتمد بعد بروفة طباعة — CMYK values are starting points; confirm with a press proof.
- الخطوة التالية: اختيار اتجاه واحد ← جولة تطوير ← دليل الهوية النهائي وتسليم الملفات.
  Next: choose one direction → refinement round → final guidelines and file delivery.
"""
    open(dst, "w").write(t)


def main():
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)
    d1 = os.path.join(PKG, "01_Identity-Book")
    os.makedirs(d1)
    pages = build_pdf(os.path.join(d1, "DAVINCI-Identity-Book.pdf"))
    shutil.copy(os.path.join(ROOT, "index.html"), os.path.join(d1, "DAVINCI-Presentation.html"))

    for k, slug in SLUG.items():
        dst = os.path.join(PKG, "02_Logos", slug)
        shutil.copytree(os.path.join(ROOT, "logos", slug), os.path.join(dst, "SVG"))
        for sub in ("PDF", "PNG", "favicon"):
            shutil.copytree(os.path.join(EXPORT, "logos", slug, sub), os.path.join(dst, sub))
        fav = os.path.join(dst, "favicon")
        src = Image.open(os.path.join(fav, "favicon-64.png"))
        src.save(os.path.join(fav, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    palettes(os.path.join(PKG, "03_Colours"))
    fonts_doc(os.path.join(PKG, "04_Typography"))
    shutil.copytree(os.path.join(EXPORT, "mockups"), os.path.join(PKG, "05_Mockups"))
    shutil.copytree(os.path.join(ROOT, "screenshots"), os.path.join(PKG, "06_Screenshots"))
    shutil.copy(os.path.join(ROOT, "PLAN.md"), os.path.join(PKG, "PLAN.md"))
    readme(os.path.join(PKG, "README.md"), pages)

    zpath = os.path.join(OUT, f"{NAME}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, _, fs in os.walk(PKG):
            for fn in sorted(fs):
                full = os.path.join(dp, fn)
                z.write(full, os.path.relpath(full, OUT))
    print(zpath, round(os.path.getsize(zpath) / 1e6, 1), "MB;", "PDF pages:", pages)


if __name__ == "__main__":
    main()
