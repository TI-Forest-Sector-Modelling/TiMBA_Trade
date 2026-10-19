
import logging
from datetime import datetime
from pathlib import Path

from timba_trade.paramters.paths import LOG_PATH, PACKAGEDIR, init_path


def setup_logging(folder_path: Path | None = None) -> None:
    root = logging.getLogger()

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    base_dir = PACKAGEDIR if folder_path is None else Path(folder_path)
    log_dir = base_dir / LOG_PATH
    init_path(log_dir)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    handlers = [console]

    log_file = log_dir / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.log"

    try:
        file_handler = logging.FileHandler(
            log_file,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)

    except OSError:
        console.handleError(
            logging.LogRecord(
                name=__name__,
                level=logging.ERROR,
                pathname=__file__,
                lineno=0,
                msg=f"Log file could not been opened: {log_file}",
                args=(),
                exc_info=None,
            )
        )

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        force=True,
    )

    for name in ("joblib", "matplotlib", "PIL", "numba", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)
