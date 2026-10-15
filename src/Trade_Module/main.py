from src.Trade_Module.core.ProcessManager import ProcessManager
from src.Trade_Module.utils.logger import setup_logging

import logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    ras_df = ProcessManager().main_process()


if __name__ == "__main__":
    main()
