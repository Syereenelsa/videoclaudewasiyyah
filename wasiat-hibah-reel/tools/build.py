#!/usr/bin/env python3
"""Generate the Wasiat vs Hibah reel HyperFrames project (index.html + compositions/*).

Inputs (tools/): words_edit.json + pieces.json (from cutlist.py), grade.json.
Re-run after changing timings or copy. Keeps the colour grade already on #aroll.
"""
import json, os, re, html, wave
from icons import icon

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
W, H = 1080, 1920
words = json.load(open(os.path.join(HERE, "words_edit.json")))
pieces = json.load(open(os.path.join(HERE, "pieces.json")))
D = round(pieces[-1]["out0"] + pieces[-1]["od"], 2)
SPEED = 1.10
# Scene, SFX and effect times below were authored on the first cut (pieces_v1.json).
# M() maps an authored time to the current cut through the source clock, so the
# animations stay on their words after the cut list changes.
pieces_v1 = json.load(open(os.path.join(HERE, "pieces_v1.json")))
D_OLD = round(pieces_v1[-1]["out0"] + pieces_v1[-1]["od"], 2)
def M(t):
    old = next((p for p in reversed(pieces_v1) if p["out0"] <= t + 1e-6), pieces_v1[0])
    src = old["s0"] + (t - old["out0"]) * SPEED
    cand = [p for p in pieces if p["s0"] - 1e-6 <= src <= p["s1"] + 1e-6]
    if cand:
        p = next((c for c in cand if c["sent"] == old["sent"]), cand[0])
        return round(min(D, p["out0"] + (src - p["s0"]) / SPEED), 3)
    nxt = [p for p in pieces if p["s0"] > src]
    return round(nxt[0]["out0"] if nxt else D, 3)
os.makedirs(os.path.join(PROJ, "compositions"), exist_ok=True)

GOLD, ICE, RED, GREEN, NAVY = "#E9C46A", "#9ADBFF", "#FF6B6B", "#5EE6A8", "#0B1F3A"

# Layout (1080x1920). Face sits at y 640 (hijab top) .. 1230 (chin).
# Cards: y 270..630 (above the head). Captions: bottom-anchored at y 1420, x 140..900
# (clear of the TikTok/Reels/Shorts username + caption block below y 1480 and the
# like/comment/share rail at x > 950).
PANEL_TOP = 270

BASE_CSS = """
#ROOT{position:absolute;inset:0;overflow:visible;font-family:'Montserrat',sans-serif;color:#FFF8E7;pointer-events:none}
#ROOT .panel{position:absolute;left:100px;width:800px;top:322px;border-radius:38px;
  background:linear-gradient(165deg,rgba(16,36,68,.93),rgba(6,15,32,.91));
  border:1.5px solid rgba(233,196,106,.45);
  box-shadow:0 30px 70px rgba(0,0,0,.50),inset 0 1px 0 rgba(255,255,255,.10);
  backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);overflow:visible}
#ROOT .krow{position:absolute;left:0;right:0;top:-26px;display:flex;justify-content:center}
#ROOT .kick{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#F6D98B,#E2B65A);
  color:#0B1F3A;font-weight:800;font-size:30px;letter-spacing:.06em;padding:10px 24px;border-radius:999px;
  text-transform:uppercase;box-shadow:0 10px 24px rgba(0,0,0,.35);white-space:nowrap}
#ROOT .num{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:50%;
  background:#0B1F3A;color:#F2CF76;font-weight:900;font-size:28px;letter-spacing:0}
#ROOT .row{position:absolute;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:18px;text-align:center}
#ROOT .t-sm{font-weight:700;font-size:32px;color:rgba(255,248,231,.86)}
#ROOT .t-md{font-weight:800;font-size:44px;letter-spacing:-.01em}
#ROOT .t-lg{font-weight:900;font-size:64px;letter-spacing:-.02em;line-height:1}
#ROOT .t-xl{font-weight:900;font-size:110px;letter-spacing:-.03em;line-height:1}
#ROOT .gold{background:linear-gradient(180deg,#FFF0C2 0%,#F2CF76 45%,#C9962E 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
#ROOT .ice{background:linear-gradient(180deg,#FFFFFF 0%,#CFEFFF 45%,#6EC6FF 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
#ROOT .redt{color:#FF7A7A}
#ROOT .greent{color:#6CF0B4}
#ROOT .col{position:absolute;top:58px;width:362px;display:flex;flex-direction:column;align-items:center;gap:14px}
#ROOT .col.l{left:22px} #ROOT .col.r{right:22px}
#ROOT .vline{position:absolute;left:399px;top:64px;bottom:28px;width:2px;background:linear-gradient(180deg,rgba(233,196,106,0),rgba(233,196,106,.6),rgba(233,196,106,0))}
#ROOT .vs{position:absolute;left:372px;top:66px;width:56px;height:56px;border-radius:50%;background:#0B1F3A;border:2px solid rgba(233,196,106,.7);
  color:#F2CF76;font-weight:900;font-size:28px;display:flex;align-items:center;justify-content:center}
#ROOT .hd{display:inline-flex;align-items:center;gap:10px;padding:8px 20px;border-radius:16px;font-weight:900;font-size:38px;letter-spacing:.06em}
#ROOT .hd.w{background:rgba(233,196,106,.16);border:1.5px solid rgba(233,196,106,.6);color:#FFE3A0}
#ROOT .hd.h{background:rgba(94,230,168,.14);border:1.5px solid rgba(94,230,168,.6);color:#A8F5D2}
#ROOT .it{display:flex;align-items:center;gap:12px;width:100%;padding:12px 16px;border-radius:20px;
  background:rgba(255,248,231,.07);border:1.5px solid rgba(255,248,231,.14);font-weight:800;font-size:30px;line-height:1.12;text-align:left}
#ROOT .it .ico{flex:none}
#ROOT .it small{display:block;font-weight:600;font-size:28px;color:rgba(255,248,231,.72);margin-top:3px}
#ROOT .chip{display:inline-flex;align-items:center;gap:10px;padding:10px 18px;border-radius:18px;
  background:rgba(255,248,231,.08);border:1.5px solid rgba(255,248,231,.18);font-weight:800;font-size:30px;white-space:nowrap}
#ROOT .pill{display:inline-flex;align-items:center;gap:10px;padding:10px 20px;border-radius:999px;
  background:rgba(233,196,106,.16);border:1.5px solid rgba(233,196,106,.55);font-weight:800;font-size:30px;color:#FFE9AE}
#ROOT .stamp{display:inline-flex;align-items:center;gap:14px;padding:10px 28px;border:5px solid currentColor;border-radius:18px;
  font-weight:900;font-size:52px;letter-spacing:.05em;background:rgba(6,15,32,.55)}
"""

