import logging
import sys

from app.core.paths import DATA_DIR

_LOG_FILE = DATA_DIR / "btcz.log"

_configured = False


def get_logger(name="btcz"):
    global _configured
    if not _configured:
        handlers = [logging.FileHandler(_LOG_FILE, encoding="utf-8")]
        if sys.stderr is not None:
            handlers.append(logging.StreamHandler())
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=handlers,
        )
        _configured = True
    return logging.getLogger(name)
