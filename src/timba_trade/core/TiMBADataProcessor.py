from src.timba_trade.paramters.country_info import country_dict
import src.timba_trade.paramters.paramters as params

import pandas as pd
import numpy as np
import xarray as xr
import logging
logger = logging.getLogger(__name__)


class TiMBADataProcessor:
    def __init__(self, data):
        self.data = data

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

    def _prepare_timba_for_biltrade(self):
        self.country_data = self.data[params.COUNTRY_COLUMNS].copy()

        self.partner_data = self.data[params.PARTNER_COLUMNS].rename(
            columns={"Country": "Partner"}
        )

        self.countries = np.sort(self.data["Country"].unique())
        self.commodities = np.sort(self.data["Commodity"].unique())
        self.periods = np.sort(self.data["Period"].unique())

    def _to_dense_array(self, df: pd.DataFrame, dim_name: str, value_col: str) -> xr.DataArray:
        series = (
            df[[dim_name, "Commodity", "Period", value_col]]
            .set_index([dim_name, "Commodity", "Period"])[value_col]
            .astype(np.float32)
        )

        array = xr.DataArray.from_series(series)
        array = array.reindex(
            {
                dim_name: self.countries,
                "Commodity": self.commodities,
                "Period": self.periods,
            }
        )

        return array

    def _to_dense_array(self, df: pd.DataFrame, dim_name: str, value_col: str) -> xr.DataArray:
        series = (
            df[[dim_name, "Commodity", "Period", value_col]]
            .set_index([dim_name, "Commodity", "Period"])[value_col]
            .astype(np.float32)
        )
        array = xr.DataArray.from_series(series)
        array = array.reindex(
            {
                dim_name: self.countries,
                "Commodity": self.commodities,
                "Period": self.periods,
            }
        )
        return array

    @staticmethod
    def _log_of_price_share(data):
        with np.errstate(divide="ignore"):
            data["P_share"] = np.log(data["P_p_o"] / data["P_p_p"])
        return data

    def _build_dataset(self):
        self.dataset = xr.Dataset(
            {
                "P_p_o": self._to_dense_array(self.country_data, "Country", "P_p"),
                "P_q_o": self._to_dense_array(self.country_data, "Country", "P_q"),
                "M_p_o": self._to_dense_array(self.country_data, "Country", "M_p"),
                "M_q_o": self._to_dense_array(self.country_data, "Country", "M_q"),
                "X_p_o": self._to_dense_array(self.country_data, "Country", "X_p"),
                "X_q_o": self._to_dense_array(self.country_data, "Country", "X_q"),
                "P_p_p": self._to_dense_array(self.partner_data, "Partner", "P_p"),
                "P_q_p": self._to_dense_array(self.partner_data, "Partner", "P_q"),
                "X_p_p": self._to_dense_array(self.partner_data, "Partner", "X_p"),
                "X_q_p": self._to_dense_array(self.partner_data, "Partner", "X_q"),
                "M_q_p": self._to_dense_array(self.partner_data, "Partner", "M_q"),
            }
        )

        self._log_of_price_share(data=self.dataset)
        self._add_lags()

    def _add_lags(self):
        lagged = self.dataset.shift(Period=1)
        lagged = lagged.rename(
            {var: f"{var}_lag" for var in lagged.data_vars}
        )

        self.dataset = xr.merge([self.dataset, lagged])

    def _process_all(self):
        chunk_size = params.PROCESS_CHUNK_SIZE
        n_countries = len(self.countries)

        chunks = []

        for start in range(0, n_countries, chunk_size):
            end = min(start + chunk_size, n_countries)

            chunk_ds = self.dataset.isel(Country=slice(start, end))

            chunk_df = (
                chunk_ds.to_dataframe()
                .reset_index()
            )

            chunks.append(chunk_df)

        self.result = pd.concat(chunks, ignore_index=True)

        self.result = self.result[
            [
                "Country", "Partner", "Commodity", "Period",
                "P_p_o", "P_p_o_lag",
                "P_q_o", "P_q_o_lag", 
                "P_p_p", "P_p_p_lag",  
                "P_q_p", "P_q_p_lag",
                "M_p_o", "M_p_o_lag", 
                "M_q_o", "M_q_o_lag",
                "M_q_p", "M_q_p_lag",
                "X_p_o", "X_p_o_lag",  
                "X_q_o", "X_q_o_lag",
                "X_p_p", "X_p_p_lag",  
                "X_q_p", "X_q_p_lag",  
                "P_share", "P_share_lag",
            ]
        ]

    def main(self) -> pd.DataFrame:
        self._rename_columns()    
        self._add_iso_codes()
        self._aggregate_domains()
        self._sort_data()
        self._downcasting()
        self._pivot_domains()
        self._prepare_timba_for_biltrade()
        self._build_dataset()
        self._process_all()

        return self.result
