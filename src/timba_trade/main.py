from timba_trade.core.ProcessManager import ProcessManager
from timba_trade.utils.logger import setup_logging

import pandas as pd
import logging
setup_logging()
logger = logging.getLogger(__name__)


def main(timba_data:pd.DataFrame|None=None, save_file:bool=True)->pd.DataFrame:
    pm = ProcessManager()
    ras_df = pm.main_process(
        td=timba_data,
        save_file=save_file,
    )
    return ras_df


if __name__ == "__main__":
    main(save_file=False)