JS_HELPERS = """
const tl = gsap.timeline({ paused: true });
const IN=(s,t,o={})=>tl.fromTo(s,{opacity:0,y:o.y??26,scale:o.s??0.94,filter:'blur(8px)'},{opacity:1,y:0,scale:1,filter:'blur(0px)',duration:o.d??0.42,ease:o.e??'power3.out',stagger:o.st??0},t);
const POP=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??0.35},{opacity:1,scale:1,duration:o.d??0.5,ease:'back.out(2.2)',stagger:o.st??0},t);
const SLAM=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??1.9,filter:'blur(10px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:o.d??0.24,ease:'power4.in'},t);
const SLIDE=(s,t,o={})=>tl.fromTo(s,{opacity:0,x:o.x??-40},{opacity:1,x:0,duration:o.d??0.4,ease:'power3.out',stagger:o.st??0},t);
const OUT=(s,t,d=0.28)=>tl.to(s,{opacity:0,y:-18,filter:'blur(8px)',duration:d,ease:'power2.in'},t);
const DIM=(s,t,o=0.5)=>tl.to(s,{opacity:o,duration:0.3,ease:'power2.out'},t);
"""


def css(sid, extra=""):
    return (BASE_CSS + extra).replace("#ROOT", f"#{sid}")


SCENES = []


def add_scene(sid, start, end, extra_css, body, js):
    SCENES.append((sid, M(start), M(end)))
    with open(os.path.join(PROJ, "compositions", f"{sid}.html"), "w") as f:
        f.write(f"""<template>
  <style>{css(sid, extra_css)}</style>
  <div id="{sid}" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
{JS_HELPERS}
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
""")


def L(start):
    return lambda g: round(M(g) - M(start), 3)


def kick(n, text, extra=""):
    lead = f'<span class="num">{n}</span>' if n else ""
    return f'<div class="krow"><span class="kick" id="{extra}">{lead}{text}</span></div>'


def it(iid, ic, col, text, sub=""):
    sub = f"<small>{sub}</small>" if sub else ""
    return f'<div class="it" id="{iid}">{icon(ic, 40, col, 2.3)}<div>{text}{sub}</div></div>'


# ================================================================ 1. HOOK (0 - 4.8)
s0, s1 = 0.0, 4.8; t = L(s0)
add_scene("hook", s0, s1, """
#hook .dim{position:absolute;inset:0;opacity:0;background:linear-gradient(180deg,rgba(4,12,28,.86) 0%,rgba(4,12,28,.6) 40%,rgba(4,12,28,.1) 62%,rgba(4,12,28,0) 100%)}
#hook .wrap{position:absolute;left:120px;width:768px;top:320px;text-align:center}
#hook .tag{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#FF8A8A,#E05555);color:#fff;font-weight:900;font-size:30px;letter-spacing:.1em;padding:10px 24px;border-radius:999px;box-shadow:0 10px 24px rgba(0,0,0,.4)}
#hook .l1{font-weight:800;font-size:58px;margin-top:26px;text-shadow:0 6px 26px rgba(0,0,0,.7)}
#hook .l2{display:flex;justify-content:center;align-items:center;gap:20px;margin-top:10px}
#hook .big{font-weight:900;font-size:118px;letter-spacing:-.03em;line-height:1;filter:drop-shadow(0 8px 28px rgba(0,0,0,.6))}
#hook .eq{font-weight:900;font-size:96px;color:#FFF8E7;position:relative}
#hook .l3{font-weight:900;font-size:110px;letter-spacing:-.02em;line-height:1;margin-top:10px;filter:drop-shadow(0 8px 28px rgba(0,0,0,.6))}
""", f"""
    <div class="dim" id="hk-dim"></div>
    <div class="wrap">
      <span class="tag" id="hk-tag">{icon('alert',32,'#fff',2.6)} SALAH FAHAM BIASA</span>
      <div class="l1" id="hk-l1">Ramai ingat, dah tulis <span style="color:#FFD873">wasiat</span>…</div>
      <div class="l2" id="hk-l2"><span id="hk-house">{icon('home',104,GOLD,2.2)}</span><span class="big gold" id="hk-rumah">RUMAH</span></div>
      <div class="l1" id="hk-auto" style="margin-top:14px">automatik jadi</div>
      <div class="l3" id="hk-l3"><span class="ice" id="hk-anak">HAK ANAK?</span></div>
    </div>
""", f"""
    DIM('#hk-dim',0,1);
    POP('#hk-tag',0.05,{{s:0.5}});
    IN('#hk-l1',{t(0.3)});
    POP('#hk-house',{t(2.5)},{{s:0.2}});
    SLAM('#hk-rumah',{t(2.56)},{{s:2.2}});
    IN('#hk-auto',{t(2.75)},{{y:20}});
    SLAM('#hk-anak',{t(3.66)},{{s:2.4,d:0.2}});
    tl.fromTo('#hk-anak',{{scale:1}},{{scale:1.08,duration:0.25,yoyo:true,repeat:1,ease:'sine.inOut',immediateRender:false}},{t(4.1)});
    tl.to('#hk-l1,#hk-l2,#hk-l3,#hk-tag',{{opacity:0.25,filter:'blur(3px)',duration:0.2}},{t(4.75)});
""")

