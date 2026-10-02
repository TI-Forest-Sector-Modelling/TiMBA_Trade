import pandas as pd
from pathlib import Path

from src.Trade_Module.paramters.paths import OUTPUT_PATH

import logging
logger = logging.getLogger(__name__)


class OutputManager:
    def __init__(self):
        pass

    def save_df(self, df, file_name, max_attempts=10):
        for i in range(max_attempts):
            file = (file_name + ".csv") if i == 0 else f"{file_name}_({i}).csv"
            try:
                df.to_csv(OUTPUT_PATH / Path(file), index=False) 
                logger.info(f"CSV file saved at: {OUTPUT_PATH / Path(file)}")
                return file
            except PermissionError:
                if i == max_attempts - 1:
                    raise
                continue
