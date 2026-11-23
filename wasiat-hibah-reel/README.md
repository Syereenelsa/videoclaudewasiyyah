# Wasiat ≠ Hibah reel: HyperFrames edit

A vertical (1080×1920) reel built from the original 2:51 talking-head video, cut down to **1:50.2**.
The voice-over script is in [`VO_SCRIPT.md`](VO_SCRIPT.md).

## Preview (no render yet)

```bash
cd wasiat-hibah-reel
npx hyperframes@0.9.66 preview --background
```

Still frames from the current edit are in `../preview-wh/`.

## How it was built

1. **Transcribe**: faster-whisper `large-v3` (Malay) with word timestamps (`tools/transcript_src.json`). Doubtful words were re-checked on short clips: "masih **tertakluk** kepada", "hibah bukan **magik**", "isu **pemilikan** atau **penyerahan**".
2. **Cut** (`tools/cutlist.py`): five repeated or overly detailed lines were dropped (see VO_SCRIPT.md). Every pause ≥ 0.22 s was removed using an energy envelope of the cleaned voice. Cuts snap to the 30 fps frame grid, and the whole edit runs at 1.10× speed with pitch preserved. Result: 56 pieces, 110.2 s.
3. **Media** (`tools/cut_media.py`, outputs kept out of git): `assets/aroll.mp4` (muted, graded in HyperFrames) and `assets/voice.wav`.
4. **Audio**: highpass at 85 Hz, RNNoise (`sh.rnnn`, mix 0.85) + FFT denoise, EQ (−2.5 dB at 250 Hz, +2.5 dB at 3.2 kHz, −1.5 dB air shelf), compressor (3:1), loudness normalised to −14 LUFS / −1.5 dBTP. No music. 74 sound effects (whoosh, pop, impact, stamp, ding, tick, lock, clock, riser), mixed at 0.16–0.55 under the voice.
5. **Look**: `media-treatment` skin-soft grade (intensity 0.6; exposure +0.13, highlights −0.24 to tame the LED strip, shadows +0.12, contrast +0.08, temperature +0.03, vibrance +0.06, vignette 0.12). See `tools/grade.json`.
6. **Layout**: split screen. Navy and gold cards sit on top, and the speaker fills the bottom stage (y 960–1920). Framing alternates between 1.00× and 1.12× punch-ins at cuts to hide jump cuts, with a slow push-in. The giant hook adds a hard 1.25× punch.
7. **Safe zones**: all text sits inside the shared TikTok / Reels / Shorts safe area (y 288–1248; x 120–888, narrowing to 120–780 below y 840). Cards sit at y 296–714. Captions sit in a 768 px band bottom-anchored at y 840, so they never cover the face, the username or the like/comment/share rail. `hyperframes check` passes with 0 errors.

## Structure

| Time | Scene | Content |
|---|---|---|
| 0:00 | `hook` | "SALAH FAHAM BIASA": RUMAH automatik jadi HAK ANAK? |
| 0:04.8 | `tidak` | Stamp: TIDAK SEMESTINYA |
| 0:07 | `giant` | GIANT HOOK: WASIAT ≠ HIBAH |
| 0:10 | `empat` | 4 PERBEZAAN PENTING |
| 0:14 | `p1` | #1 Bila berkuat kuasa (versus card) |
| 0:23 | `p2` | #2 Kepada siapa |
| 0:45 | `p3` | #3 Berapa banyak (1/3 pie vs tiada had) |
| 0:58 | `p4` | #4 Paling ramai tak tahu |
| 1:16 | `contoh` | Encik Ali → rumah → isteri, MILIK ISTERI |
| 1:26 | `magik` | Hibah bukan magik: boleh dipertikaikan |
| 1:35 | `lengkap` | Wasiat + Hibah saling melengkapi |
| 1:41 | `cta` | Komen "HIBAH" + Follow untuk Part 2 |

## Rebuild

```bash
python3 tools/cutlist.py <db.npy>                          # cut list + word timings
python3 tools/cut_media.py <src.mp4> <clean_voice.wav> <workdir>
python3 tools/build.py                                     # index.html + compositions/*
npm run check
```
