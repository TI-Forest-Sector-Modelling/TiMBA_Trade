from src.timba_trade.core.ProcessManager import ProcessManager
from src.timba_trade.utils.logger import setup_logging

import pandas as pd
import logging
setup_logging()
logger = logging.getLogger(__name__)


def main(timba_data:pd.DataFrame|None=None)->pd.DataFrame:
    ras_df = ProcessManager().main_process(td=timba_data)


if __name__ == "__main__":
    main()
