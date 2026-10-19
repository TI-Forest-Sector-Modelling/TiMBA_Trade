from timba_trade.core.ProcessManager import ProcessManager
from timba_trade.utils.logger import setup_logging

import pandas as pd
from pathlib import Path
import logging

def main(
        timba_data:pd.DataFrame|None=None, 
        save_file:bool=True,
        folder_path: Path|None = None,
)->pd.DataFrame:

    setup_logging(folder_path=folder_path)
    logger = logging.getLogger(__name__)
    
    pm = ProcessManager(folder_path=folder_path)

    ras_df = pm.main_process(
        td=timba_data,
        save_file=save_file,
    )

    return ras_df


if __name__ == "__main__":
    data = main(
        save_file=False,
        folder_path=None    
    )
