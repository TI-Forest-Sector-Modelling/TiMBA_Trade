from timba_trade.core.ProcessManager import ProcessManager
from timba_trade.utils.logger import setup_logging

import pandas as pd
from pathlib import Path
import logging
import warnings

def main(
        timba_data:pd.DataFrame|None=None, 
        scen_name:str|None=None,
        save_file:bool=True,
        folder_path: Path|None=None,
)->pd.DataFrame:

    warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
    setup_logging(folder_path=folder_path)
    
    pm = ProcessManager(folder_path=folder_path)

    ras_df = pm.main_process(
        td=timba_data,
        save_file=save_file,
        scen_name=scen_name,
    )

    return ras_df


if __name__ == "__main__":
    data = main(
        save_file=False,
        folder_path=None,
        scen_name=None,
    )
