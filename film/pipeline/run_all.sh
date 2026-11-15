#!/usr/bin/env bash
# Chaîne de production complète, de bout en bout (reproductible).
# Prérequis : ffmpeg/ffprobe (libx264, libx265, libvidstab, libzimg), fluidsynth +
# banque MuseScore General (apt: fluidsynth musescore-general-soundfont-lossless),
# Python 3 (venv .venv : faster-whisper numpy scipy soundfile opencv-python-headless
# mido matplotlib pyloudnorm pillow), Node 22 + npm (projet remotion/).
#
# Les vidéos originales sont lues (jamais modifiées) via des liens dans sources/.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

echo "### A. Analyse"
# $PY pipeline/transcribe.py large-v3 analysis/transcripts analysis/audio/WA0048_16k.wav   # (déjà fait)
# $PY pipeline/analyze_video.py analysis/video_analysis.json sources/*.mp4                   # (déjà fait)

echo "### B. Montage / prétraitement image"
for s in WA0042 WA0045; do pipeline/stabilize.sh "$s" strong; done
for s in WA0044 WA0047 WA0049; do pipeline/stabilize.sh "$s" gentle; done
$PY pipeline/make_lut.py grade/film_look.cube 33
$PY pipeline/build_timeline.py          # EDL -> remotion/src/data/timeline.json + SRT
$PY pipeline/remap.py                   # speed ramps + frame blending
$PY pipeline/grade_upscale.py           # étalonnage + upscale 4K -> remotion/public/media
$PY pipeline/make_grain.py

echo "### C. Son"
$PY pipeline/audio_voice.py
$PY pipeline/compose_music.py
$PY pipeline/mix_master.py              # -> remotion/public/audio/mix.wav

echo "### D/E. Rendu"
(cd remotion && npx remotion render Film out/master_prores.mov --codec=prores --prores-profile=hq \
  --concurrency=4 --color-space=bt709 --image-format=jpeg --jpeg-quality=98)
pipeline/encode_deliverables.sh

echo "### F. Contrôle qualité"
$PY pipeline/qc.py
$PY pipeline/contact_sheet.py deliverables/FINAL_MASTER_4K.mp4 deliverables/PLANCHE_CONTACT.jpg
