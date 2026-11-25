#!/usr/bin/env python3
"""Slower, less rushed v2 cut of the A-roll.

The scenes in build.py were authored against the v1 timeline (pieces_v1.json /
words_v1.json: 1.08x speed, every pause cut). This module builds the v2 cut
and exposes T(t_v1) -> t_v2 so every authored time follows the new pacing.

v2 changes:
  * speed: back towards natural (SPEED, solved so the reel stays under 2:00)
  * breathing room: each piece is extended into its real pause (only while the
    source audio is silent): ~0.34 s after a full stop, ~0.16 s after a comma
  * repeated / filler phrases removed (CUT_WORDS)

Run directly to write pieces.json, words_edit.json and retime.json.
"""
import json, os, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V1_SPEED = 1.08
TARGET = 118.8          # seconds; keep the reel under 2:00
FPS = 30

P1 = json.load(open(os.path.join(HERE, "pieces_v1.json")))
W1 = json.load(open(os.path.join(HERE, "words_v1.json")))

# word indices (in words_v1.json) to drop
CUT_WORDS = set(
    list(range(15, 21))      # "semuanya dibekukan dan tak boleh dikeluarkan." (repeats "terbeku")
    + [50, 51]               # "bergantung kawasan."
    + [149, 150]             # "at least."
    + [163, 164]             # "Yang mana"
    + list(range(195, 201))  # "Sekiranya anda melanggan Wasitah Intan ini,"
    + [227]                  # "kerana" (dangling)
)
POST = {".": 0.34, "?": 0.34, ",": 0.16, "": 0.05}
PRE = 0.05


def _piece_of_word(i):
    """Locate a word by its v1 edited time and re-derive its source time from the cut list."""
    w = W1[i]
    mid = (w["start"] + w["end"]) / 2
    k = next((k for k, p in enumerate(P1) if p["out0"] <= mid < p["out0"] + p["od"]), len(P1) - 1)
    p = P1[k]
    w["src"] = round(max(p["s0"], p["s0"] + (w["start"] - p["out0"]) * V1_SPEED), 3)
    return k


def _silence_mask():
    path = os.environ.get("SRC16")
    if not path:
        return None
    wv = wave.open(path)
    a = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(float) / 32768
    f = a[: len(a) // 320 * 320].reshape(-1, 320)            # 20 ms frames @16k
    db = 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)
    return db < -40


