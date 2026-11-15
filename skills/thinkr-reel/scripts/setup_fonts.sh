#!/usr/bin/env bash
# Installs THINKR brand fonts (Figtree, JetBrains Mono, Instrument Serif) as renamed TTFs for cairo.
set -euo pipefail
pip install -q pycairo fonttools --break-system-packages 2>/dev/null || pip install -q pycairo fonttools
TMP=$(mktemp -d); cd "$TMP"
npm pack @fontsource/figtree @fontsource/jetbrains-mono @fontsource/instrument-serif >/dev/null
for f in *.tgz; do tar xzf "$f" && mv package "${f%.tgz}"; done
mkdir -p ~/.fonts
python3 - <<'PY'
from fontTools.ttLib import TTFont
import glob, os
want = {"figtree-latin-500-normal.woff":"FigtreeMed","figtree-latin-800-normal.woff":"FigtreeXB",
        "figtree-latin-900-normal.woff":"FigtreeBlk","jetbrains-mono-latin-600-normal.woff":"JBMonoSB",
        "instrument-serif-latin-400-italic.woff":"InstrSerifIt"}
for name, fam in want.items():
    p = glob.glob(f"*/files/{name}")[0]; f = TTFont(p); f.flavor = None
    for rec in f["name"].names:
        if rec.nameID in (1,4,6,16): rec.string = fam
        if rec.nameID in (2,17): rec.string = "Regular"
    f["OS/2"].usWeightClass = 400; f["head"].macStyle = 0
    f.save(os.path.expanduser(f"~/.fonts/{fam}.ttf")); print("installed", fam)
PY
fc-cache -f >/dev/null || true
