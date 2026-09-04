import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import gzip
import pickle
import os

from src.Trade_Module.paramters.country_info import country_dict
from src.Trade_Module.paramters.paths import src_path


class InputManager:
    def __init__(self):
        pass

    def _open_pickle(self):
        """Open latest pkl file.
        :return: object from pkl file
        """
        path = src_path
        pkl_files = list(path.glob("*.pkl"))

        if not pkl_files:
            print(f"No .pkl file found at: {path.resolve()}")
            return None

        file = max(pkl_files, key=lambda f: f.stat().st_mtime)

        print(f"Open pkl at: {file.resolve()}")

        with gzip.open(file, "rb") as pkl_file:
            obj = pickle.load(pkl_file)
        return obj["data_periods"]
    
        
    def downcasting(self, data: pd.DataFrame):
        data.RegionCode = data.RegionCode.astype("category")
        data.CommodityCode = data.CommodityCode.astype("category")
        data.domain = data.domain.astype("category")
        data.price = data.price.astype("float32")
        data.quantity = data.quantity.astype("float32")
        data.Period = data.Period.astype("int16")
        data.year = data.year.astype("int16")
        data.Scenario = data.Scenario.astype("category")
        data.Model = data.Model.astype("category")
        return data
    
    def main(self):
        data = self._open_pickle()
        data["Country"] = data["RegionCode"].map(country_dict)
        data = data.dropna().reset_index(drop=True)
        data = data[['Country', 'CommodityCode', 'domain', 'Period', 'year','price', 'quantity',]]

        data["price_previous"] = (
            data.groupby(["Country", "CommodityCode", "domain"])["price"].shift(1)
        )

        data["quantity_previous"] = (
            data.groupby(["Country", "CommodityCode", "domain"])["quantity"].shift(1)
        )
        
        print(data)
        # country_data = self.read_country_data()
        # commodity_data = self.read_commodity_data()
        return data
