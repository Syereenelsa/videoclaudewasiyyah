# Hibah Rumah RM499: infographic video (HyperFrames)

Vertical 1080×1920 motion-graphic infographic, 2:30, timed to the recorded voice-over. Soft-blue background, navy cards and text, gold accents.
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
| 4 | 0:38.8 – 1:12.2 | Tanpa vs dengan dokumen hibah (faraid pie, then an 8 s faraid example during a voice pause, then the 3-step flow) |
| 5 | 1:12.2 – 1:25.3 | Kenali Hibah Digital Wasiyyah: press clippings (Berita Harian, DagangNews) + 3 proof points |
| 5b | 1:25.3 – 1:32 | Setakat ini, 100% hibah di Wasiyyah berjaya mendapat pengesahan: ring + company profile 2025 p.5 proof |
| 6 | 1:32 – 1:48.3 | Promosi: RM2,600 struck out, RM499 slam, RM47 × 12, JIMAT RM2,101 |
| 7 | 1:48.3 – 2:21.2 | 4 langkah (documents; draf untuk semakan; akad dipantau HQ Wasiyyah via UsraHDD) |
| 8 | 2:21.2 – 2:41.3 | Closing line, tamat 30 November, "Reply YA" button |

Faraid example (scene 4): husband dies, house RM1 juta, heirs wife 1/8 (RM125,000), mother 1/6 (RM166,667), father 1/6 (RM166,667), residue RM541,666 split 2:1 to son (RM361,111) and daughter (RM180,555). The voice pauses for 8 s after "...dibahagikan mengikut faraid" (`VO_CUT`/`VO_GAP` in `tools/build.py`; two `<audio>` clips of the same recording).

## Speed
The film runs at 1.075× so it lands on 2:30 (`TARGET`, `SPEED` and `TS` in `tools/build.py`). Cue values in the build script stay in recording seconds and are scaled at build time; the voice is time-stretched with pitch kept by `tools/make_voice.sh` (`assets/voice_1x.wav` → `assets/voice.wav`). The scene table above is in recording seconds; multiply by 0.93 for film time.

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
1. Scene 5b proof: `assets/press/profil-2025-ms5-statistik.jpg`, cropped from the user's screenshot of Wasiyyah Shoppe Berhad Company Profile 2025, page 5 (statistics panel).
2. Scene 5 press clippings, sources:
   - Berita Harian, 1 Apr 2024, "Hibah digital Wasiyyah diiktiraf Mahkamah Syariah": https://www.bharian.com.my/bisnes/korporat/2024/04/1230342/hibah-digital-wasiyyah-diiktiraf-mahkamah-syariah . Its photo is blocked for automated download, so this clipping is typeset from the real headline, date and opening paragraph. To use the real photo or a screenshot, save it in `assets/press/` and add an `<img>` to `#kn-bh`.
   - DagangNews, 11 Feb 2026, "Wasiyyah Cipta Sejarah Pendigitalan Hibah, Diiktiraf Malaysia Book of Records": https://www.dagangnews.com/article/kolumnis-terkini/wasiyyah-cipta-sejarah-pendigitalan-hibah-diiktiraf-malaysia-book-records-64907 . Photo: `assets/press/dagangnews-mbor.jpg` (from the article).
3. Confirm the instalment figure: RM47 × 12 = RM564, which is more than RM499.
