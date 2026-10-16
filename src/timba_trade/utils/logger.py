import logging
from src.timba_trade.paramters.paths import LOG_PATH


def setup_logging():
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    file = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file.setLevel(logging.DEBUG)
    file.setFormatter(fmt)

    logging.basicConfig(level=logging.DEBUG, handlers=[console, file], force=True)

    for name in ("joblib", "matplotlib", "PIL", "numba", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)