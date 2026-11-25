# Hibah Rumah RM499: infographic video (HyperFrames)

Vertical 1080×1920 motion-graphic infographic, 1:46.5, navy + gold (same look as `wasiyyah-reel`).
No footage: every visual is HTML/SVG animated with GSAP.

- **Voice-over script with timecodes:** [`SKRIP-VO.md`](SKRIP-VO.md)
- **Preview frames:** `preview/contact-sheet.jpg`
- **Draft preview MP4:** `renders/hibah-rumah-preview.mp4` (not in git)

## Scenes

| # | Time | Scene |
|---|---|---|
| 1 | 0:00 – 0:06.5 | Hook: house drawn, lights on, then out ("jika kita sudah tiada?") |
| 2 | 0:06.5 – 0:24 | Bila perlu buat hibah rumah: 6-item checklist |
| 3 | 0:24 – 0:33 | Jangan tunggu sehingga rumah habis bayar (loan bar + stamp) |
| 4 | 0:33 – 0:49.5 | Tanpa vs dengan dokumen hibah (faraid pie vs 3-step flow) |
| 5 | 0:49.5 – 1:00.5 | Kenali Hibah Digital Wasiyyah: two press clippings (Berita Harian, DagangNews) + 3 proof points (15,000+ counter) |
| 6 | 1:00.5 – 1:13.5 | Promosi: RM2,600 struck out, RM499 slam, RM47 × 12, JIMAT RM2,101 |
| 7 | 1:13.5 – 1:32.5 | 4 langkah (with the 4 documents) |
| 8 | 1:32.5 – 1:46.5 | Closing line, tamat 30 November, "Reply YA" button |

## Sound
- No background music (sound effects only).
- 83 sound effects (whoosh, pop, ding, stamp, impact, riser, cash, clock, tick, lock) placed on each animation beat, from `assets/sfx/`.
- Voice-over slot is ready in `index.html` (commented out). Save the recording as `assets/voice.wav` and uncomment the `<audio id="voice">` line.

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
1. Scene 5 press clippings, sources:
   - Berita Harian, 1 Apr 2024, "Hibah digital Wasiyyah diiktiraf Mahkamah Syariah": https://www.bharian.com.my/bisnes/korporat/2024/04/1230342/hibah-digital-wasiyyah-diiktiraf-mahkamah-syariah . Its photo is blocked for automated download, so this clipping is typeset from the real headline, date and opening paragraph. To use the real photo or a screenshot, save it in `assets/press/` and add an `<img>` to `#kn-bh`.
   - DagangNews, 11 Feb 2026, "Wasiyyah Cipta Sejarah Pendigitalan Hibah, Diiktiraf Malaysia Book of Records": https://www.dagangnews.com/article/kolumnis-terkini/wasiyyah-cipta-sejarah-pendigitalan-hibah-diiktiraf-malaysia-book-records-64907 . Photo: `assets/press/dagangnews-mbor.jpg` (from the article).
2. Record and add the voice-over, then retime scenes to the real recording.
3. Confirm the instalment figure: RM47 × 12 = RM564, which is more than RM499.
