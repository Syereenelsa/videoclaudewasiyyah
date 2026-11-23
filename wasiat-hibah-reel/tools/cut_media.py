#!/usr/bin/env python3
"""Cut the source video + cleaned voice to pieces.json, speed 1.10x (pitch kept).
usage: cut_media.py SRC_VIDEO CLEAN_VOICE_WAV WORKDIR"""
import json, subprocess, sys, os
HERE = sys.path[0]; PROJ = os.path.dirname(HERE)
SPEED = 1.10
src, voice, work = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(work, exist_ok=True)
P = json.load(open(f"{HERE}/pieces.json"))
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
lst = []
for i, p in enumerate(P):
    nf = round((p["s1"] - p["s0"]) * 30)
    out = f"{work}/p{i:03d}.mp4"
    run("-ss", f"{p['s0']:.4f}", "-i", src, "-frames:v", str(nf), "-an", "-vf", "fps=30",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12", "-pix_fmt", "yuv420p", out)
    lst.append(f"file '{out}'")
open(f"{work}/list.txt", "w").write("\n".join(lst))
run("-f", "concat", "-safe", "0", "-i", f"{work}/list.txt", "-vf", f"setpts=PTS/{SPEED},fps=30",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-g", "15", "-movflags", "+faststart",
    "-an", f"{PROJ}/assets/aroll.mp4")
a = [f"[0:a]atrim=start={p['s0']:.4f}:end={p['s1']:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
     f"afade=t=out:st={p['s1']-p['s0']-0.018:.4f}:d=0.018[a{i}]" for i, p in enumerate(P)]
fc = ";".join(a) + ";" + "".join(f"[a{i}]" for i in range(len(P))) + \
     f"concat=n={len(P)}:v=0:a=1,atempo={SPEED},loudnorm=I=-14:TP=-1.5:LRA=9[ao]"
open(f"{work}/fc.txt", "w").write(fc)
run("-i", voice, "-filter_complex_script", f"{work}/fc.txt", "-map", "[ao]", "-ar", "48000", "-ac", "1", f"{PROJ}/assets/voice.wav")
