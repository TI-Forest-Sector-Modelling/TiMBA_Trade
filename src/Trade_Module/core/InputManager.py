from src.Trade_Module.paramters.paths import INPUT_PATH, BITRADEPATH

import pandas as pd
import pickle
import gzip
import logging

logger = logging.getLogger(__name__)


class InputManager:
    def __init__(self):
        pass

    def load_timba_results(self):
        path = INPUT_PATH
        pkl_files = list(path.glob("*.pkl"))

        if not pkl_files:
            raise FileNotFoundError(
                f"   No .pkl file found at: {path.resolve()}"
            )

        file = max(pkl_files, key=lambda f: f.stat().st_mtime)

        logger.info(f"   Open pkl at: {path.resolve()}")
        logger.info(f"   Name of TiMBA result file: {file.name}")

        with gzip.open(file, "rb") as pkl_file:
            obj = pickle.load(pkl_file)

        return obj["data_periods"]

    def load_baci_data():
        return pd.read_parquet(BITRADEPATH)

