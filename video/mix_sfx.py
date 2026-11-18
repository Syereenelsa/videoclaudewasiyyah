"""Synthesise sound effects procedurally and mix them to a cue sheet.

Usage: python3 mix_sfx.py sfx_cues.json out.wav

Every sound is generated from scratch with numpy (no samples, no licensing).
Cue entries: {"name": str, "t": seconds, "g": gain (opt), "p": pitch (opt), "d": duration (opt)}
"""
import json, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def tt(d):
    return np.arange(int(d * SR)) / SR


def expenv(d, tau, att=0.002):
    t = tt(d)
    e = np.exp(-t / tau)
    a = int(att * SR)
    if a > 1:
        e[:a] *= np.linspace(0, 1, a)
    return e


def sweep_sine(f0, f1, d, curve='exp'):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d) if curve == 'exp' else f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def svf(x, fc, q=0.7, mode='band'):
    """Chamberlin state-variable filter with per-sample cutoff."""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    f = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    low = band = 0.0
    out = np.empty_like(x)
    damp = 1.0 / q
    for i in range(len(x)):
        low += f[i] * band
        high = x[i] - low - damp * band
        band += f[i] * high
        out[i] = band if mode == 'band' else (low if mode == 'low' else high)
    return out


def noise(d):
    return rng.standard_normal(int(d * SR))


def place(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return buf
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n]
    return buf


def mono(d):
    return np.zeros(int(d * SR))


def stereo(sig, pan=0.0):
    pan = np.broadcast_to(np.asarray(pan, float), sig.shape)
    a = (pan + 1) * np.pi / 4
    return np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1) * np.sqrt(2)


def bell(f, tau, d=None, ratios=(1, 2.0, 3.0, 4.2, 5.4), w=(1, .45, .22, .1, .05)):
    d = d or tau * 5
    t = tt(d)
    s = sum(wi * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (tau / r ** .5)) for r, wi in zip(ratios, w))
    s[:96] *= np.linspace(0, 1, 96)
    return s


# ---------------------------------------------------------------- sounds
def s_whoosh(p=1, **_):
    d = 0.6
    t = tt(d)
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    fc = 350 + 2600 * np.sin(np.pi * t / d) ** 1.5
    s = svf(noise(d), fc * p, q=0.8) * shape * 0.55
    return stereo(s, np.linspace(-.6, .6, len(s)))


def s_rise(p=1, **_):
    d = 0.38
    t = tt(d)
    env = (t / d) ** .6 * np.exp(-((t / d) / .55) ** 4)
    s = svf(noise(d), (900 + 3800 * t / d) * p, q=1.1) * env * 0.22
    return stereo(s, np.linspace(.3, -.3, len(s)))


def s_pop(p=1, **_):
    d = 0.14
    s = sweep_sine(560 * p, 250 * p, d) * expenv(d, .035, .001) * .4
    s[:150] += svf(noise(150 / SR), 4000, 1.0, 'high') * np.linspace(1, 0, 150) * .25
    return s


def s_tick(p=1, **_):
    d = 0.06
    t = tt(d)
    return (np.sin(2 * np.pi * 1800 * p * t) + .4 * np.sin(2 * np.pi * 3600 * p * t)) * expenv(d, .012, .0005) * .3


def s_ice(p=1, **_):
    d = 0.7
    out = mono(d)
    imp = np.zeros(int(.4 * SR))
    for k in range(40):
        pos = int((rng.random() ** 2) * len(imp))
        imp[pos] += rng.uniform(-1, 1)
    out[:len(imp)] += svf(imp, 3500, 2.0, 'high') * 1.6
    for f in rng.uniform(2200, 6500, 5):
        out += np.sin(2 * np.pi * f * p * tt(d)) * expenv(d, rng.uniform(.12, .3)) * .07
    return stereo(out * .55, rng.uniform(-.4, .4))


def s_shimmer(p=1, **_):
    d = 1.6
    out = np.zeros((int(d * SR), 2))
    for k in range(14):
        b = bell(rng.uniform(2400, 6000) * p, .25, .8, ratios=(1, 2.01), w=(1, .2)) * .07
        place(out, stereo(b, rng.uniform(-.8, .8)), k * .055)
    return out


def s_freeze(**_):
    pre = 0.45
    d = 1.6 + pre
    out = np.zeros((int(d * SR), 2))
    t = tt(pre)
    swell = svf(noise(pre)[::-1].copy(), 500 + 5000 * (t / pre) ** 2, 1.0) * (t / pre) ** 3 * .45
    place(out, stereo(swell), 0)
    boom = sweep_sine(95, 32, 1.0) * expenv(1.0, .32, .003) * .95
    hit = svf(noise(.3), 600, .7, 'low') * expenv(.3, .06) * .9
    place(out, stereo(boom + np.pad(hit, (0, len(boom) - len(hit)))), pre)
    place(out, s_ice() * 1.4, pre)
    place(out, s_shimmer() * .8, pre + .12)
    return out, pre


