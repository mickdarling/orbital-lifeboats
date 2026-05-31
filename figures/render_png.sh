#!/usr/bin/env bash
# Rasterize the SVG figures to PNG (figures/png/).
# The SVGs are canonical; PNGs are convenience renders.
# Uses rsvg-convert if available, else macOS qlmanage.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p png
for f in *.svg; do
  b="${f%.svg}"
  if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 1400 "$f" -o "png/$b.png"
  elif command -v qlmanage >/dev/null 2>&1; then
    qlmanage -t -s 1400 -o png "$f" >/dev/null 2>&1
    mv "png/$f.png" "png/$b.png" 2>/dev/null || true
  else
    echo "need rsvg-convert or qlmanage to rasterize" >&2; exit 1
  fi
  echo "rendered png/$b.png"
done