def build():
    wp = [_piece_of_word(i) for i in range(len(W1))]
    # source end of each word
    wend = []
    for i, w in enumerate(W1):
        e = w["src"] + (w["end"] - w["start"]) * V1_SPEED
        if i + 1 < len(W1) and wp[i + 1] == wp[i]:
            e = min(e, W1[i + 1]["src"])
        wend.append(min(e, P1[wp[i]]["s1"]))

    # sub-pieces: old piece minus cut words
    subs = []  # dicts: k, s0, s1, words[], end_punct
    for k, p in enumerate(P1):
        idx = [i for i in range(len(W1)) if wp[i] == k]
        cur = None
        segs = []
        lo = p["s0"]
        for i in idx:
            if i in CUT_WORDS:
                if cur is not None:
                    cur["s1"] = max(cur["words"][-1] and wend[cur["words"][-1]], W1[i]["src"] - 0.03)
                    cur["s1"] = min(cur["s1"], W1[i]["src"] - 0.03)
                    cur["cut_after"] = True
                    segs.append(cur); cur = None
                lo = None
            else:
                if cur is None:
                    s0 = lo if lo is not None else W1[i]["src"] - 0.05
                    cur = {"k": k, "s0": s0, "s1": p["s1"], "words": [], "cut_after": False}
                cur["words"].append(i)
        if cur is not None:
            segs.append(cur)
        subs += [s for s in segs if s["words"]]

    sil = _silence_mask()
    def silent(t0, t1):
        if sil is None:
            return True
        a, b = int(t0 / 0.02), int(np.ceil(t1 / 0.02))
        return bool(sil[max(0, a):b].all())

    # occupied source ranges (other subs + cut words) to avoid
    blocked = [(W1[i]["src"] - 0.03, wend[i] + 0.03) for i in CUT_WORDS]
    for j, s in enumerate(subs):
        last = W1[s["words"][-1]]["text"]
        punct = "." if s["cut_after"] else (last[-1] if last[-1] in ".?," else "")
        want = POST[punct]
        others = [(o["s0"], o["s1"]) for jj, o in enumerate(subs) if jj != j] + blocked
        e = s["s1"]
        step = 0.02
        while e - s["s1"] < want:
            n = e + step
            if any(a < n and b > e for a, b in others) or not silent(e, n):
                break
            e = n
        s["post"] = round(e - s["s1"], 3)
        b = s["s0"]
        while s["s0"] - b < PRE:
            n = b - step
            if any(a < b and bb > n for a, bb in others) or not silent(n, b):
                break
            b = n
        s["pre"] = round(s["s0"] - b, 3)
        s["punct"] = punct

    # where neighbouring pieces touch in the source, meet in the middle (no doubled audio)
    for j in range(1, len(subs)):
        a, b = subs[j - 1], subs[j]
        e_prev, s_next = a["s1"] + a["post"], b["s0"] - b["pre"]
        if b["s0"] > a["s0"] and s_next < e_prev:
            m = (max(a["s1"], s_next) + min(b["s0"], e_prev)) / 2
            a["post"] = round(max(0.0, m - a["s1"]), 3)
            b["pre"] = round(max(0.0, b["s0"] - m), 3)
            if a["s1"] > b["s0"]:          # cores overlap (already so in v1): trim the earlier one
                a["s1"] = b["s0"]; a["post"] = 0.0; b["pre"] = 0.0

    total_src = sum(s["s1"] + s["post"] - s["s0"] + s["pre"] for s in subs)
    speed = max(1.0, total_src / TARGET)

    pieces, t = [], 0.0
    for j, s in enumerate(subs):
        a, b = s["s0"] - s["pre"], s["s1"] + s["post"]
        nf = int(round((b - a) / speed * FPS))
        pieces.append({"i": j, "lab": P1[s["k"]]["lab"], "k": s["k"], "s0": round(a, 3), "s1": round(b, 3),
                       "core0": s["s0"], "core1": s["s1"], "out0": round(t, 4), "od": nf / FPS, "nf": nf})
        t += nf / FPS
    D = round(t, 3)

    def Tsrc_in(pc, s):
        return pc["out0"] + (s - pc["s0"]) / speed

    def T(t1):
        """v1 edited time -> v2 edited time."""
        t1 = max(0.0, min(t1, P1[-1]["out0"] + P1[-1]["od"]))
        k = next((k for k, p in enumerate(P1) if p["out0"] <= t1 < p["out0"] + p["od"]), len(P1) - 1)
        p = P1[k]
        s = p["s0"] + (t1 - p["out0"]) * V1_SPEED
        mine = [pc for pc in pieces if pc["k"] == k]
        for pc in mine:
            if pc["core0"] - 1e-6 <= s <= pc["core1"] + 1e-6:
                return round(Tsrc_in(pc, s), 4)
        # inside a removed stretch: spread proportionally across the neighbouring gap
        before = [pc for pc in pieces if pc["k"] < k or (pc["k"] == k and pc["core1"] < s)]
        after = [pc for pc in pieces if pc["k"] > k or (pc["k"] == k and pc["core0"] > s)]
        hole0 = max([pc["core1"] for pc in mine if pc["core1"] < s], default=p["s0"])
        hole1 = min([pc["core0"] for pc in mine if pc["core0"] > s], default=p["s1"])
        n0 = before[-1]["out0"] + before[-1]["od"] if before else 0.0
        n1 = after[0]["out0"] if after else D
        if before:
            n0 = Tsrc_in(before[-1], before[-1]["core1"])
        if after:
            n1 = Tsrc_in(after[0], after[0]["core0"])
        f = (s - hole0) / max(1e-6, hole1 - hole0)
        return round(n0 + (n1 - n0) * min(1, max(0, f)), 4)

    words = []
    for i, w in enumerate(W1):
        if i in CUT_WORDS:
            continue
        pc = next(pc for pc in pieces if pc["k"] == wp[i] and pc["s0"] - 0.06 <= w["src"] <= pc["s1"])
        st = Tsrc_in(pc, w["src"])
        en = Tsrc_in(pc, min(wend[i], pc["core1"]))
        text = w["text"]
        if i + 1 in CUT_WORDS and not text[-1] in ".?":
            text = text.rstrip(",") + "."
        words.append({"text": text, "start": round(st, 3), "end": round(max(en, st + 0.08), 3), "lab": w["lab"], "src": w["src"]})
    return pieces, words, speed, D, T


PIECES, WORDS, SPEED, D, T = build()

if __name__ == "__main__":
    json.dump([{k: v for k, v in p.items()} for p in PIECES], open(os.path.join(HERE, "pieces.json"), "w"), indent=0)
    json.dump(WORDS, open(os.path.join(HERE, "words_edit.json"), "w"), indent=0, ensure_ascii=False)
    tab = [[round(i * 0.01, 2), T(i * 0.01)] for i in range(int(round((P1[-1]["out0"] + P1[-1]["od"]) / 0.01)) + 1)]
    json.dump({"speed": SPEED, "D": D, "table": tab}, open(os.path.join(HERE, "retime.json"), "w"), separators=(",", ":"))
    print(f"pieces {len(PIECES)}  speed {SPEED:.4f}  D {D}")
    for x in (0, 4.75, 8.3, 14.75, 22.45, 37.55, 55.6, 61.05, 71.45, 78.5, 84.85, 96.95, 104.05, 111.3, 115.7):
        print(f"  {x:7.2f} -> {T(x):7.2f}")