def s_lock(**_):
    d = 0.3
    out = mono(d)
    for at, g in ((0, 1), (.075, .8)):
        c = svf(noise(.006), 3200, 1.5) * np.linspace(1, 0, int(.006 * SR)) * 1.2
        c = np.concatenate([c, np.sin(2 * np.pi * 2600 * tt(.08)) * expenv(.08, .02) * .25])
        place(out, c * g, at)
    return out * .7


def s_buzz(**_):
    d = 0.42
    out = mono(d)
    t = tt(.15)
    tone = sum(np.sin(2 * np.pi * 150 * k * t) / k for k in range(1, 9))
    env = np.minimum(1, np.minimum(t / .005, (.15 - t) / .03))
    for at in (0, .21):
        place(out, tone * env * .3, at)
    return out


def s_paper(**_):
    d = 0.32
    t = tt(d)
    flutter = np.abs(svf(noise(d), 40, .7, 'low')) * 6 + .3
    env = np.sin(np.pi * t / d) ** .8
    s = svf(noise(d), 2600 - 1400 * t / d, 1.4) * flutter * env * .32
    return stereo(s, np.linspace(.5, -.2, len(s)))


def s_stamp(**_):
    d = 0.45
    s = sweep_sine(150, 55, d) * expenv(d, .07, .001) * .95
    n = svf(noise(.12), 1500, .8, 'low') * expenv(.12, .025) * 1.1
    k = np.sin(2 * np.pi * 320 * tt(.08)) * expenv(.08, .015) * .4
    s[:len(n)] += n
    s[:len(k)] += k
    return s


def s_thud(g=1, **_):
    d = 0.6
    return sweep_sine(105, 42, d) * expenv(d, .14, .002) * .8


def s_alarm(**_):
    d = 0.6
    out = mono(d)
    t = tt(.11)
    env = np.minimum(1, np.minimum(t / .004, (.11 - t) / .02))
    for i, f in enumerate((880, 660, 880, 660)):
        sq = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 3, 5))
        place(out, sq * env * .3, i * .14)
    return out


def s_gavel(**_):
    d = 0.6
    out = mono(d)
    for at, g in ((0, 1), (.23, .75)):
        t = tt(.18)
        k = (np.sin(2 * np.pi * 420 * t) + .5 * np.sin(2 * np.pi * 1150 * t)) * np.exp(-t / .028)
        k[:400] += svf(noise(400 / SR), 1600, 1.2) * np.linspace(1, 0, 400) * .8
        place(out, k * g * .7, at)
    return out


def s_success(**_):
    d = 2.2
    out = np.zeros((int(d * SR), 2))
    for i, (f, pan) in enumerate(((1046.5, -.3), (1318.5, 0), (1568, .3), (2093, .1))):
        place(out, stereo(bell(f, .45, 1.6) * (.24 if i < 3 else .14), pan), i * .085)
    return out


def s_check(p=1, **_):
    return bell(1318.5 * p, .35, 1.4) * .26 + np.pad(s_tick(p * 1.5) * .6, (0, int(1.4 * SR) - int(.06 * SR)))


def s_impact(**_):
    pre = 0.3
    d = 1.4 + pre
    out = mono(d)
    t = tt(pre)
    place(out, svf(noise(pre), 300 + 4000 * (t / pre) ** 2, .9) * (t / pre) ** 3 * .4, 0)
    place(out, sweep_sine(75, 28, 1.2) * expenv(1.2, .38, .002), pre)
    place(out, svf(noise(.4), 900, .7, 'low') * expenv(.4, .09) * .8, pre)
    return out, pre


def s_counter(d=1.5, p=1, **_):
    out = mono(d + .1)
    n = 26
    for k in range(1, n + 1):
        at = d * (1 - np.sqrt(1 - k / n))  # inverse of power2.out
        f = (2300 if k % 2 else 2600) * p
        place(out, np.sin(2 * np.pi * f * tt(.025)) * expenv(.025, .006, .0005) * .32, at)
    return out


def s_cash(**_):
    d = 1.4
    out = np.zeros((int(d * SR), 2))
    for at, f, pan in ((0, 1900, -.2), (.085, 2550, .2)):
        b = bell(f, .38, 1.2, ratios=(1, 2.76, 5.4, 8.93), w=(1, .5, .25, .12)) * .22
        place(out, stereo(b, pan), at)
    coins = svf(noise(.35), 6000, 1.0, 'high') * expenv(.35, .07) * .2
    place(out, stereo(coins, .1), .02)
    return out


