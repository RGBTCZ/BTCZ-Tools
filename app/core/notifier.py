import time

from app.core.i18n import t

try:
    import pystray
    from pystray import Menu, MenuItem
    from PIL import Image

    _HAS_TRAY = True
except Exception:
    pystray = None
    _HAS_TRAY = False


class Notifier:
    def __init__(self, image_path=None):
        self.image_path = image_path
        self.icon = None
        self.app = None
        self.history = []
        self._max = 60
        self._listener = None

    def set_listener(self, callback):
        self._listener = callback

    def available(self):
        return _HAS_TRAY

    def _image(self):
        try:
            if self.image_path:
                return Image.open(self.image_path).convert("RGBA")
        except Exception:
            pass
        img = Image.new("RGBA", (64, 64), (13, 15, 14, 255))
        try:
            from PIL import ImageDraw

            draw = ImageDraw.Draw(img)
            draw.ellipse([8, 8, 56, 56], fill=(61, 220, 151, 255))
        except Exception:
            pass
        return img

    def attach(self, app):
        self.app = app
        if not _HAS_TRAY:
            return
        try:
            menu = Menu(
                MenuItem(t("tray.show"), self._on_show, default=True),
                MenuItem(t("tray.quit"), self._on_quit),
            )
            self.icon = pystray.Icon("btcz_tools", self._image(), "BTCZ Tools", menu)
            self.icon.run_detached()
        except Exception:
            self.icon = None

    def notify(self, title, message):
        self.history.insert(0, (time.time(), title, message))
        del self.history[self._max:]
        if self._listener is not None:
            try:
                self._listener(title, message)
            except Exception:
                pass
        if self.icon is not None:
            try:
                self.icon.notify(message, title)
            except Exception:
                pass

    def clear_history(self):
        self.history = []

    def remove_at(self, index):
        if 0 <= index < len(self.history):
            del self.history[index]

    def _on_show(self, icon=None, item=None):
        if self.app is not None:
            self.app.after(0, self.app.restore_from_tray)

    def _on_quit(self, icon=None, item=None):
        if self.app is not None:
            self.app.after(0, self.app.quit_app)

    def stop(self):
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None
