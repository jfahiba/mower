#!/usr/bin/env bash
# Chaîne complète : sources 4K manquantes, puis rendu + encodage de chaque capsule (séquentiel).
set -uo pipefail
cd "$(dirname "$0")/.."
/home/user/mower/film/.venv/bin/python ../pipeline/grade_upscale.py ../remotion_media WA0078 WA0076
for id in ${@:-C09 C08 C04 C05 C06 C07 C01 C02 C03 C10}; do
  [ -f "../deliverables/${id}_WEB.mp4" ] && continue
  scripts/render_capsule.sh "$id" 2>&1 | grep -vE "memory|Memory|docker"
done
echo ALL_DONE
