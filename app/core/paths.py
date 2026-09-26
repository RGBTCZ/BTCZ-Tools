import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]

if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    RESOURCE_DIR = BASE_DIR

ASSETS_DIR = RESOURCE_DIR / "assets"

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
