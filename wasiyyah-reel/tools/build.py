#!/usr/bin/env python3
"""Generate the Wasiyyah reel HyperFrames project (index.html + compositions/*).

Inputs (tools/): words_edit.json (word timings on the edited timeline),
pieces.json (A-roll cut list). Re-run after changing timings or copy.
"""
import json, os, re, html
from icons import icon

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
D = 115.7  # edited A-roll length (s)
W, H = 1080, 1920

words = json.load(open(os.path.join(HERE, "words_edit.json")))
pieces = json.load(open(os.path.join(HERE, "pieces.json")))

GOLD = "#E9C46A"
ICE = "#9ADBFF"
RED = "#FF6B6B"
GREEN = "#5EE6A8"

# ---------------------------------------------------------------- shared css
BASE_CSS = """
#ROOT{position:absolute;inset:0;overflow:visible;font-family:'Montserrat',sans-serif;color:#FFF8E7;pointer-events:none}
#ROOT .panel{position:absolute;left:100px;width:810px;top:296px;border-radius:38px;
  background:linear-gradient(165deg,rgba(16,36,68,.92),rgba(6,15,32,.90));
  border:1.5px solid rgba(233,196,106,.45);
  box-shadow:0 30px 70px rgba(0,0,0,.50),inset 0 1px 0 rgba(255,255,255,.10);
  backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);overflow:visible}
#ROOT .krow{position:absolute;left:0;right:0;top:20px;display:flex;justify-content:center}
#ROOT .kick{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#F6D98B,#E2B65A);
  color:#0B1F3A;font-weight:800;font-size:30px;letter-spacing:.07em;padding:10px 22px;border-radius:999px;
  text-transform:uppercase;box-shadow:0 10px 24px rgba(0,0,0,.35)}
#ROOT .row{position:absolute;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:18px;text-align:center}
#ROOT .t-sm{font-weight:700;font-size:32px;color:rgba(255,248,231,.86)}
#ROOT .t-md{font-weight:800;font-size:44px;letter-spacing:-.01em}
#ROOT .t-lg{font-weight:900;font-size:64px;letter-spacing:-.02em;line-height:1}
#ROOT .t-xl{font-weight:900;font-size:110px;letter-spacing:-.03em;line-height:1}
#ROOT .gold{background:linear-gradient(180deg,#FFF0C2 0%,#F2CF76 45%,#C9962E 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
#ROOT .ice{background:linear-gradient(180deg,#FFFFFF 0%,#CFEFFF 45%,#6EC6FF 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
#ROOT .redt{color:#FF7A7A}
#ROOT .greent{color:#6CF0B4}
#ROOT .chip{display:inline-flex;align-items:center;gap:12px;padding:12px 20px;border-radius:22px;
  background:rgba(255,248,231,.08);border:1.5px solid rgba(255,248,231,.18);font-weight:800;font-size:32px;position:relative}
#ROOT .chip .ico{flex:none}
#ROOT .pill{display:inline-flex;align-items:center;gap:10px;padding:10px 20px;border-radius:999px;
  background:rgba(233,196,106,.16);border:1.5px solid rgba(233,196,106,.55);font-weight:800;font-size:30px;color:#FFE9AE}
#ROOT .bar{position:relative;height:30px;border-radius:999px;background:rgba(255,255,255,.10);overflow:hidden}
#ROOT .bar i{position:absolute;left:0;top:0;bottom:0;border-radius:999px;transform-origin:0 50%}
#ROOT .stamp{display:inline-flex;align-items:center;gap:14px;padding:12px 30px;border:5px solid currentColor;border-radius:18px;
  font-weight:900;font-size:56px;letter-spacing:.05em}
"""

def css(scene_id, extra=""):
    return (BASE_CSS + extra).replace("#ROOT", f"#{scene_id}")

JS_HELPERS = """
const tl = gsap.timeline({ paused: true });
const IN=(s,t,o={})=>tl.fromTo(s,{opacity:0,y:o.y??26,scale:o.s??0.94,filter:'blur(8px)'},{opacity:1,y:0,scale:1,filter:'blur(0px)',duration:o.d??0.42,ease:o.e??'power3.out',stagger:o.st??0},t);
const POP=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??0.35},{opacity:1,scale:1,duration:o.d??0.5,ease:'back.out(2.2)',stagger:o.st??0},t);
const SLAM=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??1.9,filter:'blur(10px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:o.d??0.24,ease:'power4.in'},t);
const OUT=(s,t,d=0.28)=>tl.to(s,{opacity:0,y:-18,filter:'blur(8px)',duration:d,ease:'power2.in'},t);
const COUNT=(s,a,b,t,d,f,e='power2.out')=>{const el=document.querySelector(s);const o={v:a};tl.fromTo(o,{v:a},{v:b,duration:d,ease:e,onUpdate:()=>{el.textContent=f(o.v)}},t);};
const RM=(v)=>'RM'+Math.round(v).toLocaleString('en-US');
"""


def scene_file(sid, extra_css, body, js, panel_h=None):
    body = re.sub(r'class="panel" id="([\w-]+)" style="height:(\d+)px"',
                  lambda m: f'class="panel" id="{m.group(1)}" style="height:{m.group(2)}px;top:{609 - int(m.group(2)) // 2}px"', body)
    return f"""<template>
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
"""

SCENES = []  # (sid, start, end, html)

def add_scene(sid, start, end, extra_css, body, js):
    SCENES.append((sid, start, end))
    with open(os.path.join(PROJ, "compositions", f"{sid}.html"), "w") as f:
        f.write(scene_file(sid, extra_css, body, js))

def L(start):
    return lambda g: round(g - start, 3)