# ================================================================ 2. TIDAK SEMESTINYA (4.8 - 7.05)
s0, s1 = 4.8, 7.05; t = L(s0)
add_scene("tidak", s0, s1, """
#tidak .dim{position:absolute;inset:0;opacity:1;background:linear-gradient(180deg,rgba(4,12,28,.86) 0%,rgba(4,12,28,.6) 40%,rgba(4,12,28,.1) 62%,rgba(4,12,28,0) 100%)}
#tidak .wrap{position:absolute;left:120px;width:768px;top:420px;text-align:center}
#tidak .sub{font-weight:800;font-size:48px;text-shadow:0 6px 26px rgba(0,0,0,.7)}
""", f"""
    <div class="dim" id="td-dim"></div>
    <div class="wrap">
      <div class="sub" id="td-sub">Tapi sebenarnya…</div>
      <div style="margin-top:34px"><span class="stamp redt" id="td-stamp" style="font-size:52px;white-space:nowrap;padding:10px 20px">{icon('x',50,RED,3.4)} TIDAK SEMESTINYA</span></div>
    </div>
""", f"""
    IN('#td-sub',0.02);
    tl.fromTo('#td-stamp',{{opacity:0,scale:2.6,rotation:-14}},{{opacity:1,scale:1,rotation:-5,duration:0.22,ease:'power4.in'}},{t(5.6)});
    tl.to('#td-dim',{{opacity:0.0,duration:0.2}},{t(6.85)});
    OUT('#td-sub,#td-stamp',{t(6.8)},0.22);
""")

# ================================================================ 3. GIANT HOOK: WASIAT ≠ HIBAH (7.05 - 9.6)
s0, s1 = 7.05, 10.35; t = L(s0)
add_scene("giant", s0, s1, """
#giant .dim{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 45%,rgba(8,22,46,.80),rgba(2,6,16,.94))}
#giant .stack{position:absolute;left:120px;width:768px;top:330px;text-align:center}
#giant .g{font-weight:900;font-size:176px;letter-spacing:-.04em;line-height:.9}
#giant .ne{font-weight:900;font-size:150px;line-height:.9;color:#FF7A7A;filter:drop-shadow(0 0 40px rgba(255,107,107,.55));margin:10px 0}
#giant .cap{display:inline-block;margin-top:34px;font-weight:800;font-size:44px;letter-spacing:.1em;color:#FFF8E7;padding:10px 22px;border-top:3px solid rgba(233,196,106,.7);border-bottom:3px solid rgba(233,196,106,.7)}
""", f"""
    <div class="dim" id="gi-dim"></div>
    <div class="stack">
      <div class="g gold" id="gi-w" style="filter:drop-shadow(0 0 36px rgba(233,196,106,.45))">WASIAT</div>
      <div class="ne" id="gi-ne">≠</div>
      <div class="g" id="gi-h" style="color:#A8F5D2;filter:drop-shadow(0 0 36px rgba(94,230,168,.45))">HIBAH</div>
      <div class="cap" id="gi-cap">DUA PERKARA BERBEZA</div>
    </div>
""", f"""
    DIM('#gi-dim',0,1);
    SLAM('#gi-w',{t(7.42)},{{s:2.6,d:0.2}});
    SLAM('#gi-h',{t(8.05)},{{s:2.6,d:0.2}});
    tl.fromTo('#gi-ne',{{opacity:0,scale:0,rotation:-180}},{{opacity:1,scale:1,rotation:0,duration:0.4,ease:'back.out(2.4)'}},{t(8.6)});
    IN('#gi-cap',{t(8.7)},{{y:20,d:0.3}});
    tl.to('#giant .stack',{{scale:1.15,opacity:0,filter:'blur(14px)',duration:0.2,ease:'power3.in'}},{t(10.12)});
    tl.to('#gi-dim',{{opacity:0,duration:0.2}},{t(10.12)});
""")

# ================================================================ 4. EMPAT PERBEZAAN (9.6 - 14.1)
s0, s1 = 10.35, 14.1; t = L(s0)
dots = "".join(f'<span class="dot" id="em-d{i}">{i}</span>' for i in range(1, 5))
add_scene("empat", s0, s1, """
#empat .dot{display:inline-flex;align-items:center;justify-content:center;width:112px;height:112px;border-radius:30px;
  background:linear-gradient(180deg,#F6D98B,#D9A845);color:#0B1F3A;font-weight:900;font-size:66px;box-shadow:0 14px 30px rgba(0,0,0,.4)}
""", f"""
    <div class="panel" id="em-panel" style="height:330px">
      {kick(0, f"{icon('list',30,NAVY,2.6)} Hari ini saya kongsikan", "em-kick")}
      <div class="row" style="top:48px"><span class="t-xl gold" id="em-4" style="font-size:96px">4</span><span class="t-lg" id="em-t" style="font-size:54px">PERBEZAAN PENTING</span></div>
      <div class="row" style="top:150px;gap:26px">{dots}</div>
      <div class="row" style="top:278px"><span class="t-sm" id="em-sub">yang setiap <b style="color:#FFD873">pemilik aset</b> kena tahu</span></div>
    </div>
""", f"""
    IN('#em-panel',0.02,{{y:-30}});
    POP('#em-kick',0.1);
    SLAM('#em-4',{t(10.55)},{{s:2.4}});
    IN('#em-t',{t(10.65)},{{y:16}});
    POP('#em-d1,#em-d2,#em-d3,#em-d4',{t(11.1)},{{st:0.12}});
    IN('#em-sub',{t(12.1)});
    OUT('#em-panel',{t(13.85)});
""")


