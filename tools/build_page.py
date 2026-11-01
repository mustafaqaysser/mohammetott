#!/usr/bin/env python3
"""Builds the self-contained index.html presentation.

  python3 tools/build_logos.py   # logos + sprite
  python3 tools/build_page.py    # index.html

Everything (CSS, JS, SVG) is inlined. Only Google Fonts are loaded remotely.
"""
import json
import os

from illustrations import concept_svg, iso_building, mirror_script, qr_path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
META = json.load(open(os.path.join(TOOLS, "build", "meta.json")))
SPRITE = open(os.path.join(TOOLS, "build", "sprite.svg")).read()
CSS = open(os.path.join(TOOLS, "src", "styles.css")).read()
JS = open(os.path.join(TOOLS, "src", "app.js")).read()

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Alexandria:wght@200;300;400;600"
         "&family=Amiri:ital,wght@0,400;0,700;1,400"
         "&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500"
         "&family=IBM+Plex+Mono:wght@400;500"
         "&family=IBM+Plex+Sans+Arabic:wght@200;300;400;500;600"
         "&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;1,300"
         "&family=Space+Grotesk:wght@400;500;700"
         "&family=Syne:wght@400;500;600;700"
         "&display=swap")

AR_DIGITS = str.maketrans("0123456789,.%", "٠١٢٣٤٥٦٧٨٩٬٫٪")


def ad(s):
    """Western → Arabic-Indic digits."""
    return str(s).translate(AR_DIGITS)


def phone_ar():
    """Arabic-digit phone. LRMs stop bidi rule N1 from reversing the groups."""
    return '<bdi dir="ltr" class="ph">' + "\u200e ".join(ad(g) for g in ("0770", "000", "0000")) + "</bdi>"


def iqd(n):
    return ad(f"{n:,}") + " د.ع"


def AR(text, cls="", tag="p"):
    return f'<{tag} class="ar {cls}" lang="ar" dir="rtl">{text}</{tag}>'


def EN(text, cls="", tag="p"):
    return f'<{tag} class="en {cls}" lang="en" dir="ltr">{text}</{tag}>'


def logo(key, kind, cls=""):
    vb = META[key][kind] if kind not in ("sym",) else [0, 0] + META[key]["sym"]
    if kind == "sym":
        w, h = META[key]["sym"]
    else:
        w, h = vb[2], vb[3]
    ref = {"sym": f"{key}-sym", "sym-s": f"{key}-sym-s"}.get(kind, f"{key}-{kind}")
    return (f'<svg class="lg lg-{kind} {cls}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="DAVINCI {kind}"><use href="#{ref}" width="{w}" height="{h}"/></svg>')


def sym(key, cls="", small=False):
    w, h = META[key]["sym"]
    ref = f"{key}-sym-s" if small else f"{key}-sym"
    return (f'<svg class="lg lg-sym {cls}" viewBox="0 0 {w} {h}" role="img" aria-label="DAVINCI symbol">'
            f'<use href="#{ref}" width="{w}" height="{h}"/></svg>')


def wm(key, which, cls=""):
    vb = META[key][f"wm-{which}"]
    return (f'<svg class="lg lg-wm-{which} {cls}" viewBox="0 0 {vb[2]} {vb[3]}" aria-hidden="true">'
            f'<use href="#{key}-wm-{which}" width="{vb[2]}" height="{vb[3]}"/></svg>')


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cmyk(h):
    r, g, b = (v / 255 for v in rgb(h))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(round(v * 100) for v in (c, m, y, k))


# ==========================================================================
# Direction data
# ==========================================================================
DIRS = {
    "A": dict(
        key="A", cls="dir-a", id="dir-a", letter="A", en="Codex", ar="الدفتر",
        idea_en="Leonardo’s notebooks. Sepia ink and red-chalk construction lines on ivory paper — the craft of drawing before building.",
        idea_ar="دفاتر ليوناردو: خطوط إنشاء دقيقة بالحبر البنّي والطباشير الأحمر على ورق عاجي — حِرفة الرسم قبل البناء.",
        mood_en="Heritage · craft · refined", mood_ar="إرث · حِرفة · رُقيّ",
        best_en="Villas, luxury homes, architectural design", best_ar="الفلل، المنازل الفاخرة، التصميم المعماري",
        palette=[("Ivory", "عاجي", "#F2EBDD", 60, "Paper, every background"),
                 ("Sepia ink", "حبر بنّي", "#3B2A1E", 25, "Logo, text, line drawings"),
                 ("Sanguine red", "طباشير أحمر", "#A8432F", 8, "Construction lines, notes, the stem"),
                 ("Graphite", "رصاصي", "#6E6A63", 7, "Secondary text, dimensions")],
        type=[("Amiri", "Arabic · headline & body"), ("Cormorant Garamond", "English · headline & body"),
              ("IBM Plex Mono", "Annotations & dimensions")],
        win_en="Wins the private homeowner and the villa client: it feels personal, crafted and trustworthy — an atelier, not a contractor.",
        win_ar="يكسب صاحب البيت وعميل الفلل: هوية شخصية، مصنوعة باليد، وجديرة بالثقة — مَرسم، لا مقاول.",
        trade_en="Trade-off: speaks less to BIM, government and large developers; the heritage tone can read as ‘architecture only’.",
        trade_ar="المقابل: أضعف في الحديث عن BIM والمشاريع الحكومية والمطوّرين الكبار؛ وقد تُفهم كمكتب تصميم معماري فقط.",
    ),
    "B": dict(
        key="B", cls="dir-b", id="dir-b", letter="B", en="Model", ar="النموذج",
        idea_en="The blueprint becoming a 3D model. A section plane cuts the object: one half is still a drawing, the other is already built.",
        idea_ar="المخطط يتحوّل إلى نموذج ثلاثي الأبعاد. مستوى قطع يشطر الكتلة: نصفها ما زال رسماً، ونصفها بُني فعلاً.",
        mood_en="Technical · precise · institutional", mood_ar="تقني · دقيق · مؤسسي",
        best_en="Developers, contractors, government, BIM projects", best_ar="المطوّرون، المقاولون، الجهات الحكومية، مشاريع BIM",
        palette=[("White", "أبيض", "#F7F8FA", 45, "Paper, drawing field"),
                 ("Ink navy", "كحلي", "#0E1621", 30, "Text, wireframe, dark surfaces"),
                 ("Blueprint", "أزرق المخطط", "#2F6FED", 15, "The solid half, data, links"),
                 ("Concrete", "خرساني", "#C9CCCF", 7, "Grids, dividers, secondary"),
                 ("Signal orange", "برتقالي الإنذار", "#FF6A1A", 3, "Only for “clash detected”")],
        type=[("IBM Plex Sans Arabic", "Arabic · headline & body"), ("Space Grotesk", "English · headline & body"),
              ("IBM Plex Mono", "Data, layers, dimensions")],
        win_en="Wins developers, contractors and government: it looks like the BIM process it sells, scales from favicon to hoarding, and earns institutional trust.",
        win_ar="يكسب المطوّرين والمقاولين والجهات الحكومية: يشبه عملية BIM التي يبيعها، ويعمل من أيقونة المتصفح حتى لوحة الموقع، ويبني ثقة مؤسسية.",
        trade_en="Trade-off: less warmth for a homeowner building one house — the copy and the reports must carry the human tone.",
        trade_ar="المقابل: دفء أقل لصاحب بيت واحد — النصوص والتقارير يجب أن تحمل النبرة الإنسانية.",
    ),
    "C": dict(
        key="C", cls="dir-c", id="dir-c", letter="C", en="Monolith", ar="الكتلة",
        idea_en="The material itself — concrete, travertine, bronze. One block of stone, split once; light enters through the cut.",
        idea_ar="المادة نفسها — خرسانة، ترافرتين، برونز. كتلة واحدة شُقّت مرة واحدة، والضوء يدخل من الشق.",
        mood_en="Luxurious · silent · cinematic", mood_ar="فاخر · صامت · سينمائي",
        best_en="High-end real-estate developers", best_ar="مطوّرو العقارات الراقية",
        palette=[("Charcoal", "فحمي", "#141312", 50, "Surfaces, the mass"),
                 ("Travertine", "ترافرتين", "#E4DCCF", 35, "Paper, light, text on dark"),
                 ("Stone grey", "رمادي حجري", "#8A857D", 10, "Secondary text, details"),
                 ("Bronze", "برونزي", "#9A7444", 5, "Light, accents, hairlines")],
        type=[("Alexandria", "Arabic · headline, body & figures"), ("Syne", "English · headline & body")],
        win_en="Wins the premium developer selling high-end units: it feels like the building’s own material — silent, expensive, cinematic.",
        win_ar="يكسب المطوّر الراقي الذي يبيع وحدات فاخرة: كأنها مادة المبنى نفسه — صامتة، ثمينة، سينمائية.",
        trade_en="Trade-off: says little about supervision, money control or BIM; for a homeowner it can feel distant and expensive.",
        trade_ar="المقابل: لا تقول الكثير عن الإشراف وضبط المال وBIM؛ وقد تبدو بعيدة ومكلفة لصاحب البيت.",
    ),
}

