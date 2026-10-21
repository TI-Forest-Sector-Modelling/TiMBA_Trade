from timba_trade.core.ProcessManager import ProcessManager
from timba_trade.utils.logger import setup_logging

import pandas as pd
import logging
import warnings

from timba_trade.paramters.paths import default_paths

def main(
        timba_data:pd.DataFrame|None=None, 
        save_file:bool=True,
        path_dict:dict=default_paths,
)->pd.DataFrame:

    warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
    setup_logging(path_dict=path_dict)
    
    pm = ProcessManager(
        path_dict=path_dict
    )

    ras_df = pm.main_process(
        td=timba_data,
        save_file=save_file,
    )

    logging.shutdown()

    return ras_df


if __name__ == "__main__":
    data = main(
        timba_data=None,
        save_file=False,
        path_dict=default_paths
    )