# ================================================================ versus scene helper
def versus(sid, s0, s1, n, kicker, height, left, right, extra_js="", extra_css="", hd_l=None, hd_r=None):
    """left/right: list of (html, global_time, anim)."""
    t = L(s0)
    lh = "".join(h for h, _, _ in left)
    rh = "".join(h for h, _, _ in right)
    js = f"""
    IN('#{sid}-panel',0.02,{{y:-30}});
    POP('#{sid}-kick',0.1);
    POP('#{sid}-hl',{t(hd_l)},{{s:0.5}});
    POP('#{sid}-hr',{t(hd_r)},{{s:0.5}});
    tl.fromTo('#{sid}-vl',{{scaleY:0}},{{scaleY:1,duration:0.5,ease:'power2.out'}},0.3);
    POP('#{sid}-vs',0.35);
"""
    for h, tt, anim in left + right:
        iid = re.search(r'id="([\w-]+)"', h).group(1)
        js += f"    {anim}('#{iid}',{t(tt)});\n"
    js += extra_js(t) if callable(extra_js) else extra_js
    js += f"    OUT('#{sid}-panel',{t(s1 - 0.28)});\n"
    add_scene(sid, s0, s1, extra_css, f"""
    <div class="panel" id="{sid}-panel" style="height:{height}px">
      {kick(n, kicker, f"{sid}-kick")}
      <div class="vline" id="{sid}-vl"></div><div class="vs" id="{sid}-vs">VS</div>
      <div class="col l"><span class="hd w" id="{sid}-hl">{icon('file',38,'#FFE3A0',2.4)} WASIAT</span>{lh}</div>
      <div class="col r"><span class="hd h" id="{sid}-hr">{icon('gift',38,'#A8F5D2',2.4)} HIBAH</span>{rh}</div>
    </div>
""", js)


# ================================================================ 5. #1 BILA BERKUAT KUASA (14.1 - 22.9)
versus("p1", 14.1, 22.9, 1, "Bila berkuat kuasa?", 300,
       [(it("p1-a", "hourglass", GOLD, "Selepas", "kita meninggal dunia"), 17.83, "SLIDE")],
       [(it("p1-b", "heart", GREEN, "Semasa", "kita masih hidup"), 21.3, "SLIDE")],
       hd_l=16.95, hd_r=19.6)

# ================================================================ 6. #2 KEPADA SIAPA (22.9 - 45.1)
versus("p2", 22.9, 45.1, 2, "Kepada siapa?", 392,
       [(it("p2-a", "check", GREEN, "Bukan waris faraid"), 28.35, "SLIDE"),
        (it("p2-b", "users", GOLD, "Kepada waris", "perlu setuju waris lain"), 31.2, "SLIDE")],
       [(it("p2-c", "check", GREEN, "Sesiapa sahaja"), 41.05, "SLIDE"),
        ('<div class="it" id="p2-d" style="justify-content:center;gap:10px;flex-wrap:wrap;padding:10px 10px">'
         '<span class="chip" id="p2-d1" style="font-size:28px;padding:6px 10px">anak</span>'
         '<span class="chip" id="p2-d2" style="font-size:28px;padding:6px 10px">isteri</span>'
         '<span class="chip" id="p2-d3" style="font-size:28px;padding:6px 10px">ibu bapa</span></div>', 42.6, "IN")],
       hd_l=26.1, hd_r=39.25,
       extra_js=lambda t: f"""    tl.fromTo('#p2-b small',{{color:'rgba(255,248,231,.72)'}},{{color:'#FF9A9A',duration:0.2,immediateRender:false}},{t(35.25)});
    tl.fromTo('#p2-b',{{borderColor:'rgba(255,248,231,.14)'}},{{borderColor:'rgba(255,122,122,.8)',duration:0.2,immediateRender:false}},{t(35.25)});
    POP('#p2-d1',{t(43.25)});POP('#p2-d2',{t(43.8)});POP('#p2-d3',{t(44.45)});
""")

# ================================================================ 7. #3 BERAPA BANYAK (45.1 - 58.1)
R = 46; C = 2 * 3.14159 * R
pie = (f'<svg width="120" height="120" viewBox="0 0 120 120" class="ico"><circle cx="60" cy="60" r="{R}" fill="none" stroke="rgba(255,248,231,.14)" stroke-width="22"/>'
       f'<circle id="PID" cx="60" cy="60" r="{R}" fill="none" stroke="COL" stroke-width="22" stroke-dasharray="0 {C:.1f}" transform="rotate(-90 60 60)"/></svg>')
versus("p3", 45.1, 58.1, 3, "Berapa banyak?", 350,
       [(f'<div class="it" id="p3-a" style="justify-content:center;gap:18px">{pie.replace("PID","p3-pa").replace("COL",GOLD)}'
         f'<div><span style="font-size:62px;font-weight:900" class="gold">1/3</span><small>maksimum harta pusaka bersih</small></div></div>', 48.55, "IN")],
       [(f'<div class="it" id="p3-b" style="justify-content:center;gap:18px">{pie.replace("PID","p3-pb").replace("COL",GREEN)}'
         f'<div><span style="font-size:50px;font-weight:900;color:#A8F5D2">TIADA HAD</span><small>1/3 seperti wasiat</small></div></div>', 54.6, "IN")],
       hd_l=48.55, hd_r=54.6,
       extra_js=lambda t: f"""    tl.to('#p3-pa',{{attr:{{'stroke-dasharray':'{C/3:.1f} {C:.1f}'}},duration:0.7,ease:'power2.out'}},{t(51.3)});
    tl.to('#p3-pb',{{attr:{{'stroke-dasharray':'{C:.1f} {C:.1f}'}},duration:0.9,ease:'power2.out'}},{t(55.45)});
""")

# ================================================================ 8. #4 PALING RAMAI TAK TAHU (58.1 - 76.5)
versus("p4", 58.1, 76.5, 4, f"Paling ramai tak tahu {icon('alert',28,NAVY,2.6)}", 380,
       [(it("p4-a", "lock", GOLD, "Tertakluk", "proses pentadbiran pusaka"), 62.5, "SLIDE")],
       [(it("p4-b", "shield", GREEN, "Sah &amp; sempurna"), 67.0, "SLIDE"),
        (it("p4-c", "check", GREEN, "Keluar dari pusaka", "tak tertakluk faraid"), 70.95, "SLIDE")],
       hd_l=60.85, hd_r=66.45,
       extra_js=lambda t: f"""    tl.fromTo('#p4-c',{{borderColor:'rgba(255,248,231,.14)',background:'rgba(255,248,231,.07)'}},{{borderColor:'rgba(94,230,168,.85)',background:'rgba(94,230,168,.12)',duration:0.25,immediateRender:false}},{t(73.8)});
""")

