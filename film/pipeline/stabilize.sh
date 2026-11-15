#!/usr/bin/env bash
# Stabilisation 2 passes (libvidstab) d'un clip B-roll destiné au timelapse.
# Usage: stabilize.sh <SRC_ID> [mode]
#   mode "strong" : lissage ±40, zoom dynamique (plans fixes / sujet qui marche vers la caméra)
#   mode "gentle" : lissage ±12, zoom fixe 5 %, correction plafonnée (plans avec
#                   mouvements de caméra volontaires : orbites, panoramiques, marche)
# Sortie: work/stab/<SRC_ID>.mp4 (720x1280, 30 fps CFR, x264 quasi sans perte)
# Le lissage est fort (hyperlapse) : à vitesse 8-16x, un lissage de ±N images
# source devient ±N/8..16 images de sortie.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_ID="$1"
MODE="${2:-gentle}"
if [ "$MODE" = "strong" ]; then
  TRANSFORM="smoothing=40:optzoom=2:zoomspeed=0.2:crop=black"
else
  TRANSFORM="smoothing=12:optzoom=0:zoom=5:maxshift=36:maxangle=0.035:crop=keep"
fi
IN="$ROOT/sources/$SRC_ID.mp4"
OUT_DIR="$ROOT/work/stab"
mkdir -p "$OUT_DIR"
TRF="$OUT_DIR/$SRC_ID.trf"

# passe 1 : détection du mouvement (sur l'image redressée, CFR 30)
ffmpeg -v error -y -i "$IN" -vf "fps=30,vidstabdetect=shakiness=8:accuracy=15:stepsize=6:mincontrast=0.2:result=$TRF" -f null -

# passe 2 : transformation lissée + zoom adaptatif (pas de bords noirs)
ffmpeg -v info -y -i "$IN" -an \
  -vf "fps=30,vidstabtransform=input=$TRF:$TRANSFORM:interpol=bicubic" \
  -c:v libx264 -preset medium -crf 8 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  "$OUT_DIR/$SRC_ID.mp4" 2> "$OUT_DIR/$SRC_ID.log"
grep -iE "zoom|error" "$OUT_DIR/$SRC_ID.log" | tail -3 || true
echo "done $SRC_ID"