# ================================================================ 1. HOOK
s0, s1 = 0.0, 4.75; t = L(s0)
add_scene("hook", s0, s1, """
#hook .dim{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 40%,rgba(4,12,28,.55),rgba(2,6,16,.88))}
#hook .top{position:absolute;left:120px;width:768px;top:380px;text-align:center}
#hook .hl{font-weight:900;font-size:62px;line-height:1.04;letter-spacing:-.02em;text-shadow:0 6px 30px rgba(0,0,0,.65);margin-top:26px}
#hook .hw{display:inline-block}
#hook .giant{position:absolute;left:120px;width:768px;top:400px;text-align:center}
#hook .g-label{display:inline-flex;align-items:center;gap:12px;font-weight:800;font-size:38px;letter-spacing:.14em;color:#CFEFFF}
#hook .g-num{font-weight:900;font-size:300px;line-height:.92;letter-spacing:-.05em;margin-top:18px;filter:drop-shadow(0 0 40px rgba(110,198,255,.55))}
#hook .g-rm{font-size:130px;letter-spacing:-.02em;vertical-align:top;margin-right:6px}
#hook .g-bil{font-weight:900;font-size:136px;letter-spacing:.08em;line-height:1;margin-top:4px;filter:drop-shadow(0 8px 30px rgba(0,0,0,.6))}
#hook .g-sub{font-weight:700;font-size:40px;margin-top:26px;color:rgba(255,248,231,.92)}
""", f"""
    <div class="dim" id="hook-dim"></div>
    <div class="top" id="hook-top">
      <span class="kick" id="hook-kick" style="display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#F6D98B,#E2B65A);color:#0B1F3A;font-weight:800;font-size:32px;letter-spacing:.08em;padding:11px 24px;border-radius:999px">{icon('alert',34,'#0B1F3A',2.6)} TAHUKAH ANDA?</span>
      <div class="hl"><span class="hw" id="hook-w1">Aset</span> <span class="hw" id="hook-w2">terbeku</span><br/>di Malaysia<br/>sekarang mencecah…</div>
    </div>
    <div class="giant" id="hook-giant">
      <div class="g-label" id="hook-glabel">{icon('snow',40,'#CFEFFF',2.4)} ASET TERBEKU</div>
      <div class="g-num" id="hook-gnum"><span class="ice"><span class="g-rm">RM</span><span id="hook-n">0</span></span></div>
      <div class="g-bil" id="hook-gbil"><span class="gold">BILION</span></div>
    </div>
""", f"""
    tl.fromTo('#hook-top',{{scale:1.05}},{{scale:1,duration:0.6,ease:'power2.out'}},0);
    tl.to('#hook-w1,#hook-w2',{{color:'{ICE}',duration:0.15}},0.8);
    tl.fromTo('#hook-w2',{{scale:1}},{{scale:1.12,duration:0.18,yoyo:true,repeat:1,ease:'power2.out'}},1.19);
    tl.to('#hook-top',{{y:-160,opacity:0,filter:'blur(10px)',duration:0.3,ease:'power3.in'}},2.5);
    tl.to('#hook-dim',{{opacity:1,duration:0.35,ease:'power2.out'}},2.5);
    IN('#hook-glabel',2.62,{{y:30}});
    tl.fromTo('#hook-gnum',{{opacity:0,scale:0.55}},{{opacity:1,scale:1,duration:0.3,ease:'power3.out'}},2.66);
    COUNT('#hook-n',0,90,2.69,0.68,v=>Math.round(v),'power2.in');
    tl.fromTo('#hook-gnum',{{scale:1.28}},{{scale:1,duration:0.4,ease:'back.out(2.5)',immediateRender:false}},3.37);
    SLAM('#hook-gbil',3.86,{{s:2.4,d:0.18}});
    tl.to('#hook-giant',{{scale:1.18,opacity:0,filter:'blur(14px)',duration:0.24,ease:'power3.in'}},4.48);
    tl.to('#hook-dim',{{opacity:0,duration:0.24,ease:'power2.in'}},4.48);
""")

# ================================================================ 2. FREEZE (B)
s0, s1 = 4.75, 8.3; t = L(s0)
add_scene("freeze", s0, s1, """
#freeze .flake{position:absolute;opacity:0}
""", f"""
    <div class="panel" id="fz-panel" style="height:300px">
      <div class="krow"><span class="kick" id="fz-kick">Bila berlaku kematian</span></div>
      <div class="row" style="top:84px"><span class="t-lg" id="fz-l1">Semua aset kita</span></div>
      <div class="row" style="top:162px" id="fz-l2row"><span id="fz-lock">{icon('lock',76,ICE,2.4)}</span><span class="t-xl ice" id="fz-l2" style="font-size:100px">TERBEKU</span></div>
      <span class="flake" id="fz-f1" style="left:30px;top:90px">{icon('snow',46,'#CFEFFF',2)}</span>
      <span class="flake" id="fz-f2" style="right:34px;top:84px">{icon('snow',60,'#CFEFFF',2)}</span>
      <span class="flake" id="fz-f3" style="left:40px;top:220px">{icon('snow',38,'#CFEFFF',2)}</span>
      <span class="flake" id="fz-f4" style="right:40px;top:226px">{icon('snow',44,'#CFEFFF',2)}</span>
    </div>
""", f"""
    IN('#fz-panel',{t(4.8)},{{y:-30}});
    POP('#fz-kick',{t(5.3)});
    IN('#fz-l1',{t(6.4)});
    SLAM('#fz-l2',{t(7.36)},{{s:2.2}});
    POP('#fz-lock',{t(7.46)},{{s:0.2}});
    tl.fromTo('#fz-f1,#fz-f2,#fz-f3,#fz-f4',{{opacity:0,scale:0,rotation:-90}},{{opacity:0.9,scale:1,rotation:0,duration:0.5,ease:'back.out(2)',stagger:0.05}},{t(7.5)});
    OUT('#fz-panel',{t(8.02)});
""")

# ================================================================ 3. ASSETS (C)
s0, s1 = 8.3, 14.75; t = L(s0)
chips = [("car", "Kereta", 8.37), ("home", "Rumah", 9.17), ("bank", "Akaun Bank", 9.93), ("trend", "ASB", 10.63), ("coins", "Tabung Haji", 11.31)]
chip_html = ""
for i, (ic, lab, _) in enumerate(chips):
    chip_html += f'<span class="chip" id="as-c{i}">{icon(ic,40,GOLD,2.2)}<span>{lab}</span><span class="frost" id="as-fr{i}"></span><span class="lockb" id="as-lk{i}">{icon("lock",24,"#0A2A3A",2.6)}</span></span>'
add_scene("assets", s0, s1, """
#assets .frost{position:absolute;inset:-1px;border-radius:24px;background:linear-gradient(160deg,rgba(207,239,255,.55),rgba(110,198,255,.28));border:1.5px solid rgba(207,239,255,.9);opacity:0}
#assets .lockb{position:absolute;right:-16px;top:-26px;width:42px;height:42px;border-radius:50%;background:#CFEFFF;display:flex;align-items:center;justify-content:center;opacity:0;box-shadow:0 6px 16px rgba(0,0,0,.35)}
""", f"""
    <div class="panel" id="as-panel" style="height:344px">
      <div class="krow"><span class="kick" id="as-kick">{icon('snow',30,'#0B1F3A',2.6)} Aset yang dibekukan</span></div>
      <div class="row" style="top:94px;gap:14px">{chip_html.split('<span class="chip" id="as-c3"')[0]}</div>
      <div class="row" style="top:184px;gap:14px"><span class="chip" id="as-c3"{chip_html.split('<span class="chip" id="as-c3"')[1]}</div>
      <div class="row" style="top:268px"><span class="pill" id="as-ban" style="background:rgba(255,107,107,.14);border-color:rgba(255,122,122,.7);color:#FFB3B3">{icon('x',32,RED,3)} Tak boleh dikeluarkan</span></div>
    </div>
""", f"""
    IN('#as-panel',{t(8.32)},{{y:-30}});
    POP('#as-kick',{t(8.4)});
""" + "".join(f"    POP('#as-c{i}',{t(tt)});\n" for i, (_, _, tt) in enumerate(chips)) + f"""
    tl.to('#as-fr0,#as-fr1,#as-fr2,#as-fr3,#as-fr4',{{opacity:1,duration:0.3,stagger:0.07,ease:'power2.out'}},{t(12.5)});
    POP('#as-lk0,#as-lk1,#as-lk2,#as-lk3,#as-lk4',{t(12.55)},{{st:0.07}});
    tl.fromTo('#as-panel',{{x:0}},{{x:7,duration:0.05,yoyo:true,repeat:5,ease:'none'}},{t(12.55)});
    POP('#as-ban',{t(13.55)});
    OUT('#as-panel',{t(14.45)});
""")

