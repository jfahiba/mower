#!/usr/bin/env bash
# Encodage des livrables à partir du mezzanine Remotion (ProRes 422 HQ, 2160x3840)
# et du mixage masterisé (WAV 48 kHz 24 bits, -14 LUFS, -1 dBTP).
#
#   FINAL_MASTER_4K.mp4 : HEVC Main10 4:2:0, 2160x3840, 30 i/s, Rec.709 (SDR),
#                         réglages x265 orientés préservation du grain/détail,
#                         AAC-LC 320 kb/s 48 kHz stéréo, tag hvc1 (Apple), faststart.
#   FINAL_WEB.mp4       : H.264 High 4:2:0 8 bits, 1080x1920, débit plafonné,
#                         AAC-LC 192 kb/s 48 kHz, faststart (partage, réseaux sociaux).
# Usage : encode_deliverables.sh [mezzanine.mov] [mix.wav] [suffixe]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MEZZ="${1:-$ROOT/remotion/out/master_prores.mov}"
MIX="${2:-$ROOT/remotion/public/audio/mix.wav}"
SUFFIX="${3:-}"
OUT="$ROOT/deliverables"
mkdir -p "$OUT"
COLOR=(-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv)

echo "== Master HEVC 4K (arrière-plan) + Web H.264 (en parallèle)"
ffmpeg -v error -stats -y -i "$MEZZ" -i "$MIX" -map 0:v:0 -map 1:a:0 \
  -vf "format=yuv420p10le" \
  -c:v libx265 -preset medium -crf 15 -profile:v main10 -pix_fmt yuv420p10le -tag:v hvc1 \
  -x265-params "keyint=60:min-keyint=30:aq-mode=3:aq-strength=0.9:psy-rd=2.0:psy-rdoq=1.0:no-sao=1:deblock=-1,-1:colorprim=bt709:transfer=bt709:colormatrix=bt709:range=limited:log-level=error" \
  "${COLOR[@]}" \
  -c:a aac -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart -shortest \
  "$OUT/FINAL_MASTER_4K${SUFFIX}.mp4" &
MASTER_PID=$!

echo "== Web H.264 1080x1920"
ffmpeg -v error -stats -y -i "$MEZZ" -i "$MIX" -map 0:v:0 -map 1:a:0 \
  -vf "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int:sws_dither=ed,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -maxrate 16M -bufsize 32M -profile:v high -level 4.2 \
  -g 60 -keyint_min 30 -pix_fmt yuv420p \
  -x264-params "aq-mode=3:psy-rd=1.0,0.15" \
  "${COLOR[@]}" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart -shortest \
  "$OUT/FINAL_WEB${SUFFIX}.mp4"
wait $MASTER_PID

ls -la "$OUT"
