"""Synthesise a soft, warm ambient pad to sit under the voice-over.

Deterministic (no randomness without a fixed seed). Writes assets/bed.wav.
Usage: python3 tools/make_bed.py [duration_seconds]
"""
import sys, wave
from pathlib import Path
import numpy as np

SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 104.0
OUT = Path(__file__).resolve().parent.parent / "assets" / "bed.wav"

def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)

# Gentle, hopeful progression (in D): Dmaj9 - Bm7 - Gmaj7 - A6sus, 6.5 s per chord
CHORDS = [
    [50, 57, 62, 66, 69, 76],   # D  A  D  F# A  E
    [47, 54, 62, 66, 69, 73],   # B  F# D  F# A  C#
    [43, 50, 59, 62, 66, 71],   # G  D  B  D  F# B
    [45, 52, 61, 64, 66, 71],   # A  E  C# E  F# B
]
CH = 6.5
n = int(SR * DUR)
t = np.arange(n) / SR
L = np.zeros(n)
R = np.zeros(n)

idx = 0
start = 0.0
while start < DUR:
    notes = CHORDS[idx % len(CHORDS)]
    s0 = max(0.0, start - 1.2)
    s1 = min(DUR, start + CH + 1.2)
    a, b = int(s0 * SR), int(s1 * SR)
    tt = t[a:b] - s0
    seg = s1 - s0
    # slow attack / release crossfade
    env = np.minimum(1.0, np.minimum(tt / 1.8, (seg - tt) / 1.8)).clip(0, 1)
    env = env ** 1.6
    for k, m in enumerate(notes):
        f = hz(m)
        amp = (0.10 if k == 0 else 0.055) * (0.85 if m > 70 else 1.0)
        trem = 1.0 + 0.18 * np.sin(2 * np.pi * (0.11 + 0.03 * k) * tt + k)
        for det, pan in ((-0.0022, 0.3), (0.0022, 0.7)):
            ph = 2 * np.pi * f * (1 + det) * tt
            tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
            sig = amp * env * trem * tone
            L[a:b] += sig * (1 - pan)
            R[a:b] += sig * pan
    start += CH
    idx += 1

# soft "air": low-passed filtered noise, fixed seed
rng = np.random.default_rng(7)
noise = rng.standard_normal(n)
k = 900
kern = np.hanning(k); kern /= kern.sum()
air = np.convolve(noise, kern, mode="same") * 0.9
L += air; R += np.roll(air, 2205)

# light high-cut via moving average to keep it warm
def smooth(x, w=6):
    c = np.ones(w) / w
    return np.convolve(x, c, mode="same")
L, R = smooth(L), smooth(R)

# master fades
fade_in, fade_out = 2.5, 4.0
m = np.ones(n)
m *= np.clip(t / fade_in, 0, 1)
m *= np.clip((DUR - t) / fade_out, 0, 1)
L *= m; R *= m

peak = max(np.abs(L).max(), np.abs(R).max())
gain = 0.30 / peak          # leave plenty of headroom under the voice
st = np.stack([L * gain, R * gain], axis=1)
pcm = (st * 32767).astype(np.int16)
OUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {OUT} ({DUR:.1f}s)")