# ================================================================ 9. CONTOH ENCIK ALI (76.5 - 86.2)
s0, s1 = 76.5, 86.2; t = L(s0)
add_scene("contoh", s0, s1, """
#contoh .node{display:flex;flex-direction:column;align-items:center;gap:6px;font-weight:800;font-size:32px}
#contoh .circ{width:112px;height:112px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(255,248,231,.08);border:2px solid rgba(233,196,106,.6)}
#contoh .arw{position:relative;width:110px;height:6px;border-radius:3px;background:rgba(255,248,231,.15);overflow:hidden}
#contoh .arw i{position:absolute;inset:0;background:linear-gradient(90deg,#E9C46A,#5EE6A8);transform-origin:0 50%}
""", f"""
    <div class="panel" id="ct-panel" style="height:360px">
      {kick(0, f"{icon('help',30,NAVY,2.6)} Contoh", "ct-kick")}
      <div class="row" style="top:56px;gap:22px">
        <div class="node" id="ct-ali"><div class="circ">{icon('users',58,GOLD,2)}</div>Encik Ali</div>
        <div class="arw"><i id="ct-a1"></i></div>
        <div class="node" id="ct-rumah"><div class="circ">{icon('home',58,GOLD,2)}</div>Rumah</div>
        <div class="arw"><i id="ct-a2"></i></div>
        <div class="node" id="ct-isteri"><div class="circ" style="border-color:rgba(94,230,168,.8)">{icon('heart',58,GREEN,2)}</div>Isteri</div>
      </div>
      <div class="row" style="top:250px;gap:16px"><span class="pill" id="ct-hibah" style="background:rgba(94,230,168,.14);border-color:rgba(94,230,168,.7);color:#A8F5D2">{icon('gift',32,GREEN,2.4)} Hibah betul &amp; sah</span>
        <span class="stamp greent" id="ct-milik" style="font-size:38px;padding:6px 18px;border-width:4px">{icon('check',36,GREEN,3.2)} MILIK ISTERI</span></div>
    </div>
""", f"""
    IN('#ct-panel',0.02,{{y:-30}});
    POP('#ct-kick',0.1);
    POP('#ct-ali',{t(77.3)});
    tl.fromTo('#ct-a1',{{scaleX:0}},{{scaleX:1,duration:0.45,ease:'power2.out'}},{t(77.95)});
    POP('#ct-rumah',{t(78.35)});
    tl.fromTo('#ct-a2',{{scaleX:0}},{{scaleX:1,duration:0.45,ease:'power2.out'}},{t(78.8)});
    POP('#ct-isteri',{t(79.3)});
    POP('#ct-hibah',{t(80.15)});
    tl.fromTo('#ct-milik',{{opacity:0,scale:2.2,rotation:-10}},{{opacity:1,scale:1,rotation:-3,duration:0.22,ease:'power4.in'}},{t(83.3)});
    OUT('#ct-panel',{t(85.92)});
""")

# ================================================================ 10. HIBAH BUKAN MAGIK (86.2 - 95.2)
s0, s1 = 86.2, 95.2; t = L(s0)
add_scene("magik", s0, s1, "", f"""
    <div class="panel" id="mg-panel" style="height:350px;border-color:rgba(255,122,122,.6)">
      <div class="krow"><span class="kick" id="mg-kick" style="background:linear-gradient(180deg,#FF9A9A,#E05555);color:#fff">{icon('alert',30,'#fff',2.6)} Tapi ingat</span></div>
      <div class="row" style="top:44px"><span class="t-lg" id="mg-t" style="font-size:62px">HIBAH <span class="redt">BUKAN</span> MAGIK</span></div>
      <div class="row" style="top:138px;gap:14px"><span class="chip" id="mg-c1">{icon('x',32,RED,3)} Syarat tak dipenuhi</span></div>
      <div class="row" style="top:206px;gap:14px"><span class="chip" id="mg-c2">isu pemilikan</span><span class="chip" id="mg-c3">penyerahan harta</span></div>
      <div class="row" style="top:278px"><span class="stamp redt" id="mg-st" style="font-size:40px;padding:6px 20px;border-width:4px">{icon('scale',38,RED,2.6)} BOLEH DIPERTIKAIKAN</span></div>
    </div>
""", f"""
    IN('#mg-panel',0.02,{{y:-30}});
    POP('#mg-kick',0.1);
    SLAM('#mg-t',{t(87.45)},{{s:1.8}});
    POP('#mg-c1',{t(89.55)});
    POP('#mg-c2',{t(92.05)});
    POP('#mg-c3',{t(92.85)});
    tl.fromTo('#mg-st',{{opacity:0,scale:2.4,rotation:-12}},{{opacity:1,scale:1,rotation:-3,duration:0.22,ease:'power4.in'}},{t(94.1)});
    OUT('#mg-panel',{t(94.92)});
""")

# ================================================================ 11. SALING MELENGKAPI (95.2 - 100.9)
s0, s1 = 95.2, 100.9; t = L(s0)
add_scene("lengkap", s0, s1, "", f"""
    <div class="panel" id="lk-panel" style="height:310px">
      {kick(0, f"{icon('check',30,NAVY,2.8)} Tak perlu pilih", "lk-kick")}
      <div class="row" style="top:62px;gap:24px">
        <span class="hd w" id="lk-w" style="font-size:54px">{icon('file',50,'#FFE3A0',2.4)} WASIAT</span>
        <span id="lk-plus">{icon('plus',64,'#FFF8E7',3)}</span>
        <span class="hd h" id="lk-h" style="font-size:54px">{icon('gift',50,'#A8F5D2',2.4)} HIBAH</span>
      </div>
      <div class="row" style="top:196px"><span class="t-lg gold" id="lk-t" style="font-size:62px">SALING MELENGKAPI</span></div>
    </div>
""", f"""
    IN('#lk-panel',0.02,{{y:-30}});
    POP('#lk-kick',0.1);
    SLIDE('#lk-w',{t(97.85)},{{x:-120}});
    SLIDE('#lk-h',{t(98.5)},{{x:120}});
    tl.fromTo('#lk-plus',{{opacity:0,scale:0,rotation:-90}},{{opacity:1,scale:1,rotation:0,duration:0.4,ease:'back.out(2.4)'}},{t(99.55)});
    SLAM('#lk-t',{t(100.0)},{{s:1.8}});
    OUT('#lk-panel',{t(100.65)},0.22);
""")