def s_riser(**_):
    d = 1.1
    t = tt(d)
    env = (t / d) ** 2
    env[-960:] *= np.linspace(1, 0, 960)
    s = svf(noise(d), 400 * (6000 / 400) ** (t / d), 1.3) * env * .38
    s += sweep_sine(220, 880, d) * env * .06
    return stereo(s, np.sin(2 * np.pi * 1.5 * t) * .35)


def s_reveal(**_):
    d = 3.2
    out = np.zeros((int(d * SR), 2))
    for f, pan in ((523.25, -.4), (659.25, -.1), (783.99, .15), (1046.5, .4)):
        place(out, stereo(bell(f, 1.1, 3.0) * .17, pan), 0)
    place(out, stereo(sweep_sine(70, 40, 1.2) * expenv(1.2, .4, .003) * .55), 0)
    place(out, s_shimmer(1.2) * .9, .05)
    return out


def s_chime(**_):
    d = 3.2
    out = np.zeros((int(d * SR), 2))
    for i, f in enumerate((783.99, 1046.5, 1318.5, 1568, 2093)):
        place(out, stereo(bell(f, .9, 2.4) * .2, -.5 + i * .25), i * .12)
    return out


SOUNDS = {k[2:]: v for k, v in globals().items() if k.startswith('s_')}


def reverb_ir(d=1.3, tau=.32):
    t = tt(d)
    irs = []
    for _ in range(2):
        n = rng.standard_normal(len(t)) * np.exp(-t / tau)
        n = np.convolve(n, np.ones(6) / 6, 'same')  # soften highs
        n[:int(.012 * SR)] = 0  # pre-delay
        irs.append(n / np.sqrt(np.sum(n ** 2)))
    return irs


def fftconv(x, h):
    n = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[:len(x)]


def voice_track(data, n):
    import subprocess, os
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), data['vo_src'])
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    src = np.frombuffer(raw, np.float32).astype(float)
    src /= np.max(np.abs(src))
    out = np.zeros(n)
    f = int(.015 * SR)
    for c in data['vo']:
        seg = src[int(c['a'] * SR):int(c['b'] * SR)].copy()
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        place(out, seg, c['at'])
    return out


def smooth_env(x, attack, release):
    # cheap peak follower on a decimated signal, then upsampled
    hop = 240
    m = x[:len(x) // hop * hop].reshape(-1, hop).max(axis=1)
    a, r = np.exp(-hop / (attack * SR)), np.exp(-hop / (release * SR))
    e = np.zeros_like(m); v = 0.0
    for i, s in enumerate(m):
        v = a * v + (1 - a) * s if s > v else r * v + (1 - r) * s
        e[i] = v
    e = np.repeat(e, hop)
    return np.pad(e, (0, len(x) - len(e)), mode='edge')


def main(cue_path, out_path):
    data = json.load(open(cue_path))
    dur = data['duration']
    mix = np.zeros((int(dur * SR) + SR, 2))
    cache = {}
    for c in data['cues']:
        name = c['name']
        kw = {k: c[k] for k in ('p', 'd') if k in c}
        key = (name, tuple(sorted(kw.items())))
        if key not in cache or name in ('ice', 'shimmer'):  # re-roll random ones for variety
            r = SOUNDS[name](**kw)
            sig, pre = r if isinstance(r, tuple) else (r, 0.0)
            if sig.ndim == 1:
                sig = stereo(sig)
            cache[key] = (sig, pre)
        sig, pre = cache[key]
        place(mix, sig * c.get('g', 1.0), c['t'] - pre)
    mix = mix[:int(dur * SR)]
    irl, irr = reverb_ir()
    wet = np.stack([fftconv(mix[:, 0], irl), fftconv(mix[:, 1], irr)], axis=1)
    sfx = mix + wet * 0.22
    sfx /= np.max(np.abs(sfx))
    if data.get('vo'):
        vo = voice_track(data, len(sfx))
        # duck the effects while someone is speaking
        env = smooth_env(np.abs(vo), attack=.02, release=.35)
        duck = 1 - 0.55 * np.clip(env / 0.08, 0, 1)
        out = vo[:, None] * 0.9 + sfx * 0.42 * duck[:, None]
    else:
        out = sfx
    peak = np.max(np.abs(out))
    out = np.tanh(out / peak * 1.2) / np.tanh(1.2) * 0.89  # gentle limiter, ~-1 dBFS
    fade = int(.8 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    pcm = (out * 32767).astype('<i2')
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f'{len(data["cues"])} cues mixed -> {out_path} ({dur:.1f}s)')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
