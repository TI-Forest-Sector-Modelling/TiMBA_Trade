import logging
from src.Trade_Module.paramters.paths import LOG_PATH

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-1s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(     
                LOG_PATH,
                mode="w",
                encoding="utf-8",
            ),
        ],
    )