# ================================================================ 12. CTA (100.9 - end)
s0, s1 = 100.9, D_OLD; t = L(s0)
add_scene("cta", s0, s1, """
#cta .bub{display:inline-flex;align-items:center;gap:14px;padding:14px 26px;border-radius:26px 26px 26px 6px;background:#FFF8E7;color:#0B1F3A;font-weight:900;font-size:46px;box-shadow:0 16px 36px rgba(0,0,0,.45)}
#cta .btn{display:inline-flex;align-items:center;gap:12px;padding:12px 26px;border-radius:999px;background:linear-gradient(180deg,#FF6A88,#E2365B);color:#fff;font-weight:900;font-size:36px;box-shadow:0 12px 28px rgba(226,54,91,.45)}
""", f"""
    <div class="panel" id="cta-panel" style="height:350px">
      {kick(0, f"{icon('list',30,NAVY,2.6)} Nak checklist perancangan?", "cta-kick")}
      <div class="row" style="top:52px"><span class="t-sm" id="cta-l">Wasiat &amp; hibah</span></div>
      <div class="row" style="top:100px"><span class="bub" id="cta-bub">{icon('msg',46,NAVY,2.4)} Komen “HIBAH”</span></div>
      <div class="row" style="top:206px"><span class="btn" id="cta-btn">{icon('userplus',36,'#fff',2.6)} Follow untuk PART 2</span></div>
      <div class="row" style="top:288px"><span class="t-sm" id="cta-p2">Jenis-jenis hibah &amp; mana yang sesuai</span></div>
    </div>
""", f"""
    IN('#cta-panel',0.02,{{y:-30}});
    POP('#cta-kick',0.1);
    IN('#cta-l',{t(102.2)});
    POP('#cta-bub',{t(103.55)});
    tl.fromTo('#cta-bub',{{rotation:0}},{{rotation:-3,duration:0.12,yoyo:true,repeat:3,ease:'sine.inOut',immediateRender:false}},{t(104.1)});
    POP('#cta-btn',{t(104.9)});
    tl.fromTo('#cta-btn',{{scale:1}},{{scale:1.07,duration:0.35,yoyo:true,repeat:5,ease:'sine.inOut',immediateRender:false}},{t(105.9)});
    IN('#cta-p2',{t(107.6)});
""")

# ================================================================ CAPTIONS
HIDE = [(0.0, M(10.35))]  # hook, stamp and giant hook already carry those words  # the giant hook carries those words
KEY = set("""wasiat wasiat, hibah hibah. hibah? faraid faraid. waris waris-waris rumah rumahnya anak anak. isteri isteri. suami
meninggal hidup sesiapa satu per tiga had tertakluk pentadbiran pusaka pusaka. sah sah, sempurna magik. dipertikaikan
melengkapi. komen follow part 2. empat perbezaan tidak semestinya. berbeza. persetujuan""".split())
cw = [w for w in words if not any(a <= w["start"] < b for a, b in HIDE)]
groups, cur = [], []
for w in cw:
    if cur:
        prev = cur[-1]
        txt = " ".join(x["text"] for x in cur + [w])
        if (prev["sent"] != w["sent"] or prev["text"][-1] in ",.?" or w["start"] - prev["end"] > 0.2
                or len(cur) >= 3 or len(txt) > 18):
            groups.append(cur); cur = []
    cur.append(w)
groups.append(cur)

cap_html = []
for gi, g in enumerate(groups):
    g0 = max(0.05, g[0]["start"] - 0.06)
    nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else D
    g1 = min(nxt, g[-1]["end"] + 0.45)
    spans = []
    for wi, w in enumerate(g):
        clean = w["text"].lower()
        k = " k" if clean in KEY or clean.strip(",.?") in KEY else ""
        disp = html.escape(w["text"].rstrip(","))
        spans.append(f'<span class="w{k}" id="cw{gi}_{wi}" data-t="{w["start"]:.3f}">{disp}</span>')
    est = sum(0.66 if c.isupper() or c.isdigit() else (0.3 if c in " .,'il-" else 0.6) for c in " ".join(x["text"] for x in g)) * 60
    fs = f' style="font-size:{max(42, int(60 * 600 / est))}px"' if est > 600 else ""
    cap_html.append(f'      <div class="grp" id="cg{gi}" data-a="{g0:.3f}" data-b="{g1:.3f}"{fs}><span class="pb">{" ".join(spans)}</span></div>')

with open(os.path.join(PROJ, "compositions", "captions.html"), "w") as f:
    f.write(f"""<template>
  <style>
    #captions{{position:absolute;inset:0;pointer-events:none}}
    #captions .grp{{position:absolute;left:120px;width:768px;bottom:1080px;white-space:nowrap;text-align:center;opacity:0;visibility:hidden;
      font-family:'Montserrat',sans-serif;font-weight:800;font-size:60px;line-height:1.12;letter-spacing:-.01em;color:#FFFFFF;overflow:visible}}
    #captions .pb{{display:inline-block;padding:8px 24px 12px;border-radius:22px;background:rgba(8,22,46,.74);border:1.5px solid rgba(233,196,106,.30);box-shadow:0 12px 30px rgba(0,0,0,.35);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}}
    #captions .w{{display:inline-block;text-shadow:0 3px 0 rgba(0,0,0,.35),0 6px 22px rgba(0,0,0,.75)}}
    #captions .w.k{{color:#FFD873;text-shadow:0 3px 0 rgba(60,40,0,.45),0 0 26px rgba(233,196,106,.45),0 6px 22px rgba(0,0,0,.75)}}
  </style>
  <div id="captions" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(cap_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    document.querySelectorAll('#captions .grp').forEach((g) => {{
      const a = +g.dataset.a, b = +g.dataset.b;
      tl.set(g, {{ visibility: 'visible' }}, a);
      tl.fromTo(g, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.08, immediateRender: false }}, a);
      tl.fromTo(g.querySelector('.pb'), {{ y: 18, scale: 0.9 }}, {{ y: 0, scale: 1, duration: 0.2, ease: 'back.out(2.2)', immediateRender: false }}, a);
      g.querySelectorAll('.w').forEach((w) => {{
        const t = Math.max(a, +w.dataset.t - 0.03);
        tl.fromTo(w, {{ scale: 1 }}, {{ scale: 1.1, duration: 0.1, yoyo: true, repeat: 1, ease: 'power2.out', immediateRender: false }}, t);
      }});
      tl.to(g, {{ opacity: 0, duration: 0.1, ease: 'power2.in' }}, b - 0.1);
      tl.set(g, {{ opacity: 0, visibility: 'hidden' }}, b);
    }});
    window.__timelines["captions"] = tl;
  </script>
</template>
""")