ISO = {
    "A": dict(style="codex", c=dict(chalk="#A8432F", wash="#E8DCC6", wash2="#DCCAAE", paper="#F5EFE3",
                                    ink="#3B2A1E", ground="#6E6A63", sw=.8)),
    "B": dict(style="model", c=dict(line="#F7F8FA", left="#2F6FED", right="#1D4FBF", top="#8DB0F8",
                                    mull="#0E1621", plane="#FF6A1A", ground="#C9CCCF", sw=.8)),
    "C": dict(style="mono", c=dict(left="#2E2B28", right="#1A1817", top="#CFC3B0", mull="#9A7444",
                                   shadow="#000", shadow_op=.32, ground="#8A857D", sw=.8)),
}
ISO_LIGHT = {
    "A": ISO["A"],
    "B": dict(style="model", c=dict(line="#0E1621", left="#2F6FED", right="#1D4FBF", top="#8DB0F8",
                                    mull="#0E1621", plane="#FF6A1A", ground="#9AA3AE", sw=.8)),
    "C": dict(style="mono", c=dict(left="#3A3633", right="#1E1C1A", top="#E4DCCF", mull="#9A7444",
                                   shadow="#141312", shadow_op=.18, ground="#8A857D", sw=.8)),
}
BEFORE = {
    "A": dict(line="#3B2A1E", sw=.8),
    "B": dict(line="#8DB0F8", sw=.8),
    "C": dict(line="#9A7444", sw=.8),
}
AFTER = {
    "A": dict(left="#D8C7AA", right="#B79E7B", top="#F2EBDD", mull="#3B2A1E", edge="#3B2A1E",
              shadow="#3B2A1E", shadow_op=.18, sw=.8, ground="#6E6A63"),
    "B": dict(left="#E9EDF3", right="#B9C2CF", top="#FFFFFF", mull="#2F6FED", edge="#0E1621",
              shadow="#000", shadow_op=.3, sw=.8, ground="#4A5566"),
    "C": dict(left="#D9CEBD", right="#A99C88", top="#EFE8DD", mull="#141312", edge="#141312",
              shadow="#000", shadow_op=.35, sw=.6, ground="#8A857D"),
}

uid_counter = [0]


def iso(key, light=False, cls=""):
    uid_counter[0] += 1
    d = (ISO_LIGHT if light else ISO)[key]
    return iso_building(d["style"], d["c"], uid=f"i{uid_counter[0]}")


# ==========================================================================
# Shared content
# ==========================================================================
PROJECT = dict(
    ar_name="عمارة النخيل السكنية",
    en_name="Al-Nakheel Residential Building",
    ar_spec=f"سكنية · {ad(5)} طوابق + طابق تجاري · {ad(20)} شقة",
    en_spec="Residential · 5 floors + retail podium · 20 apartments",
    ar_owner="شركة بيت النخيل للتطوير العقاري",
    en_owner="Bait Al-Nakheel Real Estate Development",
    ar_loc="بغداد — المنصور، محلة ٦٠٣",
    en_loc="Al-Mansour, Baghdad",
    ar_permit=f"إجازة بناء رقم {ad(417)} / {ad(2026)}",
    en_permit="Building permit 417 / 2026",
    ar_dates=f"المباشرة: آذار {ad(2026)} — الإنجاز المتوقع: أيلول {ad(2027)}",
    en_dates="Start Mar 2026 — Completion Sep 2027",
)
QR = qr_path("DAVINCI | DVC-2026-014 | Al-Nakheel | BIM LOD 350 | 0770 000 0000")


# ==========================================================================
# Mockups
# ==========================================================================
def frame(inner, label_en, label_ar, cls=""):
    return (f'<figure class="mk-fig rv {cls}">{inner}'
            f'<figcaption><span class="en">{label_en}</span><span class="ar" lang="ar" dir="rtl">{label_ar}</span>'
            f'</figcaption></figure>')


def deco(key, where):
    """Direction-specific decorative layer."""
    if key == "A":
        if where == "card":
            return ('<svg class="dc dc-a-card" viewBox="0 0 85 55" preserveAspectRatio="none" aria-hidden="true">'
                    '<path d="M6 0V55M0 49H85M79 0V55M0 6H85" /></svg>')
        if where == "page":
            return mirror_script(seed=11, lines=8, w=300, color="#3B2A1E", op=.16)
    if key == "B" and where == "card":
        return '<div class="dc dc-grid"></div>'
    if key == "C" and where == "card":
        return '<div class="dc dc-noise"></div>'
    return ""


def card_front(key):
    D = DIRS[key]
    if key == "A":
        inner = (f'{deco("A", "card")}<div class="cf-a">{logo("A", "stacked")}</div>'
                 f'<span class="note n1">φ</span><span class="note n2">٨٥ × ٥٥</span>')
    elif key == "B":
        inner = (f'{deco("B", "card")}<div class="cf-b">{logo("B", "horizontal")}</div>'
                 f'<span class="tag t1">L-00 / IDENTITY</span><span class="tag t2">x 0.000 · y 0.000</span>')
    else:
        inner = (f'{deco("C", "card")}<div class="cf-c">{sym("C")}</div>'
                 f'<div class="cf-c-wm">{wm("C", "ar")}{wm("C", "en")}</div>')
    return f'<div class="mk card card-front {D["cls"]}-card"><div class="mk-in">{inner}</div></div>'


def card_back(key):
    D = DIRS[key]
    contact_ar = (f'<div class="cb-ar" lang="ar" dir="rtl"><b>م. علي حسن</b><span>مدير المشاريع</span>'
                  f'<span class="num">{phone_ar()}</span>'
                  f'<span>بغداد — المنصور، شارع ١٤ رمضان</span></div>')
    contact_en = ('<div class="cb-en"><b>Eng. Ali Hassan</b><span>Projects Director</span>'
                  '<span class="num">+964 770 000 0000</span><span class="num">ali@davinci-eng.iq</span></div>')
    s = sym(key, "cb-sym")
    return (f'<div class="mk card card-back {D["cls"]}-card cb"><div class="mk-in">'
            f'{s}{contact_en}{contact_ar}<div class="cb-rule"></div></div></div>')


