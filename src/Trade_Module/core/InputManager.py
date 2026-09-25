import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import gzip
import pickle
import os

from src.Trade_Module.paramters.country_info import country_dict
from src.Trade_Module.paramters.paths import INPUT_PATH
import src.Trade_Module.paramters.paramters as params

import logging
logger = logging.getLogger(__name__)


class InputManager:
    def __init__(self):
        pass

    def _open_pickle(self):
        path = INPUT_PATH
        pkl_files = list(path.glob("*.pkl"))

        if not pkl_files:
            raise FileNotFoundError(
                f"No .pkl file found at: {path.resolve()}"
            )

        file = max(pkl_files, key=lambda f: f.stat().st_mtime)

        logger.info(f"Open pkl at: {file.resolve()}")

        with gzip.open(file, "rb") as pkl_file:
            obj = pickle.load(pkl_file)

        self.data = obj["data_periods"]

    def _rename_columns(self):
        self.data = self.data.rename(columns=params.COLUMN_MAPPING)   

    def _add_iso_codes(self):
        self.data["Country"] = self.data["RegionCode"].map(country_dict)

        self.data = (
            self.data
            .dropna(subset=["Country"])
            .reset_index(drop=True)
        )

        self.data = self.data[
            [
                "Country",
                "Commodity",
                "domain",
                "Period",
                "p",
                "q",
            ]
        ]

    def _aggregate_domains(self):
        self.data = self.data[
            ~self.data["domain"].isin(params.DOMAINS_TO_REMOVE)
        ].copy()

        self.data["domain"] = self.data["domain"].replace(
            params.DOMAIN_MAPPING
        )

        self.data = (
            self.data
            .groupby(
                params.GROUP_COLUMNS,
                as_index=False,
                observed=True
            )
            .agg(
                p=("p", "max"),
                q=("q", "max"),
            )
        )

    def _downcasting(self):
        self.data["Country"] = self.data["Country"].astype("category")
        self.data["Commodity"] = self.data["Commodity"].astype("category")
        self.data["domain"] = self.data["domain"].astype("category")
        self.data["p"] = self.data["p"].astype("float32")
        self.data["q"] = self.data["q"].astype("float32")
        self.data["Period"] = self.data["Period"].astype("int16")

    def _pivot_domains(self):
        self.data = self.data.pivot(
            index=params.INDEX_COLUMNS,
            columns="domain",
            values=params.VALUE_COLUMNS,
        )

        self.data.columns = [
            f"{domain}_{variable}"
            for variable, domain in self.data.columns
        ]

        self.data = self.data.reset_index()

    def _sort_data(self):
        self.data = (
            self.data
            .sort_values(params.GROUP_COLUMNS)
            .reset_index(drop=True)
        )

    def main(self):
        self._open_pickle()
        self._rename_columns()    
        self._add_iso_codes()
        self._aggregate_domains()
        self._sort_data()
        self._downcasting()
        self._pivot_domains()

        return self.data