# ================================================================ 4. SURAT KUASA (D)
s0, s1 = 14.75, 22.45; t = L(s0)
add_scene("surat", s0, s1, """
#surat .doc{display:flex;align-items:center;gap:18px;padding:16px 28px;border-radius:28px;background:linear-gradient(180deg,#FFF8E7,#F1E3C2);color:#0B1F3A;box-shadow:0 18px 40px rgba(0,0,0,.4)}
#surat .seal{position:absolute;right:22px;top:86px;width:104px;height:104px;border-radius:50%;border:5px solid #C9962E;color:#C9962E;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:28px;letter-spacing:.04em;background:rgba(255,248,231,.95)}
""", f"""
    <div class="panel" id="su-panel" style="height:380px">
      <div class="krow"><span class="kick" id="su-kick">Nak keluarkan duit &amp; tukar geran?</span></div>
      <div class="row" style="top:80px"><span class="t-sm" id="su-l1">Waris <b>WAJIB</b> dapatkan</span></div>
      <div class="row" style="top:128px"><div class="doc" id="su-doc">{icon('file',60,'#0B1F3A',2)}<div style="text-align:left"><div style="font-weight:900;font-size:54px;letter-spacing:-.01em;line-height:1" id="su-title">SURAT KUASA</div><div style="font-weight:900;font-size:34px;color:#8A5A0B;margin-top:6px" id="su-pp">&amp; PERINTAH PEMBAHAGIAN</div></div></div></div>
      <div class="row" style="top:300px"><span class="pill" id="su-p1">{icon('map',34,GOLD,2.4)} Pejabat Tanah</span><span class="t-sm" id="su-or">atau</span><span class="pill" id="su-p2">{icon('scale',34,GOLD,2.4)} Mahkamah Tinggi</span></div>
    </div>
""", f"""
    IN('#su-panel',{t(14.8)},{{y:-30}});
    POP('#su-kick',{t(14.9)});
    IN('#su-l1',{t(17.55)});
    IN('#su-doc',{t(18.0)},{{y:30}});
    tl.fromTo('#su-title',{{scale:1.5,opacity:0.2}},{{scale:1,opacity:1,duration:0.22,ease:'power4.in'}},{t(18.84)});
    POP('#su-p1',{t(20.3)});
    IN('#su-or',{t(21.1)},{{y:10,d:0.25}});
    POP('#su-p2',{t(21.42)});
    OUT('#su-panel',{t(22.15)});
""")

# ================================================================ 5. TARIKH + TANGGUH (E,F)
s0, s1 = 22.45, 37.55; t = L(s0)
add_scene("tarikh", s0, s1, """
#tarikh .wl{display:flex;flex-direction:column;gap:16px;align-items:flex-start}
#tarikh .wi{display:flex;align-items:center;gap:14px;font-weight:800;font-size:36px}
#tarikh .barwrap{position:absolute;left:44px;right:44px;top:262px}
#tarikh .blab{display:flex;justify-content:space-between;font-weight:800;font-size:28px;margin-top:8px;color:rgba(255,248,231,.85)}
""", f"""
    <div class="panel" id="ta-panel" style="height:346px">
      <div class="krow"><span class="kick" id="ta-kick">{icon('hourglass',30,'#0B1F3A',2.6)} Prosesnya panjang</span></div>
      <div id="ta-ph1">
        <div class="row" style="top:80px"><span class="t-sm" id="ta-lab">{icon('calendar',34,GOLD,2.4)} Tarikh bicara kuasa biasanya</span></div>
        <div class="row" style="top:124px"><span class="t-xl gold" id="ta-num">6–7</span><span class="t-lg" id="ta-bln" style="font-size:62px">BULAN</span></div>
      </div>
      <div id="ta-ph2" class="row" style="top:86px;opacity:0">
        <div class="wl"><div class="wi" id="ta-w1">{icon('userx',46,RED,2.4)} Ahli faraid gagal hadir</div><div class="wi" id="ta-w2">{icon('file',46,RED,2.4)} Tiada borang persetujuan</div></div>
      </div>
      <div id="ta-ph3" class="row" style="top:84px;opacity:0"><span class="stamp redt" id="ta-stamp" style="transform:rotate(-4deg)">{icon('alert',58,RED,2.6)} DITANGGUH</span></div>
      <div class="row" style="top:190px"><span class="t-sm" id="ta-more" style="color:#FFB3B3;opacity:0">Tunggu tarikh baru: <b>+6–7 bulan lagi</b></span></div>
      <div class="barwrap" id="ta-barw">
        <div class="bar"><i id="ta-b1" style="width:50%;background:linear-gradient(90deg,#C9962E,#F2CF76)"></i><i id="ta-b2" style="left:50%;width:50%;background:linear-gradient(90deg,#FF6B6B,#FF9A7A)"></i></div>
        <div class="blab"><span id="ta-bl1">0</span><span id="ta-bl2">6–7 bulan</span><span id="ta-bl3" style="color:#FFB3B3;opacity:0">12–14 bulan</span></div>
      </div>
      <div class="row" style="top:222px"><span style="font-weight:600;font-size:28px;opacity:0" id="ta-foot">*bergantung kawasan</span></div>
    </div>
""", f"""
    tl.fromTo('#ta-b1,#ta-b2',{{scaleX:0}},{{scaleX:0,duration:0.01}},0);
    IN('#ta-panel',{t(22.5)},{{y:-30}});
    POP('#ta-kick',{t(22.55)});
    IN('#ta-lab',{t(24.3)});
    SLAM('#ta-num',{t(25.6)},{{s:1.8}});
    IN('#ta-bln',{t(27.0)},{{y:14}});
    IN('#ta-barw',{t(25.7)},{{y:10,d:0.3}});
    tl.to('#ta-b1',{{scaleX:1,duration:1.5,ease:'power2.inOut'}},{t(25.75)});
    tl.to('#ta-foot',{{opacity:0.65,duration:0.3}},{t(27.5)});
    OUT('#ta-ph1,#ta-foot',{t(28.75)});
    tl.set('#ta-ph2',{{opacity:1}},{t(29.0)});
    IN('#ta-w1',{t(30.2)},{{y:0}});
    IN('#ta-w2',{t(31.75)},{{y:0}});
    OUT('#ta-ph2',{t(34.9)});
    tl.set('#ta-ph3',{{opacity:1}},{t(35.3)});
    SLAM('#ta-stamp',{t(35.3)},{{s:2.6}});
    tl.to('#ta-b2',{{scaleX:1,duration:1.0,ease:'power2.out'}},{t(35.6)});
    tl.to('#ta-bl3',{{opacity:1,duration:0.3}},{t(36.2)});
    IN('#ta-more',{t(35.5)},{{y:10}});
    tl.fromTo('#ta-panel',{{x:0}},{{x:8,duration:0.05,yoyo:true,repeat:5,ease:'none'}},{t(35.55)});
    OUT('#ta-panel',{t(37.3)},0.22);
""")