def hoarding(key, compact=False):
    D = DIRS[key]
    bim = (f'<div class="bim"><span class="bim-k">BIM</span><span class="bim-v">LOD 350 · 0 CLASHES</span>'
           f'<span class="bim-ar" lang="ar" dir="rtl">نموذج منسّق — صفر تعارضات</span></div>')
    rows = [
        ("المالك", PROJECT["ar_owner"], "Owner", PROJECT["en_owner"]),
        ("الإشراف الهندسي", "مكتب دافنشي للاستشارات الهندسية", "Engineer", "DAVINCI Engineering Consultancy"),
        ("الموقع", PROJECT["ar_loc"], "Location", PROJECT["en_loc"]),
    ]
    info = "".join(
        f'<div class="hb-row"><div class="hb-ar" lang="ar" dir="rtl"><small>{a}</small><span>{b}</span></div>'
        f'<div class="hb-en"><small>{c}</small><span>{d}</span></div></div>' for a, b, c, d in rows)
    extra = ""
    if key == "A":
        extra = ('<span class="chalk c1">٣٫٢٠ م</span><span class="chalk c2">← ٢٠ شقة</span>'
                 '<svg class="dc hb-dim" viewBox="0 0 100 10" preserveAspectRatio="none"><path d="M2 5H98M2 1V9M98 1V9"/></svg>')
    if key == "B":
        extra = ('<span class="tag hb-t1">SECTION A–A · LEVEL +18.60</span>'
                 '<span class="tag hb-t2">GRID 1–8 / A–E</span>')
    return (f'<div class="mk hoarding {D["cls"]}-hb{" compact" if compact else ""}"><div class="mk-in">'
            f'<div class="hb-top">{logo(key, "horizontal", "hb-logo")}'
            f'<div class="hb-permit"><span lang="ar" dir="rtl">{PROJECT["ar_permit"]}</span>'
            f'<span>{PROJECT["en_permit"]}</span></div></div>'
            f'<div class="hb-main"><div class="hb-text">'
            f'<p class="hb-kicker ar" lang="ar" dir="rtl">مشروع قيد الإنشاء</p>'
            f'<h4 class="hb-name ar" lang="ar" dir="rtl">{PROJECT["ar_name"]}</h4>'
            f'<p class="hb-name-en">{PROJECT["en_name"]}</p>'
            f'<p class="hb-spec ar" lang="ar" dir="rtl">{PROJECT["ar_spec"]}</p>'
            f'<div class="hb-info">{info}</div></div>'
            f'<div class="hb-art">{iso(key)}<p class="hb-art-cap ar" lang="ar" dir="rtl">المبنى الذي سترونه هنا — بُني رقمياً أولاً</p></div></div>'
            f'<div class="hb-foot"><div class="hb-dates"><span lang="ar" dir="rtl">{PROJECT["ar_dates"]}</span>'
            f'<span>{PROJECT["en_dates"]}</span></div>{bim}'
            f'<div class="hb-qr">{QR}<span lang="ar" dir="rtl">امسح لمشاهدة النموذج</span></div>'
            f'<div class="hb-phone num">{phone_ar()}</div></div>{extra}'
            f'</div></div>')


def report(key):
    D = DIRS[key]
    paid = 7
    bars = "".join(f'<i class="{"p" if i < paid else ("c" if i == paid else "")}"></i>' for i in range(12))
    extra = ""
    if key == "B":
        extra = '<div class="rp-clash"><i></i><span>1 clash resolved before pour · L3 slab</span></div>'
    if key == "A":
        extra = '<span class="chalk rp-note">✓ موثّق بالوصولات</span>'
    return (f'<div class="mk a4 report {D["cls"]}-rp"><div class="mk-in">'
            f'<div class="rp-head">{logo(key, "horizontal", "rp-logo")}<span class="rp-ref num">DVC-2026-014 / R07</span></div>'
            f'<div class="rp-title"><p class="ar rp-k" lang="ar" dir="rtl">تقرير الدفعة</p>'
            f'<p class="rp-no num">{ad("7")}</p>'
            f'<p class="ar rp-proj" lang="ar" dir="rtl">{PROJECT["ar_name"]} — {PROJECT["ar_loc"]}</p>'
            f'<p class="rp-en">Payment progress report No. 07 · Oct 2026</p></div>'
            f'<div class="rp-big"><div class="rp-pct"><span class="num">{ad("46")}</span><em>٪</em>'
            f'<small lang="ar" dir="rtl">نسبة الإنجاز الفعلي</small></div>'
            f'<div class="rp-bar"><i style="width:46%"></i></div></div>'
            f'<div class="rp-money" lang="ar" dir="rtl">'
            f'<div><small>المصروف حتى الآن</small><b class="num">{iqd(414_000_000)}</b></div>'
            f'<div><small>المتبقّي</small><b class="num">{iqd(486_000_000)}</b></div>'
            f'<div><small>قيمة العقد</small><b class="num">{iqd(900_000_000)}</b></div>'
            f'<div><small>أتعاب المكتب (١٠٪ من المصروف)</small><b class="num">{iqd(41_400_000)}</b></div></div>'
            f'<div class="rp-inst"><p lang="ar" dir="rtl">الدفعة {ad(7)} من {ad(12)} · {iqd(72_000_000)}</p>'
            f'<div class="rp-bars">{bars}</div></div>{extra}'
            f'<div class="rp-foot"><span lang="ar" dir="rtl">كل دينار موثّق · كل مرحلة مصوّرة</span>'
            f'<span class="num">p. 01 / 18</span></div>'
            f'</div></div>')


def letterhead(key):
    D = DIRS[key]
    m = deco(key, "page") if key == "A" else ""
    return (f'<div class="mk a4 letter {D["cls"]}-lt"><div class="mk-in">{m}'
            f'<div class="lt-head">{logo(key, "horizontal", "lt-logo")}</div>'
            f'<div class="lt-body" lang="ar" dir="rtl">'
            f'<p class="lt-date num">بغداد في {ad("2026/11/01")}</p>'
            f'<p class="lt-to">السادة شركة بيت النخيل للتطوير العقاري المحترمون</p>'
            f'<p class="lt-subj">م/ تقرير الإشراف الشهري — عمارة النخيل السكنية</p>'
            f'<p>تحية طيبة…</p>'
            f'<p>نرفق لكم تقرير الإشراف لشهر تشرين الأول {ad(2026)}، ويتضمّن نسبة الإنجاز الفعلية '
            f'({ad("46%")})، وكشف المصروفات للدفعة السابعة، ونتائج فحص التعارضات في النموذج الرقمي قبل صبّ سقف الطابق الثالث.</p>'
            f'<p>لم تُسجَّل أي تعارضات مفتوحة بين الأعمال الإنشائية والمعمارية والميكانيكية، وجميع المبالغ المصروفة موثّقة بالوصولات والصور.</p>'
            f'<p>مع التقدير.</p>'
            f'<p class="lt-sign">م. علي حسن<br><small>مدير المشاريع</small></p></div>'
            f'<div class="lt-foot"><span lang="ar" dir="rtl">بغداد — المنصور، شارع ١٤ رمضان · {phone_ar()}</span>'
            f'<span>14 Ramadan St., Al-Mansour, Baghdad · davinci-eng.iq</span></div>'
            f'</div></div>')


