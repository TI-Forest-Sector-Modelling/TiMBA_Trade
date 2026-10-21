import pandas as pd
from pathlib import Path
import pyarrow

from timba_trade.paramters.paths import OUTPUT_DIR, init_path

import logging
logger = logging.getLogger(__name__)


class OutputManager:
    def __init__(self, path_dict:dict):
        self.output_dir = OUTPUT_DIR if path_dict["OUTPUT_DIR"] is None else path_dict["OUTPUT_DIR"]
        init_path(self.output_dir)

    def save_df(
            self, 
            df:pd.DataFrame, 
            file_name:str, 
            max_attempts:int=10,
    ):
        for i in range(max_attempts):
            file = (file_name + ".csv") if i == 0 else f"{file_name}_({i}).csv"
            try:
                df.to_csv(self.output_dir / Path(file), index=False) 
                logger.info(f"CSV file saved at: {self.output_dir / Path(file)}")
                return file
            except PermissionError:
                if i == max_attempts - 1:
                    raise
                continue

    def save_parquet(self, df:pd.DataFrame, file_name:str):
        file = Path(file_name + ".parquet")
        df.to_parquet(self.output_dir / Path(file)) 
        logger.info(f"Parquet saved at: {self.output_dir / Path(file)}")
