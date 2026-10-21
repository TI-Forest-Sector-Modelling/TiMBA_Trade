from timba_trade.core.TiMBADataProcessor import TiMBADataProcessor
from timba_trade.core.BACIDataProcessor import BACIProcessor
from timba_trade.core.InputManager import InputManager
from timba_trade.logic.CalculationManager import CalcManager
from timba_trade.logic.RAS import RAS
from timba_trade.core.OutputManager import OutputManager

import time
from pathlib import Path
import pandas as pd
import logging
logger = logging.getLogger(__name__)


class ProcessManager:

    def __init__(self, path_dict:dict):
        self.path_dict=path_dict
        self.im = InputManager(path_dict=self.path_dict)
        self.om = OutputManager(path_dict=self.path_dict)

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

    def load_timba_process(self,data:pd.DataFrame|None)->pd.DataFrame:
        
        self.start_process("Beginn to load TiMBA data")
        scen_name = self.path_dict["scen_name"]
        if data is None:
            data, scen_name = self.im.load_timba_results()
        tdp = TiMBADataProcessor(data)
        timba_data = tdp.main()
        self.end_process("TiMBA data loaded")

        return timba_data, scen_name

    def load_baci_process(self)->pd.DataFrame:
        self.start_process("Beginn to load BACI data")
        baci_data = self.im.load_baci_data()
        bdp = BACIProcessor(df=baci_data)
        baci_data = bdp.main()
        self.end_process("BACI data loaded")

        return baci_data

    def main_process(self, td:pd.DataFrame|None, save_file:bool=True)->pd.DataFrame:
        timba_data, scen_name = self.load_timba_process(data=td)
        fao_df = CalcManager(data=timba_data).main().copy()
        fao_df = fao_df[[
            "Reporter",
            "Partner",
            "Commodity",
            "Period",
            "X_q_o",
            "M_q_p",
            "P_share_growth"
        ]]

        bt_df = self.load_baci_process()[[
            "Reporter",
            "Partner",
            "Commodity",
            "Period",
            "Export_bilateral"
        ]]
        bt_df["Export_bilateral"] /= 1000

        self.start_process(f"Beginn the RAS process")

        fao_df = fao_df.loc[~fao_df["Commodity"].isin([89, 90, 93])]
        bt_df = bt_df.loc[~bt_df["Commodity"].isin([89, 90, 93])]
        
        merge_keys = ["Reporter","Partner", "Commodity", "Period"]
        bt_result = pd.DataFrame()
        for period in fao_df.Period.unique():
            logger.info(f" Period: {period}")
            fp = fao_df[fao_df.Period==period]

            bt_df = bt_df[[
                "Reporter",
                "Partner",
                "Commodity",
                "Export_bilateral"
            ]]

            bt_df["Period"]=period
            bt_df = bt_df.drop_duplicates()
            bt_df = bt_df.dropna().reset_index(drop=True)
            bt_df = bt_df[bt_df['Reporter'] != 'RoW']
            bt_df = bt_df[bt_df['Partner'] != 'RoW']

            ras_df = fp.merge(
                bt_df,
                on=merge_keys,
                how="left"
            )
            ras_df["Export_bilateral"] *= ras_df["P_share_growth"]

            bt_df = RAS().fit(ras_df)
            bt_result = pd.concat([bt_result,bt_df]).reset_index(drop=True)

        if save_file:
            self.om.save_parquet(
                df=bt_result,
                file_name=f"BilateralTrade_{scen_name}"
            )

        self.end_process(f"End of RAS process")

        return bt_result
    