def insta(key):
    D = DIRS[key]
    before = iso_building("draft", BEFORE[key], uid=f"bf{key}")
    after = iso_building("built", AFTER[key], uid=f"af{key}")
    return (f'<div class="ig {D["cls"]}-ig">'
            f'<div class="ig-bar"><span class="ig-av">{sym(key, small=True)}</span>'
            f'<span class="ig-h"><b>davinci.eng</b><small>Baghdad, Iraq</small></span><span class="ig-dots">···</span></div>'
            f'<div class="mk sq ig-post"><div class="mk-in">'
            f'<div class="ig-before">{before}</div><div class="ig-after">{after}</div>'
            f'<span class="ig-l ig-l1" lang="ar" dir="rtl">قبل · النموذج</span>'
            f'<span class="ig-l ig-l2" lang="ar" dir="rtl">بعد · الواقع</span>'
            f'<span class="ig-split"></span>'
            f'<span class="ig-mark">{sym(key, small=True)}</span></div></div>'
            f'<div class="ig-cap" lang="ar" dir="rtl"><b>davinci.eng</b> رأيناها كاملة في النموذج قبل أن يُصبّ أول متر من الخرسانة. '
            f'فيلا الجادرية — {ad(2026)}.</div></div>')


def avatar(key):
    D = DIRS[key]
    return (f'<div class="avs {D["cls"]}-av"><div class="av av-l">{sym(key, small=False)}</div>'
            f'<div class="av av-m">{sym(key, small=True)}</div><div class="av av-s">{sym(key, small=True)}</div></div>')


HELMET_SHELL = "M30 104C28 58 64 22 114 20C162 18 192 50 196 96L197 104Z"
HELMET_RIB = "M70 40C94 26 136 24 162 36"
HELMET_RIB2 = "M58 58C86 40 140 36 176 52"
HELMET_PEAK = "M150 98C182 95 210 98 218 107C217 112 208 115 196 115H150Z"
HELMET_RIM = "M24 98H198V112H30C22 112 20 104 24 98Z"


def helmet(key):
    pal = {"A": ("#F4EEE2", "#D9CCB4", "#3B2A1E", "#A8432F"),
           "B": ("#FFFFFF", "#D3D9E2", "#0E1621", "#2F6FED"),
           "C": ("#34302C", "#141312", "#E4DCCF", "#9A7444")}[key]
    shell, shade, ink, acc = pal
    W, H = META[key]["horizontal"][2], META[key]["horizontal"][3]
    lw = 104
    return (f'<svg class="helmet {DIRS[key]["cls"]}-hel" viewBox="0 0 224 132" role="img" aria-label="Safety helmet">'
            f'<defs><linearGradient id="hg{key}" x1="0" y1="0" x2=".35" y2="1">'
            f'<stop offset="0" stop-color="{shell}"/><stop offset="1" stop-color="{shade}"/></linearGradient>'
            f'<radialGradient id="hs{key}" cx=".35" cy=".25" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="116" cy="124" rx="98" ry="5" fill="#000" opacity=".18"/>'
            f'<path d="{HELMET_PEAK}" fill="{shade}"/>'
            f'<path d="{HELMET_SHELL}" fill="url(#hg{key})"/>'
            f'<path d="{HELMET_SHELL}" fill="url(#hs{key})"/>'
            f'<path d="{HELMET_RIB}" fill="none" stroke="{shell}" stroke-width="6" stroke-linecap="round" opacity=".9"/>'
            f'<path d="{HELMET_RIB}" fill="none" stroke="{shade}" stroke-width="1.2" stroke-linecap="round" transform="translate(0 3)"/>'
            f'<path d="{HELMET_RIM}" fill="{shade}"/>'
            f'<path d="M30 101H196" stroke="{acc}" stroke-width="2.4"/>'
            f'<g style="--lg-ink:{ink};--lg-text:{ink};--lg-sub:{ink};--lg-wire:{ink};--lg-solid:{acc};'
            f'--lg-accent:{acc};--lg-mass:{ink};--lg-mass2:{ink}">'
            f'<svg x="{113 - lw / 2}" y="56" width="{lw}" height="{lw * H / W:.2f}" viewBox="0 0 {W} {H}">'
            f'<use href="#{key}-horizontal" width="{W}" height="{H}"/></svg></g></svg>')


VEST_FRONT = ("M56 8H82L100 92L118 8H144C146 40 160 64 178 74L182 228H18L22 74C40 64 54 40 56 8Z")
VEST_BACK = ("M56 8C76 18 124 18 144 8C146 40 160 64 178 74L182 228H18L22 74C40 64 54 40 56 8Z")


def vest(key):
    pal = {"A": ("#A8432F", "#8F3726", "#F2EBDD"),
           "B": ("#0E1621", "#070C13", "#F7F8FA"),
           "C": ("#1E1C1A", "#121110", "#E4DCCF")}[key]
    body, dark, ink = pal
    strip = "#D9DCE0"
    sw, sh = META[key]["sym"]
    wa = META[key]["wm-ar"]
    st = (f'--lg-ink:{ink};--lg-text:{ink};--lg-sub:{ink};--lg-wire:{ink};--lg-solid:{"#2F6FED" if key == "B" else ink};'
          f'--lg-accent:{ink if key == "A" else "#9A7444"};--lg-mass:{ink};--lg-mass2:{ink}')
    if key == "A":
        st = f'--lg-ink:{ink};--lg-text:{ink};--lg-accent:{ink};--lg-sub:{ink}'
    if key == "B":
        st = f'--lg-wire:{ink};--lg-solid:#2F6FED;--lg-text:{ink};--lg-sub:{ink}'
    if key == "C":
        st = f'--lg-mass:{ink};--lg-mass2:{ink};--lg-text:{ink};--lg-sub:{ink}'
    sym_h = 22
    sym_w = sym_h * sw / sh

    def body_svg(path, front):
        cid = f"vc{key}{'f' if front else 'b'}"
        y1, y2 = (156, 190) if front else (176, 204)
        bands = (f'<rect x="0" y="{y1}" width="200" height="12" fill="{strip}"/>'
                 f'<rect x="0" y="{y2}" width="200" height="12" fill="{strip}"/>')
        if front:
            bands += (f'<path d="M62 8L74 156" stroke="{strip}" stroke-width="12"/>'
                      f'<path d="M138 8L126 156" stroke="{strip}" stroke-width="12"/>')
            mark = (f'<g style="{st}"><svg x="{156 - sym_w / 2:.1f}" y="98" width="{sym_w:.1f}" height="{sym_h}" '
                    f'viewBox="0 0 {sw} {sh}"><use href="#{key}-sym" width="{sw}" height="{sh}"/></svg></g>')
            zip_ = f'<path d="M100 92V228" stroke="{dark}" stroke-width="1.6"/>'
        else:
            bands += (f'<path d="M30 74L170 156M170 74L30 156" stroke="{strip}" stroke-width="10" opacity="0"/>')
            lw, lh = META[key]["stacked"][2], META[key]["stacked"][3]
            ww = 64 if key != "C" else 74
            mark = (f'<g style="{st}"><svg x="{100 - ww / 2}" y="50" width="{ww}" height="{ww * lh / lw:.1f}" '
                    f'viewBox="0 0 {lw} {lh}"><use href="#{key}-stacked" width="{lw}" height="{lh}"/></svg></g>')
            zip_ = ""
        return (f'<svg class="vest" viewBox="0 0 200 236" role="img" aria-label="Safety vest {"front" if front else "back"}">'
                f'<defs><clipPath id="{cid}"><path d="{path}"/></clipPath></defs>'
                f'<path d="{path}" fill="{body}"/><g clip-path="url(#{cid})">{bands}{zip_}</g>'
                f'{mark}</svg>')
    return (f'<div class="vests {DIRS[key]["cls"]}-vest">{body_svg(VEST_FRONT, True)}{body_svg(VEST_BACK, False)}</div>')


