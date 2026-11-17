"""Synthesised score + sound design for «نسافر قبلك» (80 s). No samples, no licences needed.
python3 audio.py  ->  build/music.wav (48 kHz stereo)"""
import numpy as np, wave, pathlib

FS = 48000
DUR = 80.0
N = int(FS * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); Rr = np.zeros(N)          # dry bus
RV = np.zeros(N)                           # reverb send (mono)

def idx(t): return int(round(t * FS))
def add(sig, t, gain=1.0, pan=0.0, verb=0.0):
    i = idx(t); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:j] += s * l * 1.414; Rr[i:j] += s * r * 1.414
    if verb: RV[i:j] += s * verb

def T(d): return np.arange(int(d * FS)) / FS
def env_exp(d, tau): return np.exp(-T(d) / tau)
def adsr(d, a, r):
    t = T(d); e = np.ones_like(t)
    e *= np.clip(t / max(a, 1e-4), 0, 1)
    e *= np.clip((d - t) / max(r, 1e-4), 0, 1)
    return e
def fft_filter(x, lo=None, hi=None, soft=0.25):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / FS); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))
def noise(d): return rng.standard_normal(int(d * FS))
def sine(f, d, ph=0):
    t = T(d)
    if callable(f): return np.sin(2 * np.pi * np.cumsum(f(t)) / FS + ph)
    return np.sin(2 * np.pi * f * t + ph)

# ---------- instruments ----------
NOTE = dict(A2=110.0, D3=146.83, F3=174.61, A3=220.0, Bb3=233.08, C4=261.63, D4=293.66, Eb4=311.13,
            F4=349.23, Fs4=369.99, G4=392.0, A4=440.0, Bb4=466.16, C5=523.25, D5=587.33, Eb5=622.25, F5=698.46, A5=880.0, D6=1174.66)

def ks(freq, d, decay=0.996, bright=0.6):
    """Karplus-Strong pluck, vectorised per period."""
    n = int(d * FS); P = int(FS / freq)
    y = np.zeros(n + P + 1)
    exc = rng.uniform(-1, 1, P)
    exc = bright * exc + (1 - bright) * np.convolve(exc, np.ones(4) / 4, 'same')
    y[:P] = exc
    k = P
    while k < n:
        e = min(k + P, n)
        prev = y[k - P:e - P]; prev2 = y[k - P - 1:e - P - 1] if k - P - 1 >= 0 else np.concatenate([[0], y[k - P:e - P - 1]])
        y[k:e] = decay * 0.5 * (prev + prev2)
        k = e
    return y[:n]

def oud(note, d=1.6, vel=1.0):
    f = NOTE[note] if isinstance(note, str) else note
    s = ks(f, d, 0.9965, 0.75) + 0.8 * ks(f * 1.004, d, 0.9962, 0.6)
    s = fft_filter(s, lo=90, hi=4200)
    s[: int(.004 * FS)] *= np.linspace(0, 1, int(.004 * FS))
    s *= adsr(d, .002, .25)
    return s / (np.max(np.abs(s)) + 1e-9) * vel

def pad(freqs, d, a=1.5, r=1.5, bright=1800):
    t = T(d); s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.25, 0.0, 0.3):
            ff = f * (1 + det / 100 * 3)
            for h in range(1, 7):
                s += np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6.28)) / h ** 1.3
    s = fft_filter(s, lo=60, hi=bright)
    s *= adsr(d, a, r) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.17 * t))
    return s / (np.max(np.abs(s)) + 1e-9)

def bell(f, d=2.5, tau=.6):
    t = T(d)
    s = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / (tau * .4)) + .25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / (tau * .2)))
    return s * np.exp(-t / tau) * adsr(d, .003, .1)

def boom(d=2.0, f0=62, f1=32, tau=.55):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t / .18)
    s = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / tau)
    s += fft_filter(noise(d), hi=900) * np.exp(-t / .06) * .35
    return s

def hit(d=.9):  # punchy slam
    t = T(d); f = 48 + 110 * np.exp(-t / .03)
    s = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / .22)
    s += fft_filter(noise(d), lo=1200, hi=7000) * np.exp(-t / .045) * .6
    return s

