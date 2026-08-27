import logging
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parents[2] / "data"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "btcz.log"

_configured = False


def get_logger(name="btcz"):
    global _configured
    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(_LOG_FILE, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        _configured = True
    return logging.getLogger(name)