# ================================================================ 6. BICARA KUASA (G)
s0, s1 = 37.55, 55.6; t = L(s0)
add_scene("bicara", s0, s1, """
#bicara .col{width:370px;padding:16px 16px;border-radius:26px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px}
#bicara .col .h{display:flex;align-items:center;gap:8px;font-weight:900;font-size:38px}
#bicara .col .s{font-weight:700;font-size:29px;line-height:1.2;color:rgba(255,248,231,.9)}
""", f"""
    <div class="panel" id="bi-panel" style="height:380px">
      <div class="krow"><span class="kick" id="bi-kick">{icon('scale',30,'#0B1F3A',2.6)} Ketika bicara kuasa</span></div>
      <div class="row" style="top:78px"><span class="t-sm" id="bi-sub">{icon('file',34,GOLD,2.4)} Semua aset dibentangkan</span></div>
      <div class="row" style="top:132px;gap:16px" id="bi-cols">
        <div class="col" id="bi-c1" style="background:rgba(94,230,168,.10);border:1.5px solid rgba(94,230,168,.6)"><div class="h greent">{icon('check',44,GREEN,3)} ADA HIBAH</div><div class="s" id="bi-c1s">Terkeluar daripada<br/>aset faraid</div></div>
        <div class="col" id="bi-c2" style="background:rgba(255,107,107,.10);border:1.5px solid rgba(255,122,122,.6)"><div class="h redt">{icon('x',44,RED,3)} TIADA HIBAH</div><div class="s" id="bi-c2s">Ikut faraid /<br/>muafakat waris</div></div>
      </div>
      <div id="bi-ph2" style="opacity:0">
        <div class="row" style="top:86px"><span class="t-md" id="bi-ks" style="font-size:38px">{icon('users',46,GOLD,2.4)} Kata sepakat semua waris</span></div>
        <div class="row" style="top:150px"><span class="stamp" id="bi-ok" style="color:#F2CF76;font-size:50px;flex-direction:column;gap:2px;padding:10px 30px"><span style="display:flex;align-items:center;gap:12px">{icon('check',52,GOLD,3)} SURAT KUASA</span><span style="font-size:32px;letter-spacing:.04em">&amp; PERINTAH PEMBAHAGIAN</span><span style="font-size:28px;letter-spacing:.2em;opacity:.85">DIKELUARKAN</span></span></div>
      </div>
    </div>
""", f"""
    IN('#bi-panel',{t(37.6)},{{y:-30}});
    POP('#bi-kick',{t(37.65)});
    IN('#bi-sub',{t(39.95)});
    IN('#bi-c1',{t(42.3)},{{y:30}});
    IN('#bi-c1s',{t(43.15)},{{y:10}});
    IN('#bi-c2',{t(45.85)},{{y:30}});
    IN('#bi-c2s',{t(47.9)},{{y:10}});
    OUT('#bi-cols,#bi-sub',{t(50.6)});
    tl.set('#bi-ph2',{{opacity:1}},{t(50.85)});
    IN('#bi-ks',{t(50.85)});
    SLAM('#bi-ok',{t(53.85)},{{s:2.0}});
    OUT('#bi-panel',{t(55.3)});
""")

# ================================================================ 7. MASALAH (H)
s0, s1 = 55.6, 61.05; t = L(s0)
add_scene("masalah", s0, s1, "", f"""
    <div class="panel" id="ma-panel" style="height:310px">
      <div class="krow"><span class="kick" id="ma-kick" style="background:linear-gradient(180deg,#FF9A9A,#FF6B6B)">{icon('alert',30,'#2A0A0A',2.6)} Masalahnya</span></div>
      <div id="ma-ph1"><div class="row" style="top:80px"><span class="t-md">Ramai waris</span></div>
      <div class="row" style="top:138px"><span class="t-lg redt" id="ma-tm" style="font-size:78px">TAK MAMPU</span></div>
      <div class="row" style="top:234px"><span class="t-sm">uruskan proses ini</span></div></div>
      <div id="ma-ph2" class="row" style="top:96px;opacity:0"><span id="ma-lk">{icon('lock',80,ICE,2.4)}</span><span class="t-lg ice" id="ma-tb" style="font-size:76px">ASET TERUS<br/>TERBEKU</span></div>
    </div>
""", f"""
    IN('#ma-panel',{t(55.65)},{{y:-30}});
    POP('#ma-kick',{t(55.7)});
    IN('#ma-ph1',{t(56.5)},{{y:20}});
    SLAM('#ma-tm',{t(57.2)},{{s:1.8}});
    OUT('#ma-ph1',{t(59.0)});
    tl.set('#ma-ph2',{{opacity:1}},{t(59.3)});
    SLAM('#ma-tb',{t(59.35)},{{s:2.0}});
    POP('#ma-lk',{t(60.35)},{{s:0.2}});
    OUT('#ma-panel',{t(60.78)});
""")