def whoosh(d=1.0, rise=True):
    x = noise(d); out = np.zeros_like(x); hop = 2048
    for k in range(0, len(x), hop):
        seg = x[k:k + hop]; p = k / len(x); p = p if rise else 1 - p
        out[k:k + hop] = fft_filter(seg, lo=200 + 2500 * p, hi=900 + 7000 * p)
    return out * np.sin(np.pi * np.clip(T(d) / d, 0, 1)) ** 1.5

def tick():
    d = .05; t = T(d)
    return (fft_filter(noise(d), lo=2500, hi=9000) * np.exp(-t / .004) + .6 * np.sin(2 * np.pi * 1900 * t) * np.exp(-t / .006))

def cup_tak():
    d = 1.0; t = T(d)
    s = fft_filter(noise(d), lo=1500, hi=12000) * np.exp(-t / .0025) * 1.2
    for f, a, tau in ((2350, .5, .16), (3720, .35, .11), (5230, .22, .07), (7400, .12, .04)):
        s += a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    s += .6 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / .03)
    return s

def daf_dum():
    d = .6; t = T(d); f = 70 + 60 * np.exp(-t / .02)
    return np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / .16) + fft_filter(noise(d), hi=600) * np.exp(-t / .02) * .3
def daf_tak():
    d = .35; t = T(d)
    s = fft_filter(noise(d), lo=900, hi=6000) * np.exp(-t / .03)
    s += .3 * np.sin(2 * np.pi * 420 * t) * np.exp(-t / .04)
    jingle = fft_filter(noise(d), lo=6000, hi=14000) * np.exp(-t / .12) * .35
    return s + jingle

def heartbeat():
    d = .5; t = T(d)
    return np.sin(2 * np.pi * 48 * t) * np.exp(-t / .09) * np.clip(t / .01, 0, 1)

def pour(d):
    x = fft_filter(noise(d), lo=700, hi=4200)
    t = T(d); mod = .7 + .3 * np.sin(2 * np.pi * 7.3 * t + np.sin(2 * np.pi * 1.7 * t))
    return x * mod * adsr(d, .25, .25)

def crackle(d, rate=14):
    x = np.zeros(int(d * FS)); n = int(d * rate)
    for p in rng.integers(0, len(x) - 400, n):
        L_ = rng.integers(40, 300); x[p:p + L_] += rng.standard_normal(L_) * np.exp(-np.arange(L_) / 50) * rng.uniform(.2, 1)
    return fft_filter(x, lo=1500, hi=9000)

def air(d, lo=200, hi=1200): return fft_filter(noise(d), lo=lo, hi=hi)

# ---------- score ----------
# loop bed (start + end): D drone + pour
for a, b in ((0, 3.25), (76.4, 80.0)):
    d = b - a
    add(pad([NOTE['D3'] / 2, NOTE['A2'], NOTE['D3']], d, a=.05 if a == 0 else .6, r=.05 if b == 80 else .3, bright=700), a, .16, verb=.15)
    add(pour(d), a, .045, pan=-.1)
add(oud('D4', 2.4, .55), 1.7, .5, pan=.2, verb=.5)
add(oud('A3', 2.4, .5), 77.6, .45, pan=.2, verb=.5)
add(oud('D4', 2.4, .5), 78.6, .4, pan=-.2, verb=.5)

# riser + impact into the airport
add(whoosh(.8, True)[::-1] * np.linspace(0, 1, int(.8 * FS)) ** 2, 2.45, .35, verb=.2)
add(boom(2.5), 3.2, .9, verb=.35); add(whoosh(1.2, False), 3.2, .25, pan=.3)
# airport: cold drone + air + crowd murmur
d = 7.0
add(pad([NOTE['A2'], NOTE['A2'] * 1.5, NOTE['D3'] * 1.5], d, a=1, r=.5, bright=900), 3.2, .14, verb=.3)
add(air(d, 150, 700) * adsr(d, .5, .5), 3.2, .05)
add(fft_filter(noise(d), 300, 1400) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.7 * T(d)))) * adsr(d, .8, .5), 3.2, .02, pan=.3)
for k, f in enumerate((1250, 900)):
    add(np.sin(2 * np.pi * f * T(.09)) * adsr(.09, .005, .03), 7.9 + k * .12, .12, verb=.2)
for k in range(5): add(bell(NOTE['A5'], .6, .12), 8.6 + k * .7, .03)

