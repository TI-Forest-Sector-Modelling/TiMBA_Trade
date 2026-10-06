from src.Trade_Module.core.TiMBADataProcessor import TiMBADataProcessor
from src.Trade_Module.core.BACIDataProcessor import BACIProcessor
from src.Trade_Module.core.InputManager import InputManager
from src.Trade_Module.logic.CalculationManager import CalcManager
from src.Trade_Module.logic.RAS import RAS

import time
import pandas as pd
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

    def load_timba_process(self)->pd.DataFrame:
        self.start_process("Beginn to load TiMBA data")
        data = self.im.load_timba_results()
        tdp = TiMBADataProcessor(data)
        timba_data = tdp.main()
        self.end_process("TiMBA data loaded")

        return timba_data

    def load_baci_process(self)->pd.DataFrame:
        self.start_process("Beginn to load BACI data")
        baci_data = self.im.load_baci_data()
        bdp = BACIProcessor(df=baci_data)
        baci_data = bdp.main()
        self.end_process("BACI data loaded")

        return baci_data

    def RAS_process(self, fao_df, bt_df):
        self.start_process("Beginn the RAS process")

        merge_keys = ["Reporter","Partner", "Commodity", "Period"]

        ras_df = fao_df.merge(
            bt_df,
            on=merge_keys,
            how="left"
        )

        ras_df = ras_df[ras_df.Period==0]
        ras_df = ras_df[ras_df['Commodity'] != 89]
        ras_df = ras_df[ras_df['Commodity'] != 90]
        ras_df = ras_df[ras_df['Commodity'] != 93]
        
        ras_result = RAS().fit(ras_df)

        self.end_process("RAS process done")

        return ras_result[["Reporter", "Partner",  "Commodity",  "Period",  "Export_bilateral"]]

    def main_process(self):
        fao_df = CalcManager(data=self.load_timba_process()).main().copy()
        fao_df = fao_df[["Reporter","Partner","Commodity","Period","X_q_o","M_q_p"]]

        logger.info("")

        bt_df = self.load_baci_process()[["Reporter","Partner","Commodity","Period","Export_bilateral"]]
        bt_df["Export_bilateral"] = bt_df["Export_bilateral"] /1000

        logger.info("")

        return self.RAS_process(fao_df=fao_df,bt_df=bt_df)
    