# ================================================================ 8. THIRD PARTY (I)
s0, s1 = 61.05, 71.45; t = L(s0)
add_scene("third", s0, s1, "", f"""
    <div class="panel" id="th-panel" style="height:340px">
      <div class="krow"><span class="kick" id="th-kick">{icon('help',30,'#0B1F3A',2.6)} Guna 3rd party trustee?</span></div>
      <div id="th-ph1">
        <div class="row" style="top:80px"><span class="t-sm">Kebanyakannya caj</span></div>
        <div class="row" style="top:122px"><span class="t-xl redt" id="th-2" style="font-size:160px">2%<span style="font-size:100px">++</span></span></div>
      </div>
      <div id="th-ph2" style="opacity:0">
        <div class="row" style="top:80px"><span class="t-sm">Setiap</span><span class="t-md gold" id="th-1j">RM1 JUTA</span><span class="t-sm">aset</span></div>
        <div class="row" style="top:146px"><span class="t-lg" style="font-size:72px">=</span><span class="t-xl redt" id="th-20k" style="font-size:112px">RM0</span></div>
        <div class="row" style="top:276px"><span class="t-sm" id="th-al" style="color:#FFB3B3;font-size:30px">minimum — ditanggung waris</span></div>
      </div>
    </div>
""", f"""
    IN('#th-panel',{t(61.1)},{{y:-30}});
    POP('#th-kick',{t(61.7)});
    IN('#th-ph1',{t(63.1)},{{y:16}});
    SLAM('#th-2',{t(64.1)},{{s:2.2}});
    OUT('#th-ph1',{t(66.2)});
    tl.set('#th-ph2',{{opacity:1}},{t(66.45)});
    IN('#th-1j',{t(66.5)});
    tl.fromTo('#th-20k',{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.3,ease:'power3.out'}},{t(68.8)});
    COUNT('#th-20k',0,20000,{t(68.85)},0.6,RM);
    tl.fromTo('#th-20k',{{scale:1.18}},{{scale:1,duration:0.35,ease:'back.out(2.5)',immediateRender:false}},{t(69.45)});
    IN('#th-al',{t(70.0)},{{y:10}});
    OUT('#th-panel',{t(71.18)});
""")

# ================================================================ 9. BRAND (J)
s0, s1 = 71.45, 78.5; t = L(s0)
add_scene("brand", s0, s1, """
#brand .wm{font-family:'Playfair Display',serif;font-weight:700;font-size:120px;letter-spacing:.01em;line-height:1;position:relative}
#brand .shine{position:absolute;top:-10%;bottom:-10%;width:120px;left:-160px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.75),transparent);transform:skewX(-20deg);mix-blend-mode:overlay}
#brand .rule{height:2px;width:120px;background:linear-gradient(90deg,transparent,#E9C46A)}
#brand .rule.r{background:linear-gradient(90deg,#E9C46A,transparent)}
""", f"""
    <div class="panel" id="br-panel" style="height:330px">
      <div class="krow"><span class="kick" id="br-kick">{icon('shield',30,'#0B1F3A',2.6)} Penyelesaiannya</span></div>
      <div class="row" style="top:76px"><span class="t-sm" id="br-sy" style="font-size:30px">Syarikat Wasiyyah Berhad memperkenalkan</span></div>
      <div class="row" style="top:104px;padding:6px 0 34px;overflow:hidden" data-layout-allow-overflow><span class="wm gold" id="br-wm">Wasitah</span><span class="shine" id="br-sh"></span></div>
      <div class="row" style="top:258px" id="br-kp"><span class="rule"></span><span style="font-weight:800;font-size:40px;letter-spacing:.2em;color:#FFE9AE">KHAIRIAT PUSAKA</span><span class="rule r"></span></div>
    </div>
""", f"""
    IN('#br-panel',{t(71.5)},{{y:-30}});
    POP('#br-kick',{t(71.55)});
    IN('#br-sy',{t(72.1)},{{y:12}});
    tl.fromTo('#br-wm',{{opacity:0,y:60,scale:1.25}},{{opacity:1,y:0,scale:1,duration:0.7,ease:'power3.out'}},{t(72.75)});
    tl.fromTo('#br-sh',{{x:0}},{{x:1100,duration:1.1,ease:'power2.inOut'}},{t(73.4)});
    IN('#br-kp',{t(77.4)},{{y:16}});
    OUT('#br-panel',{t(78.25)});
""")

# ================================================================ 10. BANTU (K)
s0, s1 = 78.5, 84.85; t = L(s0)
items = [("Uruskan pusaka anda", 80.0), ("Proses semua dokumen", 81.4), ("Dapatkan SURAT KUASA", 82.6), ("&amp; PERINTAH PEMBAHAGIAN", 83.5)]
ih = "".join(f'<div class="ci" id="bt-i{i}"><span class="cb">{icon("check",34,"#0B1F3A",3.2)}</span><span>{txt}</span></div>' for i, (txt, _) in enumerate(items))
add_scene("bantu", s0, s1, """
#bantu .cl{display:flex;flex-direction:column;gap:16px;align-items:flex-start}
#bantu .ci{display:flex;align-items:center;gap:16px;font-weight:800;font-size:36px}
#bantu .cb{width:50px;height:50px;border-radius:50%;background:linear-gradient(180deg,#F6D98B,#E2B65A);display:flex;align-items:center;justify-content:center;flex:none}
""", f"""
    <div class="panel" id="bt-panel" style="height:384px">
      <div class="krow"><span class="kick" id="bt-kick">{icon('shield',30,'#0B1F3A',2.6)} Kami bantu anda</span></div>
      <div class="row" style="top:84px"><div class="cl">{ih}</div></div>
    </div>
""", f"""
    IN('#bt-panel',{t(78.55)},{{y:-30}});
    POP('#bt-kick',{t(78.6)});
""" + "".join(f"    IN('#bt-i{i}',{t(tt)},{{y:0}});\n    POP('#bt-i{i} .cb',{t(tt+0.05)});\n" for i, (_, tt) in enumerate(items)) + f"""
    OUT('#bt-panel',{t(84.58)});
""")

