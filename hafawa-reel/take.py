"""Join the 13 Google AI Studio clips (voice/V01…V12, U01) into one take: voice/full-take.wav.
Trims each clip's silence, matches loudness, and leaves a natural 0.45 s breath between clips."""
import json, subprocess, pathlib, wave, numpy as np
R = pathlib.Path(__file__).parent; FS = 48000
order = [s['id'] for s in json.loads((R / 'voice/slots.json').read_text())]
out = []
for cid in order:
    f = next(p for p in (R / 'voice').glob(cid + '.*'))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-f', 's16le', '-ac', '1', '-ar', str(FS), '-'], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, '<i2') / 32768.
    hop = 480; e = np.sqrt(np.add.reduceat(v ** 2, np.arange(0, len(v), hop)) / hop); on = np.nonzero(e > .006)[0]
    v = v[max(0, on[0] * hop - 1440): min(len(v), (on[-1] + 1) * hop + 2400)]
    act = np.abs(v) > .02; v = v / (np.sqrt((v[act] ** 2).mean()) + 1e-9) * .16
    print(f'{cid}  {len(v) / FS:5.2f}s')
    out += [v, np.zeros(int(.45 * FS))]
y = np.concatenate([np.zeros(int(.2 * FS))] + out)
y = np.clip(y, -1, 1)
with wave.open(str(R / 'voice/full-take.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS); w.writeframes((y * 32767).astype('<i2').tobytes())
print('full-take', round(len(y) / FS, 2), 's')
