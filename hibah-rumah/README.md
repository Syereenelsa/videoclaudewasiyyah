# Hibah Rumah RM499: infographic video (HyperFrames)

Vertical 1080×1920 motion-graphic infographic, 2:33, timed to the recorded voice-over, navy + gold (same look as `wasiyyah-reel`).
No footage: every visual is HTML/SVG animated with GSAP.

- **Voice-over script with timecodes:** [`SKRIP-VO.md`](SKRIP-VO.md)
- **Preview frames:** `preview/contact-sheet.jpg`
- **Draft preview MP4:** `renders/hibah-rumah-preview.mp4` (not in git)

## Scenes

| # | Time | Scene |
|---|---|---|
| 1 | 0:00 – 0:05.9 | Hook: house drawn, lights on, then out ("jika kita sudah tiada?") |
| 2 | 0:05.9 – 0:26.5 | Bila perlu buat hibah rumah: 6-item checklist |
| 3 | 0:26.5 – 0:38.8 | Jangan tunggu sehingga rumah habis bayar (loan bar + stamp) |
| 4 | 0:38.8 – 1:04.2 | Tanpa vs dengan dokumen hibah (faraid pie vs 3-step flow) |
| 5 | 1:04.2 – 1:17.3 | Kenali Hibah Digital Wasiyyah: press clippings (Berita Harian, DagangNews) + 3 proof points |
| 5b | 1:17.3 – 1:22.8 | Setakat ini, 100% hibah di Wasiyyah berjaya mendapat pengesahan (ring fills to 100%) |
| 6 | 1:22.8 – 1:40.3 | Promosi: RM2,600 struck out, RM499 slam, RM47 × 12, JIMAT RM2,101 |
| 7 | 1:40.3 – 2:13.2 | 4 langkah (documents; draf untuk semakan; akad dipantau HQ Wasiyyah via UsraHDD) |
| 8 | 2:13.2 – 2:33.3 | Closing line, tamat 30 November, "Reply YA" button |

## Sound
- No background music (sound effects only).
- 83 sound effects (whoosh, pop, ding, stamp, impact, riser, cash, clock, tick, lock) placed on each animation beat, from `assets/sfx/`.
- Voice-over: `assets/voice.wav` (the supplied recording, version 2 with the 100% line, cleaned: highpass 80 Hz, FFT denoise, gentle compression, -16 LUFS). Word timings in `tools/transcript.json` (Whisper medium, Malay); scene cues were checked against the pauses in the audio.

## Editing
`index.html` is generated. Edit `tools/build.py`, then:

```bash
python3 tools/build.py
npm run check
npx --yes hyperframes@0.9.66 snapshot --at 5,23,40
npx --yes hyperframes@0.9.66 render --quality draft -o renders/hibah-rumah-preview.mp4
```

Scene start/end times live in `SCENES` at the top of `tools/build.py`; animation and SFX offsets inside a scene follow it.

## To do before final
1. Scene 5b (100%) follows the voice-over wording. The company profile it refers to (Scribd, page 5) could not be opened from here; add any figures from it once supplied.
2. Scene 5 press clippings, sources:
   - Berita Harian, 1 Apr 2024, "Hibah digital Wasiyyah diiktiraf Mahkamah Syariah": https://www.bharian.com.my/bisnes/korporat/2024/04/1230342/hibah-digital-wasiyyah-diiktiraf-mahkamah-syariah . Its photo is blocked for automated download, so this clipping is typeset from the real headline, date and opening paragraph. To use the real photo or a screenshot, save it in `assets/press/` and add an `<img>` to `#kn-bh`.
   - DagangNews, 11 Feb 2026, "Wasiyyah Cipta Sejarah Pendigitalan Hibah, Diiktiraf Malaysia Book of Records": https://www.dagangnews.com/article/kolumnis-terkini/wasiyyah-cipta-sejarah-pendigitalan-hibah-diiktiraf-malaysia-book-records-64907 . Photo: `assets/press/dagangnews-mbor.jpg` (from the article).
3. Confirm the instalment figure: RM47 × 12 = RM564, which is more than RM499.