# ================================================================ 11. HARGA (L)
s0, s1 = 84.85, 96.95; t = L(s0)
add_scene("harga", s0, s1, "", f"""
    <div class="panel" id="hg-panel" style="height:340px">
      <div class="krow"><span class="kick" id="hg-kick">{icon('check',30,'#0B1F3A',3)} Tiada caj selepas kematian</span></div>
      <div class="row" style="top:110px" id="hg-big"><span class="t-lg gold" style="font-size:96px">TIADA CAJ</span></div>
      <div id="hg-ph2" style="opacity:0">
        <div class="row" style="top:78px"><span class="t-sm">Hanya serendah</span></div>
        <div class="row" style="top:116px;align-items:flex-end;gap:8px"><span class="t-xl gold" id="hg-price" style="font-size:116px">RM32.40</span><span class="t-md" style="margin-bottom:16px;font-size:38px">/bulan</span></div>
      </div>
      <div class="row" style="top:262px" id="hg-pills"><span class="pill" id="hg-p1">{icon('check',30,GOLD,3)} Termasuk SST</span><span class="pill" id="hg-p2">{icon('calendar',30,GOLD,2.4)} 15 tahun</span></div>
      <div class="row" style="top:262px"><span class="pill" id="hg-2j" style="opacity:0">{icon('shield',32,GOLD,2.4)} Urus aset sehingga RM2 JUTA</span></div>
    </div>
""", f"""
    IN('#hg-panel',{t(84.88)},{{y:-30}});
    POP('#hg-kick',{t(84.9)});
    SLAM('#hg-big',{t(85.0)},{{s:1.8}});
    OUT('#hg-big',{t(86.75)},0.25);
    tl.set('#hg-ph2',{{opacity:1}},{t(86.95)});
    IN('#hg-ph2 .t-sm',{t(86.95)},{{y:10}});
    tl.fromTo('#hg-price',{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.4,ease:'back.out(2)'}},{t(87.75)});
    COUNT('#hg-price',0,32.40,{t(87.8)},0.9,v=>'RM'+v.toFixed(2));
    POP('#hg-p1',{t(90.55)});
    POP('#hg-p2',{t(92.05)});
    OUT('#hg-pills',{t(94.9)},0.2);
    POP('#hg-2j',{t(95.15)});
    OUT('#hg-panel',{t(96.68)});
""")

# ================================================================ 12. BANDING (M)
s0, s1 = 96.95, 104.05; t = L(s0)
add_scene("banding", s0, s1, """
#banding .cmp{position:absolute;left:40px;right:44px}
#banding .ch{display:flex;justify-content:space-between;align-items:baseline;font-weight:800;font-size:30px;margin-bottom:8px}
#banding .ch b{font-weight:900;font-size:44px}
#banding .bar{height:26px}
""", f"""
    <div class="panel" id="bd-panel" style="height:346px">
      <div class="krow"><span class="kick" id="bd-kick">Bandingkan • aset RM2 juta</span></div>
      <div class="cmp" style="top:76px" id="bd-r1"><div class="ch"><span>3rd party trustee (2%)</span><b class="redt" id="bd-v1">RM40,000++</b></div><div class="bar"><i id="bd-b1" style="width:100%;background:linear-gradient(90deg,#FF6B6B,#FF9A7A)"></i></div></div>
      <div class="cmp" style="top:166px" id="bd-r2"><div class="ch"><span>Wasitah Intan (15 thn)</span><b class="gold" id="bd-v2">RM0</b></div><div class="bar"><i id="bd-b2" style="width:14.6%;background:linear-gradient(90deg,#C9962E,#F2CF76)"></i></div></div>
      <div class="row" style="top:262px"><span class="stamp" id="bd-save" style="color:#6CF0B4;font-size:38px;padding:6px 22px;border-width:4px">{icon('cash',42,GREEN,2.4)} JIMAT LEBIH RM34,000</span></div>
    </div>
""", f"""
    tl.fromTo('#bd-b1,#bd-b2',{{scaleX:0}},{{scaleX:0,duration:0.01}},0);
    IN('#bd-panel',{t(97.0)},{{y:-30}});
    POP('#bd-kick',{t(97.05)});
    IN('#bd-r1',{t(97.2)},{{y:12}});
    tl.to('#bd-b1',{{scaleX:1,duration:1.0,ease:'power3.out'}},{t(97.4)});
    IN('#bd-r2',{t(99.0)},{{y:12}});
    tl.to('#bd-b2',{{scaleX:1,duration:0.6,ease:'power3.out'}},{t(100.5)});
    COUNT('#bd-v2',0,5832,{t(100.45)},0.6,RM);
    tl.fromTo('#bd-v2',{{scale:1.3}},{{scale:1,duration:0.35,ease:'back.out(2.5)',immediateRender:false}},{t(101.05)});
    SLAM('#bd-save',{t(102.3)},{{s:2.0}});
    OUT('#bd-panel',{t(103.78)});
""")

# ================================================================ 13. LEPAS (N)
s0, s1 = 104.05, 111.3; t = L(s0)
tiles = [("car", "JPJ", "Surat Kuasa", 106.85), ("map", "Pejabat Tanah", "Perintah<br/>Pembahagian", 107.7), ("bank", "Bank", "Surat Kuasa", 108.75)]
th = "".join(f'<div class="tile" id="lp-t{i}">{icon(ic,50,GOLD,2)}<span>{lab}</span><span class="doc">{doc}</span></div>' for i, (ic, lab, doc, _) in enumerate(tiles))
add_scene("lepas", s0, s1, """
#lepas .tile{width:236px;height:196px;border-radius:26px;background:rgba(255,248,231,.08);border:1.5px solid rgba(233,196,106,.45);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-weight:800;font-size:30px}
#lepas .tile .doc{font-size:28px;line-height:1.05;color:#F2CF76;text-align:center}
""", f"""
    <div class="panel" id="lp-panel" style="height:412px">
      <div class="krow"><span class="kick" id="lp-kick">{icon('check',30,'#0B1F3A',3)} Dokumen dah siap</span></div>
      <div class="row" style="top:76px"><span class="t-sm" id="lp-l1">Keluarga terus ke</span></div>
      <div class="row" style="top:122px;gap:14px">{th}</div>
      <div class="row" style="top:334px;gap:20px"><span class="pill" id="lp-p1">{icon('check',30,GOLD,3)} Tukar nama</span><span class="pill" id="lp-p2">{icon('check',30,GOLD,3)} Cairkan duit</span></div>
    </div>
""", f"""
    IN('#lp-panel',{t(104.1)},{{y:-30}});
    POP('#lp-kick',{t(104.15)});
    IN('#lp-l1',{t(105.4)},{{y:10}});
""" + "".join(f"    POP('#lp-t{i}',{t(tt)});\n" for i, (_, _, _, tt) in enumerate(tiles)) + f"""
    POP('#lp-p1',{t(109.45)});
    POP('#lp-p2',{t(110.4)});
    OUT('#lp-panel',{t(111.05)});
""")

# ================================================================ 14. CTA (P)
s0, s1 = 111.3, D; t = L(s0)
add_scene("cta", s0, s1, """
#cta .btn{display:inline-flex;align-items:center;gap:14px;padding:18px 34px;border-radius:999px;background:linear-gradient(180deg,#F6D98B,#E2B65A);color:#0B1F3A;font-weight:900;font-size:36px;box-shadow:0 16px 40px rgba(233,196,106,.35)}
""", f"""
    <div class="panel" id="ct-panel" style="height:320px">
      <div class="row" style="top:28px"><span id="ct-sh">{icon('shield',80,GOLD,2)}</span></div>
      <div class="row" style="top:122px"><span class="t-lg gold" id="ct-t" style="font-size:62px">LINDUNGI ASET ANDA</span></div>
      <div class="row" style="top:210px"><span class="btn" id="ct-btn">{icon('msg',40,'#0B1F3A',2.6)} Contact saya untuk detail</span></div>
    </div>
""", f"""
    IN('#ct-panel',{t(111.32)},{{y:-30}});
    POP('#ct-sh',{t(111.36)},{{s:0.2}});
    SLAM('#ct-t',{t(111.4)},{{s:1.8}});
    POP('#ct-btn',{t(113.05)});
    tl.fromTo('#ct-btn',{{scale:1}},{{scale:1.06,duration:0.35,yoyo:true,repeat:3,ease:'sine.inOut',immediateRender:false}},{t(113.7)});
""")

