# Wasiyyah reel: HyperFrames edit

A vertical (1080×1920) reel built from the original 3:27 talking-head video, cut down to **1:55.7**.

## Preview (no render yet)

```bash
cd wasiyyah-reel
npx hyperframes@0.9.66 preview --background
```

## How it was built

1. **Transcribe**: Whisper `medium` (Malay), with word-level timestamps; doubtful words rechecked with `large-v3`.
2. **A-roll** (`assets/aroll.mp4`, kept out of git because of its size): cut to 18 kept segments (53 pieces after removing every pause > 0.26 s), sped up 1.08× (pitch preserved). The hook line "RM90 bilion" was moved to the start.
3. **Audio**: highpass at 85 Hz, RNNoise + FFT denoise, EQ (−2.5 dB at 250 Hz, +2.5 dB at 3.2 kHz), compressor, loudness normalised to −15 LUFS. No music. 11 sound effects synthesised (whoosh, pop, impact, riser, ding, lock, cash, stamp, tick, clock), mixed at 0.18–0.55 under the voice.
4. **Clean-up**: a Bluetooth pairing pop-up on the TV (it showed a device name and passkey) was removed for the first 25 s with a person matte (HyperFrames `remove-background`) composited over a clean plate of the wallpaper.
5. **Look**: `media-treatment` Natural Portrait grade (skin-soft 0.62; highlights −0.18 to tame the fluorescent tubes, shadows +0.13, exposure +0.08, temperature −0.04, vignette 0.05), plus top and bottom scrims. Framing alternates between punch-ins (1.30× and 1.40×) at every cut to hide jump cuts, with a slow push-in.
6. **Safe zones**: every word sits inside the shared TikTok / Reels / Shorts safe area (y 288–1248; x 120–888, narrowing to 120–780 below y 840 to clear the like/comment/share rail). Captions sit in a 660 px box, bottom-anchored at y 1248.

## Files

- `index.html`: root (A-roll, camera moves, frost/flash, SFX, scene hosts)
- `compositions/*.html`: 14 scene cards plus `captions.html`
- `tools/build.py`: regenerates everything from `tools/words_edit.json` and `tools/pieces.json` (keeps the colour grade already on `#aroll`)
- `tools/grade.json`: the colour grade payload

## Product names (confirmed)

- Wasiyyah **Khairiat Pusaka**
- **Wasitah Intan**
- Syarikat Wasiyyah Berhad
