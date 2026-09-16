import numpy as np
import pandas as pd
import xarray as xr
import time

import src.Trade_Module.paramters.paramters as params


class ProcessManager:

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.country_data = None
        self.partner_data = None
        self.countries = None
        self.commodities = None
        self.periods = None
        self.dataset = None
        self.result = None
        self.start_time = None

    def start_process(self):
        self.start_time = time.time()
        print(f"Process started...")


    def end_process(self):
        if self.start_time is None:
            raise ValueError("The process has not been started. Use `start_process` first.")
        
        end_time = time.time()
        elapsed_time = round(end_time - self.start_time, 2)
        print(f"Process completed!")
        print(
            f"--- Time: {elapsed_time:.1f} seconds ({elapsed_time / 60:.1f} min)"
        )

    def _prepare_data(self):
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
            }
        )

        self.dataset["P_share"] = np.log(self.dataset["P_p_o"] / self.dataset["P_p_p"])

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
                "X_p_o", "X_p_o_lag",  
                "X_q_o", "X_q_o_lag",
                "X_p_p", "X_p_p_lag",  
                "X_q_p", "X_q_p_lag",  
                "P_share", "P_share_lag",
            ]
        ]


    def main(self):
        self.start_process()
        self._prepare_data()
        self._build_dataset()
        self._process_all()
        self.end_process()

        return self.result
