import json
import threading

from app.core.paths import DATA_DIR

SETTINGS_FILE = DATA_DIR / "settings.json"

_lock = threading.Lock()


def load():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def get(key, default=None):
    return load().get(key, default)


def set(key, value):
    with _lock:
        data = load()
        data[key] = value
        try:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