def ppe(key):
    return (f'<div class="mk-ppe {DIRS[key]["cls"]}-ppe">'
            f'<div class="ppe-helmet">{helmet(key)}</div>{vest(key)}</div>')


# ==========================================================================
# Chapter blocks
# ==========================================================================
def blk(num, en, ar, body, cls=""):
    return (f'<div class="blk {cls}"><header class="blk-h rv"><span class="blk-n num">{num}</span>'
            f'<h3 class="en">{en}</h3><h3 class="ar" lang="ar" dir="rtl">{ar}</h3></header>{body}</div>')


ANNOT = {
    "A": ('<g class="ann ann-a">'
          '<text x="91.5" y="8.6">A</text><text x="91.5" y="94">B</text><text x="5" y="94">C</text>'
          '<text x="70" y="24" class="it">r = 40</text>'
          '<text x="62" y="70" class="it">r = 40 / φ</text>'
          '<text x="58" y="98.5" class="it">φ</text>'
          '<text x="14.5" y="44" class="it" transform="rotate(-90 14.5 44)">la linea — stem</text>'
          '<text x="26" y="7.2" class="it">qalam cut</text>'
          '</g>'),
    "B": ('<g class="ann ann-b">'
          '<text x="51.5" y="4.6">SECTION PLANE x = 50</text>'
          '<text x="2" y="27">UL</text><text x="89" y="27">UR</text><text x="2" y="76">LL</text><text x="89" y="76">LR</text>'
          '<text x="64" y="52">COUNTER −11</text>'
          '<text x="2" y="98">R = 42 · ISO 30°</text><text x="70" y="98">LOD 350</text>'
          '</g>'),
    "C": ('<g class="ann ann-c">'
          '<text x="2" y="-3">161.8 = 100 · φ</text>'
          '<text x="30" y="106">61.8</text><text x="108" y="106">100</text>'
          '<text x="104" y="22">r = 38.2</text>'
          '<text x="64" y="53">VOID</text>'
          '</g>'),
}


def construction(key):
    w, h = META[key]["sym"]
    pad = 8
    vb = f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"
    cons = (f'<svg class="cons-svg" viewBox="{vb}" role="img" aria-label="Logo construction">'
            f'<use href="#{key}-cons" width="{w}" height="{h}"/>'
            f'<g class="cons-ghost"><use href="#{key}-sym" width="{w}" height="{h}"/></g>{ANNOT[key]}</svg>')
    clean = f'<svg class="cons-svg" viewBox="{vb}">{f"<use href=\"#{key}-sym\" width=\"{w}\" height=\"{h}\"/>"}</svg>'
    notes = {
        "A": [("Square + inscribed circle", "مربّع ودائرة محاطة"),
              ("Counter radius = 40 / φ", "نصف قطر الفراغ = ٤٠ ÷ φ"),
              ("Stem: the line not yet closed", "الساق: الخط الذي لم يُغلق بعد"),
              ("Reads د — and D with the stem", "تُقرأ «د» — و D مع الساق")],
        "B": [("Isometric cube, R = 42", "مكعب أيزومتري، نصف القطر ٤٢"),
              ("Section plane at x = 50", "مستوى القطع عند المحور"),
              ("Left: wireframe · right: solid", "يسار: رسم سلكي · يمين: كتلة"),
              ("Counter inset 11 → D / د", "فراغ داخلي بإزاحة ١١ ← D / د")],
        "C": [("Golden block 161.8 × 100", "كتلة ذهبية ١٦١٫٨ × ١٠٠"),
              ("Split at 61.8 : 100", "شقّ عند ٦١٫٨ : ١٠٠"),
              ("One arc, r = 100 / φ²", "قوس واحد، نصف القطر ١٠٠ ÷ φ²"),
              ("The void between masses = D", "الفراغ بين الكتلتين = D")],
    }[key]
    ol = "".join(f'<li><span class="en">{e}</span><span class="ar" lang="ar" dir="rtl">{a}</span></li>' for e, a in notes)
    return (f'<div class="cons rv"><div class="cons-panel cons-grid">{cons}<span class="cons-tag">01 — construction</span></div>'
            f'<div class="cons-panel cons-clean">{clean}<span class="cons-tag">02 — logo</span></div>'
            f'<ol class="cons-notes">{ol}</ol></div>')


def lockups(key):
    return (f'<div class="lk-grid">'
            f'<div class="lk lk-h lt rv">{logo(key, "horizontal")}<span class="lk-tag">Horizontal · أفقي</span></div>'
            f'<div class="lk lk-s lt rv">{logo(key, "stacked")}<span class="lk-tag">Stacked · عمودي</span></div>'
            f'<div class="lk lk-h dk rv">{logo(key, "horizontal")}<span class="lk-tag">Horizontal · on dark</span></div>'
            f'<div class="lk lk-s dk rv">{logo(key, "stacked")}<span class="lk-tag">Stacked · on dark</span></div>'
            f'</div>')


def symbols(key):
    ladder = "".join(
        f'<div class="ld-i"><div class="ld-box" style="--s:{s}px">{sym(key, small=s <= 32)}</div><span class="num">{s}px</span></div>'
        for s in (64, 32, 16))
    return (f'<div class="sy-grid">'
            f'<div class="sy sy-l lt rv">{sym(key)}<span class="lk-tag">On light</span></div>'
            f'<div class="sy sy-d dk rv">{sym(key)}<span class="lk-tag">On dark</span></div>'
            f'<div class="sy-ladders rv"><div class="ld lt">{ladder}</div><div class="ld dk">{ladder}</div>'
            f'<div class="tab"><span class="tab-ic">{sym(key, small=True)}</span><span class="tab-t">DAVINCI — دافنشي</span><span class="tab-x">×</span></div>'
            f'<p class="sy-note">≤ 32px uses the small-size master: heavier strokes, simplified detail.</p></div>'
            f'</div>')


def palette(key):
    pal = DIRS[key]["palette"]
    bar = "".join(f'<i style="flex:{p};background:{h}" title="{n} {p}%"><span class="num">{p}%</span></i>' for n, a, h, p, r in pal)
    cards = ""
    for n, a, h, p, r in pal:
        R, G, B = rgb(h)
        C, M, Y, K = cmyk(h)
        lum = (0.2126 * R + 0.7152 * G + 0.0722 * B) / 255
        cards += (f'<div class="sw rv" style="--sw:{h};--sw-t:{"#111" if lum > .55 else "#fff"}">'
                  f'<div class="sw-chip"><span class="sw-pct num">{p}%</span></div>'
                  f'<div class="sw-meta"><b class="en">{n}</b><b class="ar" lang="ar" dir="rtl">{a}</b>'
                  f'<dl class="num"><dt>HEX</dt><dd>{h.upper()}</dd><dt>RGB</dt><dd>{R} {G} {B}</dd>'
                  f'<dt>CMYK</dt><dd>{C} {M} {Y} {K}</dd></dl><p>{r}</p></div></div>')
    return (f'<div class="pal"><div class="pal-bar rv">{bar}</div><div class="pal-cards">{cards}</div>'
            f'<p class="pal-note">Usage proportions across a typical set of applications. CMYK values are '
            f'starting points for coated stock — final values after a press proof.</p></div>')


