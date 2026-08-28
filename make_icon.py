import sys
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent

if len(sys.argv) > 1:
    source = Path(sys.argv[1])
else:
    source = next((p for p in [BASE / "data" / "btcz_logo.png", BASE / "btcz_logo.png"] if p.exists()), None)

if source is None or not source.exists():
    print("Source PNG introuvable.")
    print("Usage : python make_icon.py [chemin/vers/logo.png]")
    print("Par defaut il cherche data/btcz_logo.png puis btcz_logo.png a la racine.")
    raise SystemExit(1)

img = Image.open(source).convert("RGBA")
width, height = img.size
print(f"Source : {source}  ({width}x{height})")

if min(width, height) < 256:
    print(f"ATTENTION : source {width}x{height} trop petite -> l'icone sera floue.")
    print("Fournis un PNG d'au moins 256x256 (ex: python make_icon.py mon_logo_256.png).")

sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
out = BASE / "btcz_logo.ico"
if out.exists():
    out.unlink()
img.save(out, format="ICO", sizes=sizes)
print(f"OK -> {out}  (tailles: {', '.join(str(s[0]) for s in sizes)} px)")