# nostalgia: oud motif over warm pad
add(pad([NOTE['D3'], NOTE['F3'], NOTE['A3']], 5.6, a=1.2, r=1.4, bright=1500), 10.1, .17, verb=.4)
for t0, n in ((10.4, 'D4'), (10.85, 'F4'), (11.3, 'Eb4'), (11.75, 'D4'), (12.7, 'G4'), (13.1, 'F4'), (13.5, 'Eb4'), (13.9, 'D4'), (14.4, 'C4'), (14.8, 'D4')):
    add(oud(n, 1.8, .8), t0, .42, pan=.15, verb=.45)
add(np.sin(2 * np.pi * 660 * T(.25)) * np.exp(-T(.25) / .05), 10.95, .12, verb=.4)   # pin plip
for t0 in (12.7, 13.9): add(whoosh(1.0, True), t0, .07, pan=-.3, verb=.3)

# tension: accelerating clock, rising drone, slams, glitch
t0 = 15.6; tt = t0; iv = .5
while tt < 21.7:
    add(tick(), tt, .28 + .1 * (tt - t0) / 6, pan=.25); tt += iv; iv = max(.11, iv * .9)
d = 6.15
dr = sine(lambda t: 55 + 12 * (t / d) ** 2, d) + .5 * sine(lambda t: 82.4 + 18 * (t / d) ** 2, d)
add(dr * adsr(d, 1.0, .02), 15.6, .22, verb=.2)
add(air(d, 800, 5000) * np.linspace(0, 1, int(d * FS)) ** 2, 15.6, .07)
for t0 in (17.4, 18.2, 19.0): add(hit(), t0, .8, verb=.3)
for k in range(26):
    t0 = 19.8 + k * .074
    if rng.random() < .6:
        g = fft_filter(noise(.05), lo=rng.uniform(300, 3000), hi=9000) * .5
        add(np.repeat(g[::8], 8)[:len(g)], t0, .25, pan=rng.uniform(-.8, .8))

# the wish: near silence
add(air(6, 80, 400) * adsr(6, 1, 1), 22.0, .02)
add(pad([NOTE['A4'], NOTE['D5']], 6, a=2.5, r=2, bright=3000), 22.0, .08, verb=.6)
add(oud('D4', 3, .5), 24.6, .3, verb=.7)

# majlis: warm room, coals, pour, heartbeat on "على طول"
d = 7.5
add(air(d, 60, 450) * adsr(d, .6, .5), 28.0, .12)
add(crackle(d, 10) * adsr(d, .5, .5), 28.0, .1, pan=-.5, verb=.2)
add(pour(1.6), 28.2, .05, pan=.3)
for k in range(3): add(heartbeat(), 33.7 + k * .82, .75); add(heartbeat(), 33.95 + k * .82, .5)
add(pad([NOTE['D3'], NOTE['A3'], NOTE['F4']], 4.2, a=2.5, r=.3, bright=1200), 35.3, .13, verb=.5)
add(whoosh(.45, False), 38.95, .12)
add(cup_tak(), 39.35, .55, verb=.9)

# founding: oud theme + daf
add(pad([NOTE['D3'], NOTE['F3'], NOTE['A3']], 6.8, a=.8, r=.6, bright=1700), 40.1, .14, verb=.4)
x = fft_filter(noise(2.0), lo=2000, hi=7000) * (np.abs(np.sin(2 * np.pi * 6 * T(2.0))) ** 3)
add(x * adsr(2.0, .1, .2), 40.4, .05, pan=.2)
for t0, n in ((40.6, 'D4'), (41.05, 'F4'), (41.5, 'Eb4'), (41.95, 'D4'), (42.8, 'A4'), (43.25, 'Bb4'), (43.7, 'A4'), (44.15, 'G4'), (44.6, 'F4'), (45.05, 'Eb4'), (45.5, 'D4')):
    add(oud(n, 1.6, .85), t0, .42, pan=.15, verb=.4)
add(daf_dum(), 44.6, .5, verb=.3)
BEAT = 60 / 90
def daf_bar(t0, g=1.0):
    for off, kind in ((0, 'd'), (1, 't'), (1.5, 't'), (2, 'd'), (3, 't'), (3.5, 't')):
        add(daf_dum() if kind == 'd' else daf_tak(), t0 + off * BEAT, (.55 if kind == 'd' else .22) * g, pan=0 if kind == 'd' else .3, verb=.15)