# ================================================================ CAPTIONS
SKIP = {"ataupun", "kerana"}
KEY = set("""kematian terbeku dibekukan kereta rumah akaun bank asb tabung haji surat kuasa geran pejabat tanah mahkamah tinggi
6 7 bulan tangguh hibah faraid muafakat kata sepakat third party 2% rm1 juta rm20,000 wasiyyah khairiat wasitah pusaka tiada cas
rm32.40 15 tahun rm2 rm5,832 jpj cairkan duit lindungi contact bicara intan""".split())
cw = [w for w in words if w["lab"] != "A" and w["text"].strip(",.?").lower() not in SKIP]
groups, cur = [], []
for i, w in enumerate(cw):
    if cur:
        prev = cur[-1]
        txt = " ".join(x["text"] for x in cur + [w])
        if (prev["lab"] != w["lab"] or prev["text"][-1] in ",.?" or w["start"] - prev["end"] > 0.18 or len(cur) >= 3 or len(txt) > 17):
            groups.append(cur); cur = []
    cur.append(w)
groups.append(cur)

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    g0 = max(0.1, g[0]["start"] - 0.06)
    nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else D
    g1 = min(nxt, g[-1]["end"] + 0.45)
    spans = []
    for wi, w in enumerate(g):
        clean = w["text"].strip(",.?").lower()
        k = " k" if clean in KEY or clean.replace(",", "") in KEY else ""
        disp = html.escape(w["text"].rstrip(","))
        spans.append(f'<span class="w{k}" id="cw{gi}_{wi}" data-t="{w["start"]:.3f}">{disp}</span>')
    est = sum(0.66 if c.isupper() or c.isdigit() else (0.3 if c in " .,'il" else 0.6) for c in " ".join(x["text"] for x in g)) * 62
    fs = f' style="font-size:{max(44, int(62 * 540 / est))}px"' if est > 540 else ""
    cap_html.append(f'      <div class="grp" id="cg{gi}" data-a="{g0:.3f}" data-b="{g1:.3f}"{fs}><span class="pb">{" ".join(spans)}</span></div>')

