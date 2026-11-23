#!/usr/bin/env python3
"""Make the cut list (pieces.json) and edited word timings (words_edit.json) from the
Whisper transcript (transcript_src.json) and an energy envelope of the cleaned voice."""
import json, sys, numpy as np
HERE = sys.path[0]
SPEED = 1.10
tx = json.load(open(f"{HERE}/transcript_src.json"))
db = np.load(sys.argv[1])  # 10 ms frames, dBFS of the cleaned voice
KEEP = [0,1,2,3,4,5,6, 9,10,11,12,13,14,15,16, 18,19,20,21,22,23, 24,27, 28,29, 31,32, 34,35,36]
# Whisper slips fixed after a second pass on the clip (and by meaning)
FIX = {(5,"menindal"):"meninggal", (10,"asetnya"):"asasnya", (20,"ketat"):"tertakluk", (20,"lalu."):"kepada", (28,"mecik."):"magik.", (29,"pembelikan"):"pemilikan", (29,"penyelamatan"):"penyerahan",
       (12,"perwasiat."):"pewasiat."}
DROP = {(21,"Tidak"),(21,"tertakluk"),(21,"kepada")}  # sentence 20+21 is one line: "...masih tertakluk kepada proses pentadbiran pusaka."
CROP_START = {27: 120.55}  # drop 'Tetapi,' (its contrast was in the cut lines 25-26)
THR, MIN_GAP, PAD = -40.0, 0.22, 0.07
voiced = db > THR
def first_voiced(t0, t1):
    for f in range(int(t0*100), int(t1*100)):
        if voiced[f:f+3].all(): return f/100
    return t0
def last_voiced(t0, t1):
    for f in range(int(t1*100), int(t0*100), -1):
        if voiced[f-3:f].all(): return f/100
    return t1
spans = []
for k in KEEP:
    ws = tx[k]["words"]
    prev_end = tx[k-1]["words"][-1]["e"] if k > 0 else 0
    nxt_start = tx[k+1]["words"][0]["s"] if k+1 < len(tx) else len(db)/100
    a = first_voiced(max(prev_end - 0.1, ws[0]["s"] - 0.35), ws[0]["s"] + 0.4)
    b = last_voiced(ws[-1]["e"] - 0.5, min(nxt_start + 0.1, ws[-1]["e"] + 0.35))
    a = max(0, a - PAD)
    if k in CROP_START: a = CROP_START[k]
    spans.append([k, a, b + PAD])
# merge spans of consecutive sentences that touch
pieces = []
for k, a, b in spans:
    # split on internal silences
    f0, f1 = int(a*100), int(b*100)
    cur = a; f = f0
    while f < f1:
        if not voiced[f]:
            g = f
            while g < f1 and not voiced[g]: g += 1
            if (g - f)/100 >= MIN_GAP and f/100 - cur > 0.15 and f1/100 - g/100 > 0.1:
                pieces.append([k, cur, f/100 + PAD]); cur = g/100 - PAD
            f = g
        else: f += 1
    pieces.append([k, cur, b])
FR = 30.0  # snap to the source frame grid so video and audio cut on the same instants
pieces = [[k, round(a * FR) / FR, round(b * FR) / FR] for k, a, b in pieces]
pieces = [p for p in pieces if p[2] - p[1] >= 2 / FR]
# words onto the edited timeline
out, words, t = [], [], 0.0
for i, (k, a, b) in enumerate(pieces):
    od = (b - a) / SPEED
    out.append({"i": i, "sent": k, "s0": round(a, 3), "s1": round(b, 3), "out0": round(t, 3), "od": round(od, 3)})
    t += od
for wi_, w in [(j, w) for k in KEEP for j, w in enumerate(tx[k]["words"]) if (k, w["w"].strip()) not in DROP and not (k in CROP_START and w["e"] <= CROP_START[k] + 0.05)]:
    pass
for k in KEEP:
    ps = [p for p in out if p["sent"] == k]
    for w in tx[k]["words"]:
        if (k, w["w"].strip()) in DROP or (k in CROP_START and w["e"] <= CROP_START[k] + 0.05): continue
        ov = [(min(w["e"], p["s1"]) - max(w["s"], p["s0"]), p) for p in ps]
        best = max(ov, key=lambda x: x[0])
        if best[0] <= 0:  # word falls in a removed pause: take the next piece
            nxt = [p for p in ps if p["s0"] >= w["s"]]
            p = nxt[0] if nxt else ps[-1]
        else: p = best[1]
        ws, we = min(max(w["s"], p["s0"]), p["s1"] - 0.05), max(min(w["e"], p["s1"]), p["s0"] + 0.05)
        if we <= ws: we = ws + 0.05
        txt = FIX.get((k, w["w"].strip()), w["w"].strip())
        words.append({"text": txt, "start": round(p["out0"] + (ws - p["s0"]) / SPEED, 3),
                      "end": round(p["out0"] + (we - p["s0"]) / SPEED, 3), "sent": k, "src": round(w["s"], 2)})
words.sort(key=lambda w: w["start"])
merged = []
for w in words:  # Whisper splits reduplicated words: "waris" "-waris"
    if w["text"].startswith("-") and merged:
        merged[-1]["text"] += w["text"]; merged[-1]["end"] = w["end"]
    else: merged.append(w)
words = merged
for a_, b_ in zip(words, words[1:]):
    if b_["start"] < a_["end"]: a_["end"] = b_["start"]
json.dump(out, open(f"{HERE}/pieces.json", "w"), indent=0)
json.dump(words, open(f"{HERE}/words_edit.json", "w"), indent=0, ensure_ascii=False)
print(f"pieces {len(out)}  total {t:.2f}s  words {len(words)}")
for s in sorted(set(w['sent'] for w in words)):
    ww = [w for w in words if w['sent'] == s]
    print(f"{ww[0]['start']:6.2f}-{ww[-1]['end']:6.2f} [{s:2d}] " + " ".join(w['text'] for w in ww))