# ================================================================ CAMERA (punch-ins hide the jump cuts)
# Split layout: navy panel area on top (cards + captions), speaker in the stage y 960..1920.
STAGE_T = 960
FX, FY = 505.0, 950.0     # face anchor in source px
# The speaker sits in a framed window (x 100..980, y 975..1920) at 0.82x so the whole
# hijab stays inside the frame, even on the punch-ins.
WIN_L, WIN_T, WIN_W = 100, 975, 880
WIN_H = H - WIN_T
SX, SY = WIN_W / 2, 330.0  # where that anchor sits inside the window (window-relative px)
BASE, PUNCH = 0.84, 0.90
def tf(s):
    x = min(-12.0, max(WIN_W - W * s + 12, SX - FX * s))   # never show the edge of the footage (12 px spare for shakes)
    y = min(0.0, max(WIN_H + 40 - H * s, SY - FY * s))
    return [round(x, 2), round(y, 2), round(s, 4)]
cam, big, held = [], False, 0.0
for i, p in enumerate(pieces):
    if i > 0 and held >= 1.0:
        big = not big; held = 0.0
    held += p["od"]
    sc = PUNCH if big else BASE
    cam.append([round(p["out0"], 3), round(p["od"], 3)] + tf(sc) + tf(sc + 0.015))
# Giant hook: hard punch to 1.25 under the overlay; last segment push-in
GIANT_PUSH = tf(0.95)

# ================================================================ SFX (no music)
SFX = [
    ("whoosh", 0.0, .26), ("pop", 0.05, .26), ("swish", 1.2, .18), ("pop", 2.5, .28), ("impact", 2.56, .34), ("stamp", 3.66, .34),
    ("riser", 4.3, .22), ("stamp", 5.6, .50), ("impact", 5.62, .40),
    ("whoosh", 7.05, .30), ("impact", 7.42, .55), ("impact", 8.05, .45), ("ding", 8.6, .30), ("whoosh", 10.12, .26),
    ("swish", 10.35, .22), ("stamp", 10.5, .38), ("pop", 11.1, .26), ("pop", 11.22, .26), ("pop", 11.34, .26), ("pop", 11.46, .26),
    ("whoosh", 14.1, .24), ("pop", 16.95, .26), ("swish", 17.83, .20), ("clock", 18.2, .16), ("pop", 19.6, .26), ("swish", 21.3, .20),
    ("whoosh", 22.9, .24), ("pop", 26.1, .26), ("ding", 28.35, .24), ("swish", 31.2, .20), ("tick", 35.25, .30),
    ("pop", 39.25, .26), ("ding", 41.05, .24), ("pop", 43.25, .24), ("pop", 43.8, .24), ("pop", 44.45, .24),
    ("whoosh", 45.1, .24), ("pop", 48.55, .26), ("tick", 51.3, .30), ("tick", 51.6, .26), ("tick", 52.0, .26), ("ding", 55.45, .28),
    ("whoosh", 58.1, .24), ("pop", 60.85, .26), ("lock", 62.5, .40), ("pop", 66.45, .26), ("swish", 67.0, .20), ("swish", 70.95, .20), ("ding", 73.8, .28),
    ("whoosh", 76.5, .24), ("pop", 77.3, .24), ("swish", 77.95, .18), ("pop", 78.35, .24), ("swish", 78.8, .18), ("pop", 79.3, .24),
    ("pop", 80.15, .24), ("stamp", 83.3, .36), ("ding", 83.4, .24),
    ("whoosh", 86.2, .24), ("impact", 87.45, .34), ("pop", 89.55, .24), ("pop", 92.05, .24), ("pop", 92.85, .24), ("stamp", 94.1, .38),
    ("whoosh", 95.2, .24), ("swish", 97.85, .20), ("swish", 98.5, .20), ("pop", 99.55, .24), ("ding", 100.0, .30),
    ("whoosh", 100.9, .24), ("pop", 103.55, .28), ("pop", 104.9, .26), ("ding", 105.9, .26), ("swish", 107.6, .18),
]
def wav_len(n):
    w = wave.open(os.path.join(PROJ, "assets", "sfx", f"{n}.wav")); return w.getnframes() / w.getframerate()
