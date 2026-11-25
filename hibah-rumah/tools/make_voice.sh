#!/usr/bin/env bash
# Time-stretch the cleaned voice-over to the film speed (pitch preserved).
# SPEED = TOTAL / TARGET in tools/build.py (161.3 / 150).
set -e
cd "$(dirname "$0")/.."
ffmpeg -y -i assets/voice_1x.wav -af "atempo=1.0753333333333335" -ar 24000 -ac 1 assets/voice.wav
