#!/usr/bin/env bash
# Remplace des plages d'images du mezzanine par des passages re-rendus (ex. ajout du logo),
# puis encode les livrables (mêmes réglages que encode_deliverables.sh).
# Usage : splice_encode.sh  (plages 915-1040 et 1760-1877, rendus remotion/out/patch_*.mov)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
M="$ROOT/remotion/out/master_prores.mov"; P1="$ROOT/remotion/out/patch_915-1040.mov"; P2="$ROOT/remotion/out/patch_1760-1877.mov"
MIX="$ROOT/remotion/public/audio/mix.wav"; OUT="$ROOT/deliverables"
# Le mezzanine est lu deux fois comme entrées séparées (pas de bufferisation 4K en mémoire).
IN=(-t 30.5 -i "$M" -i "$P1" -ss 34.7 -t 23.9667 -i "$M" -i "$P2" -i "$MIX")
FC="[0:v]trim=end_frame=915,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[2:v]trim=end_frame=719,setpts=PTS-STARTPTS[c];[3:v]setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0"
COLOR=(-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv)
ffmpeg -v error -stats -y "${IN[@]}" -filter_complex "$FC,format=yuv420p10le[v]" -map "[v]" -map 4:a:0 \
  -c:v libx265 -preset fast -crf 15 -profile:v main10 -pix_fmt yuv420p10le -tag:v hvc1 \
  -x265-params "keyint=60:min-keyint=30:aq-mode=3:aq-strength=0.9:psy-rd=2.0:psy-rdoq=1.0:no-sao=1:deblock=-1,-1:colorprim=bt709:transfer=bt709:colormatrix=bt709:range=limited:log-level=error" \
  "${COLOR[@]}" -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$OUT/FINAL_MASTER_4K.mp4"
ffmpeg -v error -stats -y "${IN[@]}" -filter_complex "$FC,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int:sws_dither=ed,format=yuv420p[v]" -map "[v]" -map 4:a:0 \
  -c:v libx264 -preset slow -crf 18 -maxrate 10M -bufsize 20M -profile:v high -level 4.2 -g 60 -keyint_min 30 -pix_fmt yuv420p \
  -x264-params "aq-mode=3:psy-rd=1.0,0.15" "${COLOR[@]}" -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -shortest "$OUT/FINAL_WEB.mp4"
ls -la "$OUT"
