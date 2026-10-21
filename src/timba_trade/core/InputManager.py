from timba_trade.paramters.paths import SCENARIO_DIR, BACI_DIR, BACI_FILE

from pathlib import Path
import pandas as pd
import pickle
import gzip
import logging

logger = logging.getLogger(__name__)


class InputManager:
    def __init__(self, path_dict:dict):
        self.scen_dir = SCENARIO_DIR if path_dict["SCENARIO_DIR"] is None else path_dict["SCENARIO_DIR"]
        self.baci_dir = BACI_DIR if path_dict["BACI_DIR"] is None else path_dict["BACI_DIR"]
        self.baci_file_name = BACI_FILE if path_dict["baci_file_name"] is None else path_dict["baci_file_name"]

    def load_timba_results(self):
        pkl_files = list(self.scen_dir.glob("*.pkl"))

        if not pkl_files:
            raise FileNotFoundError(
                f"   No .pkl file found at: {self.scen_dir.resolve()}"
            )

        file = max(pkl_files, key=lambda f: f.stat().st_mtime)
        scen_name = str(file.stem).split("Sc_")[1]
        logger.info(f" Load following scenario: {scen_name}")

        with gzip.open(file, "rb") as pkl_file:
            obj = pickle.load(pkl_file)

        return obj["data_periods"], scen_name

    def load_baci_data(self):
        BITRADEPATH = self.baci_dir / self.baci_file_name
        logger.info(f" Load following file: {self.baci_file_name}")
        return pd.read_parquet(BITRADEPATH)

