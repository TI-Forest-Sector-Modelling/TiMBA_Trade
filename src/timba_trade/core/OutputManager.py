import pandas as pd
from pathlib import Path
import pyarrow

from timba_trade.paramters.paths import OUTPUT_PATH, PACKAGEDIR, init_path, RESPATH

import logging
logger = logging.getLogger(__name__)


class OutputManager:
    def __init__(self, folder_path:Path|None):
        pckdir = PACKAGEDIR if folder_path is None else folder_path
        self.folder_path = pckdir / OUTPUT_PATH / RESPATH
        init_path(self.folder_path)

    def save_df(self, df, file_name, max_attempts=10):
        for i in range(max_attempts):
            file = (file_name + ".csv") if i == 0 else f"{file_name}_({i}).csv"
            try:
                df.to_csv(self.folder_path / Path(file), index=False) 
                logger.info(f"CSV file saved at: {self.folder_path / Path(file)}")
                return file
            except PermissionError:
                if i == max_attempts - 1:
                    raise
                continue

    def save_parquet(self, df, file_name):
        file = Path(file_name + ".parquet")
        df.to_parquet(self.folder_path / file) 
        logger.info(f"Parquet saved at: {self.folder_path / Path(file)}")
