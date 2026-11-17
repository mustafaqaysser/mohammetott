"""Mix Google AI Studio voice clips over the score and encode the final Reel.
Put clips in voice/ named V01.wav … V12.wav and U01.wav (wav/mp3/m4a all fine), then:  python3 mix.py"""
import json, subprocess, pathlib, numpy as np, wave, sys
R = pathlib.Path(__file__).parent; FS = 48000
SLOTS = json.loads((R / 'voice/slots.json').read_text())
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 's16le', '-ac', '1', '-ar', str(FS), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2') / 32768.
with wave.open(str(R / 'build/music.wav')) as w:
    music = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2) / 32768.
N = len(music); vox = np.zeros(N); found = 0
for s in SLOTS:
    f = next((p for p in (R / 'voice').glob(s['id'] + '.*') if p.suffix.lower() in ('.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac')), None)
    if not f: continue
    v = load(f); nz = np.nonzero(np.abs(v) > .01)[0]
    if len(nz): v = v[max(0, nz[0] - 480): nz[-1] + 4800]          # trim silence
    v = v / (np.sqrt((v ** 2).mean()) + 1e-9) * 0.12                 # loudness-match clips
    i = int(s['at'] * FS); j = min(N, i + len(v)); vox[i:j] += v[: j - i]; found += 1
    end = s['at'] + len(v) / FS
    if end > s['until'] + .05: print(f"! {s['id']} runs {end - s['until']:.2f}s past its slot (ends {end:.2f}s, slot ends {s['until']}s)")
print('voice clips:', found, '/', len(SLOTS))
# sidechain duck the music under the voice
env = np.convolve(np.abs(vox), np.ones(4800) / 4800, 'same'); env = np.clip(env / .04, 0, 1)
k = np.exp(-1 / (0.25 * FS)); sm = np.empty_like(env); a = 0.
for n in range(0, N, 480):
    a = max(env[n], a * k ** 480); sm[n:n + 480] = a
duck = 1 - 0.55 * sm
mix = music * duck[:, None] + vox[:, None] * np.array([1.0, 1.0])
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix /= max(np.abs(mix).max() / .89, 1)
with wave.open(str(R / 'build/soundtrack.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(FS); w.writeframes((mix * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(R / 'build/soundtrack.wav'), '-c:a', 'aac', '-b:a', '192k', str(R / 'soundtrack.m4a')], check=True)
name = 'hafawa-reel.mp4' if found else 'hafawa-reel-music-only.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', str(R / 'build/frames/f%05d.jpg'), '-i', str(R / 'build/soundtrack.wav'),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', str(R / name)], check=True)
print('->', name)
