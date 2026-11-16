#!/usr/bin/env bash
# Re-rendu complet du film (mezzanine H.264 CRF 9) puis encodage des livrables et QC.
set -euo pipefail
cd "$(dirname "$0")/.."
(cd remotion && npx remotion render Film out/master.mp4 --codec=h264 --crf=9 --x264-preset=fast --concurrency=4 \
  --color-space=bt709 --image-format=jpeg --jpeg-quality=98 --log=error)
pipeline/encode_deliverables.sh "$PWD/remotion/out/master.mp4"
.venv/bin/python pipeline/qc.py | tail -8
.venv/bin/python pipeline/contact_sheet.py deliverables/FINAL_MASTER_4K.mp4 deliverables/PLANCHE_CONTACT.jpg
.venv/bin/python pipeline/write_report.py
rm -f remotion/out/master.mp4; rm -rf /tmp/remotion-*
echo RERENDER_DONE
