from timba_trade.core.InputManager import InputManager
from timba_trade.paramters.hscodes import timba_commodity_list, timba_comcode
import timba_trade.paramters.paramters as p
from timba_trade.utils.helper import hs_to_fao_dict
from timba_trade.utils.logger import setup_logging

import logging
import pandas as pd

setup_logging()
logger = logging.getLogger(__name__)


class BACIProcessor:
    def __init__(self, df:pd.DataFrame, year: int = 2023,):
        self.im = InputManager()
        self.commodity_list = timba_commodity_list
        self.year = year
        self.df = df
        
    @staticmethod
    def _groupby_sum(df: pd.DataFrame, id_list: list, value_list: list) -> pd.DataFrame:
        return df.groupby(id_list)[value_list].sum().reset_index()

    def prepare_baci_data(self):
        hs_to_fao_map = hs_to_fao_dict(self.commodity_list)

        df = self.df.copy()
        df["Commodity"] = df[p.COM_COLUMN].map(hs_to_fao_map)

        return df[df[p.TIME_COLUMN] == self.year].dropna(subset=["Commodity"]).reset_index(drop=True)

    def create_bilateral_trade(self,df:pd.DataFrame)->pd.DataFrame:
        counterflow = df.rename(
            columns={
                p.REPORTER_COLUMN: p.PARTNER_COLUMN,
                p.PARTNER_COLUMN: p.REPORTER_COLUMN,
                p.QUANTITY_COLUMN: "Import",
            }
        )
        result = df.merge(counterflow,on=p.BACIID,how="outer")
        result = result.rename(columns={p.QUANTITY_COLUMN: "Export"})

        return self._groupby_sum(df=result,id_list=p.BACIID,value_list=p.X_M_NAMES)

    def _merge_trade_totals(self,df)->pd.DataFrame:
        exporter_totals = self._groupby_sum(df=df,id_list=p.TOTALSID,value_list=p.X_M_NAMES)
        importer_totals = exporter_totals.rename(columns={p.REPORTER_COLUMN: p.PARTNER_COLUMN})

        total = df.merge(
            right=exporter_totals,
            how="outer",
            on=p.TOTALSID,
            suffixes=(
                "_bilateral",
                "_total_exporter",
            ),
        )

        total = total.merge(
            right=importer_totals,
            how="outer",
            on=p.TOTALSIMPORTID,
            suffixes=("", "_total_importer"),
        )

        return total

    def add_trade_totals(self,df:pd.DataFrame,map:dict)->pd.DataFrame:
        total = self._merge_trade_totals(df)

        total = total[
            [
                p.TIME_COLUMN,
                p.REPORTER_COLUMN,
                p.PARTNER_COLUMN,
                "Commodity",
                "Export_bilateral",
                "Import_bilateral",
                "Export_total_exporter",
                "Import_total_exporter",
                "Export",
                "Import",
            ]
        ].rename(
            columns={
                p.REPORTER_COLUMN: "Reporter",
                p.PARTNER_COLUMN: "Partner",
                "Export": "Export_total_importer",
                "Import": "Import_total_importer",
            }
        )

        total["Period"] = 0
        total["Commodity"] = total["Commodity"].map(map)

        return total

    def main(self)->pd.DataFrame:
        baci_data = self.prepare_baci_data()
        baci_data = self._groupby_sum(
            df=baci_data,
            id_list=p.BACIID,
            value_list=["Quantity"]
        )
        bilateral_trade = self.add_trade_totals(
            df=self.create_bilateral_trade(df=baci_data),
            map=timba_comcode,
        )

        return bilateral_trade