lens = {n: wav_len(n) for n in set(x[0] for x in SFX)}
sfx_html, lane_end = [], [0.0] * 4
SFX = [(n, M(st), v) for n, st, v in SFX]
for i, (n, st, v) in enumerate(SFX):
    d = round(min(lens[n], D - st), 3)
    lane = next(k for k in range(4) if lane_end[k] <= st)
    lane_end[lane] = st + d
    sfx_html.append(f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{n}.wav" data-start="{st}" data-duration="{d}" data-volume="{v}" data-audio-group="sfx" data-track-index="{4+lane}"></audio>')

# ================================================================ INDEX
hosts = [f'      <div id="{sid}" class="clip scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{a}" data-duration="{round(b-a,3)}" data-track-index="2" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>'
         for sid, a, b in SCENES]
SHAKE = [(2.56, 8), (5.62, 12), (7.42, 14), (8.05, 10), (87.45, 6), (94.1, 6), (83.3, 5)]
shake_js = ""
for a, amp in [(M(a), amp) for a, amp in SHAKE]:
    for k, (dx, dy) in enumerate([(1, -0.6), (-0.8, 0.9), (0.6, -0.4), (-0.4, 0.5), (0.2, -0.2), (0, 0)]):
        shake_js += f"      tl.to('#shake',{{x:{dx*amp:.1f},y:{dy*amp:.1f},duration:0.035,ease:'none'}},{a+k*0.035:.3f});\n"
FLASH = [5.6, 7.42, 8.05]
flash_js = "".join(f"      tl.fromTo('#flash',{{opacity:0.7}},{{opacity:0,duration:0.22,ease:'power2.out',immediateRender:false}},{a});\n" for a in map(M, FLASH))

index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0A1A33; }}
      #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; font-family: 'Montserrat', sans-serif; }}
      #bg {{ position: absolute; inset: 0; z-index: 0; overflow: hidden;
        background: radial-gradient(ellipse 120% 70% at 50% 28%, #24507F 0%, #14325A 45%, #0A1A33 100%); }}
      #bg-pattern {{ position: absolute; inset: -120px; opacity: .07; background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'><g fill='none' stroke='%23E9C46A' stroke-width='1.2'><path d='M60 14 L73 47 L106 60 L73 73 L60 106 L47 73 L14 60 L47 47 Z'/><rect x='35' y='35' width='50' height='50' transform='rotate(45 60 60)'/><circle cx='60' cy='60' r='9'/></g></svg>"); background-size: 120px 120px; }}
      .orb {{ position: absolute; border-radius: 50%; }}
      #orb1 {{ left: -220px; top: 60px; width: 760px; height: 760px; background: radial-gradient(circle, rgba(233,196,106,.20) 0%, rgba(233,196,106,0) 65%); }}
      #orb3 {{ left: 360px; top: -260px; width: 700px; height: 700px; background: radial-gradient(circle, rgba(140,190,240,.16) 0%, rgba(140,190,240,0) 65%); }}
      #stage {{ position: absolute; left: {WIN_L}px; top: {WIN_T}px; width: {WIN_W}px; height: {WIN_H + 40}px; z-index: 1; overflow: hidden; background: #0A1A33;
        border-radius: 40px; box-shadow: 0 0 0 3px rgba(233,196,106,.75), 0 24px 60px rgba(0,0,0,.5); }}
      #shake {{ position: absolute; inset: -20px; }}
      #cam {{ position: absolute; left: 20px; top: 20px; width: {W}px; height: {H}px; transform-origin: 0 0; }}
      #aroll {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #stage-vig {{ position: absolute; inset: 0; z-index: 2; pointer-events: none;
        background: linear-gradient(180deg, rgba(10,26,51,.30) 0%, rgba(10,26,51,0) 6%, rgba(10,26,51,0) 72%, rgba(6,15,32,.5) 100%); }}
      #stage-line {{ position: absolute; left: 0; width: {W}px; top: {STAGE_T - 1}px; height: 3px; z-index: 3;
        background: linear-gradient(90deg, rgba(217,178,92,0), #D9B25C 25%, #F2CF76 50%, #D9B25C 75%, rgba(217,178,92,0)); }}
      #flash {{ position: absolute; inset: 0; z-index: 9; background: #fff; opacity: 0; }}
      .scene {{ z-index: 5; }}
      #captions {{ z-index: 6; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{W}" data-height="{H}">
      <div id="bg" data-layout-ignore><div id="bg-pattern"></div><div class="orb" id="orb1"></div><div class="orb" id="orb3"></div></div>
      <div id="stage" data-layout-ignore><div id="shake"><div id="cam">
        <video id="aroll" class="clip" src="assets/aroll.mp4" data-start="0" data-duration="{D}" data-track-index="0" muted playsinline></video>
      </div></div><div id="stage-vig"></div></div>
      <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{D}" data-volume="1" data-track-index="1"></audio>
{chr(10).join(hosts)}
      <div id="captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{D}" data-track-index="3" data-track-kind="captions" data-width="{W}" data-height="{H}"></div>
      <div id="flash" data-layout-ignore></div>
      <hf-audio-group id="sfx"></hf-audio-group>
{chr(10).join(sfx_html)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const CAM = {json.dumps(cam)};
      CAM.forEach(([t, d, x0, y0, s0, x1, y1, s1]) => {{
        tl.set('#cam', {{ x: x0, y: y0, scale: s0 }}, t);
        tl.to('#cam', {{ x: x1, y: y1, scale: s1, duration: d, ease: 'none' }}, t);
      }});
      tl.to('#cam', {{ x: {GIANT_PUSH[0]}, y: {GIANT_PUSH[1]}, scale: {GIANT_PUSH[2]}, duration: 0.25, ease: 'power3.out' }}, {M(7.42)});
      tl.set('#flash', {{ opacity: 0 }}, 0);
      tl.fromTo('#orb1', {{ x: 0, y: 0 }}, {{ x: 200, y: 160, duration: {D}, ease: 'sine.inOut' }}, 0);
      tl.fromTo('#orb3', {{ x: 0, y: 0 }}, {{ x: -160, y: 200, duration: {D}, ease: 'sine.inOut' }}, 0);
      tl.fromTo('#bg-pattern', {{ x: 0, y: 0 }}, {{ x: 60, y: 120, duration: {D}, ease: 'none' }}, 0);
{flash_js}{shake_js}      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
old = open(os.path.join(PROJ, "index.html")).read() if os.path.exists(os.path.join(PROJ, "index.html")) else ""
mg = re.search(r'data-color-grading="[^"]*"', old)
if mg:
    index = index.replace('<video id="aroll" ', '<video id="aroll" ' + mg.group(0) + ' ', 1)
with open(os.path.join(PROJ, "index.html"), "w") as f:
    f.write(index)
print("duration", D, "scenes", len(SCENES), "caption groups", len(groups), "sfx", len(SFX), "cam keys", len(cam))
