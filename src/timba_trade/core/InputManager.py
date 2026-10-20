from timba_trade.paramters.paths import BACI_FILE, INPUT_DATA_PATH, PACKAGEDIR

from pathlib import Path
import pandas as pd
import pickle
import gzip
import logging

logger = logging.getLogger(__name__)


class InputManager:
    def __init__(self, folder_path:Path|None):
        pckdir = PACKAGEDIR if folder_path is None else folder_path
        self.folder_path = pckdir / INPUT_DATA_PATH

    def load_timba_results(self):
        pkl_files = list(self.folder_path.glob("*.pkl"))

        if not pkl_files:
            raise FileNotFoundError(
                f"   No .pkl file found at: {self.folder_path.resolve()}"
            )

        file = max(pkl_files, key=lambda f: f.stat().st_mtime)
        scen_name = str(file.stem).split("Sc_")[1]
        logger.info(f"Read scenario: {scen_name}")

        with gzip.open(file, "rb") as pkl_file:
            obj = pickle.load(pkl_file)

        return obj["data_periods"], scen_name

    def load_baci_data(self):
        BITRADEPATH = self.folder_path / BACI_FILE
        return pd.read_parquet(BITRADEPATH)