SPEC = {
    "A": dict(ar_h="نرى مبناك قبل أن يُبنى", en_h="We see your building before it is built.",
              ar_b="كل خطّ في الرسم وعدٌ بشيء سيُبنى. نرسم بدقة، ونحسب كل دينار قبل أن يُصرف، ونسلّمك المبنى كما رأيته على الورق.",
              en_b="Every line in the drawing is a promise of something that will be built. We draw precisely, calculate every dinar before it is spent, and hand over the building exactly as you saw it on paper.",
              data="LVL +3.20 · AXIS B–4 · 1:50 · SHEET A-102"),
    "B": dict(ar_h="نرى مبناك قبل أن يُبنى", en_h="We see your building before it is built.",
              ar_b="نبني المشروع رقمياً بالكامل قبل أن يبدأ العمل في الموقع. نكتشف التعارضات ونحلّها في النموذج، لا في الخرسانة.",
              en_b="We build the entire project digitally before work starts on site. Clashes are found and solved in the model — not in the concrete.",
              data="LOD 350 · 1,284 ELEMENTS · 0 OPEN CLASHES · 46.0 %"),
    "C": dict(ar_h="نرى مبناك قبل أن يُبنى", en_h="We see your building before it is built.",
              ar_b="المبنى الجيد يبدأ بصمتٍ طويل وحسابٍ دقيق. نصمّم الكتلة والضوء والمادة، ونُشرف على كل مرحلة حتى تكتمل.",
              en_b="A good building begins with a long silence and an exact calculation. We design mass, light and material — and supervise every stage until it is complete.",
              data="46 % · 414,000,000 IQD · SEP 2027"),
}


def typography(key):
    S = SPEC[key]
    fam = DIRS[key]["type"]
    data_ar = {"A": f"منسوب +{ad('3.20')} · المحور ب–{ad(4)} · مقياس {ad('1:50')}",
               "B": f"{ad('1,284')} عنصراً · {ad(0)} تعارضات مفتوحة · {ad('46.0%')}",
               "C": f"{ad('46%')} · {iqd(414_000_000)} · أيلول {ad(2027)}"}[key]
    labels = "".join(f'<li><b>{n}</b><span>{r}</span></li>' for n, r in fam)
    return (f'<div class="ty rv"><ul class="ty-fams">{labels}</ul>'
            f'<div class="ty-cols"><div class="ty-col ty-ar" lang="ar" dir="rtl">'
            f'<span class="ty-l">عنوان</span><p class="ty-h">{S["ar_h"]}</p>'
            f'<span class="ty-l">نص</span><p class="ty-b">{S["ar_b"]}</p>'
            f'<span class="ty-l">بيانات</span><p class="ty-d">{data_ar}</p></div>'
            f'<div class="ty-col ty-en"><span class="ty-l">Headline</span><p class="ty-h">{S["en_h"]}</p>'
            f'<span class="ty-l">Body</span><p class="ty-b">{S["en_b"]}</p>'
            f'<span class="ty-l">Data</span><p class="ty-d">{S["data"]}</p></div></div>'
            f'<div class="ty-glyphs"><span class="ar" lang="ar" dir="rtl">ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي</span>'
            f'<span class="en">Aa Bb Cc Dd Ee Ff Gg 0123456789</span></div></div>')


def mockups(key):
    D = DIRS[key]
    return (f'<div class="mk-grid">'
            f'{frame(hoarding(key), "Site hoarding board · 3 × 2 m", "لوحة الموقع · ٣ × ٢ م", "g-hb")}'
            f'{frame(f"<div class=card-pair>{card_front(key)}{card_back(key)}</div>", "Business card · 85 × 55 mm · front & back", "بطاقة العمل · الوجه والظهر", "g-card")}'
            f'{frame(report(key), "Payment progress report · cover", "تقرير الدفعة · الغلاف", "g-rp")}'
            f'{frame(insta(key) + avatar(key), "Instagram · before / after + avatar", "إنستغرام · قبل / بعد + الصورة الشخصية", "g-ig")}'
            f'{frame(letterhead(key), "Letterhead · A4", "الورق الرسمي · A4", "g-lt")}'
            f'{frame(ppe(key), "Safety helmet & vest", "خوذة وسترة السلامة", "g-ppe")}'
            f'</div>')


def chapter(key):
    D = DIRS[key]
    rec = '<span class="rec">Recommended · موصى به</span>' if key == "B" else ""
    opener = (f'<div class="dir-open"><div class="wrap">'
              f'<div class="do-top rv"><span class="do-letter">{D["letter"]}</span>'
              f'<div class="do-names"><h2 class="en">{D["en"]}</h2><h2 class="ar" lang="ar" dir="rtl">{D["ar"]}</h2>{rec}</div></div>'
              f'<div class="do-art rv">{iso(key)}</div>'
              f'<div class="do-text rv">{AR(D["idea_ar"], "do-idea")}{EN(D["idea_en"], "do-idea")}'
              f'<dl class="do-meta"><div><dt>Mood · المزاج</dt><dd>{D["mood_en"]}<br><span lang="ar" dir="rtl">{D["mood_ar"]}</span></dd></div>'
              f'<div><dt>Best for · الأنسب لـ</dt><dd>{D["best_en"]}<br><span lang="ar" dir="rtl">{D["best_ar"]}</span></dd></div></dl></div>'
              f'</div></div>')
    k = D["letter"]
    body = (f'<div class="wrap">'
            f'{blk(k + ".1", "Logo construction", "بناء الشعار", construction(key))}'
            f'{blk(k + ".2", "Primary lockup", "الشعار الرئيسي", lockups(key))}'
            f'{blk(k + ".3", "Symbol & small sizes", "الرمز والأحجام الصغيرة", symbols(key))}'
            f'{blk(k + ".4", "Colour", "الألوان", palette(key))}'
            f'{blk(k + ".5", "Typography", "الخطوط", typography(key))}'
            f'{blk(k + ".6", "Applications", "التطبيقات", mockups(key))}'
            f'{blk(k + ".7", "Rationale", "الخلاصة", rationale(key))}'
            f'</div>')
    return f'<section class="dir {D["cls"]}" id="{D["id"]}" data-nav="{D["id"]}">{opener}{body}</section>'


def rationale(key):
    D = DIRS[key]
    return (f'<div class="rat rv"><div class="rat-win">{AR(D["win_ar"])}{EN(D["win_en"])}</div>'
            f'<div class="rat-trade">{AR(D["trade_ar"])}{EN(D["trade_en"])}</div></div>')


# ==========================================================================
# Page sections
# ==========================================================================
def cover():
    return f'''
<section class="cover" id="cover" data-nav="cover">
  <div class="wrap cover-grid">
    <div class="cv-meta rv">
      <span>Brand identity exploration</span><span>3 directions</span><span>Baghdad · November 2026</span><span>For client review</span>
    </div>
    <div class="cv-ar rv" lang="ar" dir="rtl">
      <p class="cv-k">مكتب دافنشي للاستشارات الهندسية</p>
      <h1 class="cv-title">دافنشي</h1>
      <p class="cv-sub">استكشاف الهوية البصرية — ثلاثة اتجاهات</p>
      <p class="cv-line">من الرسم إلى الواقع: نرى مبناك قبل أن يُبنى.</p>
    </div>
    <div class="cv-rule rv" aria-hidden="true"><i></i></div>
    <div class="cv-en rv">
      <p class="cv-k">DAVINCI Engineering Consultancy</p>
      <h1 class="cv-title">DAVINCI</h1>
      <p class="cv-sub">Brand identity exploration — three directions</p>
      <p class="cv-line">From drawing to reality: the office that sees your building before it is built.</p>
    </div>
    <ol class="cv-dirs rv">
      <li class="cv-a"><a href="#dir-a">{sym("A")}<span>A · Codex</span><span lang="ar" dir="rtl">الدفتر</span></a></li>
      <li class="cv-b"><a href="#dir-b">{sym("B")}<span>B · Model</span><span lang="ar" dir="rtl">النموذج</span></a></li>
      <li class="cv-c"><a href="#dir-c">{sym("C")}<span>C · Monolith</span><span lang="ar" dir="rtl">الكتلة</span></a></li>
    </ol>
  </div>
</section>'''