with open(os.path.join(PROJ, "compositions", "captions.html"), "w") as f:
    f.write(f"""<template>
  <style>
    #captions{{position:absolute;inset:0;pointer-events:none}}
    #captions .grp{{position:absolute;left:120px;width:768px;bottom:888px;white-space:nowrap;text-align:center;opacity:0;visibility:hidden;
      font-family:'Montserrat',sans-serif;font-weight:800;font-size:62px;line-height:1.12;letter-spacing:-.01em;color:#FFFFFF;overflow:visible}}
    #captions .pb{{display:inline-block;padding:8px 24px 12px;border-radius:22px;background:rgba(8,22,46,.76);border:1.5px solid rgba(233,196,106,.28);box-shadow:0 12px 30px rgba(0,0,0,.35);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}}
    #captions .w{{display:inline-block;text-shadow:0 3px 0 rgba(0,0,0,.35),0 6px 22px rgba(0,0,0,.75);-webkit-text-stroke:1.5px rgba(0,0,0,.25)}}
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

# ================================================================ CAMERA framing
# Split layout: explanations on the top half, speaker (matted) full-width on the bottom half.
STAGE_T = 960            # stage = y 960..1920
FX, FY = 540.0, 335.0    # face anchor inside the stage (stage-relative px)
def tf(s):
    return [round(FX - 540 * s, 2), round(FY - 1050 * s, 2), round(s, 4)]
SA, SB = 0.86, 0.91     # alternate scales at cuts (hide jump cuts)
cam = []
which = "A"
for i, p in enumerate(pieces):
    if i > 0 and p["od"] >= 0.8 and p["lab"] != "A":
        which = "B" if which == "A" else "A"
    if p["lab"] == "A":
        which = "A"
    sc = SA if which == "A" else SB
    dur = 2.5 if p["lab"] == "A" else p["od"]  # hook: push-in takes over at 2.5s
    cam.append([round(p["out0"], 3), round(dur, 3)] + tf(sc) + tf(sc * 1.012))
HOOK_PUSH = tf(1.05)

# ================================================================ SFX
SFX = [
    ("riser", 1.75, .32), ("impact", 3.35, .55), ("stamp", 3.86, .42), ("whoosh", 4.45, .30),
    ("swish", 5.3, .22), ("lock", 7.42, .42),
    ("whoosh", 8.25, .24), ("pop", 8.37, .30), ("pop", 9.17, .30), ("pop", 9.93, .30), ("pop", 10.63, .30), ("pop", 11.31, .30),
    ("lock", 12.5, .40), ("tick", 13.55, .28),
    ("whoosh", 14.75, .24), ("stamp", 18.84, .45), ("pop", 20.3, .28), ("pop", 21.42, .28),
    ("swish", 22.5, .24), ("clock", 25.65, .22), ("tick", 30.2, .30), ("tick", 31.75, .30), ("impact", 35.3, .38),
    ("whoosh", 37.55, .24), ("swish", 39.95, .20), ("ding", 42.3, .22), ("pop", 45.85, .28), ("swish", 50.85, .20), ("stamp", 53.85, .32), ("ding", 54.1, .26),
    ("whoosh", 55.6, .24), ("stamp", 57.2, .26), ("lock", 60.25, .40),
    ("whoosh", 61.1, .24), ("impact", 64.1, .34), ("swish", 66.45, .20), ("cash", 69.42, .34),
    ("whoosh", 71.5, .26), ("ding", 72.8, .28), ("swish", 77.4, .22),
    ("whoosh", 78.55, .22), ("tick", 80.0, .30), ("tick", 81.4, .30), ("tick", 83.7, .30),
    ("whoosh", 84.88, .24), ("stamp", 85.0, .30), ("ding", 87.8, .28), ("pop", 90.55, .26), ("pop", 92.05, .26), ("swish", 95.1, .20),
    ("whoosh", 97.0, .24), ("swish", 97.4, .18), ("cash", 101.0, .32), ("stamp", 102.3, .30), ("ding", 102.4, .24),
    ("whoosh", 104.1, .24), ("pop", 106.85, .28), ("pop", 107.7, .28), ("pop", 108.75, .28), ("tick", 109.45, .28), ("tick", 110.4, .28),
    ("whoosh", 111.3, .28), ("ding", 111.4, .30), ("pop", 113.05, .26),
]
import wave
def wav_len(n):
    w = wave.open(os.path.join(PROJ, "assets", "sfx", f"{n}.wav")); return w.getnframes() / w.getframerate()
lens = {n: wav_len(n) for n in set(x[0] for x in SFX)}
sfx_html = []
lane_end = [0.0, 0.0, 0.0]
for i, (n, st, v) in enumerate(SFX):
    d = round(lens[n], 3)
    lane = next(k for k in range(3) if lane_end[k] <= st)
    lane_end[lane] = st + d
    sfx_html.append(f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{n}.wav" data-start="{st}" data-duration="{d}" data-volume="{v}" data-audio-group="sfx" data-track-index="{4+lane}"></audio>')

# ================================================================ INDEX
hosts = []
for sid, a, b in SCENES:
    hosts.append(f'      <div id="{sid}" class="clip scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{a}" data-duration="{round(b-a,3)}" data-track-index="2" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>')

FROST = [(7.42, 8.3), (12.5, 13.7), (60.25, 61.0)]
frost_js = "".join(
    f"    tl.fromTo('#frost',{{opacity:0,scale:1.08}},{{opacity:1,scale:1,duration:0.18,ease:'power2.out',immediateRender:false}},{a});\n"
    f"    tl.to('#frost',{{opacity:0,duration:0.5,ease:'power2.in'}},{b-0.5});\n" for a, b in FROST)
SHAKE = [(3.35, 14), (35.3, 7), (64.1, 6), (7.42, 5), (12.5, 5)]
shake_js = ""
for a, amp in SHAKE:
    seq = [(1, -0.6), (-0.8, 0.9), (0.6, -0.4), (-0.4, 0.5), (0.2, -0.2), (0, 0)]
    for k, (dx, dy) in enumerate(seq):
        shake_js += f"    tl.to('#shake',{{x:{dx*amp:.1f},y:{dy*amp:.1f},duration:0.035,ease:'none'}},{a+k*0.035:.3f});\n"

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
      #orb1 {{ left: -220px; top: 120px; width: 760px; height: 760px; background: radial-gradient(circle, rgba(233,196,106,.20) 0%, rgba(233,196,106,0) 65%); }}
      #orb2 {{ right: -260px; top: 900px; width: 820px; height: 820px; background: radial-gradient(circle, rgba(120,170,230,.18) 0%, rgba(120,170,230,0) 65%); }}
      #orb3 {{ left: 240px; top: -260px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(255,240,200,.14) 0%, rgba(255,240,200,0) 65%); }}
      #stage {{ position: absolute; left: 0; top: {STAGE_T}px; width: {W}px; height: {H - STAGE_T}px; z-index: 1; overflow: hidden;
        background: radial-gradient(ellipse 75% 65% at 50% 38%, #3B6FA6 0%, #1D416E 48%, #0D2446 100%); }}
      #stage-vig {{ position: absolute; inset: 0; z-index: 2; pointer-events: none;
        background: linear-gradient(180deg, rgba(10,26,51,.55) 0%, rgba(10,26,51,0) 14%, rgba(10,26,51,0) 70%, rgba(6,15,32,.55) 100%); }}
      #stage-line {{ position: absolute; left: 0; width: {W}px; top: {STAGE_T - 1}px; height: 3px; z-index: 3;
        background: linear-gradient(90deg, rgba(217,178,92,0), #D9B25C 25%, #F2CF76 50%, #D9B25C 75%, rgba(217,178,92,0)); }}
      #shake {{ position: absolute; inset: 0;
        -webkit-mask-image: linear-gradient(90deg, transparent 0px, #000 130px, #000 950px, transparent 1080px);
        mask-image: linear-gradient(90deg, transparent 0px, #000 130px, #000 950px, transparent 1080px); }}
      #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; }}
      #aroll {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #frost {{ position: absolute; inset: 0; z-index: 3; opacity: 0;
        background: radial-gradient(ellipse at 50% 45%, rgba(160,220,255,0) 45%, rgba(160,220,255,.16) 78%, rgba(220,245,255,.42) 100%);
        box-shadow: inset 0 0 90px rgba(200,240,255,.45); }}
      #flash {{ position: absolute; inset: 0; z-index: 9; background: #fff; opacity: 0; }}
      .scene {{ z-index: 5; }}
      #captions {{ z-index: 6; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{W}" data-height="{H}">
      <div id="bg" data-layout-ignore><div id="bg-pattern"></div><div class="orb" id="orb1"></div><div class="orb" id="orb2"></div><div class="orb" id="orb3"></div></div>
      <div id="stage" data-layout-ignore><div id="shake"><div id="cam">
        <video id="aroll" class="clip" src="assets/person.webm" data-start="0" data-duration="{D}" data-track-index="0" muted playsinline></video>
      </div></div><div id="stage-vig"></div></div>
      <div id="stage-line" data-layout-ignore></div>
      <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{D}" data-volume="1" data-track-index="1"></audio>
      <div id="frost" data-layout-ignore></div>
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
      // giant-hook push-in (2.5s -> 4.5s)
      tl.to('#cam', {{ x: {HOOK_PUSH[0]}, y: {HOOK_PUSH[1]}, scale: {HOOK_PUSH[2]}, duration: 2.0, ease: 'power2.in' }}, 2.5);
      // calm background drift
      tl.fromTo('#orb1', {{ x: 0, y: 0 }}, {{ x: 160, y: 220, duration: {D}, ease: 'sine.inOut' }}, 0);
      tl.fromTo('#orb2', {{ x: 0, y: 0 }}, {{ x: -180, y: -260, duration: {D}, ease: 'sine.inOut' }}, 0);
      tl.fromTo('#orb3', {{ x: 0, y: 0 }}, {{ x: 120, y: 160, duration: {D}, ease: 'sine.inOut' }}, 0);
      tl.fromTo('#bg-pattern', {{ x: 0, y: 0 }}, {{ x: 60, y: 120, duration: {D}, ease: 'none' }}, 0);
      tl.fromTo('#flash', {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.22, ease: 'power2.out', immediateRender: false }}, 3.37);
      tl.set('#flash', {{ opacity: 0 }}, 0);
{frost_js}{shake_js}      window.__timelines["main"] = tl;
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
print("scenes", len(SCENES), "caption groups", len(groups), "sfx", len(SFX), "cam keys", len(cam))
