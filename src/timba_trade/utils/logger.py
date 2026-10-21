
import logging
from datetime import datetime

from timba_trade.paramters.paths import LOG_DIR, init_path

def setup_logging(path_dict:dict):
    root = logging.getLogger()

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    fmt = logging.Formatter(
        "TiMBA_Trade: %(levelname)-8s  %(message)s",
    )

    log_dir = LOG_DIR if path_dict["LOG_DIR"] is None else path_dict["LOG_DIR"]
    init_path(log_dir)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    handlers = [console]

    log_file = log_dir / f"{datetime.now():%Y-%m-%d_%H-%M-%S}_trade_module.log"

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