def brief():
    services = [
        ("إشراف وإدارة موقع", "المالك يدفع على أقساط، والمكتب يتعاقد مع الفرق ويديرها، ويأخذ نحو ١٠٪ من كل دفعة.",
         "Construction supervision & site management", "The owner pays in installments; the office hires and manages the crews and takes ~10 % of each payment."),
        ("المخططات المعمارية", "مخططات، واجهات، وكل ما يتعلق بالتصميم.",
         "Architectural drawings", "Plans, elevations — everything design-related."),
        ("الإشراف على المشاريع الكبيرة", "المجمّعات السكنية للمطوّرين العقاريين.",
         "Large-project supervision", "Residential complexes for developers."),
        ("BIM — جوهر المستقبل", "كل مشروع يُنمذج بالكامل ثلاثي الأبعاد (Revit، Navisworks)، وتُكتشف التعارضات وتُحلّ قبل البدء بالتنفيذ. العراق بدأ يشترط BIM في المشاريع الكبرى.",
         "BIM — the future core", "Every project fully modelled in 3D (Revit, Navisworks); clashes detected and solved before construction. Iraq is starting to require BIM on major projects."),
    ]
    sv = "".join(
        f'<li class="rv"><span class="num">0{i + 1}</span><div class="c-en">{EN(c, "sv-h")}{EN(d, "sv-b")}</div><div class="c-ar">{AR(a, "sv-h")}{AR(b, "sv-b")}</div></li>'
        for i, (a, b, c, d) in enumerate(services))
    aud = [
        ("صاحب البيت", "يخاف أن يُخدع ويخسر ماله.", "يحتاج أن يرى: أين ذهب كل دينار.",
         "Private homeowner", "Fears being cheated and losing money.", "Needs to see where every dinar went."),
        ("المقاول والمطوّر", "يخاف التأخير وأخطاء التصميم في الموقع.", "يحتاج أن يرى: مشروعاً محسوباً ومنسّقاً مسبقاً.",
         "Contractor / developer", "Fears delays and design errors on site.", "Needs to see a project calculated and coordinated in advance."),
        ("الجهات الحكومية والمشاريع الكبيرة", "تحتاج مصداقية مؤسسية والتزاماً بمعايير BIM.", "تحتاج أن ترى: نظاماً، لا أشخاصاً.",
         "Government / large projects", "Need institutional credibility and BIM compliance.", "Need to see a system, not individuals."),
    ]
    au = "".join(
        f'<li class="rv"><span class="num">0{i + 1}</span><div class="c-en">{EN(d, "au-h")}{EN(e + " " + f_, "au-b")}</div><div class="c-ar">{AR(a, "au-h")}{AR(b + " " + c, "au-b")}</div></li>'
        for i, (a, b, c, d, e, f_) in enumerate(aud))
    pers = [("دقيق، لا بارد", "Precise, not cold"), ("هادئ وواثق", "Calm and confident"),
            ("شفّاف", "Transparent"), ("سابق لزمنه", "Ahead of its time")]
    pe = "".join(f'<li class="rv">{AR(a)}{EN(b)}</li>' for a, b in pers)
    return f'''
<section class="brief" id="brief" data-nav="brief">
  <div class="wrap">
    <header class="sec-h rv"><span class="num">01</span><h2 class="en">The brief</h2><h2 class="ar" lang="ar" dir="rtl">الموجز</h2></header>
    <div class="br-client rv">
      <p class="lbl">Client · العميل</p>
      {AR("مكتب دافنشي للاستشارات الهندسية", "br-name")}
      {EN("An engineering office in Iraq — supervision, design and, increasingly, BIM. Arabic is the primary language of the brand.", "br-desc")}
    </div>
    <div class="br-grid">
      <div class="br-col"><p class="lbl rv">Services · الخدمات</p><ol class="br-sv">{sv}</ol></div>
      <div class="br-col"><p class="lbl rv">Audiences · الجمهور</p><ol class="br-au">{au}</ol></div>
    </div>
    <div class="br-pos rv">
      <p class="lbl">Positioning · التموضع</p>
      {AR("المكتب الذي يرى مبناك قبل أن يُبنى.", "br-quote")}
      {EN("The office that sees your building before it is built.", "br-quote")}
    </div>
    <div class="br-two">
      <div class="rv"><p class="lbl">Core promise · الوعد</p>{AR("أموالك محميّة، ومشروعك محسوب مسبقاً.", "br-promise")}{EN("Your money is protected. Your project is calculated in advance.", "br-promise")}</div>
      <div><p class="lbl rv">Personality · الشخصية</p><ul class="br-pers">{pe}</ul></div>
    </div>
    <div class="br-rules rv">
      <p class="lbl">Ground rules for all directions · قواعد ثابتة</p>
      <ul>
        <li>Every mark is drawn from geometry — no clip-art, no stock icons.</li>
        <li>Arabic first, always right-to-left, never letter-spaced. The name is spelled «دافنشي» — nothing else.</li>
        <li>No Mona Lisa, no Vitruvian Man, no yellow hard hat, no crane, no house-roof triangle.</li>
      </ul>
    </div>
  </div>
</section>'''


def concept():
    return f'''
<section class="concept" id="concept" data-nav="concept">
  <div class="wrap">
    <header class="sec-h rv"><span class="num">02</span><h2 class="en">The concept</h2><h2 class="ar" lang="ar" dir="rtl">الفكرة</h2></header>
    <div class="cc-head">
      {AR("من الرسم إلى الواقع", "cc-title rv")}
      {EN("From drawing to reality", "cc-title rv")}
    </div>
    <div class="cc-stage rv" id="cc-stage">
      {concept_svg()}
      <ol class="cc-steps">
        <li><span class="num">01</span><b lang="ar" dir="rtl">خط</b><span>Line</span></li>
        <li><span class="num">02</span><b lang="ar" dir="rtl">نموذج</b><span>Model</span></li>
        <li><span class="num">03</span><b lang="ar" dir="rtl">كتلة</b><span>Mass</span></li>
      </ol>
      <button class="cc-replay" type="button" aria-label="Replay animation">↻ Replay · إعادة</button>
    </div>
    <div class="cc-text">
      <div class="rv">{AR("رسم ليوناردو الآلة في دفتره قبل أن تُصنع. ودافنشي يبني المشروع رقمياً قبل أن يُبنى في الموقع.")}</div>
      <div class="rv">{EN("Leonardo drew the machine in his notebook before it was built. DAVINCI builds the project digitally before it is built on site.")}</div>
      <div class="rv cc-sig">{AR("خطّ إنشاء رفيع يتحوّل إلى كتلة صلبة — هذه الحركة هي توقيع الهوية في الاتجاهات الثلاثة.")}{EN("A thin construction line that becomes a solid mass — this movement is the signature of the identity in all three directions.")}</div>
    </div>
  </div>
</section>'''


