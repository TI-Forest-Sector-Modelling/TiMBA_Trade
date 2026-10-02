import time

from src.Trade_Module.core.TiMBADataProcessor import TiMBADataProcessor
from src.Trade_Module.core.InputManager import InputManager

import logging
logger = logging.getLogger(__name__)


class ProcessManager:

    def __init__(self):
        self.data = None
        self.country_data = None
        self.partner_data = None
        self.countries = None
        self.commodities = None
        self.periods = None
        self.dataset = None
        self.result = None
        self.start_time = None
        self.im = InputManager()

    def start_process(self, process_description:str):
        self.start_time = time.time()
        logger.info(process_description)


    def end_process(self, process_description):
        if self.start_time is None:
            raise ValueError("The process has not been started. Use `start_process` first.")
        
        end_time = time.time()
        elapsed_time = round(end_time - self.start_time, 2)
        logger.info(
            f"{process_description} in {elapsed_time:.1f} seconds"
        )

    def load_timba_process(self):
        self.start_process("Beginn to load TiMBA data")

        data = self.im.load_timba_results()

        tdp = TiMBADataProcessor(data)
        timba_data = tdp.main()


        self.end_process("TiMBA data loaded")

        return timba_data
