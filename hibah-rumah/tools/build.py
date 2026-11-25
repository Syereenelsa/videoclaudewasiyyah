"""Builds index.html for the Hibah Rumah RM499 infographic video.

Scene timing follows SKRIP-VO.md. Change a scene start in SCENES and the
offsets inside that scene (written as S('name', offset)) follow it.
Usage: python3 tools/build.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOTAL = 153.3      # voice-over is 151.9 s; hold the end card ~1.4 s after it

SCENES = {            # name: (start, end), aligned to assets/voice.wav
    "hook":    (0.0, 5.85),
    "bila":    (5.85, 26.5),
    "tunggu":  (26.5, 38.8),
    "beza":    (38.8, 64.2),
    "kenali":  (64.2, 77.3),
    "seratus": (77.3, 84.0),
    "promo":   (84.0, 100.25),
    "cara":    (100.25, 133.2),
    "cta":     (133.2, TOTAL),
}
BILA_CUES = [3.54, 6.75, 8.96, 11.12, 14.58, 17.25]   # the six checklist rows
CARA_DOCS = [9.43, 10.85, 12.7, 14.35]                # the four documents

def S(name, off=0.0):
    return round(SCENES[name][0] + off, 3)

# ---------------------------------------------------------------- icons
ICONS = {
    "home": '<path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M10.7 12.3L21 2"/><path d="M16 7l3 3"/><path d="M19 4l2 2"/>',
    "bank": '<path d="M3 21h18"/><path d="M5 21V10"/><path d="M9.5 21V10"/><path d="M14.5 21V10"/><path d="M19 21V10"/><path d="M2 10l10-7 10 7z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "x": '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "gavel": '<path d="M14.5 12.5l-8 8a2.12 2.12 0 1 1-3-3l8-8"/><path d="M16 16l6-6"/><path d="M8 8l6-6"/><path d="M9 7l8 8"/><path d="M21 11l-8-8"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7z"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/>',
    "phone": '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    "id": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2.5"/><path d="M14 10h5"/><path d="M14 14h4"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"/>',
    "hourglass": '<path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.17a2 2 0 0 0-.59-1.42L12 12l-4.41 4.41A2 2 0 0 0 7 17.83V22"/><path d="M7 2v4.17a2 2 0 0 0 .59 1.42L12 12l4.41-4.41A2 2 0 0 0 17 6.17V2"/>',
    "arrow": '<path d="M5 12h14"/><path d="M12 5l7 7-7 7"/>',
    "arrowdown": '<path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "spark": '<path d="M12 3l1.9 5.8L20 10l-6.1 1.2L12 17l-1.9-5.8L4 10l6.1-1.2z"/>',
    "alert": '<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "newspaper": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8z"/>',
}

def icon(name, size=40, color="#E9C46A", sw=2.4):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICONS[name]}</svg>')

def expand_icons(html):
    def rep(m):
        parts = m.group(1).split(":")
        name = parts[0]
        size = int(parts[1]) if len(parts) > 1 else 40
        color = parts[2] if len(parts) > 2 else "#E9C46A"
        sw = float(parts[3]) if len(parts) > 3 else 2.4
        return icon(name, size, color, sw)
    return re.sub(r"@@([a-z]+(?::[^@]+)?)@@", rep, html)

# ---------------------------------------------------------------- sfx
SFX_LEN = {"cash": .6, "clock": 2.0, "ding": 1.2, "impact": 1.4, "lock": .5, "pop": .12,
           "riser": 1.6, "stamp": .35, "swish": .32, "tick": .05, "whoosh": .55}
SFX = []
def sfx(name, t, vol):
    SFX.append((name, round(t, 3), vol))

# Cue times are taken from the voice-over (tools/transcript.json), corrected
# against the pauses in assets/voice.wav. Offsets are seconds from scene start.
# hook
sfx("whoosh", S("hook", 0.0), .30); sfx("pop", S("hook", 2.12), .26)
sfx("ding", S("hook", 2.15), .24); sfx("pop", S("hook", 4.4), .22)
sfx("riser", S("hook", 3.4), .22); sfx("impact", S("hook", 5.0), .40)
# bila
sfx("whoosh", S("bila"), .28); sfx("stamp", S("bila", .45), .32)
for off in BILA_CUES:
    sfx("swish", S("bila", off), .20); sfx("pop", S("bila", off + .55), .30)
# tunggu
sfx("whoosh", S("tunggu"), .28); sfx("ding", S("tunggu", 4.35), .24)
sfx("clock", S("tunggu", 6.2), .22); sfx("stamp", S("tunggu", 6.86), .45)
sfx("pop", S("tunggu", 8.2), .22); sfx("ding", S("tunggu", 9.1), .20)
# beza
sfx("whoosh", S("beza"), .28); sfx("pop", S("beza", .29), .26)
sfx("swish", S("beza", 4.45), .22); sfx("lock", S("beza", 5.15), .32)
for k in range(4):
    sfx("tick", S("beza", 8.9 + k * .12), .30)
sfx("swish", S("beza", 10.25), .22)
for off in (12.8, 14.8, 18.5):
    sfx("pop", S("beza", off), .28)
sfx("ding", S("beza", 20.83), .30)
# kenali
sfx("whoosh", S("kenali"), .28)
sfx("swish", S("kenali", 1.9), .22); sfx("swish", S("kenali", 2.35), .22); sfx("stamp", S("kenali", 3.11), .45)
sfx("pop", S("kenali", 3.54), .28); sfx("pop", S("kenali", 7.12), .28)
for k in range(6):
    sfx("tick", S("kenali", 7.27 + k * .25), .22)
sfx("ding", S("kenali", 8.8), .22); sfx("pop", S("kenali", 10.05), .28)
# seratus (100% pengesahan)
sfx("whoosh", S("seratus"), .28); sfx("pop", S("seratus", .35), .24)
sfx("riser", S("seratus", 1.7), .22)
for k in range(8):
    sfx("tick", S("seratus", 2.1 + k * .15), .24)
sfx("impact", S("seratus", 3.3), .40); sfx("ding", S("seratus", 3.32), .26)
sfx("stamp", S("seratus", 3.96), .40); sfx("swish", S("seratus", 1.0), .22); sfx("stamp", S("seratus", 4.66), .36)
# promo
sfx("whoosh", S("promo"), .30); sfx("ding", S("promo", 0.2), .26)
sfx("pop", S("promo", 1.7), .24); sfx("swish", S("promo", 3.05), .30)
sfx("riser", S("promo", 4.7), .30); sfx("impact", S("promo", 6.28), .55)
sfx("pop", S("promo", 6.9), .26); sfx("pop", S("promo", 7.81), .30)
sfx("cash", S("promo", 11.5), .40); sfx("ding", S("promo", 14.22), .24)
# cara
sfx("whoosh", S("cara"), .28); sfx("pop", S("cara", .5), .24)
for off in (3.55, 7.76, 17.16, 22.29):
    sfx("lock", S("cara", off), .30)
for off in CARA_DOCS:
    sfx("pop", S("cara", off), .28)
sfx("swish", S("cara", 20.15), .20); sfx("swish", S("cara", 26.65), .20)
sfx("stamp", S("cara", 32.11), .45); sfx("ding", S("cara", 32.15), .30)
# cta
sfx("whoosh", S("cta"), .28); sfx("ding", S("cta", .9), .26)
sfx("pop", S("cta", 6.35), .22); sfx("clock", S("cta", 7.92), .20)
sfx("stamp", S("cta", 9.96), .40); sfx("riser", S("cta", 12.78), .24)
sfx("impact", S("cta", 14.4), .35); sfx("pop", S("cta", 15.9), .22)


def sfx_tags():
    out = []
    lanes = []   # end time of the last clip in each Studio lane
    for i, (n, t, v) in enumerate(sorted(SFX, key=lambda x: x[1])):
        lane = next((k for k, end in enumerate(lanes) if end <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + SFX_LEN[n]
        out.append(f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{n}.wav" data-start="{t}" '
                   f'data-duration="{SFX_LEN[n]}" data-volume="{v}" data-audio-group="sfx" '
                   f'data-track-index="{4 + lane}"></audio>')
    return "\n".join(out)

def scene_tags(name, inner):
    a, b = SCENES[name]
    return (f'      <div id="sc-{name}" class="clip scene" data-start="{a}" data-duration="{round(b - a, 3)}" '
            f'data-track-index="2">\n{inner}\n      </div>')

# deterministic sparkle burst for the price slam
def sparkles(n=22):
    out = []
    for i in range(n):
        ang = (i * 137.508) % 360
        dist = 230 + (i * 53) % 170
        size = 10 + (i * 7) % 14
        out.append(f'<i class="spk" data-a="{ang:.1f}" data-d="{dist}" style="width:{size}px;height:{size}px"></i>')
    return "".join(out)

# ---------------------------------------------------------------- house art
HOUSE = '''<svg id="{id}" class="house" width="{w}" height="{h}" viewBox="0 0 500 440" fill="none">
  <path class="draw" pathLength="1" d="M40 210 L250 40 L460 210" stroke="#F2CF76" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
  <path class="draw" pathLength="1" d="M345 120 V60 H395 V160" stroke="#F2CF76" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <path class="draw" pathLength="1" d="M90 175 V410 H410 V175" stroke="#FFF8E7" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <path class="draw" pathLength="1" d="M30 410 H470" stroke="#FFF8E7" stroke-width="10" stroke-linecap="round"/>
  <rect class="win" x="130" y="225" width="80" height="70" rx="8" fill="#3E6290" stroke="#FFF8E7" stroke-width="8"/>
  <rect class="win" x="290" y="225" width="80" height="70" rx="8" fill="#3E6290" stroke="#FFF8E7" stroke-width="8"/>
  <path class="draw" pathLength="1" d="M215 410 V320 Q250 290 285 320 V410" stroke="#FFF8E7" stroke-width="10" stroke-linejoin="round"/>
  <path class="hheart" d="M250 262c6-6 12-12 12-20a12 12 0 0 0-12-12c-4 0-7 2-10 5-3-3-6-5-10-5a12 12 0 0 0-12 12c0 8 6 14 12 20l10 10z" transform="translate(10 -150)" fill="#FF8A8A" opacity="0"/>
</svg>'''

# ---------------------------------------------------------------- scenes
# Text lives in flex columns (.col) so a line that wraps pushes the next one
# down instead of overlapping it.
HOOK = f'''
        <div class="glow" id="hk-glow"></div>
        <div class="center" style="top:330px">{HOUSE.format(id="hk-house", w=520, h=458)}</div>
        <div class="col" style="top:850px">
          <span class="t-md" id="hk-l1">Pernah terfikir,</span>
          <span class="t-lg" id="hk-l2" style="margin-top:14px">apa akan jadi pada</span>
          <span class="t-xl gold" id="hk-l2b">RUMAH kita</span>
          <span class="t-lg" id="hk-l3" style="margin-top:4px">jika kita sudah <span class="redt">tiada?</span></span>
          <span class="pill" id="hk-pill" style="margin-top:44px">@@home:30@@ Promosi Hibah Rumah RM499</span>
        </div>
'''

BILA_ITEMS = [
    ("key", "Dah ada rumah <b>atas nama sendiri</b>"),
    ("bank", "Rumah masih dalam <b>pinjaman bank</b>"),
    ("users", "Dah <b>berkahwin</b> &amp; ada <b>anak</b>"),
    ("gift", "Nak beri rumah kepada <b>pasangan / anak pilihan</b>"),
    ("shield", "Kurangkan risiko <b>pertikaian keluarga</b>"),
    ("calendar", "Rancang pembahagian harta <b>semasa hidup</b>"),
]
rows = []
for i, (ic, txt) in enumerate(BILA_ITEMS):
    top = 545 + i * 150
    rows.append(f'''        <div class="item" id="bl-i{i}" style="top:{top}px">
          <span class="ibub">@@{ic}:42@@</span><span class="itxt">{txt}</span>
          <span class="itick" id="bl-t{i}">@@check:30:#0B1F3A:3.4@@</span>
        </div>''')
BILA = f'''
        <div class="col" style="top:320px">
          <span class="kick" id="bl-kick">Bila anda perlu</span>
          <span class="t-lg" id="bl-title" style="margin-top:20px">buat <span class="gold">HIBAH RUMAH?</span></span>
        </div>
{chr(10).join(rows)}
'''

TUNGGU = f'''
        <div class="col" style="top:320px">
          <span class="t-sm center-t" id="tg-l1">Jika anda tergolong dalam <b class="goldt">salah satu</b><br>situasi tadi,</span>
          <span class="t-lg" id="tg-l2" style="margin-top:18px">inilah</span>
          <span class="t-lg gold" id="tg-l2b">masa yang sesuai</span>
          <div class="panel fp" id="tg-panel" style="margin-top:40px">
            <span class="stamp redt" id="tg-stamp">JANGAN TUNGGU</span>
            <span class="t-md" style="margin-top:26px;font-size:42px">sehingga rumah <span class="goldt">habis bayar</span></span>
            <div class="loan" style="margin-top:32px">
              <div class="loanlbl"><span>@@home:30@@ Pinjaman rumah</span><span id="tg-yr">Tahun 1</span></div>
              <div class="bar"><i id="tg-bar"></i></div>
            </div>
            <span class="t-xs" id="tg-hg" style="margin-top:30px">@@hourglass:28:#FFE9AE@@ Siapa tahu berapa lama masa kita?</span>
          </div>
          <span class="quote" id="tg-q" style="margin-top:46px">Perancangan harta yang baik bermula<br>semasa kita <b class="goldt">masih hidup</b>.</span>
        </div>
'''

PIE = '''<svg width="130" height="130" viewBox="-80 -80 160 160" id="bz-pie">
  <path class="sl" d="M0 0 L0 -70 A70 70 0 0 1 70 0 Z" fill="#E9C46A"/>
  <path class="sl" d="M0 0 L70 0 A70 70 0 0 1 -35 60.6 Z" fill="#6EC6FF"/>
  <path class="sl" d="M0 0 L-35 60.6 A70 70 0 0 1 -66.6 -21.6 Z" fill="#FF8A8A"/>
  <path class="sl" d="M0 0 L-66.6 -21.6 A70 70 0 0 1 0 -70 Z" fill="#B9A6FF"/>
</svg>'''

BEZA = f'''
        <div class="col" style="top:300px">
          <span class="kick" id="bz-kick">Apa bezanya?</span>
          <span class="t-md center-t" id="bz-title" style="margin-top:16px">Ada vs Tiada <span class="goldt">Dokumen<br>Pengisytiharan Hibah</span></span>
          <div class="panel bad fp" id="bz-a" style="margin-top:30px;padding:26px 36px 22px">
            <span class="tag tag-bad">@@x:26:#FFFFFF:3.4@@ TANPA HIBAH YANG SAH</span>
            <div class="flow2">
              <div class="fnode"><span class="fic">@@home:96:#FFF8E7:1.8@@</span><span>Rumah jadi<br>harta pusaka</span></div>
              <div class="farrow">@@arrow:48:#FF9A9A:2.6@@</div>
              <div class="fnode"><span class="fic">{PIE}</span><span>Dibahagi ikut <b class="redt">FARAID</b></span></div>
            </div>
            <span class="fine">*tertakluk kepada hak &amp; tuntutan lain yang berkaitan</span>
          </div>
          <div class="panel good fp" id="bz-b" style="margin-top:26px;padding:26px 28px 22px">
            <span class="tag tag-good">@@check:26:#0B1F3A:3.4@@ DENGAN DOKUMEN HIBAH YANG SAH</span>
            <div class="steps3">
              <div class="s3" id="bz-s1"><span class="s3i">@@file:52@@</span><span>Dokumen hibah <b>dikemukakan</b></span></div>
              <div class="s3a">@@arrow:30:#6CF0B4:2.6@@</div>
              <div class="s3" id="bz-s2"><span class="s3i">@@gavel:52@@</span><span>semasa <b>bicara kuasa</b> / urusan pusaka</span></div>
              <div class="s3a">@@arrow:30:#6CF0B4:2.6@@</div>
              <div class="s3" id="bz-s3"><span class="s3i">@@home:52@@</span><span>bukti pemberian kepada <b>penerima pilihan</b></span></div>
            </div>
            <div class="result" id="bz-res">@@shield:40:#6CF0B4@@<span>Jika sah, rumah boleh <b class="greent">dikeluarkan</b> daripada harta pusaka yang difaraidkan</span></div>
            <span class="fine">*jika hibah memenuhi syarat &amp; diiktiraf sebagai sah</span>
          </div>
        </div>
'''

KENALI = f'''
        <div class="col" style="top:300px">
          <span class="kick" id="kn-kick">Kenali</span>
          <div id="kn-title" class="col-in" style="margin-top:14px"><span class="t-lg gold">HIBAH DIGITAL</span><span class="t-lg">WASIYYAH</span></div>
          <div class="clipwrap" id="kn-clip" style="margin-top:34px" data-layout-allow-overlap data-layout-allow-occlusion>
            <!-- Press coverage: Berita Harian, 1 Apr 2024 (bharian.com.my/bisnes/korporat/2024/04/1230342) -->
            <div class="paper bh" id="kn-bh">
              <div class="mast">BERITA HARIAN</div>
              <div class="dateline">BISNES &middot; KORPORAT &middot; 1 APRIL 2024</div>
              <div class="hl">Hibah digital Wasiyyah diiktiraf Mahkamah Syariah</div>
              <div class="lead" data-layout-ignore><b>KUALA LUMPUR:</b> Wasiyyah Shoppe Bhd mengumumkan bahawa ia telah berjaya memperoleh <span class="hi" id="kn-hi">perintah pengesahan hibah pertama untuk dokumen hibah digital</span> pelanggannya.</div>
            </div>
            <!-- Press coverage: DagangNews, 11 Feb 2026 (dagangnews.com/article/kolumnis-terkini/...-64907) -->
            <div class="paper dn" id="kn-dn">
              <div class="dnmast"><span>dagangnews</span><small>11 Feb 2026</small></div>
              <div class="dnimg"><img src="assets/press/dagangnews-mbor.jpg" alt="Sijil Malaysia Book of Records Wasiyyah"></div>
              <div class="dnhl">Wasiyyah Cipta Sejarah Pendigitalan Hibah, Diiktiraf Malaysia Book of Records</div>
            </div>
            <div class="bukti" id="kn-bukti">BUKTI</div>
          </div>
          <div class="item rel" id="kn-i0" style="margin-top:54px"><span class="ibub">@@gavel:42@@</span><span class="itxt">Hibah digital yang telah mendapat <b>pengesahan Mahkamah Syariah</b></span></div>
          <div class="item rel" id="kn-i1" style="margin-top:20px"><span class="ibub">@@users:42@@</span><span class="itxt">Digunakan oleh lebih <b class="goldt big" id="kn-num">15,000+</b> <b>pelanggan</b></span></div>
          <div class="item rel" id="kn-i2" style="margin-top:20px"><span class="ibub">@@heart:42@@</span><span class="itxt">Rancang pemberian rumah kepada <b>orang tersayang</b></span></div>
        </div>
'''

PROMO = f'''
        <div class="col" style="top:310px">
          <span class="kick big" id="pr-kick">@@spark:34:#0B1F3A:2.4@@ Promosi Istimewa! @@spark:34:#0B1F3A:2.4@@</span>
          <div class="panel fp" id="pr-panel" style="margin-top:40px;padding:46px 40px 54px">
            <span class="t-sm" id="pr-asal-l">Harga asal</span>
            <span class="strike" id="pr-asal" style="margin-top:4px" data-layout-allow-occlusion><span class="t-lg dim">RM2,600</span><i id="pr-line" data-layout-allow-occlusion></i></span>
            <span class="t-md" id="pr-now" style="margin-top:40px">Sekarang cuma</span>
            <div class="pricewrap"><span class="burst" id="pr-burst" data-layout-ignore>{sparkles()}</span><span class="t-mega gold" id="pr-price">RM499</span></div>
            <span class="sahaja" id="pr-sahaja">sahaja!</span>
            <span class="pill big" id="pr-month" style="margin-top:40px">@@card:36@@ atau RM47/bulan &times; 12 bulan</span>
            <span class="save" id="pr-save" style="margin-top:40px">JIMAT <span id="pr-savenum">RM2,101</span></span>
            <span class="t-xs" id="pr-note" style="margin-top:18px">untuk rumah yang masih dalam pinjaman bank</span>
          </div>
        </div>
'''

DOCS = [("file", "Salinan S&amp;P (Perjanjian Jual Beli)"),
        ("bank", "Surat tawaran pinjaman bank"),
        ("shield", "Dokumen MRTA / MRTT"),
        ("id", "Salinan IC penerima hibah")]
docs = "".join(f'<div class="doc" id="cr-d{i}">@@{ic}:36@@<span>{t}</span></div>' for i, (ic, t) in enumerate(DOCS))
CARA = f'''
        <div class="col" style="top:290px">
          <span class="kick" id="cr-kick">Cara membuat</span>
          <span class="t-lg gold" id="cr-title" style="margin-top:16px">HIBAH RUMAH</span>
          <span class="t-xs" id="cr-sub" style="margin-top:8px">4 langkah mudah</span>
        </div>
        <div class="rail"><i id="cr-rail"></i></div>
        <div class="step" id="cr-s1" style="top:540px"><span class="num">1</span><div><div class="st">Daftar &amp; buat bayaran</div><div class="ss">melalui pautan yang diberikan</div></div><span class="sico">@@card:44@@</span></div>
        <div class="step" id="cr-s2" style="top:680px"><span class="num">2</span><div><div class="st">Muat naik dokumen</div><div class="ss">sediakan dokumen berikut:</div></div><span class="sico">@@upload:44@@</span></div>
        <div class="docs" style="top:806px">{docs}</div>
        <div class="step" id="cr-s3" style="top:1090px"><span class="num">3</span><div><div class="st">Penyediaan skrip akad</div><div class="ss">draf dikeluarkan untuk <b class="goldt" id="cr-semak">semakan</b></div></div><span class="sico">@@pen:44@@</span></div>
        <div class="step" id="cr-s4" style="top:1230px"><span class="num">4</span><div><div class="st">Akad hibah online</div><div class="ss">ijab &amp; qabul dipantau <b class="goldt" id="cr-hq">HQ Wasiyyah</b>,<br>melalui aplikasi <b class="goldt" id="cr-usra">UsraHDD</b></div></div><span class="sico">@@phone:44@@</span></div>
        <div class="col" style="top:1376px"><span class="stamp greent" id="cr-siap">@@check:44:#6CF0B4:3.4@@ SIAP!</span></div>
'''

SERATUS = f'''
        <div class="col" style="top:300px">
          <span class="kick" id="sr-kick">Setakat ini</span>
          <span class="t-md" id="sr-l1" style="margin-top:18px">hibah di <span class="goldt">Wasiyyah</span></span>
          <div class="ringwrap sm" id="sr-ringwrap">
            <svg width="440" height="440" viewBox="0 0 440 440">
              <circle cx="220" cy="220" r="185" fill="none" stroke="rgba(255,255,255,.10)" stroke-width="28"/>
              <circle id="sr-arc" cx="220" cy="220" r="185" fill="none" stroke="url(#srg)" stroke-width="28" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" transform="rotate(-90 220 220)"/>
              <defs><linearGradient id="srg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8FF7C6"/><stop offset="1" stop-color="#3CCB8C"/></linearGradient></defs>
            </svg>
            <span class="ringnum gold" id="sr-num">100%</span>
          </div>
          <span class="t-lg greent" id="sr-l2" style="margin-top:22px">BERJAYA</span>
          <span class="t-md center-t" id="sr-l3" style="margin-top:6px">mendapat <span class="goldt">pengesahan hibah</span></span>
          <!-- Proof: Wasiyyah Shoppe Berhad company profile 2025, page 5 (statistics panel) -->
          <div class="proof" id="sr-proof" style="margin-top:34px" data-layout-allow-overlap data-layout-allow-occlusion>
            <div class="proofhd">@@file:26:#FFFFFF:2.4@@ Profil Syarikat Wasiyyah 2025 &middot; ms. 5</div>
            <div class="proofimg"><img src="assets/press/profil-2025-ms5-statistik.jpg" alt="Statistik profil syarikat Wasiyyah 2025: 100% Hibah Verification Success Rate"><i class="hl100" id="sr-hl"></i></div>
            <div class="bukti" id="sr-bukti">BUKTI</div>
          </div>
        </div>
'''

CTA = f'''
        <div class="glow warm" id="ct-glow"></div>
        <div class="center" style="top:300px" id="ct-hwrap">{HOUSE.format(id="ct-house", w=360, h=317)}</div>
        <div class="col" style="top:680px">
          <span class="t-md center-t" id="ct-l1" style="font-size:42px">Rumah yang kita beli<br>dengan penuh usaha</span>
          <span class="t-md center-t" id="ct-l2" style="font-size:42px;margin-top:6px">bukan sekadar <span class="goldt">aset</span>,</span>
          <span class="t-md center-t" id="ct-l3" style="font-size:42px;margin-top:6px">tetapi tempat berteduh untuk</span>
          <span class="gold big2" id="ct-l3b">orang yang kita sayang.</span>
          <span class="deadline" id="ct-dead" style="margin-top:54px">@@calendar:36:#0B1F3A:2.6@@ Promosi RM499 tamat <b>30 NOVEMBER</b></span>
          <span class="btn" id="ct-btn" style="margin-top:44px">@@chat:44:#0B1F3A:2.6@@ Reply <b>&ldquo;YA&rdquo;</b> sekarang</span>
          <span class="t-xs" id="ct-sub" style="margin-top:26px">Saya akan kongsikan pautan pendaftaran</span>
        </div>
'''

# ---------------------------------------------------------------- page
CSS = r'''
* { margin:0; padding:0; box-sizing:border-box; }
html, body { margin:0; width:1080px; height:1920px; overflow:hidden; background:#0A1A33; }
#root { width:100%; height:100%; position:relative; overflow:hidden; font-family:'Montserrat',sans-serif; color:#FFF8E7; }
#bg { position:absolute; inset:0; z-index:0; overflow:hidden;
  background: radial-gradient(ellipse 120% 70% at 50% 30%, #24507F 0%, #14325A 45%, #0A1A33 100%); }
#bg-pattern { position:absolute; inset:-120px; opacity:.07; background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'><g fill='none' stroke='%23E9C46A' stroke-width='1.2'><path d='M60 14 L73 47 L106 60 L73 73 L60 106 L47 73 L14 60 L47 47 Z'/><rect x='35' y='35' width='50' height='50' transform='rotate(45 60 60)'/><circle cx='60' cy='60' r='9'/></g></svg>"); background-size:120px 120px; }
.orb { position:absolute; border-radius:50%; }
#orb1 { left:-220px; top:120px; width:760px; height:760px; background:radial-gradient(circle, rgba(233,196,106,.20) 0%, rgba(233,196,106,0) 65%); }
#orb2 { right:-260px; top:1000px; width:820px; height:820px; background:radial-gradient(circle, rgba(120,170,230,.18) 0%, rgba(120,170,230,0) 65%); }
#orb3 { left:240px; top:-260px; width:600px; height:600px; background:radial-gradient(circle, rgba(255,240,200,.14) 0%, rgba(255,240,200,0) 65%); }
#brand { position:absolute; left:0; right:0; top:236px; z-index:4; display:flex; justify-content:center; }
#brand span { font-weight:800; font-size:22px; letter-spacing:.22em; text-transform:uppercase; color:rgba(255,233,174,.78);
  display:inline-flex; align-items:center; gap:10px; }
#brand span::before, #brand span::after { content:""; width:46px; height:2px; background:linear-gradient(90deg,rgba(233,196,106,0),#E9C46A); }
#brand span::after { transform:scaleX(-1); }
#progress { position:absolute; left:110px; width:850px; top:1520px; height:6px; border-radius:6px; background:rgba(255,255,255,.10); z-index:4; overflow:hidden; }
#progress i { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:6px; transform-origin:0 50%; transform:scaleX(0);
  background:linear-gradient(90deg,#C9962E,#F2CF76); }
#flash { position:absolute; inset:0; z-index:9; background:#fff; opacity:0; pointer-events:none; }
#shake { position:absolute; inset:0; z-index:5; }

.scene { position:absolute; inset:0; z-index:5; pointer-events:none; }
.row { position:absolute; left:110px; right:120px; display:flex; justify-content:center; align-items:center; gap:16px; text-align:center; }
.col { position:absolute; left:110px; right:120px; display:flex; flex-direction:column; align-items:center; text-align:center; }
.col-in { display:flex; flex-direction:column; align-items:center; }
.panel.fp { position:relative; left:auto; width:850px; display:flex; flex-direction:column; align-items:center; padding:40px 46px; }
.center { position:absolute; left:0; right:0; display:flex; justify-content:center; }
.center-t { text-align:center; line-height:1.18; }
.kick { display:inline-flex; align-items:center; gap:12px; background:linear-gradient(180deg,#F6D98B,#E2B65A); color:#0B1F3A;
  font-weight:800; font-size:32px; letter-spacing:.08em; padding:12px 28px; border-radius:999px; text-transform:uppercase;
  box-shadow:0 10px 24px rgba(0,0,0,.35); }
.kick.big { font-size:40px; padding:16px 34px; }
.t-xs { font-weight:600; font-size:30px; color:rgba(255,248,231,.80); display:inline-flex; align-items:center; gap:10px; }
.t-sm { font-weight:600; font-size:34px; color:rgba(255,248,231,.88); }
.t-md { font-weight:800; font-size:46px; letter-spacing:-.01em; line-height:1.15; }
.t-lg { font-weight:900; font-size:64px; letter-spacing:-.02em; line-height:1.05; }
.t-xl { font-weight:900; font-size:116px; letter-spacing:-.03em; line-height:1.02; }
.t-mega { font-weight:900; font-size:190px; letter-spacing:-.04em; line-height:1; position:relative; }
.gold { background:linear-gradient(180deg,#FFF0C2 0%,#F2CF76 45%,#C9962E 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.goldt { color:#F2CF76; }
.redt { color:#FF8A8A; }
.greent { color:#6CF0B4; }
.dim { color:rgba(255,248,231,.55); }
.big2 { font-size:52px; font-weight:900; line-height:1.15; }
.pill { display:inline-flex; align-items:center; gap:12px; padding:12px 24px; border-radius:999px;
  background:rgba(233,196,106,.16); border:1.5px solid rgba(233,196,106,.55); font-weight:800; font-size:30px; color:#FFE9AE; }
.pill.big { font-size:36px; padding:16px 30px; white-space:nowrap; }
.panel { position:absolute; left:110px; width:860px; border-radius:38px;
  background:linear-gradient(165deg,rgba(16,36,68,.92),rgba(6,15,32,.90)); border:1.5px solid rgba(233,196,106,.45);
  box-shadow:0 30px 70px rgba(0,0,0,.50), inset 0 1px 0 rgba(255,255,255,.10); }
.panel.bad { border-color:rgba(255,138,138,.55); background:linear-gradient(165deg,rgba(60,24,36,.90),rgba(22,10,20,.90)); }
.panel.good { border-color:rgba(108,240,180,.55); background:linear-gradient(165deg,rgba(14,52,56,.92),rgba(6,22,30,.92)); }
.stamp { display:inline-flex; align-items:center; gap:14px; padding:12px 32px; border:6px solid currentColor; border-radius:20px;
  font-weight:900; font-size:60px; letter-spacing:.05em; transform:rotate(-3deg); white-space:nowrap; }
.quote { font-weight:700; font-size:38px; line-height:1.35; text-align:center; font-style:italic; color:rgba(255,248,231,.92); }

/* hook / cta house */
.house .draw { stroke-dasharray:1; stroke-dashoffset:1; }
.glow { position:absolute; left:190px; top:300px; width:700px; height:600px; border-radius:50%; opacity:0;
  background:radial-gradient(circle, rgba(255,214,120,.42) 0%, rgba(255,214,120,0) 62%); }
.glow.warm { top:200px; }

/* bila items */
.item { position:absolute; left:110px; width:850px; height:128px; border-radius:30px; display:flex; align-items:center; gap:24px; padding:0 30px 0 22px;
  background:linear-gradient(165deg,rgba(16,36,68,.90),rgba(6,15,32,.86)); border:1.5px solid rgba(233,196,106,.30);
  box-shadow:0 18px 40px rgba(0,0,0,.40); }
.item.rel { position:relative; left:auto; width:850px; height:126px; }
.ibub { flex:none; width:80px; height:80px; border-radius:24px; display:flex; align-items:center; justify-content:center;
  background:rgba(233,196,106,.14); border:1.5px solid rgba(233,196,106,.45); }
.itxt { flex:1; font-weight:600; font-size:35px; line-height:1.18; text-align:left; color:rgba(255,248,231,.92); }
.itxt b { font-weight:800; color:#FFF8E7; }
.itxt b.goldt { color:#F2CF76; }
.itxt .big { font-size:44px; font-weight:900; }
.itick { flex:none; width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(180deg,#8FF7C6,#3CCB8C); box-shadow:0 6px 16px rgba(60,203,140,.45); }

/* tunggu loan bar */
.loan { position:relative; width:100%; }
.loanlbl { display:flex; justify-content:space-between; align-items:center; font-weight:700; font-size:28px; color:rgba(255,248,231,.85); margin-bottom:12px; }
.loanlbl span { display:inline-flex; align-items:center; gap:10px; }
.loanlbl.small { font-size:22px; font-weight:600; color:rgba(255,248,231,.6); margin:12px 0 0; }
.bar { position:relative; height:34px; border-radius:999px; background:rgba(255,255,255,.10); overflow:hidden; }
.bar i { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:999px; transform-origin:0 50%; transform:scaleX(0);
  background:linear-gradient(90deg,#C9962E,#F2CF76); }

/* beza */
.tag { position:relative; align-self:flex-start; display:inline-flex; align-items:center; gap:10px; padding:10px 20px; border-radius:999px;
  font-weight:800; font-size:26px; letter-spacing:.06em; }
.tag-bad { background:#E35D6A; color:#fff; }
.tag-good { background:linear-gradient(180deg,#8FF7C6,#3CCB8C); color:#0B1F3A; }
.flow2 { position:relative; width:100%; margin-top:18px; display:flex; align-items:center; justify-content:space-around; }
.fnode { display:flex; flex-direction:column; align-items:center; gap:8px; width:300px; }
.fnode > span:last-child { font-weight:700; font-size:31px; line-height:1.2; text-align:center; }
.fic { height:130px; display:flex; align-items:center; justify-content:center; }
.fine { position:relative; margin-top:14px; text-align:center; font-weight:500; font-size:24px; font-style:italic; color:rgba(255,248,231,.66); }
.steps3 { position:relative; width:100%; margin-top:22px; display:flex; align-items:flex-start; justify-content:space-between; }
.s3 { width:244px; display:flex; flex-direction:column; align-items:center; gap:12px; }
.s3i { width:100px; height:100px; border-radius:30px; display:flex; align-items:center; justify-content:center;
  background:rgba(108,240,180,.12); border:1.5px solid rgba(108,240,180,.5); }
.s3 > span:last-child { font-weight:600; font-size:28px; line-height:1.22; text-align:center; }
.s3a { padding-top:35px; }
.result { position:relative; width:100%; margin-top:24px; min-height:116px; padding-top:14px !important; padding-bottom:14px !important; border-radius:26px; display:flex; align-items:center; gap:20px; padding:0 28px;
  background:rgba(108,240,180,.10); border:1.5px dashed rgba(108,240,180,.6); }
.result span { font-weight:700; font-size:30px; line-height:1.25; text-align:left; }

/* kenali press clippings */
.clipwrap { position:relative; width:850px; height:440px; flex:none; }
.paper { position:absolute; border-radius:8px; background:linear-gradient(170deg,#F8F2E2,#E9DFC6); color:#211B12;
  box-shadow:0 26px 54px rgba(0,0,0,.55); overflow:hidden; text-align:left; }
.paper.bh { left:6px; top:34px; width:440px; height:392px; padding:22px 26px; transform:rotate(-5deg); }
.mast { font-family:'Merriweather',Georgia,serif; font-weight:900; font-size:34px; letter-spacing:.06em; text-align:center;
  border-bottom:3px double #211B12; padding-bottom:6px; }
.dateline { font-weight:700; font-size:16px; letter-spacing:.12em; color:#6B5B3E; text-align:center; margin:8px 0 12px; }
.hl { font-family:'Merriweather',Georgia,serif; font-weight:900; font-size:32px; line-height:1.18; }
.lead { font-family:'Merriweather',Georgia,serif; font-size:19px; line-height:1.5; color:#3A3122; margin-top:12px;
  border-top:1.5px solid rgba(33,27,18,.35); padding-top:10px; }
.hi { background-image:linear-gradient(transparent 52%, rgba(242,207,118,.95) 52%); background-repeat:no-repeat; background-size:0% 100%; }
.paper.dn { right:6px; top:0; width:400px; height:430px; padding:16px 18px 18px; transform:rotate(4deg); background:#FFFFFF; }
.dnmast { display:flex; justify-content:space-between; align-items:baseline; border-bottom:4px solid #6B2C8F; padding-bottom:6px; }
.dnmast span { font-weight:900; font-size:30px; letter-spacing:-.02em; color:#2A2A2A; }
.dnmast small { font-weight:600; font-size:16px; color:#777; }
.dnimg { margin-top:12px; height:200px; border-radius:4px; overflow:hidden; background:#ddd; }
.dnimg img { width:100%; height:100%; object-fit:cover; object-position:50% 45%; display:block; }
.dnhl { font-weight:800; font-size:26px; line-height:1.22; color:#1E1E1E; margin-top:12px; }
.bukti { position:absolute; left:640px; top:410px; z-index:3; padding:8px 22px; border:5px solid #C93545; color:#C93545; border-radius:14px;
  font-weight:900; font-size:44px; letter-spacing:.1em; transform:rotate(10deg); background:rgba(255,248,231,.92); }

/* promo */
.strike { position:relative; display:inline-block; }
.strike i { position:absolute; left:-12px; right:-12px; top:60%; height:8px; margin-top:-4px; border-radius:8px; background:#FF6B6B;
  transform:rotate(-6deg); transform-origin:0 50%; }
.sahaja { position:relative; margin-top:-6px; font-weight:900; font-size:40px; color:#0B1F3A; background:#6CF0B4; padding:6px 22px; border-radius:14px;
  transform:rotate(-4deg); }
.pricewrap { position:relative; display:flex; justify-content:center; align-items:center; }
.burst { position:absolute; left:50%; top:50%; width:0; height:0; z-index:-1; }
.spk { position:absolute; left:0; top:0; border-radius:3px; background:#F2CF76; transform:rotate(45deg); opacity:0; }
.save { display:inline-flex; gap:14px; font-weight:900; font-size:60px; color:#0B1F3A; background:linear-gradient(180deg,#8FF7C6,#3CCB8C);
  padding:14px 40px; border-radius:24px; box-shadow:0 14px 30px rgba(60,203,140,.40); }

/* seratus */
.ringwrap { position:relative; width:440px; height:440px; margin-top:30px; flex:none; }
.ringwrap svg { position:absolute; inset:0; }
.ringnum { position:absolute; left:0; right:0; top:50%; transform:translateY(-50%); text-align:center; font-weight:900; font-size:112px; letter-spacing:-.04em; line-height:1; }
.ringwrap.sm { width:300px; height:300px; margin-top:22px; }
.ringwrap.sm svg { width:300px; height:300px; }
.ringwrap.sm .ringnum { font-size:80px; }
.proof { position:relative; width:780px; flex:none; background:#FFFFFF; border-radius:18px; padding:0 18px 18px;
  box-shadow:0 22px 48px rgba(20,55,100,.30); transform:rotate(-1.5deg); }
.proofhd { margin:0 -18px 16px; padding:12px 20px; background:#0F2B50; color:#FFFFFF; font-weight:700; font-size:26px;
  border-radius:18px 18px 0 0; display:flex; align-items:center; gap:12px; text-align:left; }
.proofimg { position:relative; width:744px; height:317px; border-radius:10px; overflow:visible; }
.proofimg img { width:100%; height:100%; display:block; border-radius:10px; }
.hl100 { position:absolute; left:482px; top:156px; width:202px; height:112px; border:5px solid #D2334A; border-radius:20px; opacity:0;
  box-shadow:0 0 0 6px rgba(210,51,74,.18); }
#sr-bukti { left:auto; right:-34px; top:356px; font-size:38px; }
/* cara */
.rail { position:absolute; left:163px; top:596px; width:6px; height:690px; border-radius:6px; background:rgba(255,255,255,.12); overflow:hidden; }
.rail i { position:absolute; inset:0; transform-origin:50% 0; transform:scaleY(0); background:linear-gradient(180deg,#F2CF76,#C9962E); }
.step { position:absolute; left:110px; width:860px; height:110px; display:flex; align-items:center; gap:26px; }
.num { flex:none; width:112px; height:112px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:54px; color:#0B1F3A; background:linear-gradient(180deg,#F6D98B,#E2B65A);
  box-shadow:0 0 0 8px rgba(233,196,106,.18), 0 12px 26px rgba(0,0,0,.45); }
.step > div { flex:1; }
.st { font-weight:800; font-size:40px; line-height:1.1; }
.ss { font-weight:600; font-size:28px; line-height:1.2; color:rgba(255,248,231,.78); margin-top:6px; }
.sico { flex:none; width:84px; height:84px; border-radius:24px; display:flex; align-items:center; justify-content:center;
  background:rgba(233,196,106,.12); border:1.5px solid rgba(233,196,106,.40); }
.docs { position:absolute; left:248px; width:722px; display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.doc { height:122px; border-radius:22px; display:flex; align-items:center; gap:14px; padding:0 18px;
  background:rgba(255,248,231,.07); border:1.5px solid rgba(255,248,231,.20); }
.doc span { font-weight:700; font-size:28px; line-height:1.18; text-align:left; }
.doc small { font-size:20px; font-weight:600; color:rgba(255,248,231,.7); }

/* cta */
.deadline { display:inline-flex; align-items:center; gap:14px; padding:16px 30px; border-radius:20px; background:#FF8A8A; color:#0B1F3A;
  font-weight:700; font-size:32px; box-shadow:0 14px 30px rgba(255,100,100,.35); white-space:nowrap; }
.deadline b { font-weight:900; }
.btn { display:inline-flex; align-items:center; gap:18px; padding:26px 52px; border-radius:999px; background:linear-gradient(180deg,#F6D98B,#E2B65A);
  color:#0B1F3A; font-weight:800; font-size:50px; white-space:nowrap; box-shadow:0 0 0 10px rgba(233,196,106,.20), 0 20px 40px rgba(0,0,0,.45); }
.btn b { font-weight:900; }

/* ===== SOFT BLUE THEME (overrides the navy base above) ===== */
html, body { background:#DCEBFA; }
#root { color:#0E2A4D; }
#bg { background: radial-gradient(ellipse 120% 72% at 50% 26%, #F4F9FF 0%, #DCEBFA 42%, #B7D4F1 100%); }
#bg-pattern { opacity:.10; background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'><g fill='none' stroke='%233A6EA8' stroke-width='1.2'><path d='M60 14 L73 47 L106 60 L73 73 L60 106 L47 73 L14 60 L47 47 Z'/><rect x='35' y='35' width='50' height='50' transform='rotate(45 60 60)'/><circle cx='60' cy='60' r='9'/></g></svg>"); }
#orb1 { background:radial-gradient(circle, rgba(255,255,255,.70) 0%, rgba(255,255,255,0) 65%); }
#orb2 { background:radial-gradient(circle, rgba(120,175,235,.35) 0%, rgba(120,175,235,0) 65%); }
#orb3 { background:radial-gradient(circle, rgba(255,236,190,.45) 0%, rgba(255,236,190,0) 65%); }
#brand span { color:#2C5C90; }
#brand span::before, #brand span::after { background:linear-gradient(90deg,rgba(44,92,144,0),#2C5C90); }
#progress { background:rgba(14,42,77,.12); }

/* text that sits straight on the light background */
.t-xs { color:rgba(14,42,77,.78); }
.t-sm { color:rgba(14,42,77,.88); }
.quote { color:#163A66; }
.gold { background:linear-gradient(180deg,#D99A22 0%,#B8780F 50%,#8E5609 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.goldt { color:#A86A0A; }
.redt { color:#D2334A; }
.greent { color:#13895A; }
.pill { background:rgba(255,255,255,.75); border-color:rgba(184,120,15,.55); color:#8A560A; }
.pill svg, .sico svg, .doc svg { stroke:#B8780F; }
.kick { box-shadow:0 10px 22px rgba(20,60,110,.22); }
.stamp.greent { background:rgba(255,255,255,.6); }

/* dark cards keep light text and the bright gold */
.panel, .item { color:#FFF8E7; }
.panel { background:linear-gradient(165deg,#1B4272,#0F2B50); box-shadow:0 26px 60px rgba(20,55,100,.30), inset 0 1px 0 rgba(255,255,255,.12); }
.item { background:linear-gradient(165deg,#1B4272,#0F2B50); box-shadow:0 16px 36px rgba(20,55,100,.26); }
.panel .t-xs { color:rgba(255,248,231,.80); }
.panel .t-sm { color:rgba(255,248,231,.88); }
.panel .gold { background:linear-gradient(180deg,#FFF0C2 0%,#F2CF76 45%,#C9962E 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.panel .goldt, .item .goldt { color:#F2CF76; }
.panel .redt { color:#FF8A8A; }
.panel .greent { color:#6CF0B4; }
.panel .pill { background:rgba(233,196,106,.16); border-color:rgba(233,196,106,.55); color:#FFE9AE; }
.panel .pill svg { stroke:#E9C46A; }

/* house art */
.house .draw[stroke="#FFF8E7"] { stroke:#1C3D66; }
.house .draw[stroke="#F2CF76"] { stroke:#C98614; }
.house .win { stroke:#1C3D66; }
.glow { background:radial-gradient(circle, rgba(255,205,100,.55) 0%, rgba(255,205,100,0) 62%); }

/* seratus ring */
#sr-ringwrap circle:first-of-type { stroke:rgba(14,42,77,.12); }

/* cara: steps and documents sit on the background */
.st { color:#0E2A4D; }
.ss { color:rgba(14,42,77,.78); }
.sico { background:rgba(255,255,255,.72); border-color:rgba(184,120,15,.40); }
.rail { background:rgba(14,42,77,.14); }
.num { box-shadow:0 0 0 8px rgba(233,196,106,.25), 0 12px 24px rgba(20,55,100,.25); }
.doc { background:rgba(255,255,255,.78); border-color:rgba(14,42,77,.12); color:#0E2A4D; box-shadow:0 8px 20px rgba(20,55,100,.10); }
.btn { box-shadow:0 0 0 10px rgba(233,196,106,.25), 0 18px 36px rgba(20,55,100,.28); }
.deadline { box-shadow:0 12px 26px rgba(210,51,74,.25); }
'''

JS = r'''
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const IN=(s,t,o={})=>tl.fromTo(s,{opacity:0,y:o.y??28,x:o.x??0,scale:o.s??0.94,filter:'blur(8px)'},{opacity:1,y:0,x:0,scale:1,filter:'blur(0px)',duration:o.d??0.45,ease:o.e??'power3.out',stagger:o.st??0},t);
const POP=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??0.35},{opacity:1,scale:1,duration:o.d??0.5,ease:'back.out(2.2)',stagger:o.st??0},t);
const SLAM=(s,t,o={})=>tl.fromTo(s,{opacity:0,scale:o.s??1.9,filter:'blur(10px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:o.d??0.26,ease:'power4.in'},t);
const OUT=(s,t,d=0.3)=>tl.to(s,{opacity:0,y:-18,filter:'blur(8px)',duration:d,ease:'power2.in'},t);
const COUNT=(s,a,b,t,d,f,e='power2.out')=>{const el=document.querySelector(s);const o={v:a};tl.fromTo(o,{v:a},{v:b,duration:d,ease:e,onUpdate:()=>{el.textContent=f(o.v)}},t);};
const NUM=(v)=>Math.round(v).toLocaleString('en-US');
const DRAW=(s,t,d=1.2,st=0.12)=>tl.fromTo(s,{strokeDashoffset:1},{strokeDashoffset:0,duration:d,ease:'power2.inOut',stagger:st},t);
const SHAKE=(t,a=10)=>{[[1,-.6],[-.8,.9],[.6,-.4],[-.4,.5],[.2,-.2],[0,0]].forEach((p,i)=>tl.to('#shake',{x:p[0]*a,y:p[1]*a,duration:0.035,ease:'none'},t+i*0.035));};
const GLOW=(s,t)=>tl.fromTo(s,{textShadow:'0 0 0px rgba(242,207,118,0)'},{textShadow:'0 0 22px rgba(242,207,118,.95)',duration:0.45,yoyo:true,repeat:1,ease:'sine.inOut'},t);
const FLASH=(t,o=.75)=>tl.fromTo('#flash',{opacity:o},{opacity:0,duration:0.25,ease:'power2.out',immediateRender:false},t);

// ambient background drift
tl.fromTo('#bg-pattern',{x:0,y:0},{x:120,y:-240,duration:TOTAL,ease:'none'},0);
tl.fromTo('#orb1',{x:0,y:0},{x:120,y:160,duration:TOTAL,ease:'sine.inOut'},0);
tl.fromTo('#orb2',{x:0,y:0},{x:-140,y:-220,duration:TOTAL,ease:'sine.inOut'},0);
tl.fromTo('#progress i',{scaleX:0},{scaleX:1,duration:TOTAL,ease:'none'},0);
tl.set('#flash',{opacity:0},0);
IN('#brand',0.2,{y:-10});

/* 1 HOOK */
DRAW('#hk-house .draw',H+0.05,1.2);
IN('#hk-l1',H+0.05);
IN('#hk-l2',H+1.08);
SLAM('#hk-l2b',H+1.85,{s:1.5});
tl.to('#hk-house .win',{fill:'#FFD36E',duration:0.35,ease:'power2.out'},H+2.15);
tl.to('#hk-glow',{opacity:1,duration:0.6},H+2.15);
IN('#hk-l3',H+3.7);
POP('#hk-pill',H+4.4);
tl.to('#hk-house .win',{fill:'#3E6290',duration:0.12,ease:'none'},H+5.0);
tl.to('#hk-glow',{opacity:0,duration:0.25},H+5.0);
tl.to('#hk-house',{opacity:.55,duration:0.4},H+5.05);
SHAKE(H+5.0,8);
OUT('#sc-hook > *',H+5.55);

/* 2 BILA */
POP('#bl-kick',B+0.05);
SLAM('#bl-title',B+0.2,{s:1.6});
BILA_CUES.forEach((o,i)=>{
  IN('#bl-i'+i,B+o,{x:-60,y:0});
  POP('#bl-t'+i,B+o+0.55,{s:0.2});
});
OUT('#sc-bila > *',B+20.35);

/* 3 TUNGGU */
IN('#tg-l1',T+0.27);
GLOW('#tg-l1 b',T+2.1);
IN('#tg-l2',T+3.98); IN('#tg-l2b',T+4.35);
IN('#tg-panel',T+6.2,{y:40});
tl.fromTo('#tg-bar',{scaleX:0},{scaleX:0.33,duration:2.4,ease:'power1.inOut'},T+6.4);
COUNT('#tg-yr',1,10,T+6.4,2.4,v=>'Tahun '+Math.round(v),'power1.inOut');
SLAM('#tg-stamp',T+6.6,{s:2.2});
SHAKE(T+6.86,7);
IN('#tg-hg',T+8.2,{y:10});
IN('#tg-q',T+9.1);
OUT('#sc-tunggu > *',T+12.0);

/* 4 BEZA */
POP('#bz-kick',Z+0.05);
IN('#bz-title',Z+0.29);
tl.fromTo('#bz-title .goldt',{textShadow:'0 0 0px rgba(242,207,118,0)'},{textShadow:'0 0 26px rgba(242,207,118,.9)',duration:0.55,yoyo:true,repeat:1,ease:'sine.inOut'},Z+2.2);
IN('#bz-a',Z+4.45,{y:40});
tl.fromTo('#bz-a .fnode:first-child .fic',{scale:1},{scale:1.12,duration:0.35,yoyo:true,repeat:1,ease:'sine.inOut'},Z+7.4);
tl.fromTo('#bz-pie .sl',{scale:1,x:0,y:0,transformOrigin:'0px 0px'},{scale:0.86,duration:0.3,ease:'power2.out'},Z+8.8);
['#bz-pie .sl:nth-child(1)','#bz-pie .sl:nth-child(2)','#bz-pie .sl:nth-child(3)','#bz-pie .sl:nth-child(4)'].forEach((s,i)=>{
  const d=[[9,-9],[9,9],[-9,9],[-9,-9]][i];
  tl.to(s,{x:d[0],y:d[1],duration:0.3,ease:'back.out(2)'},Z+8.9+i*0.12);
});
IN('#bz-b',Z+10.25,{y:40});
POP('#bz-s1',Z+12.8); POP('#bz-s2',Z+14.8); GLOW('#bz-s2 b',Z+16.7); POP('#bz-s3',Z+18.5);
IN('#bz-res',Z+20.83,{y:16});
tl.fromTo('#bz-res',{boxShadow:'0 0 0 0 rgba(108,240,180,0)'},{boxShadow:'0 0 0 14px rgba(108,240,180,.18)',duration:0.5,yoyo:true,repeat:1},Z+23.3);
OUT('#sc-beza > *',Z+25.1);

/* 5 KENALI */
POP('#kn-kick',K+0.22);
SLAM('#kn-title',K+1.4,{s:1.5});
tl.fromTo('#kn-bh',{opacity:0,x:-160,y:80,rotation:-16},{opacity:1,x:0,y:0,rotation:-5,duration:0.6,ease:'power3.out'},K+1.9);
tl.fromTo('#kn-dn',{opacity:0,x:160,y:80,rotation:14},{opacity:1,x:0,y:0,rotation:4,duration:0.6,ease:'power3.out'},K+2.35);
SLAM('#kn-bukti',K+2.85,{s:2.4});
tl.fromTo('#kn-hi',{backgroundSize:'0% 100%'},{backgroundSize:'100% 100%',duration:0.9,ease:'power2.inOut'},K+4.0);
IN('#kn-i0',K+3.54,{x:-60,y:0});
IN('#kn-i1',K+7.12,{x:-60,y:0});
COUNT('#kn-num',0,15000,K+7.27,1.5,v=>NUM(v)+'+');
IN('#kn-i2',K+10.05,{x:-60,y:0});
OUT('#sc-kenali > *',K+12.8);

/* 5b SERATUS: 100% pengesahan, with the company-profile proof */
POP('#sr-kick',R+0.35);
tl.fromTo('#sr-proof',{opacity:0,y:120,rotation:-6},{opacity:1,y:0,rotation:-1.5,duration:0.6,ease:'power3.out'},R+1.0);
IN('#sr-l1',R+1.8);
tl.fromTo('#sr-ringwrap',{opacity:0,scale:0.7},{opacity:1,scale:1,duration:0.45,ease:'back.out(1.8)'},R+1.6);
tl.fromTo('#sr-arc',{strokeDashoffset:1},{strokeDashoffset:0,duration:1.2,ease:'power2.inOut'},R+2.1);
COUNT('#sr-num',0,100,R+2.1,1.2,v=>Math.round(v)+'%','power2.inOut');
tl.fromTo('#sr-ringwrap',{scale:1},{scale:1.08,duration:0.18,yoyo:true,repeat:1,ease:'power2.out',immediateRender:false},R+3.3);
FLASH(R+3.3,.3);
tl.fromTo('#sr-hl',{opacity:0,scale:1.5},{opacity:1,scale:1,duration:0.35,ease:'back.out(2)'},R+3.35);
tl.fromTo('#sr-hl',{boxShadow:'0 0 0 6px rgba(210,51,74,.18)'},{boxShadow:'0 0 0 16px rgba(210,51,74,.10)',duration:0.5,yoyo:true,repeat:3,ease:'sine.inOut',immediateRender:false},R+3.7);
SLAM('#sr-l2',R+3.7,{s:1.9});
IN('#sr-l3',R+4.0,{y:12});
SLAM('#sr-bukti',R+4.4,{s:2.4});
OUT('#sc-seratus > *',R+6.4);

/* 6 PROMO */
POP('#pr-kick',P+0.2,{s:0.5});
IN('#pr-panel',P+1.2,{y:40});
IN('#pr-asal-l',P+1.6,{y:10}); IN('#pr-asal',P+1.7,{y:14});
tl.fromTo('#pr-line',{scaleX:0,scaleY:1,skewX:0,rotation:-6},{scaleX:1,scaleY:1,skewX:0,rotation:-6,duration:0.35,ease:'power2.out'},P+3.05);
tl.to('#pr-asal',{scale:0.9,opacity:.7,duration:0.3},P+3.5);
IN('#pr-now',P+4.7,{y:12});
SLAM('#pr-price',P+6.0,{s:2.6,d:0.28});
FLASH(P+6.28,.6); SHAKE(P+6.28,14);
document.querySelectorAll('#pr-burst .spk').forEach((el,i)=>{
  const a=parseFloat(el.dataset.a)*Math.PI/180, d=parseFloat(el.dataset.d);
  tl.fromTo(el,{x:0,y:0,opacity:0,scale:0.3},{x:Math.cos(a)*d,y:Math.sin(a)*d*0.6,opacity:1,scale:1,duration:0.5,ease:'power3.out'},P+6.3);
  tl.to(el,{opacity:0,scale:0.2,duration:0.5,ease:'power2.in'},P+6.9+(i%5)*0.06);
});
POP('#pr-sahaja',P+6.9,{s:0.2});
tl.to('#pr-price',{scale:1.05,duration:0.6,yoyo:true,repeat:3,ease:'sine.inOut'},P+7.35);
POP('#pr-month',P+7.81);
POP('#pr-save',P+11.5,{s:0.5});
COUNT('#pr-savenum',0,2101,P+11.55,1.0,v=>'RM'+NUM(v));
IN('#pr-note',P+13.85,{y:10});
OUT('#sc-promo > *',P+15.97,0.26);

/* 7 CARA */
POP('#cr-kick',C+0.05);
SLAM('#cr-title',C+0.26,{s:1.6});
IN('#cr-sub',C+1.91,{y:10});
tl.fromTo('#cr-rail',{scaleY:0},{scaleY:0.04,duration:0.6,ease:'power2.out'},C+3.55);
IN('#cr-s1',C+3.55,{x:-50,y:0});
GLOW('#cr-s1 .ss',C+5.95);
tl.to('#cr-rail',{scaleY:0.21,duration:0.6,ease:'power2.out'},C+7.76);
IN('#cr-s2',C+7.76,{x:-50,y:0});
CARA_DOCS.forEach((o,i)=>POP('#cr-d'+i,C+o,{s:0.4}));
tl.to('#cr-rail',{scaleY:0.80,duration:0.6,ease:'power2.out'},C+17.16);
IN('#cr-s3',C+17.16,{x:-50,y:0});
GLOW('#cr-semak',C+20.15);
tl.to('#cr-rail',{scaleY:1,duration:0.6,ease:'power2.out'},C+22.29);
IN('#cr-s4',C+22.29,{x:-50,y:0});
GLOW('#cr-s4 .st',C+25.6);
GLOW('#cr-hq',C+26.65);
GLOW('#cr-usra',C+30.1);
SLAM('#cr-siap',C+31.85,{s:2.3});
SHAKE(C+32.11,8);
OUT('#sc-cara > *',C+32.6);

/* 8 CTA */
DRAW('#ct-house .draw',A+0.1,1.0,0.08);
tl.to('#ct-house .win',{fill:'#FFD36E',duration:0.4},A+0.9);
tl.to('#ct-glow',{opacity:1,duration:0.8},A+0.9);
IN('#ct-l1',A+0.25); IN('#ct-l2',A+3.4); IN('#ct-l3',A+4.6); IN('#ct-l3b',A+6.3);
tl.fromTo('#ct-house .hheart',{opacity:0,scale:0.3,transformOrigin:'250px 250px'},{opacity:1,scale:1,duration:0.6,ease:'back.out(2.5)'},A+6.35);
tl.to('#ct-hwrap',{y:-14,duration:1.6,yoyo:true,repeat:7,ease:'sine.inOut'},A+6.8);
tl.to('#ct-glow',{opacity:.6,duration:1.6,yoyo:true,repeat:7,ease:'sine.inOut'},A+6.8);
SLAM('#ct-dead',A+9.7,{s:1.8});
POP('#ct-btn',A+14.38,{s:0.4});
tl.to('#ct-btn',{scale:1.06,duration:0.45,yoyo:true,repeat:7,ease:'sine.inOut'},A+15.0);
IN('#ct-sub',A+15.9,{y:10});

window.__timelines["main"] = tl;
'''

def build():
    consts = (f"const TOTAL={TOTAL};const H={S('hook')},B={S('bila')},T={S('tunggu')},Z={S('beza')},"
              f"K={S('kenali')},R={S('seratus')},P={S('promo')},C={S('cara')},A={S('cta')};"
              f"const BILA_CUES={BILA_CUES},CARA_DOCS={CARA_DOCS};")
    scenes = "\n".join([
        scene_tags("hook", HOOK), scene_tags("bila", BILA), scene_tags("tunggu", TUNGGU),
        scene_tags("beza", BEZA), scene_tags("kenali", KENALI), scene_tags("promo", PROMO),
        scene_tags("seratus", SERATUS), scene_tags("cara", CARA), scene_tags("cta", CTA),
    ])
    html = f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;0,900;1,700&display=block" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="bg" data-layout-ignore><div id="bg-pattern"></div><div class="orb" id="orb1"></div><div class="orb" id="orb2"></div><div class="orb" id="orb3"></div></div>
      <div id="brand" data-layout-ignore><span>Hibah Digital Wasiyyah</span></div>
      <div id="progress" data-layout-ignore><i></i></div>
      <div id="shake">
{scenes}
      </div>
      <div id="flash" data-layout-ignore></div>

      <!-- Voice-over (cleaned: highpass, denoise, compression, -16 LUFS) -->
      <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="151.88" data-volume="1" data-track-index="0"></audio>

      <hf-audio-group id="sfx"></hf-audio-group>
{sfx_tags()}
    </div>
    <script>
{consts}
{JS}
    </script>
  </body>
</html>
'''
    html = expand_icons(html)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html written: {len(html)} bytes, {len(SFX)} sfx")

if __name__ == "__main__":
    build()
