import requests
from PIL import Image, ImageTk

from app.core.logger import get_logger
from app.core.paths import DATA_DIR
from config.config import LOGO_URLS

log = get_logger("assets")

LOGO_PNG = DATA_DIR / "btcz_logo.png"
LOGO_ICO = DATA_DIR / "btcz_logo.ico"


def ensure_logo():
    if not LOGO_PNG.exists():
        for url in LOGO_URLS:
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                if resp.content:
                    LOGO_PNG.write_bytes(resp.content)
                    log.info("Logo downloaded from %s", url)
                    break
            except Exception as exc:
                log.warning("Logo download failed (%s): %s", url, exc)
                continue

    if LOGO_PNG.exists() and not LOGO_ICO.exists():
        try:
            img = Image.open(LOGO_PNG).convert("RGBA")
            img.save(LOGO_ICO, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        except Exception as exc:
            log.warning("ICO conversion failed: %s", exc)


def load_logo_image(size=(42, 42)):
    import customtkinter as ctk

    if not LOGO_PNG.exists():
        return None
    try:
        img = Image.open(LOGO_PNG).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as exc:
        log.warning("Logo load failed: %s", exc)
        return None


def apply_window_icon(window):
    try:
        if LOGO_ICO.exists():
            window.iconbitmap(str(LOGO_ICO))
        elif LOGO_PNG.exists():
            icon = ImageTk.PhotoImage(Image.open(LOGO_PNG))
            window._icon_ref = icon
            window.iconphoto(True, icon)
    except Exception as exc:
        log.warning("Window icon failed: %s", exc)
