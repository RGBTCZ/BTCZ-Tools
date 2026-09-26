import shutil

import requests
from PIL import Image, ImageTk

from app.core.logger import get_logger
from app.core.paths import ASSETS_DIR, DATA_DIR
from config.config import LOGO_URLS

log = get_logger("assets")

BUNDLED_PNG = ASSETS_DIR / "btcz_logo.png"
BUNDLED_ICO = ASSETS_DIR / "btcz_logo.ico"

LOGO_PNG = DATA_DIR / "btcz_logo.png"
LOGO_ICO = DATA_DIR / "btcz_logo.ico"


def ensure_logo():
    if BUNDLED_PNG.exists():
        try:
            shutil.copyfile(BUNDLED_PNG, LOGO_PNG)
        except Exception as exc:
            log.warning("Bundled logo copy failed: %s", exc)
    elif not LOGO_PNG.exists():
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

    if BUNDLED_ICO.exists():
        try:
            shutil.copyfile(BUNDLED_ICO, LOGO_ICO)
            return
        except Exception as exc:
            log.warning("Bundled ICO copy failed: %s", exc)

    if LOGO_PNG.exists():
        try:
            img = Image.open(LOGO_PNG).convert("RGBA")
            img.save(
                LOGO_ICO,
                format="ICO",
                sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
            )
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


def set_app_user_model_id(app_id="BTCZTools.Desktop.1"):
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def apply_window_icon(window):
    if LOGO_ICO.exists():
        try:
            window.iconbitmap(default=str(LOGO_ICO))
        except Exception:
            try:
                window.iconbitmap(str(LOGO_ICO))
            except Exception as exc:
                log.info("iconbitmap unavailable (%s), using iconphoto", exc)

    if LOGO_PNG.exists():
        try:
            sizes = [16, 24, 32, 48, 64, 128, 256]
            base = Image.open(LOGO_PNG).convert("RGBA")
            photos = [ImageTk.PhotoImage(base.resize((s, s), Image.Resampling.LANCZOS)) for s in sizes]
            window._icon_refs = photos
            window.iconphoto(True, *photos)
        except Exception as exc:
            log.warning("iconphoto failed: %s", exc)
