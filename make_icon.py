from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
candidates = [BASE / "data" / "btcz_logo.png", BASE / "btcz_logo.png"]
source = next((p for p in candidates if p.exists()), None)

if source is None:
    print("btcz_logo.png introuvable (cherché dans data/ et à la racine).")
    raise SystemExit(1)

out = BASE / "btcz_logo.ico"
img = Image.open(source).convert("RGBA")
img.save(out, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f"Icône écrite : {out}  (source : {source})")