b = 42.6
while b < 46.8: daf_bar(b, .7); b += 4 * BEAT

# principle: build
b = 47.2
while b < 58.9: daf_bar(b, .55 + .45 * (b - 47.2) / 11.7); b += 4 * BEAT
add(pad([NOTE['D3'], NOTE['A3'], NOTE['D4'], NOTE['F4']], 11.8, a=4, r=.05, bright=2600), 47.2, .2, verb=.4)
for t0 in (51.8, 52.7, 53.6, 54.6, 55.6):
    add(boom(1.4, 90, 45, .3), t0, .55, verb=.3); add(bell(NOTE['D6'], 1.2, .25), t0 + .22, .05, verb=.6)
add(whoosh(2.0, True) * np.linspace(0, 1, int(2.0 * FS)) ** 2, 57.0, .3, verb=.3)

# the line: silence -> whisper shimmer -> big hit
sh = np.zeros(int(.75 * FS))
for f in (NOTE['D5'], NOTE['A5'], NOTE['D6']): sh += np.sin(2 * np.pi * f * T(.75))
add(sh * np.linspace(0, 1, len(sh)) ** 3, 59.85, .05, verb=.8)
add(boom(3.0, 70, 30, .8), 60.6, 1.0, verb=.5)
add(fft_filter(noise(3.0), lo=4000, hi=15000) * env_exp(3.0, .8), 60.6, .12, verb=.5)
add(pad([NOTE['D3'], NOTE['A3'], NOTE['D4'], NOTE['F4'], NOTE['A4']], 9.5, a=.02, r=1.2, bright=3200), 60.6, .22, verb=.5)
add(oud('D4', 2.4, 1), 60.6, .45, verb=.5)

# growth: full theme, rising plucks per country, chimes for branches
b = 62.0
while b < 69.9: daf_bar(b, .9); b += 4 * BEAT
scale = ['D4', 'Eb4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'F5']
for i in range(21):
    f = NOTE[scale[i % len(scale)]] * (2 if i >= len(scale) * 2 else 1)
    add(oud(f, .9, .7), 62.95 + i * .13, .2, pan=-.6 + 1.2 * (i / 20), verb=.4)
for t0, n in ((63.4, 'D4'), (63.85, 'F4'), (64.3, 'Eb4'), (64.75, 'D4')): add(oud(n, 1.6), t0, .35, verb=.4)
for t0 in (65.2, 67.4): add(bell(NOTE['A5'], 2.5, .7), t0, .12, verb=.6); add(bell(NOTE['D6'], 2.5, .6), t0 + .1, .08, verb=.6)

# arrival: chime + resolve to D major
add(bell(NOTE['F5'] * 1.06, 2.2, .7), 70.3, .12, verb=.5)
add(bell(NOTE['C5'] * 1.06, 2.6, .9), 70.75, .12, verb=.5)
add(pad([NOTE['D3'], NOTE['Fs4'], NOTE['A3'], NOTE['D4'], NOTE['A4']], 6.6, a=.5, r=1.4, bright=3400), 70.1, .24, verb=.5)
for t0, n in ((71.0, 'D4'), (71.5, 'Fs4'), (72.0, 'A4'), (72.6, 'G4'), (73.1, 'Fs4'), (73.7, 'D4')): add(oud(n, 2.0, .9), t0, .38, pan=.1, verb=.5)
b = 70.0
while b < 75.4: daf_bar(b, .5); b += 4 * BEAT

# ---------- reverb + master ----------
ir_d = 2.6; t = T(ir_d)
irL = fft_filter(noise(ir_d), hi=6000) * np.exp(-t / .55); irR = fft_filter(noise(ir_d), hi=6000) * np.exp(-t / .6)
def conv(x, h):
    n = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[: len(x)]
wetL = conv(RV, irL); wetR = conv(RV, irR)
sc = .9 / max(np.max(np.abs(wetL)), 1e-9) * .25
L += wetL * sc; Rr += wetR * sc
mix = np.stack([L, Rr], 1)
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.max(np.abs(mix)) / 0.89
fade = int(.012 * FS); mix[:fade] *= np.linspace(0, 1, fade)[:, None]; mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = pathlib.Path(__file__).parent / 'build'; out.mkdir(exist_ok=True)
with wave.open(str(out / 'music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(FS)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('music.wav', mix.shape[0] / FS, 's')
