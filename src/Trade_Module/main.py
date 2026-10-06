from src.Trade_Module.core.ProcessManager import ProcessManager
from src.Trade_Module.utils.logger import setup_logging

import logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    pm = ProcessManager()

    timba_data = pm.load_timba_process()
    baci_data = pm.load_baci_process()

    print(timba_data)
    print(baci_data)


if __name__ == "__main__":
    main()
