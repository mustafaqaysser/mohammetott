"""Fit the visual timeline to a continuous voice take.
Input : build/voice_full.wav + build/align.json (phrase timings from the alignment pass)
Output: build/voice_track.wav (voice with dramatic pauses added) and src/timing.json
        (time-warp anchors visual->output, duration, caption cues)."""
import json, re, wave, pathlib, numpy as np
R = pathlib.Path(__file__).parent
al = json.loads((R / 'build/align.json').read_text())
strip = lambda t: re.sub(r'[ً-ْ\s….؟:،]', '', t)

# ---- per-phrase timings (split multi-phrase rows by character share) ----
ph = []
for row in al['al']:
    idx = row['phr']; a, b = row['a'], row['b']
    L = [len(strip(al['ph'][i][1])) for i in idx]; tot = sum(L); t = a
    for i, l in zip(idx, L):
        d = (b - a) * l / tot; ph.append(dict(text=al['ph'][i][1], a=t, b=t + d)); t += d
def find(prefix, nth=1):
    hits = [p for p in ph if strip(p['text']).startswith(strip(prefix))]
    return hits[nth - 1]

# ---- dramatic pauses inserted before these phrases ----
INSERT = [('وكنت أقول لنفسي', .5), ('فأسسنا', .5), ('سافر قبلك', .7), ('واليوم', 1.0)]
with wave.open(str(R / 'voice/full-take.wav')) as w:
    fs = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64)
cuts = sorted((find(p)['a'] - .12, g) for p, g in INSERT)
parts, last, shift = [], 0, 0.0
for t, g in cuts:
    i = int(t * fs); parts += [x[last:i], np.zeros(int(g * fs))]; last = i
parts.append(x[last:]); y = np.concatenate(parts)
def sh(t): return t + sum(g for c, g in cuts if t >= c)
for p in ph: p['a'], p['b'] = sh(p['a']), sh(p['b'])
D = round(len(y) / fs, 3)
with wave.open(str(R / 'build/voice_track.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs); w.writeframes(y.astype('<i2').tobytes())

S = lambda p, n=1: find(p, n)['a']
E = lambda p, n=1: find(p, n)['b']
ton = find('ونتأكد من التراخيص')
anchors = [
    (0, 0), (0.25, S('هذا الفنجان')), (3.2, S('تعرف') - .15), (3.6, S('تعرف')), (5.6, S('توصل')), (7.7, S('الكل')),
    (10.2, E('إلا أنت') + .2), (10.4, S('من صغري')), (12.7, S('من شنغهاي') + .1), (13.9, S('لماربيا') - .1),
    (15.6, S('بس ترتيبات') - .25), (15.8, S('بس ترتيبات')), (17.4, S('فنادق')), (18.2, S('أسعار')), (19.0, S('مواصلات')),
    (19.8, S('وهل كل')), (21.75, E('وهل كل') + .1), (22.4, S('وكنت أقول')), (24.6, S('يا ليت')),
    (28.0, S('يا وليدي') - .4), (28.4, S('يا وليدي')), (31.2, S('لو تقدر')), (33.6, S('أنا معك')), (35.4, E('أنا معك') + .1),
    (35.8, S('وهنا انتبهت')), (37.3, S('هو يطلب')), (39.35, E('اللي كنت') + .12), (40.0, S('فأسسنا') - .45), (40.6, S('فأسسنا')),
    (42.8, S('لأن المسافر')), (47.0, S('ومبدأنا') - .2), (47.2, S('ومبدأنا')), (49.6, S('ما نقدم')),
    (51.8, S('نجرب الفندق')), (52.7, S('السيارة')), (53.6, S('السواق')), (54.6, ton['a']), (55.6, ton['a'] + .58 * (ton['b'] - ton['a'])),
    (56.8, S('عشان لما')), (59.0, E('يكون فيه') + .1), (59.85, S('سافر قبلك')), (60.6, E('سافر قبلك') + .05),
    (62.0, S('واليوم') - .3), (62.4, S('واليوم')), (65.2, S('وفرع في جدة')), (67.4, S('وفرع في طرابزون')),
    (70.0, E('وفرع في طرابزون') - .06), (70.6, S('حفاوة المسافرون', 2) + .08), (72.6, S('نسافر قبلك')),
    (76.4, S('وكل هذا') - .4), (76.8, S('وكل هذا')), (80.0, D),
]
for (v0, o0), (v1, o1) in zip(anchors, anchors[1:]):
    k = (o1 - o0) / (v1 - v0)
    assert o1 > o0, (v0, v1)
    if k < .5 or k > 2.6: print(f'! stretch {k:.2f} between visual {v0}-{v1}')

# ---- caption cues from the real speech ----
def cue(first, last=None, hl=(), style='cap', y=None, end=None, nth=1):
    a = find(first, nth)['a']; e = find(last or first, nth)['b']
    return dict(a=round(a - .06, 3), e=round(e, 3), b=round(end if end else e + .45, 3), hl=list(hl), style=style, y=y,
                text=' '.join(p['text'] for p in ph[ph.index(find(first, nth)): ph.index(find(last or first, nth)) + 1]))
qend = S('وهنا انتبهت') - .3
C = [
    cue('هذا الفنجان', 'وراه', ['واحد', 'وعشرين', 'دولة.']),
    cue('تعرف'), cue('توصل'), cue('الكل', 'إلا أنت', ['إلا', 'أنت.']),
    cue('من صغري', hl=['السفر…']), cue('من شنغهاي', 'لماربيا', ['شَنْغهاي…', 'لماربِيّا.']),
    cue('بس ترتيبات'), cue('وهل كل'),
    cue('وكنت أقول', style='hero'), cue('يا ليت', 'يرتب لي', ['أثق'], style='hero'),
    cue('يا وليدي', 'أنا أسافر', style='quote', y=640, end=qend), cue('لو تقدر', 'وفنادق زينة', style='quote', y=800, end=qend),
    cue('أنا معك', hl=['أنا', 'معك', 'على', 'طول.'], style='quote', y=980, end=qend),
    cue('وهنا انتبهت', style='hero'), cue('هو يطلب', 'اللي كنت', ['أتمناه'], style='hero'),
    cue('فأسسنا', 'حفاوة المسافرون', ['حَفاوة', 'المسافرون.']), cue('لأن المسافر', 'مو بس', ['استقبال…']),
    cue('ومبدأنا', style='hero'), cue('ما نقدم', 'ما جربناها', ['جرّبناها.'], style='hero'),
    cue('نجرب الفندق', 'السواق'), cue('ونتأكد'), cue('عشان لما', 'يكون فيه', ['أحد…']),
    cue('واليوم', 'أكثر من', ['واحد', 'وعشرين', 'دولة…']), cue('وفرع في جدة', hl=['جدة…']), cue('وفرع في طرابزون', hl=['طَرابْزون.']),
    cue('حفاوة المسافرون', hl=['حَفاوة', 'المسافرون…'], nth=2), cue('نسافر قبلك', 'عشان ترتاح', ['نسافر', 'قبلك…']),
    cue('وكل هذا', 'بدأ من', ['هالفنجان.']),
]
for c, n in zip(C, C[1:]):
    if c['style'] == n['style'] == 'quote': continue
    c['b'] = min(c['b'], n['a'] - .02)
C[-1]['b'] = min(C[-1]['b'], D - .05)
(R / 'src/timing.json').write_text(json.dumps(dict(D=D, anchors=anchors, cues=C), ensure_ascii=False, indent=1))
print('D', D, 'anchors', len(anchors), 'cues', len(C))
