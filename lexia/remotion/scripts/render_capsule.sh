#!/usr/bin/env bash
# Rendu 4K d'une capsule (mezzanine H.264 CRF 9, quasi sans perte) puis encodage des livrables et suppression du mezzanine.
set -euo pipefail
cd "$(dirname "$0")/.."
ID="$1"; OUT=../deliverables; mkdir -p "$OUT"
npx remotion render "$ID" "out/$ID.mp4" --codec=h264 --crf=9 --x264-preset=fast --concurrency=4 --color-space=bt709 \
  --image-format=jpeg --jpeg-quality=98 --log=error
COLOR=(-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv)
ffmpeg -v error -y -i "out/$ID.mp4" -i "public/audio/$ID.wav" -map 0:v:0 -map 1:a:0 -vf format=yuv420p10le \
  -c:v libx265 -preset fast -crf 16 -profile:v main10 -pix_fmt yuv420p10le -tag:v hvc1 \
  -x265-params "keyint=60:min-keyint=30:aq-mode=3:psy-rd=2.0:no-sao=1:colorprim=bt709:transfer=bt709:colormatrix=bt709:log-level=error" \
  "${COLOR[@]}" -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest "$OUT/${ID}_4K.mp4"
ffmpeg -v error -y -i "out/$ID.mp4" -i "public/audio/$ID.wav" -map 0:v:0 -map 1:a:0 \
  -vf "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int:sws_dither=ed,format=yuv420p" \
  -c:v libx264 -preset slow -crf 18 -maxrate 10M -bufsize 20M -profile:v high -level 4.2 -g 60 -pix_fmt yuv420p \
  "${COLOR[@]}" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT/${ID}_WEB.mp4"
rm -f "out/$ID.mp4"; rm -rf /tmp/remotion-webpack-bundle-* /tmp/remotion-v4*-assets*
echo "done $ID"