def compare():
    cols = ""
    for key in ("A", "B", "C"):
        D = DIRS[key]
        cols += (f'<div class="cmp-col {D["cls"]} rv{" is-rec" if key == "B" else ""}">'
                 f'<p class="cmp-h"><span class="num">{D["letter"]}</span> {D["en"]} <span lang="ar" dir="rtl">{D["ar"]}</span>'
                 f'{"<em>Recommended</em>" if key == "B" else ""}</p>'
                 f'{hoarding(key, compact=True)}<div class="cmp-card">{card_front(key)}</div>'
                 f'<p class="cmp-best">{D["best_en"]}</p></div>')
    return f'''
<section class="compare" id="compare" data-nav="compare">
  <div class="wrap">
    <header class="sec-h rv"><span class="num">03</span><h2 class="en">Side by side</h2><h2 class="ar" lang="ar" dir="rtl">مقارنة</h2></header>
    <p class="cmp-intro rv">The same hoarding board and the same business card, in each direction.</p>
    <div class="cmp-grid">{cols}</div>
    <div class="cmp-rec rv">
      <p class="lbl">Our recommendation · توصيتنا</p>
      <h3 class="en">B — Model</h3><h3 class="ar" lang="ar" dir="rtl">ب — النموذج</h3>
      <div class="cmp-rec-text">
        {AR("نوصي بالاتجاه «النموذج» لأنه الوحيد الذي يُظهر ما يبيعه المكتب فعلاً: مشروع مبنيّ رقمياً قبل أن يُبنى. نصف الرمز رسمٌ ونصفه كتلة — وهذه هي القصة كاملة في شكل واحد يعمل من أيقونة ١٦ بكسل حتى لوحة الموقع. يمنح المطوّرين والجهات الحكومية الثقة المؤسسية التي يتطلبها اشتراط BIM، ويمنح صاحب البيت الشفافية عبر تقارير الدفعات الواضحة. نقترح أن نستعير من «الدفتر» دفء النبرة في النصوص، ومن «الكتلة» الهدوء والمساحة البيضاء في المواد الراقية.")}
        {EN("We recommend Model because it is the only direction that shows what the office actually sells: a project built digitally before it is built. Half of the symbol is drawing, half is mass — the whole story in one shape that works from a 16 px favicon to a 3 × 2 m site board. It gives developers and government the institutional confidence that BIM requirements demand, and gives the homeowner transparency through clear, data-led payment reports. From Codex we would borrow warmth of tone in the copy; from Monolith, the restraint and white space for premium materials.")}
      </div>
    </div>
  </div>
</section>'''


def next_steps():
    steps = [
        ("اختيار اتجاه واحد", "يختار العميل اتجاهاً واحداً — مع ملاحظاته.", "Choose one direction", "The client picks one direction, with comments."),
        ("جولة تطوير", "أسبوع واحد: ضبط الرمز والخطوط والألوان وفق الملاحظات.", "Refinement round", "One week: symbol, type and colour refined against feedback."),
        ("الدليل والتسليم", "دليل الهوية الكامل، ملفات الشعار (SVG، PDF، PNG)، قوالب اللوحات والتقارير والمراسلات، ومواصفات الخوذ والسترات.",
         "Guidelines & file delivery", "Full brand guidelines; logo files (SVG, PDF, PNG); templates for hoardings, reports and letters; PPE specifications."),
    ]
    st = "".join(f'<li class="rv"><span class="num">0{i + 1}</span>{AR(a, "ns-h")}{AR(b)}{EN(c, "ns-h")}{EN(d)}</li>'
                 for i, (a, b, c, d) in enumerate(steps))
    return f'''
<section class="next" id="next" data-nav="next">
  <div class="wrap">
    <header class="sec-h rv"><span class="num">04</span><h2 class="en">Next steps</h2><h2 class="ar" lang="ar" dir="rtl">الخطوات التالية</h2></header>
    <ol class="ns">{st}</ol>
    <div class="ns-end rv">
      {AR("اختر اتجاهاً — ونبدأ.", "ns-cta")}
      {EN("Pick one direction — and we begin.", "ns-cta")}
      <p class="ns-files">Logo files for all three directions are delivered with this presentation in <code>/logos/</code> — symbol, horizontal and stacked, light and dark, SVG with outlined type.</p>
    </div>
  </div>
  <footer class="foot wrap"><span>DAVINCI · دافنشي — Brand identity exploration</span><span class="num">2026</span></footer>
</section>'''


def nav():
    links = [("cover", "Cover", "الغلاف"), ("brief", "Brief", "الموجز"), ("concept", "Concept", "الفكرة"),
             ("dir-a", "A", "Codex"), ("dir-b", "B", "Model"), ("dir-c", "C", "Monolith"),
             ("compare", "Compare", "مقارنة"), ("next", "Next", "التالي")]
    a = "".join(f'<a href="#{i}" data-k="{i}"><span>{e}</span>{f"<small>{x}</small>" if i.startswith("dir") else ""}</a>'
                for i, e, x in links)
    return (f'<header class="nav" id="nav"><a class="nav-brand" href="#cover">DAVINCI</a>'
            f'<nav aria-label="Sections">{a}</nav></header>')


def texture_tokens():
    from urllib.parse import quote
    def noise(r, g, b, a, freq=.9):
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>"
               f"<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='{freq}' numOctaves='3' stitchTiles='stitch'/>"
               f"<feColorMatrix values='0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 {a} 0'/></filter>"
               "<rect width='100%' height='100%' filter='url(#n)'/></svg>")
        return f'url("data:image/svg+xml,{quote(svg)}")'
    mirror = mirror_script(seed=3, lines=14, w=300, color="#A8432F", op=.22)
    mirror = mirror.replace('<svg ', "<svg xmlns='http://www.w3.org/2000/svg' ", 1).replace('"', "'")
    w, h = META["C"]["sym"]
    from build_logos import sym_monolith
    inner, _, _ = sym_monolith({"mass": "#141312", "mass2": "#141312"})
    csym = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'>" + inner.replace('"', "'") + "</svg>")
    return (":root{"
            f"--noise:{noise(.23, .16, .12, .09)};"
            f"--noise-d:{noise(.9, .86, .8, .05, .75)};"
            f"--mirror-a:url(\"data:image/svg+xml,{quote(mirror)}\");"
            f"--c-sym-faint:url(\"data:image/svg+xml,{quote(csym)}\");"
            "}")


def page():
    body = (nav() + "<main>" + cover() + brief() + concept() + chapter("A") + chapter("B") + chapter("C")
            + compare() + next_steps() + "</main>")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DAVINCI · دافنشي — Brand Identity Exploration</title>
<meta name="description" content="Three brand identity directions for DAVINCI Engineering Consultancy, Baghdad.">
<link rel="icon" href="data:image/svg+xml,{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
{texture_tokens()}
{CSS}
</style>
</head>
<body>
{SPRITE}
{body}
<script>
{JS}
</script>
</body>
</html>
'''


FAVICON = ("%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Cpath d='M50 8L86.37 29L86.37 71L50 92ZM59 32.2L77.37 42.8L77.37 57.2L59 67.8Z' "
           "fill='%232F6FED' fill-rule='evenodd'/%3E%3Cpath d='M50 13L17 31.8L17 68.2L50 87M17 31.8L50 50L50 87' "
           "fill='none' stroke='%230E1621' stroke-width='7'/%3E%3C/svg%3E")

if __name__ == "__main__":
    html = page()
    with open(os.path.join(ROOT, "index.html"), "w") as fh:
        fh.write(html)
    print("index.html", round(len(html) / 1024), "KB")
